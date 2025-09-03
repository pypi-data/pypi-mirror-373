"""
📈 Vector Visualization Functions
================================

This module provides visualization functions for holographic vectors,
including distribution plots, similarity matrices, and dimensionality analysis.

Author: Benedict Chen (benedict@benedictchen.com)
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any, List, Optional, Union, Tuple
import warnings

try:
    from sklearn.decomposition import PCA
    from sklearn.manifold import TSNE
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


def plot_vector_distribution(vectors: np.ndarray,
                           names: Optional[List[str]] = None,
                           title: str = "Vector Value Distribution",
                           figsize: Tuple[int, int] = (12, 8),
                           save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot distribution of vector values.
    
    Parameters
    ----------
    vectors : np.ndarray
        Array of vectors (shape: n_vectors, vector_dim)
    names : List[str], optional
        Names for each vector
    title : str, default="Vector Value Distribution"
        Plot title
    figsize : Tuple[int, int], default=(12, 8)
        Figure size
    save_path : str, optional
        Path to save the plot
        
    Returns
    -------
    plt.Figure
        The created figure
    """
    if vectors.ndim == 1:
        vectors = vectors.reshape(1, -1)
    
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    fig.suptitle(title, fontsize=16)
    
    # Flatten all vectors for overall distribution
    all_values = vectors.flatten()
    
    # Overall histogram
    axes[0, 0].hist(all_values, bins=50, alpha=0.7, edgecolor='black')
    axes[0, 0].set_title('Overall Value Distribution')
    axes[0, 0].set_xlabel('Value')
    axes[0, 0].set_ylabel('Frequency')
    axes[0, 0].grid(True, alpha=0.3)
    
    # Box plot of vectors
    if len(vectors) <= 20:  # Only if reasonable number of vectors
        box_data = [vector for vector in vectors]
        box_labels = names[:len(vectors)] if names else [f'V{i}' for i in range(len(vectors))]
        
        axes[0, 1].boxplot(box_data, labels=box_labels)
        axes[0, 1].set_title('Vector Value Ranges')
        axes[0, 1].tick_params(axis='x', rotation=45)
    else:
        # Show sample of vectors
        sample_indices = np.random.choice(len(vectors), min(20, len(vectors)), replace=False)
        sample_vectors = vectors[sample_indices]
        box_data = [vector for vector in sample_vectors]
        box_labels = [f'V{i}' for i in sample_indices]
        
        axes[0, 1].boxplot(box_data, labels=box_labels)
        axes[0, 1].set_title(f'Sample Vector Value Ranges (n={len(sample_vectors)})')
        axes[0, 1].tick_params(axis='x', rotation=45)
    
    # Q-Q plot for normality check
    from scipy import stats
    stats.probplot(all_values[:10000], dist="norm", plot=axes[1, 0])  # Sample for speed
    axes[1, 0].set_title('Q-Q Plot (Normal Distribution)')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Vector norms
    norms = np.linalg.norm(vectors, axis=1)
    axes[1, 1].hist(norms, bins=30, alpha=0.7, edgecolor='black')
    axes[1, 1].set_title('Vector Norm Distribution')
    axes[1, 1].set_xlabel('Norm')
    axes[1, 1].set_ylabel('Frequency')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_vector_similarity_matrix(vectors: np.ndarray,
                                 names: Optional[List[str]] = None,
                                 metric: str = 'cosine',
                                 title: str = "Vector Similarity Matrix",
                                 figsize: Tuple[int, int] = (10, 8),
                                 save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot similarity matrix between vectors.
    
    Parameters
    ----------
    vectors : np.ndarray
        Array of vectors
    names : List[str], optional
        Names for vectors
    metric : str, default='cosine'
        Similarity metric
    title : str, default="Vector Similarity Matrix"
        Plot title
    figsize : Tuple[int, int], default=(10, 8)
        Figure size
    save_path : str, optional
        Path to save the plot
        
    Returns
    -------
    plt.Figure
        The created figure
    """
    n_vectors = len(vectors)
    
    # Limit size for readability
    if n_vectors > 50:
        indices = np.random.choice(n_vectors, 50, replace=False)
        vectors = vectors[indices]
        names = [names[i] for i in indices] if names else None
        n_vectors = 50
        title += f" (Sample of 50)"
    
    # Compute similarity matrix
    similarity_matrix = np.zeros((n_vectors, n_vectors))
    
    for i in range(n_vectors):
        for j in range(n_vectors):
            if metric == 'cosine':
                norm_i = np.linalg.norm(vectors[i])
                norm_j = np.linalg.norm(vectors[j])
                if norm_i > 0 and norm_j > 0:
                    similarity_matrix[i, j] = np.dot(vectors[i], vectors[j]) / (norm_i * norm_j)
            elif metric == 'correlation':
                similarity_matrix[i, j] = np.corrcoef(vectors[i], vectors[j])[0, 1]
            elif metric == 'euclidean':
                similarity_matrix[i, j] = -np.linalg.norm(vectors[i] - vectors[j])
    
    # Create plot
    fig, ax = plt.subplots(figsize=figsize)
    
    im = ax.imshow(similarity_matrix, cmap='RdBu_r', aspect='auto', 
                   vmin=-1, vmax=1 if metric != 'euclidean' else None)
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label(f'{metric.title()} Similarity')
    
    # Set labels
    if names and len(names) == n_vectors:
        ax.set_xticks(range(n_vectors))
        ax.set_yticks(range(n_vectors))
        ax.set_xticklabels(names, rotation=45, ha='right')
        ax.set_yticklabels(names)
    
    ax.set_title(title)
    ax.set_xlabel('Vector Index')
    ax.set_ylabel('Vector Index')
    
    # Add text annotations for small matrices
    if n_vectors <= 20:
        for i in range(n_vectors):
            for j in range(n_vectors):
                text = ax.text(j, i, f'{similarity_matrix[i, j]:.2f}',
                             ha="center", va="center", color="black" if abs(similarity_matrix[i, j]) < 0.5 else "white")
    
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_vector_norms(vectors: np.ndarray,
                     names: Optional[List[str]] = None,
                     title: str = "Vector Norms",
                     figsize: Tuple[int, int] = (12, 6),
                     save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot vector norms and statistics.
    
    Parameters
    ----------
    vectors : np.ndarray
        Array of vectors
    names : List[str], optional
        Names for vectors
    title : str, default="Vector Norms"
        Plot title
    figsize : Tuple[int, int], default=(12, 6)
        Figure size
    save_path : str, optional
        Path to save the plot
        
    Returns
    -------
    plt.Figure
        The created figure
    """
    norms = np.linalg.norm(vectors, axis=1)
    
    fig, axes = plt.subplots(1, 2, figsize=figsize)
    fig.suptitle(title, fontsize=16)
    
    # Histogram of norms
    axes[0].hist(norms, bins=30, alpha=0.7, edgecolor='black')
    axes[0].axvline(np.mean(norms), color='red', linestyle='--', label=f'Mean: {np.mean(norms):.3f}')
    axes[0].axvline(np.median(norms), color='orange', linestyle='--', label=f'Median: {np.median(norms):.3f}')
    axes[0].set_xlabel('Norm')
    axes[0].set_ylabel('Frequency')
    axes[0].set_title('Norm Distribution')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Norms over vector index
    if len(vectors) <= 100:
        # Show all vectors
        x = range(len(norms))
        labels = names[:len(norms)] if names else None
    else:
        # Sample for readability
        sample_indices = np.linspace(0, len(norms)-1, 100, dtype=int)
        x = sample_indices
        norms = norms[sample_indices]
        labels = None
    
    axes[1].plot(x, norms, 'bo-', markersize=3, alpha=0.7)
    axes[1].axhline(np.mean(norms), color='red', linestyle='--', alpha=0.7)
    axes[1].fill_between(x, np.mean(norms) - np.std(norms), np.mean(norms) + np.std(norms), 
                        alpha=0.2, color='red', label='±1 std')
    
    axes[1].set_xlabel('Vector Index')
    axes[1].set_ylabel('Norm')
    axes[1].set_title('Norms by Vector')
    axes[1].grid(True, alpha=0.3)
    axes[1].legend()
    
    if labels:
        axes[1].set_xticks(x[::max(1, len(x)//10)])  # Show every 10th label
        axes[1].set_xticklabels([labels[i] for i in x[::max(1, len(x)//10)]], rotation=45)
    
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_vector_components(vectors: np.ndarray,
                          component_indices: Optional[List[int]] = None,
                          names: Optional[List[str]] = None,
                          title: str = "Vector Components",
                          figsize: Tuple[int, int] = (12, 8),
                          save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot specific components of vectors.
    
    Parameters
    ----------
    vectors : np.ndarray
        Array of vectors
    component_indices : List[int], optional
        Indices of components to plot
    names : List[str], optional
        Names for vectors
    title : str, default="Vector Components"
        Plot title
    figsize : Tuple[int, int], default=(12, 8)
        Figure size
    save_path : str, optional
        Path to save the plot
        
    Returns
    -------
    plt.Figure
        The created figure
    """
    if component_indices is None:
        # Select representative components
        vector_dim = vectors.shape[1]
        if vector_dim <= 10:
            component_indices = list(range(vector_dim))
        else:
            component_indices = [0, vector_dim//4, vector_dim//2, 3*vector_dim//4, vector_dim-1]
    
    n_components = len(component_indices)
    n_vectors = len(vectors)
    
    # Limit number of vectors for readability
    if n_vectors > 20:
        sample_indices = np.random.choice(n_vectors, 20, replace=False)
        vectors = vectors[sample_indices]
        names = [names[i] for i in sample_indices] if names else None
        n_vectors = 20
        title += f" (Sample of 20 vectors)"
    
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    fig.suptitle(title, fontsize=16)
    axes = axes.flatten()
    
    # Component distributions
    ax = axes[0]
    for i, comp_idx in enumerate(component_indices[:4]):  # Show up to 4 components
        if i < 4:
            component_values = vectors[:, comp_idx]
            ax.hist(component_values, bins=20, alpha=0.6, label=f'Comp {comp_idx}')
    
    ax.set_xlabel('Component Value')
    ax.set_ylabel('Frequency')
    ax.set_title('Component Value Distributions')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Component means across vectors
    ax = axes[1]
    component_means = [np.mean(vectors[:, idx]) for idx in component_indices]
    ax.bar(range(len(component_indices)), component_means)
    ax.set_xlabel('Component Index')
    ax.set_ylabel('Mean Value')
    ax.set_title('Mean Component Values')
    ax.set_xticks(range(len(component_indices)))
    ax.set_xticklabels([str(idx) for idx in component_indices])
    ax.grid(True, alpha=0.3)
    
    # Component standard deviations
    ax = axes[2]
    component_stds = [np.std(vectors[:, idx]) for idx in component_indices]
    ax.bar(range(len(component_indices)), component_stds)
    ax.set_xlabel('Component Index')
    ax.set_ylabel('Standard Deviation')
    ax.set_title('Component Standard Deviations')
    ax.set_xticks(range(len(component_indices)))
    ax.set_xticklabels([str(idx) for idx in component_indices])
    ax.grid(True, alpha=0.3)
    
    # Heatmap of selected components
    ax = axes[3]
    selected_components = vectors[:, component_indices]
    im = ax.imshow(selected_components.T, aspect='auto', cmap='RdBu_r')
    
    vector_labels = names if names else [f'V{i}' for i in range(n_vectors)]
    ax.set_xticks(range(n_vectors))
    ax.set_xticklabels(vector_labels, rotation=45, ha='right')
    ax.set_yticks(range(len(component_indices)))
    ax.set_yticklabels([f'C{idx}' for idx in component_indices])
    ax.set_title('Component Values Heatmap')
    ax.set_xlabel('Vectors')
    ax.set_ylabel('Components')
    
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Component Value')
    
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_vector_pca(vectors: np.ndarray,
                   names: Optional[List[str]] = None,
                   n_components: int = 3,
                   title: str = "Vector PCA Analysis",
                   figsize: Tuple[int, int] = (15, 5),
                   save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot PCA analysis of vectors.
    
    Parameters
    ----------
    vectors : np.ndarray
        Array of vectors
    names : List[str], optional
        Names for vectors
    n_components : int, default=3
        Number of PCA components
    title : str, default="Vector PCA Analysis"
        Plot title
    figsize : Tuple[int, int], default=(15, 5)
        Figure size
    save_path : str, optional
        Path to save the plot
        
    Returns
    -------
    plt.Figure
        The created figure
    """
    if not SKLEARN_AVAILABLE:
        warnings.warn("sklearn not available, cannot perform PCA")
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, 'sklearn not available\nCannot perform PCA', 
               ha='center', va='center', fontsize=16)
        ax.set_title(title)
        return fig
    
    # Perform PCA
    pca = PCA(n_components=min(n_components, vectors.shape[1], vectors.shape[0]))
    transformed = pca.fit_transform(vectors)
    
    fig, axes = plt.subplots(1, 3, figsize=figsize)
    fig.suptitle(title, fontsize=16)
    
    # Explained variance
    explained_var_ratio = pca.explained_variance_ratio_
    cumulative_var = np.cumsum(explained_var_ratio)
    
    axes[0].bar(range(len(explained_var_ratio)), explained_var_ratio)
    axes[0].set_xlabel('Principal Component')
    axes[0].set_ylabel('Explained Variance Ratio')
    axes[0].set_title('Explained Variance by Component')
    axes[0].grid(True, alpha=0.3)
    
    # Add text annotations
    for i, var in enumerate(explained_var_ratio):
        axes[0].text(i, var + 0.01, f'{var:.3f}', ha='center', va='bottom')
    
    # Cumulative explained variance
    axes[1].plot(range(len(cumulative_var)), cumulative_var, 'bo-')
    axes[1].axhline(y=0.9, color='r', linestyle='--', alpha=0.7, label='90% variance')
    axes[1].axhline(y=0.95, color='orange', linestyle='--', alpha=0.7, label='95% variance')
    axes[1].set_xlabel('Number of Components')
    axes[1].set_ylabel('Cumulative Explained Variance')
    axes[1].set_title('Cumulative Explained Variance')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    # 2D projection (first two components)
    if transformed.shape[1] >= 2:
        scatter = axes[2].scatter(transformed[:, 0], transformed[:, 1], 
                                alpha=0.7, s=50, c=range(len(vectors)), cmap='viridis')
        
        axes[2].set_xlabel(f'PC1 ({explained_var_ratio[0]:.3f} var)')
        axes[2].set_ylabel(f'PC2 ({explained_var_ratio[1]:.3f} var)')
        axes[2].set_title('2D PCA Projection')
        axes[2].grid(True, alpha=0.3)
        
        # Add colorbar
        cbar = plt.colorbar(scatter, ax=axes[2])
        cbar.set_label('Vector Index')
        
        # Add labels for small datasets
        if len(vectors) <= 20 and names:
            for i, name in enumerate(names):
                axes[2].annotate(name, (transformed[i, 0], transformed[i, 1]), 
                               xytext=(5, 5), textcoords='offset points', 
                               fontsize=8, alpha=0.7)
    else:
        axes[2].text(0.5, 0.5, 'Need at least 2 components\nfor 2D projection', 
                    ha='center', va='center')
        axes[2].set_title('2D PCA Projection (Not Available)')
    
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig