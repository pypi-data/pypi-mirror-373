"""
Holographic Memory Modules

Modular components for the Holographic Reduced Representations memory system.
Based on Tony Plate's Vector Symbolic Architecture (VSA).

Author: Benedict Chen (benedict@benedictchen.com)
"""

from .configuration import HRRConfig, HRRMemoryItem, create_config
from .vector_operations import VectorOperations
from .memory_management import MemoryManager
from .composite_operations import CompositeOperations
from .cleanup_operations import CleanupOperations
from .capacity_analysis import CapacityAnalyzer
from .holographic_core import HolographicMemoryCore, HolographicMemory, create_holographic_memory

__all__ = [
    # Configuration
    'HRRConfig',
    'HRRMemoryItem', 
    'create_config',
    
    # Core modules
    'VectorOperations',
    'MemoryManager',
    'CompositeOperations',
    'CleanupOperations',
    'CapacityAnalyzer',
    
    # Main class and factory
    'HolographicMemoryCore',
    'HolographicMemory',  # Backward compatibility alias
    'create_holographic_memory',
]

__version__ = "2.0.0"
__author__ = "Benedict Chen"
__email__ = "benedict@benedictchen.com"