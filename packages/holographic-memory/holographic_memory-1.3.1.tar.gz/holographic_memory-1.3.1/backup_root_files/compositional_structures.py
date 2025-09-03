"""
Compositional Structures using Holographic Reduced Representations
Based on: Plate (1995) "Holographic Reduced Representations" 
         and Kanerva (2009) "Hyperdimensional Computing"

Implements compositional data structures and hierarchical representations
using circular convolution binding for complex symbolic structures.
"""

import numpy as np
from typing import Dict, Any, List, Optional, Union, Tuple, Set
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import json

from .src.holographic_memory import HolographicMemory, HolographicMemoryCore
try:
    from .src.holographic_memory import HRRMemoryItem
except ImportError:
    HRRMemoryItem = None
from .vector_symbolic import VectorSymbolicArchitecture, VSASymbol, VSAOperation

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
    value: Union[str, np.ndarray, VSASymbol]
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
    
class CompositionalHRR:
    """
    Compositional Holographic Reduced Representations
    
    Implements hierarchical and compositional data structures using HRR binding
    operations. Supports sequences, trees, graphs, and other complex structures.
    """
    
    def __init__(self,
                 vector_dim: int = 512,
                 vsa: Optional[VectorSymbolicArchitecture] = None,
                 normalize_vectors: bool = True,
                 random_seed: Optional[int] = None):
        """
        Initialize Compositional HRR system
        
        Args:
            vector_dim: Dimensionality of vectors
            vsa: Vector Symbolic Architecture (created if None)
            normalize_vectors: Whether to normalize vectors
            random_seed: Random seed for reproducibility
        """
        self.vector_dim = vector_dim
        self.normalize_vectors = normalize_vectors
        
        if random_seed is not None:
            np.random.seed(random_seed)
        
        # Initialize VSA if not provided
        if vsa is None:
            self.vsa = VectorSymbolicArchitecture(
                vector_dim=vector_dim,
                normalize_vectors=normalize_vectors,
                random_seed=random_seed
            )
        else:
            self.vsa = vsa
        
        # Initialize HRR memory for underlying operations
        self.hrr_memory = HolographicMemory(
            vector_size=vector_dim,
            normalize_vectors=normalize_vectors
        )
        
        # Structure storage
        self.structures = {}  # name -> encoded structure vector
        self.structure_metadata = {}  # name -> metadata
        
        # Composition rules
        self.composition_rules = {}
        
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
    
    def create_sequence(self, elements: List[Any], name: Optional[str] = None) -> np.ndarray:
        """
        Create a sequence structure using positional binding
        
        Args:
            elements: List of elements to encode in sequence
            name: Optional name for the sequence
            
        Returns:
            Encoded sequence vector
        """
        if not elements:
            return np.zeros(self.vector_dim)
        
        # Convert elements to vectors
        element_vectors = []
        for element in elements:
            if isinstance(element, str) and element in self.vsa.symbols:
                element_vectors.append(self.vsa.symbols[element].vector)
            elif isinstance(element, np.ndarray):
                element_vectors.append(element)
            else:
                # Create new symbol for element
                symbol_name = str(element)
                if symbol_name not in self.vsa.symbols:
                    self.vsa.create_random_symbol(symbol_name, "element")
                element_vectors.append(self.vsa.symbols[symbol_name].vector)
        
        # Compose sequence using positional binding
        sequence_vector = self._compose_sequence(element_vectors)
        
        # Store if named
        if name is not None:
            self.structures[name] = sequence_vector
            self.structure_metadata[name] = {
                "type": StructureType.SEQUENCE,
                "length": len(elements),
                "elements": elements
            }
        
        return sequence_vector
    
    def _compose_sequence(self, element_vectors: List[np.ndarray]) -> np.ndarray:
        """Compose sequence using positional role binding"""
        if not element_vectors:
            return np.zeros(self.vector_dim)
        
        sequence_parts = []
        
        # Bind each element with its positional role
        for i, element_vec in enumerate(element_vectors):
            if i < 10:  # Use specific position roles for first 10 elements
                if i == 0:
                    position_role = self.vsa.symbols["FIRST"].vector
                elif i == len(element_vectors) - 1:
                    position_role = self.vsa.symbols["LAST"].vector
                else:
                    # Create numbered position role
                    pos_name = f"POS_{i}"
                    if pos_name not in self.vsa.symbols:
                        self.vsa.create_random_symbol(pos_name, "position")
                    position_role = self.vsa.symbols[pos_name].vector
            else:
                # For longer sequences, use modular positions
                pos_name = f"POS_{i % 10}"
                if pos_name not in self.vsa.symbols:
                    self.vsa.create_random_symbol(pos_name, "position")
                position_role = self.vsa.symbols[pos_name].vector
            
            # Bind element with position
            bound_element = self.vsa.bind(position_role, element_vec)
            sequence_parts.append(bound_element)
        
        # Superpose all bound elements
        sequence_vector = self.vsa.superpose(*sequence_parts)
        
        # Add sequence length information
        length_name = f"LEN_{len(element_vectors)}"
        if length_name not in self.vsa.symbols:
            self.vsa.create_random_symbol(length_name, "length")
        
        length_info = self.vsa.bind("SIZE", length_name)
        sequence_vector = self.vsa.superpose(sequence_vector, length_info)
        
        return sequence_vector
    
    def create_tree(self, root_value: Any, children: Optional[List['TreeSpec']] = None, 
                   name: Optional[str] = None) -> np.ndarray:
        """
        Create a tree structure
        
        Args:
            root_value: Value at root node
            children: List of child subtrees
            name: Optional name for the tree
            
        Returns:
            Encoded tree vector
        """
        # Convert root value to vector
        root_vec = self._value_to_vector(root_value)
        
        # Create tree structure
        tree_parts = []
        
        # Bind root value with ROOT role
        root_binding = self.vsa.bind("ROOT", root_vec)
        tree_parts.append(root_binding)
        
        # Process children
        if children:
            for i, child_spec in enumerate(children):
                child_vector = self._process_tree_child(child_spec, i)
                tree_parts.append(child_vector)
        
        # Superpose all parts
        tree_vector = self.vsa.superpose(*tree_parts)
        
        # Store if named
        if name is not None:
            self.structures[name] = tree_vector
            self.structure_metadata[name] = {
                "type": StructureType.TREE,
                "root": root_value,
                "n_children": len(children) if children else 0
            }
        
        return tree_vector
    
    def _compose_tree(self, tree_data: Dict[str, Any]) -> np.ndarray:
        """Compose tree structure from specification"""
        # This is called by composition rules
        root = tree_data.get("root")
        children = tree_data.get("children", [])
        
        return self.create_tree(root, children)
    
    def _process_tree_child(self, child_spec: Any, child_index: int) -> np.ndarray:
        """Process a child node in tree structure"""
        if isinstance(child_spec, dict) and "root" in child_spec:
            # Recursive tree structure
            child_tree = self.create_tree(child_spec["root"], child_spec.get("children"))
        else:
            # Simple value
            child_tree = self._value_to_vector(child_spec)
        
        # Bind with child role
        if child_index == 0:
            child_role = "LEFT"
        elif child_index == 1:
            child_role = "RIGHT"
        else:
            child_role = f"CHILD_{child_index}"
            if child_role not in self.vsa.symbols:
                self.vsa.create_random_symbol(child_role, "tree")
        
        return self.vsa.bind(child_role, child_tree)
    
    def create_record(self, fields: Dict[str, Any], name: Optional[str] = None) -> np.ndarray:
        """
        Create a record (struct-like) structure
        
        Args:
            fields: Dictionary of field_name -> value
            name: Optional name for the record
            
        Returns:
            Encoded record vector
        """
        if not fields:
            return np.zeros(self.vector_dim)
        
        record_parts = []
        
        for field_name, field_value in fields.items():
            # Create role for field name
            if field_name not in self.vsa.symbols:
                self.vsa.create_random_symbol(field_name, "field")
            
            field_role = self.vsa.symbols[field_name].vector
            field_vector = self._value_to_vector(field_value)
            
            # Bind field name with field value
            field_binding = self.vsa.bind(field_role, field_vector)
            record_parts.append(field_binding)
        
        # Superpose all fields
        record_vector = self.vsa.superpose(*record_parts)
        
        # Store if named
        if name is not None:
            self.structures[name] = record_vector
            self.structure_metadata[name] = {
                "type": StructureType.RECORD,
                "fields": list(fields.keys()),
                "n_fields": len(fields)
            }
        
        return record_vector
    
    def _compose_record(self, fields: Dict[str, Any]) -> np.ndarray:
        """Compose record structure"""
        return self.create_record(fields)
    
    def create_graph(self, nodes: List[Any], edges: List[Tuple[int, int]], 
                    edge_weights: Optional[List[float]] = None,
                    name: Optional[str] = None) -> np.ndarray:
        """
        Create a graph structure
        
        Args:
            nodes: List of node values
            edges: List of (source_idx, target_idx) tuples
            edge_weights: Optional edge weights
            name: Optional name for the graph
            
        Returns:
            Encoded graph vector
        """
        graph_parts = []
        
        # Encode nodes
        node_vectors = []
        for i, node_value in enumerate(nodes):
            node_vec = self._value_to_vector(node_value)
            node_vectors.append(node_vec)
            
            # Bind node with index
            node_role = f"NODE_{i}"
            if node_role not in self.vsa.symbols:
                self.vsa.create_random_symbol(node_role, "graph")
            
            node_binding = self.vsa.bind(node_role, node_vec)
            graph_parts.append(node_binding)
        
        # Encode edges
        for i, (src_idx, tgt_idx) in enumerate(edges):
            if src_idx >= len(nodes) or tgt_idx >= len(nodes):
                continue
            
            # Create edge representation
            edge_parts = []
            
            # Source node
            src_binding = self.vsa.bind("SOURCE", node_vectors[src_idx])
            edge_parts.append(src_binding)
            
            # Target node
            tgt_binding = self.vsa.bind("TARGET", node_vectors[tgt_idx])
            edge_parts.append(tgt_binding)
            
            # Edge weight if provided
            if edge_weights and i < len(edge_weights):
                weight_name = f"WEIGHT_{edge_weights[i]:.2f}"
                if weight_name not in self.vsa.symbols:
                    self.vsa.create_random_symbol(weight_name, "weight")
                
                weight_binding = self.vsa.bind("WEIGHT", weight_name)
                edge_parts.append(weight_binding)
            
            # Compose edge
            edge_vector = self.vsa.superpose(*edge_parts)
            
            # Bind edge with edge role
            edge_role = f"EDGE_{i}"
            if edge_role not in self.vsa.symbols:
                self.vsa.create_random_symbol(edge_role, "graph")
            
            edge_binding = self.vsa.bind(edge_role, edge_vector)
            graph_parts.append(edge_binding)
        
        # Superpose all graph components
        graph_vector = self.vsa.superpose(*graph_parts)
        
        # Store if named
        if name is not None:
            self.structures[name] = graph_vector
            self.structure_metadata[name] = {
                "type": StructureType.GRAPH,
                "n_nodes": len(nodes),
                "n_edges": len(edges),
                "nodes": nodes,
                "edges": edges
            }
        
        return graph_vector
    
    def create_set(self, elements: List[Any], name: Optional[str] = None) -> np.ndarray:
        """
        Create a set structure (unordered collection)
        
        Args:
            elements: List of elements (duplicates ignored)
            name: Optional name for the set
            
        Returns:
            Encoded set vector
        """
        # Remove duplicates
        unique_elements = list(set(str(e) for e in elements))
        
        if not unique_elements:
            return np.zeros(self.vector_dim)
        
        # Convert to vectors and superpose (sets are unordered)
        element_vectors = []
        for element in unique_elements:
            element_vec = self._value_to_vector(element)
            element_vectors.append(element_vec)
        
        # Simple superposition for unordered collection
        set_vector = self.vsa.superpose(*element_vectors)
        
        # Add cardinality information
        card_name = f"CARD_{len(unique_elements)}"
        if card_name not in self.vsa.symbols:
            self.vsa.create_random_symbol(card_name, "cardinality")
        
        card_binding = self.vsa.bind("SIZE", card_name)
        set_vector = self.vsa.superpose(set_vector, card_binding)
        
        # Store if named
        if name is not None:
            self.structures[name] = set_vector
            self.structure_metadata[name] = {
                "type": StructureType.SET,
                "cardinality": len(unique_elements),
                "elements": unique_elements
            }
        
        return set_vector
    
    def create_stack(self, elements: List[Any], name: Optional[str] = None) -> np.ndarray:
        """
        Create a stack structure (LIFO)
        
        Args:
            elements: List of elements (top of stack is last element)
            name: Optional name for the stack
            
        Returns:
            Encoded stack vector
        """
        if not elements:
            return np.zeros(self.vector_dim)
        
        stack_parts = []
        
        # Bind elements with stack positions (top has highest weight)
        for i, element in enumerate(elements):
            element_vec = self._value_to_vector(element)
            
            # Stack level (higher number = closer to top)
            level = len(elements) - 1 - i
            level_name = f"LEVEL_{level}"
            if level_name not in self.vsa.symbols:
                self.vsa.create_random_symbol(level_name, "stack")
            
            # Special role for top element
            if i == len(elements) - 1:
                element_binding = self.vsa.bind("HEAD", element_vec)
            else:
                element_binding = self.vsa.bind(level_name, element_vec)
            
            stack_parts.append(element_binding)
        
        # Superpose all levels
        stack_vector = self.vsa.superpose(*stack_parts)
        
        # Add size information
        size_name = f"SIZE_{len(elements)}"
        if size_name not in self.vsa.symbols:
            self.vsa.create_random_symbol(size_name, "size")
        
        size_binding = self.vsa.bind("SIZE", size_name)
        stack_vector = self.vsa.superpose(stack_vector, size_binding)
        
        # Store if named
        if name is not None:
            self.structures[name] = stack_vector
            self.structure_metadata[name] = {
                "type": StructureType.STACK,
                "size": len(elements),
                "top_element": elements[-1] if elements else None
            }
        
        return stack_vector
    
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
        
        # Cleanup if requested
        if cleanup:
            # Find best match in vocabulary
            best_match, similarity = self.vsa.find_best_match(result)
            if best_match and similarity > 0.3:
                return self.vsa.symbols[best_match].vector
        
        return result
    
    def structure_similarity(self, struct1: np.ndarray, struct2: np.ndarray) -> float:
        """Compute similarity between two structures"""
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
        
        return {
            "total_structures": len(self.structures),
            "structure_types": type_counts,
            "vector_dim": self.vector_dim,
            "vsa_symbols": len(self.vsa.symbols),
            "composition_rules": len(self.composition_rules),
            "vsa_stats": self.vsa.get_statistics()
        }

