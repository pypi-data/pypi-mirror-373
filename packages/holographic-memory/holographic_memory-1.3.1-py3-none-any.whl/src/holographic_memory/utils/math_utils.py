"""
🧮 Mathematical Utility Functions
================================

This module provides mathematical utility functions for holographic memory
operations, including circular convolution, correlation, and statistical tests.

Author: Benedict Chen (benedict@benedictchen.com)
"""

import numpy as np
from typing import Tuple, List, Optional, Dict, Any
from scipy import stats
import warnings


def circular_convolution(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """
    Compute circular convolution of two vectors.
    
    Parameters
    ----------
    x, y : np.ndarray
        Input vectors of same length
        
    Returns
    -------
    np.ndarray
        Circular convolution result
    """
    if len(x) != len(y):
        raise ValueError("Vectors must have same length")
    
    n = len(x)
    result = np.zeros(n)
    
    for i in range(n):
        for j in range(n):
            result[i] += x[j] * y[(i - j) % n]
    
    return result


def circular_correlation(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """
    Compute circular correlation of two vectors.
    
    Parameters
    ----------
    x, y : np.ndarray
        Input vectors of same length
        
    Returns
    -------
    np.ndarray
        Circular correlation result
    """
    if len(x) != len(y):
        raise ValueError("Vectors must have same length")
    
    n = len(x)
    result = np.zeros(n)
    
    for i in range(n):
        for j in range(n):
            result[i] += x[j] * y[(i + j) % n]
    
    return result


def fft_convolution(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """
    Compute circular convolution using FFT (much faster for large vectors).
    
    Parameters
    ----------
    x, y : np.ndarray
        Input vectors of same length
        
    Returns
    -------
    np.ndarray
        Circular convolution result
    """
    if len(x) != len(y):
        raise ValueError("Vectors must have same length")
    
    X = np.fft.fft(x)
    Y = np.fft.fft(y)
    
    # Convolution in frequency domain is element-wise multiplication
    Z = X * Y
    
    # Convert back to time domain and take real part
    return np.fft.ifft(Z).real


def fft_correlation(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """
    Compute circular correlation using FFT.
    
    Parameters
    ----------
    x, y : np.ndarray
        Input vectors of same length
        
    Returns
    -------
    np.ndarray
        Circular correlation result
    """
    if len(x) != len(y):
        raise ValueError("Vectors must have same length")
    
    X = np.fft.fft(x)
    Y = np.fft.fft(y)
    
    # Correlation in frequency domain is conjugate multiplication
    Z = X * np.conj(Y)
    
    # Convert back to time domain and take real part
    return np.fft.ifft(Z).real


def complex_exponential(vector: np.ndarray) -> np.ndarray:
    """
    Convert real vector to complex exponential form.
    
    Parameters
    ----------
    vector : np.ndarray
        Real input vector
        
    Returns
    -------
    np.ndarray
        Complex exponential vector
    """
    return np.exp(1j * vector)


def phase_encoding(vector: np.ndarray, 
                  scale: float = 2 * np.pi) -> np.ndarray:
    """
    Encode vector values as phases in complex exponential.
    
    Parameters
    ----------
    vector : np.ndarray
        Input vector
    scale : float, default=2π
        Scaling factor for phase values
        
    Returns
    -------
    np.ndarray
        Phase-encoded complex vector
    """
    phases = (vector / np.max(np.abs(vector))) * scale
    return np.exp(1j * phases)


def magnitude_phase_split(complex_vector: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Split complex vector into magnitude and phase components.
    
    Parameters
    ----------
    complex_vector : np.ndarray
        Complex input vector
        
    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        Magnitude and phase arrays
    """
    magnitude = np.abs(complex_vector)
    phase = np.angle(complex_vector)
    return magnitude, phase


def statistical_tests(vector1: np.ndarray, 
                     vector2: np.ndarray) -> Dict[str, Any]:
    """
    Perform statistical tests comparing two vectors.
    
    Parameters
    ----------
    vector1, vector2 : np.ndarray
        Vectors to compare
        
    Returns
    -------
    Dict[str, Any]
        Dictionary of test results
    """
    results = {}
    
    # T-test for equal means
    try:
        t_stat, t_pval = stats.ttest_ind(vector1, vector2)
        results['t_test'] = {
            'statistic': t_stat,
            'p_value': t_pval,
            'significant': t_pval < 0.05
        }
    except Exception as e:
        results['t_test'] = {'error': str(e)}
    
    # Kolmogorov-Smirnov test for equal distributions
    try:
        ks_stat, ks_pval = stats.ks_2samp(vector1, vector2)
        results['ks_test'] = {
            'statistic': ks_stat,
            'p_value': ks_pval,
            'significant': ks_pval < 0.05
        }
    except Exception as e:
        results['ks_test'] = {'error': str(e)}
    
    # Mann-Whitney U test (non-parametric)
    try:
        u_stat, u_pval = stats.mannwhitneyu(vector1, vector2)
        results['mannwhitney_u'] = {
            'statistic': u_stat,
            'p_value': u_pval,
            'significant': u_pval < 0.05
        }
    except Exception as e:
        results['mannwhitney_u'] = {'error': str(e)}
    
    # Basic statistics comparison
    results['descriptive'] = {
        'mean_diff': np.mean(vector1) - np.mean(vector2),
        'std_ratio': np.std(vector1) / max(np.std(vector2), 1e-10),
        'range_ratio': (np.max(vector1) - np.min(vector1)) / max(np.max(vector2) - np.min(vector2), 1e-10)
    }
    
    return results


def entropy(vector: np.ndarray, bins: int = 50) -> float:
    """
    Compute Shannon entropy of vector values.
    
    Parameters
    ----------
    vector : np.ndarray
        Input vector
    bins : int, default=50
        Number of bins for histogram
        
    Returns
    -------
    float
        Shannon entropy
    """
    hist, _ = np.histogram(vector, bins=bins)
    hist = hist + 1e-12  # Avoid log(0)
    probs = hist / np.sum(hist)
    return -np.sum(probs * np.log2(probs))


def mutual_information(vector1: np.ndarray, 
                      vector2: np.ndarray,
                      bins: int = 50) -> float:
    """
    Compute mutual information between two vectors.
    
    Parameters
    ----------
    vector1, vector2 : np.ndarray
        Input vectors
    bins : int, default=50
        Number of bins for histogram
        
    Returns
    -------
    float
        Mutual information
    """
    # Compute joint histogram
    hist_2d, _, _ = np.histogram2d(vector1, vector2, bins=bins)
    hist_2d = hist_2d + 1e-12
    
    # Marginal distributions
    p_x = np.sum(hist_2d, axis=1)
    p_y = np.sum(hist_2d, axis=0)
    
    # Joint distribution
    p_xy = hist_2d / np.sum(hist_2d)
    p_x = p_x / np.sum(p_x)
    p_y = p_y / np.sum(p_y)
    
    # Mutual information
    mi = 0.0
    for i in range(len(p_x)):
        for j in range(len(p_y)):
            if p_xy[i, j] > 0:
                mi += p_xy[i, j] * np.log2(p_xy[i, j] / (p_x[i] * p_y[j]))
    
    return mi


def power_spectrum(vector: np.ndarray) -> np.ndarray:
    """
    Compute power spectrum of vector using FFT.
    
    Parameters
    ----------
    vector : np.ndarray
        Input vector
        
    Returns
    -------
    np.ndarray
        Power spectrum
    """
    fft_result = np.fft.fft(vector)
    return np.abs(fft_result) ** 2


def autocorrelation(vector: np.ndarray, max_lag: Optional[int] = None) -> np.ndarray:
    """
    Compute autocorrelation function of vector.
    
    Parameters
    ----------
    vector : np.ndarray
        Input vector
    max_lag : int, optional
        Maximum lag to compute (default: vector length)
        
    Returns
    -------
    np.ndarray
        Autocorrelation values
    """
    if max_lag is None:
        max_lag = len(vector)
    
    # Normalize vector
    vector = vector - np.mean(vector)
    
    # Compute autocorrelation using convolution
    autocorr = np.correlate(vector, vector, mode='full')
    
    # Take positive lags only and normalize
    mid = len(autocorr) // 2
    autocorr = autocorr[mid:mid + max_lag]
    autocorr = autocorr / autocorr[0]  # Normalize by zero-lag value
    
    return autocorr


def cross_correlation(vector1: np.ndarray, 
                     vector2: np.ndarray,
                     max_lag: Optional[int] = None) -> np.ndarray:
    """
    Compute cross-correlation between two vectors.
    
    Parameters
    ----------
    vector1, vector2 : np.ndarray
        Input vectors
    max_lag : int, optional
        Maximum lag to compute
        
    Returns
    -------
    np.ndarray
        Cross-correlation values
    """
    if max_lag is None:
        max_lag = min(len(vector1), len(vector2))
    
    # Normalize vectors
    v1 = vector1 - np.mean(vector1)
    v2 = vector2 - np.mean(vector2)
    
    # Compute cross-correlation
    xcorr = np.correlate(v1, v2, mode='full')
    
    # Extract relevant portion
    mid = len(xcorr) // 2
    start = max(0, mid - max_lag)
    end = min(len(xcorr), mid + max_lag + 1)
    
    return xcorr[start:end]


def matrix_condition_number(matrix: np.ndarray) -> float:
    """
    Compute condition number of matrix.
    
    Parameters
    ----------
    matrix : np.ndarray
        Input matrix
        
    Returns
    -------
    float
        Condition number
    """
    try:
        return np.linalg.cond(matrix)
    except np.linalg.LinAlgError:
        return np.inf


def robust_svd(matrix: np.ndarray, 
               rank: Optional[int] = None) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute robust SVD with optional rank approximation.
    
    Parameters
    ----------
    matrix : np.ndarray
        Input matrix
    rank : int, optional
        Desired rank for low-rank approximation
        
    Returns
    -------
    Tuple[np.ndarray, np.ndarray, np.ndarray]
        U, S, Vt matrices from SVD
    """
    try:
        U, S, Vt = np.linalg.svd(matrix, full_matrices=False)
        
        if rank is not None and rank < len(S):
            U = U[:, :rank]
            S = S[:rank]
            Vt = Vt[:rank, :]
        
        return U, S, Vt
    
    except np.linalg.LinAlgError as e:
        warnings.warn(f"SVD failed: {e}")
        # Return identity-like matrices as fallback
        m, n = matrix.shape
        k = min(m, n, rank) if rank is not None else min(m, n)
        U = np.eye(m, k)
        S = np.ones(k)
        Vt = np.eye(k, n)
        return U, S, Vt