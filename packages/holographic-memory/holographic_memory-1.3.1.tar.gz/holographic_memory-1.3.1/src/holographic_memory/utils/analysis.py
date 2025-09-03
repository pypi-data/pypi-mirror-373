"""
📊 Analysis Utility Functions
============================

This module provides analysis utilities for holographic memory systems,
including vector distribution analysis, binding quality assessment,
and capacity analysis.

Author: Benedict Chen (benedict@benedictchen.com)
"""

import numpy as np
from typing import Dict, Any, List, Tuple, Optional, Union
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import warnings


def analyze_vector_distribution(vectors: np.ndarray,
                              name: str = "vectors") -> Dict[str, Any]:
    """
    Analyze the statistical distribution of vectors.
    
    Parameters
    ----------
    vectors : np.ndarray
        Array of vectors (shape: n_vectors, vector_dim)
    name : str, default="vectors"
        Name for the analysis
        
    Returns
    -------
    Dict[str, Any]
        Dictionary containing distribution analysis
    """
    if vectors.ndim == 1:
        vectors = vectors.reshape(1, -1)
    
    n_vectors, vector_dim = vectors.shape
    
    analysis = {
        'name': name,
        'n_vectors': n_vectors,
        'vector_dim': vector_dim,
        'basic_stats': {},
        'distribution_tests': {},
        'vector_properties': {}
    }
    
    # Basic statistics
    flattened = vectors.flatten()
    analysis['basic_stats'] = {
        'mean': float(np.mean(flattened)),
        'std': float(np.std(flattened)),
        'min': float(np.min(flattened)),
        'max': float(np.max(flattened)),
        'median': float(np.median(flattened)),
        'skewness': float(stats.skew(flattened)),
        'kurtosis': float(stats.kurtosis(flattened))
    }
    
    # Distribution tests
    try:
        # Test for normality
        shapiro_stat, shapiro_p = stats.shapiro(
            flattened[:5000] if len(flattened) > 5000 else flattened
        )
        
        # Test for uniformity
        ks_uniform_stat, ks_uniform_p = stats.kstest(
            (flattened - np.min(flattened)) / (np.max(flattened) - np.min(flattened)),
            'uniform'
        )
        
        # Test for normality with KS test
        normalized = (flattened - np.mean(flattened)) / np.std(flattened)
        ks_normal_stat, ks_normal_p = stats.kstest(normalized, 'norm')
        
        analysis['distribution_tests'] = {
            'shapiro_normality': {
                'statistic': float(shapiro_stat),
                'p_value': float(shapiro_p),
                'is_normal': shapiro_p > 0.05
            },
            'ks_uniformity': {
                'statistic': float(ks_uniform_stat),
                'p_value': float(ks_uniform_p),
                'is_uniform': ks_uniform_p > 0.05
            },
            'ks_normality': {
                'statistic': float(ks_normal_stat),
                'p_value': float(ks_normal_p),
                'is_normal': ks_normal_p > 0.05
            }
        }
    except Exception as e:
        analysis['distribution_tests'] = {'error': str(e)}
    
    # Vector properties
    norms = np.linalg.norm(vectors, axis=1)
    analysis['vector_properties'] = {
        'mean_norm': float(np.mean(norms)),
        'std_norm': float(np.std(norms)),
        'min_norm': float(np.min(norms)),
        'max_norm': float(np.max(norms)),
        'norm_range': float(np.max(norms) - np.min(norms))
    }
    
    # Sparsity analysis
    zero_threshold = 1e-6
    sparsity_per_vector = np.mean(np.abs(vectors) < zero_threshold, axis=1)
    analysis['vector_properties']['sparsity'] = {
        'mean_sparsity': float(np.mean(sparsity_per_vector)),
        'std_sparsity': float(np.std(sparsity_per_vector)),
        'min_sparsity': float(np.min(sparsity_per_vector)),
        'max_sparsity': float(np.max(sparsity_per_vector))
    }
    
    return analysis


