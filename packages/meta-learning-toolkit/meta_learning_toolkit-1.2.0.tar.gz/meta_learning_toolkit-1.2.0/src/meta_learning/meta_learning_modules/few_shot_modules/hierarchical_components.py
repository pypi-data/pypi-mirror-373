"""
Hierarchical Prototype Components for Few-Shot Learning
======================================================

Comprehensive implementation of hierarchical prototype methods for 
improved few-shot learning performance.

Based on research from:
- Hierarchical Prototypes (Chen et al., 2019)
- Tree-structured Prototypes (Liu et al., 2020)
- Multi-level Few-shot Learning (Ye et al., 2020)
- Coarse-to-Fine Few-shot Learning (Zhang et al., 2021)

Author: Benedict Chen (benedict@benedictchen.com)
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple, Optional, Union, Any
import numpy as np
from dataclasses import dataclass
from sklearn.cluster import KMeans
import math


@dataclass
class HierarchicalConfig:
    """Configuration for hierarchical prototype methods."""
    method: str = "multi_level"  # multi_level, tree_structured, coarse_to_fine, adaptive_hierarchy
    num_levels: int = 3
    max_clusters: int = 4
    hierarchy_type: str = "attention_weighted"  # attention_weighted, tree_kmeans, learnable_hierarchy
    attention_heads: int = 8
    level_weights: Optional[List[float]] = None
    temperature: float = 1.0
    diversity_loss_weight: float = 0.1
    hierarchy_dropout: float = 0.1
    use_level_adaptation: bool = True


class MultiLevelHierarchicalPrototypes(nn.Module):
    """
    Multi-level Hierarchical Prototypes (Chen et al., 2019).
    
    Creates prototypes at multiple levels of abstraction with learnable weights.
    """
    
    def __init__(self, embedding_dim: int, num_levels: int = 3, attention_heads: int = 8):
        super().__init__()
        self.embedding_dim = embedding_dim
        self.num_levels = num_levels
        self.attention_heads = attention_heads
        
        # Level-specific prototype networks
        self.prototype_networks = nn.ModuleList([
            nn.Sequential(
                nn.Linear(embedding_dim, embedding_dim),
                nn.LayerNorm(embedding_dim),
                nn.ReLU(),
                nn.Dropout(0.1),
                nn.Linear(embedding_dim, embedding_dim)
            ) for _ in range(num_levels)
        ])
        
        # Multi-head attention for level weighting
        self.level_attention = nn.MultiheadAttention(
            embedding_dim, attention_heads, batch_first=True, dropout=0.1
        )
        
        # Learnable level importance weights
        self.level_weights = nn.Parameter(torch.ones(num_levels) / num_levels)
        
        # Level-specific temperature parameters
        self.level_temperatures = nn.Parameter(torch.ones(num_levels))
        
    def forward(self, support_features: torch.Tensor, support_labels: torch.Tensor, 
                query_features: torch.Tensor = None) -> Dict[str, torch.Tensor]:
        """
        Compute hierarchical prototypes at multiple levels.
        
        Args:
            support_features: [n_support, embedding_dim]
            support_labels: [n_support]
            query_features: [n_query, embedding_dim] (optional)
            
        Returns:
            Dictionary with prototypes and level information
        """
        unique_labels = torch.unique(support_labels)
        n_classes = len(unique_labels)
        
        # Compute prototypes at each level
        level_prototypes = []
        level_attention_weights = []
        
        for level, proto_net in enumerate(self.prototype_networks):
            # Transform features for this level
            level_features = proto_net(support_features)
            
            # Compute prototypes for each class at this level
            level_class_prototypes = []
            for class_idx in unique_labels:
                class_mask = support_labels == class_idx
                class_features = level_features[class_mask]
                
                if len(class_features) > 1:
                    # Use attention to weight class examples
                    class_context = class_features.mean(dim=0, keepdim=True)  # [1, embedding_dim]
                    attended_features, attention_weights = self.level_attention(
                        class_context,  # query
                        class_features.unsqueeze(0),  # key
                        class_features.unsqueeze(0)   # value
                    )
                    prototype = attended_features.squeeze(0).squeeze(0)
                    level_attention_weights.append(attention_weights.squeeze())
                else:
                    prototype = class_features.mean(dim=0)
                    level_attention_weights.append(torch.ones(1))
                
                level_class_prototypes.append(prototype)
            
            level_prototypes.append(torch.stack(level_class_prototypes))
        
        # Weighted combination of multi-level prototypes
        level_weights_normalized = F.softmax(self.level_weights, dim=0)
        
        final_prototypes = torch.zeros_like(level_prototypes[0])
        for i, (prototypes, weight, temp) in enumerate(zip(level_prototypes, level_weights_normalized, self.level_temperatures)):
            final_prototypes += weight * prototypes / temp
            
        return {
            'prototypes': final_prototypes,
            'level_prototypes': level_prototypes,
            'level_weights': level_weights_normalized,
            'attention_weights': level_attention_weights,
            'level_temperatures': self.level_temperatures
        }


class TreeStructuredHierarchicalPrototypes(nn.Module):
    """
    Tree-structured Hierarchical Prototypes using clustering.
    
    Builds a hierarchy using k-means clustering with learnable refinements.
    """
    
    def __init__(self, embedding_dim: int, max_clusters: int = 4, num_levels: int = 2):
        super().__init__()
        self.embedding_dim = embedding_dim
        self.max_clusters = max_clusters
        self.num_levels = num_levels
        
        # Cluster assignment networks
        self.cluster_heads = nn.ModuleList([
            nn.Sequential(
                nn.Linear(embedding_dim, embedding_dim // 2),
                nn.ReLU(),
                nn.Linear(embedding_dim // 2, max_clusters),
                nn.Softmax(dim=-1)
            ) for _ in range(num_levels)
        ])
        
        # Prototype refinement networks
        self.prototype_refiners = nn.ModuleList([
            nn.Sequential(
                nn.Linear(embedding_dim, embedding_dim),
                nn.LayerNorm(embedding_dim),
                nn.ReLU(),
                nn.Linear(embedding_dim, embedding_dim)
            ) for _ in range(num_levels)
        ])
        
        # Hierarchy combination network
        self.hierarchy_combiner = nn.Sequential(
            nn.Linear(embedding_dim * num_levels, embedding_dim),
            nn.ReLU(),
            nn.Linear(embedding_dim, embedding_dim)
        )
        
    def forward(self, support_features: torch.Tensor, support_labels: torch.Tensor, 
                query_features: torch.Tensor = None) -> Dict[str, torch.Tensor]:
        """
        Build tree-structured hierarchical prototypes.
        
        Args:
            support_features: [n_support, embedding_dim]
            support_labels: [n_support]
            query_features: [n_query, embedding_dim] (optional)
            
        Returns:
            Dictionary with hierarchical prototype structure
        """
        unique_labels = torch.unique(support_labels)
        n_classes = len(unique_labels)
        
        hierarchical_prototypes = {}
        level_prototypes = []
        
        for class_idx in unique_labels:
            class_mask = support_labels == class_idx
            class_features = support_features[class_mask]
            
            class_hierarchy = {}
            class_level_prototypes = []
            
            current_features = class_features
            
            for level in range(self.num_levels):
                # Get cluster assignments for this level
                cluster_probs = self.cluster_heads[level](current_features)  # [n_samples, max_clusters]
                cluster_assignments = torch.argmax(cluster_probs, dim=1)
                
                # Create sub-prototypes for each cluster
                level_sub_prototypes = []
                level_cluster_info = []
                
                for cluster_id in range(self.max_clusters):
                    cluster_mask = cluster_assignments == cluster_id
                    if cluster_mask.sum() > 0:
                        cluster_features = current_features[cluster_mask]
                        
                        # Compute cluster prototype
                        cluster_prototype = cluster_features.mean(dim=0)
                        
                        # Refine prototype
                        refined_prototype = self.prototype_refiners[level](cluster_prototype)
                        level_sub_prototypes.append(refined_prototype)
                        
                        level_cluster_info.append({
                            'cluster_id': cluster_id,
                            'size': cluster_mask.sum().item(),
                            'prototype': refined_prototype
                        })
                
                if level_sub_prototypes:
                    # Combine sub-prototypes for this level
                    level_prototype = torch.stack(level_sub_prototypes).mean(dim=0)
                    class_level_prototypes.append(level_prototype)
                    class_hierarchy[f'level_{level}'] = {
                        'prototype': level_prototype,
                        'sub_prototypes': level_sub_prototypes,
                        'cluster_info': level_cluster_info
                    }
                    
                    # Update features for next level (use prototype as context)
                    current_features = current_features + level_prototype.unsqueeze(0)
            
            # Combine all levels for final class prototype
            if class_level_prototypes:
                combined_features = torch.cat(class_level_prototypes)
                final_prototype = self.hierarchy_combiner(combined_features)
                class_hierarchy['final_prototype'] = final_prototype
            
            hierarchical_prototypes[class_idx.item()] = class_hierarchy
            level_prototypes.append(final_prototype if 'final_prototype' in class_hierarchy 
                                  else class_features.mean(dim=0))
        
        return {
            'prototypes': torch.stack(level_prototypes),
            'hierarchical_structure': hierarchical_prototypes,
            'num_levels': self.num_levels
        }


class CoarseToFineHierarchicalPrototypes(nn.Module):
    """
    Coarse-to-Fine Hierarchical Prototypes (Zhang et al., 2021).
    
    Progressively refines prototypes from coarse to fine representations.
    """
    
    def __init__(self, embedding_dim: int, num_refinement_steps: int = 3):
        super().__init__()
        self.embedding_dim = embedding_dim
        self.num_refinement_steps = num_refinement_steps
        
        # Coarse-to-fine refinement networks
        self.refinement_networks = nn.ModuleList([
            nn.Sequential(
                nn.Linear(embedding_dim * 2, embedding_dim),  # [prototype, context]
                nn.LayerNorm(embedding_dim),
                nn.ReLU(),
                nn.Dropout(0.1),
                nn.Linear(embedding_dim, embedding_dim),
                nn.Tanh()  # Bounded refinement
            ) for _ in range(num_refinement_steps)
        ])
        
        # Context encoders for each refinement step
        self.context_encoders = nn.ModuleList([
            nn.Sequential(
                nn.Linear(embedding_dim, embedding_dim),
                nn.ReLU(),
                nn.Linear(embedding_dim, embedding_dim)
            ) for _ in range(num_refinement_steps)
        ])
        
        # Attention mechanisms for refinement
        self.refinement_attention = nn.ModuleList([
            nn.MultiheadAttention(embedding_dim, num_heads=4, batch_first=True)
            for _ in range(num_refinement_steps)
        ])
        
    def forward(self, support_features: torch.Tensor, support_labels: torch.Tensor, 
                query_features: torch.Tensor = None) -> Dict[str, torch.Tensor]:
        """
        Perform coarse-to-fine prototype refinement.
        
        Args:
            support_features: [n_support, embedding_dim]
            support_labels: [n_support]
            query_features: [n_query, embedding_dim] (optional)
            
        Returns:
            Dictionary with refinement progression
        """
        unique_labels = torch.unique(support_labels)
        n_classes = len(unique_labels)
        
        # Initialize with coarse prototypes (simple means)
        coarse_prototypes = []
        refinement_history = []
        
        for class_idx in unique_labels:
            class_mask = support_labels == class_idx
            class_features = support_features[class_mask]
            coarse_prototype = class_features.mean(dim=0)
            coarse_prototypes.append(coarse_prototype)
        
        current_prototypes = torch.stack(coarse_prototypes)
        refinement_history.append(current_prototypes.clone())
        
        # Iterative refinement
        for step in range(self.num_refinement_steps):
            refined_prototypes = []
            
            for i, class_idx in enumerate(unique_labels):
                class_mask = support_labels == class_idx
                class_features = support_features[class_mask]
                current_prototype = current_prototypes[i]
                
                # Create context for this refinement step
                if query_features is not None:
                    # Use query features as context if available
                    context_features = torch.cat([class_features, query_features], dim=0)
                else:
                    context_features = class_features
                
                context = self.context_encoders[step](context_features).mean(dim=0)
                
                # Apply attention-based refinement
                prototype_query = current_prototype.unsqueeze(0).unsqueeze(0)  # [1, 1, embedding_dim]
                context_kv = context_features.unsqueeze(0)  # [1, n_context, embedding_dim]
                
                attended_prototype, attention_weights = self.refinement_attention[step](
                    prototype_query, context_kv, context_kv
                )
                attended_prototype = attended_prototype.squeeze(0).squeeze(0)
                
                # Refine prototype
                refinement_input = torch.cat([current_prototype, context])
                refinement_delta = self.refinement_networks[step](refinement_input)
                
                # Apply bounded refinement
                refined_prototype = current_prototype + 0.1 * refinement_delta
                refined_prototypes.append(refined_prototype)
            
            current_prototypes = torch.stack(refined_prototypes)
            refinement_history.append(current_prototypes.clone())
        
        return {
            'prototypes': current_prototypes,
            'refinement_history': refinement_history,
            'coarse_prototypes': refinement_history[0],
            'fine_prototypes': refinement_history[-1],
            'num_refinement_steps': self.num_refinement_steps
        }


class AdaptiveHierarchicalPrototypes(nn.Module):
    """
    Adaptive Hierarchical Prototypes with learned hierarchy structure.
    
    Learns the optimal hierarchy structure for each task.
    """
    
    def __init__(self, embedding_dim: int, max_levels: int = 4):
        super().__init__()
        self.embedding_dim = embedding_dim
        self.max_levels = max_levels
        
        # Hierarchy structure predictor
        self.structure_predictor = nn.Sequential(
            nn.Linear(embedding_dim, embedding_dim // 2),
            nn.ReLU(),
            nn.Linear(embedding_dim // 2, max_levels),
            nn.Sigmoid()  # Level activation probabilities
        )
        
        # Level-adaptive prototype networks
        self.adaptive_networks = nn.ModuleList([
            nn.Sequential(
                nn.Linear(embedding_dim + 1, embedding_dim),  # +1 for level embedding
                nn.LayerNorm(embedding_dim),
                nn.ReLU(),
                nn.Linear(embedding_dim, embedding_dim)
            ) for _ in range(max_levels)
        ])
        
        # Level embeddings
        self.level_embeddings = nn.Embedding(max_levels, 1)
        
        # Adaptive fusion network
        self.adaptive_fusion = nn.Sequential(
            nn.Linear(embedding_dim * max_levels + max_levels, embedding_dim),
            nn.ReLU(),
            nn.Linear(embedding_dim, embedding_dim)
        )
        
    def forward(self, support_features: torch.Tensor, support_labels: torch.Tensor, 
                query_features: torch.Tensor = None) -> Dict[str, torch.Tensor]:
        """
        Adaptively build hierarchical prototypes.
        
        Args:
            support_features: [n_support, embedding_dim]
            support_labels: [n_support]
            query_features: [n_query, embedding_dim] (optional)
            
        Returns:
            Dictionary with adaptive hierarchy information
        """
        unique_labels = torch.unique(support_labels)
        n_classes = len(unique_labels)
        
        # Predict hierarchy structure for this task
        task_context = support_features.mean(dim=0)  # Global task representation
        level_activations = self.structure_predictor(task_context)  # [max_levels]
        
        # Compute prototypes at each active level
        adaptive_prototypes = []
        level_contributions = []
        
        for class_idx in unique_labels:
            class_mask = support_labels == class_idx
            class_features = support_features[class_mask]
            
            class_level_prototypes = []
            class_level_weights = []
            
            for level in range(self.max_levels):
                level_activation = level_activations[level]
                
                if level_activation > 0.1:  # Only use sufficiently active levels
                    # Add level embedding to features
                    level_emb = self.level_embeddings(torch.tensor(level)).squeeze()
                    level_features = torch.cat([
                        class_features, 
                        level_emb.expand(len(class_features), 1)
                    ], dim=1)
                    
                    # Transform features for this level
                    transformed_features = self.adaptive_networks[level](level_features)
                    level_prototype = transformed_features.mean(dim=0)
                    
                    class_level_prototypes.append(level_prototype)
                    class_level_weights.append(level_activation)
            
            if class_level_prototypes:
                # Adaptive fusion of level prototypes
                stacked_prototypes = torch.stack(class_level_prototypes)
                weights = torch.stack(class_level_weights)
                
                # Create fusion input
                fusion_input = torch.cat([
                    stacked_prototypes.flatten(),
                    weights
                ])
                
                # Pad if necessary
                expected_size = self.embedding_dim * self.max_levels + self.max_levels
                if len(fusion_input) < expected_size:
                    padding = torch.zeros(expected_size - len(fusion_input))
                    fusion_input = torch.cat([fusion_input, padding])
                
                adaptive_prototype = self.adaptive_fusion(fusion_input)
                adaptive_prototypes.append(adaptive_prototype)
                level_contributions.append(weights)
            else:
                # Fallback to simple mean
                adaptive_prototypes.append(class_features.mean(dim=0))
                level_contributions.append(torch.zeros(self.max_levels))
        
        return {
            'prototypes': torch.stack(adaptive_prototypes),
            'level_activations': level_activations,
            'level_contributions': level_contributions,
            'active_levels': (level_activations > 0.1).sum().item()
        }


class HierarchicalPrototypes(nn.Module):
    """
    Unified Hierarchical Prototypes Module.
    
    Supports multiple hierarchical prototype methods with configurable options.
    """
    
    def __init__(self, embedding_dim: int, config: HierarchicalConfig = None):
        super().__init__()
        self.embedding_dim = embedding_dim
        self.config = config or HierarchicalConfig()
        
        # Initialize hierarchical method based on configuration
        if self.config.method == "multi_level":
            self.hierarchical_module = MultiLevelHierarchicalPrototypes(
                embedding_dim, self.config.num_levels, self.config.attention_heads
            )
        elif self.config.method == "tree_structured":
            self.hierarchical_module = TreeStructuredHierarchicalPrototypes(
                embedding_dim, self.config.max_clusters, self.config.num_levels
            )
        elif self.config.method == "coarse_to_fine":
            self.hierarchical_module = CoarseToFineHierarchicalPrototypes(
                embedding_dim, self.config.num_levels
            )
        elif self.config.method == "adaptive_hierarchy":
            self.hierarchical_module = AdaptiveHierarchicalPrototypes(
                embedding_dim, self.config.num_levels
            )
        else:
            raise ValueError(f"Unknown hierarchical method: {self.config.method}")
        
        # Optional level adaptation network
        if self.config.use_level_adaptation:
            self.level_adapter = nn.Sequential(
                nn.Linear(embedding_dim, embedding_dim),
                nn.Dropout(self.config.hierarchy_dropout),
                nn.ReLU(),
                nn.Linear(embedding_dim, embedding_dim)
            )
        
    def forward(self, support_features: torch.Tensor, support_labels: torch.Tensor, 
                query_features: torch.Tensor = None) -> Dict[str, torch.Tensor]:
        """
        Compute hierarchical prototypes using the configured method.
        
        Args:
            support_features: [n_support, embedding_dim]
            support_labels: [n_support]
            query_features: [n_query, embedding_dim] (optional)
            
        Returns:
            Dictionary with hierarchical prototype information
        """
        # Apply hierarchical method
        result = self.hierarchical_module(support_features, support_labels, query_features)
        
        # Apply level adaptation if enabled
        if self.config.use_level_adaptation and hasattr(self, 'level_adapter'):
            adapted_prototypes = self.level_adapter(result['prototypes'])
            result['prototypes'] = adapted_prototypes
            result['adapted'] = True
        
        return result


# Factory functions for easy creation
def create_hierarchical_prototypes(method: str = "multi_level", 
                                 embedding_dim: int = 512, 
                                 **kwargs) -> HierarchicalPrototypes:
    """Factory function to create hierarchical prototype modules."""
    config = HierarchicalConfig(method=method, **kwargs)
    return HierarchicalPrototypes(embedding_dim, config)


def create_multi_level_prototypes(embedding_dim: int, num_levels: int = 3, 
                                 attention_heads: int = 8) -> HierarchicalPrototypes:
    """Create multi-level hierarchical prototypes."""
    config = HierarchicalConfig(
        method="multi_level",
        num_levels=num_levels,
        attention_heads=attention_heads
    )
    return HierarchicalPrototypes(embedding_dim, config)


def create_tree_prototypes(embedding_dim: int, max_clusters: int = 4, 
                          num_levels: int = 2) -> HierarchicalPrototypes:
    """Create tree-structured hierarchical prototypes."""
    config = HierarchicalConfig(
        method="tree_structured",
        max_clusters=max_clusters,
        num_levels=num_levels
    )
    return HierarchicalPrototypes(embedding_dim, config)


def create_coarse_to_fine_prototypes(embedding_dim: int, 
                                    num_refinement_steps: int = 3) -> HierarchicalPrototypes:
    """Create coarse-to-fine hierarchical prototypes."""
    config = HierarchicalConfig(
        method="coarse_to_fine",
        num_levels=num_refinement_steps
    )
    return HierarchicalPrototypes(embedding_dim, config)


def create_adaptive_prototypes(embedding_dim: int, max_levels: int = 4) -> HierarchicalPrototypes:
    """Create adaptive hierarchical prototypes."""
    config = HierarchicalConfig(
        method="adaptive_hierarchy",
        num_levels=max_levels
    )
    return HierarchicalPrototypes(embedding_dim, config)