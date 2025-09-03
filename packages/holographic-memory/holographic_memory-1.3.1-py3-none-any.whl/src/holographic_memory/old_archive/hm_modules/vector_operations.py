"""
Vector Operations Module for Holographic Memory System

Core vector operations including binding, unbinding, similarity calculations,
and vector generation following Tony Plate's HRR methodology.

Author: Benedict Chen (benedict@benedictchen.com)
"""

import numpy as np
from typing import Union, List
from scipy.fft import fft, ifft
from .configuration import HRRConfig


class VectorOperations:
    """Core vector operations for holographic reduced representations"""
    
    def __init__(self, config: HRRConfig):
        """Initialize vector operations with configuration"""
        self.config = config
        
        # Precompute FFT frequencies for efficiency
        self._fft_freqs = np.fft.fftfreq(config.vector_dim)
        
        # Set random seed if specified
        if config.random_seed is not None:
            np.random.seed(config.random_seed)
    
    def generate_random_vector(self, name: str = None) -> np.ndarray:
        """
        Generate random HRR vector with proper distribution
        
        Parameters:
        -----------
        name : str, optional
            Name for the vector (for debugging/tracking)
        
        Returns:
        --------
        vector : np.ndarray
            Random vector with appropriate distribution
        """
        if self.config.unitary_vectors:
            # Generate unitary vector (for exact unbinding)
            vector = self._generate_unitary_vector()
        else:
            # Standard Gaussian distribution (Plate 1995)
            vector = np.random.normal(0, 1/np.sqrt(self.config.vector_dim), 
                                    self.config.vector_dim)
        
        # Normalize if enabled
        if self.config.normalize:
            vector = self.normalize_vector(vector)
        
        return vector
    
    def _generate_unitary_vector(self) -> np.ndarray:
        """Generate unitary vector for exact unbinding"""
        # Generate random phases
        phases = np.random.uniform(0, 2*np.pi, self.config.vector_dim)
        
        # Create complex exponentials and take real part of IFFT
        complex_vector = np.exp(1j * phases)
        real_vector = np.real(ifft(complex_vector))
        
        return real_vector
    
    def normalize_vector(self, vector: np.ndarray) -> np.ndarray:
        """Normalize vector to unit length"""
        norm = np.linalg.norm(vector)
        return vector / norm if norm > 1e-10 else vector
    
    def bind(self, vec_a: np.ndarray, vec_b: np.ndarray) -> np.ndarray:
        """
        Circular convolution binding operation (⊗)
        
        The fundamental operation of HRR that combines two vectors into one.
        Properties: approximately commutative, distributes over superposition.
        
        # FIXME: Critical Implementation Issues in bind() - Core HRR Operation
        #
        # 1. INCORRECT FFT HANDLING FOR NON-POWER-OF-2 DIMENSIONS
        #    - FFT is most efficient for power-of-2 dimensions
        #    - Current implementation doesn't pad or warn about inefficient dimensions
        #    - May introduce numerical artifacts for arbitrary dimensions
        #    - Solutions:
        #      a) Add dimension validation: warn if not power of 2
        #      b) Implement zero-padding for FFT efficiency
        #      c) Use different algorithms for small non-power-of-2 vectors
        #    - Research note: Plate (1995) typically used dimensions like 256, 512, 1024
        #    - Example:
        #      ```python
        #      if not (self.config.vector_dim & (self.config.vector_dim - 1)) == 0:
        #          warnings.warn("Vector dimension is not power of 2, FFT may be inefficient")
        #      ```
        #
        # 2. MISSING NUMERICAL STABILITY CHECKS
        #    - No handling of FFT numerical precision issues
        #    - Complex-to-real conversion may introduce small imaginary components
        #    - Missing validation that result is actually real
        #    - Solutions:
        #      a) Add numerical precision threshold: np.real() with tolerance check
        #      b) Validate imaginary components are negligible: assert np.max(np.imag(fft_result)) < 1e-10
        #      c) Implement high-precision binding for critical applications
        #    - Example:
        #      ```python
        #      complex_result = ifft(fft(vec_a) * fft(vec_b))
        #      if np.max(np.abs(np.imag(complex_result))) > 1e-12:
        #          warnings.warn("Significant imaginary component in binding result")
        #      result = np.real(complex_result)
        #      ```
        #
        # 3. NO BINDING STRENGTH OR WEIGHTING
        #    - All bindings have equal strength regardless of semantic importance
        #    - Missing weighted binding for hierarchical structures
        #    - No confidence or salience parameters
        #    - Solutions:
        #      a) Add binding_weight parameter: result *= weight
        #      b) Implement semantic distance-based weighting
        #      c) Add contextual binding strength modulation
        #    - Research basis: Cognitive systems have variable binding strengths
        #
        # 4. MISSING COMMUTATIVITY VALIDATION
        #    - HRR binding should be approximately commutative: a⊗b ≈ b⊗a
        #    - No validation or measurement of commutativity error
        #    - Should track and report binding quality metrics
        #    - Solutions:
        #      a) Add commutativity test: similarity(bind(a,b), bind(b,a))
        #      b) Track binding quality metrics over time
        #      c) Implement binding diagnostics for debugging
        #    - Critical for validating HRR implementation correctness
        
        Parameters:
        -----------
        vec_a, vec_b : np.ndarray
            Input vectors to bind
        
        Returns:
        --------
        result : np.ndarray
            Bound vector (a ⊗ b)
        """
        if len(vec_a) != len(vec_b):
            raise ValueError("Vectors must have same dimension")
        
        if self.config.binding_operation == 'circular_convolution':
            # Standard HRR binding using FFT for efficiency
            result = np.real(ifft(fft(vec_a) * fft(vec_b)))
        elif self.config.binding_operation == 'walsh_hadamard':
            # Walsh-Hadamard binding (alternative approach)
            result = self._walsh_hadamard_bind(vec_a, vec_b)
        else:
            raise ValueError(f"Unknown binding operation: {self.config.binding_operation}")
        
        # Add noise if specified
        if self.config.noise_level > 0:
            noise = np.random.normal(0, self.config.noise_level, len(result))
            result += noise
            
        # Normalize if enabled
        if self.config.normalize:
            result = self.normalize_vector(result)
            
        return result
    
    def unbind(self, bound_vec: np.ndarray, cue_vec: np.ndarray) -> np.ndarray:
        """
        Circular correlation unbinding operation (⊘)
        
        Retrieves information from a bound vector using a cue.
        If bound_vec = a ⊗ b, then bound_vec ⊘ a ≈ b (with noise).
        
        Parameters:
        -----------
        bound_vec : np.ndarray
            Vector containing bound information
        cue_vec : np.ndarray
            Cue vector for unbinding
        
        Returns:
        --------
        result : np.ndarray
            Unbound vector approximating the target
        """
        if len(bound_vec) != len(cue_vec):
            raise ValueError("Vectors must have same dimension")
        
        if self.config.binding_operation == 'circular_convolution':
            # Standard HRR unbinding - correlation is convolution with reversed vector
            reversed_cue = np.concatenate([cue_vec[:1], cue_vec[1:][::-1]])
            result = np.real(ifft(fft(bound_vec) * fft(reversed_cue)))
        elif self.config.binding_operation == 'walsh_hadamard':
            # Walsh-Hadamard unbinding (same as binding)
            result = self._walsh_hadamard_bind(bound_vec, cue_vec)
        else:
            raise ValueError(f"Unknown binding operation: {self.config.binding_operation}")
            
        return result
    
    def superpose(self, vectors: List[np.ndarray], normalize: bool = True) -> np.ndarray:
        """
        Create superposition of multiple vectors (+)
        
        Combines multiple vectors through addition. This preserves the 
        ability to retrieve any component vector later.
        
        Parameters:
        -----------
        vectors : List[np.ndarray]
            List of vectors to superpose
        normalize : bool, default=True
            Whether to normalize the result
        
        Returns:
        --------
        result : np.ndarray
            Superposition of input vectors
        """
        if not vectors:
            return np.zeros(self.config.vector_dim)
            
        # Validate all vectors have same dimension
        for i, vec in enumerate(vectors):
            if len(vec) != self.config.vector_dim:
                raise ValueError(f"Vector {i} has wrong dimension: {len(vec)} != {self.config.vector_dim}")
        
        # Sum all vectors
        result = np.sum(vectors, axis=0)
            
        # Normalize if requested
        if normalize and self.config.normalize:
            result = self.normalize_vector(result)
            
        return result
    
    def similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate similarity between vectors (dot product for normalized vectors)
        
        Parameters:
        -----------
        vec1, vec2 : np.ndarray
            Vectors to compare
        
        Returns:
        --------
        similarity : float
            Similarity score (cosine similarity if normalized)
        """
        if len(vec1) != len(vec2):
            raise ValueError("Vectors must have same dimension")
        
        # Normalize for similarity calculation
        if self.config.normalize or self.config.similarity_preservation:
            vec1 = self.normalize_vector(vec1)
            vec2 = self.normalize_vector(vec2)
            
        return float(np.dot(vec1, vec2))
    
    def _walsh_hadamard_bind(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Walsh-Hadamard binding (element-wise multiplication after transform)"""
        # This is a simplified version - full Walsh-Hadamard requires power-of-2 dimensions
        return a * b  # Element-wise multiplication
    
    def create_analogy_vector(self, vec_a: np.ndarray, vec_b: np.ndarray, 
                             vec_c: np.ndarray) -> np.ndarray:
        """
        Create analogical reasoning vector: a:b :: c:?
        
        Uses the formula: result ≈ (b ⊘ a) ⊗ c
        
        Parameters:
        -----------
        vec_a, vec_b : np.ndarray
            Source analogy pair (a:b)
        vec_c : np.ndarray
            Target input for analogy
        
        Returns:
        --------
        result : np.ndarray
            Analogical result vector
        """
        # Extract relation from a:b
        relation = self.unbind(vec_b, vec_a)  # b ⊘ a
        
        # Apply relation to c
        result = self.bind(relation, vec_c)   # relation ⊗ c
        
        return result
    
    def calculate_vector_statistics(self, vector: np.ndarray) -> dict:
        """Calculate statistics for a vector"""
        return {
            'mean': float(np.mean(vector)),
            'std': float(np.std(vector)),
            'norm': float(np.linalg.norm(vector)),
            'min': float(np.min(vector)),
            'max': float(np.max(vector)),
            'sparsity': float(np.sum(np.abs(vector) < 1e-10) / len(vector))
        }
    
    def validate_vector(self, vector: np.ndarray, name: str = "vector") -> bool:
        """
        Validate that a vector meets HRR requirements
        
        Parameters:
        -----------
        vector : np.ndarray
            Vector to validate
        name : str
            Name for error reporting
        
        Returns:
        --------
        valid : bool
            True if vector is valid
        
        Raises:
        -------
        ValueError
            If vector is invalid
        """
        if not isinstance(vector, np.ndarray):
            raise ValueError(f"{name} must be numpy array")
        
        if len(vector) != self.config.vector_dim:
            raise ValueError(f"{name} has wrong dimension: {len(vector)} != {self.config.vector_dim}")
        
        if not np.isfinite(vector).all():
            raise ValueError(f"{name} contains non-finite values")
        
        norm = np.linalg.norm(vector)
        if norm < 1e-10:
            raise ValueError(f"{name} has near-zero norm")
        
        return True