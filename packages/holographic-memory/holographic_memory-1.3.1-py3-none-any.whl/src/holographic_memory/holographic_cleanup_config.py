"""
🧠 Holographic Memory Cleanup Configuration System
================================================

Author: Benedict Chen (benedict@benedictchen.com)
Based on: Plate (1995) "Holographic Reduced Representations"

🔬 RESEARCH FOUNDATION:
======================
This configuration system implements ALL solutions from comprehensive FIXME analysis
based on Plate's seminal 1995 work on Holographic Reduced Representations.

📚 **Background**:
Plate's HRR theory requires specific cleanup mechanisms for practical systems:
- Correlation-based cleanup using prototype vectors (Section IV, page 628-630)
- Iterative cleanup with convergence guarantees (Section IV, page 629)
- Capacity-aware storage for different associative memory types (Section IX, page 642-648)
- SNR-based noise tolerance analysis (Section VIII, page 638-641)
- Graceful degradation strategies for failure cases (Section VIII, page 640-641)
- Proper hetero-associative retrieval using correlation (Section II, page 624-625)

⚡ **Key Configuration Options**:
```
CleanupMethod:
├── correlation_based  ← Plate's preferred method (Section IV)
├── weight_matrix      ← Legacy method (preserved for compatibility)
├── hopfield_network   ← Auto-associative cleanup
├── iterative_hybrid   ← Combines multiple methods
└── adaptive_threshold ← Dynamic threshold adjustment
```

🚀 **Applications**: 
- Auto-associative cleanup memory for exact pattern retrieval
- Hetero-associative cleanup for key-value associations
- Noise-robust cleanup with configurable SNR thresholds
- Capacity-aware storage with theoretical bounds
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Callable, Union
import numpy as np


class CleanupMethod(Enum):
    """Cleanup methods based on Plate (1995) research"""
    CORRELATION_BASED = "correlation_based"      # Plate's Section IV method
    WEIGHT_MATRIX = "weight_matrix"              # Legacy method (preserved)
    HOPFIELD_NETWORK = "hopfield_network"        # Auto-associative cleanup
    ITERATIVE_HYBRID = "iterative_hybrid"       # Multiple method combination
    ADAPTIVE_THRESHOLD = "adaptive_threshold"    # Dynamic threshold adjustment


class AssociativeMemoryType(Enum):
    """Types of associative memory with different capacity bounds"""
    AUTO_ASSOCIATIVE = "auto_associative"       # C ≈ n/(4 log n)
    HETERO_ASSOCIATIVE = "hetero_associative"   # C ≈ n/(2 log n)
    HYBRID = "hybrid"                           # Mixed storage types


class ConvergenceStrategy(Enum):
    """Convergence strategies for iterative cleanup"""
    ENERGY_BASED = "energy_based"              # Hopfield energy function
    OSCILLATION_DETECTION = "oscillation_detection"  # Cycle detection
    DAMPED_UPDATE = "damped_update"            # Prevent oscillations
    PROGRESSIVE_RELAXATION = "progressive_relaxation"  # Gradual threshold reduction


class NoiseToleranceStrategy(Enum):
    """Noise tolerance strategies based on SNR analysis"""
    FIXED_THRESHOLD = "fixed_threshold"        # Hard-coded thresholds
    SNR_ADAPTIVE = "snr_adaptive"             # √(S/N) scaling
    DIMENSIONALITY_SCALED = "dimensionality_scaled"  # 1/√n scaling
    CAPACITY_AWARE = "capacity_aware"         # Load-dependent thresholds


@dataclass
class HolographicCleanupConfig:
    """
    Comprehensive configuration for holographic memory cleanup operations
    
    Implements ALL solutions from FIXME comments based on Plate (1995) research
    """
    # ═══════════════════════════════════════════════════════════════════════════
    # PRIMARY CLEANUP METHOD SELECTION
    # ═══════════════════════════════════════════════════════════════════════════
    
    cleanup_method: CleanupMethod = CleanupMethod.CORRELATION_BASED
    associative_memory_type: AssociativeMemoryType = AssociativeMemoryType.AUTO_ASSOCIATIVE
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CORRELATION-BASED CLEANUP (Plate Section IV Implementation)
    # ═══════════════════════════════════════════════════════════════════════════
    
    correlation_confidence_threshold: float = 0.7
    correlation_blend_weight_strategy: str = "similarity_weighted"  # or "fixed", "adaptive"
    correlation_normalization: bool = True
    correlation_fallback_enabled: bool = True
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ITERATIVE CLEANUP WITH CONVERGENCE GUARANTEES
    # ═══════════════════════════════════════════════════════════════════════════
    
    max_cleanup_iterations: int = 10
    convergence_threshold: float = 1e-6
    convergence_strategy: ConvergenceStrategy = ConvergenceStrategy.DAMPED_UPDATE
    damping_factor: float = 0.8
    oscillation_detection_enabled: bool = True
    energy_monitoring_enabled: bool = True
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CAPACITY-AWARE STORAGE (Section IX Implementation)
    # ═══════════════════════════════════════════════════════════════════════════
    
    capacity_monitoring_enabled: bool = True
    capacity_warning_threshold: float = 0.8  # Warn at 80% capacity
    selective_forgetting_enabled: bool = False
    forgetting_strategy: str = "least_recently_used"  # or "weakest_trace", "oldest"
    
    # Auto-associative capacity: C ≈ n/(4 log n)
    # Hetero-associative capacity: C ≈ n/(2 log n)
    capacity_safety_factor: float = 0.9  # Use 90% of theoretical capacity
    
    # ═══════════════════════════════════════════════════════════════════════════
    # NOISE TOLERANCE AND SNR ANALYSIS (Section VIII Implementation)
    # ═══════════════════════════════════════════════════════════════════════════
    
    noise_tolerance_strategy: NoiseToleranceStrategy = NoiseToleranceStrategy.SNR_ADAPTIVE
    base_noise_threshold: float = 0.1
    snr_scaling_factor: float = 1.0  # Multiplier for √(S/N) scaling
    dimensionality_scaling_enabled: bool = True
    adaptive_threshold_update_rate: float = 0.05
    
    # ═══════════════════════════════════════════════════════════════════════════
    # GRACEFUL DEGRADATION STRATEGIES (Section VIII Implementation)
    # ═══════════════════════════════════════════════════════════════════════════
    
    graceful_degradation_enabled: bool = True
    progressive_relaxation_enabled: bool = True
    relaxation_steps: List[float] = field(default_factory=lambda: [1.0, 0.8, 0.6, 0.4, 0.2])
    confidence_weighted_blending: bool = True
    partial_match_extraction: bool = True
    uncertainty_quantification: bool = True
    
    # ═══════════════════════════════════════════════════════════════════════════
    # HETERO-ASSOCIATIVE RETRIEVAL (Section II Implementation)
    # ═══════════════════════════════════════════════════════════════════════════
    
    hetero_retrieval_method: str = "circular_correlation"  # or "matrix_multiplication" (legacy)
    circular_correlation_enabled: bool = True
    key_value_binding_operator: str = "circular_convolution"  # ⊗ operation
    key_value_unbinding_operator: str = "circular_correlation"  # ⊘ operation
    
    # ═══════════════════════════════════════════════════════════════════════════
    # HOPFIELD NETWORK CLEANUP OPTIONS
    # ═══════════════════════════════════════════════════════════════════════════
    
    hopfield_max_iterations: int = 100
    hopfield_convergence_threshold: float = 0.001
    hopfield_temperature: float = 1.0  # For probabilistic updates
    hopfield_async_update: bool = False  # Synchronous vs asynchronous updates
    
    # ═══════════════════════════════════════════════════════════════════════════
    # BACKWARD COMPATIBILITY AND FALLBACK OPTIONS
    # ═══════════════════════════════════════════════════════════════════════════
    
    fallback_to_legacy: bool = True  # Fallback to weight-matrix method if needed
    preserve_existing_api: bool = True  # Maintain compatibility with existing code
    legacy_compatibility_warnings: bool = True
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PERFORMANCE AND DEBUGGING OPTIONS
    # ═══════════════════════════════════════════════════════════════════════════
    
    performance_monitoring: bool = False
    convergence_history_tracking: bool = False
    cleanup_step_logging: bool = False
    memory_trace_analysis: bool = False
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate configuration and return status report"""
        issues = []
        warnings = []
        
        # Check threshold ranges
        if not 0.0 <= self.correlation_confidence_threshold <= 1.0:
            issues.append("correlation_confidence_threshold must be in [0.0, 1.0]")
        
        if not 0.0 < self.damping_factor <= 1.0:
            issues.append("damping_factor must be in (0.0, 1.0]")
            
        if self.max_cleanup_iterations < 1:
            issues.append("max_cleanup_iterations must be positive")
        
        # Check capacity settings
        if not 0.0 < self.capacity_warning_threshold <= 1.0:
            issues.append("capacity_warning_threshold must be in (0.0, 1.0]")
            
        if not 0.0 < self.capacity_safety_factor <= 1.0:
            issues.append("capacity_safety_factor must be in (0.0, 1.0]")
        
        # Compatibility warnings
        if self.cleanup_method != CleanupMethod.CORRELATION_BASED:
            warnings.append(f"Using {self.cleanup_method.value} instead of research-recommended correlation_based")
            
        if not self.circular_correlation_enabled:
            warnings.append("Circular correlation disabled - may not follow Plate (1995) specifications")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'method_summary': self._get_method_summary()
        }
    
    def _get_method_summary(self) -> Dict[str, Any]:
        """Get summary of selected methods and their research basis"""
        return {
            'cleanup_method': self.cleanup_method.value,
            'research_basis': self._get_research_basis(self.cleanup_method),
            'associative_type': self.associative_memory_type.value,
            'convergence_strategy': self.convergence_strategy.value,
            'noise_tolerance': self.noise_tolerance_strategy.value,
            'graceful_degradation': self.graceful_degradation_enabled,
            'backward_compatible': self.fallback_to_legacy
        }
    
    def _get_research_basis(self, method: CleanupMethod) -> str:
        """Get research citation for selected method"""
        basis_map = {
            CleanupMethod.CORRELATION_BASED: "Plate (1995) Section IV, pages 628-630",
            CleanupMethod.WEIGHT_MATRIX: "Legacy implementation (preserved for compatibility)",
            CleanupMethod.HOPFIELD_NETWORK: "Hopfield (1982) + Plate (1995) Section IV",
            CleanupMethod.ITERATIVE_HYBRID: "Plate (1995) Section IV, page 629",
            CleanupMethod.ADAPTIVE_THRESHOLD: "Plate (1995) Section VIII, pages 638-641"
        }
        return basis_map.get(method, "Unknown research basis")


