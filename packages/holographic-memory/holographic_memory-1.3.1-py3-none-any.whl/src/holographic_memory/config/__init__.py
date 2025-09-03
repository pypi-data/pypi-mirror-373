"""
🔧 Configuration Module for Holographic Memory
============================================

This module provides configuration classes, enums, and default settings
for the holographic memory system.

Author: Benedict Chen (benedict@benedictchen.com)
"""

from .enums import (
    BindingMethod,
    CleanupStrategy,
    VectorDistribution,
    MemoryType,
    StorageFormat
)

from .config_classes import (
    HolographicConfig,
    VectorConfig,
    MemoryConfig,
    CleanupConfig,
    PerformanceConfig,
    ExperimentConfig
)

from .defaults import (
    DEFAULT_HOLOGRAPHIC_CONFIG,
    DEFAULT_VECTOR_CONFIG,
    DEFAULT_MEMORY_CONFIG,
    DEFAULT_CLEANUP_CONFIG,
    DEFAULT_PERFORMANCE_CONFIG,
    PRESET_CONFIGS
)

__all__ = [
    # Enums
    'BindingMethod',
    'CleanupStrategy', 
    'VectorDistribution',
    'MemoryType',
    'StorageFormat',
    
    # Config Classes
    'HolographicConfig',
    'VectorConfig',
    'MemoryConfig',
    'CleanupConfig',
    'PerformanceConfig',
    'ExperimentConfig',
    
    # Defaults and Presets
    'DEFAULT_HOLOGRAPHIC_CONFIG',
    'DEFAULT_VECTOR_CONFIG',
    'DEFAULT_MEMORY_CONFIG',
    'DEFAULT_CLEANUP_CONFIG',
    'DEFAULT_PERFORMANCE_CONFIG',
    'PRESET_CONFIGS'
]