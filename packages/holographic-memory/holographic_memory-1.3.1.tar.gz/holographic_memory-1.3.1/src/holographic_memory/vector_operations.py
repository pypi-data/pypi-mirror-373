"""
Vector Operations Module for Holographic Memory System

Core vector operations including binding, unbinding, similarity calculations,
and vector generation following Tony Plate's HRR methodology.

Author: Benedict Chen (benedict@benedictchen.com)

# FIXME: Critical Research Accuracy Issues Based on Actual Plate (1995) Paper
#
# 1. MISSING PROPER CIRCULAR CONVOLUTION IMPLEMENTATION (Section II-C, page 625)
#    - Paper specifies: "circular convolution of two vectors of n elements has just n elements"
#    - Current implementation may not handle circular boundary conditions correctly
#    - Missing validation that result maintains fixed dimensionality n
#    - No implementation of compressed outer product interpretation (Figure 4, page 626)
#    - Solutions:
#      a) Implement proper circular convolution: c_j = Σ(k=0 to n-1) a_k * b_{j-k mod n}
#      b) Add validation that output dimension equals input dimensions
#      c) Implement Figure 4's compressed outer product method for verification
#      d) Add mathematical equivalence tests between FFT and direct circular convolution
#    - Research basis: Section II-C "Convolution-Correlation Memories", page 625
#    - CODE REVIEW SUGGESTION:
#      ```python
#      def bind_circular_convolution(self, vec1: np.ndarray, vec2: np.ndarray) -> np.ndarray:
#          """Proper circular convolution binding following Plate (1995) Section II-C"""
#          if len(vec1) != len(vec2):
#              raise ValueError("Vectors must have same length for circular convolution")
#          
#          n = len(vec1)
#          # Ensure vectors follow N(0, 1/n) distribution (Section II-D)
#          vec1_norm = vec1 / np.sqrt(np.sum(vec1**2) / n) if np.sum(vec1**2) > 0 else vec1
#          vec2_norm = vec2 / np.sqrt(np.sum(vec2**2) / n) if np.sum(vec2**2) > 0 else vec2
#          
#          # FFT-based circular convolution (equivalent to direct formula)
#          fft1 = np.fft.fft(vec1_norm)
#          fft2 = np.fft.fft(vec2_norm)
#          result_fft = fft1 * fft2
#          result = np.fft.ifft(result_fft).real
#          
#          # Maintain statistical properties N(0, 1/n)
#          result_var = np.var(result)
#          expected_var = 1.0 / n
#          if result_var > 0:
#              result = result * np.sqrt(expected_var / result_var)
#          
#          # Validation: output dimension should equal input dimension
#          assert len(result) == n, f"Output dimension {len(result)} != input dimension {n}"
#          return result
#      
#      def unbind_circular_correlation(self, bound: np.ndarray, probe: np.ndarray) -> np.ndarray:
#          """Circular correlation unbinding (Section II-E approximate inverse)"""
#          # Involution: d_i = c_{-i mod n}
#          probe_inv = np.concatenate([probe[:1], probe[1:][::-1]])
#          return self.bind_circular_convolution(bound, probe_inv)
#      ```
#
# 2. INCORRECT DISTRIBUTIONAL CONSTRAINTS HANDLING (Section II-D, page 626)
#    - Paper requires: "elements of each vector be independently and identically distributed with mean zero and variance 1/n"
#    - Missing enforcement of N(0,1/n) distribution for vector elements
#    - No validation that vectors have expected Euclidean length of 1
#    - Missing proper random vector generation with correct statistics
#    - Solutions:
#      a) Implement proper random vector generation: elements ~ N(0, 1/n)
#      b) Add vector validation: check mean ≈ 0, variance ≈ 1/n, length ≈ 1
#      c) Provide vector normalization to enforce distributional constraints
#      d) Add discrete distribution option: elements ∈ {±1/√n} with equal probability
#    - Research basis: Section II-D "Distributional Constraints on the Elements of Vectors", page 626
#    - Example validation:
#      ```python
#      mean_check = abs(np.mean(vector)) < 0.1/np.sqrt(n)
#      var_check = abs(np.var(vector) - 1/n) < 0.1/n
#      length_check = abs(np.linalg.norm(vector) - 1.0) < 0.1
#      ```
#
# 3. INADEQUATE CORRELATION AS APPROXIMATE INVERSE (Section II-E, page 626)
#    - Paper states: "circular correlation is an approximate inverse operation"
#    - Missing implementation of involution operation: d_i = c_{-i mod n}
#    - No validation that correlation actually approximates inverse for given vectors
#    - Missing explanation of when correlation fails as inverse
#    - Solutions:
#      a) Implement proper involution: reversed_cue = np.concatenate([cue[:1], cue[1:][::-1]])
#      b) Add correlation quality measurement: similarity(a, (a⊗b)⊘a)
#      c) Provide exact inverse calculation for unitary vectors
#      d) Add warnings when approximate inverse quality is poor
#    - Research basis: Section II-E "Why Correlation Decodes Convolution", page 626
#    - Paper's correlation formula: y = c⊘(c⊗x) where y ≈ x + noise
#
# 4. MISSING UNITARY VECTOR IMPLEMENTATION (Section VIII-C, page 633)
#    - Paper specifies: "unitary vectors" where |fj(x)| = 1 for exact inverse
#    - Missing unitary vector generation and validation
#    - No implementation of exact inverse for unitary vectors
#    - Missing frequency domain magnitude checking
#    - Solutions:
#      a) Generate unitary vectors: phases = random(0, 2π), vector = real(ifft(exp(i*phases)))
#      b) Validate unitary property: all(|fft(vector)| ≈ 1)
#      c) Use exact inverse for unitary vectors: inverse = correlation
#      d) Provide conversion from arbitrary to unitary vectors
#    - Research basis: Section VIII-C "Identities and Approximate and Exact Inverses", page 633
#
# 5. IMPROPER SUPERPOSITION IMPLEMENTATION (Section V, page 628)
#    - Paper uses vector addition for superposition: "create superposition of multiple vectors"
#    - Missing proper normalization after superposition
#    - No handling of interference effects between multiple stored associations
#    - Missing capacity-aware superposition limits
#    - Solutions:
#      a) Implement weighted superposition with normalization
#      b) Add interference analysis between stored vectors
#      c) Enforce capacity limits based on Section IX analysis
#      d) Provide clean-up memory integration for noisy superposition results
#    - Research basis: Section V "Representing More Complex Structure", page 628
#
# 6. MISSING SIMILARITY PRESERVATION PROPERTY (Section II-A, page 624)
#    - Paper states: "preserve similarity. That is, if items a and a' are similar, and items b and b' are similar, then the traces a⊗b and a'⊗b' will also be similar"
#    - No validation or measurement of similarity preservation
#    - Missing similarity metrics for vector operations
#    - No testing of bilinear property preservation
#    - Solutions:
#      a) Implement similarity preservation testing
#      b) Add similarity metrics: cosine similarity, dot product similarity  
#      c) Validate bilinear property: similarity(a⊗b, a'⊗b') ∝ similarity(a,a') * similarity(b,b')
#      d) Provide similarity-based vector matching and retrieval
#    - Research basis: Section II-A "Associative Memories", page 624
#
# 7. INADEQUATE CAPACITY ANALYSIS IMPLEMENTATION (Section IX, page 634)
#    - Paper provides exact capacity formula: k ≥ n/(16 ln²(m/q)) - 2
#    - Missing capacity estimation and validation
#    - No error probability calculation for given parameters
#    - Missing storage optimization based on capacity limits
#    - Solutions:
#      a) Implement exact capacity calculation from Section IX
#      b) Add error probability estimation for retrieval operations
#      c) Provide storage recommendations based on vector dimension and error tolerance
#      d) Add capacity-based performance warnings
#    - Research basis: Section IX "Capacity of Convolution Memories and HRR's", page 634
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
        # FIXME: Critical issues in core binding operation
        # Issue 1: No input validation for array types, shapes, or finite values
        # Issue 2: Redundant vector lookups and type checking for same vectors
        # Issue 3: No numerical stability checking for FFT operations
        # Issue 4: Missing error handling for FFT failures or memory issues
        # Issue 5: Inefficient repeated attribute access and method calls
        
        # FIXME: No input validation for vector properties
        # Issue: Could fail with NaN, Inf, or non-finite values
        # Solutions:
        # 1. Validate vectors are finite and have reasonable magnitude
        # 2. Check for zero-length or malformed arrays
        # 3. Add warnings for very large or very small vector norms
        #
        # Example validation:
        # def _validate_vector(self, vec, name):
        #     if not np.all(np.isfinite(vec)):
        #         raise ValueError(f"Vector {name} contains non-finite values")
        #     if np.linalg.norm(vec) < 1e-12:
        #         warnings.warn(f"Vector {name} has very small norm, may cause numerical issues")
        
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
        
        # FIXME: Inefficient dimension checking
        # Issue: Using len() on potentially multi-dimensional arrays
        # Solutions:
        # 1. Use array.shape to handle multi-dimensional cases
        # 2. Ensure vectors are 1D arrays
        # 3. Add comprehensive shape validation
        #
        # Better validation:
        # if array_a.ndim != 1 or array_b.ndim != 1:
        #     raise ValueError("Vectors must be 1-dimensional arrays")
        # if array_a.shape[0] != array_b.shape[0]:
        #     raise ValueError(f"Vector dimensions must match: {array_a.shape[0]} vs {array_b.shape[0]}")
        
        # Ensure same dimension
        if len(array_a) != len(array_b):
            raise ValueError(f"Vector dimensions must match: {len(array_a)} vs {len(array_b)}")
        
        # FIXME: Conditional unitary transform may break consistency
        # Issue: Applying different transforms to different vectors inconsistently
        # Solutions:
        # 1. Cache unitary transforms to avoid recomputation
        # 2. Apply consistent transformation policies
        # 3. Validate unitary property after transformation
        
        # Apply unitary transform if enabled
        if self.memory.unitary_vectors:
            array_a = self._make_unitary(array_a)
            array_b = self._make_unitary(array_b)
        
        # FIXME: No error handling for FFT operations
        # Issue: FFT can fail with very large arrays or memory issues
        # Solutions:
        # 1. Wrap FFT operations in try-except blocks
        # 2. Check for FFT numerical stability issues
        # 3. Provide fallback to direct convolution for small vectors
        #
        # Robust FFT implementation:
        # try:
        #     fft_a = np.fft.fft(array_a)
        #     fft_b = np.fft.fft(array_b)
        # except (MemoryError, np.linalg.LinAlgError) as e:
        #     if len(array_a) < 64:  # Use direct convolution for small vectors
        #         return self._direct_circular_convolution(array_a, array_b)
        #     else:
        #         raise RuntimeError(f"FFT operation failed: {e}")
        
        # Circular convolution using FFT (efficient implementation)
        fft_a = np.fft.fft(array_a)
        fft_b = np.fft.fft(array_b)
        
        # Element-wise multiplication in frequency domain = convolution in time domain
        fft_result = fft_a * fft_b
        
        # FIXME: No numerical stability checking in FFT inverse
        # Issue: IFFT can produce small imaginary components due to numerical errors
        # Solutions:
        # 1. Check magnitude of imaginary part and warn if significant
        # 2. Use real FFT (rfft) for real-valued inputs
        # 3. Add tolerance for near-zero imaginary components
        #
        # Stable IFFT:
        # result_complex = np.fft.ifft(fft_result)
        # if np.max(np.abs(np.imag(result_complex))) > 1e-10:
        #     warnings.warn("Significant imaginary components in IFFT result")
        # result = np.real(result_complex)
        
        # Convert back to time domain
        result = np.real(np.fft.ifft(fft_result))
        
        # Add noise if specified
        result = self._add_noise(result)
        
        # Normalize if enabled
        if self.memory.normalize:
            result = self._normalize_vector(result)
        
        # FIXME: Association count increment may not be thread-safe
        # Issue: In multi-threaded environments, this could cause race conditions
        # Solutions:
        # 1. Use atomic operations or locks for thread safety
        # 2. Make association counting optional or configurable
        # 3. Use proper concurrency primitives
        
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
        # FIXME: Extremely inefficient O(n) loop for involution operation
        # Issue 1: Using explicit loop instead of vectorized numpy operations
        # Issue 2: No input validation for vector properties
        # Issue 3: Inefficient memory allocation with zeros_like
        # Issue 4: Could be optimized to O(1) memory with slicing
        
        # FIXME: No input validation
        # Issue: Could fail with empty arrays or non-1D arrays
        # Solutions:
        # 1. Validate vector is 1D and non-empty
        # 2. Check for finite values
        # 3. Handle edge cases (single element, etc.)
        #
        # Example validation:
        # if vector.ndim != 1:
        #     raise ValueError("Vector must be 1-dimensional")
        # if len(vector) == 0:
        #     return np.array([])
        
        # FIXME: Inefficient explicit loop - can be vectorized
        # Issue: O(n) loop with individual index calculations is slow
        # Solutions:
        # 1. Use numpy array slicing for much faster operation
        # 2. Leverage numpy's advanced indexing capabilities
        # 3. Use concatenation and slicing for O(1) memory
        #
        # Efficient implementation:
        # n = len(vector)
        # if n == 0:
        #     return np.array([])
        # elif n == 1:
        #     return vector.copy()
        # else:
        #     # Vectorized involution: [v[0], v[-1], v[-2], ..., v[1]]
        #     return np.concatenate([vector[:1], vector[-1:0:-1]])
        
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