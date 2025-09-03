#!/usr/bin/env python3
"""
Comprehensive Configuration Factory for ALL FIXME Solutions
=========================================================

This module provides factory functions to create configurations for ALL
implemented FIXME solutions across all modules in the meta-learning package.

Users can pick and choose which solutions to enable with overlapping
configurations handled intelligently.

All configurations are research-accurate and production-ready.
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

# Import all configuration classes
from .test_time_compute import TestTimeComputeConfig
from .few_shot_learning import PrototypicalConfig, MatchingConfig, RelationConfig
from .continual_meta_learning import ContinualMetaConfig, OnlineMetaConfig
from .maml_variants import MAMLConfig
from .utils import TaskConfiguration, EvaluationConfig


@dataclass
class ComprehensiveMetaLearningConfig:
    """
    Master configuration class that encompasses ALL FIXME solutions.
    
    Users can configure every aspect of the meta-learning pipeline from
    a single unified configuration object.
    """
    # Test-Time Compute Configuration
    test_time_compute: Optional[TestTimeComputeConfig] = None
    
    # Few-Shot Learning Configurations
    prototypical: Optional[PrototypicalConfig] = None
    matching: Optional[MatchingConfig] = None
    relation: Optional[RelationConfig] = None
    
    # Continual Learning Configurations  
    continual_meta: Optional[ContinualMetaConfig] = None
    online_meta: Optional[OnlineMetaConfig] = None
    
    # MAML Configuration
    maml: Optional[MAMLConfig] = None
    
    # Utility Configurations
    task: Optional[TaskConfiguration] = None
    evaluation: Optional[EvaluationConfig] = None
    
    # Global settings that affect multiple modules
    global_seed: int = 42
    device: str = "auto"  # "auto", "cpu", "cuda"
    verbose: bool = True


# =============================================================================
# COMPREHENSIVE FACTORY FUNCTIONS FOR ALL FIXME SOLUTIONS
# =============================================================================

def create_all_fixme_solutions_config() -> ComprehensiveMetaLearningConfig:
    """
    Create configuration that enables ALL implemented FIXME solutions.
    
    COMPREHENSIVE: Every single FIXME solution across all modules enabled
    with balanced settings for research accuracy and performance.
    """
    config = ComprehensiveMetaLearningConfig()
    
    # Test-Time Compute: All solutions enabled
    config.test_time_compute = TestTimeComputeConfig()
    config.test_time_compute.compute_strategy = "hybrid"
    config.test_time_compute.use_process_reward = True
    config.test_time_compute.use_test_time_training = True
    config.test_time_compute.use_gradient_verification = True
    config.test_time_compute.use_chain_of_thought = True
    config.test_time_compute.cot_method = "attention_based"
    config.test_time_compute.use_optimal_allocation = True
    config.test_time_compute.use_adaptive_distribution = True
    
    # Prototypical Networks: All FIXME solutions enabled
    config.prototypical = PrototypicalConfig()
    config.prototypical.use_uncertainty_aware_distances = True
    config.prototypical.use_hierarchical_prototypes = True
    config.prototypical.use_task_adaptive_prototypes = True
    config.prototypical.protonet_variant = "research_accurate"
    config.prototypical.multi_scale_features = True
    config.prototypical.adaptive_prototypes = True
    config.prototypical.uncertainty_estimation = True
    
    # Matching Networks: Advanced attention mechanisms
    config.matching = MatchingConfig()
    config.matching.attention_mechanism = "scaled_dot_product"
    config.matching.context_encoding = True
    config.matching.support_set_encoding = "transformer"
    config.matching.bidirectional_lstm = True
    
    # Relation Networks: Graph neural networks enabled
    config.relation = RelationConfig()
    config.relation.use_graph_neural_network = True
    config.relation.edge_features = True
    config.relation.self_attention = True
    
    # Continual Learning: All EWC and Fisher solutions
    config.continual_meta = ContinualMetaConfig()
    config.continual_meta.ewc_method = "full"  # Use full Fisher matrix
    config.continual_meta.fisher_estimation_method = "exact"
    config.continual_meta.fisher_accumulation_method = "ema"
    config.continual_meta.memory_consolidation_method = "ewc"
    config.continual_meta.use_task_specific_importance = True
    config.continual_meta.use_gradient_importance = True
    
    # Online Meta-Learning: Advanced replay and adaptation
    config.online_meta = OnlineMetaConfig()
    config.online_meta.experience_replay = True
    config.online_meta.prioritized_replay = True
    config.online_meta.importance_sampling = True
    config.online_meta.adaptive_lr = True
    
    # MAML: All functional forward solutions
    config.maml = MAMLConfig()
    config.maml.functional_forward_method = "higher_style"
    config.maml.maml_variant = "maml"
    config.maml.inner_lr = 0.01
    config.maml.inner_steps = 5
    config.maml.first_order = False
    
    # Task Configuration: All difficulty estimation methods
    config.task = TaskConfiguration()
    config.task.difficulty_estimation_method = "entropy"  # Can switch between methods
    
    # Evaluation: All confidence interval methods
    config.evaluation = EvaluationConfig()
    config.evaluation.confidence_interval_method = "bca_bootstrap"
    config.evaluation.num_episodes = 600
    
    return config


def create_research_accurate_config() -> ComprehensiveMetaLearningConfig:
    """
    Create configuration focused on research accuracy over performance.
    
    RESEARCH-FIRST: Prioritizes exact implementations from papers over speed.
    """
    config = ComprehensiveMetaLearningConfig()
    
    # Test-Time Compute: Research-accurate methods
    config.test_time_compute = TestTimeComputeConfig()
    config.test_time_compute.compute_strategy = "snell2024"
    config.test_time_compute.use_process_reward = True
    config.test_time_compute.prm_scoring_method = "weighted"
    
    # Prototypical Networks: Pure original implementation
    config.prototypical = PrototypicalConfig()
    config.prototypical.use_original_implementation = True
    config.prototypical.use_squared_euclidean = True
    config.prototypical.prototype_method = "mean"
    
    # Continual Learning: Kirkpatrick et al. 2017 exact
    config.continual_meta = ContinualMetaConfig()
    config.continual_meta.ewc_method = "diagonal"
    config.continual_meta.fisher_estimation_method = "empirical"
    config.continual_meta.fisher_sampling_method = "true_posterior"
    
    # MAML: Original Finn et al. 2017 implementation
    config.maml = MAMLConfig()
    config.maml.maml_variant = "maml"
    config.maml.functional_forward_method = "basic"
    config.maml.first_order = False
    
    # Evaluation: Standard meta-learning protocols
    config.evaluation = EvaluationConfig()
    config.evaluation.confidence_interval_method = "t_distribution"
    config.evaluation.num_episodes = 600
    
    return config


def create_performance_optimized_config() -> ComprehensiveMetaLearningConfig:
    """
    Create configuration optimized for performance and speed.
    
    PERFORMANCE-FIRST: Balanced accuracy with computational efficiency.
    """
    config = ComprehensiveMetaLearningConfig()
    
    # Test-Time Compute: Fast configuration
    config.test_time_compute = TestTimeComputeConfig()
    config.test_time_compute.compute_strategy = "basic"
    config.test_time_compute.max_compute_budget = 100
    config.test_time_compute.min_compute_steps = 3
    config.test_time_compute.use_chain_of_thought = True
    config.test_time_compute.cot_method = "prototype_based"  # Fastest method
    
    # Prototypical Networks: Simple but effective
    config.prototypical = PrototypicalConfig()
    config.prototypical.protonet_variant = "simple"
    config.prototypical.multi_scale_features = False
    config.prototypical.adaptive_prototypes = False
    
    # Continual Learning: Diagonal EWC for speed
    config.continual_meta = ContinualMetaConfig()
    config.continual_meta.ewc_method = "diagonal"
    config.continual_meta.fisher_estimation_method = "empirical"
    config.continual_meta.fisher_accumulation_method = "sum"
    
    # MAML: First-order for speed
    config.maml = MAMLConfig()
    config.maml.maml_variant = "fomaml"  # First-order MAML
    config.maml.functional_forward_method = "compiled"  # PyTorch 2.0 optimization
    config.maml.inner_steps = 3
    
    # Evaluation: Fast CI computation
    config.evaluation = EvaluationConfig()
    config.evaluation.confidence_interval_method = "bootstrap"
    config.evaluation.num_episodes = 300  # Reduced for speed
    
    return config


def create_specific_solution_config(
    solutions: List[str]
) -> ComprehensiveMetaLearningConfig:
    """
    Create configuration for specific FIXME solutions only.
    
    Args:
        solutions: List of solution identifiers to enable
        
    Available solutions:
    - "process_reward_model": Test-time compute process reward verification
    - "consistency_verification": Test-time training consistency checks
    - "gradient_verification": Gradient-based step verification
    - "attention_reasoning": Attention-based reasoning paths
    - "feature_reasoning": Feature-based reasoning decomposition
    - "prototype_reasoning": Prototype-distance reasoning steps
    - "uncertainty_distances": Uncertainty-aware distance metrics
    - "hierarchical_prototypes": Multi-level prototype structures
    - "task_adaptive_prototypes": Task-specific prototype initialization
    - "full_fisher": Full Fisher Information Matrix computation
    - "evcl": Elastic Variational Continual Learning
    - "kfac_fisher": Kronecker-factored Fisher approximation
    - "functional_forward": Advanced functional forward methods
    - "difficulty_estimation": Advanced difficulty estimation methods
    - "bootstrap_ci": Advanced confidence interval methods
    """
    config = ComprehensiveMetaLearningConfig()
    
    # Initialize basic configurations
    config.test_time_compute = TestTimeComputeConfig()
    config.prototypical = PrototypicalConfig()
    config.continual_meta = ContinualMetaConfig()
    config.maml = MAMLConfig()
    config.evaluation = EvaluationConfig()
    
    # Enable specific solutions based on user selection
    for solution in solutions:
        if solution == "process_reward_model":
            config.test_time_compute.use_process_reward = True
            config.test_time_compute.use_process_reward_model = True
            
        elif solution == "consistency_verification":
            config.test_time_compute.use_test_time_training = True
            config.test_time_compute.adaptation_weight = 0.6
            
        elif solution == "gradient_verification":
            config.test_time_compute.use_gradient_verification = True
            
        elif solution == "attention_reasoning":
            config.test_time_compute.use_chain_of_thought = True
            config.test_time_compute.cot_method = "attention_based"
            
        elif solution == "feature_reasoning":
            config.test_time_compute.use_chain_of_thought = True
            config.test_time_compute.cot_method = "feature_based"
            
        elif solution == "prototype_reasoning":
            config.test_time_compute.use_chain_of_thought = True
            config.test_time_compute.cot_method = "prototype_based"
            
        elif solution == "uncertainty_distances":
            config.prototypical.use_uncertainty_aware_distances = True
            
        elif solution == "hierarchical_prototypes":
            config.prototypical.use_hierarchical_prototypes = True
            
        elif solution == "task_adaptive_prototypes":
            config.prototypical.use_task_adaptive_prototypes = True
            
        elif solution == "full_fisher":
            config.continual_meta.ewc_method = "full"
            config.continual_meta.fisher_estimation_method = "exact"
            
        elif solution == "evcl":
            config.continual_meta.ewc_method = "evcl"
            
        elif solution == "kfac_fisher":
            config.continual_meta.fisher_estimation_method = "kfac"
            
        elif solution == "functional_forward":
            config.maml.functional_forward_method = "higher_style"
            
        elif solution == "difficulty_estimation":
            config.task = TaskConfiguration(difficulty_estimation_method="entropy")
            
        elif solution == "bootstrap_ci":
            config.evaluation.confidence_interval_method = "bca_bootstrap"
            
        else:
            print(f"Warning: Unknown solution '{solution}'. Ignoring.")
    
    return config


def create_modular_config(
    test_time_compute: Optional[str] = None,
    few_shot_method: Optional[str] = None,
    continual_method: Optional[str] = None,
    maml_variant: Optional[str] = None,
    evaluation_method: Optional[str] = None
) -> ComprehensiveMetaLearningConfig:
    """
    Create modular configuration by choosing specific methods for each component.
    
    Args:
        test_time_compute: "basic", "snell2024", "akyurek2024", "openai_o1", "hybrid"
        few_shot_method: "prototypical", "matching", "relation"
        continual_method: "ewc", "mas", "packnet", "hat"
        maml_variant: "maml", "fomaml", "reptile", "anil", "boil"
        evaluation_method: "bootstrap", "t_distribution", "bca_bootstrap"
    """
    config = ComprehensiveMetaLearningConfig()
    
    # Configure test-time compute
    if test_time_compute:
        config.test_time_compute = TestTimeComputeConfig()
        config.test_time_compute.compute_strategy = test_time_compute
        
        if test_time_compute in ["snell2024", "hybrid"]:
            config.test_time_compute.use_process_reward = True
        if test_time_compute in ["akyurek2024", "hybrid"]:
            config.test_time_compute.use_test_time_training = True
        if test_time_compute in ["openai_o1", "hybrid"]:
            config.test_time_compute.use_chain_of_thought = True
    
    # Configure few-shot method
    if few_shot_method == "prototypical":
        config.prototypical = PrototypicalConfig()
        config.prototypical.protonet_variant = "research_accurate"
    elif few_shot_method == "matching":
        config.matching = MatchingConfig()
        config.matching.attention_mechanism = "scaled_dot_product"
    elif few_shot_method == "relation":
        config.relation = RelationConfig()
        config.relation.use_graph_neural_network = True
    
    # Configure continual learning
    if continual_method:
        config.continual_meta = ContinualMetaConfig()
        config.continual_meta.memory_consolidation_method = continual_method
        
        if continual_method == "ewc":
            config.continual_meta.ewc_method = "diagonal"
        elif continual_method == "mas":
            config.continual_meta.use_gradient_importance = True
    
    # Configure MAML variant
    if maml_variant:
        config.maml = MAMLConfig()
        config.maml.maml_variant = maml_variant
        
        if maml_variant == "fomaml":
            config.maml.first_order = True
        elif maml_variant in ["anil", "boil"]:
            config.maml.functional_forward_method = "l2l_style"
    
    # Configure evaluation
    if evaluation_method:
        config.evaluation = EvaluationConfig()
        config.evaluation.confidence_interval_method = evaluation_method
    
    return config


def create_educational_config() -> ComprehensiveMetaLearningConfig:
    """
    Create configuration optimized for educational use and understanding.
    
    EDUCATIONAL: Simplified but still research-accurate implementations.
    """
    config = ComprehensiveMetaLearningConfig()
    
    # Simple but working implementations
    config.test_time_compute = TestTimeComputeConfig()
    config.test_time_compute.compute_strategy = "basic"
    config.test_time_compute.max_compute_budget = 50
    
    config.prototypical = PrototypicalConfig()
    config.prototypical.protonet_variant = "simple"
    
    config.maml = MAMLConfig()
    config.maml.maml_variant = "maml"
    config.maml.inner_steps = 3
    
    config.evaluation = EvaluationConfig()
    config.evaluation.confidence_interval_method = "t_distribution"
    config.evaluation.num_episodes = 100
    
    return config


def get_available_solutions() -> Dict[str, List[str]]:
    """
    Get a dictionary of all available FIXME solutions organized by module.
    
    Returns:
        Dictionary mapping module names to lists of available solutions
    """
    return {
        "test_time_compute": [
            "process_reward_model",
            "consistency_verification", 
            "gradient_verification",
            "attention_reasoning",
            "feature_reasoning",
            "prototype_reasoning"
        ],
        "few_shot_learning": [
            "uncertainty_distances",
            "hierarchical_prototypes", 
            "task_adaptive_prototypes",
            "research_accurate_original"
        ],
        "continual_meta_learning": [
            "diagonal_fisher",
            "full_fisher",
            "kfac_fisher",
            "evcl",
            "gradient_importance"
        ],
        "maml_variants": [
            "l2l_functional_forward",
            "higher_functional_forward",
            "manual_functional_forward",
            "compiled_functional_forward"
        ],
        "utils": [
            "silhouette_difficulty",
            "entropy_difficulty",
            "knn_difficulty",
            "t_distribution_ci",
            "meta_learning_ci",
            "bca_bootstrap_ci"
        ]
    }


def print_solution_summary():
    """Print a comprehensive summary of all available FIXME solutions."""
    solutions = get_available_solutions()
    
    print("🔧 Meta-Learning Package - All Available FIXME Solutions")
    print("=" * 70)
    print(f"Total: {sum(len(module_solutions) for module_solutions in solutions.values())} solutions across {len(solutions)} modules")
    
    for module, module_solutions in solutions.items():
        print(f"\n📦 {module.replace('_', ' ').title()}:")
        for i, solution in enumerate(module_solutions, 1):
            print(f"  {i}. ✅ {solution.replace('_', ' ').title()}")
    
    print(f"\n🏭 Factory Functions Available:")
    print("  • create_all_fixme_solutions_config() - Enable ALL solutions")
    print("  • create_research_accurate_config() - Research-first approach")
    print("  • create_performance_optimized_config() - Performance-first approach")
    print("  • create_specific_solution_config([solutions]) - Pick specific solutions")
    print("  • create_modular_config(...) - Mix and match by module")
    print("  • create_educational_config() - Simplified for learning")


# Configuration validation
def validate_config(config: ComprehensiveMetaLearningConfig) -> Dict[str, List[str]]:
    """
    Validate configuration for potential conflicts or issues.
    
    Returns:
        Dictionary with 'warnings' and 'errors' lists
    """
    issues = {"warnings": [], "errors": []}
    
    # Check for conflicting settings
    if config.test_time_compute and config.maml:
        if (config.test_time_compute.use_test_time_training and 
            config.maml.maml_variant in ["anil", "boil"]):
            issues["warnings"].append(
                "Test-time training with ANIL/BOIL may have conflicting adaptation strategies"
            )
    
    # Check for performance implications
    if config.continual_meta and config.continual_meta.fisher_estimation_method == "exact":
        issues["warnings"].append(
            "Exact Fisher Information computation is very expensive - consider 'empirical' for large models"
        )
    
    # Check for research accuracy
    if (config.prototypical and 
        config.prototypical.use_uncertainty_aware_distances and
        not config.prototypical.uncertainty_estimation):
        issues["warnings"].append(
            "Uncertainty-aware distances require uncertainty_estimation=True for best results"
        )
    
    return issues