# Utility functions for common compositional patterns
def create_json_structure(json_data: Any, compositional_hrr: CompositionalHRR, 
                         name: Optional[str] = None) -> np.ndarray:
    """
    Create HRR structure from JSON-like data
    
    Args:
        json_data: JSON-serializable data
        compositional_hrr: CompositionalHRR instance
        name: Optional name for structure
        
    Returns:
        Encoded structure vector
    """
    if isinstance(json_data, dict):
        return compositional_hrr.create_record(json_data, name)
    elif isinstance(json_data, list):
        return compositional_hrr.create_sequence(json_data, name)
    else:
        # Simple value
        return compositional_hrr._value_to_vector(json_data)

def create_nested_structure(spec: Dict[str, Any], 
                          compositional_hrr: CompositionalHRR) -> np.ndarray:
    """
    Create nested structure from specification
    
    Args:
        spec: Structure specification
        compositional_hrr: CompositionalHRR instance
        
    Returns:
        Encoded nested structure
    """
    struct_type = spec.get("type", "record")
    
    if struct_type == "sequence":
        elements = spec.get("elements", [])
        return compositional_hrr.create_sequence(elements)
    elif struct_type == "tree":
        root = spec.get("root")
        children = spec.get("children", [])
        return compositional_hrr.create_tree(root, children)
    elif struct_type == "record":
        fields = spec.get("fields", {})
        return compositional_hrr.create_record(fields)
    elif struct_type == "graph":
        nodes = spec.get("nodes", [])
        edges = spec.get("edges", [])
        return compositional_hrr.create_graph(nodes, edges)
    elif struct_type == "set":
        elements = spec.get("elements", [])
        return compositional_hrr.create_set(elements)
    else:
        raise ValueError(f"Unknown structure type: {struct_type}")

def visualize_structure_similarity(structures: Dict[str, np.ndarray],
                                 compositional_hrr: CompositionalHRR) -> np.ndarray:
    """
    Create similarity matrix for structures
    
    Args:
        structures: Dictionary of structure_name -> vector
        compositional_hrr: CompositionalHRR instance
        
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
                similarity = compositional_hrr.structure_similarity(
                    structures[name1], structures[name2]
                )
                similarity_matrix[i, j] = similarity
    
    return similarity_matrix