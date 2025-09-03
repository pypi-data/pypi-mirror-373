"""
Task-Adaptive Prototype Components for Few-Shot Learning
=======================================================

Comprehensive implementation of task-adaptive prototype methods that
adjust prototypes based on the specific characteristics of each task.

Based on research from:
- Task-Adaptive Prototypes (Li et al., 2020)
- Meta-learning Task Adaptation (Finn et al., 2017)
- Attention-based Task Adaptation (Baik et al., 2020)
- Context-dependent Few-shot Learning (Ye et al., 2021)

Author: Benedict Chen (benedict@benedictchen.com)
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple, Optional, Union, Any
import numpy as np
from dataclasses import dataclass
import math


@dataclass
class TaskAdaptiveConfig:
    """Configuration for task-adaptive prototype methods."""
    method: str = "attention_based"  # attention_based, meta_learning, context_dependent, transformer_based
    adaptation_layers: int = 2
    attention_heads: int = 8
    adaptation_dim: int = 128
    meta_lr: float = 0.01
    temperature: float = 1.0
    context_pooling: str = "attention"  # mean, attention, max, learned
    adaptation_dropout: float = 0.1
    use_residual_adaptation: bool = True
    adaptation_steps: int = 5
    normalization: str = "layer"  # layer, batch, instance


class AttentionBasedTaskAdaptation(nn.Module):
    """
    Attention-based Task Adaptive Prototypes (Baik et al., 2020).
    
    Uses multi-head attention to adapt prototypes based on task context.
    """
    
    def __init__(self, embedding_dim: int, adaptation_layers: int = 2, 
                 attention_heads: int = 8, adaptation_dropout: float = 0.1):
        super().__init__()
        self.embedding_dim = embedding_dim
        self.adaptation_layers = adaptation_layers
        self.attention_heads = attention_heads
        
        # Task context encoder
        self.task_encoder = nn.Sequential(*[
            nn.Sequential(
                nn.Linear(embedding_dim, embedding_dim),
                nn.LayerNorm(embedding_dim),
                nn.ReLU(),
                nn.Dropout(adaptation_dropout)
            ) for _ in range(adaptation_layers)
        ])
        
        # Multi-head attention for prototype adaptation
        self.adaptation_attention = nn.MultiheadAttention(
            embedding_dim, attention_heads, batch_first=True, dropout=adaptation_dropout
        )
        
        # Context-aware transformation
        self.context_transform = nn.Sequential(
            nn.Linear(embedding_dim * 2, embedding_dim),
            nn.LayerNorm(embedding_dim),
            nn.ReLU(),
            nn.Linear(embedding_dim, embedding_dim)
        )
        
        # Adaptation gate
        self.adaptation_gate = nn.Sequential(
            nn.Linear(embedding_dim * 2, embedding_dim),
            nn.Sigmoid()
        )
        
        # Output projection
        self.output_projection = nn.Linear(embedding_dim, embedding_dim)
        
    def forward(self, support_features: torch.Tensor, support_labels: torch.Tensor, 
                query_features: torch.Tensor = None) -> Dict[str, torch.Tensor]:
        """
        Perform attention-based task adaptation.
        
        Args:
            support_features: [n_support, embedding_dim]
            support_labels: [n_support]
            query_features: [n_query, embedding_dim] (optional)
            
        Returns:
            Dictionary with adapted prototypes and attention information
        """
        unique_labels = torch.unique(support_labels)
        n_classes = len(unique_labels)
        
        # Encode task context from support set
        task_context = self.task_encoder(support_features.mean(dim=0, keepdim=True))  # [1, embedding_dim]
        
        # Compute base prototypes
        base_prototypes = []
        for class_idx in unique_labels:
            class_mask = support_labels == class_idx
            class_features = support_features[class_mask]
            base_prototype = class_features.mean(dim=0)
            base_prototypes.append(base_prototype)
        
        base_prototypes = torch.stack(base_prototypes)  # [n_classes, embedding_dim]
        
        # Adapt prototypes using attention with task context
        prototype_queries = base_prototypes.unsqueeze(0)  # [1, n_classes, embedding_dim]
        task_keys = task_context.repeat(n_classes, 1).unsqueeze(0)  # [1, n_classes, embedding_dim]
        task_values = base_prototypes.unsqueeze(0)  # [1, n_classes, embedding_dim]
        
        attended_prototypes, attention_weights = self.adaptation_attention(
            prototype_queries, task_keys, task_values
        )
        attended_prototypes = attended_prototypes.squeeze(0)  # [n_classes, embedding_dim]
        
        # Context-aware transformation
        context_input = torch.cat([
            base_prototypes, 
            task_context.repeat(n_classes, 1)
        ], dim=1)  # [n_classes, embedding_dim * 2]
        
        context_adapted = self.context_transform(context_input)  # [n_classes, embedding_dim]
        
        # Gated combination
        gate_input = torch.cat([attended_prototypes, context_adapted], dim=1)
        adaptation_gate = self.adaptation_gate(gate_input)  # [n_classes, embedding_dim]
        
        adapted_prototypes = (adaptation_gate * attended_prototypes + 
                            (1 - adaptation_gate) * context_adapted)
        
        # Final projection
        final_prototypes = self.output_projection(adapted_prototypes)
        
        return {
            'prototypes': final_prototypes,
            'base_prototypes': base_prototypes,
            'attention_weights': attention_weights.squeeze(0),
            'adaptation_gates': adaptation_gate,
            'task_context': task_context.squeeze(0)
        }


class MetaLearningTaskAdaptation(nn.Module):
    """
    Meta-learning based Task Adaptation (Finn et al., 2017).
    
    Uses gradient-based meta-learning for prototype adaptation.
    """
    
    def __init__(self, embedding_dim: int, meta_lr: float = 0.01, 
                 adaptation_steps: int = 5):
        super().__init__()
        self.embedding_dim = embedding_dim
        self.meta_lr = meta_lr
        self.adaptation_steps = adaptation_steps
        
        # Adaptation network
        self.adaptation_network = nn.Sequential(
            nn.Linear(embedding_dim * 2, embedding_dim),  # [prototype, task_context]
            nn.LayerNorm(embedding_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(embedding_dim, embedding_dim),
            nn.Tanh()  # Bounded adaptation
        )
        
        # Task context encoder
        self.context_encoder = nn.Sequential(
            nn.Linear(embedding_dim, embedding_dim),
            nn.ReLU(),
            nn.Linear(embedding_dim, embedding_dim)
        )
        
        # Meta parameters for adaptation
        self.meta_parameters = nn.ParameterDict({
            'adaptation_weights': nn.Parameter(torch.randn(embedding_dim, embedding_dim) * 0.01),
            'adaptation_bias': nn.Parameter(torch.zeros(embedding_dim))
        })
        
    def forward(self, support_features: torch.Tensor, support_labels: torch.Tensor, 
                query_features: torch.Tensor = None) -> Dict[str, torch.Tensor]:
        """
        Perform meta-learning based task adaptation.
        
        Args:
            support_features: [n_support, embedding_dim]
            support_labels: [n_support]
            query_features: [n_query, embedding_dim] (optional)
            
        Returns:
            Dictionary with adapted prototypes and meta information
        """
        unique_labels = torch.unique(support_labels)
        n_classes = len(unique_labels)
        
        # Compute task context vector
        task_context = self.context_encoder(support_features.mean(dim=0))
        
        # Compute base prototypes
        adapted_prototypes = []
        adaptation_history = []
        
        for class_idx in unique_labels:
            class_mask = support_labels == class_idx
            class_features = support_features[class_mask]
            base_prototype = class_features.mean(dim=0)
            
            # Initialize adapted prototype
            current_prototype = base_prototype.clone()
            class_adaptation_history = [current_prototype.clone()]
            
            # Iterative adaptation
            for step in range(self.adaptation_steps):
                # Create adaptation input
                adaptation_input = torch.cat([current_prototype, task_context])
                
                # Compute adaptation delta
                adaptation_delta = self.adaptation_network(adaptation_input)
                
                # Apply meta-learned adaptation
                meta_adapted = torch.matmul(adaptation_delta, self.meta_parameters['adaptation_weights']) + \
                             self.meta_parameters['adaptation_bias']
                
                # Update prototype with bounded adaptation
                current_prototype = current_prototype + self.meta_lr * meta_adapted
                class_adaptation_history.append(current_prototype.clone())
            
            adapted_prototypes.append(current_prototype)
            adaptation_history.append(class_adaptation_history)
        
        return {
            'prototypes': torch.stack(adapted_prototypes),
            'adaptation_history': adaptation_history,
            'task_context': task_context,
            'adaptation_steps': self.adaptation_steps
        }


class ContextDependentTaskAdaptation(nn.Module):
    """
    Context-dependent Task Adaptation (Ye et al., 2021).
    
    Adapts prototypes based on global and local task contexts.
    """
    
    def __init__(self, embedding_dim: int, adaptation_dim: int = 128, 
                 context_pooling: str = "attention"):
        super().__init__()
        self.embedding_dim = embedding_dim
        self.adaptation_dim = adaptation_dim
        self.context_pooling = context_pooling
        
        # Global context encoder
        self.global_context_encoder = nn.Sequential(
            nn.Linear(embedding_dim, adaptation_dim),
            nn.ReLU(),
            nn.Linear(adaptation_dim, adaptation_dim)
        )
        
        # Local context encoder
        self.local_context_encoder = nn.Sequential(
            nn.Linear(embedding_dim, adaptation_dim),
            nn.ReLU(), 
            nn.Linear(adaptation_dim, adaptation_dim)
        )
        
        # Context pooling mechanisms
        if context_pooling == "attention":
            self.context_attention = nn.MultiheadAttention(
                adaptation_dim, num_heads=4, batch_first=True
            )
        elif context_pooling == "learned":
            self.context_pooling_weights = nn.Parameter(torch.randn(adaptation_dim))
        
        # Context fusion network
        self.context_fusion = nn.Sequential(
            nn.Linear(adaptation_dim * 2, adaptation_dim),
            nn.ReLU(),
            nn.Linear(adaptation_dim, embedding_dim)
        )
        
        # Prototype adaptation network
        self.prototype_adaptation = nn.Sequential(
            nn.Linear(embedding_dim * 2, embedding_dim),  # [prototype, context]
            nn.LayerNorm(embedding_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(embedding_dim, embedding_dim)
        )
        
    def _pool_context(self, contexts: torch.Tensor) -> torch.Tensor:
        """Pool context features using the specified method."""
        if self.context_pooling == "mean":
            return contexts.mean(dim=0)
        elif self.context_pooling == "max":
            return contexts.max(dim=0)[0]
        elif self.context_pooling == "attention":
            # Self-attention pooling
            pooled, _ = self.context_attention(
                contexts.unsqueeze(0), contexts.unsqueeze(0), contexts.unsqueeze(0)
            )
            return pooled.squeeze(0).mean(dim=0)
        elif self.context_pooling == "learned":
            # Learned weighted pooling
            weights = F.softmax(torch.matmul(contexts, self.context_pooling_weights), dim=0)
            return torch.sum(contexts * weights.unsqueeze(1), dim=0)
        else:
            return contexts.mean(dim=0)
    
    def forward(self, support_features: torch.Tensor, support_labels: torch.Tensor, 
                query_features: torch.Tensor = None) -> Dict[str, torch.Tensor]:
        """
        Perform context-dependent task adaptation.
        
        Args:
            support_features: [n_support, embedding_dim]
            support_labels: [n_support]
            query_features: [n_query, embedding_dim] (optional)
            
        Returns:
            Dictionary with context-adapted prototypes
        """
        unique_labels = torch.unique(support_labels)
        n_classes = len(unique_labels)
        
        # Encode global task context
        global_contexts = self.global_context_encoder(support_features)
        global_context = self._pool_context(global_contexts)
        
        # Adapt prototypes for each class
        adapted_prototypes = []
        local_contexts = []
        
        for class_idx in unique_labels:
            class_mask = support_labels == class_idx
            class_features = support_features[class_mask]
            
            # Compute base prototype
            base_prototype = class_features.mean(dim=0)
            
            # Encode local class context
            class_local_contexts = self.local_context_encoder(class_features)
            local_context = self._pool_context(class_local_contexts)
            local_contexts.append(local_context)
            
            # Fuse global and local contexts
            fused_context = self.context_fusion(
                torch.cat([global_context, local_context])
            )
            
            # Adapt prototype using fused context
            adaptation_input = torch.cat([base_prototype, fused_context])
            adapted_prototype = self.prototype_adaptation(adaptation_input)
            
            adapted_prototypes.append(adapted_prototype)
        
        return {
            'prototypes': torch.stack(adapted_prototypes),
            'global_context': global_context,
            'local_contexts': torch.stack(local_contexts),
            'pooling_method': self.context_pooling
        }


class TransformerBasedTaskAdaptation(nn.Module):
    """
    Transformer-based Task Adaptation using cross-attention.
    
    Uses transformer architecture for sophisticated task adaptation.
    """
    
    def __init__(self, embedding_dim: int, num_layers: int = 2, 
                 attention_heads: int = 8, feedforward_dim: int = 512):
        super().__init__()
        self.embedding_dim = embedding_dim
        self.num_layers = num_layers
        
        # Positional encoding for prototypes
        self.positional_encoding = nn.Parameter(
            torch.randn(100, embedding_dim) * 0.1  # Support up to 100 classes
        )
        
        # Transformer encoder for task context
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embedding_dim,
            nhead=attention_heads,
            dim_feedforward=feedforward_dim,
            dropout=0.1,
            batch_first=True
        )
        self.task_encoder = nn.TransformerEncoder(encoder_layer, num_layers)
        
        # Cross-attention for prototype adaptation
        self.cross_attention_layers = nn.ModuleList([
            nn.TransformerDecoderLayer(
                d_model=embedding_dim,
                nhead=attention_heads,
                dim_feedforward=feedforward_dim,
                dropout=0.1,
                batch_first=True
            ) for _ in range(num_layers)
        ])
        
        # Final output projection
        self.output_projection = nn.Sequential(
            nn.Linear(embedding_dim, embedding_dim),
            nn.LayerNorm(embedding_dim)
        )
        
    def forward(self, support_features: torch.Tensor, support_labels: torch.Tensor, 
                query_features: torch.Tensor = None) -> Dict[str, torch.Tensor]:
        """
        Perform transformer-based task adaptation.
        
        Args:
            support_features: [n_support, embedding_dim]
            support_labels: [n_support]
            query_features: [n_query, embedding_dim] (optional)
            
        Returns:
            Dictionary with transformer-adapted prototypes
        """
        unique_labels = torch.unique(support_labels)
        n_classes = len(unique_labels)
        
        # Encode task context using transformer
        task_context = self.task_encoder(support_features.unsqueeze(0))  # [1, n_support, embedding_dim]
        
        # Compute base prototypes with positional encoding
        base_prototypes = []
        for i, class_idx in enumerate(unique_labels):
            class_mask = support_labels == class_idx
            class_features = support_features[class_mask]
            base_prototype = class_features.mean(dim=0)
            
            # Add positional encoding
            base_prototype = base_prototype + self.positional_encoding[i]
            base_prototypes.append(base_prototype)
        
        prototypes = torch.stack(base_prototypes).unsqueeze(0)  # [1, n_classes, embedding_dim]
        
        # Apply cross-attention layers
        attention_weights_history = []
        current_prototypes = prototypes
        
        for cross_attn_layer in self.cross_attention_layers:
            adapted_prototypes = cross_attn_layer(
                current_prototypes,  # target (prototypes)
                task_context         # memory (task context)
            )
            current_prototypes = adapted_prototypes
        
        # Final projection
        final_prototypes = self.output_projection(current_prototypes.squeeze(0))
        
        return {
            'prototypes': final_prototypes,
            'task_context': task_context.squeeze(0),
            'num_transformer_layers': self.num_layers
        }


class TaskAdaptivePrototypes(nn.Module):
    """
    Unified Task-Adaptive Prototypes Module.
    
    Supports multiple task adaptation methods with configurable options.
    """
    
    def __init__(self, embedding_dim: int, config: TaskAdaptiveConfig = None):
        super().__init__()
        self.embedding_dim = embedding_dim
        self.config = config or TaskAdaptiveConfig()
        
        # Initialize adaptation method based on configuration
        if self.config.method == "attention_based":
            self.adaptation_module = AttentionBasedTaskAdaptation(
                embedding_dim, self.config.adaptation_layers, 
                self.config.attention_heads, self.config.adaptation_dropout
            )
        elif self.config.method == "meta_learning":
            self.adaptation_module = MetaLearningTaskAdaptation(
                embedding_dim, self.config.meta_lr, self.config.adaptation_steps
            )
        elif self.config.method == "context_dependent":
            self.adaptation_module = ContextDependentTaskAdaptation(
                embedding_dim, self.config.adaptation_dim, self.config.context_pooling
            )
        elif self.config.method == "transformer_based":
            self.adaptation_module = TransformerBasedTaskAdaptation(
                embedding_dim, self.config.adaptation_layers, self.config.attention_heads
            )
        else:
            raise ValueError(f"Unknown adaptation method: {self.config.method}")
        
        # Optional residual connection
        if self.config.use_residual_adaptation:
            self.residual_weight = nn.Parameter(torch.tensor(0.5))
        
        # Temperature scaling
        self.temperature = nn.Parameter(torch.ones(1) * self.config.temperature)
        
    def forward(self, support_features: torch.Tensor, support_labels: torch.Tensor, 
                query_features: torch.Tensor = None) -> Dict[str, torch.Tensor]:
        """
        Perform task adaptation using the configured method.
        
        Args:
            support_features: [n_support, embedding_dim]
            support_labels: [n_support]
            query_features: [n_query, embedding_dim] (optional)
            
        Returns:
            Dictionary with task-adapted prototypes and method-specific information
        """
        # Get base prototypes for residual connection
        if self.config.use_residual_adaptation:
            unique_labels = torch.unique(support_labels)
            base_prototypes = []
            for class_idx in unique_labels:
                class_mask = support_labels == class_idx
                class_features = support_features[class_mask]
                base_prototype = class_features.mean(dim=0)
                base_prototypes.append(base_prototype)
            base_prototypes = torch.stack(base_prototypes)
        
        # Apply adaptation method
        result = self.adaptation_module(support_features, support_labels, query_features)
        
        # Apply residual connection if enabled
        if self.config.use_residual_adaptation:
            adapted_prototypes = (self.residual_weight * result['prototypes'] + 
                                (1 - self.residual_weight) * base_prototypes)
            result['prototypes'] = adapted_prototypes
            result['residual_weight'] = self.residual_weight.item()
        
        # Apply temperature scaling
        result['prototypes'] = result['prototypes'] / self.temperature
        result['temperature'] = self.temperature.item()
        result['adaptation_method'] = self.config.method
        
        return result


# Factory functions for easy creation
def create_task_adaptive_prototypes(method: str = "attention_based", 
                                   embedding_dim: int = 512, 
                                   **kwargs) -> TaskAdaptivePrototypes:
    """Factory function to create task-adaptive prototype modules."""
    config = TaskAdaptiveConfig(method=method, **kwargs)
    return TaskAdaptivePrototypes(embedding_dim, config)


def create_attention_adaptive_prototypes(embedding_dim: int, adaptation_layers: int = 2, 
                                       attention_heads: int = 8) -> TaskAdaptivePrototypes:
    """Create attention-based task-adaptive prototypes."""
    config = TaskAdaptiveConfig(
        method="attention_based",
        adaptation_layers=adaptation_layers,
        attention_heads=attention_heads
    )
    return TaskAdaptivePrototypes(embedding_dim, config)


def create_meta_adaptive_prototypes(embedding_dim: int, meta_lr: float = 0.01, 
                                   adaptation_steps: int = 5) -> TaskAdaptivePrototypes:
    """Create meta-learning based task-adaptive prototypes."""
    config = TaskAdaptiveConfig(
        method="meta_learning",
        meta_lr=meta_lr,
        adaptation_steps=adaptation_steps
    )
    return TaskAdaptivePrototypes(embedding_dim, config)


def create_context_adaptive_prototypes(embedding_dim: int, adaptation_dim: int = 128, 
                                     context_pooling: str = "attention") -> TaskAdaptivePrototypes:
    """Create context-dependent task-adaptive prototypes."""
    config = TaskAdaptiveConfig(
        method="context_dependent",
        adaptation_dim=adaptation_dim,
        context_pooling=context_pooling
    )
    return TaskAdaptivePrototypes(embedding_dim, config)


def create_transformer_adaptive_prototypes(embedding_dim: int, num_layers: int = 2, 
                                         attention_heads: int = 8) -> TaskAdaptivePrototypes:
    """Create transformer-based task-adaptive prototypes."""
    config = TaskAdaptiveConfig(
        method="transformer_based",
        adaptation_layers=num_layers,
        attention_heads=attention_heads
    )
    return TaskAdaptivePrototypes(embedding_dim, config)