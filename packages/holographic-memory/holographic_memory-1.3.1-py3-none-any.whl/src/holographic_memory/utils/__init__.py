"""
🛠️ Utility Functions for Holographic Memory
==========================================

This module provides utility functions for vector operations, validation,
mathematical computations, and data handling in the holographic memory system.

Author: Benedict Chen (benedict@benedictchen.com)
"""

from .vector_utils import (
    create_random_vectors,
    normalize_vector,
    add_noise,
    compute_similarity,
    orthogonalize_vectors,
    project_vector,
    vector_statistics
)

from .math_utils import (
    circular_convolution,
    circular_correlation,
    fft_convolution,
    complex_exponential,
    phase_encoding,
    magnitude_phase_split,
    statistical_tests
)

from .validation import (
    validate_vector_dimension,
    validate_similarity_range,
    validate_memory_capacity,
    validate_config_consistency,
    check_vector_properties,
    sanitize_inputs
)

from .data_utils import (
    save_memory_state,
    load_memory_state,
    export_vectors,
    import_vectors,
    convert_format,
    compress_data,
    decompress_data
)

from .performance import (
    ProfileManager,
    MemoryTracker,
    TimeTracker,
    benchmark_operation,
    memory_usage,
    execution_timer
)

from .analysis import (
    analyze_vector_distribution,
    measure_binding_quality,
    capacity_analysis,
    noise_robustness_test,
    similarity_matrix,
    clustering_analysis,
    dimensionality_analysis
)

__all__ = [
    # Vector utilities
    'create_random_vectors',
    'normalize_vector',
    'add_noise',
    'compute_similarity',
    'orthogonalize_vectors',
    'project_vector',
    'vector_statistics',
    
    # Mathematical utilities
    'circular_convolution',
    'circular_correlation',
    'fft_convolution',
    'complex_exponential',
    'phase_encoding',
    'magnitude_phase_split',
    'statistical_tests',
    
    # Validation utilities
    'validate_vector_dimension',
    'validate_similarity_range',
    'validate_memory_capacity',
    'validate_config_consistency',
    'check_vector_properties',
    'sanitize_inputs',
    
    # Data utilities
    'save_memory_state',
    'load_memory_state',
    'export_vectors',
    'import_vectors',
    'convert_format',
    'compress_data',
    'decompress_data',
    
    # Performance utilities
    'ProfileManager',
    'MemoryTracker',
    'TimeTracker',
    'benchmark_operation',
    'memory_usage',
    'execution_timer',
    
    # Analysis utilities
    'analyze_vector_distribution',
    'measure_binding_quality',
    'capacity_analysis',
    'noise_robustness_test',
    'similarity_matrix',
    'clustering_analysis',
    'dimensionality_analysis'
]