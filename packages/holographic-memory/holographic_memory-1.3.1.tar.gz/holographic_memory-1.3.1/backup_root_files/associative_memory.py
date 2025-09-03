"""
Associative Memory and Cleanup Networks for Holographic Memory
Based on: Plate (1995) "Holographic Reduced Representations" 
         and Hinton (1981) "Implementing Semantic Networks in Parallel Hardware"

Implements associative cleanup mechanisms for noisy holographic memory retrieval,
including auto-associative and hetero-associative memory networks.
"""

import numpy as np
from typing import Dict, Any, List, Optional, Union, Tuple, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import logging

from .src.holographic_memory import HolographicMemory, HolographicMemoryCore
try:
    from .src.holographic_memory import HRRMemoryItem
except ImportError:
    # Fallback for src layout differences
    HRRMemoryItem = None

@dataclass
class MemoryTrace:
    """Represents a memory trace in associative memory"""
    key_vector: np.ndarray
    value_vector: np.ndarray
    trace_strength: float = 1.0
    access_count: int = 0
    creation_time: int = 0
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class CleanupResult:
    """Result from associative cleanup operation"""
    cleaned_vector: np.ndarray
    confidence: float
    original_similarity: float
    iterations: int
    converged: bool
    candidate_matches: List[Tuple[str, float]] = field(default_factory=list)

class AssociativeMemory(ABC):
    """Abstract base class for associative memory implementations"""
    
    @abstractmethod
    def store(self, key: np.ndarray, value: np.ndarray, strength: float = 1.0):
        """
        📋 Store Key-Value Association - Holographic Memory Encoding!
        
        Stores an associative memory trace using holographic encoding,
        following Plate's Holographic Reduced Representations theory.
        
        Args:
            key: Key vector for retrieval [vector_size]
            value: Value vector to associate [vector_size] 
            strength: Association strength (0.0-1.0, default=1.0)
            
        📚 **Reference**: Plate, T. (1995). "Holographic reduced representations"
        
        🧠 **Holographic Principles**:
        - Distributed storage across entire memory
        - Interference patterns encode associations
        - Content-addressable retrieval
        - Graceful degradation with noise
        
        🎆 **Storage Process**:
        ```python
        # Encode: key ⊗ value (convolution binding)
        trace = circular_convolution(key, value) * strength
        memory += trace  # Superposition storage
        ```
        
        ✨ **Applications**: Episodic memory, semantic networks, symbol grounding
        """
        pass
    
    @abstractmethod
    def retrieve(self, key: np.ndarray, cleanup: bool = True) -> CleanupResult:
        """Retrieve value associated with key"""
        pass
    
    @abstractmethod
    def cleanup(self, noisy_vector: np.ndarray, max_iterations: int = 10) -> CleanupResult:
        """Clean up a noisy vector"""
        pass

