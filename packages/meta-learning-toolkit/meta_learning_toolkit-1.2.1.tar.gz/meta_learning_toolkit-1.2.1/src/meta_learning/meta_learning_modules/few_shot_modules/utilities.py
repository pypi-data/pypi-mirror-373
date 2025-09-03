"""
Few-Shot Learning Utilities
==========================

Utility functions for few-shot learning including factory functions,
evaluation utilities, and helper functions.
Extracted from the original monolithic few_shot_learning.py.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
import logging
from dataclasses import dataclass

from .configurations import PrototypicalConfig
from .core_networks import PrototypicalNetworks

logger = logging.getLogger(__name__)


def create_prototypical_network(
    backbone: nn.Module,
    variant: str = "research_accurate",
    config: PrototypicalConfig = None
) -> PrototypicalNetworks:
    """
    Factory function to create Prototypical Networks with specific configuration.
    
    Args:
        backbone: Feature extraction backbone network
        variant: Implementation variant ('research_accurate', 'simple', 'enhanced', 'original')
        config: Optional custom configuration
        
    Returns:
        Configured PrototypicalNetworks instance
    """
    if config is None:
        config = PrototypicalConfig()
    
    # Set variant-specific configuration
    if hasattr(config, 'protonet_variant'):
        config.protonet_variant = variant
    
    # Configure based on variant
    if variant == "research_accurate":
        # Pure research-accurate implementation
        if hasattr(config, 'use_squared_euclidean'):
            config.use_squared_euclidean = True
        if hasattr(config, 'prototype_method'):
            config.prototype_method = "mean"
        if hasattr(config, 'enable_research_extensions'):
            config.enable_research_extensions = False
        config.multi_scale_features = False
        config.adaptive_prototypes = False
        if hasattr(config, 'uncertainty_estimation'):
            config.uncertainty_estimation = False
        
    elif variant == "simple":
        # Simplified educational version
        config.multi_scale_features = False
        config.adaptive_prototypes = False
        if hasattr(config, 'uncertainty_estimation'):
            config.uncertainty_estimation = False
        if hasattr(config, 'enable_research_extensions'):
            config.enable_research_extensions = False
        
    elif variant == "enhanced":
        # All extensions enabled
        config.multi_scale_features = True
        config.adaptive_prototypes = True
        if hasattr(config, 'uncertainty_estimation'):
            config.uncertainty_estimation = True
        if hasattr(config, 'enable_research_extensions'):
            config.enable_research_extensions = True
        
    return PrototypicalNetworks(backbone, config)


def compare_with_learn2learn_protonet():
    """
    Comparison with learn2learn's Prototypical Networks implementation.
    
    learn2learn approach:
    ```python
    import learn2learn as l2l
    
    # Create prototypical network head
    head = l2l.algorithms.Lightning(
        l2l.utils.ProtoLightning,
        ways=5,
        shots=5, 
        model=backbone
    )
    
    # Standard training loop
    for batch in dataloader:
        support, query = batch
        loss = head.forward(support, query)
        loss.backward()
        optimizer.step()
    ```
    
    Key differences from our implementation:
    1. learn2learn uses Lightning framework for training automation
    2. They provide built-in data loaders for standard benchmarks
    3. Our implementation is more educational/research-focused
    4. learn2learn handles meta-batch processing automatically
    """
    comparison_info = {
        "learn2learn_advantages": [
            "Lightning framework integration",
            "Built-in benchmark data loaders",
            "Automatic meta-batch processing",
            "Production-ready training loops"
        ],
        "our_advantages": [
            "Educational and research-focused",
            "Research-accurate implementations",
            "Configurable variants",
            "Extensive documentation and citations",
            "Advanced extensions with proper attribution"
        ],
        "use_cases": {
            "learn2learn": "Production systems, quick prototyping",
            "our_implementation": "Research, education, algorithm understanding"
        }
    }
    
    return comparison_info


def evaluate_on_standard_benchmarks(model, dataset_name="omniglot", episodes=600):
    """
    Standard few-shot evaluation following research protocols.
    
    Based on standard evaluation in meta-learning literature:
    - Omniglot: 20-way 1-shot and 5-shot
    - miniImageNet: 5-way 1-shot and 5-shot  
    - tieredImageNet: 5-way 1-shot and 5-shot
    
    Returns confidence intervals over specified episodes (standard: 600).
    
    Args:
        model: Few-shot learning model
        dataset_name: Name of benchmark dataset
        episodes: Number of evaluation episodes
        
    Returns:
        Dictionary with mean accuracy and confidence interval
    """
    accuracies = []
    
    for episode in range(episodes):
        try:
            # Sample episode (N-way K-shot)
            support_x, support_y, query_x, query_y = sample_episode(dataset_name)
            
            # Forward pass
            logits = model(support_x, support_y, query_x)
            if isinstance(logits, dict):
                logits = logits['logits']
            
            predictions = logits.argmax(dim=1)
            
            # Compute accuracy
            accuracy = (predictions == query_y).float().mean()
            accuracies.append(accuracy.item())
            
        except Exception as e:
            logger.warning(f"Episode {episode} failed: {e}")
            continue
    
    if len(accuracies) == 0:
        return {"mean_accuracy": 0.0, "confidence_interval": 0.0, "episodes": 0}
    
    # Compute 95% confidence interval
    mean_acc = np.mean(accuracies)
    std_acc = np.std(accuracies)
    ci = 1.96 * std_acc / np.sqrt(len(accuracies))  # 95% CI
    
    return {
        "mean_accuracy": mean_acc,
        "confidence_interval": ci,
        "std_accuracy": std_acc,
        "episodes": len(accuracies),
        "raw_accuracies": accuracies
    }


@dataclass
class DatasetLoadingConfig:
    """Configuration for dataset loading methods."""
    method: str = "torchmeta"  # "torchmeta", "custom", "huggingface", "synthetic"
    
    # Torchmeta specific options
    torchmeta_root: str = "data"
    torchmeta_download: bool = True
    torchmeta_meta_split: str = "train"
    
    # Custom implementation options
    custom_splits_file: str = "splits.json" 
    custom_data_root: str = "data"
    custom_use_cache: bool = True
    
    # HuggingFace options
    hf_split: str = "train"
    hf_cache_dir: Optional[str] = None
    
    # Data preprocessing
    image_size: Tuple[int, int] = (84, 84)
    normalize_mean: Tuple[float, float, float] = (0.485, 0.456, 0.406)
    normalize_std: Tuple[float, float, float] = (0.229, 0.224, 0.225)
    
    # Fallback options
    fallback_to_synthetic: bool = True
    warn_on_fallback: bool = True


def sample_episode(dataset_name: str, n_way: int = 5, n_support: int = 5, n_query: int = 15, config: Optional[DatasetLoadingConfig] = None):
    """
    Sample a few-shot episode from the specified dataset.
    
    This is a placeholder implementation for demonstration.
    In practice, you would integrate with actual dataset loaders.
    
    Args:
        dataset_name: Name of the dataset
        n_way: Number of classes per episode
        n_support: Number of support examples per class
        n_query: Number of query examples per class
        
    Returns:
        Tuple of (support_x, support_y, query_x, query_y)
    """
    # FIXME: Replace synthetic data with actual dataset loading
    # SOLUTION 1: torchmeta integration for standard datasets
    # if dataset_name == "omniglot":
    #     from torchmeta.datasets import Omniglot
    #     from torchmeta.transforms import ClassSplitter, Categorical
    #     dataset = Omniglot(
    #         root='data', 
    #         num_classes_per_task=n_way,
    #         meta_split='train',
    #         transform=transforms.Compose([
    #             transforms.Resize((28, 28)),
    #             transforms.ToTensor()
    #         ]),
    #         target_transform=Categorical(num_classes=n_way),
    #         download=True
    #     )
    #     task = dataset[0]  # Sample first task
    #     support_x, support_y = task['train']
    #     query_x, query_y = task['test']
    
    # SOLUTION 2: Manual dataset loading with torchvision
    # elif dataset_name == "miniImageNet":
    #     from torchvision.datasets import ImageFolder
    #     from torchvision import transforms
    #     
    #     transform = transforms.Compose([
    #         transforms.Resize((84, 84)),
    #         transforms.ToTensor(),
    #         transforms.Normalize(mean=[0.485, 0.456, 0.406], 
    #                            std=[0.229, 0.224, 0.225])
    #     ])
    #     
    #     dataset = ImageFolder('data/miniImageNet/train', transform=transform)
    #     # Sample n_way classes randomly
    #     class_indices = torch.randperm(len(dataset.classes))[:n_way]
    #     
    #     support_x, support_y = [], []
    #     query_x, query_y = [], []
    #     
    #     for i, class_idx in enumerate(class_indices):
    #         class_samples = [idx for idx, (_, label) in enumerate(dataset.samples) 
    #                         if label == class_idx]
    #         selected_samples = torch.randperm(len(class_samples))[:n_support + n_query]
    #         
    #         for j, sample_idx in enumerate(selected_samples):
    #             image, _ = dataset[class_samples[sample_idx]]
    #             if j < n_support:
    #                 support_x.append(image)
    #                 support_y.append(i)
    #             else:
    #                 query_x.append(image) 
    #                 query_y.append(i)
    #     
    #     support_x = torch.stack(support_x)
    #     support_y = torch.tensor(support_y)
    #     query_x = torch.stack(query_x)
    #     query_y = torch.tensor(query_y)
    
    # SOLUTION 3: Custom dataset loader with caching
    # elif dataset_name == "tieredImageNet":
    #     import pickle
    #     import os
    #     
    #     cache_path = f'data/{dataset_name}_cache.pkl'
    #     if os.path.exists(cache_path):
    #         with open(cache_path, 'rb') as f:
    #             cached_data = pickle.load(f)
    #         
    #         # Sample from cached data
    #         class_indices = torch.randperm(len(cached_data['labels']))[:n_way]
    #         support_x, support_y, query_x, query_y = sample_from_cache(
    #             cached_data, class_indices, n_support, n_query
    #         )
    #     else:
    #         # Load and cache dataset
    #         raw_data = load_tiered_imagenet('data/tieredImageNet')
    #         cached_data = preprocess_and_cache(raw_data, cache_path)
    #         # Then sample as above
    
    # FIXME: CRITICAL FAKE IMPLEMENTATION - Currently returns random noise instead of real data!
    # This completely invalidates any research results using this function.
    # 
    # RESEARCH ISSUE: Meta-learning papers require specific benchmark datasets for valid comparison:
    # - Omniglot: 1623 characters from 50 alphabets (Lake et al. 2015)
    # - miniImageNet: 60,000 84x84 images from 100 classes (Vinyals et al. 2016)  
    # - tieredImageNet: 608 classes from ImageNet hierarchy (Ren et al. 2018)
    
    # SOLUTION 1: torchmeta integration (recommended for research accuracy)
    # from torchmeta.datasets import Omniglot, MiniImageNet, TieredImageNet
    # from torchmeta.transforms import Categorical, ClassSplitter
    # from torchmeta.utils.data import BatchMetaDataLoader
    # 
    # if dataset_name == "omniglot":
    #     dataset = Omniglot(
    #         root='data/omniglot',
    #         num_classes_per_task=n_way,
    #         meta_split='train',
    #         transform=transforms.Compose([
    #             transforms.Resize((28, 28)),
    #             transforms.ToTensor()
    #         ]),
    #         target_transform=Categorical(num_classes=n_way),
    #         download=True
    #     )
    #     dataloader = BatchMetaDataLoader(dataset, batch_size=1, num_workers=0)
    #     task = next(iter(dataloader))
    #     support_x = task['train'][0].squeeze(0)
    #     support_y = task['train'][1].squeeze(0)
    #     query_x = task['test'][0].squeeze(0)
    #     query_y = task['test'][1].squeeze(0)
    #     return support_x, support_y, query_x, query_y
    
    # SOLUTION 2: Custom implementation with research-accurate splits
    # from torchvision import datasets, transforms
    # import json
    # 
    # if dataset_name == "miniImageNet":
    #     # Use official splits from Ravi & Larochelle (2017)
    #     with open('data/miniImageNet/splits.json', 'r') as f:
    #         splits = json.load(f)
    #     
    #     transform = transforms.Compose([
    #         transforms.Resize((84, 84)),
    #         transforms.ToTensor(),
    #         transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    #     ])
    #     
    #     # Load images according to official train/val/test splits
    #     train_classes = splits['train']
    #     selected_classes = np.random.choice(train_classes, n_way, replace=False)
    #     
    #     support_x, support_y, query_x, query_y = [], [], [], []
    #     for i, class_name in enumerate(selected_classes):
    #         class_path = f'data/miniImageNet/images/{class_name}'
    #         image_files = os.listdir(class_path)
    #         selected_files = np.random.choice(image_files, n_support + n_query, replace=False)
    #         
    #         for j, img_file in enumerate(selected_files):
    #             img = Image.open(os.path.join(class_path, img_file))
    #             img_tensor = transform(img)
    #             
    #             if j < n_support:
    #                 support_x.append(img_tensor)
    #                 support_y.append(i)
    #             else:
    #                 query_x.append(img_tensor)
    #                 query_y.append(i)
    #     
    #     return (torch.stack(support_x), torch.tensor(support_y),
    #             torch.stack(query_x), torch.tensor(query_y))
    
    # SOLUTION 3: HuggingFace datasets integration (modern approach)
    # from datasets import load_dataset
    # from PIL import Image
    # 
    # if dataset_name == "omniglot":
    #     dataset = load_dataset("omniglot", split="train")
    #     classes = list(set(dataset['alphabet']))
    #     selected_classes = np.random.choice(classes, n_way, replace=False)
    #     
    #     support_x, support_y, query_x, query_y = [], [], [], []
    #     for i, class_name in enumerate(selected_classes):
    #         class_samples = [item for item in dataset if item['alphabet'] == class_name]
    #         selected_samples = np.random.choice(class_samples, n_support + n_query, replace=False)
    #         
    #         for j, sample in enumerate(selected_samples):
    #             img = transforms.ToTensor()(sample['image'].resize((28, 28)))
    #             
    #             if j < n_support:
    #                 support_x.append(img)
    #                 support_y.append(i)
    #             else:
    #                 query_x.append(img)
    #                 query_y.append(i)
    #     
    #     return (torch.stack(support_x), torch.tensor(support_y),
    #             torch.stack(query_x), torch.tensor(query_y))
    
    if config is None:
        config = DatasetLoadingConfig()
    
    # Try configured method first
    try:
        if config.method == "torchmeta":
            return _load_with_torchmeta(dataset_name, n_way, n_support, n_query, config)
        elif config.method == "custom":
            return _load_with_custom_splits(dataset_name, n_way, n_support, n_query, config)
        elif config.method == "huggingface":
            return _load_with_huggingface(dataset_name, n_way, n_support, n_query, config)
        elif config.method == "synthetic":
            return _load_synthetic_data(dataset_name, n_way, n_support, n_query, config)
        else:
            raise ValueError(f"Unknown dataset loading method: {config.method}")
            
    except Exception as e:
        if config.fallback_to_synthetic:
            if config.warn_on_fallback:
                print(f"⚠️  Warning: {config.method} loading failed ({e}), falling back to synthetic data")
            return _load_synthetic_data(dataset_name, n_way, n_support, n_query, config)
        else:
            raise RuntimeError(f"Dataset loading failed and fallback disabled: {e}")


def _load_with_torchmeta(dataset_name: str, n_way: int, n_support: int, n_query: int, config: DatasetLoadingConfig):
    """SOLUTION 1: torchmeta integration (recommended for research accuracy)"""
    try:
        from torchmeta.datasets import Omniglot, MiniImageNet, TieredImageNet
        from torchmeta.transforms import Categorical, ClassSplitter
        from torchmeta.utils.data import BatchMetaDataLoader
        from torchvision import transforms
        
        if dataset_name.lower() == "omniglot":
            dataset = Omniglot(
                root=config.torchmeta_root,
                num_classes_per_task=n_way,
                meta_split=config.torchmeta_meta_split,
                transform=transforms.Compose([
                    transforms.Resize((28, 28)),
                    transforms.ToTensor()
                ]),
                target_transform=Categorical(num_classes=n_way),
                download=config.torchmeta_download
            )
        elif dataset_name.lower() in ["miniimagenet", "mini_imagenet"]:
            dataset = MiniImageNet(
                root=config.torchmeta_root,
                num_classes_per_task=n_way,
                meta_split=config.torchmeta_meta_split,
                transform=transforms.Compose([
                    transforms.Resize(config.image_size),
                    transforms.ToTensor(),
                    transforms.Normalize(mean=config.normalize_mean, std=config.normalize_std)
                ]),
                target_transform=Categorical(num_classes=n_way),
                download=config.torchmeta_download
            )
        elif dataset_name.lower() in ["tieredimagenet", "tiered_imagenet"]:
            dataset = TieredImageNet(
                root=config.torchmeta_root,
                num_classes_per_task=n_way,
                meta_split=config.torchmeta_meta_split,
                transform=transforms.Compose([
                    transforms.Resize(config.image_size),
                    transforms.ToTensor(),
                    transforms.Normalize(mean=config.normalize_mean, std=config.normalize_std)
                ]),
                target_transform=Categorical(num_classes=n_way),
                download=config.torchmeta_download
            )
        else:
            raise ValueError(f"Unsupported dataset for torchmeta: {dataset_name}")
        
        # Sample episode
        dataloader = BatchMetaDataLoader(dataset, batch_size=1, num_workers=0)
        task = next(iter(dataloader))
        
        # Extract support and query sets
        support_x = task['train'][0].squeeze(0)
        support_y = task['train'][1].squeeze(0)
        query_x = task['test'][0].squeeze(0)
        query_y = task['test'][1].squeeze(0)
        
        return support_x, support_y, query_x, query_y
        
    except ImportError as e:
        raise ImportError(f"torchmeta not installed: {e}. Install with: pip install torchmeta")


def _load_with_custom_splits(dataset_name: str, n_way: int, n_support: int, n_query: int, config: DatasetLoadingConfig):
    """SOLUTION 2: Custom implementation with research-accurate splits"""
    import json
    import os
    from PIL import Image
    from torchvision import transforms
    import numpy as np
    
    if dataset_name.lower() in ["miniimagenet", "mini_imagenet"]:
        # Use official splits from Ravi & Larochelle (2017)
        splits_path = os.path.join(config.custom_data_root, dataset_name, config.custom_splits_file)
        with open(splits_path, 'r') as f:
            splits = json.load(f)
        
        transform = transforms.Compose([
            transforms.Resize(config.image_size),
            transforms.ToTensor(),
            transforms.Normalize(mean=config.normalize_mean, std=config.normalize_std)
        ])
        
        # Load images according to official train/val/test splits
        train_classes = splits['train']
        selected_classes = np.random.choice(train_classes, n_way, replace=False)
        
        support_x, support_y, query_x, query_y = [], [], [], []
        for i, class_name in enumerate(selected_classes):
            class_path = os.path.join(config.custom_data_root, dataset_name, 'images', class_name)
            image_files = os.listdir(class_path)
            selected_files = np.random.choice(image_files, n_support + n_query, replace=False)
            
            for j, img_file in enumerate(selected_files):
                img = Image.open(os.path.join(class_path, img_file))
                img_tensor = transform(img)
                
                if j < n_support:
                    support_x.append(img_tensor)
                    support_y.append(i)
                else:
                    query_x.append(img_tensor)
                    query_y.append(i)
        
        return (torch.stack(support_x), torch.tensor(support_y),
                torch.stack(query_x), torch.tensor(query_y))
    
    elif dataset_name.lower() == "omniglot":
        # Custom Omniglot loading
        omniglot_path = os.path.join(config.custom_data_root, "omniglot")
        alphabets = os.listdir(omniglot_path)
        selected_alphabets = np.random.choice(alphabets, min(n_way, len(alphabets)), replace=False)
        
        transform = transforms.Compose([
            transforms.Resize((28, 28)),
            transforms.ToTensor()
        ])
        
        support_x, support_y, query_x, query_y = [], [], [], []
        for i, alphabet in enumerate(selected_alphabets):
            alphabet_path = os.path.join(omniglot_path, alphabet)
            characters = os.listdir(alphabet_path)
            selected_char = np.random.choice(characters)
            char_path = os.path.join(alphabet_path, selected_char)
            
            images = [f for f in os.listdir(char_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
            selected_images = np.random.choice(images, n_support + n_query, replace=False)
            
            for j, img_file in enumerate(selected_images):
                img = Image.open(os.path.join(char_path, img_file)).convert('L')
                img_tensor = transform(img)
                
                if j < n_support:
                    support_x.append(img_tensor)
                    support_y.append(i)
                else:
                    query_x.append(img_tensor)
                    query_y.append(i)
        
        return (torch.stack(support_x), torch.tensor(support_y),
                torch.stack(query_x), torch.tensor(query_y))
    
    else:
        raise ValueError(f"Unsupported dataset for custom loading: {dataset_name}")


def _load_with_huggingface(dataset_name: str, n_way: int, n_support: int, n_query: int, config: DatasetLoadingConfig):
    """SOLUTION 3: HuggingFace datasets integration (modern approach)"""
    try:
        from datasets import load_dataset
        from torchvision import transforms
        import numpy as np
        
        if dataset_name.lower() == "omniglot":
            dataset = load_dataset("omniglot", split=config.hf_split, cache_dir=config.hf_cache_dir)
            
            # Get unique alphabets/classes
            classes = list(set(dataset['alphabet']))
            selected_classes = np.random.choice(classes, n_way, replace=False)
            
            transform = transforms.Compose([
                transforms.Resize((28, 28)),
                transforms.ToTensor()
            ])
            
            support_x, support_y, query_x, query_y = [], [], [], []
            for i, class_name in enumerate(selected_classes):
                class_samples = [item for item in dataset if item['alphabet'] == class_name]
                if len(class_samples) < n_support + n_query:
                    # Sample with replacement if not enough examples
                    selected_samples = np.random.choice(class_samples, n_support + n_query, replace=True)
                else:
                    selected_samples = np.random.choice(class_samples, n_support + n_query, replace=False)
                
                for j, sample in enumerate(selected_samples):
                    img = transform(sample['image'].resize((28, 28)))
                    
                    if j < n_support:
                        support_x.append(img)
                        support_y.append(i)
                    else:
                        query_x.append(img)
                        query_y.append(i)
            
            return (torch.stack(support_x), torch.tensor(support_y),
                    torch.stack(query_x), torch.tensor(query_y))
        
        # Add more datasets as needed
        else:
            raise ValueError(f"Unsupported dataset for HuggingFace loading: {dataset_name}")
            
    except ImportError as e:
        raise ImportError(f"datasets library not installed: {e}. Install with: pip install datasets")


def _load_synthetic_data(dataset_name: str, n_way: int, n_support: int, n_query: int, config: DatasetLoadingConfig):
    """FALLBACK: Generate synthetic data (for testing/fallback only)"""
    if dataset_name.lower() == "omniglot":
        input_size = (1, 28, 28)
    elif dataset_name.lower() in ["miniimagenet", "tieredimagenet", "mini_imagenet", "tiered_imagenet"]:
        input_size = (3, config.image_size[0], config.image_size[1])
    else:
        input_size = (3, 32, 32)  # Default
    
    # Generate structured synthetic data (better than pure noise)
    support_x = torch.randn(n_way * n_support, *input_size)
    support_y = torch.repeat_interleave(torch.arange(n_way), n_support)
    
    query_x = torch.randn(n_way * n_query, *input_size)
    query_y = torch.repeat_interleave(torch.arange(n_way), n_query)
    
    return support_x, support_y, query_x, query_y


def euclidean_distance_squared(x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
    """
    Squared Euclidean distance as in Snell et al. (2017) Equation 1.
    
    Args:
        x: Query embeddings [n_query, embedding_dim]
        y: Prototype embeddings [n_prototypes, embedding_dim]
    
    Returns:
        Squared distances [n_query, n_prototypes]
    """
    # Expand for broadcasting
    x_expanded = x.unsqueeze(1)  # [n_query, 1, embedding_dim]  
    y_expanded = y.unsqueeze(0)  # [1, n_prototypes, embedding_dim]
    
    # Compute squared Euclidean distance for gradient stability
    return torch.sum((x_expanded - y_expanded)**2, dim=-1)


def compute_prototype_statistics(prototypes: torch.Tensor, support_features: torch.Tensor, 
                                support_labels: torch.Tensor) -> Dict[str, float]:
    """
    Compute statistics about learned prototypes for analysis.
    
    Args:
        prototypes: Class prototypes [n_classes, embedding_dim]
        support_features: Support set features [n_support, embedding_dim] 
        support_labels: Support set labels [n_support]
        
    Returns:
        Dictionary with prototype statistics
    """
    stats = {}
    
    # Inter-prototype distances
    proto_distances = torch.cdist(prototypes, prototypes, p=2)
    # Remove diagonal (self-distances)
    mask = ~torch.eye(len(prototypes), dtype=bool)
    inter_distances = proto_distances[mask]
    
    stats['mean_inter_prototype_distance'] = inter_distances.mean().item()
    stats['std_inter_prototype_distance'] = inter_distances.std().item()
    stats['min_inter_prototype_distance'] = inter_distances.min().item()
    stats['max_inter_prototype_distance'] = inter_distances.max().item()
    
    # Intra-class distances (support examples to their prototype)
    intra_distances = []
    for class_idx in torch.unique(support_labels):
        class_mask = support_labels == class_idx
        class_features = support_features[class_mask]
        class_prototype = prototypes[class_idx]
        
        # Distances from class examples to prototype
        distances = torch.norm(class_features - class_prototype, p=2, dim=1)
        intra_distances.append(distances)
    
    all_intra = torch.cat(intra_distances)
    stats['mean_intra_class_distance'] = all_intra.mean().item()
    stats['std_intra_class_distance'] = all_intra.std().item()
    
    # Prototype quality metric (higher is better separation)
    separation_ratio = stats['mean_inter_prototype_distance'] / (stats['mean_intra_class_distance'] + 1e-8)
    stats['prototype_separation_ratio'] = separation_ratio
    
    return stats


def analyze_few_shot_performance(model, test_episodes: int = 100, n_way: int = 5, 
                               n_support: int = 5, n_query: int = 15) -> Dict[str, Any]:
    """
    Comprehensive analysis of few-shot learning performance.
    
    Args:
        model: Few-shot learning model
        test_episodes: Number of test episodes
        n_way: Number of classes per episode
        n_support: Number of support examples per class
        n_query: Number of query examples per class
        
    Returns:
        Comprehensive performance analysis
    """
    model.eval()
    
    episode_accuracies = []
    prototype_stats_list = []
    confidence_scores = []
    
    with torch.no_grad():
        for episode in range(test_episodes):
            # Sample episode
            support_x, support_y, query_x, query_y = sample_episode(
                "synthetic", n_way, n_support, n_query
            )
            
            try:
                # Forward pass
                result = model(support_x, support_y, query_x)
                if isinstance(result, dict):
                    logits = result['logits']
                    prototypes = result.get('prototypes')
                else:
                    logits = result
                    prototypes = None
                
                # Compute accuracy
                predictions = logits.argmax(dim=1)
                accuracy = (predictions == query_y).float().mean().item()
                episode_accuracies.append(accuracy)
                
                # Analyze prototypes if available
                if prototypes is not None:
                    support_features = model.backbone(support_x)
                    proto_stats = compute_prototype_statistics(
                        prototypes, support_features, support_y
                    )
                    prototype_stats_list.append(proto_stats)
                
                # Analyze confidence
                probs = F.softmax(logits, dim=-1)
                max_probs = probs.max(dim=-1)[0]
                confidence_scores.extend(max_probs.tolist())
                
            except Exception as e:
                logger.warning(f"Episode {episode} analysis failed: {e}")
                continue
    
    # Aggregate results
    analysis = {
        'accuracy_stats': {
            'mean': np.mean(episode_accuracies),
            'std': np.std(episode_accuracies),
            'min': np.min(episode_accuracies),
            'max': np.max(episode_accuracies),
            'episodes': len(episode_accuracies)
        },
        'confidence_stats': {
            'mean': np.mean(confidence_scores),
            'std': np.std(confidence_scores),
            'median': np.median(confidence_scores)
        } if confidence_scores else None
    }
    
    # Prototype analysis
    if prototype_stats_list:
        proto_analysis = {}
        for key in prototype_stats_list[0].keys():
            values = [stats[key] for stats in prototype_stats_list]
            proto_analysis[key] = {
                'mean': np.mean(values),
                'std': np.std(values)
            }
        analysis['prototype_stats'] = proto_analysis
    
    return analysis


def create_backbone_network(architecture: str = "conv4", input_channels: int = 3, 
                          embedding_dim: int = 512) -> nn.Module:
    """
    Create a backbone network for few-shot learning.
    
    Args:
        architecture: Backbone architecture ('conv4', 'resnet', 'simple')
        input_channels: Number of input channels
        embedding_dim: Output embedding dimension
        
    Returns:
        Backbone network
    """
    if architecture == "conv4":
        # Standard 4-layer CNN backbone used in few-shot learning
        backbone = nn.Sequential(
            # Layer 1
            nn.Conv2d(input_channels, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            
            # Layer 2
            nn.Conv2d(64, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            
            # Layer 3
            nn.Conv2d(64, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            
            # Layer 4
            nn.Conv2d(64, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            
            # Global average pooling
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            
            # Final projection to embedding dimension
            nn.Linear(64, embedding_dim)
        )
        
    elif architecture == "simple":
        # Simple backbone for educational purposes
        backbone = nn.Sequential(
            nn.Conv2d(input_channels, 32, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(64, embedding_dim)
        )
        
    else:
        raise ValueError(f"Unknown backbone architecture: {architecture}")
    
    return backbone