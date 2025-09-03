"""
💰 SUPPORT THIS RESEARCH - PLEASE DONATE! 💰

🙏 If this library helps your research or project, please consider donating:
💳 https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS

Your support makes advanced AI research accessible to everyone! 🚀

Holographic Memory Library  
========================

Based on: Plate (1995) "Holographic Reduced Representations"
         Hinton (1981) "Implementing Semantic Networks in Parallel Hardware"

This library implements the foundational Vector Symbolic Architecture (VSA) 
that revolutionized distributed representation in neural networks.

🔬 Research Foundation:
- Tony Plate's Holographic Reduced Representations (HRR)
- Geoffrey Hinton's distributed memory principles
- Vector Symbolic Architecture (VSA) framework
- Circular convolution for binding operations

🎯 Key Features:
- Holographic binding and unbinding operations
- Associative memory with cleanup networks
- Compositional structure representation
- Memory management and optimization
- Research-accurate HRR implementations
"""

def _print_attribution():
    """Print attribution message with donation link"""
    try:
        print("\\n🌀 Holographic Memory Library - Made possible by Benedict Chen")
        print("   \\033]8;;mailto:benedict@benedictchen.com\\033\\\\benedict@benedictchen.com\\033]8;;\\033\\\\")
        print("")
        print("💰 PLEASE DONATE! Your support keeps this research alive! 💰")
        print("   🔗 \\033]8;;https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS\\033\\\\💳 CLICK HERE TO DONATE VIA PAYPAL\\033]8;;\\033\\\\")
        print("")
        print("   ☕ Buy me a coffee → 🍺 Buy me a beer → 🏎️ Buy me a Lamborghini → ✈️ Buy me a private jet!")
        print("   (Start small, dream big! Every donation helps! 😄)")
        print("")
    except:
        print("\\n🌀 Holographic Memory Library - Made possible by Benedict Chen")
        print("   benedict@benedictchen.com")
        print("")
        print("💰 PLEASE DONATE! Your support keeps this research alive! 💰")
        print("   💳 PayPal: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS")
        print("")
        print("   ☕ Buy me a coffee → 🍺 Buy me a beer → 🏎️ Buy me a Lamborghini → ✈️ Buy me a private jet!")
        print("   (Start small, dream big! Every donation helps! 😄)")

# ===============================================================================
# 🚀 NEW MODULAR ARCHITECTURE - Clean, Testable, Maintainable (v2.1.0)
# ===============================================================================

# Core holographic memory system (PRESERVED - All existing functionality)
from .core.holographic_memory import HolographicMemory
from .core.hrr_operations import HRROperations, HRRVector
from .core.associative_memory import AssociativeMemory, MemoryTrace, CleanupResult
from .core.compositional_hrr import CompositionalHRR
from .core.memory_management import MemoryManager, VectorRecord

# ===============================================================================
# 🔬 NEW: COMPLETE RESEARCH-ACCURATE CLEANUP IMPLEMENTATIONS (Added v2.2.0)
# ===============================================================================

# Complete Plate (1995) cleanup system - ALL FIXME solutions implemented
from .complete_holographic_cleanup import (
    CompletePlateCleanupSystem,
    create_plate_1995_cleanup_system,
    create_legacy_compatible_cleanup_system,
    create_high_performance_cleanup_system,
    CleanupResult as EnhancedCleanupResult,
    CapacityInfo,
    MemoryTrace as EnhancedMemoryTrace
)

# Configuration system for complete cleanup implementations
from .holographic_cleanup_config import (
    HolographicCleanupConfig,
    CleanupMethod,
    AssociativeMemoryType,
    ConvergenceStrategy,
    NoiseToleranceStrategy,
    create_plate_1995_config,
    create_legacy_compatible_config,
    create_high_performance_config,
    create_research_validation_config
)

# Configuration system
from .config.config_classes import (
    HolographicConfig,
    VectorConfig, 
    MemoryConfig,
    CleanupConfig,
    PerformanceConfig,
    ExperimentConfig
)
from .config.enums import (
    BindingMethod,
    CleanupStrategy,
    VectorDistribution,
    MemoryType,
    StorageFormat
)
from .config.defaults import (
    DEFAULT_HOLOGRAPHIC_CONFIG,
    get_config,
    list_presets,
    PRESET_CONFIGS
)

# Utility functions
from .utils.vector_utils import (
    create_random_vectors,
    normalize_vector,
    add_noise,
    compute_similarity,
    vector_statistics
)
from .utils.math_utils import (
    circular_convolution,
    circular_correlation,
    fft_convolution,
    fft_correlation
)
from .utils.validation import (
    validate_vector_dimension,
    validate_similarity_range,
    validate_config_consistency,
    sanitize_inputs
)
from .utils.data_utils import (
    save_memory_state,
    load_memory_state,
    export_vectors,
    import_vectors
)
from .utils.performance import (
    ProfileManager,
    MemoryTracker,
    TimeTracker,
    benchmark_operation
)
from .utils.analysis import (
    analyze_vector_distribution,
    measure_binding_quality,
    capacity_analysis,
    noise_robustness_test
)

# Visualization functions (optional import)
try:
    from .visualization.vector_plots import (
        plot_vector_distribution,
        plot_vector_similarity_matrix,
        plot_vector_pca
    )
    from .visualization.memory_plots import (
        plot_memory_capacity,
        plot_noise_robustness,
        plot_memory_statistics
    )
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False

