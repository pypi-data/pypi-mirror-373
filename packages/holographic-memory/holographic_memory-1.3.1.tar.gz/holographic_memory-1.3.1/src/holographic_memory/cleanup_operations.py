"""
Cleanup operations for Holographic Memory
Implements auto-associative cleanup memory from Plate 1995 Section IV
"""

import numpy as np
from typing import Dict, Any, Optional, List, Tuple


class CleanupOperations:
    """Handles cleanup operations for HolographicMemory systems"""
    
    def __init__(self, memory_instance):
        self.memory = memory_instance
    
    def cleanup_memory(self, noisy_vector: np.ndarray, candidates: Optional[List[str]] = None, 
                      threshold: float = 0.1, max_iterations: int = 10) -> Tuple[str, float]:
        """
        Clean up noisy vector by finding best matching clean memory item
        
        This implements associative memory cleanup - a key property of HRR
        """
        
        if not self.memory.cleanup_enabled:
            # Fallback to simple nearest neighbor if cleanup disabled
            return self._nearest_neighbor_cleanup(noisy_vector, candidates)
        
        # FIXED: Implement iterative cleanup using auto-associative memory
        current_vector = noisy_vector.copy()
        
        for iteration in range(max_iterations):
            # Find best matching clean vector
            best_match, best_similarity = self._nearest_neighbor_cleanup(current_vector, candidates)
            
            if best_match is None or best_similarity < threshold:
                break
                
            # Get the clean version from cleanup memory
            if best_match in self.memory.cleanup_items:
                clean_vector = self.memory.cleanup_items[best_match]
                
                # Iterative cleanup: blend current vector with clean version
                # This simulates auto-associative memory dynamics
                blend_factor = min(0.8, best_similarity)  # Higher similarity -> more trust
                current_vector = blend_factor * clean_vector + (1 - blend_factor) * current_vector
                
                # Normalize after blending
                if self.memory.normalize:
                    current_vector = self.memory.vector_ops._normalize_vector(current_vector)
                    
                # Check convergence
                new_similarity = self.memory.vector_ops.similarity(current_vector, clean_vector)
                if abs(new_similarity - best_similarity) < 0.01:
                    break  # Converged
                    
        # Final match after cleanup iterations
        return self._nearest_neighbor_cleanup(current_vector, candidates)
    
    def _nearest_neighbor_cleanup(self, noisy_vector: np.ndarray, candidates: Optional[List[str]] = None) -> Tuple[str, float]:
        """Simple nearest neighbor cleanup fallback"""
        if candidates is None:
            candidates = list(self.memory.memory_items.keys())
            
        best_match = None
        best_similarity = -1
        
        for candidate in candidates:
            if candidate not in self.memory.memory_items:
                continue
                
            sim = self.memory.vector_ops.similarity(noisy_vector, self.memory.memory_items[candidate].vector)
            if sim > best_similarity:
                best_similarity = sim
                best_match = candidate
        
        return best_match, best_similarity
    
    def _initialize_hopfield_cleanup(self):
        """Initialize Hopfield-style auto-associative cleanup memory"""
        if not hasattr(self.memory, 'hopfield_weights'):
            # Initialize Hopfield weight matrix for cleanup
            n = self.memory.vector_dim
            self.memory.hopfield_weights = np.zeros((n, n))
            
        # Update weights with current memory items
        for item in self.memory.memory_items.values():
            vector = item.vector
            # Hopfield learning rule: W += (x ⊗ x) / n
            self.memory.hopfield_weights += np.outer(vector, vector) / self.memory.vector_dim
        
        print("✓ Hopfield cleanup memory initialized")
    
    def _hopfield_cleanup(self, noisy_vector: np.ndarray, max_iterations: int = 100, threshold: float = 0.001) -> np.ndarray:
        """Hopfield network cleanup"""
        if not hasattr(self.memory, 'hopfield_weights'):
            self._initialize_hopfield_cleanup()
        
        current = noisy_vector.copy()
        
        for iteration in range(max_iterations):
            # Hopfield update: x_new = sign(W @ x_old)
            new_vector = np.tanh(self.memory.hopfield_weights @ current)
            
            # Check convergence
            diff = np.linalg.norm(new_vector - current)
            if diff < threshold:
                break
                
            current = new_vector
        
        return current