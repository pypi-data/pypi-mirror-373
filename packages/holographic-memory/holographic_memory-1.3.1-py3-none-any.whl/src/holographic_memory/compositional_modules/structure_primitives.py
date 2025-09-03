"""
Structure Primitives for Compositional HRR

Core functionality and management for compositional structures. This module
has been split for 800-line compliance - creation methods moved to structure_creation.py.
"""

import numpy as np
from typing import Dict, Any, List, Optional, Union, Tuple, Set
import json
import logging

from .structure_types import StructureType, StructureNode, CompositionRule, TreeSpec
from .reduced_representations import ReducedRepresentationEngine
from .compositional_cleanup import CompositionalCleanupEngine
from .analogy_engine import AnalogyEngine
from .capacity_monitor import CapacityMonitor
from .structure_creation import StructureCreationMixin

logger = logging.getLogger(__name__)


class StructurePrimitives(StructureCreationMixin):
    """
    Core structure primitives and operations for Compositional HRR
    
    This class implements the main CompositionalHRR functionality including
    sequence, tree, record, graph, set, and stack creation with comprehensive
    FIXME resolution and research-accurate implementations.
    
    Structure creation methods are inherited from StructureCreationMixin.
    """
    
    def __init__(self,
                 vector_dim: int = 512,
                 vsa: Optional['VectorSymbolicArchitecture'] = None,
                 normalize_vectors: bool = True,
                 random_seed: Optional[int] = None,
                 enable_advanced_features: bool = True):
        """
        Initialize Structure Primitives
        
        Args:
            vector_dim: Dimensionality of vectors
            vsa: Vector Symbolic Architecture (created if None)
            normalize_vectors: Whether to normalize vectors
            random_seed: Random seed for reproducibility
            enable_advanced_features: Enable advanced FIXME resolution features
        """
        self.vector_dim = vector_dim
        self.normalize_vectors = normalize_vectors
        
        if random_seed is not None:
            np.random.seed(random_seed)
        
        # Initialize VSA if not provided
        if vsa is None:
            # Import here to avoid circular imports
            from ..vector_symbolic import VectorSymbolicArchitecture
            self.vsa = VectorSymbolicArchitecture(
                vector_dim=vector_dim,
                normalize_vectors=normalize_vectors,
                random_seed=random_seed
            )
        else:
            self.vsa = vsa
        
        # Initialize HRR memory for underlying operations
        from ..core.holographic_memory import HolographicMemory
        self.hrr_memory = HolographicMemory(
            vector_dim=vector_dim,
            normalize_vectors=normalize_vectors
        )
        
        # Structure storage
        self.structures = {}  # name -> encoded structure vector
        self.structure_metadata = {}  # name -> metadata
        
        # Composition rules
        self.composition_rules = {}
        
        # Initialize advanced FIXME resolution features
        if enable_advanced_features:
            self.reduced_repr_engine = ReducedRepresentationEngine(
                vector_dim=vector_dim,
                reduction_threshold=0.7
            )
            
            self.cleanup_engine = CompositionalCleanupEngine(
                vector_dim=vector_dim,
                cleanup_threshold=0.3
            )
            
            self.analogy_engine = AnalogyEngine(
                vector_dim=vector_dim,
                similarity_threshold=0.3
            )
            
            self.capacity_monitor = CapacityMonitor(
                vector_dim=vector_dim,
                monitoring_enabled=True
            )
        else:
            self.reduced_repr_engine = None
            self.cleanup_engine = None  
            self.analogy_engine = None
            self.capacity_monitor = None
        
        # Initialize fundamental structure operations
        self._initialize_structure_primitives()
        self._initialize_composition_rules()
    
    def _initialize_structure_primitives(self):
        """Initialize primitive symbols for structure operations"""
        # Positional roles for sequences
        position_roles = ["FIRST", "SECOND", "THIRD", "LAST", "NEXT", "PREV"]
        for role in position_roles:
            self.vsa.create_random_symbol(role, "position")
        
        # Tree structure roles
        tree_roles = ["ROOT", "LEFT", "RIGHT", "PARENT", "CHILD", "SIBLING"]
        for role in tree_roles:
            self.vsa.create_random_symbol(role, "tree")
        
        # Graph structure roles
        graph_roles = ["NODE", "EDGE", "SOURCE", "TARGET", "WEIGHT"]
        for role in graph_roles:
            self.vsa.create_random_symbol(role, "graph")
        
        # Container roles
        container_roles = ["HEAD", "TAIL", "CONTENT", "SIZE", "INDEX", "KEY", "VALUE"]
        for role in container_roles:
            self.vsa.create_random_symbol(role, "container")
    
    def _initialize_composition_rules(self):
        """Initialize standard composition rules"""
        self.composition_rules[StructureType.SEQUENCE] = CompositionRule(
            rule_name="sequence_composition",
            structure_types=[StructureType.SEQUENCE],
            composition_function=self._compose_sequence
        )
        
        self.composition_rules[StructureType.TREE] = CompositionRule(
            rule_name="tree_composition", 
            structure_types=[StructureType.TREE],
            composition_function=self._compose_tree
        )
        
        self.composition_rules[StructureType.RECORD] = CompositionRule(
            rule_name="record_composition",
            structure_types=[StructureType.RECORD],
            composition_function=self._compose_record
        )
    
    def query_structure(self, structure_vector: np.ndarray, 
                       query_role: str, cleanup: bool = True) -> np.ndarray:
        """
        Query a structure for a specific role
        
        Args:
            structure_vector: Encoded structure to query
            query_role: Role to query for
            cleanup: Whether to apply cleanup to result
            
        Returns:
            Vector bound to the queried role
        """
        if query_role not in self.vsa.symbols:
            raise ValueError(f"Query role {query_role} not found in vocabulary")
        
        role_vector = self.vsa.symbols[query_role].vector
        
        # Unbind role from structure
        result = self.vsa.unbind(structure_vector, role_vector)
        
        # Apply advanced cleanup if available
        if cleanup and self.cleanup_engine:
            cleanup_result = self.cleanup_engine.cleanup_compositional_structure(result)
            result = cleanup_result.cleaned_vector
        elif cleanup:
            # Basic cleanup - find best match in vocabulary
            best_match, similarity = self.vsa.find_best_match(result)
            if best_match and similarity > 0.3:
                return self.vsa.symbols[best_match].vector
        
        return result
    
    def structure_similarity(self, struct1: np.ndarray, struct2: np.ndarray) -> float:
        """Compute similarity between two structures"""
        if self.analogy_engine:
            # Use advanced structural similarity
            structural_sim = self.analogy_engine.compute_structural_similarity(struct1, struct2)
            return structural_sim.overall_similarity
        else:
            # Basic similarity
            return self.vsa.similarity(struct1, struct2)
    
    def decode_sequence(self, sequence_vector: np.ndarray, max_length: int = 10) -> List[str]:
        """
        Attempt to decode a sequence structure
        
        Args:
            sequence_vector: Encoded sequence vector
            max_length: Maximum sequence length to try
            
        Returns:
            List of decoded element names
        """
        decoded_elements = []
        
        # Try to extract elements at each position
        for i in range(max_length):
            if i == 0:
                pos_role = "FIRST"
            elif i < 10:
                pos_role = f"POS_{i}"
            else:
                break
            
            if pos_role in self.vsa.symbols:
                element_vec = self.query_structure(sequence_vector, pos_role, cleanup=True)
                
                # Find best matching symbol
                best_match, similarity = self.vsa.find_best_match(element_vec)
                
                if best_match and similarity > 0.2:
                    decoded_elements.append(best_match)
                else:
                    break
        
        return decoded_elements
    
    def decode_record(self, record_vector: np.ndarray, 
                     field_names: Optional[List[str]] = None) -> Dict[str, str]:
        """
        Attempt to decode a record structure
        
        Args:
            record_vector: Encoded record vector
            field_names: Known field names to try (all symbols if None)
            
        Returns:
            Dictionary of decoded field values
        """
        decoded_fields = {}
        
        if field_names is None:
            # Try all symbols that might be field names
            field_names = [name for name, symbol in self.vsa.symbols.items() 
                          if symbol.symbol_type == "field"]
        
        for field_name in field_names:
            if field_name in self.vsa.symbols:
                field_vec = self.query_structure(record_vector, field_name, cleanup=True)
                
                # Find best matching value
                best_match, similarity = self.vsa.find_best_match(field_vec)
                
                if best_match and similarity > 0.3:
                    decoded_fields[field_name] = best_match
        
        return decoded_fields
    
    def _value_to_vector(self, value: Any) -> np.ndarray:
        """Convert a value to vector representation"""
        if isinstance(value, np.ndarray):
            return value
        elif isinstance(value, str) and value in self.vsa.symbols:
            return self.vsa.symbols[value].vector
        else:
            # Create new symbol for value
            value_str = str(value)
            if value_str not in self.vsa.symbols:
                self.vsa.create_random_symbol(value_str, "value")
            return self.vsa.symbols[value_str].vector
    
    def get_structure_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get information about a stored structure"""
        if name in self.structure_metadata:
            return self.structure_metadata[name].copy()
        return None
    
    def list_structures(self) -> List[str]:
        """List all stored structure names"""
        return list(self.structures.keys())
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the compositional system"""
        type_counts = {}
        for metadata in self.structure_metadata.values():
            struct_type = metadata["type"].value
            type_counts[struct_type] = type_counts.get(struct_type, 0) + 1
        
        base_stats = {
            "total_structures": len(self.structures),
            "structure_types": type_counts,
            "vector_dim": self.vector_dim,
            "vsa_symbols": len(self.vsa.symbols),
            "composition_rules": len(self.composition_rules),
            "vsa_stats": self.vsa.get_statistics()
        }
        
        # Add advanced feature statistics if available
        if self.capacity_monitor:
            base_stats["capacity_stats"] = self.capacity_monitor.get_capacity_statistics()
        
        if self.cleanup_engine:
            base_stats["cleanup_stats"] = self.cleanup_engine.get_cleanup_statistics()
        
        if self.analogy_engine:
            base_stats["analogy_stats"] = self.analogy_engine.get_analogy_statistics()
        
        if self.reduced_repr_engine:
            base_stats["reduced_repr_stats"] = self.reduced_repr_engine.get_vocabulary_stats()
        
        return base_stats