def measure_binding_quality(role_vectors: np.ndarray,
                          filler_vectors: np.ndarray,
                          bound_vectors: np.ndarray,
                          binding_func: callable,
                          unbinding_func: callable) -> Dict[str, Any]:
    """
    Measure the quality of binding operations.
    
    Parameters
    ----------
    role_vectors : np.ndarray
        Array of role vectors
    filler_vectors : np.ndarray
        Array of filler vectors
    bound_vectors : np.ndarray
        Array of bound vectors
    binding_func : callable
        Binding function
    unbinding_func : callable
        Unbinding function
        
    Returns
    -------
    Dict[str, Any]
        Dictionary containing binding quality metrics
    """
    n_pairs = min(len(role_vectors), len(filler_vectors), len(bound_vectors))
    
    metrics = {
        'n_pairs': n_pairs,
        'binding_accuracy': {},
        'unbinding_accuracy': {},
        'similarity_analysis': {},
        'noise_analysis': {}
    }
    
    # Test binding accuracy
    binding_similarities = []
    for i in range(n_pairs):
        # Re-bind and compare
        rebound = binding_func(role_vectors[i], filler_vectors[i])
        similarity = np.dot(bound_vectors[i], rebound) / (
            np.linalg.norm(bound_vectors[i]) * np.linalg.norm(rebound)
        )
        binding_similarities.append(similarity)
    
    metrics['binding_accuracy'] = {
        'mean_similarity': float(np.mean(binding_similarities)),
        'std_similarity': float(np.std(binding_similarities)),
        'min_similarity': float(np.min(binding_similarities)),
        'max_similarity': float(np.max(binding_similarities))
    }
    
    # Test unbinding accuracy
    unbinding_similarities = []
    for i in range(n_pairs):
        # Unbind and compare to original filler
        retrieved_filler = unbinding_func(bound_vectors[i], role_vectors[i])
        similarity = np.dot(filler_vectors[i], retrieved_filler) / (
            np.linalg.norm(filler_vectors[i]) * np.linalg.norm(retrieved_filler)
        )
        unbinding_similarities.append(similarity)
    
    metrics['unbinding_accuracy'] = {
        'mean_similarity': float(np.mean(unbinding_similarities)),
        'std_similarity': float(np.std(unbinding_similarities)),
        'min_similarity': float(np.min(unbinding_similarities)),
        'max_similarity': float(np.max(unbinding_similarities))
    }
    
    # Similarity analysis between roles and fillers
    role_filler_similarities = []
    for i in range(n_pairs):
        similarity = np.dot(role_vectors[i], filler_vectors[i]) / (
            np.linalg.norm(role_vectors[i]) * np.linalg.norm(filler_vectors[i])
        )
        role_filler_similarities.append(similarity)
    
    metrics['similarity_analysis'] = {
        'role_filler_similarity': {
            'mean': float(np.mean(role_filler_similarities)),
            'std': float(np.std(role_filler_similarities)),
            'independence_score': 1.0 - abs(np.mean(role_filler_similarities))
        }
    }
    
    # Noise robustness test
    if n_pairs > 0:
        noise_levels = [0.1, 0.2, 0.3]
        noise_robustness = {}
        
        for noise_level in noise_levels:
            noisy_similarities = []
            
            for i in range(min(n_pairs, 10)):  # Test on subset for speed
                # Add noise to bound vector
                noise = np.random.normal(0, noise_level, bound_vectors[i].shape)
                noisy_bound = bound_vectors[i] + noise
                
                # Try to retrieve filler
                retrieved_filler = unbinding_func(noisy_bound, role_vectors[i])
                similarity = np.dot(filler_vectors[i], retrieved_filler) / (
                    np.linalg.norm(filler_vectors[i]) * np.linalg.norm(retrieved_filler)
                )
                noisy_similarities.append(similarity)
            
            noise_robustness[f'noise_{noise_level}'] = {
                'mean_similarity': float(np.mean(noisy_similarities)),
                'degradation': float(np.mean(unbinding_similarities[:len(noisy_similarities)]) - 
                                  np.mean(noisy_similarities))
            }
        
        metrics['noise_analysis'] = noise_robustness
    
    return metrics


