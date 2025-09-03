"""
Composite Memory Operations Module for Holographic Memory System

Handles complex memory structures including hierarchies, sequences, and
structured representations using HRR binding and superposition.

Author: Benedict Chen (benedict@benedictchen.com)
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional, Union
from .configuration import HRRConfig
from .vector_operations import VectorOperations
from .memory_management import MemoryManager


class CompositeOperations:
    """Handles complex memory structures and operations"""
    
    def __init__(self, config: HRRConfig, vector_ops: VectorOperations, memory_manager: MemoryManager):
        """Initialize composite operations"""
        self.config = config
        self.vector_ops = vector_ops
        self.memory_manager = memory_manager
        
    def create_hierarchy(self, structure: Dict, name: str) -> np.ndarray:
        """
        Create hierarchical structure using nested binding and superposition
        
        Parameters:
        -----------
        structure : dict
            Hierarchical structure, e.g.:
            {
                'animal': ['dog', 'cat'],
                'color': ['red', 'blue']  
            }
        name : str
            Name to store the hierarchy under
        
        Returns:
        --------
        hierarchy : np.ndarray
            Vector representing the hierarchical structure
        """
        components = []
        
        for role, fillers in structure.items():
            if isinstance(fillers, list):
                # Create superposition of fillers
                filler_vectors = []
                for filler in fillers:
                    if isinstance(filler, str) and not self.memory_manager.has_vector(filler):
                        self.memory_manager.create_vector(filler)
                    
                    if isinstance(filler, str):
                        filler_vectors.append(self.memory_manager.get_vector(filler))
                    else:
                        filler_vectors.append(filler)
                        
                filler_superposition = self.vector_ops.superpose(filler_vectors)
            else:
                # Single filler
                if isinstance(fillers, str) and not self.memory_manager.has_vector(fillers):
                    self.memory_manager.create_vector(fillers)
                
                if isinstance(fillers, str):
                    filler_superposition = self.memory_manager.get_vector(fillers)
                else:
                    filler_superposition = fillers
            
            # Create role vector if needed
            if not self.memory_manager.has_vector(role):
                self.memory_manager.create_vector(role)
                
            # Bind role with filler superposition
            role_vec = self.memory_manager.get_vector(role)
            role_filler = self.vector_ops.bind(role_vec, filler_superposition)
            components.append(role_filler)
        
        # Create final hierarchy as superposition of all role-filler pairs
        hierarchy = self.vector_ops.superpose(components, normalize=True)
        
        # Store composite memory
        self.memory_manager.composite_memories[name] = hierarchy
        
        return hierarchy
    
    def create_sequence(self, items: List[str], sequence_name: str, 
                       encoding: str = None) -> np.ndarray:
        """
        Create sequence representation using different encoding methods
        
        Parameters:
        -----------
        items : List[str]
            Items in the sequence
        sequence_name : str
            Name to store the sequence under
        encoding : str, optional
            Encoding method: 'positional', 'chaining', 'ngram'
        
        Returns:
        --------
        sequence : np.ndarray
            Vector representing the sequence
        """
        if encoding is None:
            encoding = self.config.sequence_encoding
            
        # Ensure all items exist as vectors
        for item in items:
            if not self.memory_manager.has_vector(item):
                self.memory_manager.create_vector(item)
        
        if encoding == 'positional':
            # Bind each item with position
            sequence_components = []
            for i, item in enumerate(items):
                pos_name = f"pos_{i}"
                if not self.memory_manager.has_vector(pos_name):
                    self.memory_manager.create_vector(pos_name)
                
                item_vec = self.memory_manager.get_vector(item)
                pos_vec = self.memory_manager.get_vector(pos_name)
                item_at_pos = self.vector_ops.bind(item_vec, pos_vec)
                sequence_components.append(item_at_pos)
            
            sequence = self.vector_ops.superpose(sequence_components)
            
        elif encoding == 'chaining':
            # Create chain: item1 ⊗ (item2 ⊗ (item3 ⊗ ...))
            if len(items) < 2:
                sequence = self.memory_manager.get_vector(items[0]) if items else np.zeros(self.config.vector_dim)
            else:
                sequence = self.memory_manager.get_vector(items[-1])
                for item in reversed(items[:-1]):
                    item_vec = self.memory_manager.get_vector(item)
                    sequence = self.vector_ops.bind(item_vec, sequence)
        
        elif encoding == 'ngram':
            # N-gram encoding (simplified 2-gram)
            sequence_components = []
            for i in range(len(items) - 1):
                item1_vec = self.memory_manager.get_vector(items[i])
                item2_vec = self.memory_manager.get_vector(items[i + 1])
                bigram = self.vector_ops.bind(item1_vec, item2_vec)
                sequence_components.append(bigram)
            
            if sequence_components:
                sequence = self.vector_ops.superpose(sequence_components)
            else:
                sequence = np.zeros(self.config.vector_dim)
                    
        else:
            raise ValueError(f"Unknown sequence encoding: {encoding}")
        
        # Store sequence
        self.memory_manager.composite_memories[sequence_name] = sequence
        
        return sequence
    
    def query_memory(self, memory_name: str, cue_role: str) -> Tuple[np.ndarray, float]:
        """
        Query composite memory with a role to retrieve filler
        
        Parameters:
        -----------
        memory_name : str
            Name of the composite memory to query
        cue_role : str
            Role to use as cue for retrieval
        
        Returns:
        --------
        retrieved : np.ndarray
            Retrieved vector
        confidence : float
            Confidence in the retrieval (similarity to best match)
        """
        if memory_name not in self.memory_manager.composite_memories:
            raise KeyError(f"Composite memory '{memory_name}' not found")
        
        if not self.memory_manager.has_vector(cue_role):
            raise KeyError(f"Cue role '{cue_role}' not found in memory")
            
        memory = self.memory_manager.composite_memories[memory_name]
        cue_vec = self.memory_manager.get_vector(cue_role)
        retrieved = self.vector_ops.unbind(memory, cue_vec)
        
        # Calculate confidence as best similarity to known vectors
        best_similarity = 0.0
        for item in self.memory_manager.memory_items.values():
            sim = self.vector_ops.similarity(retrieved, item.vector)
            if sim > best_similarity:
                best_similarity = sim
        
        return retrieved, float(best_similarity)
    
    def query_sequence_position(self, sequence_name: str, position: int) -> Tuple[np.ndarray, float]:
        """
        Query sequence at specific position
        
        Parameters:
        -----------
        sequence_name : str
            Name of the sequence
        position : int
            Position to query (0-indexed)
        
        Returns:
        --------
        retrieved : np.ndarray
            Retrieved vector at position
        confidence : float
            Confidence in the retrieval
        """
        if sequence_name not in self.memory_manager.composite_memories:
            raise KeyError(f"Sequence '{sequence_name}' not found")
            
        sequence = self.memory_manager.composite_memories[sequence_name]
        pos_name = f"pos_{position}"
        
        if not self.memory_manager.has_vector(pos_name):
            return np.zeros(self.config.vector_dim), 0.0
        
        pos_vec = self.memory_manager.get_vector(pos_name)
        retrieved = self.vector_ops.unbind(sequence, pos_vec)
        
        # Calculate confidence
        best_similarity = 0.0
        for item in self.memory_manager.memory_items.values():
            sim = self.vector_ops.similarity(retrieved, item.vector)
            if sim > best_similarity:
                best_similarity = sim
        
        return retrieved, float(best_similarity)
    
    def create_composite_memory(self, bindings: List[Tuple[str, str]], memory_name: str) -> np.ndarray:
        """
        Create composite memory from role-filler bindings
        
        Parameters:
        -----------
        bindings : List[Tuple[str, str]]
            List of (role, filler) pairs
        memory_name : str
            Name to store the composite memory under
        
        Returns:
        --------
        composite : np.ndarray
            Composite memory vector
        """
        bound_vectors = []
        for role, filler in bindings:
            if not self.memory_manager.has_vector(role):
                self.memory_manager.create_vector(role)
            if not self.memory_manager.has_vector(filler):
                self.memory_manager.create_vector(filler)
            
            role_vec = self.memory_manager.get_vector(role)
            filler_vec = self.memory_manager.get_vector(filler)
            bound = self.vector_ops.bind(role_vec, filler_vec)
            bound_vectors.append(bound)
        
        composite = self.vector_ops.superpose(bound_vectors)
        self.memory_manager.composite_memories[memory_name] = composite
        return composite
    
    def create_frame(self, attributes: Dict[str, Union[str, List[str]]], frame_name: str) -> np.ndarray:
        """
        Create frame representation (like a semantic frame or concept)
        
        Parameters:
        -----------
        attributes : Dict[str, Union[str, List[str]]]
            Frame attributes and their values
        frame_name : str
            Name for the frame
        
        Returns:
        --------
        frame : np.ndarray
            Frame representation vector
        """
        return self.create_hierarchy(attributes, frame_name)
    
    def blend_memories(self, memory_names: List[str], weights: Optional[List[float]] = None,
                      blend_name: str = None) -> np.ndarray:
        """
        Create weighted blend of multiple memories
        
        Parameters:
        -----------
        memory_names : List[str]
            Names of memories to blend
        weights : List[float], optional
            Weights for blending (defaults to equal weights)
        blend_name : str, optional
            Name to store the blend under
        
        Returns:
        --------
        blend : np.ndarray
            Blended memory vector
        """
        if weights is None:
            weights = [1.0] * len(memory_names)
        
        if len(weights) != len(memory_names):
            raise ValueError("Weights must match number of memories")
        
        # Collect memory vectors
        memory_vectors = []
        for name in memory_names:
            if name in self.memory_manager.composite_memories:
                memory_vectors.append(self.memory_manager.composite_memories[name])
            elif self.memory_manager.has_vector(name):
                memory_vectors.append(self.memory_manager.get_vector(name))
            else:
                raise KeyError(f"Memory '{name}' not found")
        
        # Weight and sum
        weighted_vectors = []
        total_weight = sum(weights)
        for vec, weight in zip(memory_vectors, weights):
            weighted_vectors.append(vec * (weight / total_weight))
        
        blend = self.vector_ops.superpose(weighted_vectors, normalize=True)
        
        if blend_name:
            self.memory_manager.composite_memories[blend_name] = blend
        
        return blend
    
    def analyze_memory_composition(self, memory_name: str, 
                                  candidate_roles: List[str]) -> Dict[str, float]:
        """
        Analyze what roles/concepts are present in a composite memory
        
        Parameters:
        -----------
        memory_name : str
            Name of memory to analyze
        candidate_roles : List[str]
            Potential roles to check for
        
        Returns:
        --------
        composition : Dict[str, float]
            Role names mapped to their similarity scores
        """
        if memory_name not in self.memory_manager.composite_memories:
            raise KeyError(f"Memory '{memory_name}' not found")
        
        memory = self.memory_manager.composite_memories[memory_name]
        composition = {}
        
        for role in candidate_roles:
            if self.memory_manager.has_vector(role):
                role_vec = self.memory_manager.get_vector(role)
                # Unbind to see what's associated with this role
                unbound = self.vector_ops.unbind(memory, role_vec)
                
                # Find best match among stored vectors
                best_sim = 0.0
                for item in self.memory_manager.memory_items.values():
                    sim = self.vector_ops.similarity(unbound, item.vector)
                    if sim > best_sim:
                        best_sim = sim
                
                composition[role] = float(best_sim)
        
        return composition
    
    def create_analogical_mapping(self, source_structure: Dict, target_items: List[str],
                                 mapping_name: str) -> np.ndarray:
        """
        Create analogical mapping between source structure and target items
        
        Parameters:
        -----------
        source_structure : Dict
            Source structure for analogy
        target_items : List[str]
            Target items to map to
        mapping_name : str
            Name for the mapping
        
        Returns:
        --------
        mapping : np.ndarray
            Analogical mapping vector
        """
        # Create source hierarchy
        source_hierarchy = self.create_hierarchy(source_structure, f"{mapping_name}_source")
        
        # Create target representation
        for item in target_items:
            if not self.memory_manager.has_vector(item):
                self.memory_manager.create_vector(item)
        
        target_vectors = [self.memory_manager.get_vector(item) for item in target_items]
        target_representation = self.vector_ops.superpose(target_vectors)
        
        # Create analogical mapping
        mapping = self.vector_ops.bind(source_hierarchy, target_representation)
        self.memory_manager.composite_memories[mapping_name] = mapping
        
        return mapping