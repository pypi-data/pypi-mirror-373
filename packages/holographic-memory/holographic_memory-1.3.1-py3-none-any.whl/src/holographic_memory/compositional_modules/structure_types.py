"""
Structure Types and Core Data Structures

Defines the fundamental data structures and enums for compositional structures
in Holographic Reduced Representations.
"""

import numpy as np
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum


class StructureType(Enum):
    """Types of compositional structures"""
    SEQUENCE = "sequence"
    TREE = "tree"
    GRAPH = "graph"
    SET = "set"
    RECORD = "record"
    STACK = "stack"
    QUEUE = "queue"
    MAP = "map"


@dataclass
class StructureNode:
    """Node in a compositional structure"""
    value: Union[str, np.ndarray, 'VSASymbol']
    node_id: str
    node_type: str = "data"
    children: List['StructureNode'] = field(default_factory=list)
    parent: Optional['StructureNode'] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CompositionRule:
    """Rule for composing structures"""
    rule_name: str
    structure_types: List[StructureType]
    composition_function: callable
    requirements: Dict[str, Any] = field(default_factory=dict)


# Tree specification type helper for type hints
TreeSpec = Union[Dict[str, Any], Any]