def capacity_analysis(memory_system,
                     n_items_range: List[int] = None,
                     vector_dim: int = 512,
                     n_trials: int = 5) -> Dict[str, Any]:
    """
    Analyze memory capacity and performance degradation.
    
    Parameters
    ----------
    memory_system : object
        Memory system to test
    n_items_range : List[int], optional
        Range of item counts to test
    vector_dim : int, default=512
        Vector dimension
    n_trials : int, default=5
        Number of trials per item count
        
    Returns
    -------
    Dict[str, Any]
        Dictionary containing capacity analysis
    """
    if n_items_range is None:
        n_items_range = [10, 50, 100, 200, 500, 1000]
    
    results = {
        'item_counts': n_items_range,
        'retrieval_accuracy': [],
        'storage_time': [],
        'retrieval_time': [],
        'memory_usage': [],
        'capacity_estimate': None
    }
    
    for n_items in n_items_range:
        trial_accuracies = []
        trial_store_times = []
        trial_retrieve_times = []
        trial_memory_usage = []
        
        for trial in range(n_trials):
            # Reset memory system
            if hasattr(memory_system, 'reset'):
                memory_system.reset()
            elif hasattr(memory_system, 'clear'):
                memory_system.clear()
            
            # Generate test data
            test_vectors = np.random.randn(n_items, vector_dim)
            test_keys = [f"item_{i}" for i in range(n_items)]
            
            # Measure storage time
            start_time = time.time()
            for key, vector in zip(test_keys, test_vectors):
                memory_system.store(key, vector)
            store_time = time.time() - start_time
            
            # Measure retrieval accuracy and time
            start_time = time.time()
            correct_retrievals = 0
            
            for key, original_vector in zip(test_keys, test_vectors):
                retrieved = memory_system.retrieve(key)
                if retrieved is not None:
                    # Check similarity
                    if hasattr(retrieved, 'data'):
                        retrieved_data = retrieved.data
                    else:
                        retrieved_data = retrieved
                    
                    similarity = np.dot(original_vector, retrieved_data) / (
                        np.linalg.norm(original_vector) * np.linalg.norm(retrieved_data)
                    )
                    
                    if similarity > 0.9:  # High similarity threshold
                        correct_retrievals += 1
            
            retrieve_time = time.time() - start_time
            accuracy = correct_retrievals / n_items
            
            # Measure memory usage
            if hasattr(memory_system, 'get_statistics'):
                stats = memory_system.get_statistics()
                memory_usage = stats.get('memory_usage_mb', 0)
            else:
                memory_usage = 0
            
            trial_accuracies.append(accuracy)
            trial_store_times.append(store_time)
            trial_retrieve_times.append(retrieve_time)
            trial_memory_usage.append(memory_usage)
        
        # Average across trials
        results['retrieval_accuracy'].append(np.mean(trial_accuracies))
        results['storage_time'].append(np.mean(trial_store_times))
        results['retrieval_time'].append(np.mean(trial_retrieve_times))
        results['memory_usage'].append(np.mean(trial_memory_usage))
    
    # Estimate capacity (where accuracy drops below 90%)
    accuracies = results['retrieval_accuracy']
    for i, accuracy in enumerate(accuracies):
        if accuracy < 0.9:
            if i > 0:
                # Interpolate between previous and current point
                prev_items, prev_acc = n_items_range[i-1], accuracies[i-1]
                curr_items, curr_acc = n_items_range[i], accuracy
                
                # Linear interpolation to find where accuracy = 0.9
                if prev_acc > 0.9:
                    slope = (curr_acc - prev_acc) / (curr_items - prev_items)
                    capacity_estimate = prev_items + (0.9 - prev_acc) / slope
                    results['capacity_estimate'] = int(capacity_estimate)
                    break
            else:
                results['capacity_estimate'] = n_items_range[0]
                break
    else:
        # Accuracy never dropped below 90%
        results['capacity_estimate'] = n_items_range[-1]
    
    return results


