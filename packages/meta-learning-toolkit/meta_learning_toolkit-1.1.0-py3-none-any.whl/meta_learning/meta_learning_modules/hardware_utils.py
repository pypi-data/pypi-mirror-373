"""
Modern Hardware Support Utilities for Meta-Learning
================================================

Comprehensive support for modern hardware accelerators including:
- NVIDIA GPUs (RTX 4090, A100, H100, etc.)
- Apple Silicon (M1/M2/M3/M4 with MPS)
- Multi-GPU distributed training
- Mixed precision training (FP16, BF16)
- Memory optimization and efficient computation

This module provides hardware abstraction that automatically detects
and utilizes the best available hardware for meta-learning workloads.

Author: Benedict Chen (benedict@benedictchen.com)
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.cuda.amp import autocast, GradScaler
from typing import Dict, List, Tuple, Optional, Any, Union
import logging
import psutil
import gc
from contextlib import contextmanager
from dataclasses import dataclass
import warnings

logger = logging.getLogger(__name__)


@dataclass
class HardwareConfig:
    """Configuration for modern hardware utilization."""
    # Device selection
    device: Optional[str] = None  # Auto-detect if None
    use_mixed_precision: bool = True  # AMP for faster training
    precision_dtype: str = "float16"  # "float16", "bfloat16", or "float32"
    
    # Multi-GPU settings
    use_data_parallel: bool = False  # Use DataParallel
    use_distributed: bool = False  # Use DistributedDataParallel  
    world_size: int = 1
    rank: int = 0
    
    # Memory optimization
    gradient_checkpointing: bool = False  # Trade compute for memory
    memory_efficient: bool = True  # Enable memory optimizations
    max_memory_fraction: float = 0.9  # Max GPU memory to use
    
    # Apple Silicon specific
    use_mps_fallback: bool = True  # Fallback for unsupported ops
    
    # Performance tuning
    compile_model: bool = False  # PyTorch 2.0 compilation
    channels_last: bool = False  # Memory format optimization
    benchmark_mode: bool = True  # cuDNN benchmark mode


class HardwareManager:
    """Manages modern hardware resources for meta-learning."""
    
    def __init__(self, config: Optional[HardwareConfig] = None):
        self.config = config or HardwareConfig()
        self.device = self._detect_best_device()
        self.scaler = None
        self.is_distributed = False
        
        # Initialize hardware-specific settings
        self._initialize_hardware()
        
    def _detect_best_device(self) -> torch.device:
        """Automatically detect the best available device."""
        if self.config.device:
            return torch.device(self.config.device)
            
        # Priority order: CUDA > MPS > CPU
        if torch.cuda.is_available():
            device_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
            logger.info(f"🚀 Using CUDA GPU: {device_name} ({gpu_memory:.1f}GB)")
            return torch.device("cuda")
            
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            logger.info("🍎 Using Apple Silicon MPS acceleration")
            return torch.device("mps")
            
        else:
            cpu_count = psutil.cpu_count()
            ram_gb = psutil.virtual_memory().total / 1e9
            logger.info(f"💻 Using CPU: {cpu_count} cores, {ram_gb:.1f}GB RAM")
            return torch.device("cpu")
            
    def _initialize_hardware(self):
        """Initialize hardware-specific optimizations."""
        if self.device.type == "cuda":
            self._setup_cuda()
        elif self.device.type == "mps":
            self._setup_mps()
        else:
            self._setup_cpu()
            
    def _setup_cuda(self):
        """Setup CUDA-specific optimizations."""
        # Enable cuDNN benchmark for consistent input sizes
        if self.config.benchmark_mode:
            torch.backends.cudnn.benchmark = True
            
        # Mixed precision training
        if self.config.use_mixed_precision:
            self.scaler = GradScaler()
            logger.info("⚡ Enabled mixed precision training (AMP)")
            
        # Memory management
        if self.config.max_memory_fraction < 1.0:
            torch.cuda.set_per_process_memory_fraction(self.config.max_memory_fraction)
            
        # Log GPU information
        props = torch.cuda.get_device_properties(0)
        logger.info(f"🎯 GPU: {props.name}, Compute: {props.major}.{props.minor}, Memory: {props.total_memory/1e9:.1f}GB")
        
    def _setup_mps(self):
        """Setup Apple Silicon MPS optimizations."""
        # MPS doesn't support mixed precision yet (as of PyTorch 2.1)
        if self.config.use_mixed_precision:
            logger.warning("⚠️  Mixed precision not supported on MPS, disabling")
            self.config.use_mixed_precision = False
            
        logger.info("🍎 Configured for Apple Silicon optimization")
        
    def _setup_cpu(self):
        """Setup CPU optimizations.""" 
        # Set optimal thread count
        if torch.get_num_threads() < psutil.cpu_count():
            torch.set_num_threads(psutil.cpu_count())
            
        # Disable mixed precision on CPU
        if self.config.use_mixed_precision:
            logger.warning("⚠️  Mixed precision not efficient on CPU, disabling")
            self.config.use_mixed_precision = False
            
    def prepare_model(self, model: nn.Module) -> nn.Module:
        """Prepare model for optimal hardware utilization."""
        # Move to device
        model = model.to(self.device)
        
        # Enable gradient checkpointing if requested
        if self.config.gradient_checkpointing and hasattr(model, 'gradient_checkpointing_enable'):
            model.gradient_checkpointing_enable()
            logger.info("💾 Enabled gradient checkpointing for memory efficiency")
            
        # Channels-last memory format (for conv nets)
        if self.config.channels_last and hasattr(model, 'to'):
            try:
                model = model.to(memory_format=torch.channels_last)
                logger.info("🔄 Using channels-last memory format")
            except Exception as e:
                logger.warning(f"Could not use channels-last format: {e}")
                
        # Multi-GPU setup
        if self.config.use_data_parallel and torch.cuda.device_count() > 1:
            model = nn.DataParallel(model)
            logger.info(f"🔗 Using DataParallel across {torch.cuda.device_count()} GPUs")
            
        # PyTorch 2.0 compilation
        if self.config.compile_model and hasattr(torch, 'compile'):
            try:
                model = torch.compile(model)
                logger.info("⚡ Model compiled with PyTorch 2.0")
            except Exception as e:
                logger.warning(f"Model compilation failed: {e}")
                
        return model
        
    def prepare_data(self, data: Union[torch.Tensor, Tuple, List]) -> Any:
        """Prepare data tensors for optimal hardware utilization."""
        if isinstance(data, torch.Tensor):
            tensor = data.to(self.device, non_blocking=True)
            
            # Convert to channels-last if enabled and applicable
            if (self.config.channels_last and 
                len(tensor.shape) == 4 and 
                self.device.type == "cuda"):
                try:
                    tensor = tensor.to(memory_format=torch.channels_last)
                except:
                    pass  # Ignore if not applicable
                    
            return tensor
            
        elif isinstance(data, (tuple, list)):
            return type(data)(self.prepare_data(item) for item in data)
            
        elif isinstance(data, dict):
            return {key: self.prepare_data(value) for key, value in data.items()}
            
        else:
            return data
            
    @contextmanager
    def autocast_context(self):
        """Context manager for mixed precision computation."""
        if self.config.use_mixed_precision and self.device.type == "cuda":
            dtype = torch.float16 if self.config.precision_dtype == "float16" else torch.bfloat16
            with autocast(enabled=True, dtype=dtype):
                yield
        else:
            yield
            
    def backward_and_step(self, loss: torch.Tensor, optimizer: torch.optim.Optimizer) -> torch.Tensor:
        """Perform backward pass with hardware optimizations."""
        if self.config.use_mixed_precision and self.scaler:
            # Mixed precision backward
            self.scaler.scale(loss).backward()
            self.scaler.step(optimizer)
            self.scaler.update()
        else:
            # Regular backward
            loss.backward()
            optimizer.step()
            
        return loss
        
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get current memory usage statistics."""
        stats = {}
        
        if self.device.type == "cuda":
            stats.update({
                'gpu_memory_allocated': torch.cuda.memory_allocated() / 1e9,
                'gpu_memory_reserved': torch.cuda.memory_reserved() / 1e9,
                'gpu_memory_max_allocated': torch.cuda.max_memory_allocated() / 1e9,
                'gpu_utilization': self._get_gpu_utilization()
            })
            
        # CPU/system memory
        vm = psutil.virtual_memory()
        stats.update({
            'cpu_memory_used': vm.used / 1e9,
            'cpu_memory_total': vm.total / 1e9,
            'cpu_memory_percent': vm.percent
        })
        
        return stats
        
    def _get_gpu_utilization(self) -> float:
        """Get GPU utilization percentage."""
        try:
            import nvidia_ml_py3 as nvml
            nvml.nvmlInit()
            handle = nvml.nvmlDeviceGetHandleByIndex(0)
            util = nvml.nvmlDeviceGetUtilizationRates(handle)
            return util.gpu
        except:
            return 0.0
            
    def clear_cache(self):
        """Clear GPU/CPU cache to free memory."""
        if self.device.type == "cuda":
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            
        # Python garbage collection
        gc.collect()
        
    def benchmark_device(self, model: nn.Module, input_shape: Tuple[int, ...]) -> Dict[str, float]:
        """Benchmark model performance on current device."""
        model = model.to(self.device)
        dummy_input = torch.randn(input_shape).to(self.device)
        
        # Warmup
        for _ in range(10):
            with torch.no_grad():
                _ = model(dummy_input)
                
        if self.device.type == "cuda":
            torch.cuda.synchronize()
            
        # Benchmark inference
        import time
        start_time = time.time()
        
        with torch.no_grad():
            for _ in range(100):
                _ = model(dummy_input)
                
        if self.device.type == "cuda":
            torch.cuda.synchronize()
            
        inference_time = (time.time() - start_time) / 100
        
        # Benchmark training
        optimizer = torch.optim.Adam(model.parameters())
        
        if self.device.type == "cuda":
            torch.cuda.synchronize()
            
        start_time = time.time()
        
        for _ in range(50):
            optimizer.zero_grad()
            output = model(dummy_input)
            loss = output.mean()
            loss.backward()
            optimizer.step()
            
        if self.device.type == "cuda":
            torch.cuda.synchronize()
            
        training_time = (time.time() - start_time) / 50
        
        return {
            'inference_time_ms': inference_time * 1000,
            'training_time_ms': training_time * 1000,
            'device': str(self.device),
            'memory_used_gb': self.get_memory_stats().get('gpu_memory_allocated', 0)
        }


