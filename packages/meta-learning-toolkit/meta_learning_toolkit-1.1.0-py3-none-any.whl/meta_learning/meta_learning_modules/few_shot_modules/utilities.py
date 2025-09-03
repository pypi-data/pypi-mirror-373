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


def sample_episode(dataset_name: str, n_way: int = 5, n_support: int = 5, n_query: int = 15):
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
    # Placeholder implementation - replace with actual dataset loading
    if dataset_name == "omniglot":
        input_size = (1, 28, 28)
        n_way = 20  # Standard for Omniglot
    elif dataset_name in ["miniImageNet", "tieredImageNet"]:
        input_size = (3, 84, 84)
        n_way = 5   # Standard for ImageNet variants
    else:
        input_size = (3, 32, 32)  # Default
    
    # Generate synthetic data for demonstration
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