class AssociativeCleanup(AssociativeMemory):
    """
    Associative cleanup network for holographic memory
    
    Implements both auto-associative (pattern completion) and hetero-associative
    (pattern transformation) cleanup using correlation-based storage and retrieval.
    """
    
    def __init__(self,
                 vector_dim: int = 512,
                 memory_capacity: int = 1000,
                 cleanup_threshold: float = 0.3,
                 convergence_threshold: float = 0.001,
                 learning_rate: float = 0.1,
                 decay_rate: float = 0.001,
                 noise_tolerance: float = 0.2):
        """
        Initialize Associative Cleanup Network
        
        Args:
            vector_dim: Dimensionality of vectors
            memory_capacity: Maximum number of stored associations
            cleanup_threshold: Minimum similarity for cleanup
            convergence_threshold: Threshold for convergence detection
            learning_rate: Learning rate for weight updates
            decay_rate: Decay rate for memory traces
            noise_tolerance: Tolerance for noisy input
        """
        self.vector_dim = vector_dim
        self.memory_capacity = memory_capacity
        self.cleanup_threshold = cleanup_threshold
        self.convergence_threshold = convergence_threshold
        self.learning_rate = learning_rate
        self.decay_rate = decay_rate
        self.noise_tolerance = noise_tolerance
        
        # Memory traces
        self.memory_traces = {}  # key_hash -> MemoryTrace
        self.trace_counter = 0
        
        # Auto-associative weight matrix (for pattern completion)
        self.auto_weights = np.zeros((vector_dim, vector_dim))
        
        # Hetero-associative weight matrix (for pattern transformation)  
        self.hetero_weights = np.zeros((vector_dim, vector_dim))
        
        # Statistics
        self.storage_count = 0
        self.retrieval_count = 0
        self.cleanup_count = 0
        self.successful_cleanups = 0
        
    def store(self, key: np.ndarray, value: np.ndarray, strength: float = 1.0):
        """
        Store a key-value association in memory
        
        Args:
            key: Key vector
            value: Value vector  
            strength: Storage strength
        """
        if len(key) != self.vector_dim or len(value) != self.vector_dim:
            raise ValueError(f"Vectors must have dimension {self.vector_dim}")
        
        # Create memory trace
        key_hash = self._hash_vector(key)
        
        trace = MemoryTrace(
            key_vector=key.copy(),
            value_vector=value.copy(), 
            trace_strength=strength,
            creation_time=self.trace_counter,
            metadata={"storage_method": "correlation"}
        )
        
        # Store in memory
        if len(self.memory_traces) >= self.memory_capacity:
            self._forget_weakest_trace()
        
        self.memory_traces[key_hash] = trace
        self.trace_counter += 1
        
        # Update weight matrices using outer product rule
        self._update_auto_associative_weights(key, strength)
        self._update_hetero_associative_weights(key, value, strength)
        
        self.storage_count += 1
    
    def retrieve(self, key: np.ndarray, cleanup: bool = True) -> CleanupResult:
        """
        Retrieve value associated with key
        
        Args:
            key: Query key vector
            cleanup: Whether to apply cleanup
            
        Returns:
            CleanupResult with retrieved/cleaned vector
        """
        self.retrieval_count += 1
        
        # Direct lookup first
        key_hash = self._hash_vector(key)
        if key_hash in self.memory_traces:
            trace = self.memory_traces[key_hash]
            trace.access_count += 1
            
            if cleanup:
                return self.cleanup(trace.value_vector)
            else:
                return CleanupResult(
                    cleaned_vector=trace.value_vector,
                    confidence=1.0,
                    original_similarity=1.0,
                    iterations=0,
                    converged=True
                )
        
        # Associative retrieval using weight matrix
        retrieved = np.dot(self.hetero_weights, key)
        
        if cleanup:
            return self.cleanup(retrieved)
        else:
            # Find best matching stored value
            best_match, similarity = self._find_best_match(retrieved)
            
            return CleanupResult(
                cleaned_vector=retrieved,
                confidence=similarity,
                original_similarity=similarity,
                iterations=0,
                converged=False,
                candidate_matches=[(best_match, similarity)] if best_match else []
            )
    
    def cleanup(self, noisy_vector: np.ndarray, max_iterations: int = 10) -> CleanupResult:
        """
        Clean up a noisy vector using iterative auto-associative recall
        
        Args:
            noisy_vector: Noisy input vector
            max_iterations: Maximum cleanup iterations
            
        Returns:
            CleanupResult with cleaned vector and statistics
        """
        self.cleanup_count += 1
        
        if len(noisy_vector) != self.vector_dim:
            raise ValueError(f"Vector must have dimension {self.vector_dim}")
        
        # Initialize
        current_vector = noisy_vector.copy()
        original_similarity = 0.0
        iterations = 0
        converged = False
        candidate_matches = []
        
        # Find initial best match
        initial_match, original_similarity = self._find_best_match(current_vector)
        if initial_match:
            candidate_matches.append((initial_match, original_similarity))
        
        # Iterative cleanup using auto-associative recall
        for iteration in range(max_iterations):
            # Auto-associative recall
            recalled_vector = np.dot(self.auto_weights, current_vector)
            
            # Normalize to unit length
            if np.linalg.norm(recalled_vector) > 0:
                recalled_vector = recalled_vector / np.linalg.norm(recalled_vector)
            
            # Check for convergence
            change = np.linalg.norm(recalled_vector - current_vector)
            if change < self.convergence_threshold:
                converged = True
                break
            
            current_vector = recalled_vector
            iterations = iteration + 1
            
            # Find current best match
            match_name, similarity = self._find_best_match(current_vector)
            if match_name and similarity > self.cleanup_threshold:
                candidate_matches.append((match_name, similarity))
        
        # Determine final result
        final_match, final_similarity = self._find_best_match(current_vector)
        
        # Success if we found a good match
        success = final_similarity > self.cleanup_threshold
        if success:
            self.successful_cleanups += 1
        
        # If we found a very good match, use the exact stored vector
        if final_match and final_similarity > 0.8:
            key_hash = self._hash_vector_by_name(final_match)
            if key_hash and key_hash in self.memory_traces:
                current_vector = self.memory_traces[key_hash].value_vector.copy()
        
        return CleanupResult(
            cleaned_vector=current_vector,
            confidence=final_similarity,
            original_similarity=original_similarity,
            iterations=iterations,
            converged=converged,
            candidate_matches=candidate_matches
        )
    
    def _update_auto_associative_weights(self, vector: np.ndarray, strength: float):
        """Update auto-associative weight matrix using Hebbian learning"""
        # Hebbian update: W += α * v * v^T
        outer_product = np.outer(vector, vector)
        self.auto_weights += self.learning_rate * strength * outer_product
        
        # Apply decay to prevent unlimited growth
        self.auto_weights *= (1 - self.decay_rate)
    
    def _update_hetero_associative_weights(self, key: np.ndarray, value: np.ndarray, strength: float):
        """Update hetero-associative weight matrix"""
        # Hetero-associative update: W += α * value * key^T  
        outer_product = np.outer(value, key)
        self.hetero_weights += self.learning_rate * strength * outer_product
        
        # Apply decay
        self.hetero_weights *= (1 - self.decay_rate)
    
    def _find_best_match(self, query_vector: np.ndarray) -> Tuple[Optional[str], float]:
        """Find the best matching stored vector"""
        best_match = None
        best_similarity = -1.0
        
        for key_hash, trace in self.memory_traces.items():
            # Try both key and value vectors
            key_similarity = self._cosine_similarity(query_vector, trace.key_vector)
            value_similarity = self._cosine_similarity(query_vector, trace.value_vector)
            
            max_similarity = max(key_similarity, value_similarity)
            
            if max_similarity > best_similarity:
                best_similarity = max_similarity
                best_match = f"trace_{trace.creation_time}"
        
        return best_match, best_similarity
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _hash_vector(self, vector: np.ndarray) -> str:
        """Create a hash for a vector (for indexing)"""
        # Simple hash based on first few components
        return f"vec_{hash(tuple(vector[:min(10, len(vector))].round(6)))}"
    
    def _hash_vector_by_name(self, name: str) -> Optional[str]:
        """Find vector hash by trace name"""
        for key_hash, trace in self.memory_traces.items():
            if f"trace_{trace.creation_time}" == name:
                return key_hash
        return None
    
    def _forget_weakest_trace(self):
        """Remove the weakest memory trace to make room"""
        if not self.memory_traces:
            return
        
        # Find trace with lowest strength * access_count
        weakest_key = None
        weakest_score = float('inf')
        
        for key_hash, trace in self.memory_traces.items():
            # Score combines strength and usage
            score = trace.trace_strength * (1 + trace.access_count)
            if score < weakest_score:
                weakest_score = score
                weakest_key = key_hash
        
        if weakest_key:
            del self.memory_traces[weakest_key]
    
    def add_prototypes(self, prototypes: Dict[str, np.ndarray]):
        """
        Add prototype vectors for cleanup
        
        Args:
            prototypes: Dictionary mapping names to prototype vectors
        """
        for name, vector in prototypes.items():
            # Store as auto-associative pair (vector -> vector)
            self.store(vector, vector, strength=2.0)  # Higher strength for prototypes
    
    def pattern_completion(self, partial_vector: np.ndarray, 
                          mask: Optional[np.ndarray] = None) -> CleanupResult:
        """
        Complete a partial pattern using auto-associative recall
        
        Args:
            partial_vector: Incomplete vector (some dimensions may be unknown)
            mask: Binary mask indicating known dimensions (1=known, 0=unknown)
            
        Returns:
            CleanupResult with completed pattern
        """
        if mask is not None and len(mask) != self.vector_dim:
            raise ValueError("Mask must have same dimension as vectors")
        
        # If no mask, treat as standard cleanup
        if mask is None:
            return self.cleanup(partial_vector)
        
        # Initialize with partial vector
        current_vector = partial_vector.copy()
        
        # Iterative completion
        iterations = 0
        converged = False
        
        for iteration in range(10):  # Max iterations for completion
            # Auto-associative recall
            recalled = np.dot(self.auto_weights, current_vector)
            
            # Apply mask: keep known dimensions, update unknown ones
            if mask is not None:
                current_vector = mask * partial_vector + (1 - mask) * recalled
            
            # Normalize
            if np.linalg.norm(current_vector) > 0:
                current_vector = current_vector / np.linalg.norm(current_vector)
            
            iterations = iteration + 1
            
            # Check convergence (only on unknown dimensions)
            unknown_change = np.linalg.norm((1 - mask) * (recalled - current_vector))
            if unknown_change < self.convergence_threshold:
                converged = True
                break
        
        # Find best match for completed pattern
        best_match, similarity = self._find_best_match(current_vector)
        
        return CleanupResult(
            cleaned_vector=current_vector,
            confidence=similarity,
            original_similarity=self._cosine_similarity(partial_vector, current_vector),
            iterations=iterations,
            converged=converged,
            candidate_matches=[(best_match, similarity)] if best_match else []
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get memory statistics"""
        total_strength = sum(trace.trace_strength for trace in self.memory_traces.values())
        total_access = sum(trace.access_count for trace in self.memory_traces.values())
        
        cleanup_success_rate = (self.successful_cleanups / self.cleanup_count 
                              if self.cleanup_count > 0 else 0.0)
        
        return {
            "memory_capacity": self.memory_capacity,
            "stored_traces": len(self.memory_traces),
            "total_strength": total_strength,
            "total_accesses": total_access,
            "storage_count": self.storage_count,
            "retrieval_count": self.retrieval_count,
            "cleanup_count": self.cleanup_count,
            "successful_cleanups": self.successful_cleanups,
            "cleanup_success_rate": cleanup_success_rate,
            "vector_dim": self.vector_dim,
            "cleanup_threshold": self.cleanup_threshold
        }
    
    def decay_memory(self, decay_factor: float = 0.95):
        """Apply decay to all memory traces"""
        traces_to_remove = []
        
        for key_hash, trace in self.memory_traces.items():
            trace.trace_strength *= decay_factor
            
            # Remove very weak traces
            if trace.trace_strength < 0.01:
                traces_to_remove.append(key_hash)
        
        # Remove weak traces
        for key_hash in traces_to_remove:
            del self.memory_traces[key_hash]
    
    def clear_memory(self):
        """Clear all stored memory traces"""
        self.memory_traces.clear()
        self.auto_weights.fill(0)
        self.hetero_weights.fill(0)
        self.trace_counter = 0

class HopfieldCleanup(AssociativeMemory):
    """
    Hopfield network implementation for associative cleanup
    
    Uses energy minimization approach for pattern retrieval and cleanup
    """
    
    def __init__(self,
                 vector_dim: int = 512,
                 max_patterns: int = 100,
                 temperature: float = 0.1,
                 max_iterations: int = 100):
        """
        Initialize Hopfield cleanup network
        
        Args:
            vector_dim: Vector dimensionality
            max_patterns: Maximum number of stored patterns
            temperature: Temperature parameter for updates
            max_iterations: Maximum iterations for convergence
        """
        self.vector_dim = vector_dim
        self.max_patterns = max_patterns
        self.temperature = temperature
        self.max_iterations = max_iterations
        
        # Weight matrix
        self.weights = np.zeros((vector_dim, vector_dim))
        
        # Stored patterns
        self.patterns = []
        self.pattern_names = []
    
    def store(self, key: np.ndarray, value: np.ndarray, strength: float = 1.0):
        """Store pattern in Hopfield network"""
        # For Hopfield networks, we typically store the value as the pattern
        pattern = value.copy()
        
        # Convert to bipolar (-1, +1)
        pattern = np.sign(pattern)
        pattern[pattern == 0] = 1  # No zeros in bipolar representation
        
        if len(self.patterns) >= self.max_patterns:
            # Remove oldest pattern
            old_pattern = self.patterns.pop(0)
            self.pattern_names.pop(0)
            
            # Remove its contribution to weights
            self.weights -= strength * np.outer(old_pattern, old_pattern)
        
        # Add new pattern
        self.patterns.append(pattern)
        self.pattern_names.append(f"pattern_{len(self.pattern_names)}")
        
        # Update weights using Hebbian rule
        self.weights += strength * np.outer(pattern, pattern)
        
        # Zero diagonal (no self-connections)
        np.fill_diagonal(self.weights, 0)
    
    def retrieve(self, key: np.ndarray, cleanup: bool = True) -> CleanupResult:
        """Retrieve using Hopfield dynamics"""
        return self.cleanup(key)
    
    def cleanup(self, noisy_vector: np.ndarray, max_iterations: int = None) -> CleanupResult:
        """Clean up vector using Hopfield dynamics"""
        if max_iterations is None:
            max_iterations = self.max_iterations
        
        # Convert to bipolar
        current = np.sign(noisy_vector)
        current[current == 0] = 1
        
        original_similarity = 0.0
        best_match = self._find_closest_pattern(current)
        if best_match:
            original_similarity = self._pattern_similarity(current, self.patterns[best_match])
        
        # Hopfield dynamics
        iterations = 0
        converged = False
        
        for iteration in range(max_iterations):
            # Compute field
            field = np.dot(self.weights, current)
            
            # Update rule (asynchronous or synchronous)
            new_state = np.tanh(field / self.temperature)
            new_state = np.sign(new_state)
            new_state[new_state == 0] = 1
            
            # Check convergence
            if np.array_equal(new_state, current):
                converged = True
                break
            
            current = new_state
            iterations = iteration + 1
        
        # Find best matching pattern
        best_pattern_idx = self._find_closest_pattern(current)
        confidence = 0.0
        candidates = []
        
        if best_pattern_idx is not None:
            confidence = self._pattern_similarity(current, self.patterns[best_pattern_idx])
            candidates = [(self.pattern_names[best_pattern_idx], confidence)]
        
        return CleanupResult(
            cleaned_vector=current,
            confidence=confidence,
            original_similarity=original_similarity,
            iterations=iterations,
            converged=converged,
            candidate_matches=candidates
        )
    
    def _find_closest_pattern(self, query: np.ndarray) -> Optional[int]:
        """Find index of closest stored pattern"""
        if not self.patterns:
            return None
        
        best_idx = 0
        best_similarity = self._pattern_similarity(query, self.patterns[0])
        
        for i, pattern in enumerate(self.patterns[1:], 1):
            similarity = self._pattern_similarity(query, pattern)
            if similarity > best_similarity:
                best_similarity = similarity
                best_idx = i
        
        return best_idx
    
    def _pattern_similarity(self, pattern1: np.ndarray, pattern2: np.ndarray) -> float:
        """Compute similarity between bipolar patterns"""
        return np.mean(pattern1 == pattern2)

# Utility functions
def create_prototype_cleanup(prototypes: Dict[str, np.ndarray],
                           vector_dim: int = 512) -> AssociativeCleanup:
    """
    Create cleanup network with predefined prototypes
    
    Args:
        prototypes: Dictionary of prototype vectors
        vector_dim: Vector dimensionality
        
    Returns:
        Configured AssociativeCleanup network
    """
    cleanup = AssociativeCleanup(vector_dim=vector_dim)
    cleanup.add_prototypes(prototypes)
    return cleanup

def test_cleanup_network(cleanup: AssociativeMemory,
                        test_vectors: List[np.ndarray],
                        noise_levels: List[float] = [0.1, 0.2, 0.3]) -> Dict[str, Any]:
    """
    Test cleanup network performance with various noise levels
    
    Args:
        cleanup: Cleanup network to test
        test_vectors: Clean test vectors
        noise_levels: Noise levels to test
        
    Returns:
        Test results dictionary
    """
    results = {}
    
    for noise_level in noise_levels:
        level_results = []
        
        for clean_vector in test_vectors:
            # Add noise
            noise = np.random.normal(0, noise_level, len(clean_vector))
            noisy_vector = clean_vector + noise
            
            # Cleanup
            result = cleanup.cleanup(noisy_vector)
            
            # Measure performance
            original_similarity = np.dot(clean_vector, noisy_vector) / (
                np.linalg.norm(clean_vector) * np.linalg.norm(noisy_vector)
            )
            
            cleaned_similarity = np.dot(clean_vector, result.cleaned_vector) / (
                np.linalg.norm(clean_vector) * np.linalg.norm(result.cleaned_vector)
            )
            
            level_results.append({
                "original_similarity": original_similarity,
                "cleaned_similarity": cleaned_similarity,
                "improvement": cleaned_similarity - original_similarity,
                "converged": result.converged,
                "iterations": result.iterations
            })
        
        results[f"noise_{noise_level}"] = {
            "mean_improvement": np.mean([r["improvement"] for r in level_results]),
            "mean_iterations": np.mean([r["iterations"] for r in level_results]),
            "convergence_rate": np.mean([r["converged"] for r in level_results]),
            "details": level_results
        }
    
    return results