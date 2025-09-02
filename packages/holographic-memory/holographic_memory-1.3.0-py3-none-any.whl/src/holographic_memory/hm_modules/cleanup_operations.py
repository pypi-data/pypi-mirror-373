"""
Cleanup and Error Correction Module for Holographic Memory System

Implements cleanup operations essential for HRR systems, including
auto-associative cleanup memory and Hopfield-style error correction.

Author: Benedict Chen (benedict@benedictchen.com)
"""

import numpy as np
from typing import List, Tuple, Optional, Dict, Any
from .configuration import HRRConfig
from .vector_operations import VectorOperations
from .memory_management import MemoryManager


class CleanupOperations:
    """Handles cleanup and error correction for noisy HRR vectors"""
    
    def __init__(self, config: HRRConfig, vector_ops: VectorOperations, memory_manager: MemoryManager):
        """Initialize cleanup operations"""
        self.config = config
        self.vector_ops = vector_ops
        self.memory_manager = memory_manager
        
        # Cleanup memory storage
        self.cleanup_items = {}
        self.last_cleanup_success_rate = None
        
        print(f"✓ Cleanup Operations initialized with {config.cleanup_memory_type} cleanup")
    
    def cleanup_memory(self, noisy_vector: np.ndarray, 
                      candidates: Optional[List[str]] = None,
                      threshold: float = 0.1) -> Tuple[str, float]:
        """
        Clean up noisy vector by finding best match among stored vectors
        
        This is crucial for HRR systems as binding/unbinding introduces noise.
        
        Parameters:
        -----------
        noisy_vector : np.ndarray
            Noisy vector to clean up
        candidates : List[str], optional
            Candidate vector names to match against
        threshold : float
            Minimum similarity threshold for valid match
        
        Returns:
        --------
        best_match : str
            Name of best matching vector
        confidence : float
            Confidence score (similarity to best match)
        """
        if candidates is None:
            candidates = list(self.memory_manager.memory_items.keys())
            
        if not candidates:
            return "", 0.0
        
        # Validate input vector
        try:
            self.vector_ops.validate_vector(noisy_vector, "noisy_vector")
        except ValueError:
            return "", 0.0
            
        best_match = ""
        best_similarity = -float('inf')
        
        # Find best matching vector
        for candidate in candidates:
            if self.memory_manager.has_vector(candidate):
                candidate_vec = self.memory_manager.get_vector(candidate)
                sim = self.vector_ops.similarity(noisy_vector, candidate_vec)
                if sim > best_similarity:
                    best_similarity = sim
                    best_match = candidate
        
        # Check if similarity meets threshold
        confidence = float(best_similarity)
        if confidence < threshold:
            best_match = ""
            
        return best_match, confidence
    
    def create_cleanup_memory(self, item_names: List[str]):
        """
        Create auto-associative cleanup memory (Hopfield-style)
        
        Parameters:
        -----------
        item_names : List[str]
            Names of vectors to include in cleanup memory
        """
        if not item_names:
            return
            
        # Collect vectors for cleanup memory
        vectors = []
        valid_names = []
        
        for name in item_names:
            if self.memory_manager.has_vector(name):
                vectors.append(self.memory_manager.get_vector(name))
                valid_names.append(name)
                
        if not vectors:
            print("Warning: No valid vectors found for cleanup memory")
            return
            
        # Create Hopfield-style weight matrix
        vectors_matrix = np.array(vectors)
        
        # Compute outer product sum (Hopfield rule)
        n_vectors, dim = vectors_matrix.shape
        weights = np.zeros((dim, dim))
        
        for i in range(n_vectors):
            v = vectors_matrix[i]
            if self.config.normalize:
                v = self.vector_ops.normalize_vector(v)
            weights += np.outer(v, v)
            
        # Remove diagonal (no self-connections)
        np.fill_diagonal(weights, 0)
        weights /= n_vectors  # Normalize
        
        # Store cleanup memory
        self.cleanup_items['weight_matrix'] = weights
        self.cleanup_items['item_names'] = valid_names.copy()
        self.cleanup_items['vectors'] = vectors_matrix.copy()
        
        print(f"✓ Cleanup memory created with {n_vectors} vectors")
    
    def hopfield_cleanup(self, noisy_vector: np.ndarray, max_iterations: int = 10) -> np.ndarray:
        """
        Use Hopfield network for cleanup
        
        Parameters:
        -----------
        noisy_vector : np.ndarray
            Noisy vector to clean up
        max_iterations : int
            Maximum number of iterations
        
        Returns:
        --------
        cleaned : np.ndarray
            Cleaned vector after Hopfield iterations
        """
        if 'weight_matrix' not in self.cleanup_items:
            print("Warning: Cleanup memory not initialized")
            return noisy_vector
            
        weights = self.cleanup_items['weight_matrix']
        
        # Validate input
        try:
            self.vector_ops.validate_vector(noisy_vector, "noisy_vector")
        except ValueError:
            return noisy_vector
        
        # Iterative cleanup
        current = noisy_vector.copy()
        
        for iteration in range(max_iterations):
            # Hopfield update rule
            next_state = np.tanh(weights @ current)
            
            # Check for convergence
            if np.allclose(current, next_state, atol=1e-6):
                break
                
            current = next_state
            
        return current
    
    def iterative_cleanup(self, noisy_vector: np.ndarray, 
                         n_iterations: int = 3,
                         candidates: Optional[List[str]] = None) -> Tuple[str, float, np.ndarray]:
        """
        Perform iterative cleanup using both Hopfield and similarity matching
        
        Parameters:
        -----------
        noisy_vector : np.ndarray
            Noisy vector to clean up
        n_iterations : int
            Number of cleanup iterations
        candidates : List[str], optional
            Candidate vectors for matching
        
        Returns:
        --------
        best_match : str
            Name of best matching vector
        confidence : float
            Final confidence score
        cleaned_vector : np.ndarray
            Cleaned vector
        """
        current_vector = noisy_vector.copy()
        
        for i in range(n_iterations):
            # Apply Hopfield cleanup if available
            if self.config.cleanup_memory and 'weight_matrix' in self.cleanup_items:
                current_vector = self.hopfield_cleanup(current_vector, max_iterations=5)
            
            # Find best match
            best_match, confidence = self.cleanup_memory(current_vector, candidates)
            
            # If we found a good match, use it for next iteration
            if confidence > 0.5 and best_match and self.memory_manager.has_vector(best_match):
                matched_vector = self.memory_manager.get_vector(best_match)
                # Blend with current vector for gradual cleanup
                alpha = 0.3  # Blending factor
                current_vector = alpha * matched_vector + (1 - alpha) * current_vector
                if self.config.normalize:
                    current_vector = self.vector_ops.normalize_vector(current_vector)
        
        # Final cleanup pass
        final_match, final_confidence = self.cleanup_memory(current_vector, candidates)
        
        return final_match, final_confidence, current_vector
    
    def test_cleanup_performance(self, test_vectors: List[str], 
                               noise_levels: List[float] = None,
                               n_trials: int = 10) -> Dict[str, Any]:
        """
        Test cleanup performance across different noise levels
        
        Parameters:
        -----------
        test_vectors : List[str]
            Names of vectors to test cleanup on
        noise_levels : List[float], optional
            Noise levels to test
        n_trials : int
            Number of trials per noise level
        
        Returns:
        --------
        results : Dict[str, Any]
            Performance results
        """
        if noise_levels is None:
            noise_levels = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
        
        # Ensure test vectors exist
        valid_test_vectors = [name for name in test_vectors 
                             if self.memory_manager.has_vector(name)]
        
        if not valid_test_vectors:
            return {'error': 'No valid test vectors found'}
        
        results = {
            'noise_levels': noise_levels,
            'test_vectors': valid_test_vectors,
            'accuracy_by_noise': {},
            'confidence_by_noise': {},
            'n_trials': n_trials
        }
        
        for noise_level in noise_levels:
            correct_cleanups = 0
            total_trials = 0
            confidence_scores = []
            
            for trial in range(n_trials):
                for vector_name in valid_test_vectors:
                    # Get clean vector
                    clean_vector = self.memory_manager.get_vector(vector_name)
                    
                    # Add noise
                    noisy_vector = clean_vector.copy()
                    if noise_level > 0:
                        noise = np.random.normal(0, noise_level, len(clean_vector))
                        noisy_vector += noise
                        if self.config.normalize:
                            noisy_vector = self.vector_ops.normalize_vector(noisy_vector)
                    
                    # Test cleanup
                    cleaned_name, confidence = self.cleanup_memory(noisy_vector, valid_test_vectors)
                    
                    total_trials += 1
                    confidence_scores.append(confidence)
                    
                    if cleaned_name == vector_name:
                        correct_cleanups += 1
            
            # Calculate metrics
            accuracy = correct_cleanups / total_trials if total_trials > 0 else 0.0
            avg_confidence = np.mean(confidence_scores) if confidence_scores else 0.0
            
            results['accuracy_by_noise'][noise_level] = accuracy
            results['confidence_by_noise'][noise_level] = avg_confidence
        
        # Store last success rate
        self.last_cleanup_success_rate = results['accuracy_by_noise'].get(0.1, 0.0)
        
        return results
    
    def adaptive_cleanup(self, noisy_vector: np.ndarray,
                        initial_candidates: Optional[List[str]] = None,
                        max_candidates: int = 10) -> Tuple[str, float, List[str]]:
        """
        Adaptive cleanup that narrows down candidates iteratively
        
        Parameters:
        -----------
        noisy_vector : np.ndarray
            Vector to clean up
        initial_candidates : List[str], optional
            Initial candidate set
        max_candidates : int
            Maximum number of candidates to consider
        
        Returns:
        --------
        best_match : str
            Best matching vector name
        confidence : float
            Confidence score
        cleanup_path : List[str]
            Path of cleanup decisions
        """
        if initial_candidates is None:
            initial_candidates = list(self.memory_manager.memory_items.keys())
        
        candidates = initial_candidates.copy()
        cleanup_path = []
        
        # Iteratively narrow down candidates
        while len(candidates) > max_candidates and len(candidates) > 1:
            # Calculate similarities to all current candidates
            similarities = []
            for candidate in candidates:
                if self.memory_manager.has_vector(candidate):
                    candidate_vec = self.memory_manager.get_vector(candidate)
                    sim = self.vector_ops.similarity(noisy_vector, candidate_vec)
                    similarities.append((candidate, sim))
            
            # Keep top half of candidates
            similarities.sort(key=lambda x: x[1], reverse=True)
            keep_count = max(1, len(similarities) // 2)
            candidates = [name for name, _ in similarities[:keep_count]]
            cleanup_path.append(f"Narrowed to top {keep_count} candidates")
        
        # Final cleanup with remaining candidates
        best_match, confidence = self.cleanup_memory(noisy_vector, candidates)
        cleanup_path.append(f"Final match: {best_match} (confidence: {confidence:.3f})")
        
        return best_match, confidence, cleanup_path
    
    def batch_cleanup(self, noisy_vectors: List[np.ndarray],
                     candidates: Optional[List[str]] = None) -> List[Tuple[str, float]]:
        """
        Perform cleanup on multiple vectors efficiently
        
        Parameters:
        -----------
        noisy_vectors : List[np.ndarray]
            List of noisy vectors to clean up
        candidates : List[str], optional
            Candidate vectors for matching
        
        Returns:
        --------
        results : List[Tuple[str, float]]
            List of (best_match, confidence) tuples
        """
        results = []
        
        for noisy_vector in noisy_vectors:
            try:
                best_match, confidence = self.cleanup_memory(noisy_vector, candidates)
                results.append((best_match, confidence))
            except Exception as e:
                print(f"Warning: Cleanup failed for vector: {e}")
                results.append(("", 0.0))
        
        return results
    
    def get_cleanup_stats(self) -> Dict[str, Any]:
        """Get statistics about cleanup operations"""
        stats = {
            'cleanup_enabled': self.config.cleanup_memory,
            'cleanup_type': self.config.cleanup_memory_type,
            'last_success_rate': self.last_cleanup_success_rate,
            'hopfield_available': 'weight_matrix' in self.cleanup_items,
        }
        
        if 'weight_matrix' in self.cleanup_items:
            stats.update({
                'cleanup_vectors_count': len(self.cleanup_items.get('item_names', [])),
                'weight_matrix_shape': self.cleanup_items['weight_matrix'].shape,
                'weight_matrix_sparsity': float(np.sum(np.abs(self.cleanup_items['weight_matrix']) < 1e-10) / 
                                              self.cleanup_items['weight_matrix'].size)
            })
        
        return stats