# Utility functions for common compositional patterns
def create_json_structure(json_data: Any, structure_primitives: StructurePrimitives, 
                         name: Optional[str] = None) -> np.ndarray:
    """
    Create HRR structure from JSON-like data
    
    Args:
        json_data: JSON-serializable data
        structure_primitives: StructurePrimitives instance
        name: Optional name for structure
        
    Returns:
        Encoded structure vector
    """
    if isinstance(json_data, dict):
        return structure_primitives.create_record(json_data, name)
    elif isinstance(json_data, list):
        return structure_primitives.create_sequence(json_data, name)
    else:
        # Simple value
        return structure_primitives._value_to_vector(json_data)


def create_nested_structure(spec: Dict[str, Any], 
                          structure_primitives: StructurePrimitives) -> np.ndarray:
    """
    Create nested structure from specification
    
    Args:
        spec: Structure specification
        structure_primitives: StructurePrimitives instance
        
    Returns:
        Encoded nested structure
    """
    struct_type = spec.get("type", "record")
    
    if struct_type == "sequence":
        elements = spec.get("elements", [])
        return structure_primitives.create_sequence(elements)
    elif struct_type == "tree":
        root = spec.get("root")
        children = spec.get("children", [])
        return structure_primitives.create_tree(root, children)
    elif struct_type == "record":
        fields = spec.get("fields", {})
        return structure_primitives.create_record(fields)
    elif struct_type == "graph":
        nodes = spec.get("nodes", [])
        edges = spec.get("edges", [])
        return structure_primitives.create_graph(nodes, edges)
    elif struct_type == "set":
        elements = spec.get("elements", [])
        return structure_primitives.create_set(elements)
    else:
        raise ValueError(f"Unknown structure type: {struct_type}")


def visualize_structure_similarity(structures: Dict[str, np.ndarray],
                                 structure_primitives: StructurePrimitives) -> np.ndarray:
    """
    Create similarity matrix for structures
    
    Args:
        structures: Dictionary of structure_name -> vector
        structure_primitives: StructurePrimitives instance
        
    Returns:
        Similarity matrix
    """
    structure_names = list(structures.keys())
    n_structures = len(structure_names)
    
    similarity_matrix = np.zeros((n_structures, n_structures))
    
    for i, name1 in enumerate(structure_names):
        for j, name2 in enumerate(structure_names):
            if i == j:
                similarity_matrix[i, j] = 1.0
            else:
                similarity = structure_primitives.structure_similarity(
                    structures[name1], structures[name2]
                )
                similarity_matrix[i, j] = similarity
    
    return similarity_matrix