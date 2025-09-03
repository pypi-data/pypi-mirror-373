"""
✅ Validation Utility Functions
=============================

This module provides validation functions for input parameters, configurations,
and data integrity in the holographic memory system.

Author: Benedict Chen (benedict@benedictchen.com)
"""

import numpy as np
from typing import Any, Optional, Union, List, Dict, Tuple
import warnings


def validate_vector_dimension(vector: Union[np.ndarray, List], 
                            expected_dim: Optional[int] = None,
                            min_dim: int = 1,
                            max_dim: int = 100000) -> bool:
    """
    Validate vector dimension constraints.
    
    Parameters
    ----------
    vector : np.ndarray or List
        Vector to validate
    expected_dim : int, optional
        Expected dimension (if specified)
    min_dim : int, default=1
        Minimum allowed dimension
    max_dim : int, default=100000
        Maximum allowed dimension
        
    Returns
    -------
    bool
        True if valid
        
    Raises
    ------
    ValueError
        If validation fails
    """
    if not isinstance(vector, (np.ndarray, list)):
        raise ValueError(f"Vector must be numpy array or list, got {type(vector)}")
    
    if isinstance(vector, list):
        vector = np.array(vector)
    
    if vector.ndim != 1:
        raise ValueError(f"Vector must be 1-dimensional, got shape {vector.shape}")
    
    dim = len(vector)
    
    if dim < min_dim:
        raise ValueError(f"Vector dimension {dim} below minimum {min_dim}")
    
    if dim > max_dim:
        raise ValueError(f"Vector dimension {dim} exceeds maximum {max_dim}")
    
    if expected_dim is not None and dim != expected_dim:
        raise ValueError(f"Vector dimension {dim} does not match expected {expected_dim}")
    
    return True


def validate_similarity_range(similarity: float,
                            min_val: float = -1.0,
                            max_val: float = 1.0,
                            allow_nan: bool = False) -> bool:
    """
    Validate similarity value is in expected range.
    
    Parameters
    ----------
    similarity : float
        Similarity value to validate
    min_val : float, default=-1.0
        Minimum allowed value
    max_val : float, default=1.0
        Maximum allowed value
    allow_nan : bool, default=False
        Whether to allow NaN values
        
    Returns
    -------
    bool
        True if valid
        
    Raises
    ------
    ValueError
        If validation fails
    """
    if not isinstance(similarity, (int, float, np.number)):
        raise ValueError(f"Similarity must be numeric, got {type(similarity)}")
    
    if np.isnan(similarity):
        if not allow_nan:
            raise ValueError("Similarity value is NaN")
        return True
    
    if np.isinf(similarity):
        raise ValueError("Similarity value is infinite")
    
    if similarity < min_val or similarity > max_val:
        raise ValueError(f"Similarity {similarity} outside range [{min_val}, {max_val}]")
    
    return True


def validate_memory_capacity(capacity: Optional[int],
                           min_capacity: int = 1,
                           max_capacity: int = 1000000) -> bool:
    """
    Validate memory capacity parameter.
    
    Parameters
    ----------
    capacity : int or None
        Memory capacity to validate
    min_capacity : int, default=1
        Minimum allowed capacity
    max_capacity : int, default=1000000
        Maximum allowed capacity
        
    Returns
    -------
    bool
        True if valid
        
    Raises
    ------
    ValueError
        If validation fails
    """
    if capacity is None:
        return True
    
    if not isinstance(capacity, (int, np.integer)):
        raise ValueError(f"Capacity must be integer or None, got {type(capacity)}")
    
    if capacity < min_capacity:
        raise ValueError(f"Capacity {capacity} below minimum {min_capacity}")
    
    if capacity > max_capacity:
        raise ValueError(f"Capacity {capacity} exceeds maximum {max_capacity}")
    
    return True


