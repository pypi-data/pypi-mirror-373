"""
🌀 Core Module for Holographic Memory System
===========================================

This module provides the core functionality for Holographic Reduced Representations (HRR)
and Vector Symbolic Architecture (VSA) operations. It implements the foundational
algorithms from Tony Plate's research and modern extensions.

Main Components:
- HolographicMemory: Main memory system class
- HRROperations: Core binding and unbinding operations  
- AssociativeMemory: Associative memory with cleanup
- MemoryTrace: Individual memory trace management
- CompositionalHRR: Compositional structure operations

Based on:
- Plate (1995) "Holographic Reduced Representations"
- Hinton (1981) "Implementing Semantic Networks in Parallel Hardware"
"""

from .holographic_memory import HolographicMemory
from .hrr_operations import HRROperations, HRRVector
from .associative_memory import AssociativeMemory, MemoryTrace
from .compositional_hrr import CompositionalHRR
from .memory_management import MemoryManager

__all__ = [
    'HolographicMemory',
    'HRROperations', 
    'HRRVector',
    'AssociativeMemory',
    'MemoryTrace',
    'CompositionalHRR',
    'MemoryManager'
]