"""
🔄 HRR Operations - Core Holographic Operations
==============================================

This module implements the fundamental operations for Holographic Reduced
Representations (HRR), including circular convolution binding, correlation
unbinding, and vector composition operations.

Based on Plate (1995) "Holographic Reduced Representations".

Author: Benedict Chen (benedict@benedictchen.com)
"""

import numpy as np
from typing import List, Optional, Union, Dict, Any
from dataclasses import dataclass
import warnings


@dataclass
class HRRVector:
    """
    🌀 Holographic Reduced Representation Vector
    
    Represents a vector in the HRR space with metadata and operations.
    
    Attributes
    ----------
    data : np.ndarray
        The actual vector data
    name : str, optional
        Name identifier for the vector
    is_bound : bool, default=False
        Whether this vector represents a bound structure
    metadata : dict, optional
        Additional metadata about the vector
    """
    data: np.ndarray
    name: Optional[str] = None
    is_bound: bool = False
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        
        # Ensure data is numpy array
        if not isinstance(self.data, np.ndarray):
            self.data = np.array(self.data)
    
    @property
    def dimension(self) -> int:
        """Get vector dimension."""
        return len(self.data)
    
    @property
    def norm(self) -> float:
        """Get vector norm."""
        return np.linalg.norm(self.data)
    
    def normalize(self) -> 'HRRVector':
        """Return normalized copy of vector."""
        norm = self.norm
        if norm > 0:
            normalized_data = self.data / norm
        else:
            normalized_data = self.data.copy()
        
        return HRRVector(
            data=normalized_data,
            name=self.name,
            is_bound=self.is_bound,
            metadata=self.metadata.copy()
        )
    
    def similarity(self, other: 'HRRVector') -> float:
        """Compute cosine similarity with another HRR vector."""
        if len(self.data) != len(other.data):
            raise ValueError("Vectors must have same dimension")
        
        norm_self = self.norm
        norm_other = other.norm
        
        if norm_self == 0 or norm_other == 0:
            return 0.0
        
        return np.dot(self.data, other.data) / (norm_self * norm_other)
    
    def __add__(self, other: 'HRRVector') -> 'HRRVector':
        """Vector addition (superposition)."""
        return HRRVector(
            data=self.data + other.data,
            name=f"({self.name or 'vec'}+{other.name or 'vec'})",
            metadata={'operation': 'addition', 'operands': [self.name, other.name]}
        )
    
    def __mul__(self, scalar: float) -> 'HRRVector':
        """Scalar multiplication."""
        return HRRVector(
            data=self.data * scalar,
            name=f"{scalar}*{self.name or 'vec'}",
            metadata={'operation': 'scaling', 'scalar': scalar, 'original': self.name}
        )
    
    def __repr__(self) -> str:
        return f"HRRVector(name='{self.name}', dim={self.dimension}, norm={self.norm:.3f})"