def validate_config_consistency(config: Dict[str, Any]) -> bool:
    """
    Validate configuration for internal consistency.
    
    Parameters
    ----------
    config : Dict[str, Any]
        Configuration dictionary to validate
        
    Returns
    -------
    bool
        True if consistent
        
    Raises
    ------
    ValueError
        If inconsistencies found
    """
    issues = []
    
    # Check vector dimension consistency
    vector_dim = config.get('vector_dim')
    if vector_dim is not None:
        if not isinstance(vector_dim, (int, np.integer)) or vector_dim <= 0:
            issues.append(f"Invalid vector_dim: {vector_dim}")
    
    # Check normalization settings
    normalize = config.get('normalize', True)
    noise_level = config.get('noise_level', 0.0)
    if normalize and noise_level > 0.5:
        warnings.warn("High noise level with normalization may cause instability")
    
    # Check cleanup settings
    cleanup_threshold = config.get('cleanup_threshold')
    if cleanup_threshold is not None:
        if not 0 <= cleanup_threshold <= 1:
            issues.append(f"cleanup_threshold {cleanup_threshold} not in [0, 1]")
    
    max_iterations = config.get('max_cleanup_iterations')
    if max_iterations is not None:
        if not isinstance(max_iterations, (int, np.integer)) or max_iterations < 1:
            issues.append(f"Invalid max_cleanup_iterations: {max_iterations}")
    
    # Check capacity settings
    capacity = config.get('capacity_threshold')
    if capacity is not None:
        validate_memory_capacity(capacity)
    
    # Check noise level
    if noise_level is not None:
        if not 0 <= noise_level <= 1:
            issues.append(f"noise_level {noise_level} not in [0, 1]")
    
    if issues:
        raise ValueError("Configuration issues found: " + "; ".join(issues))
    
    return True


def check_vector_properties(vector: np.ndarray,
                          check_finite: bool = True,
                          check_norm: bool = False,
                          expected_norm: Optional[float] = None,
                          norm_tolerance: float = 1e-6) -> Dict[str, Any]:
    """
    Check various properties of a vector and return diagnostics.
    
    Parameters
    ----------
    vector : np.ndarray
        Vector to check
    check_finite : bool, default=True
        Whether to check for finite values
    check_norm : bool, default=False
        Whether to check vector norm
    expected_norm : float, optional
        Expected norm value
    norm_tolerance : float, default=1e-6
        Tolerance for norm comparison
        
    Returns
    -------
    Dict[str, Any]
        Dictionary of property check results
    """
    results = {
        'is_valid': True,
        'issues': [],
        'properties': {}
    }
    
    # Basic properties
    results['properties'].update({
        'shape': vector.shape,
        'dtype': str(vector.dtype),
        'size': vector.size,
        'norm': np.linalg.norm(vector),
        'min': np.min(vector),
        'max': np.max(vector),
        'mean': np.mean(vector),
        'std': np.std(vector)
    })
    
    # Check for finite values
    if check_finite:
        n_nan = np.sum(np.isnan(vector))
        n_inf = np.sum(np.isinf(vector))
        
        results['properties']['n_nan'] = n_nan
        results['properties']['n_inf'] = n_inf
        
        if n_nan > 0:
            results['is_valid'] = False
            results['issues'].append(f"{n_nan} NaN values found")
        
        if n_inf > 0:
            results['is_valid'] = False
            results['issues'].append(f"{n_inf} infinite values found")
    
    # Check norm
    if check_norm or expected_norm is not None:
        norm = results['properties']['norm']
        
        if norm == 0:
            results['issues'].append("Vector has zero norm")
            if expected_norm != 0:
                results['is_valid'] = False
        
        if expected_norm is not None:
            norm_diff = abs(norm - expected_norm)
            results['properties']['norm_difference'] = norm_diff
            
            if norm_diff > norm_tolerance:
                results['is_valid'] = False
                results['issues'].append(
                    f"Norm {norm:.6f} differs from expected {expected_norm:.6f} "
                    f"by {norm_diff:.6f} (tolerance: {norm_tolerance:.6f})"
                )
    
    # Check for sparsity
    zero_threshold = 1e-12
    n_zeros = np.sum(np.abs(vector) < zero_threshold)
    sparsity = n_zeros / len(vector)
    results['properties']['sparsity'] = sparsity
    results['properties']['n_zeros'] = n_zeros
    
    # Check for unusual distributions
    if len(vector) > 10:
        # Kolmogorov-Smirnov test against normal distribution
        try:
            from scipy import stats
            normalized_vector = (vector - np.mean(vector)) / max(np.std(vector), 1e-12)
            ks_stat, ks_pval = stats.kstest(normalized_vector, 'norm')
            results['properties']['normality_test'] = {
                'ks_statistic': ks_stat,
                'p_value': ks_pval,
                'is_normal': ks_pval > 0.05
            }
        except ImportError:
            pass
    
    return results


