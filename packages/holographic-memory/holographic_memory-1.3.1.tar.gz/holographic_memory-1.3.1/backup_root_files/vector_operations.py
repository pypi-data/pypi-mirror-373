"""
Core vector operations for Holographic Memory
Implements binding, unbinding, and utility operations from Plate 1995
"""

import numpy as np
from typing import Union, List, Optional


class VectorOperations:
    """Core vector operations for HRR"""
    
    def __init__(self, memory_instance):
        self.memory = memory_instance
    
    def bind(self, vec_a: Union[str, np.ndarray], vec_b: Union[str, np.ndarray]) -> np.ndarray:
        """
        Circular convolution binding operation (⊛) - Core HRR Operation!
        """
        # Convert to arrays if names
        if isinstance(vec_a, str):
            if vec_a not in self.memory.memory_items:
                raise ValueError(f"Vector '{vec_a}' not found in memory")
            array_a = self.memory.memory_items[vec_a].vector
        else:
            array_a = vec_a
            
        if isinstance(vec_b, str):
            if vec_b not in self.memory.memory_items:
                raise ValueError(f"Vector '{vec_b}' not found in memory")
            array_b = self.memory.memory_items[vec_b].vector
        else:
            array_b = vec_b
        
        # Ensure same dimension
        if len(array_a) != len(array_b):
            raise ValueError(f"Vector dimensions must match: {len(array_a)} vs {len(array_b)}")
        
        # Apply unitary transform if enabled
        if self.memory.unitary_vectors:
            array_a = self._make_unitary(array_a)
            array_b = self._make_unitary(array_b)
        
        # Circular convolution using FFT (efficient implementation)
        fft_a = np.fft.fft(array_a)
        fft_b = np.fft.fft(array_b)
        
        # Element-wise multiplication in frequency domain = convolution in time domain
        fft_result = fft_a * fft_b
        
        # Convert back to time domain
        result = np.real(np.fft.ifft(fft_result))
        
        # Add noise if specified
        result = self._add_noise(result)
        
        # Normalize if enabled
        if self.memory.normalize:
            result = self._normalize_vector(result)
        
        # Track association count for capacity monitoring
        self.memory.association_count += 1
        
        return result
    
    def unbind(self, bound_vec: np.ndarray, cue_vec: Union[str, np.ndarray]) -> np.ndarray:
        """
        Circular correlation unbinding operation (~) - HRR Decoding!
        """
        # Convert cue to array if name
        if isinstance(cue_vec, str):
            if cue_vec not in self.memory.memory_items:
                raise ValueError(f"Cue vector '{cue_vec}' not found in memory")
            cue_array = self.memory.memory_items[cue_vec].vector
        else:
            cue_array = cue_vec
            
        # Ensure same dimension
        if len(bound_vec) != len(cue_array):
            raise ValueError(f"Vector dimensions must match: {len(bound_vec)} vs {len(cue_array)}")
        
        # Circular correlation using involution and convolution
        # a ~ b = a ⊛ b* where b* is involution of b
        inverted_cue = self._involution(cue_array)
        
        # Perform circular convolution with inverted cue
        fft_bound = np.fft.fft(bound_vec)
        fft_inv_cue = np.fft.fft(inverted_cue)
        
        fft_result = fft_bound * fft_inv_cue
        result = np.real(np.fft.ifft(fft_result))
        
        # Add noise if specified
        result = self._add_noise(result)
        
        # Normalize if enabled
        if self.memory.normalize:
            result = self._normalize_vector(result)
        
        return result
    
    def superpose(self, vectors: List[Union[str, np.ndarray]], normalize: bool = True) -> np.ndarray:
        """Create superposition (sum) of multiple vectors"""
        if not vectors:
            return np.zeros(self.memory.vector_dim)
            
        result = np.zeros(self.memory.vector_dim)
        
        for vec in vectors:
            if isinstance(vec, str):
                if vec not in self.memory.memory_items:
                    raise ValueError(f"Vector '{vec}' not found in memory")
                vector_data = self.memory.memory_items[vec].vector
            else:
                vector_data = vec
                
            result += vector_data
            
        if normalize and self.memory.normalize:
            result = self._normalize_vector(result)
            
        return result
    
    def similarity(self, vec1: Union[str, np.ndarray], vec2: Union[str, np.ndarray]) -> float:
        """Calculate similarity between two vectors using dot product"""
        # Convert to arrays if names
        if isinstance(vec1, str):
            if vec1 not in self.memory.memory_items:
                raise ValueError(f"Vector '{vec1}' not found in memory")
            array1 = self.memory.memory_items[vec1].vector
        else:
            array1 = vec1
            
        if isinstance(vec2, str):
            if vec2 not in self.memory.memory_items:
                raise ValueError(f"Vector '{vec2}' not found in memory")
            array2 = self.memory.memory_items[vec2].vector
        else:
            array2 = vec2
        
        # Normalize vectors for cosine similarity
        norm1 = np.linalg.norm(array1)
        norm2 = np.linalg.norm(array2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return np.dot(array1, array2) / (norm1 * norm2)
    
    def _normalize_vector(self, vector: np.ndarray) -> np.ndarray:
        """Normalize vector to unit length"""
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector
        return vector / norm
    
    def _make_unitary(self, vector: np.ndarray) -> np.ndarray:
        """Make vector unitary for exact inverse property (Section VIII-C)"""
        # For unitary vectors, normalize in frequency domain to ensure |F[v]| = 1
        fft_v = np.fft.fft(vector)
        # Make all frequency components have unit magnitude
        unitary_fft = np.exp(1j * np.angle(fft_v))
        unitary_vector = np.real(np.fft.ifft(unitary_fft))
        
        if self.memory.normalize:
            unitary_vector = self._normalize_vector(unitary_vector)
            
        return unitary_vector
    
    def _involution(self, vector: np.ndarray) -> np.ndarray:
        """Compute involution of vector: d_i = c_{-i mod n} (Section II-F)"""
        result = np.zeros_like(vector)
        n = len(vector)
        for i in range(n):
            result[i] = vector[(-i) % n]
        return result
    
    def _exact_inverse(self, vector: np.ndarray) -> np.ndarray:
        """Compute exact inverse using involution for unitary vectors"""
        if not self.memory.unitary_vectors:
            return self._involution(vector)
        
        # For unitary vectors, involution gives exact inverse
        return self._involution(vector)
    
    def _add_noise(self, vector: np.ndarray) -> np.ndarray:
        """Add Gaussian noise to vector if noise_level > 0"""
        if self.memory.noise_level > 0:
            noise = np.random.normal(0, self.memory.noise_level, self.memory.vector_dim)
            return vector + noise
        return vector