# Show attribution on library import
_print_attribution()

__version__ = "2.1.0"
__authors__ = ["Based on Plate (1995)"]

# Define explicit public API
__all__ = [
    # ===============================================================================
    # Core Classes - Main holographic memory functionality
    # ===============================================================================
    "HolographicMemory",           # Main holographic memory system
    "HRROperations",               # Core HRR operations (bind, unbind, compose)
    "HRRVector",                   # Holographic vector representation
    "AssociativeMemory",           # Associative memory with cleanup
    "CompositionalHRR",            # Compositional structure operations
    "MemoryManager",               # Memory lifecycle management
    
    # ===============================================================================
    # Configuration System - Structured parameter management
    # ===============================================================================
    "HolographicConfig",           # Main configuration class
    "VectorConfig",                # Vector-specific configuration
    "MemoryConfig",                # Memory system configuration
    "CleanupConfig",               # Cleanup operation configuration
    "PerformanceConfig",           # Performance optimization settings
    "ExperimentConfig",            # Experiment configuration
    
    # Configuration enums
    "BindingMethod",               # Binding operation methods
    "CleanupStrategy",             # Cleanup strategies
    "VectorDistribution",          # Vector generation distributions
    "MemoryType",                  # Memory system types
    "StorageFormat",               # Data storage formats
    
    # Default configurations
    "DEFAULT_HOLOGRAPHIC_CONFIG",  # Default system configuration
    "get_config",                  # Get preset configuration
    "list_presets",                # List available presets
    "PRESET_CONFIGS",              # All preset configurations
    
    # ===============================================================================
    # Utility Functions - Helper functions and analysis tools
    # ===============================================================================
    # Vector utilities
    "create_random_vectors",       # Create random vector collections
    "normalize_vector",            # Vector normalization
    "add_noise",                   # Add noise to vectors
    "compute_similarity",          # Compute vector similarity
    "vector_statistics",           # Analyze vector properties
    
    # Mathematical utilities
    "circular_convolution",        # Circular convolution operation
    "circular_correlation",        # Circular correlation operation
    "fft_convolution",             # FFT-based convolution (faster)
    "fft_correlation",             # FFT-based correlation (faster)
    
    # Validation utilities
    "validate_vector_dimension",   # Validate vector dimensions
    "validate_similarity_range",   # Validate similarity values
    "validate_config_consistency", # Validate configuration consistency
    "sanitize_inputs",             # Sanitize input parameters
    
    # Data utilities
    "save_memory_state",           # Save memory system state
    "load_memory_state",           # Load memory system state
    "export_vectors",              # Export vectors to external formats
    "import_vectors",              # Import vectors from external formats
    
    # Performance utilities
    "ProfileManager",              # Performance profiling manager
    "MemoryTracker",               # Memory usage tracking
    "TimeTracker",                 # Execution time tracking
    "benchmark_operation",         # Benchmark functions
    
    # Analysis utilities
    "analyze_vector_distribution", # Analyze vector statistical properties
    "measure_binding_quality",     # Measure binding operation quality
    "capacity_analysis",           # Analyze memory capacity
    "noise_robustness_test",       # Test robustness to noise
    
    # ===============================================================================
    # Data Classes - Supporting data structures (PRESERVED)
    # ===============================================================================
    "MemoryTrace",                 # Memory trace representation
    "CleanupResult",               # Cleanup operation result
    "VectorRecord",                # Managed vector record
    
    # ===============================================================================
    # NEW: Complete Research-Accurate Cleanup System (Added v2.2.0)
    # ===============================================================================
    # Complete Plate (1995) cleanup implementations - ALL FIXME solutions
    "CompletePlateCleanupSystem",  # Complete cleanup system with all research methods
    "create_plate_1995_cleanup_system",      # Research-accurate factory
    "create_legacy_compatible_cleanup_system", # Backward compatibility factory  
    "create_high_performance_cleanup_system", # Performance-optimized factory
    "EnhancedCleanupResult",       # Enhanced cleanup result with diagnostics
    "CapacityInfo",                # Capacity analysis information
    "EnhancedMemoryTrace",         # Enhanced memory trace with access tracking
    
    # Configuration system for complete cleanup
    "HolographicCleanupConfig",    # Main cleanup configuration class
    "CleanupMethod",               # Cleanup method enumeration
    "AssociativeMemoryType",       # Associative memory type enumeration
    "ConvergenceStrategy",         # Convergence strategy enumeration
    "NoiseToleranceStrategy",      # Noise tolerance strategy enumeration
    "create_plate_1995_config",    # Research-accurate config factory
    "create_legacy_compatible_config", # Legacy compatibility config factory
    "create_high_performance_config",  # Performance config factory
    "create_research_validation_config", # Research validation config factory
]

# Add visualization functions to __all__ if available
if VISUALIZATION_AVAILABLE:
    __all__.extend([
        # Vector visualization
        "plot_vector_distribution",
        "plot_vector_similarity_matrix", 
        "plot_vector_pca",
        
        # Memory system visualization
        "plot_memory_capacity",
        "plot_noise_robustness",
        "plot_memory_statistics",
    ])

"""
💝 Thank you for using this research software! 💝

📚 If this work contributed to your research, please:
💳 DONATE: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS
📝 CITE: Benedict Chen (2025) - Holographic Memory Research Implementation

Your support enables continued development of cutting-edge AI research tools! 🎓✨
"""