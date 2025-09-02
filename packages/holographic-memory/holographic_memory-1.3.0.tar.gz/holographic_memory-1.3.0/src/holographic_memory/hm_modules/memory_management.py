"""
Memory Management Module for Holographic Memory System

Handles storage, retrieval, and management of HRR memory items.
Provides basic key-value storage with holographic binding.

Author: Benedict Chen (benedict@benedictchen.com)
"""

import numpy as np
import time
import pickle
from typing import Dict, Optional, Any, Union
from .configuration import HRRConfig, HRRMemoryItem
from .vector_operations import VectorOperations


class MemoryManager:
    """Manages storage and retrieval of holographic memory items"""
    
    def __init__(self, config: HRRConfig, vector_ops: VectorOperations):
        """Initialize memory manager"""
        self.config = config
        self.vector_ops = vector_ops
        
        # Memory storage
        self.memory_items = {}  # name -> HRRMemoryItem
        self.composite_memories = {}  # name -> composite vector
        
        # Performance tracking
        self.association_count = 0
        self.memory_usage = 0
        
        print(f"✓ Memory Manager initialized: {config.vector_dim}D vectors")
    
    def create_vector(self, name: str, vector: Optional[np.ndarray] = None, 
                     metadata: Optional[Dict[str, Any]] = None) -> np.ndarray:
        """
        Create and store a new HRR vector
        
        Parameters:
        -----------
        name : str
            Name/identifier for the vector
        vector : np.ndarray, optional
            Pre-defined vector, or None to generate random
        metadata : dict, optional
            Additional metadata to store with vector
        
        Returns:
        --------
        vector : np.ndarray
            The created/stored vector
        """
        if vector is None:
            vector = self.vector_ops.generate_random_vector(name)
        else:
            # Validate provided vector
            self.vector_ops.validate_vector(vector, name)
            if self.config.normalize:
                vector = self.vector_ops.normalize_vector(vector)
        
        # Store in memory
        self.memory_items[name] = HRRMemoryItem(
            vector=vector.copy(),
            name=name,
            created_at=time.time(),
            metadata=metadata or {}
        )
        
        # Update memory usage
        self.memory_usage += vector.nbytes + len(name) * 8  # Rough estimate
        
        return vector
    
    def get_vector(self, name: str) -> np.ndarray:
        """
        Retrieve vector by name
        
        Parameters:
        -----------
        name : str
            Name of the vector to retrieve
        
        Returns:
        --------
        vector : np.ndarray
            The stored vector
        
        Raises:
        -------
        KeyError
            If vector not found
        """
        if name not in self.memory_items:
            raise KeyError(f"Vector '{name}' not found in memory")
        return self.memory_items[name].vector
    
    def has_vector(self, name: str) -> bool:
        """Check if a vector exists in memory"""
        return name in self.memory_items
    
    def delete_vector(self, name: str) -> bool:
        """
        Delete a vector from memory
        
        Parameters:
        -----------
        name : str
            Name of vector to delete
        
        Returns:
        --------
        success : bool
            True if vector was deleted, False if not found
        """
        if name in self.memory_items:
            # Update memory usage
            vector = self.memory_items[name].vector
            self.memory_usage -= vector.nbytes + len(name) * 8
            
            del self.memory_items[name]
            return True
        return False
    
    def store_association(self, key: str, value: Union[str, np.ndarray]) -> None:
        """
        Store a key-value association using holographic binding
        
        Parameters:
        -----------
        key : str
            Key for the association
        value : str or np.ndarray
            Value to associate with the key
        """
        # Create key vector if it doesn't exist
        if key not in self.memory_items:
            self.create_vector(key)
        
        # Handle value vector
        if isinstance(value, str):
            if value not in self.memory_items:
                self.create_vector(value)
            value_vec = self.memory_items[value].vector
        else:
            self.vector_ops.validate_vector(value, "value")
            value_vec = value
            
        # Bind key with value and store in composite memories
        key_vec = self.memory_items[key].vector
        bound = self.vector_ops.bind(key_vec, value_vec)
        memory_name = f"assoc_{key}"
        self.composite_memories[memory_name] = bound
        
        # Update association count
        self.association_count += 1
    
    def retrieve_association(self, key: str) -> Optional[np.ndarray]:
        """
        Retrieve value associated with key
        
        Parameters:
        -----------
        key : str
            Key to look up
        
        Returns:
        --------
        result : np.ndarray or None
            Retrieved vector, or None if not found
        """
        memory_name = f"assoc_{key}"
        if memory_name not in self.composite_memories:
            return None
            
        if key not in self.memory_items:
            return None
            
        # Unbind using key to retrieve value
        bound_memory = self.composite_memories[memory_name]
        key_vec = self.memory_items[key].vector
        retrieved = self.vector_ops.unbind(bound_memory, key_vec)
        return retrieved
    
    def list_vectors(self) -> list:
        """List all stored vector names"""
        return list(self.memory_items.keys())
    
    def list_associations(self) -> list:
        """List all stored associations"""
        return [name.replace("assoc_", "") for name in self.composite_memories.keys() 
                if name.startswith("assoc_")]
    
    def get_vector_info(self, name: str) -> Dict[str, Any]:
        """
        Get information about a stored vector
        
        Parameters:
        -----------
        name : str
            Name of the vector
        
        Returns:
        --------
        info : dict
            Vector information including metadata and statistics
        """
        if name not in self.memory_items:
            raise KeyError(f"Vector '{name}' not found")
        
        item = self.memory_items[name]
        stats = self.vector_ops.calculate_vector_statistics(item.vector)
        
        return {
            'name': item.name,
            'created_at': item.created_at,
            'metadata': item.metadata,
            'statistics': stats,
            'dimension': len(item.vector)
        }
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics"""
        return {
            'total_vectors': len(self.memory_items),
            'total_associations': len([k for k in self.composite_memories.keys() 
                                     if k.startswith("assoc_")]),
            'composite_memories': len(self.composite_memories),
            'vector_dimension': self.config.vector_dim,
            'memory_usage_bytes': self.memory_usage,
            'memory_usage_mb': self.memory_usage / (1024 * 1024),
            'association_count': self.association_count,
            'average_vector_norm': np.mean([np.linalg.norm(item.vector) 
                                          for item in self.memory_items.values()]) if self.memory_items else 0,
        }
    
    def clear_memory(self) -> None:
        """Clear all stored vectors and associations"""
        self.memory_items.clear()
        self.composite_memories.clear()
        self.association_count = 0
        self.memory_usage = 0
        print("✓ Memory cleared")
    
    def save_memory(self, filename: str) -> None:
        """
        Save memory state to file
        
        Parameters:
        -----------
        filename : str
            Path to save file
        """
        save_data = {
            'config': self.config,
            'memory_items': self.memory_items,
            'composite_memories': self.composite_memories,
            'association_count': self.association_count,
            'memory_usage': self.memory_usage
        }
        
        with open(filename, 'wb') as f:
            pickle.dump(save_data, f)
            
        print(f"✓ Memory saved to {filename}")
    
    def load_memory(self, filename: str) -> None:
        """
        Load memory state from file
        
        Parameters:
        -----------
        filename : str
            Path to load file
        """
        with open(filename, 'rb') as f:
            save_data = pickle.load(f)
        
        # Validate compatibility
        if save_data['config'].vector_dim != self.config.vector_dim:
            raise ValueError(f"Incompatible vector dimensions: {save_data['config'].vector_dim} != {self.config.vector_dim}")
            
        self.memory_items = save_data['memory_items']
        self.composite_memories = save_data['composite_memories']
        self.association_count = save_data.get('association_count', 0)
        self.memory_usage = save_data.get('memory_usage', 0)
        
        print(f"✓ Memory loaded from {filename}")
        print(f"  Loaded {len(self.memory_items)} vectors and {len(self.composite_memories)} composite memories")
    
    def batch_create_vectors(self, names: list, vectors: Optional[list] = None) -> Dict[str, np.ndarray]:
        """
        Create multiple vectors in batch for efficiency
        
        Parameters:
        -----------
        names : list
            List of vector names
        vectors : list, optional
            List of pre-defined vectors, or None for random generation
        
        Returns:
        --------
        created : dict
            Dictionary mapping names to created vectors
        """
        if vectors is not None and len(vectors) != len(names):
            raise ValueError("vectors list must match names list length")
        
        created = {}
        for i, name in enumerate(names):
            if vectors is not None:
                vector = vectors[i]
            else:
                vector = None
            
            created[name] = self.create_vector(name, vector)
        
        return created
    
    def find_similar_vectors(self, query_vector: np.ndarray, 
                           top_k: int = 5, threshold: float = 0.1) -> list:
        """
        Find vectors similar to query vector
        
        Parameters:
        -----------
        query_vector : np.ndarray
            Vector to find similarities for
        top_k : int
            Number of top results to return
        threshold : float
            Minimum similarity threshold
        
        Returns:
        --------
        results : list
            List of (name, similarity) tuples sorted by similarity
        """
        if not self.memory_items:
            return []
        
        similarities = []
        for name, item in self.memory_items.items():
            sim = self.vector_ops.similarity(query_vector, item.vector)
            if sim >= threshold:
                similarities.append((name, sim))
        
        # Sort by similarity (descending) and return top k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]