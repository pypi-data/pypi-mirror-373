"""
Meta-Learning Modules

This package contains cutting-edge meta-learning algorithms that address
critical gaps in existing libraries. All implementations focus on algorithms
with no existing public implementations or significant improvements over
basic versions.

Modules:
- test_time_compute: Test-Time Compute Scaling (2024 breakthrough)
- maml_variants: Advanced MAML variants including MAML-en-LLM
- few_shot_learning: Enhanced few-shot algorithms with 2024 improvements  
- continual_meta_learning: Online meta-learning with memory banks
- utils: Advanced utilities and evaluation tools

All algorithms are research-accurate implementations based on recent papers
and fill identified gaps in the meta-learning library ecosystem.
"""

from .test_time_compute import TestTimeComputeScaler, TestTimeComputeConfig
from .maml_variants import (
    MAMLLearner,
    FirstOrderMAML,
    MAMLenLLM,
    MAMLConfig,
    MAMLenLLMConfig,
    LoRALayer
)
from .few_shot_learning import (
    PrototypicalNetworks,
    MatchingNetworks,
    RelationNetworks,
    PrototypicalConfig,
    MatchingConfig,
    RelationConfig
)
from .continual_meta_learning import (
    OnlineMetaLearner,
    OnlineMetaConfig,
    ContinualMetaConfig,
    EpisodicMemoryConfig
)
from .utils import (
    MetaLearningDataset,
    TaskSampler,
    few_shot_accuracy,
    adaptation_speed,
    compute_confidence_interval,
    visualize_meta_learning_results,
    save_meta_learning_results,
    load_meta_learning_results,
    TaskConfiguration,
    EvaluationConfig
)

__all__ = [
    # Test-Time Compute Scaling
    "TestTimeComputeScaler",
    "TestTimeComputeConfig",
    
    # MAML Variants
    "MAMLLearner",
    "FirstOrderMAML", 
    "MAMLenLLM",
    "MAMLConfig",
    "MAMLenLLMConfig",
    "LoRALayer",
    
    # Few-Shot Learning
    "PrototypicalNetworks",
    "MatchingNetworks",
    "RelationNetworks",
    "PrototypicalConfig",
    "MatchingConfig",
    "RelationConfig",
    
    # Continual Meta-Learning
    "OnlineMetaLearner",
    "OnlineMetaConfig",
    "ContinualMetaConfig", 
    "EpisodicMemoryConfig",
    
    # Utilities
    "MetaLearningDataset",
    "TaskSampler",
    "few_shot_accuracy",
    "adaptation_speed",
    "compute_confidence_interval",
    "visualize_meta_learning_results",
    "save_meta_learning_results",
    "load_meta_learning_results",
    "TaskConfiguration",
    "EvaluationConfig",
]