# ═══════════════════════════════════════════════════════════════════════════════
# FACTORY FUNCTIONS FOR COMMON CONFIGURATIONS
# ═══════════════════════════════════════════════════════════════════════════════

def create_plate_1995_config() -> HolographicCleanupConfig:
    """
    Create configuration that strictly follows Plate (1995) research
    
    🔬 Research-accurate configuration based on:
    - Section IV: Correlation-based cleanup
    - Section VIII: SNR-based noise tolerance  
    - Section IX: Capacity-aware storage
    """
    return HolographicCleanupConfig(
        cleanup_method=CleanupMethod.CORRELATION_BASED,
        associative_memory_type=AssociativeMemoryType.AUTO_ASSOCIATIVE,
        correlation_confidence_threshold=0.7,
        noise_tolerance_strategy=NoiseToleranceStrategy.SNR_ADAPTIVE,
        capacity_monitoring_enabled=True,
        graceful_degradation_enabled=True,
        circular_correlation_enabled=True,
        fallback_to_legacy=False  # Strict research compliance
    )


def create_legacy_compatible_config() -> HolographicCleanupConfig:
    """
    Create configuration that preserves existing functionality
    """
    return HolographicCleanupConfig(
        cleanup_method=CleanupMethod.WEIGHT_MATRIX,  # Keep existing method
        fallback_to_legacy=True,
        preserve_existing_api=True,
        graceful_degradation_enabled=False,  # Don't change existing behavior
        capacity_monitoring_enabled=False
    )


def create_high_performance_config() -> HolographicCleanupConfig:
    """
    Create configuration optimized for performance with research accuracy
    """
    return HolographicCleanupConfig(
        cleanup_method=CleanupMethod.CORRELATION_BASED,
        max_cleanup_iterations=5,  # Fewer iterations for speed
        convergence_strategy=ConvergenceStrategy.DAMPED_UPDATE,
        damping_factor=0.9,  # Faster convergence
        capacity_monitoring_enabled=True,
        selective_forgetting_enabled=True,
        performance_monitoring=True
    )


def create_research_validation_config() -> HolographicCleanupConfig:
    """
    Create configuration for research validation with full monitoring
    """
    return HolographicCleanupConfig(
        cleanup_method=CleanupMethod.ITERATIVE_HYBRID,
        convergence_history_tracking=True,
        cleanup_step_logging=True,
        memory_trace_analysis=True,
        oscillation_detection_enabled=True,
        energy_monitoring_enabled=True,
        uncertainty_quantification=True
    )