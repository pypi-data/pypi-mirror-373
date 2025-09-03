"""
Compositional Modules for Holographic Reduced Representations

Modular components for compositional structures, implementing research-accurate
solutions based on Plate (1995) "Holographic Reduced Representations".
"""

from .structure_types import StructureType, StructureNode, CompositionRule
from .reduced_representations import ReducedRepresentationEngine
from .compositional_cleanup import CompositionalCleanupEngine
from .analogy_engine import AnalogyEngine
from .capacity_monitor import CapacityMonitor
from .structure_creation import StructureCreationMixin
from .structure_primitives import StructurePrimitives

__all__ = [
    'StructureType',
    'StructureNode', 
    'CompositionRule',
    'ReducedRepresentationEngine',
    'CompositionalCleanupEngine',
    'AnalogyEngine',
    'CapacityMonitor',
    'StructureCreationMixin',
    'StructurePrimitives'
]