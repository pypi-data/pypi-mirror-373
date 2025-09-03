"""
🎛️ Default Configurations for Holographic Memory
===============================================

This module provides default configuration objects and preset configurations
for common use cases of the holographic memory system.

Author: Benedict Chen (benedict@benedictchen.com)
"""

from typing import Dict, Any
from .config_classes import (
    HolographicConfig,
    VectorConfig,
    MemoryConfig,
    CleanupConfig,
    PerformanceConfig,
    ExperimentConfig
)
from .enums import (
    BindingMethod,
    CleanupStrategy,
    VectorDistribution,
    MemoryType,
    StorageFormat,
    CompositionMethod,
    SimilarityMetric,
    NoiseType,
    OptimizationMethod,
    VectorSpaceType,
    ArchitectureType
)


# Default Vector Configuration
DEFAULT_VECTOR_CONFIG = VectorConfig(
    vector_dim=512,
    complex_vectors=False,
    normalize=True,
    normalization_method="l2",
    distribution=VectorDistribution.GAUSSIAN,
    random_seed=None,
    noise_level=0.0,
    noise_type=NoiseType.GAUSSIAN,
    space_type=VectorSpaceType.REAL,
    sparsity_level=0.1,
    min_norm=1e-8,
    max_norm=100.0
)

# Default Memory Configuration
DEFAULT_MEMORY_CONFIG = MemoryConfig(
    capacity_threshold=1000,
    auto_cleanup=True,
    cleanup_threshold=0.8,
    memory_type=MemoryType.HOLOGRAPHIC,
    distributed_storage=True,
    access_decay=0.0,
    rehearsal_boost=1.1,
    storage_format=StorageFormat.NUMPY,
    compression_enabled=False,
    cleanup_strategy=CleanupStrategy.AUTO_ASSOCIATIVE,
    max_cleanup_iterations=10,
    convergence_threshold=1e-3
)

# Default Cleanup Configuration
DEFAULT_CLEANUP_CONFIG = CleanupConfig(
    strategy=CleanupStrategy.AUTO_ASSOCIATIVE,
    threshold=0.3,
    max_iterations=10,
    convergence_tolerance=1e-3,
    similarity_metric=SimilarityMetric.COSINE,
    candidate_limit=100,
    competition_strength=1.0,
    winner_threshold=0.5,
    early_stopping=True,
    adaptive_threshold=False,
    learning_rate=0.01
)

# Default Performance Configuration
DEFAULT_PERFORMANCE_CONFIG = PerformanceConfig(
    use_multiprocessing=False,
    num_workers=None,
    batch_size=32,
    memory_limit_mb=None,
    garbage_collect_frequency=1000,
    enable_caching=True,
    cache_size=1000,
    cache_timeout=3600.0,
    enable_profiling=False,
    profile_memory=False,
    profile_timing=False,
    optimization_method=OptimizationMethod.NONE,
    learning_rate=0.001,
    momentum=0.9
)

# Default Holographic Configuration
DEFAULT_HOLOGRAPHIC_CONFIG = HolographicConfig(
    binding_method=BindingMethod.CIRCULAR_CONVOLUTION,
    composition_method=CompositionMethod.SUPERPOSITION,
    architecture_type=ArchitectureType.STANDARD_HRR,
    vector_config=DEFAULT_VECTOR_CONFIG,
    memory_config=DEFAULT_MEMORY_CONFIG,
    cleanup_config=DEFAULT_CLEANUP_CONFIG,
    performance_config=DEFAULT_PERFORMANCE_CONFIG,
    debug_mode=False,
    verbose=False,
    log_level="INFO",
    experiment_name=None,
    experiment_id=None,
    metadata={}
)

# Preset Configurations for Different Use Cases

