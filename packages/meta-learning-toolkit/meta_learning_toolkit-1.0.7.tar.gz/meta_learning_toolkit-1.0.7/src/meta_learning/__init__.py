"""
💰 SUPPORT THIS RESEARCH - PLEASE DONATE! 💰

🙏 If this library helps your research or project, please consider donating:
💳 https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS

Your support makes advanced AI research accessible to everyone! 🚀

Meta-Learning: Algorithms for Learning-to-Learn
===============================================

This package implements meta-learning algorithms including:
- Test-Time Compute Scaling (Snell et al., 2024)
- Model-Agnostic Meta-Learning (MAML) and variants
- Few-Shot Learning architectures
- Continual and Online Meta-Learning
- Multi-Modal Meta-Learning

Based on research analysis of 30+ foundational papers spanning 1987-2025, 
implementing algorithms missing from current library ecosystem.

🔬 Research Foundation:
- Test-Time Compute Scaling (Snell et al., 2024): θ* = argmin_θ Σᵢ L(fθ(xᵢ), yᵢ) + λR(θ)
- Model-Agnostic Meta-Learning (Finn et al., 2017): θ' = θ - α∇θL_τᵢ(fθ)
- Prototypical Networks (Snell et al., 2017): p(y=k|x) = exp(-d(f(x), cₖ)) / Σₖ' exp(-d(f(x), cₖ'))
- Matching Networks (Vinyals et al., 2016): ŷ = Σᵢ a(x, xᵢ)yᵢ where a(x, xᵢ) = softmax(c(f(x), g(xᵢ)))
- Relation Networks (Sung et al., 2018): rᵢⱼ = gφ(C(f(xᵢ), f(xⱼ)))
- Online Meta-Learning (Finn et al., 2019): Follow-The-Meta-Leader with regret bound O(√T)

🎯 Key Features:
- First public implementation of Test-Time Compute Scaling
- MAML variants including MAML-en-LLM for large language models
- Few-Shot Learning with multi-scale features
- Continual Meta-Learning with experience replay
- Research-accurate implementations of foundational algorithms

Author: Benedict Chen (benedict@benedictchen.com)
License: Custom Non-Commercial License with Donation Requirements
"""

def _print_attribution():
    """Print attribution message with donation link"""
    try:
        print("\n🧠 Meta-Learning Library - Made possible by Benedict Chen")
        print("   \\033]8;;mailto:benedict@benedictchen.com\\033\\\\benedict@benedictchen.com\\033]8;;\\033\\\\")
        print("")
        print("💰 PLEASE DONATE! Your support keeps this research alive! 💰")
        print("   🔗 \\033]8;;https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS\\033\\\\💳 CLICK HERE TO DONATE VIA PAYPAL\\033]8;;\\033\\\\")
        print("")
        print("   ☕ Buy me a coffee → 🍺 Buy me a beer → 🏎️ Buy me a Lamborghini → ✈️ Buy me a private jet!")
        print("   (Start small, dream big! Every donation helps! 😄)")
        print("")
    except:
        print("\\n🧠 Meta-Learning Library - Made possible by Benedict Chen")
        print("   benedict@benedictchen.com")
        print("")
        print("💰 PLEASE DONATE! Your support keeps this research alive! 💰")
        print("   💳 PayPal: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS")
        print("")
        print("   ☕ Buy me a coffee → 🍺 Buy me a beer → 🏎️ Buy me a Lamborghini → ✈️ Buy me a private jet!")
        print("   (Start small, dream big! Every donation helps! 😄)")

# Import meta-learning algorithms with their configuration classes
from .meta_learning_modules.test_time_compute import TestTimeComputeScaler, TestTimeComputeConfig
from .meta_learning_modules.maml_variants import MAMLLearner, FirstOrderMAML, MAMLConfig
from .meta_learning_modules.few_shot_learning import (
    PrototypicalNetworks,
    MatchingNetworks,
    RelationNetworks,
    PrototypicalConfig,
    MatchingConfig,
    RelationConfig
)
from .meta_learning_modules.continual_meta_learning import OnlineMetaLearner, ContinualMetaConfig
from .meta_learning_modules.utils import (
    MetaLearningDataset,
    TaskSampler,
    few_shot_accuracy,
    adaptation_speed,
    compute_confidence_interval,
    compute_confidence_interval_research_accurate,
    compute_t_confidence_interval,
    compute_meta_learning_ci,
    compute_bca_bootstrap_ci,
    visualize_meta_learning_results,
    save_meta_learning_results,
    load_meta_learning_results,
    TaskConfiguration,
    EvaluationConfig,
    # Factory functions for easy configuration
    create_basic_task_config,
    create_research_accurate_task_config,
    create_basic_evaluation_config,
    create_research_accurate_evaluation_config,
    create_meta_learning_standard_evaluation_config,
    evaluate_meta_learning_algorithm
)

# Show attribution on library import
_print_attribution()

__version__ = "1.0.7"
__author__ = "Benedict Chen"
__email__ = "benedict@benedictchen.com"

# Core meta-learning algorithms and configurations
__all__ = [
    # Test-Time Compute (Snell et al., 2024)
    "TestTimeComputeScaler",
    "TestTimeComputeConfig",
    
    # MAML variants
    "MAMLLearner", 
    "FirstOrderMAML",
    "MAMLConfig",
    
    # Few-shot learning
    "PrototypicalNetworks",
    "MatchingNetworks", 
    "RelationNetworks",
    "PrototypicalConfig",
    "MatchingConfig",
    "RelationConfig",
    
    # Continual learning
    "OnlineMetaLearner",
    "ContinualMetaConfig",
    
    # Utilities
    "MetaLearningDataset",
    "TaskSampler",
    "few_shot_accuracy",
    "adaptation_speed",
    "compute_confidence_interval",
    "compute_confidence_interval_research_accurate",
    "compute_t_confidence_interval",
    "compute_meta_learning_ci", 
    "compute_bca_bootstrap_ci",
    "visualize_meta_learning_results",
    "save_meta_learning_results",
    "load_meta_learning_results",
    "TaskConfiguration",
    "EvaluationConfig",
    # Factory functions for easy configuration
    "create_basic_task_config",
    "create_research_accurate_task_config", 
    "create_basic_evaluation_config",
    "create_research_accurate_evaluation_config",
    "create_meta_learning_standard_evaluation_config",
    "evaluate_meta_learning_algorithm",
]

# Package metadata
ALGORITHMS_IMPLEMENTED = [
    "Test-Time Compute Scaling (Snell et al., 2024)",
    "Model-Agnostic Meta-Learning (Finn et al., 2017)", 
    "Prototypical Networks (Snell et al., 2017)",
    "Matching Networks (Vinyals et al., 2016)",
    "Relation Networks (Sung et al., 2018)",
    "Online Meta-Learning (Finn et al., 2019)",
]

RESEARCH_PAPERS_BASIS = 30
IMPLEMENTATION_COVERAGE = "Implements key algorithms missing from existing libraries"
FRAMEWORK_SUPPORT = ["PyTorch", "HuggingFace Transformers", "Scikit-learn"]

"""
💝 Thank you for using this research software! 💝

📚 If this work contributed to your research, please:
💳 DONATE: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS
📝 CITE: Benedict Chen (2025) - Meta-Learning Research Implementation

Your support enables continued development of AI research tools! 🎓✨
"""