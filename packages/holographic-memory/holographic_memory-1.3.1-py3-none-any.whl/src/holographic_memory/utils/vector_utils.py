"""
🧮 Vector Utility Functions
==========================

This module provides utility functions for vector operations commonly used
in holographic memory systems, including creation, normalization, and analysis.

Author: Benedict Chen (benedict@benedictchen.com)
"""

import numpy as np
from typing import List, Tuple, Optional, Dict, Any, Union
import warnings


def create_random_vectors(n_vectors: int, 
                         vector_dim: int,
                         distribution: str = 'gaussian',
                         normalize: bool = True,
                         seed: Optional[int] = None) -> np.ndarray:
    """
    Create multiple random vectors with specified distribution.
    
    Parameters
    ----------
    n_vectors : int
        Number of vectors to create
    vector_dim : int
        Dimension of each vector
    distribution : str, default='gaussian'
        Distribution type ('gaussian', 'uniform', 'binary', 'sparse')
    normalize : bool, default=True
        Whether to normalize vectors to unit length
    seed : int, optional
        Random seed for reproducibility
        
    Returns
    -------
    np.ndarray
        Array of shape (n_vectors, vector_dim)
    """
    if seed is not None:
        np.random.seed(seed)
    
    if distribution == 'gaussian':
        vectors = np.random.randn(n_vectors, vector_dim)
    elif distribution == 'uniform':
        vectors = np.random.uniform(-1, 1, (n_vectors, vector_dim))
    elif distribution == 'binary':
        vectors = np.random.choice([-1, 1], (n_vectors, vector_dim))
    elif distribution == 'sparse':
        vectors = np.random.randn(n_vectors, vector_dim)
        # Make 90% of elements zero for sparsity
        mask = np.random.random((n_vectors, vector_dim)) > 0.1
        vectors[~mask] = 0
    else:
        raise ValueError(f"Unknown distribution: {distribution}")
    
    if normalize:
        vectors = normalize_vector(vectors)
    
    return vectors


def normalize_vector(vectors: np.ndarray, 
                    method: str = 'l2',
                    axis: int = -1) -> np.ndarray:
    """
    Normalize vector(s) using specified method.
    
    Parameters
    ----------
    vectors : np.ndarray
        Vector(s) to normalize
    method : str, default='l2'
        Normalization method ('l2', 'l1', 'max', 'unit_variance')
    axis : int, default=-1
        Axis along which to normalize
        
    Returns
    -------
    np.ndarray
        Normalized vector(s)
    """
    if method == 'l2':
        norms = np.linalg.norm(vectors, axis=axis, keepdims=True)
        norms = np.where(norms == 0, 1, norms)  # Avoid division by zero
        return vectors / norms
    
    elif method == 'l1':
        norms = np.sum(np.abs(vectors), axis=axis, keepdims=True)
        norms = np.where(norms == 0, 1, norms)
        return vectors / norms
    
    elif method == 'max':
        max_vals = np.max(np.abs(vectors), axis=axis, keepdims=True)
        max_vals = np.where(max_vals == 0, 1, max_vals)
        return vectors / max_vals
    
    elif method == 'unit_variance':
        mean = np.mean(vectors, axis=axis, keepdims=True)
        std = np.std(vectors, axis=axis, keepdims=True)
        std = np.where(std == 0, 1, std)
        return (vectors - mean) / std
    
    else:
        raise ValueError(f"Unknown normalization method: {method}")


def add_noise(vectors: np.ndarray,
              noise_level: float,
              noise_type: str = 'gaussian') -> np.ndarray:
    """
    Add noise to vector(s).
    
    Parameters
    ----------
    vectors : np.ndarray
        Input vector(s)
    noise_level : float
        Amount of noise to add (0.0 to 1.0)
    noise_type : str, default='gaussian'
        Type of noise ('gaussian', 'uniform', 'salt_pepper')
        
    Returns
    -------
    np.ndarray
        Noisy vector(s)
    """
    if noise_level <= 0:
        return vectors.copy()
    
    shape = vectors.shape
    
    if noise_type == 'gaussian':
        noise = np.random.normal(0, noise_level, shape)
        
    elif noise_type == 'uniform':
        noise = np.random.uniform(-noise_level, noise_level, shape)
        
    elif noise_type == 'salt_pepper':
        noise = np.zeros(shape)
        # Salt noise (set to maximum)
        salt_mask = np.random.random(shape) < noise_level / 2
        noise[salt_mask] = 1.0
        # Pepper noise (set to minimum)
        pepper_mask = np.random.random(shape) < noise_level / 2
        noise[pepper_mask] = -1.0
        
    else:
        raise ValueError(f"Unknown noise type: {noise_type}")
    
    return vectors + noise


