"""
🌀 Main Holographic Memory System
==================================

This module implements the main HolographicMemory class, which provides a complete
implementation of Plate's Holographic Reduced Representations (HRR) system.

The HolographicMemory system uses circular convolution for binding operations
and distributed storage for associative memory functionality.

Based on:
- Plate (1995) "Holographic Reduced Representations"
- Vector Symbolic Architecture principles
- Circular convolution for binding operations

Author: Benedict Chen (benedict@benedictchen.com)
"""

import numpy as np
from typing import Dict, Any, List, Optional, Union, Tuple
import warnings

from .hrr_operations import HRROperations, HRRVector
from .associative_memory import AssociativeMemory, MemoryTrace
from .memory_management import MemoryManager


class HolographicMemory:
    """
    🌀 Main Holographic Memory System
    
    A complete implementation of Plate's Holographic Reduced Representations,
    featuring circular convolution binding, distributed storage, and associative
    cleanup mechanisms.
    
    Parameters
    ----------
    vector_dim : int, default=512
        Dimension of holographic vectors
    normalize : bool, default=True
        Whether to normalize vectors after operations
    noise_level : float, default=0.0
        Amount of noise to add for robustness testing
    cleanup_memory : bool, default=True
        Enable associative cleanup functionality
    capacity_threshold : int, optional
        Maximum number of items to store
    random_seed : int, optional
        Random seed for reproducibility
    
    Examples
    --------
    >>> hm = HolographicMemory(vector_dim=256)
    >>> # Bind role and filler
    >>> bound = hm.bind("AGENT", "John")
    >>> # Store in associative memory
    >>> hm.store("sentence1", bound)
    >>> # Retrieve and unbind
    >>> retrieved = hm.retrieve("sentence1")
    >>> agent = hm.unbind(retrieved, "AGENT")
    >>> cleaned = hm.cleanup(agent)
    """
    
    def __init__(self,
                 vector_dim: int = 512,
                 normalize: bool = True,
                 noise_level: float = 0.0,
                 cleanup_memory: bool = True,
                 capacity_threshold: Optional[int] = None,
                 random_seed: Optional[int] = None,
                 **kwargs):
        
        self.vector_dim = vector_dim
        self.normalize = normalize
        self.noise_level = noise_level
        self.cleanup_memory = cleanup_memory
        self.capacity_threshold = capacity_threshold
        
        # Set random seed if provided
        if random_seed is not None:
            np.random.seed(random_seed)
        
        # Initialize core components
        self.hrr_ops = HRROperations(
            vector_dim=vector_dim,
            normalize=normalize,
            noise_level=noise_level
        )
        
        # Initialize associative memory if enabled
        if cleanup_memory:
            self.associative_memory = AssociativeMemory(
                vector_dim=vector_dim,
                capacity_threshold=capacity_threshold
            )
        else:
            self.associative_memory = None
        
        # Initialize memory management
        self.memory_manager = MemoryManager(
            vector_dim=vector_dim,
            capacity_threshold=capacity_threshold
        )
        
        # Statistics tracking
        self.stats = {
            'total_bindings': 0,
            'total_unbindings': 0,
            'total_stores': 0,
            'total_retrievals': 0,
            'cleanup_operations': 0
        }
    
    def create_vector(self, name: str, vector_data: Optional[np.ndarray] = None) -> HRRVector:
        """
        Create a named holographic vector.
        
        Parameters
        ----------
        name : str
            Name identifier for the vector
        vector_data : np.ndarray, optional
            Specific vector data, otherwise random vector generated
            
        Returns
        -------
        HRRVector
            The created holographic vector
        """
        if vector_data is None:
            # Generate random vector
            vector_data = np.random.randn(self.vector_dim)
            if self.normalize:
                vector_data = vector_data / np.linalg.norm(vector_data)
        
        vector = HRRVector(data=vector_data, name=name)
        
        # Register with memory manager
        self.memory_manager.register_vector(name, vector)
        
        return vector
    
    def bind(self, 
             role: Union[str, np.ndarray, HRRVector], 
             filler: Union[str, np.ndarray, HRRVector]) -> HRRVector:
        """
        Bind two vectors using circular convolution.
        
        Implements Plate's holographic binding operation using circular
        convolution to create a compressed representation that preserves
        the relational structure between role and filler.
        
        Parameters
        ----------
        role : str, np.ndarray, or HRRVector
            Role vector (what to bind)
        filler : str, np.ndarray, or HRRVector
            Filler vector (what to bind it to)
            
        Returns
        -------
        HRRVector
            Bound holographic vector
        """
        # Convert inputs to HRRVector objects
        if isinstance(role, str):
            role = self.memory_manager.get_or_create_vector(role)
        elif isinstance(role, np.ndarray):
            role = HRRVector(data=role)
        
        if isinstance(filler, str):
            filler = self.memory_manager.get_or_create_vector(filler)
        elif isinstance(filler, np.ndarray):
            filler = HRRVector(data=filler)
        
        # Perform binding operation
        bound_vector = self.hrr_ops.bind(role, filler)
        
        self.stats['total_bindings'] += 1
        return bound_vector
    
    def unbind(self,
               bound_vector: Union[np.ndarray, HRRVector],
               role: Union[str, np.ndarray, HRRVector]) -> HRRVector:
        """
        Unbind a vector using circular correlation.
        
        Retrieves the filler from a bound representation using the role
        vector through circular correlation (inverse of convolution).
        
        Parameters
        ----------
        bound_vector : np.ndarray or HRRVector
            The bound vector to unbind from
        role : str, np.ndarray, or HRRVector
            The role vector used for unbinding
            
        Returns
        -------
        HRRVector
            The unbound filler vector (potentially noisy)
        """
        # Convert inputs
        if isinstance(bound_vector, np.ndarray):
            bound_vector = HRRVector(data=bound_vector)
        
        if isinstance(role, str):
            role = self.memory_manager.get_or_create_vector(role)
        elif isinstance(role, np.ndarray):
            role = HRRVector(data=role)
        
        # Perform unbinding operation
        unbound_vector = self.hrr_ops.unbind(bound_vector, role)
        
        self.stats['total_unbindings'] += 1
        return unbound_vector
    
    def compose(self, vectors: List[Union[HRRVector, np.ndarray]], 
                weights: Optional[List[float]] = None) -> HRRVector:
        """
        Compose multiple vectors using weighted superposition.
        
        Parameters
        ----------
        vectors : List[HRRVector or np.ndarray]
            List of vectors to compose
        weights : List[float], optional
            Weights for each vector (default: equal weights)
            
        Returns
        -------
        HRRVector
            Composed vector
        """
        if not vectors:
            raise ValueError("Cannot compose empty list of vectors")
        
        # Convert all to HRRVector
        hrr_vectors = []
        for v in vectors:
            if isinstance(v, np.ndarray):
                hrr_vectors.append(HRRVector(data=v))
            else:
                hrr_vectors.append(v)
        
        composed = self.hrr_ops.compose(hrr_vectors, weights)
        return composed
    
    def store(self, key: str, value: Union[HRRVector, np.ndarray]) -> bool:
        """
        Store a vector in associative memory.
        
        Parameters
        ----------
        key : str
            Key for retrieval
        value : HRRVector or np.ndarray
            Vector to store
            
        Returns
        -------
        bool
            True if stored successfully
        """
        if self.associative_memory is None:
            warnings.warn("Associative memory not enabled")
            return False
        
        # Convert value to HRRVector
        if isinstance(value, np.ndarray):
            value = HRRVector(data=value)
        
        success = self.associative_memory.store(key, value)
        if success:
            self.stats['total_stores'] += 1
        
        return success
    
    def retrieve(self, key: str) -> Optional[HRRVector]:
        """
        Retrieve a vector from associative memory.
        
        Parameters
        ----------
        key : str
            Key to retrieve
            
        Returns
        -------
        HRRVector or None
            Retrieved vector, or None if not found
        """
        if self.associative_memory is None:
            warnings.warn("Associative memory not enabled")
            return None
        
        result = self.associative_memory.retrieve(key)
        if result is not None:
            self.stats['total_retrievals'] += 1
        
        return result
    
    def cleanup(self, 
                noisy_vector: Union[HRRVector, np.ndarray],
                candidates: Optional[List[Union[str, HRRVector]]] = None) -> HRRVector:
        """
        Clean up a noisy vector using associative memory.
        
        Parameters
        ----------
        noisy_vector : HRRVector or np.ndarray
            Noisy vector to clean up
        candidates : List[str or HRRVector], optional
            Candidate vectors for cleanup
            
        Returns
        -------
        HRRVector
            Cleaned vector
        """
        if isinstance(noisy_vector, np.ndarray):
            noisy_vector = HRRVector(data=noisy_vector)
        
        if self.associative_memory is not None:
            cleaned = self.associative_memory.cleanup(noisy_vector, candidates)
        else:
            # Simple normalization cleanup if no associative memory
            cleaned = self.hrr_ops.normalize(noisy_vector)
        
        self.stats['cleanup_operations'] += 1
        return cleaned
    
    def similarity(self, 
                   vector1: Union[HRRVector, np.ndarray],
                   vector2: Union[HRRVector, np.ndarray]) -> float:
        """
        Compute cosine similarity between two vectors.
        
        Parameters
        ----------
        vector1, vector2 : HRRVector or np.ndarray
            Vectors to compare
            
        Returns
        -------
        float
            Cosine similarity (-1 to 1)
        """
        return self.hrr_ops.similarity(vector1, vector2)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get system statistics.
        
        Returns
        -------
        Dict[str, Any]
            Dictionary of statistics
        """
        stats = self.stats.copy()
        
        # Add memory manager stats
        stats.update(self.memory_manager.get_statistics())
        
        # Add associative memory stats if available
        if self.associative_memory is not None:
            stats.update(self.associative_memory.get_statistics())
        
        stats['vector_dim'] = self.vector_dim
        stats['normalize'] = self.normalize
        stats['noise_level'] = self.noise_level
        stats['cleanup_memory_enabled'] = self.cleanup_memory
        
        return stats
    
    def reset(self):
        """Reset the memory system, clearing all stored data."""
        if self.associative_memory is not None:
            self.associative_memory.clear()
        
        self.memory_manager.clear()
        
        # Reset statistics
        for key in self.stats:
            self.stats[key] = 0
    
    def save_state(self, filepath: str) -> bool:
        """
        Save the current state to file.
        
        Parameters
        ----------
        filepath : str
            Path to save file
            
        Returns
        -------
        bool
            True if saved successfully
        """
        try:
            state = {
                'vector_dim': self.vector_dim,
                'normalize': self.normalize,
                'noise_level': self.noise_level,
                'cleanup_memory': self.cleanup_memory,
                'capacity_threshold': self.capacity_threshold,
                'stats': self.stats,
                'memory_manager_state': self.memory_manager.get_state(),
                'associative_memory_state': (
                    self.associative_memory.get_state() 
                    if self.associative_memory else None
                )
            }
            
            np.save(filepath, state)
            return True
        except Exception as e:
            warnings.warn(f"Failed to save state: {e}")
            return False
    
    def load_state(self, filepath: str) -> bool:
        """
        Load state from file.
        
        Parameters
        ----------
        filepath : str
            Path to load file
            
        Returns
        -------
        bool
            True if loaded successfully
        """
        try:
            state = np.load(filepath, allow_pickle=True).item()
            
            # Restore basic parameters
            self.vector_dim = state['vector_dim']
            self.normalize = state['normalize']
            self.noise_level = state['noise_level']
            self.cleanup_memory = state['cleanup_memory']
            self.capacity_threshold = state.get('capacity_threshold')
            self.stats = state['stats']
            
            # Restore components
            self.memory_manager.load_state(state['memory_manager_state'])
            
            if state['associative_memory_state'] is not None and self.associative_memory:
                self.associative_memory.load_state(state['associative_memory_state'])
            
            return True
        except Exception as e:
            warnings.warn(f"Failed to load state: {e}")
            return False
    
    def __repr__(self) -> str:
        return (f"HolographicMemory(vector_dim={self.vector_dim}, "
                f"normalize={self.normalize}, "
                f"cleanup_memory={self.cleanup_memory})")