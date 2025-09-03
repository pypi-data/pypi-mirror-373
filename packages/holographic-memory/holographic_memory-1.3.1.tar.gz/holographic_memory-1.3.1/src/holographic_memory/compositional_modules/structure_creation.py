"""
Structure Creation Methods for Compositional HRR

This module contains the core structure creation methods (sequences, trees, records, etc.)
that were split from structure_primitives.py for 800-line compliance.
"""

import numpy as np
from typing import Dict, Any, List, Optional, Union, Tuple, Set
import logging

from .structure_types import StructureType, TreeSpec

logger = logging.getLogger(__name__)


class StructureCreationMixin:
    """Mixin class for structure creation methods"""
    
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
        
        # Apply advanced processing if available
        if self.cleanup_engine:
            cleanup_result = self.cleanup_engine.cleanup_compositional_structure(
                sequence_vector, StructureType.SEQUENCE
            )
            sequence_vector = cleanup_result.cleaned_vector
        
        # Register with capacity monitor
        if self.capacity_monitor:
            item_id = name or f"seq_{len(self.structures)}"
            self.capacity_monitor.register_stored_item(
                item_id, sequence_vector, StructureType.SEQUENCE
            )
        
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
    
    def create_tree(self, root_value: Any, children: Optional[List[TreeSpec]] = None, 
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
        
        # Apply advanced processing if available
        if self.cleanup_engine:
            cleanup_result = self.cleanup_engine.cleanup_compositional_structure(
                tree_vector, StructureType.TREE
            )
            tree_vector = cleanup_result.cleaned_vector
        
        # Register with capacity monitor
        if self.capacity_monitor:
            item_id = name or f"tree_{len(self.structures)}"
            self.capacity_monitor.register_stored_item(
                item_id, tree_vector, StructureType.TREE
            )
        
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
        
        # Apply advanced processing if available
        if self.cleanup_engine:
            cleanup_result = self.cleanup_engine.cleanup_compositional_structure(
                record_vector, StructureType.RECORD
            )
            record_vector = cleanup_result.cleaned_vector
        
        # Register with capacity monitor
        if self.capacity_monitor:
            item_id = name or f"record_{len(self.structures)}"
            self.capacity_monitor.register_stored_item(
                item_id, record_vector, StructureType.RECORD
            )
        
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
        
        # Apply advanced processing if available
        if self.cleanup_engine:
            cleanup_result = self.cleanup_engine.cleanup_compositional_structure(
                graph_vector, StructureType.GRAPH
            )
            graph_vector = cleanup_result.cleaned_vector
        
        # Register with capacity monitor
        if self.capacity_monitor:
            item_id = name or f"graph_{len(self.structures)}"
            self.capacity_monitor.register_stored_item(
                item_id, graph_vector, StructureType.GRAPH
            )
        
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
        
        # Apply advanced processing if available
        if self.cleanup_engine:
            cleanup_result = self.cleanup_engine.cleanup_compositional_structure(
                set_vector, StructureType.SET
            )
            set_vector = cleanup_result.cleaned_vector
        
        # Register with capacity monitor
        if self.capacity_monitor:
            item_id = name or f"set_{len(self.structures)}"
            self.capacity_monitor.register_stored_item(
                item_id, set_vector, StructureType.SET
            )
        
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
        
        # Apply advanced processing if available
        if self.cleanup_engine:
            cleanup_result = self.cleanup_engine.cleanup_compositional_structure(
                stack_vector, StructureType.STACK
            )
            stack_vector = cleanup_result.cleaned_vector
        
        # Register with capacity monitor
        if self.capacity_monitor:
            item_id = name or f"stack_{len(self.structures)}"
            self.capacity_monitor.register_stored_item(
                item_id, stack_vector, StructureType.STACK
            )
        
        # Store if named
        if name is not None:
            self.structures[name] = stack_vector
            self.structure_metadata[name] = {
                "type": StructureType.STACK,
                "size": len(elements),
                "top_element": elements[-1] if elements else None
            }
        
        return stack_vector
    
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