def noise_robustness_test(memory_system,
                         noise_levels: List[float] = None,
                         n_items: int = 100,
                         vector_dim: int = 512,
                         n_trials: int = 3) -> Dict[str, Any]:
    """
    Test robustness to different noise levels.
    
    Parameters
    ----------
    memory_system : object
        Memory system to test
    noise_levels : List[float], optional
        Noise levels to test
    n_items : int, default=100
        Number of items to store
    vector_dim : int, default=512
        Vector dimension
    n_trials : int, default=3
        Number of trials per noise level
        
    Returns
    -------
    Dict[str, Any]
        Dictionary containing noise robustness results
    """
    if noise_levels is None:
        noise_levels = [0.0, 0.1, 0.2, 0.3, 0.5]
    
    results = {
        'noise_levels': noise_levels,
        'retrieval_accuracy': [],
        'similarity_degradation': []
    }
    
    # Generate base test data
    test_vectors = np.random.randn(n_items, vector_dim)
    test_keys = [f"item_{i}" for i in range(n_items)]
    
    for noise_level in noise_levels:
        trial_accuracies = []
        trial_similarities = []
        
        for trial in range(n_trials):
            # Reset and populate memory
            if hasattr(memory_system, 'reset'):
                memory_system.reset()
            elif hasattr(memory_system, 'clear'):
                memory_system.clear()
            
            for key, vector in zip(test_keys, test_vectors):
                memory_system.store(key, vector)
            
            # Test retrieval with noise
            correct_retrievals = 0
            similarities = []
            
            for key, original_vector in zip(test_keys, test_vectors):
                # Add noise to query (simulating noisy retrieval cues)
                noise = np.random.normal(0, noise_level, original_vector.shape)
                noisy_query = original_vector + noise
                
                # Store noisy version and retrieve
                noisy_key = f"{key}_noisy"
                memory_system.store(noisy_key, noisy_query)
                retrieved = memory_system.retrieve(noisy_key)
                
                if retrieved is not None:
                    if hasattr(retrieved, 'data'):
                        retrieved_data = retrieved.data
                    else:
                        retrieved_data = retrieved
                    
                    similarity = np.dot(original_vector, retrieved_data) / (
                        np.linalg.norm(original_vector) * np.linalg.norm(retrieved_data)
                    )
                    similarities.append(similarity)
                    
                    if similarity > 0.7:  # Lower threshold for noisy conditions
                        correct_retrievals += 1
                else:
                    similarities.append(0.0)
            
            accuracy = correct_retrievals / n_items
            mean_similarity = np.mean(similarities)
            
            trial_accuracies.append(accuracy)
            trial_similarities.append(mean_similarity)
        
        results['retrieval_accuracy'].append(np.mean(trial_accuracies))
        results['similarity_degradation'].append(np.mean(trial_similarities))
    
    return results


def similarity_matrix(vectors: np.ndarray,
                     metric: str = 'cosine',
                     sample_size: Optional[int] = None) -> np.ndarray:
    """
    Compute similarity matrix between vectors.
    
    Parameters
    ----------
    vectors : np.ndarray
        Array of vectors
    metric : str, default='cosine'
        Similarity metric
    sample_size : int, optional
        Maximum number of vectors to include (for large arrays)
        
    Returns
    -------
    np.ndarray
        Similarity matrix
    """
    if sample_size and len(vectors) > sample_size:
        indices = np.random.choice(len(vectors), sample_size, replace=False)
        vectors = vectors[indices]
    
    n_vectors = len(vectors)
    similarity_mat = np.zeros((n_vectors, n_vectors))
    
    for i in range(n_vectors):
        for j in range(i, n_vectors):
            if metric == 'cosine':
                sim = np.dot(vectors[i], vectors[j]) / (
                    np.linalg.norm(vectors[i]) * np.linalg.norm(vectors[j])
                )
            elif metric == 'euclidean':
                sim = -np.linalg.norm(vectors[i] - vectors[j])
            elif metric == 'correlation':
                sim = np.corrcoef(vectors[i], vectors[j])[0, 1]
            else:
                raise ValueError(f"Unknown metric: {metric}")
            
            similarity_mat[i, j] = sim
            similarity_mat[j, i] = sim
    
    return similarity_mat