class MultiGPUManager:
    """Manager for multi-GPU distributed training."""
    
    def __init__(self, config: HardwareConfig):
        self.config = config
        self.world_size = config.world_size
        self.rank = config.rank
        self.is_initialized = False
        
    def setup_distributed(self, backend: str = "nccl"):
        """Setup distributed training."""
        if not torch.cuda.is_available() or torch.cuda.device_count() < 2:
            logger.warning("Distributed training requires multiple CUDA GPUs")
            return False
            
        try:
            if not torch.distributed.is_initialized():
                torch.distributed.init_process_group(
                    backend=backend,
                    world_size=self.world_size,
                    rank=self.rank
                )
                self.is_initialized = True
                logger.info(f"🔗 Initialized distributed training: rank {self.rank}/{self.world_size}")
                
            return True
        except Exception as e:
            logger.error(f"Failed to setup distributed training: {e}")
            return False
            
    def wrap_model(self, model: nn.Module) -> nn.Module:
        """Wrap model for distributed training."""
        if not self.is_initialized:
            return model
            
        from torch.nn.parallel import DistributedDataParallel as DDP
        
        device = torch.device(f"cuda:{self.rank}")
        model = model.to(device)
        model = DDP(model, device_ids=[self.rank])
        
        logger.info(f"📦 Wrapped model with DistributedDataParallel on GPU {self.rank}")
        return model
        
    def cleanup(self):
        """Cleanup distributed resources."""
        if self.is_initialized and torch.distributed.is_initialized():
            torch.distributed.destroy_process_group()
            self.is_initialized = False