def compute_similarity(vector1: np.ndarray,
                      vector2: np.ndarray,
                      metric: str = 'cosine') -> float:
    """
    Compute similarity between two vectors.
    
    Parameters
    ----------
    vector1, vector2 : np.ndarray
        Vectors to compare
    metric : str, default='cosine'
        Similarity metric ('cosine', 'correlation', 'dot', 'euclidean')
        
    Returns
    -------
    float
        Similarity value
    """
    if vector1.shape != vector2.shape:
        raise ValueError("Vectors must have same shape")
    
    if metric == 'cosine':
        norm1 = np.linalg.norm(vector1)
        norm2 = np.linalg.norm(vector2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return np.dot(vector1, vector2) / (norm1 * norm2)
    
    elif metric == 'correlation':
        return np.corrcoef(vector1, vector2)[0, 1]
    
    elif metric == 'dot':
        return np.dot(vector1, vector2)
    
    elif metric == 'euclidean':
        return -np.linalg.norm(vector1 - vector2)  # Negative for similarity
    
    else:
        raise ValueError(f"Unknown similarity metric: {metric}")


def orthogonalize_vectors(vectors: np.ndarray,
                         method: str = 'gram_schmidt') -> np.ndarray:
    """
    Orthogonalize a set of vectors.
    
    Parameters
    ----------
    vectors : np.ndarray
        Array of vectors to orthogonalize (shape: n_vectors, vector_dim)
    method : str, default='gram_schmidt'
        Orthogonalization method ('gram_schmidt', 'qr')
        
    Returns
    -------
    np.ndarray
        Orthogonalized vectors
    """
    if method == 'gram_schmidt':
        orthogonal = np.zeros_like(vectors)
        
        for i in range(len(vectors)):
            orthogonal[i] = vectors[i].copy()
            
            # Subtract projections onto previous orthogonal vectors
            for j in range(i):
                projection = np.dot(orthogonal[i], orthogonal[j]) / np.dot(orthogonal[j], orthogonal[j])
                orthogonal[i] -= projection * orthogonal[j]
            
            # Normalize
            norm = np.linalg.norm(orthogonal[i])
            if norm > 0:
                orthogonal[i] /= norm
        
        return orthogonal
    
    elif method == 'qr':
        Q, R = np.linalg.qr(vectors.T)
        return Q.T
    
    else:
        raise ValueError(f"Unknown orthogonalization method: {method}")


def project_vector(vector: np.ndarray,
                  onto: np.ndarray) -> np.ndarray:
    """
    Project vector onto another vector.
    
    Parameters
    ----------
    vector : np.ndarray
        Vector to project
    onto : np.ndarray
        Vector to project onto
        
    Returns
    -------
    np.ndarray
        Projected vector
    """
    dot_product = np.dot(vector, onto)
    norm_squared = np.dot(onto, onto)
    
    if norm_squared == 0:
        return np.zeros_like(vector)
    
    return (dot_product / norm_squared) * onto


def vector_statistics(vectors: np.ndarray) -> Dict[str, Any]:
    """
    Compute statistics for a collection of vectors.
    
    Parameters
    ----------
    vectors : np.ndarray
        Array of vectors (shape: n_vectors, vector_dim)
        
    Returns
    -------
    Dict[str, Any]
        Dictionary containing vector statistics
    """
    if vectors.ndim == 1:
        vectors = vectors.reshape(1, -1)
    
    n_vectors, vector_dim = vectors.shape
    
    # Basic statistics
    means = np.mean(vectors, axis=0)
    stds = np.std(vectors, axis=0)
    mins = np.min(vectors, axis=0)
    maxs = np.max(vectors, axis=0)
    
    # Norms
    norms = np.linalg.norm(vectors, axis=1)
    
    # Pairwise similarities (sample if too many vectors)
    if n_vectors <= 100:
        similarities = []
        for i in range(n_vectors):
            for j in range(i + 1, n_vectors):
                sim = compute_similarity(vectors[i], vectors[j])
                similarities.append(sim)
        similarities = np.array(similarities)
    else:
        # Sample 1000 random pairs
        indices = np.random.choice(n_vectors, size=(1000, 2), replace=True)
        similarities = []
        for i, j in indices:
            if i != j:
                sim = compute_similarity(vectors[i], vectors[j])
                similarities.append(sim)
        similarities = np.array(similarities)
    
    # Sparsity (fraction of near-zero elements)
    sparsity = np.mean(np.abs(vectors) < 1e-6)
    
    return {
        'n_vectors': n_vectors,
        'vector_dim': vector_dim,
        'mean_values': {
            'mean': np.mean(means),
            'std': np.std(means),
            'min': np.min(means),
            'max': np.max(means)
        },
        'std_values': {
            'mean': np.mean(stds),
            'std': np.std(stds),
            'min': np.min(stds),
            'max': np.max(stds)
        },
        'range_values': {
            'min': np.min(mins),
            'max': np.max(maxs),
            'range': np.max(maxs) - np.min(mins)
        },
        'norms': {
            'mean': np.mean(norms),
            'std': np.std(norms),
            'min': np.min(norms),
            'max': np.max(norms)
        },
        'similarities': {
            'mean': np.mean(similarities) if len(similarities) > 0 else 0.0,
            'std': np.std(similarities) if len(similarities) > 0 else 0.0,
            'min': np.min(similarities) if len(similarities) > 0 else 0.0,
            'max': np.max(similarities) if len(similarities) > 0 else 0.0,
            'n_pairs': len(similarities)
        },
        'sparsity': sparsity,
        'memory_usage_mb': vectors.nbytes / (1024 * 1024)
    }