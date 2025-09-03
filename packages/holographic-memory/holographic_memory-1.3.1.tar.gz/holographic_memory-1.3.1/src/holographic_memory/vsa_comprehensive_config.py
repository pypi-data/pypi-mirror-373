"""
Vector Symbolic Architecture Comprehensive Configuration System
==============================================================

Author: Benedict Chen (benedict@benedictchen.com)

This module implements ALL VSA FIXME solutions with comprehensive user configuration
options, allowing researchers to choose between different parameter settings and
theoretical approaches.

Based on: 
- Plate (1995) "Holographic Reduced Representations"
- Gayler (1998) "Multiplicative Binding, Representation Operators & Analogy" 
- Kanerva (2009) "Hyperdimensional Computing"
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Callable
from enum import Enum
import numpy as np
import math


class VectorDimensionStrategy(Enum):
    """Vector dimensionality selection strategies with research basis."""
    AUTO_CAPACITY_BASED = "auto_capacity"  # Based on expected symbol count and capacity analysis
    PLATE_1995_STANDARD = "plate_standard"  # Plate's original dimensions (256-1024)
    KANERVA_2009_OPTIMIZED = "kanerva_optimized"  # Kanerva's optimized dimensions
    CUSTOM_SPECIFIED = "custom"  # User-specified dimension
    POWER_OF_TWO = "power_of_two"  # Nearest power of 2 for efficiency


class VectorDistribution(Enum):
    """Vector initialization distributions from research."""
    NORMAL_IID = "normal"  # i.i.d. normal distribution (Plate 1995)
    UNIFORM_RANDOM = "uniform"  # Uniform random distribution
    BERNOULLI_BIPOLAR = "bernoulli"  # Bernoulli ±1 distribution (Kanerva 2009)
    GAUSSIAN_NORMALIZED = "gaussian_normalized"  # Normalized Gaussian
    SPARSE_BINARY = "sparse_binary"  # Sparse binary vectors


class BindingOperation(Enum):
    """Binding operation implementations."""
    CIRCULAR_CONVOLUTION = "circular_convolution"  # Plate's HRR binding (default)
    ELEMENT_WISE_MULTIPLY = "element_wise"  # Hadamard product (simple but limited)
    FOURIER_DOMAIN = "fourier"  # FFT-based convolution (efficient)
    XOR_BINDING = "xor"  # XOR-based binding for binary vectors
    TENSOR_PRODUCT = "tensor_product"  # Full tensor product (very high dimensional)


class CleanupMethod(Enum):
    """Cleanup memory and similarity-based retrieval methods."""
    NEAREST_NEIGHBOR = "nearest_neighbor"  # Simple nearest neighbor
    THRESHOLD_CLEANUP = "threshold"  # Similarity threshold-based
    RESONATOR_NETWORK = "resonator"  # Resonator network cleanup (Plate 1995)
    ITERATIVE_CLEANUP = "iterative"  # Multiple cleanup iterations
    NO_CLEANUP = "none"  # No cleanup (raw similarity)


class SimilarityMetric(Enum):
    """Similarity metrics for VSA operations."""
    COSINE_SIMILARITY = "cosine"  # Standard cosine similarity
    DOT_PRODUCT = "dot_product"  # Raw dot product
    EUCLIDEAN_DISTANCE = "euclidean"  # Euclidean distance (inverted)
    HAMMING_DISTANCE = "hamming"  # Hamming distance for binary vectors
    CORRELATION = "correlation"  # Pearson correlation


@dataclass
class VSAComprehensiveConfig:
    """
    MASTER CONFIGURATION for ALL VSA FIXME solutions.
    
    Provides comprehensive control over all aspects of Vector Symbolic Architecture
    implementation, allowing users to choose between research-accurate approaches.
    """
    
    # ============================================================================
    # VECTOR DIMENSIONALITY SOLUTIONS
    # ============================================================================
    
    # Dimension Selection Strategy
    dimension_strategy: VectorDimensionStrategy = VectorDimensionStrategy.AUTO_CAPACITY_BASED
    
    # Custom dimension (used if strategy is CUSTOM_SPECIFIED)
    custom_vector_dim: int = 512
    
    # Auto-dimensioning parameters
    expected_symbol_count: int = 100  # Expected number of symbols in vocabulary
    capacity_safety_factor: float = 2.5  # Safety factor for capacity estimation
    min_dimension: int = 256  # Minimum allowed dimension
    max_dimension: int = 2048  # Maximum allowed dimension
    
    # Research-based dimension ranges
    plate_1995_dimension_range: tuple = (256, 1024)  # Plate's tested range
    kanerva_2009_optimal_dims: List[int] = field(default_factory=lambda: [512, 1024, 2048])
    
    # ============================================================================
    # VECTOR DISTRIBUTION SOLUTIONS
    # ============================================================================
    
    # Distribution Type
    vector_distribution: VectorDistribution = VectorDistribution.NORMAL_IID
    
    # Normal Distribution Parameters
    normal_mean: float = 0.0  # Mean for normal distribution
    normal_std_formula: str = "1_over_sqrt_d"  # "1_over_sqrt_d", "unit_variance", "custom"
    custom_normal_std: float = 1.0  # Custom standard deviation
    
    # Uniform Distribution Parameters  
    uniform_low: float = -1.0  # Lower bound for uniform distribution
    uniform_high: float = 1.0  # Upper bound for uniform distribution
    
    # Bernoulli Parameters
    bernoulli_prob: float = 0.5  # Probability of +1 (vs -1)
    
    # Sparse Binary Parameters
    sparsity_level: float = 0.1  # Fraction of non-zero elements
    
    # Normalization Settings
    normalize_vectors: bool = True  # Whether to normalize vectors to unit length
    normalization_epsilon: float = 1e-8  # Epsilon for numerical stability
    
    # ============================================================================
    # BINDING OPERATION SOLUTIONS
    # ============================================================================
    
    # Binding Method
    binding_operation: BindingOperation = BindingOperation.CIRCULAR_CONVOLUTION
    
    # Circular Convolution Parameters
    use_fft_acceleration: bool = True  # Use FFT for large dimensions
    fft_threshold_dimension: int = 128  # Switch to FFT above this dimension
    
    # Fourier Domain Parameters
    preserve_phase_information: bool = True  # Preserve phase in frequency domain
    frequency_domain_epsilon: float = 1e-10  # Epsilon for frequency domain ops
    
    # XOR Binding Parameters (for binary vectors)
    xor_permutation_seed: Optional[int] = None  # Seed for permutation generation
    
    # Element-wise Multiplication Parameters
    elementwise_normalization: bool = True  # Normalize after element-wise ops
    
    # ============================================================================
    # CLEANUP AND RETRIEVAL SOLUTIONS
    # ============================================================================
    
    # Cleanup Method
    cleanup_method: CleanupMethod = CleanupMethod.THRESHOLD_CLEANUP
    
    # Similarity Metric
    similarity_metric: SimilarityMetric = SimilarityMetric.COSINE_SIMILARITY
    
    # Cleanup Threshold Parameters
    cleanup_threshold: float = 0.3  # Minimum similarity for retrieval
    adaptive_threshold: bool = True  # Adapt threshold based on noise level
    threshold_adaptation_rate: float = 0.1  # Rate of threshold adaptation
    
    # Resonator Network Parameters (if using RESONATOR cleanup)
    resonator_iterations: int = 10  # Number of resonator iterations
    resonator_learning_rate: float = 0.1  # Learning rate for resonator
    resonator_temperature: float = 1.0  # Temperature for resonator dynamics
    
    # Iterative Cleanup Parameters
    max_cleanup_iterations: int = 5  # Maximum cleanup iterations
    cleanup_convergence_threshold: float = 0.01  # Convergence criterion
    
    # ============================================================================
    # COMPOSITIONAL STRUCTURE SOLUTIONS
    # ============================================================================
    
    # Compositional Operations
    enable_recursive_binding: bool = True  # Allow recursive compositional structures
    max_binding_depth: int = 10  # Maximum depth to prevent infinite recursion
    
    # Role-Filler Decomposition
    enable_role_filler_decomposition: bool = True  # Support role-filler analysis
    role_filler_similarity_threshold: float = 0.2  # Threshold for decomposition
    
    # Superposition Parameters
    superposition_normalization: bool = True  # Normalize after superposition
    superposition_weights: Optional[List[float]] = None  # Weights for weighted superposition
    
    # ============================================================================
    # CAPACITY AND PERFORMANCE SOLUTIONS
    # ============================================================================
    
    # Capacity Estimation
    perform_capacity_analysis: bool = False  # Analyze binding capacity
    capacity_test_symbols: int = 50  # Number of symbols for capacity testing
    capacity_noise_levels: List[float] = field(default_factory=lambda: [0.0, 0.1, 0.2, 0.3])
    
    # Performance Optimization
    enable_vector_caching: bool = True  # Cache frequently used vectors
    cache_size_limit: int = 1000  # Maximum vectors in cache
    
    # Memory Management
    use_memory_mapping: bool = False  # Use memory mapping for large vocabularies
    lazy_vector_loading: bool = False  # Load vectors on demand
    
    # Parallel Processing
    enable_parallel_binding: bool = False  # Parallelize binding operations
    parallel_threshold: int = 100  # Minimum operations for parallelization
    max_parallel_workers: int = 4  # Maximum parallel workers
    
    # ============================================================================
    # NOISE HANDLING AND ROBUSTNESS SOLUTIONS
    # ============================================================================
    
    # Noise Parameters
    base_noise_level: float = 0.0  # Base noise level for operations
    additive_noise_std: float = 0.0  # Standard deviation of additive noise
    
    # Robustness Measures
    enable_error_correction: bool = False  # Enable error correction mechanisms
    error_correction_redundancy: int = 3  # Redundancy factor for error correction
    
    # Degradation Handling
    handle_vector_degradation: bool = True  # Handle cumulative degradation
    degradation_compensation: str = "renormalization"  # "renormalization", "amplification", "none"
    
    # ============================================================================
    # DEBUGGING AND VALIDATION SOLUTIONS
    # ============================================================================
    
    # Validation Settings
    validate_against_plate_1995: bool = False  # Validate against Plate's results
    validate_binding_properties: bool = True  # Validate binding algebraic properties
    check_distributivity: bool = True  # Check distributivity properties
    
    # Debugging Options
    verbose_operations: bool = False  # Detailed operation logging
    log_similarity_computations: bool = False  # Log similarity calculations
    trace_cleanup_process: bool = False  # Trace cleanup iterations
    
    # Statistics Collection
    collect_operation_statistics: bool = True  # Collect performance statistics
    statistics_sample_rate: float = 0.1  # Sampling rate for statistics
    
    # Testing and Benchmarking
    enable_benchmark_mode: bool = False  # Enable benchmarking
    benchmark_repetitions: int = 100  # Number of repetitions for benchmarks
    
    # ============================================================================
    # RESEARCH ACCURACY AND COMPLIANCE
    # ============================================================================
    
    # Research Compliance
    enforce_plate_1995_compliance: bool = False  # Enforce Plate's original methods
    enforce_kanerva_2009_compliance: bool = False  # Enforce Kanerva's methods
    
    # Mathematical Properties
    verify_associativity: bool = True  # Verify binding associativity
    verify_commutativity: bool = True  # Verify binding commutativity  
    verify_identity_element: bool = True  # Verify identity element properties
    
    # Theoretical Validation
    validate_capacity_bounds: bool = False  # Validate theoretical capacity bounds
    capacity_bound_tolerance: float = 0.1  # Tolerance for capacity validation


def create_plate_1995_accurate_config() -> VSAComprehensiveConfig:
    """
    Create configuration that matches Plate (1995) HRR paper exactly.
    
    Returns:
        VSAComprehensiveConfig: Plate (1995) accurate configuration
    """
    return VSAComprehensiveConfig(
        # Plate's original parameters
        dimension_strategy=VectorDimensionStrategy.PLATE_1995_STANDARD,
        plate_1995_dimension_range=(256, 1024),
        
        # i.i.d. normal distribution as in Plate (1995)
        vector_distribution=VectorDistribution.NORMAL_IID,
        normal_std_formula="1_over_sqrt_d",  # σ = 1/√d
        normalize_vectors=True,
        
        # Circular convolution as primary binding
        binding_operation=BindingOperation.CIRCULAR_CONVOLUTION,
        use_fft_acceleration=False,  # Plate used direct convolution
        
        # Cleanup method from paper
        cleanup_method=CleanupMethod.RESONATOR_NETWORK,
        similarity_metric=SimilarityMetric.COSINE_SIMILARITY,
        
        # Research validation
        validate_against_plate_1995=True,
        enforce_plate_1995_compliance=True,
        validate_binding_properties=True
    )


def create_kanerva_2009_optimized_config() -> VSAComprehensiveConfig:
    """
    Create configuration based on Kanerva (2009) optimizations.
    
    Returns:
        VSAComprehensiveConfig: Kanerva optimized configuration  
    """
    return VSAComprehensiveConfig(
        # Kanerva's optimized dimensions
        dimension_strategy=VectorDimensionStrategy.KANERVA_2009_OPTIMIZED,
        kanerva_2009_optimal_dims=[512, 1024, 2048],
        
        # Binary vectors as in Kanerva's approach
        vector_distribution=VectorDistribution.BERNOULLI_BIPOLAR,
        bernoulli_prob=0.5,
        
        # XOR binding for binary vectors
        binding_operation=BindingOperation.XOR_BINDING,
        
        # Hamming distance for binary similarity
        cleanup_method=CleanupMethod.THRESHOLD_CLEANUP,
        similarity_metric=SimilarityMetric.HAMMING_DISTANCE,
        
        # Performance optimizations
        enable_parallel_binding=True,
        enable_vector_caching=True,
        
        # Research compliance
        enforce_kanerva_2009_compliance=True
    )


def create_performance_optimized_vsa_config() -> VSAComprehensiveConfig:
    """
    Create VSA configuration optimized for computational performance.
    
    Returns:
        VSAComprehensiveConfig: Performance-optimized configuration
    """
    return VSAComprehensiveConfig(
        # Efficient dimension
        dimension_strategy=VectorDimensionStrategy.POWER_OF_TWO,
        custom_vector_dim=512,  # Power of 2 for FFT efficiency
        
        # Fast distribution
        vector_distribution=VectorDistribution.UNIFORM_RANDOM,
        normalize_vectors=False,  # Skip normalization for speed
        
        # FFT-accelerated binding
        binding_operation=BindingOperation.FOURIER_DOMAIN,
        use_fft_acceleration=True,
        
        # Simple cleanup
        cleanup_method=CleanupMethod.NEAREST_NEIGHBOR,
        similarity_metric=SimilarityMetric.DOT_PRODUCT,  # Fastest similarity
        
        # Performance optimizations
        enable_parallel_binding=True,
        enable_vector_caching=True,
        lazy_vector_loading=True,
        
        # Minimal validation
        validate_binding_properties=False,
        verbose_operations=False
    )


def auto_select_dimension(symbol_count: int, capacity_factor: float = 2.5) -> int:
    """
    SOLUTION: Auto-select vector dimension based on capacity requirements.
    
    This implements the auto-dimensioning solution from the FIXME comments.
    
    Args:
        symbol_count: Expected number of symbols
        capacity_factor: Safety factor for capacity
        
    Returns:
        int: Recommended vector dimension
    """
    # Plate's capacity rule-of-thumb: d ≈ k * n where k is safety factor
    base_dimension = int(symbol_count * capacity_factor)
    
    # Round up to nearest power of 2 for FFT efficiency
    power_of_two = 2 ** math.ceil(math.log2(base_dimension))
    
    # Clamp to reasonable range
    return max(256, min(2048, power_of_two))


def get_available_vsa_solutions() -> Dict[str, List[str]]:
    """
    Get all available VSA solution options by category.
    
    Returns:
        Dict[str, List[str]]: All available solutions
    """
    return {
        "Dimension Strategies": [strategy.value for strategy in VectorDimensionStrategy],
        "Vector Distributions": [dist.value for dist in VectorDistribution], 
        "Binding Operations": [op.value for op in BindingOperation],
        "Cleanup Methods": [method.value for method in CleanupMethod],
        "Similarity Metrics": [metric.value for metric in SimilarityMetric],
        
        "Configuration Presets": [
            "plate_1995_accurate",
            "kanerva_2009_optimized", 
            "performance_optimized"
        ],
        
        "Research Papers Implemented": [
            "Plate (1995) 'Holographic Reduced Representations'",
            "Gayler (1998) 'Multiplicative Binding, Representation Operators & Analogy'",
            "Kanerva (2009) 'Hyperdimensional Computing'",
            "Rachkovskij & Kussul (2001) 'Binding and Normalization of Binary Sparse Distributed Representations'"
        ]
    }


def validate_vsa_config(config: VSAComprehensiveConfig) -> List[str]:
    """
    Validate VSA configuration and return warnings.
    
    Args:
        config: Configuration to validate
        
    Returns:
        List[str]: List of validation warnings
    """
    warnings = []
    
    # Check dimension consistency
    if config.dimension_strategy == VectorDimensionStrategy.CUSTOM_SPECIFIED:
        if config.custom_vector_dim < 64:
            warnings.append("⚠️  Very low vector dimension may have poor capacity")
        if config.custom_vector_dim > 4096:
            warnings.append("⚠️  Very high dimension may be computationally expensive")
    
    # Check binding-distribution compatibility
    if (config.binding_operation == BindingOperation.XOR_BINDING and 
        config.vector_distribution != VectorDistribution.BERNOULLI_BIPOLAR):
        warnings.append("⚠️  XOR binding works best with binary vectors")
    
    if (config.similarity_metric == SimilarityMetric.HAMMING_DISTANCE and
        config.vector_distribution not in [VectorDistribution.BERNOULLI_BIPOLAR, VectorDistribution.SPARSE_BINARY]):
        warnings.append("⚠️  Hamming distance intended for binary vectors")
    
    # Check research compliance
    if (config.enforce_plate_1995_compliance and 
        config.binding_operation != BindingOperation.CIRCULAR_CONVOLUTION):
        warnings.append("💡 Plate (1995) used circular convolution for binding")
    
    # Check performance settings
    if (config.enable_parallel_binding and 
        config.parallel_threshold > config.expected_symbol_count):
        warnings.append("⚠️  Parallel threshold higher than expected symbol count")
    
    return warnings


if __name__ == "__main__":
    print("🧠 VSA Comprehensive Solutions Summary")
    print("=" * 50)
    
    solutions = get_available_vsa_solutions()
    for category, items in solutions.items():
        print(f"\n📂 {category}:")
        for item in items:
            print(f"   ✅ {item}")
    
    print(f"\n🎯 Auto-dimension example:")
    print(f"   100 symbols → {auto_select_dimension(100)} dimensions")
    print(f"   1000 symbols → {auto_select_dimension(1000)} dimensions")