def sanitize_inputs(**kwargs) -> Dict[str, Any]:
    """
    Sanitize and validate input parameters.
    
    Parameters
    ----------
    **kwargs : dict
        Input parameters to sanitize
        
    Returns
    -------
    Dict[str, Any]
        Sanitized parameters
        
    Raises
    ------
    ValueError
        If inputs cannot be sanitized
    """
    sanitized = {}
    
    for key, value in kwargs.items():
        
        if key == 'vector_dim':
            if not isinstance(value, (int, np.integer)):
                raise ValueError(f"vector_dim must be integer, got {type(value)}")
            if value <= 0:
                raise ValueError(f"vector_dim must be positive, got {value}")
            sanitized[key] = int(value)
        
        elif key == 'normalize':
            sanitized[key] = bool(value)
        
        elif key in ['noise_level', 'cleanup_threshold']:
            if not isinstance(value, (int, float, np.number)):
                raise ValueError(f"{key} must be numeric, got {type(value)}")
            value = float(value)
            if not 0 <= value <= 1:
                raise ValueError(f"{key} must be in [0, 1], got {value}")
            sanitized[key] = value
        
        elif key == 'capacity_threshold':
            if value is not None:
                if not isinstance(value, (int, np.integer)):
                    raise ValueError(f"{key} must be integer or None, got {type(value)}")
                if value <= 0:
                    raise ValueError(f"{key} must be positive, got {value}")
                sanitized[key] = int(value)
            else:
                sanitized[key] = None
        
        elif key in ['max_cleanup_iterations', 'max_iterations']:
            if not isinstance(value, (int, np.integer)):
                raise ValueError(f"{key} must be integer, got {type(value)}")
            if value <= 0:
                raise ValueError(f"{key} must be positive, got {value}")
            sanitized[key] = int(value)
        
        elif key == 'convergence_threshold':
            if not isinstance(value, (int, float, np.number)):
                raise ValueError(f"{key} must be numeric, got {type(value)}")
            value = float(value)
            if value <= 0:
                raise ValueError(f"{key} must be positive, got {value}")
            sanitized[key] = value
        
        elif key == 'random_seed':
            if value is not None:
                if not isinstance(value, (int, np.integer)):
                    raise ValueError(f"{key} must be integer or None, got {type(value)}")
                sanitized[key] = int(value)
            else:
                sanitized[key] = None
        
        else:
            # Pass through other parameters unchanged
            sanitized[key] = value
    
    return sanitized


def validate_matrix_properties(matrix: np.ndarray,
                             required_shape: Optional[Tuple[int, ...]] = None,
                             symmetric: bool = False,
                             positive_definite: bool = False) -> bool:
    """
    Validate properties of a matrix.
    
    Parameters
    ----------
    matrix : np.ndarray
        Matrix to validate
    required_shape : tuple, optional
        Required shape
    symmetric : bool, default=False
        Whether matrix should be symmetric
    positive_definite : bool, default=False
        Whether matrix should be positive definite
        
    Returns
    -------
    bool
        True if valid
        
    Raises
    ------
    ValueError
        If validation fails
    """
    if not isinstance(matrix, np.ndarray):
        raise ValueError(f"Expected numpy array, got {type(matrix)}")
    
    if matrix.ndim != 2:
        raise ValueError(f"Expected 2D matrix, got {matrix.ndim}D array")
    
    if required_shape is not None and matrix.shape != required_shape:
        raise ValueError(f"Expected shape {required_shape}, got {matrix.shape}")
    
    if symmetric:
        if matrix.shape[0] != matrix.shape[1]:
            raise ValueError("Symmetric matrix must be square")
        
        if not np.allclose(matrix, matrix.T):
            raise ValueError("Matrix is not symmetric")
    
    if positive_definite:
        if matrix.shape[0] != matrix.shape[1]:
            raise ValueError("Positive definite matrix must be square")
        
        try:
            eigenvals = np.linalg.eigvals(matrix)
            if np.any(eigenvals <= 0):
                raise ValueError("Matrix is not positive definite")
        except np.linalg.LinAlgError:
            raise ValueError("Cannot compute eigenvalues for positive definite check")
    
    return True