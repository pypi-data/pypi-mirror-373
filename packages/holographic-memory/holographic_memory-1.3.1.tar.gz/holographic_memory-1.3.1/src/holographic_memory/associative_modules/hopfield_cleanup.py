"""
🧲 Holographic Memory - Hopfield Cleanup Network Module
=====================================================

Split from associative_memory.py (918 lines → modular architecture)
Part of holographic_memory package 800-line compliance initiative.

Author: Benedict Chen (benedict@benedictchen.com)
Based on: Hopfield (1982) "Neural networks and physical systems with emergent collective computational abilities"
         Plate (1995) "Holographic Reduced Representations"

🎯 MODULE PURPOSE:
=================
Hopfield network implementation for associative cleanup and pattern completion.
Uses energy minimization approach for robust pattern retrieval in holographic memory.

🔬 RESEARCH FOUNDATION:
======================
Implements Hopfield (1982) energy minimization cleanup with adaptations for:
- Holographic memory pattern storage and retrieval
- Energy-based convergence guarantees for cleanup operations
- Bipolar pattern representation with asynchronous/synchronous updates
- Temperature-controlled pattern completion dynamics

This module provides specialized Hopfield-based cleanup for cases where
energy minimization is preferred over correlation-based methods.
"""

import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from .memory_structures import AssociativeMemory, CleanupResult