class HRROperations:
    """
    🔄 Core HRR Operations Class
    
    Implements the fundamental operations for Holographic Reduced Representations,
    including binding through circular convolution and unbinding through correlation.
    
    Parameters
    ----------
    vector_dim : int, default=512
        Dimension of HRR vectors
    normalize : bool, default=True
        Whether to normalize vectors after operations
    noise_level : float, default=0.0
        Amount of noise to add for robustness testing
    """
    
    def __init__(self,
                 vector_dim: int = 512,
                 normalize: bool = True,
                 noise_level: float = 0.0):
        
        self.vector_dim = vector_dim
        self.normalize = normalize
        self.noise_level = noise_level
        
        # Operation statistics
        self.stats = {
            'bind_operations': 0,
            'unbind_operations': 0,
            'compose_operations': 0,
            'normalize_operations': 0
        }
    
    def bind(self, 
             role: HRRVector, 
             filler: HRRVector) -> HRRVector:
        """
        Bind two vectors using circular convolution.
        
        Implements the core HRR binding operation using circular convolution
        to create a compressed representation that preserves relational structure.
        
        Parameters
        ----------
        role : HRRVector
            Role vector (what to bind)
        filler : HRRVector
            Filler vector (what to bind it to)
            
        Returns
        -------
        HRRVector
            Bound vector using circular convolution
        """
        if len(role.data) != len(filler.data):
            raise ValueError("Role and filler vectors must have same dimension")
        
        # Perform circular convolution using FFT
        role_fft = np.fft.fft(role.data)
        filler_fft = np.fft.fft(filler.data)
        
        # Convolution in frequency domain is element-wise multiplication
        bound_fft = role_fft * filler_fft
        bound_data = np.fft.ifft(bound_fft).real
        
        # Add noise if specified
        if self.noise_level > 0:
            noise = np.random.normal(0, self.noise_level, len(bound_data))
            bound_data += noise
        
        # Normalize if specified
        if self.normalize:
            norm = np.linalg.norm(bound_data)
            if norm > 0:
                bound_data = bound_data / norm
        
        # Create bound vector
        bound_vector = HRRVector(
            data=bound_data,
            name=f"{role.name or 'role'}⊛{filler.name or 'filler'}",
            is_bound=True,
            metadata={
                'operation': 'binding',
                'method': 'circular_convolution',
                'role': role.name,
                'filler': filler.name,
                'noise_level': self.noise_level
            }
        )
        
        self.stats['bind_operations'] += 1
        return bound_vector
    
    def unbind(self,
               bound_vector: HRRVector,
               role: HRRVector) -> HRRVector:
        """
        Unbind a vector using circular correlation.
        
        Retrieves the filler from a bound representation using circular
        correlation (inverse of convolution).
        
        Parameters
        ----------
        bound_vector : HRRVector
            The bound vector to unbind from
        role : HRRVector
            The role vector used for unbinding
            
        Returns
        -------
        HRRVector
            The unbound filler vector (potentially noisy)
        """
        if len(bound_vector.data) != len(role.data):
            raise ValueError("Bound and role vectors must have same dimension")
        
        # Perform circular correlation using FFT
        bound_fft = np.fft.fft(bound_vector.data)
        role_fft = np.fft.fft(role.data)
        
        # Correlation in frequency domain is conjugate multiplication
        role_fft_conj = np.conj(role_fft)
        
        # Avoid division by zero in frequency domain
        denominator = np.abs(role_fft)**2
        safe_denominator = np.where(denominator > 1e-12, denominator, 1e-12)
        
        unbound_fft = bound_fft * role_fft_conj / safe_denominator
        unbound_data = np.fft.ifft(unbound_fft).real
        
        # Add noise if specified
        if self.noise_level > 0:
            noise = np.random.normal(0, self.noise_level, len(unbound_data))
            unbound_data += noise
        
        # Normalize if specified
        if self.normalize:
            norm = np.linalg.norm(unbound_data)
            if norm > 0:
                unbound_data = unbound_data / norm
        
        # Create unbound vector
        unbound_vector = HRRVector(
            data=unbound_data,
            name=f"unbound({bound_vector.name or 'bound'}, {role.name or 'role'})",
            is_bound=False,
            metadata={
                'operation': 'unbinding',
                'method': 'circular_correlation',
                'bound_vector': bound_vector.name,
                'role': role.name,
                'noise_level': self.noise_level
            }
        )
        
        self.stats['unbind_operations'] += 1
        return unbound_vector
    
    def compose(self,
                vectors: List[HRRVector],
                weights: Optional[List[float]] = None) -> HRRVector:
        """
        Compose multiple vectors using weighted superposition.
        
        Parameters
        ----------
        vectors : List[HRRVector]
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
        
        if weights is None:
            weights = [1.0 / len(vectors)] * len(vectors)
        elif len(weights) != len(vectors):
            raise ValueError("Number of weights must match number of vectors")
        
        # Check dimension consistency
        dim = len(vectors[0].data)
        for i, vec in enumerate(vectors[1:], 1):
            if len(vec.data) != dim:
                raise ValueError(f"Vector {i} has dimension {len(vec.data)}, expected {dim}")
        
        # Weighted superposition
        composed_data = np.zeros(dim)
        for weight, vector in zip(weights, vectors):
            composed_data += weight * vector.data
        
        # Add noise if specified
        if self.noise_level > 0:
            noise = np.random.normal(0, self.noise_level, len(composed_data))
            composed_data += noise
        
        # Normalize if specified
        if self.normalize:
            norm = np.linalg.norm(composed_data)
            if norm > 0:
                composed_data = composed_data / norm
        
        # Create composed vector
        vector_names = [v.name for v in vectors if v.name]
        composed_vector = HRRVector(
            data=composed_data,
            name=f"compose({'+'.join(vector_names[:3])}{'...' if len(vector_names) > 3 else ''})",
            metadata={
                'operation': 'composition',
                'method': 'weighted_superposition',
                'num_vectors': len(vectors),
                'weights': weights,
                'component_names': vector_names
            }
        )
        
        self.stats['compose_operations'] += 1
        return composed_vector
    
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
        # Extract data arrays
        data1 = vector1.data if isinstance(vector1, HRRVector) else vector1
        data2 = vector2.data if isinstance(vector2, HRRVector) else vector2
        
        if len(data1) != len(data2):
            raise ValueError("Vectors must have same dimension")
        
        # Compute cosine similarity
        norm1 = np.linalg.norm(data1)
        norm2 = np.linalg.norm(data2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return np.dot(data1, data2) / (norm1 * norm2)
    
    def normalize(self, vector: HRRVector) -> HRRVector:
        """
        Normalize a vector to unit length.
        
        Parameters
        ----------
        vector : HRRVector
            Vector to normalize
            
        Returns
        -------
        HRRVector
            Normalized vector
        """
        normalized = vector.normalize()
        self.stats['normalize_operations'] += 1
        return normalized
    
    def create_random_vector(self, 
                           name: Optional[str] = None,
                           distribution: str = 'gaussian') -> HRRVector:
        """
        Create a random HRR vector.
        
        Parameters
        ----------
        name : str, optional
            Name for the vector
        distribution : str, default='gaussian'
            Distribution type ('gaussian', 'uniform', 'binary')
            
        Returns
        -------
        HRRVector
            Random HRR vector
        """
        if distribution == 'gaussian':
            data = np.random.randn(self.vector_dim)
        elif distribution == 'uniform':
            data = np.random.uniform(-1, 1, self.vector_dim)
        elif distribution == 'binary':
            data = np.random.choice([-1, 1], self.vector_dim)
        else:
            raise ValueError(f"Unknown distribution: {distribution}")
        
        # Normalize if specified
        if self.normalize:
            norm = np.linalg.norm(data)
            if norm > 0:
                data = data / norm
        
        return HRRVector(
            data=data,
            name=name or f"random_{distribution}",
            metadata={'distribution': distribution}
        )
    
    def permute_vector(self, vector: HRRVector, permutation: Optional[np.ndarray] = None) -> HRRVector:
        """
        Permute a vector (useful for creating role vectors).
        
        Parameters
        ----------
        vector : HRRVector
            Vector to permute
        permutation : np.ndarray, optional
            Permutation indices (random if not provided)
            
        Returns
        -------
        HRRVector
            Permuted vector
        """
        if permutation is None:
            permutation = np.random.permutation(len(vector.data))
        
        permuted_data = vector.data[permutation]
        
        return HRRVector(
            data=permuted_data,
            name=f"perm({vector.name or 'vec'})",
            metadata={
                'operation': 'permutation',
                'original': vector.name,
                'permutation': permutation.tolist()
            }
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get operation statistics.
        
        Returns
        -------
        Dict[str, Any]
            Statistics dictionary
        """
        stats = self.stats.copy()
        stats.update({
            'vector_dim': self.vector_dim,
            'normalize': self.normalize,
            'noise_level': self.noise_level,
            'total_operations': sum(self.stats.values())
        })
        return stats
    
    def reset_statistics(self):
        """Reset operation statistics."""
        for key in self.stats:
            self.stats[key] = 0