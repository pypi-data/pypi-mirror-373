"""
Uncertainty-Aware Distance Components for Few-Shot Learning
=========================================================

Comprehensive implementation of uncertainty estimation methods for 
distance-based few-shot learning algorithms.

Based on research from:
- Monte Carlo Dropout (Gal & Ghahramani, 2016)
- Deep Ensembles (Lakshminarayanan et al., 2017) 
- Evidential Deep Learning (Sensoy et al., 2018)
- Bayesian Neural Networks (Blundell et al., 2015)

Author: Benedict Chen (benedict@benedictchen.com)
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple, Optional, Union
import numpy as np
from dataclasses import dataclass
import math


@dataclass
class UncertaintyConfig:
    """Configuration for uncertainty estimation methods."""
    method: str = "monte_carlo_dropout"  # monte_carlo_dropout, deep_ensemble, evidential, bayesian
    dropout_rate: float = 0.1
    n_samples: int = 10
    ensemble_size: int = 5
    temperature: float = 1.0
    evidential_lambda: float = 1.0
    bayesian_prior_sigma: float = 1.0
    uncertainty_weight: float = 1.0


class MonteCarloDropoutUncertainty(nn.Module):
    """
    Monte Carlo Dropout Uncertainty Estimation (Gal & Ghahramani, 2016).
    
    Uses multiple forward passes with dropout to estimate epistemic uncertainty.
    """
    
    def __init__(self, embedding_dim: int, dropout_rate: float = 0.1, n_samples: int = 10):
        super().__init__()
        self.embedding_dim = embedding_dim
        self.dropout_rate = dropout_rate
        self.n_samples = n_samples
        self.dropout = nn.Dropout(dropout_rate)
        
    def forward(self, query_features: torch.Tensor, prototypes: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Compute uncertainty-aware distances using Monte Carlo dropout.
        
        Args:
            query_features: [n_query, embedding_dim]
            prototypes: [n_prototypes, embedding_dim]
            
        Returns:
            mean_distances: [n_query, n_prototypes] 
            uncertainties: [n_query, n_prototypes]
        """
        distances = []
        
        # Multiple forward passes with dropout
        for _ in range(self.n_samples):
            # Apply dropout to query features
            query_uncertain = self.dropout(query_features)
            
            # Compute distances
            dist = torch.cdist(query_uncertain, prototypes, p=2)
            distances.append(dist)
        
        # Stack and compute statistics
        stacked_distances = torch.stack(distances)  # [n_samples, n_query, n_prototypes]
        mean_distances = stacked_distances.mean(dim=0)
        uncertainties = stacked_distances.std(dim=0)
        
        return mean_distances, uncertainties