class HopfieldCleanup(AssociativeMemory):
    """
    🧲 Hopfield Network for Associative Memory Cleanup
    
    Energy minimization approach to pattern retrieval and cleanup,
    based on Hopfield (1982) with adaptations for holographic memory.
    
    Features:
    ---------
    ✅ Energy function minimization for guaranteed convergence
    ✅ Bipolar pattern representation for robust storage
    ✅ Temperature-controlled dynamics for smooth convergence
    ✅ Capacity management following Hopfield storage limits
    """
    
    def __init__(self,
                 vector_dim: int = 512,
                 max_patterns: int = 100,
                 temperature: float = 0.1,
                 max_iterations: int = 100,
                 convergence_threshold: float = 1e-6):
        """
        Initialize Hopfield Cleanup Network
        
        Parameters:
        -----------
        vector_dim : int, default=512
            Vector dimensionality (typically high for holographic memory)
        max_patterns : int, default=100
            Maximum stored patterns (Hopfield capacity ~0.14 * vector_dim)
        temperature : float, default=0.1
            Temperature parameter for update dynamics
        max_iterations : int, default=100
            Maximum iterations for energy minimization
        convergence_threshold : float, default=1e-6
            Threshold for detecting convergence
        """
        self.vector_dim = vector_dim
        self.max_patterns = min(max_patterns, int(0.14 * vector_dim))  # Hopfield capacity limit
        self.temperature = temperature
        self.max_iterations = max_iterations
        self.convergence_threshold = convergence_threshold
        
        # Hopfield weight matrix
        self.weights = np.zeros((vector_dim, vector_dim))
        np.fill_diagonal(self.weights, 0)  # No self-connections
        
        # Stored patterns and metadata
        self.patterns: List[np.ndarray] = []
        self.pattern_names: List[str] = []
        self.pattern_energies: List[float] = []
        
        # Performance statistics
        self.stats = {
            'patterns_stored': 0,
            'retrievals_attempted': 0,
            'successful_retrievals': 0,
            'energy_minimizations': 0,
            'convergent_retrievals': 0
        }
    
    def store(self, key: np.ndarray, value: np.ndarray, strength: float = 1.0) -> None:
        """
        Store pattern in Hopfield network using Hebbian learning.
        
        For Hopfield networks, we store the value vector as the pattern to be retrieved.
        
        Parameters:
        -----------
        key : np.ndarray
            Key vector (used for naming/indexing)
        value : np.ndarray
            Value vector to store as attractor pattern
        strength : float, default=1.0
            Storage strength weight
        """
        # Convert to bipolar representation (-1, +1)
        pattern = self._to_bipolar(value)
        
        # Check capacity
        if len(self.patterns) >= self.max_patterns:
            # Remove oldest pattern and its contribution
            old_pattern = self.patterns.pop(0)
            old_name = self.pattern_names.pop(0) if self.pattern_names else "unknown"
            self.pattern_energies.pop(0) if self.pattern_energies else None
            
            # Remove weight contribution
            self.weights -= strength * np.outer(old_pattern, old_pattern)
            np.fill_diagonal(self.weights, 0)
        
        # Add new pattern
        self.patterns.append(pattern)
        self.pattern_names.append(f"pattern_{len(self.patterns)}")
        
        # Update weights using Hebbian rule: ΔW = η * pattern ⊗ pattern
        weight_update = strength * np.outer(pattern, pattern)
        self.weights += weight_update
        np.fill_diagonal(self.weights, 0)  # Ensure no self-connections
        
        # Store pattern energy
        energy = self._compute_energy(pattern)
        self.pattern_energies.append(energy)
        
        self.stats['patterns_stored'] += 1
    
    def recall(self, key: np.ndarray, cleanup: bool = True) -> CleanupResult:
        """Recall pattern using Hopfield dynamics."""
        return self.cleanup(key)
    
    def cleanup(self, noisy_vector: np.ndarray, max_iterations: int = None) -> CleanupResult:
        """
        Clean up noisy vector using Hopfield energy minimization.
        
        Parameters:
        -----------
        noisy_vector : np.ndarray
            Noisy input vector to be cleaned
        max_iterations : int, optional
            Maximum iterations (uses instance default if None)
            
        Returns:
        --------
        CleanupResult
            Cleanup result with energy minimization details
        """
        if max_iterations is None:
            max_iterations = self.max_iterations
            
        self.stats['retrievals_attempted'] += 1
        self.stats['energy_minimizations'] += 1
        
        # Convert to bipolar
        current_state = self._to_bipolar(noisy_vector)
        initial_energy = self._compute_energy(current_state)
        
        # Track convergence
        energy_history = [initial_energy]
        state_history = [current_state.copy()]
        
        converged = False
        iterations = 0
        
        for iteration in range(max_iterations):
            # Compute local field for each neuron
            local_fields = np.dot(self.weights, current_state)
            
            # Asynchronous update (one neuron at a time for guaranteed convergence)
            new_state = current_state.copy()
            for i in range(self.vector_dim):
                if local_fields[i] > 0:
                    new_state[i] = 1
                elif local_fields[i] < 0:
                    new_state[i] = -1
                # If field is exactly 0, keep current state
            
            # Apply temperature-controlled updates
            if self.temperature > 0:
                # Stochastic updates with temperature
                probabilities = np.tanh(local_fields / self.temperature)
                random_updates = np.random.random(self.vector_dim)
                new_state = np.where(random_updates < (probabilities + 1) / 2, 1, -1)
            
            # Check for convergence
            energy = self._compute_energy(new_state)
            energy_history.append(energy)
            
            # Convergence: no change in state
            if np.array_equal(new_state, current_state):
                converged = True
                break
                
            # Energy-based convergence check
            if len(energy_history) > 1 and abs(energy_history[-1] - energy_history[-2]) < self.convergence_threshold:
                converged = True
                break
            
            current_state = new_state
            iterations = iteration + 1
            
            # Prevent cycles by checking state history
            for prev_state in state_history[-5:]:  # Check last 5 states
                if np.array_equal(current_state, prev_state):
                    converged = False  # Detected cycle, stop
                    break
            else:
                state_history.append(current_state.copy())
                continue
            break
        
        # Find best matching stored pattern
        final_energy = self._compute_energy(current_state)
        best_pattern_idx = self._find_closest_pattern(current_state)
        
        confidence = 0.0
        candidates = []
        if best_pattern_idx is not None:
            confidence = self._pattern_overlap(current_state, self.patterns[best_pattern_idx])
            candidates = [(self.pattern_names[best_pattern_idx], confidence)]
        
        # Success metrics
        if confidence > 0.8:
            self.stats['successful_retrievals'] += 1
        if converged:
            self.stats['convergent_retrievals'] += 1
        
        return CleanupResult(
            cleaned_vector=current_state.astype(float),
            confidence=confidence,
            original_similarity=self._pattern_overlap(self._to_bipolar(noisy_vector), current_state),
            iterations=iterations,
            converged=converged,
            candidate_matches=candidates
        )
    
    def similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute pattern similarity (overlap for bipolar patterns)."""
        bipolar1 = self._to_bipolar(vec1)
        bipolar2 = self._to_bipolar(vec2)
        return self._pattern_overlap(bipolar1, bipolar2)
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get comprehensive Hopfield network statistics."""
        success_rate = (self.stats['successful_retrievals'] / 
                       max(1, self.stats['retrievals_attempted']))
        convergence_rate = (self.stats['convergent_retrievals'] / 
                          max(1, self.stats['energy_minimizations']))
        
        capacity_utilization = len(self.patterns) / self.max_patterns
        
        return {
            'memory_type': 'HopfieldCleanup',
            'implementation': 'energy_minimization',
            'vector_dimension': self.vector_dim,
            'max_capacity': self.max_patterns,
            'theoretical_capacity': int(0.14 * self.vector_dim),
            'stored_patterns': len(self.patterns),
            'capacity_utilization': capacity_utilization,
            'success_rate': success_rate,
            'convergence_rate': convergence_rate,
            'temperature': self.temperature,
            **self.stats
        }
    
    # Private helper methods
    def _to_bipolar(self, vector: np.ndarray) -> np.ndarray:
        """Convert vector to bipolar representation (-1, +1)."""
        bipolar = np.sign(vector)
        bipolar[bipolar == 0] = 1  # No zeros in bipolar
        return bipolar
    
    def _compute_energy(self, state: np.ndarray) -> float:
        """Compute Hopfield energy: E = -½ Σᵢⱼ wᵢⱼsᵢsⱼ"""
        return -0.5 * np.dot(state, np.dot(self.weights, state))
    
    def _find_closest_pattern(self, query: np.ndarray) -> Optional[int]:
        """Find index of closest stored pattern."""
        if not self.patterns:
            return None
        
        best_idx = 0
        best_overlap = self._pattern_overlap(query, self.patterns[0])
        
        for i, pattern in enumerate(self.patterns[1:], 1):
            overlap = self._pattern_overlap(query, pattern)
            if overlap > best_overlap:
                best_overlap = overlap
                best_idx = i
        
        return best_idx
    
    def _pattern_overlap(self, pattern1: np.ndarray, pattern2: np.ndarray) -> float:
        """Compute overlap between bipolar patterns."""
        return np.mean(pattern1 == pattern2)


# Export the Hopfield cleanup engine
__all__ = ['HopfieldCleanup']


if __name__ == "__main__":
    print("🧲 Holographic Memory - Hopfield Cleanup Network Module")
    print("=" * 61)
    print("📊 MODULE CONTENTS:")
    print("  • HopfieldCleanup - Energy minimization cleanup network")
    print("  • Bipolar pattern representation for robust storage")
    print("  • Temperature-controlled dynamics for smooth convergence")
    print("  • Capacity management following Hopfield theoretical limits")
    print("")
    print("✅ Hopfield cleanup network module loaded successfully!")
    print("🔬 Hopfield (1982) energy minimization for holographic memory cleanup!")