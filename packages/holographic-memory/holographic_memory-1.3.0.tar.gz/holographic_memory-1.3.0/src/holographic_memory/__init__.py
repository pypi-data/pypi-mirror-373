"""
Holographic Memory Package

Modular implementation of Holographic Reduced Representations (HRR) memory system
based on Tony Plate's Vector Symbolic Architecture (VSA).

Author: Benedict Chen (benedict@benedictchen.com)
"""

# Import the main classes for easy access
from .hm_modules import (
    HolographicMemory,
    HolographicMemoryCore,
    create_holographic_memory,
    HRRConfig,
    create_config,
)

# Keep the original holographic_memory.py available for backward compatibility
try:
    from . import holographic_memory as legacy
except ImportError:
    legacy = None

__all__ = [
    'HolographicMemory',
    'HolographicMemoryCore', 
    'create_holographic_memory',
    'HRRConfig',
    'create_config',
]

__version__ = "2.0.0"
__author__ = "Benedict Chen"
__email__ = "benedict@benedictchen.com"