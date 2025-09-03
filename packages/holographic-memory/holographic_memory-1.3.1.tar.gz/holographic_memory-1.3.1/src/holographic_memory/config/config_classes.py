"""
⚙️ Configuration Classes for Holographic Memory
==============================================

This module defines dataclass-based configuration objects for the
holographic memory system, providing structured parameter management.

Author: Benedict Chen (benedict@benedictchen.com)
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Tuple
import numpy as np

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


@dataclass
class VectorConfig:
    """Configuration for vector operations and properties."""
    
    # Vector dimensions
    vector_dim: int = 512
    complex_vectors: bool = False
    
    # Normalization
    normalize: bool = True
    normalization_method: str = "l2"
    
    # Random generation
    distribution: VectorDistribution = VectorDistribution.GAUSSIAN
    random_seed: Optional[int] = None
    
    # Noise parameters
    noise_level: float = 0.0
    noise_type: NoiseType = NoiseType.GAUSSIAN
    
    # Vector space properties
    space_type: VectorSpaceType = VectorSpaceType.REAL
    sparsity_level: float = 0.1  # For sparse vectors
    
    # Validation bounds
    min_norm: float = 1e-8
    max_norm: float = 100.0
    
    def validate(self) -> bool:
        """Validate configuration parameters."""
        if self.vector_dim <= 0:
            raise ValueError("Vector dimension must be positive")
        if not 0 <= self.noise_level <= 1:
            raise ValueError("Noise level must be between 0 and 1")
        if not 0 <= self.sparsity_level <= 1:
            raise ValueError("Sparsity level must be between 0 and 1")
        return True


@dataclass
class MemoryConfig:
    """Configuration for memory storage and retrieval."""
    
    # Capacity settings
    capacity_threshold: Optional[int] = None
    auto_cleanup: bool = True
    cleanup_threshold: float = 0.8
    
    # Memory type and structure
    memory_type: MemoryType = MemoryType.HOLOGRAPHIC
    distributed_storage: bool = True
    
    # Access patterns
    access_decay: float = 0.0  # Forgetting rate
    rehearsal_boost: float = 1.1  # Strength increase on access
    
    # Storage format
    storage_format: StorageFormat = StorageFormat.NUMPY
    compression_enabled: bool = False
    
    # Cleanup strategy
    cleanup_strategy: CleanupStrategy = CleanupStrategy.AUTO_ASSOCIATIVE
    max_cleanup_iterations: int = 10
    convergence_threshold: float = 1e-3
    
    def validate(self) -> bool:
        """Validate configuration parameters."""
        if self.capacity_threshold is not None and self.capacity_threshold <= 0:
            raise ValueError("Capacity threshold must be positive")
        if not 0 <= self.cleanup_threshold <= 1:
            raise ValueError("Cleanup threshold must be between 0 and 1")
        if self.access_decay < 0:
            raise ValueError("Access decay must be non-negative")
        return True


@dataclass
class CleanupConfig:
    """Configuration for associative cleanup operations."""
    
    # Cleanup parameters
    strategy: CleanupStrategy = CleanupStrategy.AUTO_ASSOCIATIVE
    threshold: float = 0.3
    max_iterations: int = 10
    convergence_tolerance: float = 1e-3
    
    # Similarity settings
    similarity_metric: SimilarityMetric = SimilarityMetric.COSINE
    candidate_limit: int = 100
    
    # Competition parameters
    competition_strength: float = 1.0
    winner_threshold: float = 0.5
    
    # Performance tuning
    early_stopping: bool = True
    adaptive_threshold: bool = False
    learning_rate: float = 0.01
    
    def validate(self) -> bool:
        """Validate configuration parameters."""
        if not 0 <= self.threshold <= 1:
            raise ValueError("Cleanup threshold must be between 0 and 1")
        if self.max_iterations <= 0:
            raise ValueError("Max iterations must be positive")
        if self.convergence_tolerance <= 0:
            raise ValueError("Convergence tolerance must be positive")
        return True


@dataclass
class PerformanceConfig:
    """Configuration for performance optimization."""
    
    # Parallel processing
    use_multiprocessing: bool = False
    num_workers: Optional[int] = None
    batch_size: int = 32
    
    # Memory management
    memory_limit_mb: Optional[int] = None
    garbage_collect_frequency: int = 1000
    
    # Caching
    enable_caching: bool = True
    cache_size: int = 1000
    cache_timeout: float = 3600.0  # seconds
    
    # Profiling
    enable_profiling: bool = False
    profile_memory: bool = False
    profile_timing: bool = False
    
    # Optimization
    optimization_method: OptimizationMethod = OptimizationMethod.NONE
    learning_rate: float = 0.001
    momentum: float = 0.9
    
    def validate(self) -> bool:
        """Validate configuration parameters."""
        if self.batch_size <= 0:
            raise ValueError("Batch size must be positive")
        if self.cache_size < 0:
            raise ValueError("Cache size must be non-negative")
        if self.learning_rate <= 0:
            raise ValueError("Learning rate must be positive")
        return True


@dataclass
class HolographicConfig:
    """Main configuration class combining all subsystem configurations."""
    
    # Core binding settings
    binding_method: BindingMethod = BindingMethod.CIRCULAR_CONVOLUTION
    composition_method: CompositionMethod = CompositionMethod.SUPERPOSITION
    
    # Architecture
    architecture_type: ArchitectureType = ArchitectureType.STANDARD_HRR
    
    # Component configurations
    vector_config: VectorConfig = field(default_factory=VectorConfig)
    memory_config: MemoryConfig = field(default_factory=MemoryConfig)
    cleanup_config: CleanupConfig = field(default_factory=CleanupConfig)
    performance_config: PerformanceConfig = field(default_factory=PerformanceConfig)
    
    # Global settings
    debug_mode: bool = False
    verbose: bool = False
    log_level: str = "INFO"
    
    # Experiment tracking
    experiment_name: Optional[str] = None
    experiment_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> bool:
        """Validate all configuration components."""
        self.vector_config.validate()
        self.memory_config.validate()
        self.cleanup_config.validate()
        self.performance_config.validate()
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'binding_method': self.binding_method.value,
            'composition_method': self.composition_method.value,
            'architecture_type': self.architecture_type.value,
            'vector_config': self.vector_config.__dict__,
            'memory_config': self.memory_config.__dict__,
            'cleanup_config': self.cleanup_config.__dict__,
            'performance_config': self.performance_config.__dict__,
            'debug_mode': self.debug_mode,
            'verbose': self.verbose,
            'log_level': self.log_level,
            'experiment_name': self.experiment_name,
            'experiment_id': self.experiment_id,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'HolographicConfig':
        """Create configuration from dictionary."""
        # Create component configs
        vector_config = VectorConfig(**config_dict.get('vector_config', {}))
        memory_config = MemoryConfig(**config_dict.get('memory_config', {}))
        cleanup_config = CleanupConfig(**config_dict.get('cleanup_config', {}))
        performance_config = PerformanceConfig(**config_dict.get('performance_config', {}))
        
        # Create main config
        return cls(
            binding_method=BindingMethod(config_dict.get('binding_method', 'circular_convolution')),
            composition_method=CompositionMethod(config_dict.get('composition_method', 'superposition')),
            architecture_type=ArchitectureType(config_dict.get('architecture_type', 'standard_hrr')),
            vector_config=vector_config,
            memory_config=memory_config,
            cleanup_config=cleanup_config,
            performance_config=performance_config,
            debug_mode=config_dict.get('debug_mode', False),
            verbose=config_dict.get('verbose', False),
            log_level=config_dict.get('log_level', 'INFO'),
            experiment_name=config_dict.get('experiment_name'),
            experiment_id=config_dict.get('experiment_id'),
            metadata=config_dict.get('metadata', {})
        )


@dataclass
class ExperimentConfig:
    """Configuration for experimental runs and comparisons."""
    
    # Experiment identification
    name: str = "holographic_memory_experiment"
    description: str = ""
    tags: List[str] = field(default_factory=list)
    
    # Test parameters
    test_vector_dims: List[int] = field(default_factory=lambda: [128, 256, 512])
    test_noise_levels: List[float] = field(default_factory=lambda: [0.0, 0.1, 0.2])
    test_capacities: List[int] = field(default_factory=lambda: [100, 1000, 10000])
    
    # Evaluation metrics
    similarity_thresholds: List[float] = field(default_factory=lambda: [0.1, 0.3, 0.5, 0.7, 0.9])
    performance_metrics: List[str] = field(default_factory=lambda: ['accuracy', 'precision', 'recall'])
    
    # Output settings
    save_results: bool = True
    results_directory: str = "./experiment_results"
    generate_plots: bool = True
    
    # Resource limits
    max_runtime_minutes: Optional[int] = None
    memory_limit_gb: Optional[float] = None
    
    def validate(self) -> bool:
        """Validate experiment configuration."""
        if not self.name:
            raise ValueError("Experiment name cannot be empty")
        if not self.test_vector_dims:
            raise ValueError("Must specify at least one test vector dimension")
        return True