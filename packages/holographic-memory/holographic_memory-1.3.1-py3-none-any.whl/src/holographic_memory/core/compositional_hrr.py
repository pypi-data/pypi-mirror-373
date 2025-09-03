"""
🏗️ Compositional HRR - Structured Representation Operations
===========================================================

This module implements compositional operations for Holographic Reduced
Representations, enabling the construction and manipulation of structured
symbolic representations using HRR operations.

Based on Plate (1995) and extensions for compositional semantics.

Author: Benedict Chen (benedict@benedictchen.com)
"""

import numpy as np
from typing import Dict, List, Optional, Union, Any, Tuple
import warnings

from .hrr_operations import HRROperations, HRRVector


class CompositionalHRR:
    """
    🏗️ Compositional HRR System
    
    Enables construction and manipulation of structured representations
    using holographic binding operations. Supports nested structures,
    sequences, and complex compositional patterns.
    
    Parameters
    ----------
    vector_dim : int, default=512
        Dimension of HRR vectors
    normalize : bool, default=True
        Whether to normalize vectors after operations
    role_vectors : Dict[str, HRRVector], optional
        Pre-defined role vectors
    """
    
    def __init__(self,
                 vector_dim: int = 512,
                 normalize: bool = True,
                 role_vectors: Optional[Dict[str, HRRVector]] = None):
        
        self.vector_dim = vector_dim
        self.normalize = normalize
        
        # Initialize HRR operations
        self.hrr_ops = HRROperations(
            vector_dim=vector_dim,
            normalize=normalize
        )
        
        # Storage for vectors and structures
        self.role_vectors: Dict[str, HRRVector] = role_vectors or {}
        self.filler_vectors: Dict[str, HRRVector] = {}
        self.structures: Dict[str, HRRVector] = {}
        
        # Statistics
        self.stats = {
            'structures_created': 0,
            'bindings_performed': 0,
            'compositions_created': 0,
            'queries_executed': 0
        }
    
    def create_role_vector(self, role_name: str, 
                          vector_data: Optional[np.ndarray] = None) -> HRRVector:
        """
        Create or retrieve a role vector.
        
        Parameters
        ----------
        role_name : str
            Name of the role
        vector_data : np.ndarray, optional
            Specific vector data, otherwise random generated
            
        Returns
        -------
        HRRVector
            The role vector
        """
        if role_name in self.role_vectors:
            return self.role_vectors[role_name]
        
        if vector_data is not None:
            role_vector = HRRVector(data=vector_data, name=role_name)
        else:
            # Create random role vector
            role_vector = self.hrr_ops.create_random_vector(name=role_name)
        
        self.role_vectors[role_name] = role_vector
        return role_vector
    
    def create_filler_vector(self, filler_name: str,
                           vector_data: Optional[np.ndarray] = None) -> HRRVector:
        """
        Create or retrieve a filler vector.
        
        Parameters
        ----------
        filler_name : str
            Name of the filler
        vector_data : np.ndarray, optional
            Specific vector data, otherwise random generated
            
        Returns
        -------
        HRRVector
            The filler vector
        """
        if filler_name in self.filler_vectors:
            return self.filler_vectors[filler_name]
        
        if vector_data is not None:
            filler_vector = HRRVector(data=vector_data, name=filler_name)
        else:
            # Create random filler vector
            filler_vector = self.hrr_ops.create_random_vector(name=filler_name)
        
        self.filler_vectors[filler_name] = filler_vector
        return filler_vector
    
    def bind_role_filler(self, role_name: str, filler_name: str) -> HRRVector:
        """
        Bind a role to a filler.
        
        Parameters
        ----------
        role_name : str
            Name of the role
        filler_name : str
            Name of the filler
            
        Returns
        -------
        HRRVector
            Bound vector representing the role-filler pair
        """
        role_vector = self.create_role_vector(role_name)
        filler_vector = self.create_filler_vector(filler_name)
        
        bound_vector = self.hrr_ops.bind(role_vector, filler_vector)
        
        self.stats['bindings_performed'] += 1
        return bound_vector
    
    def create_structure(self, structure_name: str,
                        bindings: List[Tuple[str, str]]) -> HRRVector:
        """
        Create a structured representation from role-filler bindings.
        
        Parameters
        ----------
        structure_name : str
            Name for the structure
        bindings : List[Tuple[str, str]]
            List of (role, filler) pairs
            
        Returns
        -------
        HRRVector
            Composed structure vector
            
        Example
        -------
        >>> comp = CompositionalHRR()
        >>> sentence = comp.create_structure("sentence1", [
        ...     ("AGENT", "John"),
        ...     ("ACTION", "loves"),
        ...     ("PATIENT", "Mary")
        ... ])
        """
        if not bindings:
            raise ValueError("Cannot create structure with no bindings")
        
        # Create individual bindings
        bound_vectors = []
        for role, filler in bindings:
            bound_vector = self.bind_role_filler(role, filler)
            bound_vectors.append(bound_vector)
        
        # Compose all bindings
        if len(bound_vectors) == 1:
            structure_vector = bound_vectors[0]
        else:
            structure_vector = self.hrr_ops.compose(bound_vectors)
        
        # Update name and metadata
        structure_vector.name = structure_name
        structure_vector.metadata.update({
            'structure_type': 'composed',
            'bindings': bindings,
            'num_bindings': len(bindings)
        })
        
        # Store structure
        self.structures[structure_name] = structure_vector
        
        self.stats['structures_created'] += 1
        self.stats['compositions_created'] += 1
        
        return structure_vector
    
    def query_structure(self, structure: Union[str, HRRVector], 
                       role_name: str) -> HRRVector:
        """
        Query a structure for a specific role.
        
        Parameters
        ----------
        structure : str or HRRVector
            Structure to query
        role_name : str
            Role to query for
            
        Returns
        -------
        HRRVector
            Retrieved filler vector (potentially noisy)
        """
        # Get structure vector
        if isinstance(structure, str):
            if structure not in self.structures:
                raise ValueError(f"Structure '{structure}' not found")
            structure_vector = self.structures[structure]
        else:
            structure_vector = structure
        
        # Get role vector
        if role_name not in self.role_vectors:
            warnings.warn(f"Role '{role_name}' not found, creating new role vector")
            role_vector = self.create_role_vector(role_name)
        else:
            role_vector = self.role_vectors[role_name]
        
        # Unbind to get filler
        filler_vector = self.hrr_ops.unbind(structure_vector, role_vector)
        
        self.stats['queries_executed'] += 1
        return filler_vector
    
    def create_sequence(self, sequence_name: str,
                       items: List[Union[str, HRRVector]],
                       position_roles: Optional[List[str]] = None) -> HRRVector:
        """
        Create a sequence representation.
        
        Parameters
        ----------
        sequence_name : str
            Name for the sequence
        items : List[str or HRRVector]
            Items in the sequence
        position_roles : List[str], optional
            Role names for positions (default: "POS0", "POS1", ...)
            
        Returns
        -------
        HRRVector
            Sequence representation
        """
        if not items:
            raise ValueError("Cannot create empty sequence")
        
        if position_roles is None:
            position_roles = [f"POS{i}" for i in range(len(items))]
        elif len(position_roles) != len(items):
            raise ValueError("Number of position roles must match number of items")
        
        # Create bindings for each position
        bound_vectors = []
        for pos_role, item in zip(position_roles, items):
            # Get or create position role vector
            pos_vector = self.create_role_vector(pos_role)
            
            # Get item vector
            if isinstance(item, str):
                item_vector = self.create_filler_vector(item)
            else:
                item_vector = item
            
            # Bind position to item
            bound_vector = self.hrr_ops.bind(pos_vector, item_vector)
            bound_vectors.append(bound_vector)
        
        # Compose sequence
        sequence_vector = self.hrr_ops.compose(bound_vectors)
        sequence_vector.name = sequence_name
        sequence_vector.metadata.update({
            'structure_type': 'sequence',
            'length': len(items),
            'position_roles': position_roles
        })
        
        # Store sequence
        self.structures[sequence_name] = sequence_vector
        
        self.stats['structures_created'] += 1
        return sequence_vector
    
    def create_tree(self, tree_name: str, tree_structure: Dict[str, Any]) -> HRRVector:
        """
        Create a hierarchical tree representation.
        
        Parameters
        ----------
        tree_name : str
            Name for the tree
        tree_structure : Dict[str, Any]
            Nested dictionary representing tree structure
            
        Returns
        -------
        HRRVector
            Tree representation
            
        Example
        -------
        >>> tree = comp.create_tree("parse_tree", {
        ...     "ROOT": {
        ...         "SUBJECT": "John",
        ...         "PREDICATE": {
        ...             "VERB": "loves",
        ...             "OBJECT": "Mary"
        ...         }
        ...     }
        ... })
        """
        def _create_subtree(node_data: Any, depth: int = 0) -> HRRVector:
            if isinstance(node_data, dict):
                # Create bindings for all key-value pairs
                bindings = []
                for key, value in node_data.items():
                    key_vector = self.create_role_vector(f"{key}_D{depth}")
                    value_vector = _create_subtree(value, depth + 1)
                    binding = self.hrr_ops.bind(key_vector, value_vector)
                    bindings.append(binding)
                
                # Compose all bindings at this level
                return self.hrr_ops.compose(bindings)
            
            elif isinstance(node_data, list):
                # Handle list as sequence
                item_vectors = []
                for i, item in enumerate(node_data):
                    pos_role = self.create_role_vector(f"ITEM{i}_D{depth}")
                    item_vector = _create_subtree(item, depth + 1)
                    binding = self.hrr_ops.bind(pos_role, item_vector)
                    item_vectors.append(binding)
                
                return self.hrr_ops.compose(item_vectors)
            
            else:
                # Leaf node - create or get filler vector
                return self.create_filler_vector(str(node_data))
        
        tree_vector = _create_subtree(tree_structure)
        tree_vector.name = tree_name
        tree_vector.metadata.update({
            'structure_type': 'tree',
            'tree_structure': tree_structure
        })
        
        # Store tree
        self.structures[tree_name] = tree_vector
        
        self.stats['structures_created'] += 1
        return tree_vector
    
    def similarity_search(self, query_vector: Union[HRRVector, np.ndarray],
                         search_space: Optional[List[str]] = None,
                         top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Search for similar structures.
        
        Parameters
        ----------
        query_vector : HRRVector or np.ndarray
            Query vector
        search_space : List[str], optional
            Names of structures to search (default: all)
        top_k : int, default=5
            Number of top matches to return
            
        Returns
        -------
        List[Tuple[str, float]]
            List of (structure_name, similarity) pairs
        """
        if search_space is None:
            search_space = list(self.structures.keys())
        
        similarities = []
        for struct_name in search_space:
            if struct_name in self.structures:
                struct_vector = self.structures[struct_name]
                similarity = self.hrr_ops.similarity(query_vector, struct_vector)
                similarities.append((struct_name, similarity))
        
        # Sort by similarity and return top k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def get_structure(self, name: str) -> Optional[HRRVector]:
        """Get a stored structure by name."""
        return self.structures.get(name)
    
    def list_structures(self) -> List[str]:
        """List names of all stored structures."""
        return list(self.structures.keys())
    
    def remove_structure(self, name: str) -> bool:
        """Remove a structure by name."""
        if name in self.structures:
            del self.structures[name]
            return True
        return False
    
    def clear_all(self):
        """Clear all stored vectors and structures."""
        self.role_vectors.clear()
        self.filler_vectors.clear()
        self.structures.clear()
        
        # Reset statistics
        for key in self.stats:
            self.stats[key] = 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics."""
        stats = self.stats.copy()
        stats.update({
            'num_role_vectors': len(self.role_vectors),
            'num_filler_vectors': len(self.filler_vectors),
            'num_structures': len(self.structures),
            'vector_dim': self.vector_dim,
            'normalize': self.normalize
        })
        
        # Add HRR operations statistics
        stats.update(self.hrr_ops.get_statistics())
        
        return stats