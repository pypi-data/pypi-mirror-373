"""
💾 Holographic Memory - Memory Data Structures Module
===================================================

Split from associative_memory.py (918 lines → modular architecture)
Part of holographic_memory package 800-line compliance initiative.

Author: Benedict Chen (benedict@benedictchen.com)
Based on: Plate (1995) "Holographic Reduced Representations"
         Hinton (1981) "Implementing Semantic Networks in Parallel Hardware"

🎯 MODULE PURPOSE:
=================
Core data structures for associative memory and cleanup operations.
Defines memory traces, cleanup results, and abstract memory interfaces.

🔬 RESEARCH FOUNDATION:
======================
Implements foundational structures based on Plate (1995) and Hinton (1981):
- MemoryTrace: Distributed memory storage following HRR principles
- CleanupResult: Comprehensive cleanup operation results with confidence metrics
- AssociativeMemory: Abstract interface for different memory architectures

This module contains the foundational data structures, split from the
918-line monolith for clean architectural separation.
"""

import numpy as np
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field
from abc import ABC, abstractmethod


@dataclass
class MemoryTrace:
    """
    🧠 Memory Trace for Holographic Associative Memory
    
    Represents a stored association between key and value vectors in the
    holographic memory system, following Plate (1995) HRR principles.
    
    Attributes:
    -----------
    key_vector : np.ndarray
        The key vector used for retrieval (query pattern)
    value_vector : np.ndarray  
        The value vector to be retrieved (stored pattern)
    trace_strength : float, default=1.0
        Storage strength/weight for this memory trace
    access_count : int, default=0
        Number of times this trace has been accessed
    creation_time : int, default=0
        Timestamp when this trace was created
    metadata : Optional[Dict[str, Any]], default=None
        Additional metadata about this memory trace
        
    Research Context:
    ----------------
    Based on Plate (1995) Section III: "The associative memory model stores
    a set of vector pairs (key, value) and when presented with a noisy version
    of a key vector, returns the corresponding value vector."
    """
    key_vector: np.ndarray
    value_vector: np.ndarray  
    trace_strength: float = 1.0
    access_count: int = 0
    creation_time: int = 0
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Initialize metadata dict if not provided"""
        if self.metadata is None:
            self.metadata = {}
            
    def update_access(self):
        """Update access statistics for memory trace"""
        self.access_count += 1
        
    def get_age(self, current_time: int) -> int:
        """Get age of memory trace"""
        return current_time - self.creation_time


@dataclass
class CleanupResult:
    """
    🔧 Cleanup Operation Result
    
    Comprehensive result from associative memory cleanup operations,
    including confidence metrics and convergence information.
    
    Attributes:
    -----------
    cleaned_vector : np.ndarray
        The cleaned/recalled vector after associative cleanup
    confidence : float
        Confidence score of the cleanup operation (0.0 to 1.0)
    original_similarity : float
        Similarity between original query and cleaned result
    iterations : int
        Number of iterations used in iterative cleanup
    converged : bool
        Whether the cleanup process converged successfully
    candidate_matches : List[Tuple[str, float]], default=[]
        List of (pattern_name, similarity_score) for candidate matches
        
    Research Context:
    ----------------
    Based on Plate (1995) Section IV: "Cleanup operations are essential for
    practical HRR systems to recover clean patterns from noisy queries."
    """
    cleaned_vector: np.ndarray
    confidence: float
    original_similarity: float
    iterations: int
    converged: bool
    candidate_matches: List[Tuple[str, float]] = field(default_factory=list)
    
    def is_high_confidence(self, threshold: float = 0.8) -> bool:
        """Check if cleanup result has high confidence"""
        return self.confidence >= threshold
        
    def get_best_match(self) -> Optional[Tuple[str, float]]:
        """Get the best candidate match if available"""
        if self.candidate_matches:
            return max(self.candidate_matches, key=lambda x: x[1])
        return None


class AssociativeMemory(ABC):
    """
    🏛️ Abstract Base Class for Associative Memory Systems
    
    Defines the interface for different associative memory implementations,
    including auto-associative and hetero-associative memory variants.
    
    Research Context:
    ----------------
    Based on Hinton (1981) and Plate (1995) associative memory principles:
    - Auto-associative: key and value are the same (pattern completion)
    - Hetero-associative: key and value are different (pattern association)
    - Cleanup memory: specialized for noise reduction and pattern retrieval
    """
    
    @abstractmethod
    def store(self, key: np.ndarray, value: np.ndarray, strength: float = 1.0) -> None:
        """
        Store a key-value association in memory.
        
        Parameters:
        -----------
        key : np.ndarray
            Key vector for retrieval
        value : np.ndarray
            Value vector to be stored
        strength : float, default=1.0
            Storage strength/weight for this association
        """
        pass
    
    @abstractmethod  
    def recall(self, key: np.ndarray, cleanup: bool = True) -> CleanupResult:
        """
        Recall value associated with key.
        
        Parameters:
        -----------
        key : np.ndarray
            Query key vector
        cleanup : bool, default=True
            Whether to apply cleanup operations
            
        Returns:
        --------
        CleanupResult
            Comprehensive recall result with confidence metrics
        """
        pass
    
    @abstractmethod
    def cleanup(self, noisy_vector: np.ndarray, max_iterations: int = 10) -> CleanupResult:
        """
        Clean up a noisy vector using associative memory.
        
        Parameters:
        -----------
        noisy_vector : np.ndarray
            Noisy input vector to be cleaned
        max_iterations : int, default=10
            Maximum iterations for iterative cleanup
            
        Returns:
        --------
        CleanupResult
            Cleanup result with convergence information
        """
        pass
    
    @abstractmethod
    def similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Compute similarity between two vectors.
        
        Parameters:
        -----------
        vec1, vec2 : np.ndarray
            Vectors to compare
            
        Returns:
        --------
        float
            Similarity score (typically cosine similarity)
        """
        pass
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get statistics about memory usage and performance.
        
        Returns:
        --------
        Dict[str, Any]
            Dictionary containing memory statistics
        """
        return {
            'memory_type': self.__class__.__name__,
            'implementation': 'abstract_base'
        }


# Export the memory structures
__all__ = [
    'MemoryTrace',
    'CleanupResult', 
    'AssociativeMemory'
]


if __name__ == "__main__":
    print("💾 Holographic Memory - Memory Data Structures Module")
    print("=" * 59)
    print("📊 MODULE CONTENTS:")
    print("  • MemoryTrace - Distributed memory storage following HRR principles")
    print("  • CleanupResult - Comprehensive cleanup operation results")
    print("  • AssociativeMemory - Abstract interface for memory architectures")
    print("")
    print("✅ Memory data structures module loaded successfully!")
    print("🔬 Essential structures for Plate (1995) holographic memory systems!")