def get_optimal_batch_size(model: nn.Module, input_shape: Tuple[int, ...], 
                          device: torch.device) -> int:
    """Find optimal batch size for current hardware."""
    if device.type != "cuda":
        return 32  # Conservative default for CPU/MPS
        
    # Start with a reasonable batch size
    batch_size = 16
    max_batch_size = 1024
    
    model = model.to(device)
    model.train()  # Enable training mode for accurate memory estimation
    
    optimizer = torch.optim.Adam(model.parameters())
    
    while batch_size <= max_batch_size:
        try:
            # Clear cache
            torch.cuda.empty_cache()
            
            # Test batch
            dummy_input = torch.randn(batch_size, *input_shape[1:]).to(device)
            
            optimizer.zero_grad()
            output = model(dummy_input)
            loss = output.mean()
            loss.backward()
            optimizer.step()
            
            # If successful, try larger batch
            batch_size *= 2
            
        except RuntimeError as e:
            if "out of memory" in str(e):
                # Return previous successful batch size
                optimal_batch_size = batch_size // 2
                logger.info(f"🎯 Optimal batch size: {optimal_batch_size}")
                return max(1, optimal_batch_size)
            else:
                raise e
                
    return batch_size // 2


def create_hardware_manager(device: Optional[str] = None, 
                          use_mixed_precision: bool = True,
                          **kwargs) -> HardwareManager:
    """Factory function to create hardware manager with optimal settings."""
    config = HardwareConfig(
        device=device,
        use_mixed_precision=use_mixed_precision,
        **kwargs
    )
    
    return HardwareManager(config)


# Compatibility functions for easy integration
def auto_device() -> torch.device:
    """Get the best available device."""
    manager = HardwareManager()
    return manager.device


def prepare_for_hardware(model: nn.Module, device: Optional[torch.device] = None) -> nn.Module:
    """Prepare model for optimal hardware usage."""
    if device is None:
        device = auto_device()
        
    manager = HardwareManager(HardwareConfig(device=str(device)))
    return manager.prepare_model(model)


def log_hardware_info():
    """Log detailed hardware information."""
    logger.info("🔧 Hardware Configuration:")
    
    # CPU info
    cpu_count = psutil.cpu_count()
    ram_gb = psutil.virtual_memory().total / 1e9
    logger.info(f"   CPU: {cpu_count} cores, {ram_gb:.1f}GB RAM")
    
    # GPU info
    if torch.cuda.is_available():
        for i in range(torch.cuda.device_count()):
            props = torch.cuda.get_device_properties(i)
            logger.info(f"   GPU {i}: {props.name}, {props.total_memory/1e9:.1f}GB")
    
    # Apple Silicon
    if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        logger.info("   Apple Silicon MPS: Available")
        
    # PyTorch info
    logger.info(f"   PyTorch: {torch.__version__}")
    logger.info(f"   CUDA: {torch.version.cuda if torch.cuda.is_available() else 'Not available'}")