def clustering_analysis(vectors: np.ndarray,
                       n_clusters: int = 10,
                       max_samples: int = 1000) -> Dict[str, Any]:
    """
    Perform clustering analysis on vectors.
    
    Parameters
    ----------
    vectors : np.ndarray
        Array of vectors
    n_clusters : int, default=10
        Number of clusters
    max_samples : int, default=1000
        Maximum samples to use (for large datasets)
        
    Returns
    -------
    Dict[str, Any]
        Dictionary containing clustering results
    """
    if len(vectors) > max_samples:
        indices = np.random.choice(len(vectors), max_samples, replace=False)
        sample_vectors = vectors[indices]
    else:
        sample_vectors = vectors
        indices = np.arange(len(vectors))
    
    try:
        # K-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(sample_vectors)
        
        # Compute cluster statistics
        cluster_stats = {}
        for i in range(n_clusters):
            cluster_mask = cluster_labels == i
            cluster_vectors = sample_vectors[cluster_mask]
            
            if len(cluster_vectors) > 0:
                cluster_center = kmeans.cluster_centers_[i]
                distances = [np.linalg.norm(v - cluster_center) for v in cluster_vectors]
                
                cluster_stats[f'cluster_{i}'] = {
                    'size': int(np.sum(cluster_mask)),
                    'mean_distance_to_center': float(np.mean(distances)),
                    'std_distance_to_center': float(np.std(distances)),
                    'max_distance_to_center': float(np.max(distances))
                }
        
        # Overall clustering quality
        inertia = kmeans.inertia_
        silhouette_score = None
        
        try:
            from sklearn.metrics import silhouette_score as sk_silhouette_score
            if len(np.unique(cluster_labels)) > 1:  # Need at least 2 clusters
                silhouette_score = float(sk_silhouette_score(sample_vectors, cluster_labels))
        except ImportError:
            pass
        
        results = {
            'n_clusters': n_clusters,
            'n_samples': len(sample_vectors),
            'inertia': float(inertia),
            'silhouette_score': silhouette_score,
            'cluster_statistics': cluster_stats,
            'cluster_labels': cluster_labels.tolist()
        }
        
        return results
        
    except Exception as e:
        return {'error': str(e)}


def dimensionality_analysis(vectors: np.ndarray,
                          n_components: Optional[int] = None,
                          methods: List[str] = None) -> Dict[str, Any]:
    """
    Analyze dimensionality characteristics of vectors.
    
    Parameters
    ----------
    vectors : np.ndarray
        Array of vectors
    n_components : int, optional
        Number of components for dimensionality reduction
    methods : List[str], optional
        Dimensionality reduction methods to use
        
    Returns
    -------
    Dict[str, Any]
        Dictionary containing dimensionality analysis
    """
    if methods is None:
        methods = ['pca']
    
    if n_components is None:
        n_components = min(50, vectors.shape[1], vectors.shape[0] - 1)
    
    results = {
        'original_dim': vectors.shape[1],
        'n_samples': vectors.shape[0],
        'effective_rank': None,
        'intrinsic_dimensionality': None
    }
    
    # Effective rank (based on singular values)
    try:
        _, s, _ = np.linalg.svd(vectors.T, full_matrices=False)
        # Normalize singular values
        s_norm = s / np.sum(s)
        # Compute entropy-based effective rank
        entropy = -np.sum(s_norm * np.log(s_norm + 1e-12))
        effective_rank = np.exp(entropy)
        results['effective_rank'] = float(effective_rank)
        
        # Estimate intrinsic dimensionality (90% of variance)
        cumsum_variance = np.cumsum(s_norm)
        intrinsic_dim = np.argmax(cumsum_variance >= 0.9) + 1
        results['intrinsic_dimensionality'] = int(intrinsic_dim)
        
    except Exception as e:
        results['svd_error'] = str(e)
    
    # Dimensionality reduction methods
    for method in methods:
        try:
            if method == 'pca':
                pca = PCA(n_components=n_components)
                reduced = pca.fit_transform(vectors)
                
                results['pca'] = {
                    'explained_variance_ratio': pca.explained_variance_ratio_.tolist(),
                    'cumulative_variance': np.cumsum(pca.explained_variance_ratio_).tolist(),
                    'n_components_90_variance': int(np.argmax(np.cumsum(pca.explained_variance_ratio_) >= 0.9) + 1),
                    'reduced_shape': reduced.shape
                }
                
            elif method == 'tsne':
                # Use smaller number of components for t-SNE
                tsne_components = min(3, n_components)
                tsne = TSNE(n_components=tsne_components, random_state=42)
                
                # Sample data if too large
                sample_size = min(1000, len(vectors))
                if len(vectors) > sample_size:
                    indices = np.random.choice(len(vectors), sample_size, replace=False)
                    sample_vectors = vectors[indices]
                else:
                    sample_vectors = vectors
                
                reduced = tsne.fit_transform(sample_vectors)
                
                results['tsne'] = {
                    'reduced_shape': reduced.shape,
                    'sample_size': sample_size,
                    'kl_divergence': float(tsne.kl_divergence_)
                }
                
        except ImportError:
            results[f'{method}_error'] = f"{method} not available (missing sklearn)"
        except Exception as e:
            results[f'{method}_error'] = str(e)
    
    return results