FAST_CONFIG = HolographicConfig(
    binding_method=BindingMethod.CIRCULAR_CONVOLUTION,
    composition_method=CompositionMethod.SUPERPOSITION,
    architecture_type=ArchitectureType.STANDARD_HRR,
    vector_config=VectorConfig(
        vector_dim=256,
        normalize=True,
        distribution=VectorDistribution.GAUSSIAN,
        noise_level=0.0
    ),
    memory_config=MemoryConfig(
        capacity_threshold=500,
        auto_cleanup=True,
        cleanup_strategy=CleanupStrategy.SIMILARITY_THRESHOLD,
        max_cleanup_iterations=5
    ),
    cleanup_config=CleanupConfig(
        strategy=CleanupStrategy.SIMILARITY_THRESHOLD,
        threshold=0.5,
        max_iterations=5,
        early_stopping=True
    ),
    performance_config=PerformanceConfig(
        use_multiprocessing=False,
        batch_size=16,
        enable_caching=True,
        cache_size=500
    )
)

HIGH_ACCURACY_CONFIG = HolographicConfig(
    binding_method=BindingMethod.CIRCULAR_CONVOLUTION,
    composition_method=CompositionMethod.SUPERPOSITION,
    architecture_type=ArchitectureType.COMPOSITIONAL,
    vector_config=VectorConfig(
        vector_dim=1024,
        normalize=True,
        distribution=VectorDistribution.GAUSSIAN,
        noise_level=0.0
    ),
    memory_config=MemoryConfig(
        capacity_threshold=5000,
        auto_cleanup=True,
        cleanup_strategy=CleanupStrategy.AUTO_ASSOCIATIVE,
        max_cleanup_iterations=20,
        convergence_threshold=1e-6
    ),
    cleanup_config=CleanupConfig(
        strategy=CleanupStrategy.AUTO_ASSOCIATIVE,
        threshold=0.1,
        max_iterations=20,
        convergence_tolerance=1e-6,
        adaptive_threshold=True
    ),
    performance_config=PerformanceConfig(
        use_multiprocessing=True,
        batch_size=64,
        enable_caching=True,
        cache_size=2000,
        enable_profiling=False
    )
)

ROBUST_CONFIG = HolographicConfig(
    binding_method=BindingMethod.CIRCULAR_CONVOLUTION,
    composition_method=CompositionMethod.WEIGHTED_SUM,
    architecture_type=ArchitectureType.HIERARCHICAL,
    vector_config=VectorConfig(
        vector_dim=512,
        normalize=True,
        distribution=VectorDistribution.GAUSSIAN,
        noise_level=0.1,
        noise_type=NoiseType.GAUSSIAN
    ),
    memory_config=MemoryConfig(
        capacity_threshold=2000,
        auto_cleanup=True,
        cleanup_strategy=CleanupStrategy.ITERATIVE_THRESHOLD,
        max_cleanup_iterations=15,
        access_decay=0.01,
        rehearsal_boost=1.2
    ),
    cleanup_config=CleanupConfig(
        strategy=CleanupStrategy.ITERATIVE_THRESHOLD,
        threshold=0.2,
        max_iterations=15,
        convergence_tolerance=1e-4,
        competition_strength=1.5,
        adaptive_threshold=True
    ),
    performance_config=PerformanceConfig(
        use_multiprocessing=True,
        batch_size=32,
        enable_caching=True,
        cache_size=1500,
        garbage_collect_frequency=500
    )
)

