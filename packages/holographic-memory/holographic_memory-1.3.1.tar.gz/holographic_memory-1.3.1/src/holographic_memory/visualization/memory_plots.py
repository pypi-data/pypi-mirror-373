"""
🧠 Memory System Visualization Functions
=======================================

This module provides visualization functions for holographic memory system
performance, capacity analysis, and memory statistics.

Author: Benedict Chen (benedict@benedictchen.com)
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Any, List, Optional, Tuple
import warnings


def plot_memory_capacity(capacity_results: Dict[str, Any],
                        title: str = "Memory Capacity Analysis",
                        figsize: Tuple[int, int] = (15, 10),
                        save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot memory capacity analysis results.
    
    Parameters
    ----------
    capacity_results : Dict[str, Any]
        Results from capacity_analysis function
    title : str, default="Memory Capacity Analysis"
        Plot title
    figsize : Tuple[int, int], default=(15, 10)
        Figure size
    save_path : str, optional
        Path to save the plot
        
    Returns
    -------
    plt.Figure
        The created figure
    """
    item_counts = capacity_results['item_counts']
    retrieval_accuracy = capacity_results['retrieval_accuracy']
    storage_time = capacity_results['storage_time']
    retrieval_time = capacity_results['retrieval_time']
    memory_usage = capacity_results['memory_usage']
    capacity_estimate = capacity_results.get('capacity_estimate')
    
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    fig.suptitle(title, fontsize=16)
    
    # Retrieval accuracy vs item count
    axes[0, 0].plot(item_counts, retrieval_accuracy, 'bo-', linewidth=2, markersize=6)
    axes[0, 0].axhline(y=0.9, color='red', linestyle='--', alpha=0.7, label='90% threshold')
    if capacity_estimate:
        axes[0, 0].axvline(x=capacity_estimate, color='red', linestyle=':', alpha=0.7, 
                         label=f'Capacity estimate: {capacity_estimate}')
    axes[0, 0].set_xlabel('Number of Items')
    axes[0, 0].set_ylabel('Retrieval Accuracy')
    axes[0, 0].set_title('Retrieval Accuracy vs Capacity')
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].legend()
    axes[0, 0].set_ylim(0, 1.05)
    
    # Storage time vs item count
    axes[0, 1].plot(item_counts, storage_time, 'go-', linewidth=2, markersize=6)
    axes[0, 1].set_xlabel('Number of Items')
    axes[0, 1].set_ylabel('Storage Time (seconds)')
    axes[0, 1].set_title('Storage Time vs Item Count')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Retrieval time vs item count
    axes[1, 0].plot(item_counts, retrieval_time, 'mo-', linewidth=2, markersize=6)
    axes[1, 0].set_xlabel('Number of Items')
    axes[1, 0].set_ylabel('Retrieval Time (seconds)')
    axes[1, 0].set_title('Retrieval Time vs Item Count')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Memory usage vs item count
    axes[1, 1].plot(item_counts, memory_usage, 'co-', linewidth=2, markersize=6)
    axes[1, 1].set_xlabel('Number of Items')
    axes[1, 1].set_ylabel('Memory Usage (MB)')
    axes[1, 1].set_title('Memory Usage vs Item Count')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_noise_robustness(noise_results: Dict[str, Any],
                         title: str = "Noise Robustness Analysis",
                         figsize: Tuple[int, int] = (12, 5),
                         save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot noise robustness test results.
    
    Parameters
    ----------
    noise_results : Dict[str, Any]
        Results from noise_robustness_test function
    title : str, default="Noise Robustness Analysis"
        Plot title
    figsize : Tuple[int, int], default=(12, 5)
        Figure size
    save_path : str, optional
        Path to save the plot
        
    Returns
    -------
    plt.Figure
        The created figure
    """
    noise_levels = noise_results['noise_levels']
    retrieval_accuracy = noise_results['retrieval_accuracy']
    similarity_degradation = noise_results.get('similarity_degradation', [])
    
    fig, axes = plt.subplots(1, 2, figsize=figsize)
    fig.suptitle(title, fontsize=16)
    
    # Retrieval accuracy vs noise level
    axes[0].plot(noise_levels, retrieval_accuracy, 'ro-', linewidth=2, markersize=8)
    axes[0].set_xlabel('Noise Level')
    axes[0].set_ylabel('Retrieval Accuracy')
    axes[0].set_title('Accuracy vs Noise Level')
    axes[0].grid(True, alpha=0.3)
    axes[0].set_ylim(0, 1.05)
    
    # Add value annotations
    for x, y in zip(noise_levels, retrieval_accuracy):
        axes[0].annotate(f'{y:.3f}', (x, y), textcoords="offset points", 
                        xytext=(0,10), ha='center')
    
    # Similarity degradation
    if similarity_degradation:
        axes[1].plot(noise_levels, similarity_degradation, 'bo-', linewidth=2, markersize=8)
        axes[1].set_xlabel('Noise Level')
        axes[1].set_ylabel('Mean Similarity')
        axes[1].set_title('Similarity vs Noise Level')
        axes[1].grid(True, alpha=0.3)
        axes[1].set_ylim(0, 1.05)
        
        # Add value annotations
        for x, y in zip(noise_levels, similarity_degradation):
            axes[1].annotate(f'{y:.3f}', (x, y), textcoords="offset points", 
                            xytext=(0,10), ha='center')
    else:
        axes[1].text(0.5, 0.5, 'Similarity data\nnot available', 
                    ha='center', va='center', transform=axes[1].transAxes)
        axes[1].set_title('Similarity vs Noise Level')
    
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_cleanup_convergence(cleanup_results: List[Dict[str, Any]],
                           title: str = "Cleanup Convergence Analysis",
                           figsize: Tuple[int, int] = (12, 8),
                           save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot cleanup convergence results.
    
    Parameters
    ----------
    cleanup_results : List[Dict[str, Any]]
        List of cleanup result dictionaries
    title : str, default="Cleanup Convergence Analysis"
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
    # Extract data
    iterations = [result.get('iterations', 0) for result in cleanup_results]
    confidences = [result.get('confidence', 0) for result in cleanup_results]
    converged = [result.get('converged', False) for result in cleanup_results]
    similarities = [result.get('original_similarity', 0) for result in cleanup_results]
    
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    fig.suptitle(title, fontsize=16)
    
    # Iterations histogram
    axes[0, 0].hist(iterations, bins=max(1, max(iterations)), alpha=0.7, edgecolor='black')
    axes[0, 0].axvline(np.mean(iterations), color='red', linestyle='--', 
                      label=f'Mean: {np.mean(iterations):.1f}')
    axes[0, 0].set_xlabel('Number of Iterations')
    axes[0, 0].set_ylabel('Frequency')
    axes[0, 0].set_title('Cleanup Iterations Distribution')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Confidence histogram
    axes[0, 1].hist(confidences, bins=30, alpha=0.7, edgecolor='black')
    axes[0, 1].axvline(np.mean(confidences), color='red', linestyle='--',
                      label=f'Mean: {np.mean(confidences):.3f}')
    axes[0, 1].set_xlabel('Confidence Score')
    axes[0, 1].set_ylabel('Frequency')
    axes[0, 1].set_title('Cleanup Confidence Distribution')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # Convergence success rate
    convergence_rate = np.mean(converged)
    axes[1, 0].bar(['Converged', 'Not Converged'], 
                  [convergence_rate, 1 - convergence_rate],
                  color=['green', 'red'], alpha=0.7)
    axes[1, 0].set_ylabel('Proportion')
    axes[1, 0].set_title(f'Convergence Rate: {convergence_rate:.3f}')
    axes[1, 0].set_ylim(0, 1)
    axes[1, 0].grid(True, alpha=0.3)
    
    # Confidence vs iterations scatter
    colors = ['green' if c else 'red' for c in converged]
    scatter = axes[1, 1].scatter(iterations, confidences, c=colors, alpha=0.6, s=30)
    axes[1, 1].set_xlabel('Iterations')
    axes[1, 1].set_ylabel('Confidence')
    axes[1, 1].set_title('Confidence vs Iterations')
    axes[1, 1].grid(True, alpha=0.3)
    
    # Add legend
    import matplotlib.patches as mpatches
    green_patch = mpatches.Patch(color='green', label='Converged')
    red_patch = mpatches.Patch(color='red', label='Not Converged')
    axes[1, 1].legend(handles=[green_patch, red_patch])
    
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig


def plot_memory_statistics(statistics: Dict[str, Any],
                         title: str = "Memory System Statistics",
                         figsize: Tuple[int, int] = (15, 10),
                         save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot comprehensive memory system statistics.
    
    Parameters
    ----------
    statistics : Dict[str, Any]
        Statistics dictionary from memory system
    title : str, default="Memory System Statistics"
        Plot title
    figsize : Tuple[int, int], default=(15, 10)
        Figure size
    save_path : str, optional
        Path to save the plot
        
    Returns
    -------
    plt.Figure
        The created figure
    """
    fig, axes = plt.subplots(2, 3, figsize=figsize)
    fig.suptitle(title, fontsize=16)
    
    # Memory usage
    memory_stats = ['num_traces', 'capacity_utilization', 'total_stores', 'total_retrievals']
    memory_values = [statistics.get(stat, 0) for stat in memory_stats]
    memory_labels = ['# Traces', 'Capacity %', '# Stores', '# Retrievals']
    
    axes[0, 0].bar(memory_labels, memory_values)
    axes[0, 0].set_title('Memory Usage Statistics')
    axes[0, 0].tick_params(axis='x', rotation=45)
    axes[0, 0].grid(True, alpha=0.3)
    
    # Success rates
    retrieval_rate = statistics.get('retrieval_success_rate', 0)
    cleanup_rate = statistics.get('cleanup_success_rate', 0)
    
    axes[0, 1].bar(['Retrieval', 'Cleanup'], [retrieval_rate, cleanup_rate], 
                  color=['blue', 'orange'])
    axes[0, 1].set_ylabel('Success Rate')
    axes[0, 1].set_title('Success Rates')
    axes[0, 1].set_ylim(0, 1)
    axes[0, 1].grid(True, alpha=0.3)
    
    # Add value annotations
    axes[0, 1].text(0, retrieval_rate + 0.02, f'{retrieval_rate:.3f}', ha='center')
    axes[0, 1].text(1, cleanup_rate + 0.02, f'{cleanup_rate:.3f}', ha='center')
    
    # Operation counts
    operations = ['total_stores', 'successful_retrievals', 'cleanup_operations', 'successful_cleanups']
    op_values = [statistics.get(op, 0) for op in operations]
    op_labels = ['Stores', 'Retrievals', 'Cleanups', 'Successful\nCleanups']
    
    axes[0, 2].bar(op_labels, op_values, color=['green', 'blue', 'orange', 'red'])
    axes[0, 2].set_title('Operation Counts')
    axes[0, 2].tick_params(axis='x', rotation=45)
    axes[0, 2].grid(True, alpha=0.3)
    
    # System configuration
    config_items = ['vector_dim', 'cleanup_threshold', 'max_cleanup_iterations']
    config_values = [statistics.get(item, 0) for item in config_items]
    config_labels = ['Vector Dim', 'Cleanup\nThreshold', 'Max Cleanup\nIterations']
    
    axes[1, 0].bar(config_labels, config_values)
    axes[1, 0].set_title('System Configuration')
    axes[1, 0].tick_params(axis='x', rotation=45)
    axes[1, 0].grid(True, alpha=0.3)
    
    # Performance metrics
    avg_cleanup_iter = statistics.get('average_cleanup_iterations', 0)
    bind_ops = statistics.get('bind_operations', 0)
    unbind_ops = statistics.get('unbind_operations', 0)
    compose_ops = statistics.get('compose_operations', 0)
    
    perf_values = [avg_cleanup_iter, bind_ops, unbind_ops, compose_ops]
    perf_labels = ['Avg Cleanup\nIterations', 'Bind Ops', 'Unbind Ops', 'Compose Ops']
    
    axes[1, 1].bar(perf_labels, perf_values, color=['purple', 'cyan', 'magenta', 'yellow'])
    axes[1, 1].set_title('Performance Metrics')
    axes[1, 1].tick_params(axis='x', rotation=45)
    axes[1, 1].grid(True, alpha=0.3)
    
    # Memory efficiency pie chart
    if statistics.get('capacity_threshold'):
        used = statistics.get('num_traces', 0)
        available = statistics.get('capacity_threshold', 1) - used
        
        if used + available > 0:
            axes[1, 2].pie([used, available], labels=['Used', 'Available'], 
                          colors=['red', 'lightgreen'], autopct='%1.1f%%')
            axes[1, 2].set_title('Memory Capacity')
        else:
            axes[1, 2].text(0.5, 0.5, 'No capacity\ndata available', 
                           ha='center', va='center')
    else:
        axes[1, 2].text(0.5, 0.5, 'Unlimited\ncapacity', ha='center', va='center')
    
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    return fig