class DeepEnsembleUncertainty(nn.Module):
    """
    Deep Ensemble Uncertainty Estimation (Lakshminarayanan et al., 2017).
    
    Uses multiple independently trained networks to estimate uncertainty.
    """
    
    def __init__(self, embedding_dim: int, n_models: int = 5):
        super().__init__()
        self.embedding_dim = embedding_dim
        self.n_models = n_models
        
        # Create ensemble of distance networks
        self.distance_networks = nn.ModuleList([
            nn.Sequential(
                nn.Linear(embedding_dim, embedding_dim // 2),
                nn.ReLU(),
                nn.Dropout(0.1),
                nn.Linear(embedding_dim // 2, embedding_dim),
                nn.Tanh()  # Bounded output
            ) for _ in range(n_models)
        ])
        
        # Diversity regularization weights
        self.diversity_weights = nn.Parameter(
            torch.randn(n_models, embedding_dim) * 0.1
        )
        
    def forward(self, query_features: torch.Tensor, prototypes: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Compute uncertainty-aware distances using deep ensembles.
        
        Args:
            query_features: [n_query, embedding_dim]
            prototypes: [n_prototypes, embedding_dim]
            
        Returns:
            mean_distances: [n_query, n_prototypes]
            uncertainties: [n_query, n_prototypes] 
        """
        ensemble_distances = []
        
        for i, distance_net in enumerate(self.distance_networks):
            # Transform query features with ensemble member
            query_transformed = distance_net(query_features)
            
            # Add diversity regularization
            query_diverse = query_transformed + self.diversity_weights[i]
            
            # Compute distances
            dist = torch.cdist(query_diverse, prototypes, p=2)
            ensemble_distances.append(dist)
        
        # Ensemble statistics
        stacked_distances = torch.stack(ensemble_distances)
        mean_distances = stacked_distances.mean(dim=0)
        uncertainties = stacked_distances.std(dim=0)
        
        return mean_distances, uncertainties


class EvidentialUncertaintyDistance(nn.Module):
    """
    Evidential Deep Learning Uncertainty (Sensoy et al., 2018).
    
    Models uncertainty using Dirichlet distributions and evidence.
    """
    
    def __init__(self, embedding_dim: int, num_classes: int, lambda_reg: float = 1.0):
        super().__init__()
        self.embedding_dim = embedding_dim
        self.num_classes = num_classes
        self.lambda_reg = lambda_reg
        
        # Evidence generation network
        self.evidence_head = nn.Sequential(
            nn.Linear(embedding_dim, embedding_dim // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(embedding_dim // 2, num_classes),
            nn.Softplus()  # Ensure positive evidence
        )
        
        # Prototype evidence network
        self.prototype_evidence = nn.Sequential(
            nn.Linear(embedding_dim, embedding_dim // 2),
            nn.ReLU(),
            nn.Linear(embedding_dim // 2, num_classes),
            nn.Softplus()
        )
        
    def forward(self, query_features: torch.Tensor, prototypes: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Compute evidential uncertainty-aware distances.
        
        Args:
            query_features: [n_query, embedding_dim]
            prototypes: [n_prototypes, embedding_dim]
            
        Returns:
            weighted_distances: [n_query, n_prototypes]
            uncertainties: [n_query, n_prototypes]
        """
        # Generate evidence for query features
        query_evidence = self.evidence_head(query_features)  # [n_query, num_classes]
        query_alpha = query_evidence + 1  # Dirichlet parameters
        query_strength = torch.sum(query_alpha, dim=1, keepdim=True)  # [n_query, 1]
        
        # Generate evidence for prototypes
        proto_evidence = self.prototype_evidence(prototypes)  # [n_prototypes, num_classes]
        proto_alpha = proto_evidence + 1
        proto_strength = torch.sum(proto_alpha, dim=1, keepdim=True)  # [n_prototypes, 1]
        
        # Compute uncertainties
        query_uncertainty = self.num_classes / query_strength  # [n_query, 1]
        proto_uncertainty = self.num_classes / proto_strength.T  # [1, n_prototypes]
        
        # Combine uncertainties
        combined_uncertainty = query_uncertainty + proto_uncertainty  # [n_query, n_prototypes]
        
        # Compute base distances
        base_distances = torch.cdist(query_features, prototypes, p=2)
        
        # Weight distances by uncertainty
        weighted_distances = base_distances * (1 + self.lambda_reg * combined_uncertainty)
        
        return weighted_distances, combined_uncertainty


class BayesianUncertaintyDistance(nn.Module):
    """
    Bayesian Neural Network Uncertainty (Blundell et al., 2015).
    
    Uses variational inference for uncertainty estimation.
    """
    
    def __init__(self, embedding_dim: int, prior_sigma: float = 1.0):
        super().__init__()
        self.embedding_dim = embedding_dim
        self.prior_sigma = prior_sigma
        
        # Variational parameters for weight distributions
        self.weight_mu = nn.Parameter(torch.randn(embedding_dim, embedding_dim) * 0.1)
        self.weight_rho = nn.Parameter(torch.randn(embedding_dim, embedding_dim) * 0.1)
        self.bias_mu = nn.Parameter(torch.zeros(embedding_dim))
        self.bias_rho = nn.Parameter(torch.ones(embedding_dim) * 0.1)
        
    def reparameterize(self, mu: torch.Tensor, rho: torch.Tensor) -> torch.Tensor:
        """Reparameterization trick for sampling from weight distribution."""
        sigma = torch.log1p(torch.exp(rho))
        epsilon = torch.randn_like(sigma)
        return mu + epsilon * sigma
        
    def forward(self, query_features: torch.Tensor, prototypes: torch.Tensor, 
                n_samples: int = 10) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Compute Bayesian uncertainty-aware distances.
        
        Args:
            query_features: [n_query, embedding_dim]
            prototypes: [n_prototypes, embedding_dim]
            n_samples: Number of weight samples
            
        Returns:
            mean_distances: [n_query, n_prototypes]
            uncertainties: [n_query, n_prototypes]
        """
        distances = []
        
        for _ in range(n_samples):
            # Sample weights from posterior
            weight = self.reparameterize(self.weight_mu, self.weight_rho)
            bias = self.reparameterize(self.bias_mu, self.bias_rho)
            
            # Transform query features
            query_transformed = torch.matmul(query_features, weight) + bias
            
            # Compute distances
            dist = torch.cdist(query_transformed, prototypes, p=2)
            distances.append(dist)
            
        # Compute statistics
        stacked_distances = torch.stack(distances)
        mean_distances = stacked_distances.mean(dim=0)
        uncertainties = stacked_distances.std(dim=0)
        
        return mean_distances, uncertainties
    
    def kl_divergence(self) -> torch.Tensor:
        """Compute KL divergence for variational inference."""
        # Weight KL divergence
        weight_sigma = torch.log1p(torch.exp(self.weight_rho))
        weight_kl = 0.5 * torch.sum(
            (self.weight_mu**2 + weight_sigma**2) / (self.prior_sigma**2) - 
            torch.log(weight_sigma**2) + torch.log(self.prior_sigma**2) - 1
        )
        
        # Bias KL divergence  
        bias_sigma = torch.log1p(torch.exp(self.bias_rho))
        bias_kl = 0.5 * torch.sum(
            (self.bias_mu**2 + bias_sigma**2) / (self.prior_sigma**2) -
            torch.log(bias_sigma**2) + torch.log(self.prior_sigma**2) - 1
        )
        
        return weight_kl + bias_kl


class UncertaintyAwareDistance(nn.Module):
    """
    Unified Uncertainty-Aware Distance Module.
    
    Supports multiple uncertainty estimation methods with configurable options.
    """
    
    def __init__(self, embedding_dim: int, config: UncertaintyConfig = None):
        super().__init__()
        self.embedding_dim = embedding_dim
        self.config = config or UncertaintyConfig()
        
        # Initialize uncertainty estimator based on configuration
        if self.config.method == "monte_carlo_dropout":
            self.uncertainty_estimator = MonteCarloDropoutUncertainty(
                embedding_dim, self.config.dropout_rate, self.config.n_samples
            )
        elif self.config.method == "deep_ensemble":
            self.uncertainty_estimator = DeepEnsembleUncertainty(
                embedding_dim, self.config.ensemble_size
            )
        elif self.config.method == "evidential":
            # Assume reasonable number of classes for evidential learning
            num_classes = getattr(self.config, 'num_classes', 10)
            self.uncertainty_estimator = EvidentialUncertaintyDistance(
                embedding_dim, num_classes, self.config.evidential_lambda
            )
        elif self.config.method == "bayesian":
            self.uncertainty_estimator = BayesianUncertaintyDistance(
                embedding_dim, self.config.bayesian_prior_sigma
            )
        else:
            raise ValueError(f"Unknown uncertainty method: {self.config.method}")
            
        # Temperature scaling for calibration
        self.temperature = nn.Parameter(torch.ones(1) * self.config.temperature)
        
    def forward(self, query_features: torch.Tensor, prototypes: torch.Tensor, 
                return_uncertainty: bool = True) -> Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        """
        Compute uncertainty-aware distances.
        
        Args:
            query_features: [n_query, embedding_dim]
            prototypes: [n_prototypes, embedding_dim]
            return_uncertainty: Whether to return uncertainty estimates
            
        Returns:
            distances: [n_query, n_prototypes]
            uncertainties: [n_query, n_prototypes] (if return_uncertainty=True)
        """
        # Get distances and uncertainties from chosen method
        distances, uncertainties = self.uncertainty_estimator(query_features, prototypes)
        
        # Apply temperature scaling
        distances = distances / self.temperature
        
        # Weight distances by uncertainty
        if self.config.uncertainty_weight != 1.0:
            distances = distances * (1 + self.config.uncertainty_weight * uncertainties)
            
        if return_uncertainty:
            return distances, uncertainties
        else:
            return distances
    
    def get_kl_divergence(self) -> torch.Tensor:
        """Get KL divergence for Bayesian methods."""
        if hasattr(self.uncertainty_estimator, 'kl_divergence'):
            return self.uncertainty_estimator.kl_divergence()
        else:
            return torch.tensor(0.0, device=next(self.parameters()).device)


# Factory functions for easy creation
def create_uncertainty_distance(method: str = "monte_carlo_dropout", 
                              embedding_dim: int = 512, 
                              **kwargs) -> UncertaintyAwareDistance:
    """Factory function to create uncertainty-aware distance modules."""
    config = UncertaintyConfig(method=method, **kwargs)
    return UncertaintyAwareDistance(embedding_dim, config)


def create_monte_carlo_uncertainty(embedding_dim: int, dropout_rate: float = 0.1, 
                                 n_samples: int = 10) -> UncertaintyAwareDistance:
    """Create Monte Carlo dropout uncertainty distance."""
    config = UncertaintyConfig(
        method="monte_carlo_dropout",
        dropout_rate=dropout_rate,
        n_samples=n_samples
    )
    return UncertaintyAwareDistance(embedding_dim, config)


def create_ensemble_uncertainty(embedding_dim: int, ensemble_size: int = 5) -> UncertaintyAwareDistance:
    """Create deep ensemble uncertainty distance."""
    config = UncertaintyConfig(
        method="deep_ensemble",
        ensemble_size=ensemble_size
    )
    return UncertaintyAwareDistance(embedding_dim, config)


def create_evidential_uncertainty(embedding_dim: int, num_classes: int = 10, 
                                lambda_reg: float = 1.0) -> UncertaintyAwareDistance:
    """Create evidential uncertainty distance.""" 
    config = UncertaintyConfig(
        method="evidential",
        evidential_lambda=lambda_reg,
        num_classes=num_classes
    )
    return UncertaintyAwareDistance(embedding_dim, config)


def create_bayesian_uncertainty(embedding_dim: int, prior_sigma: float = 1.0) -> UncertaintyAwareDistance:
    """Create Bayesian uncertainty distance."""
    config = UncertaintyConfig(
        method="bayesian",
        bayesian_prior_sigma=prior_sigma
    )
    return UncertaintyAwareDistance(embedding_dim, config)