EXPERIMENTAL_CONFIG = HolographicConfig(
    binding_method=BindingMethod.TENSOR_PRODUCT,
    composition_method=CompositionMethod.MAX_POOLING,
    architecture_type=ArchitectureType.NEURAL_HYBRID,
    vector_config=VectorConfig(
        vector_dim=768,
        complex_vectors=True,
        normalize=True,
        distribution=VectorDistribution.COMPLEX_GAUSSIAN,
        space_type=VectorSpaceType.COMPLEX
    ),
    memory_config=MemoryConfig(
        capacity_threshold=3000,
        memory_type=MemoryType.HYBRID,
        distributed_storage=True,
        cleanup_strategy=CleanupStrategy.COMPETITIVE
    ),
    cleanup_config=CleanupConfig(
        strategy=CleanupStrategy.COMPETITIVE,
        threshold=0.4,
        max_iterations=12,
        similarity_metric=SimilarityMetric.CORRELATION,
        competition_strength=2.0
    ),
    performance_config=PerformanceConfig(
        use_multiprocessing=True,
        num_workers=4,
        batch_size=48,
        enable_caching=True,
        cache_size=1200,
        enable_profiling=True,
        profile_timing=True
    ),
    debug_mode=True,
    verbose=True
)

MINIMAL_CONFIG = HolographicConfig(
    binding_method=BindingMethod.XOR,
    composition_method=CompositionMethod.AVERAGE,
    architecture_type=ArchitectureType.STANDARD_HRR,
    vector_config=VectorConfig(
        vector_dim=128,
        normalize=False,
        distribution=VectorDistribution.BINARY,
        space_type=VectorSpaceType.BINARY
    ),
    memory_config=MemoryConfig(
        capacity_threshold=100,
        auto_cleanup=False,
        cleanup_strategy=CleanupStrategy.NONE,
        storage_format=StorageFormat.BINARY
    ),
    cleanup_config=CleanupConfig(
        strategy=CleanupStrategy.NONE,
        threshold=0.8,
        max_iterations=1
    ),
    performance_config=PerformanceConfig(
        use_multiprocessing=False,
        batch_size=8,
        enable_caching=False
    )
)

# Dictionary of all preset configurations
PRESET_CONFIGS: Dict[str, HolographicConfig] = {
    'default': DEFAULT_HOLOGRAPHIC_CONFIG,
    'fast': FAST_CONFIG,
    'high_accuracy': HIGH_ACCURACY_CONFIG,
    'robust': ROBUST_CONFIG,
    'experimental': EXPERIMENTAL_CONFIG,
    'minimal': MINIMAL_CONFIG
}

# Configuration for benchmark experiments
BENCHMARK_EXPERIMENT_CONFIG = ExperimentConfig(
    name="holographic_memory_benchmark",
    description="Comprehensive benchmark of holographic memory system",
    tags=["benchmark", "performance", "accuracy"],
    test_vector_dims=[128, 256, 512, 1024],
    test_noise_levels=[0.0, 0.05, 0.1, 0.2, 0.3],
    test_capacities=[100, 500, 1000, 2000, 5000],
    similarity_thresholds=[0.1, 0.2, 0.3, 0.5, 0.7, 0.9],
    performance_metrics=['accuracy', 'precision', 'recall', 'f1_score', 'retrieval_time'],
    save_results=True,
    results_directory="./benchmark_results",
    generate_plots=True,
    max_runtime_minutes=120
)


def get_config(preset_name: str = 'default') -> HolographicConfig:
    """
    Get a preset configuration by name.
    
    Parameters
    ----------
    preset_name : str
        Name of the preset configuration
        
    Returns
    -------
    HolographicConfig
        The requested configuration
        
    Raises
    ------
    ValueError
        If preset_name is not found
    """
    if preset_name not in PRESET_CONFIGS:
        available = list(PRESET_CONFIGS.keys())
        raise ValueError(f"Unknown preset '{preset_name}'. Available: {available}")
    
    return PRESET_CONFIGS[preset_name]


def list_presets() -> list[str]:
    """List available preset configuration names."""
    return list(PRESET_CONFIGS.keys())


def validate_config(config: HolographicConfig) -> bool:
    """
    Validate a holographic configuration.
    
    Parameters
    ----------
    config : HolographicConfig
        Configuration to validate
        
    Returns
    -------
    bool
        True if configuration is valid
        
    Raises
    ------
    ValueError
        If configuration is invalid
    """
    return config.validate()