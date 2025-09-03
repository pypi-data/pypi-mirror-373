"""
📊 Visualization Module for Holographic Memory
=============================================

This module provides visualization capabilities for holographic memory systems,
including vector plots, memory analysis, and interactive tools.

Author: Benedict Chen (benedict@benedictchen.com)
"""

from .vector_plots import (
    plot_vector_distribution,
    plot_vector_similarity_matrix,
    plot_vector_norms,
    plot_vector_components,
    plot_vector_pca
)

from .memory_plots import (
    plot_memory_capacity,
    plot_retrieval_accuracy,
    plot_noise_robustness,
    plot_memory_statistics,
    plot_cleanup_convergence
)

from .binding_plots import (
    plot_binding_quality,
    plot_binding_accuracy,
    plot_unbinding_accuracy,
    plot_binding_similarity_distribution
)

from .analysis_plots import (
    plot_performance_analysis,
    plot_clustering_results,
    plot_dimensionality_analysis,
    plot_statistical_distribution,
    plot_correlation_matrix
)

from .interactive import (
    create_interactive_memory_explorer,
    create_vector_space_browser,
    create_binding_visualizer,
    create_memory_dashboard
)

__all__ = [
    # Vector plots
    'plot_vector_distribution',
    'plot_vector_similarity_matrix',
    'plot_vector_norms', 
    'plot_vector_components',
    'plot_vector_pca',
    
    # Memory plots
    'plot_memory_capacity',
    'plot_retrieval_accuracy',
    'plot_noise_robustness',
    'plot_memory_statistics',
    'plot_cleanup_convergence',
    
    # Binding plots
    'plot_binding_quality',
    'plot_binding_accuracy',
    'plot_unbinding_accuracy',
    'plot_binding_similarity_distribution',
    
    # Analysis plots
    'plot_performance_analysis',
    'plot_clustering_results',
    'plot_dimensionality_analysis',
    'plot_statistical_distribution',
    'plot_correlation_matrix',
    
    # Interactive tools
    'create_interactive_memory_explorer',
    'create_vector_space_browser',
    'create_binding_visualizer',
    'create_memory_dashboard'
]