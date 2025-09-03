"""
🔗 Binding Operation Visualization for Tensor Product Binding
============================================================

This module provides visualization functions for binding operations,
including binding quality analysis, reconstruction accuracy, and
statistical analysis of binding performance.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Any, Optional, Tuple, Callable
import warnings


def plot_binding_operation(role: np.ndarray,
                          filler: np.ndarray,
                          bound: np.ndarray,
                          title: str = "Binding Operation Visualization",
                          figsize: Tuple[int, int] = (12, 8)) -> plt.Figure:
    """
    Visualize a tensor product binding operation.
    
    Parameters
    ----------
    role : np.ndarray
        Role vector
    filler : np.ndarray
        Filler vector
    bound : np.ndarray
        Bound vector result
    title : str, default="Binding Operation Visualization"
        Plot title
    figsize : Tuple[int, int], default=(12, 8)
        Figure size
        
    Returns
    -------
    plt.Figure
        Figure containing the binding operation visualization
    """
    fig, axes = plt.subplots(2, 3, figsize=figsize)
    fig.suptitle(title, fontsize=14, fontweight='bold')
    
    # Show first N dimensions for visualization
    max_dims = 50
    role_show = role[:max_dims] if len(role) > max_dims else role
    filler_show = filler[:max_dims] if len(filler) > max_dims else filler
    bound_show = bound[:max_dims] if len(bound) > max_dims else bound
    
    # 1. Role vector
    axes[0, 0].plot(role_show, 'b-', linewidth=2, label='Role')
    axes[0, 0].set_title(f'Role Vector (dim={len(role)})')
    axes[0, 0].set_xlabel('Dimension')
    axes[0, 0].set_ylabel('Value')
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].legend()
    
    # 2. Filler vector
    axes[0, 1].plot(filler_show, 'r-', linewidth=2, label='Filler')
    axes[0, 1].set_title(f'Filler Vector (dim={len(filler)})')
    axes[0, 1].set_xlabel('Dimension')
    axes[0, 1].set_ylabel('Value')
    axes[0, 1].grid(True, alpha=0.3)
    axes[0, 1].legend()
    
    # 3. Bound vector
    axes[0, 2].plot(bound_show, 'g-', linewidth=2, label='Bound')
    axes[0, 2].set_title(f'Bound Vector (dim={len(bound)})')
    axes[0, 2].set_xlabel('Dimension')
    axes[0, 2].set_ylabel('Value')
    axes[0, 2].grid(True, alpha=0.3)
    axes[0, 2].legend()
    
    # 4. Vector norms comparison
    norms = [np.linalg.norm(role), np.linalg.norm(filler), np.linalg.norm(bound)]
    names = ['Role', 'Filler', 'Bound']
    colors = ['blue', 'red', 'green']
    
    bars = axes[1, 0].bar(names, norms, color=colors, alpha=0.7)
    axes[1, 0].set_title('Vector Norms')
    axes[1, 0].set_ylabel('Norm')
    
    # Add value labels on bars
    for bar, norm in zip(bars, norms):
        axes[1, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                       f'{norm:.3f}', ha='center', va='bottom')
    
    # 5. Value distribution comparison
    axes[1, 1].hist(role, bins=20, alpha=0.5, label='Role', color='blue', density=True)
    axes[1, 1].hist(filler, bins=20, alpha=0.5, label='Filler', color='red', density=True)
    if len(bound) <= 1000:  # Only show bound histogram if not too large
        axes[1, 1].hist(bound, bins=20, alpha=0.5, label='Bound', color='green', density=True)
    axes[1, 1].set_title('Value Distributions')
    axes[1, 1].set_xlabel('Value')
    axes[1, 1].set_ylabel('Density')
    axes[1, 1].legend()
    
    # 6. Binding statistics
    stats_text = f"""
    Binding Operation Statistics:
    
    Role Vector:
    • Dimension: {len(role)}
    • Norm: {np.linalg.norm(role):.4f}
    • Mean: {np.mean(role):.4f}
    • Std: {np.std(role):.4f}
    
    Filler Vector:
    • Dimension: {len(filler)}
    • Norm: {np.linalg.norm(filler):.4f}
    • Mean: {np.mean(filler):.4f}
    • Std: {np.std(filler):.4f}
    
    Bound Vector:
    • Dimension: {len(bound)}
    • Norm: {np.linalg.norm(bound):.4f}
    • Mean: {np.mean(bound):.4f}
    • Std: {np.std(bound):.4f}
    
    Binding Quality:
    • Dim Expansion: {len(bound) / len(role):.1f}x
    • Expected Norm: {np.linalg.norm(role) * np.linalg.norm(filler):.4f}
    • Actual/Expected: {np.linalg.norm(bound) / (np.linalg.norm(role) * np.linalg.norm(filler)):.3f}
    """
    
    axes[1, 2].text(0.05, 0.95, stats_text, transform=axes[1, 2].transAxes,
                    fontsize=9, verticalalignment='top', fontfamily='monospace')
    axes[1, 2].set_title('Binding Statistics')
    axes[1, 2].axis('off')
    
    plt.tight_layout()
    return fig


def plot_unbinding_quality(role: np.ndarray,
                           original_filler: np.ndarray,
                           reconstructed_filler: np.ndarray,
                           title: str = "Unbinding Quality Analysis",
                           figsize: Tuple[int, int] = (12, 8)) -> plt.Figure:
    """
    Visualize the quality of an unbinding operation.
    
    Parameters
    ----------
    role : np.ndarray
        Role vector used for unbinding
    original_filler : np.ndarray
        Original filler vector
    reconstructed_filler : np.ndarray
        Reconstructed filler from unbinding
    title : str, default="Unbinding Quality Analysis"
        Plot title
    figsize : Tuple[int, int], default=(12, 8)
        Figure size
        
    Returns
    -------
    plt.Figure
        Figure containing unbinding quality analysis
    """
    fig, axes = plt.subplots(2, 3, figsize=figsize)
    fig.suptitle(title, fontsize=14, fontweight='bold')
    
    # Calculate quality metrics
    original_norm = np.linalg.norm(original_filler)
    reconstructed_norm = np.linalg.norm(reconstructed_filler)
    
    if original_norm > 0 and reconstructed_norm > 0:
        cosine_similarity = np.dot(original_filler, reconstructed_filler) / (original_norm * reconstructed_norm)
    else:
        cosine_similarity = 0.0
    
    reconstruction_error = np.linalg.norm(original_filler - reconstructed_filler)
    if original_norm > 0:
        relative_error = reconstruction_error / original_norm
    else:
        relative_error = reconstruction_error
    
    # Show first N dimensions for visualization
    max_dims = min(50, len(original_filler))
    
    # 1. Original vs Reconstructed overlay
    axes[0, 0].plot(original_filler[:max_dims], 'b-', linewidth=2, label='Original', alpha=0.8)
    axes[0, 0].plot(reconstructed_filler[:max_dims], 'r--', linewidth=2, label='Reconstructed', alpha=0.8)
    axes[0, 0].set_title('Original vs Reconstructed')
    axes[0, 0].set_xlabel('Dimension')
    axes[0, 0].set_ylabel('Value')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. Reconstruction error per dimension
    error_per_dim = np.abs(original_filler[:max_dims] - reconstructed_filler[:max_dims])
    axes[0, 1].bar(range(max_dims), error_per_dim, alpha=0.7, color='orange')
    axes[0, 1].set_title('Reconstruction Error (per dimension)')
    axes[0, 1].set_xlabel('Dimension')
    axes[0, 1].set_ylabel('Absolute Error')
    
    # 3. Scatter plot: Original vs Reconstructed
    axes[0, 2].scatter(original_filler, reconstructed_filler, alpha=0.6, s=20)
    
    # Add perfect reconstruction line
    min_val = min(np.min(original_filler), np.min(reconstructed_filler))
    max_val = max(np.max(original_filler), np.max(reconstructed_filler))
    axes[0, 2].plot([min_val, max_val], [min_val, max_val], 'r--', alpha=0.8, label='Perfect')
    
    axes[0, 2].set_title('Original vs Reconstructed Scatter')
    axes[0, 2].set_xlabel('Original Value')
    axes[0, 2].set_ylabel('Reconstructed Value')
    axes[0, 2].legend()
    axes[0, 2].grid(True, alpha=0.3)
    
    # 4. Quality metrics bar chart
    metrics = ['Cosine Sim.', 'Norm Ratio', '1 - Rel. Error']
    norm_ratio = reconstructed_norm / original_norm if original_norm > 0 else 0
    values = [cosine_similarity, norm_ratio, 1 - relative_error]
    colors = ['green' if v > 0.8 else 'orange' if v > 0.5 else 'red' for v in values]
    
    bars = axes[1, 0].bar(metrics, values, color=colors, alpha=0.7)
    axes[1, 0].set_title('Quality Metrics')
    axes[1, 0].set_ylabel('Score')
    axes[1, 0].set_ylim(0, 1.1)
    
    # Add value labels
    for bar, value in zip(bars, values):
        axes[1, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                       f'{value:.3f}', ha='center', va='bottom')
    
    # 5. Error distribution
    errors = original_filler - reconstructed_filler
    axes[1, 1].hist(errors, bins=30, alpha=0.7, density=True, color='purple')
    axes[1, 1].axvline(0, color='red', linestyle='--', alpha=0.8, label='Zero Error')
    axes[1, 1].set_title('Reconstruction Error Distribution')
    axes[1, 1].set_xlabel('Error')
    axes[1, 1].set_ylabel('Density')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    # 6. Quality summary
    quality_text = f"""
    Unbinding Quality Summary:
    
    Similarity Metrics:
    • Cosine Similarity: {cosine_similarity:.4f}
    • Correlation: {np.corrcoef(original_filler, reconstructed_filler)[0,1]:.4f}
    
    Error Metrics:
    • Absolute Error: {reconstruction_error:.4f}
    • Relative Error: {relative_error:.4f}
    • RMSE: {np.sqrt(np.mean(errors**2)):.4f}
    
    Norm Analysis:
    • Original Norm: {original_norm:.4f}
    • Reconstructed Norm: {reconstructed_norm:.4f}
    • Norm Ratio: {norm_ratio:.4f}
    
    Quality Assessment:
    {_assess_quality(cosine_similarity, relative_error)}
    """
    
    axes[1, 2].text(0.05, 0.95, quality_text, transform=axes[1, 2].transAxes,
                    fontsize=9, verticalalignment='top', fontfamily='monospace')
    axes[1, 2].set_title('Quality Summary')
    axes[1, 2].axis('off')
    
    plt.tight_layout()
    return fig


def plot_binding_statistics(binding_results: List[Dict[str, Any]],
                           title: str = "Binding Statistics Analysis",
                           figsize: Tuple[int, int] = (14, 10)) -> plt.Figure:
    """
    Plot statistics for multiple binding operations.
    
    Parameters
    ----------
    binding_results : List[Dict[str, Any]]
        List of binding result dictionaries
    title : str, default="Binding Statistics Analysis"
        Plot title
    figsize : Tuple[int, int], default=(14, 10)
        Figure size
        
    Returns
    -------
    plt.Figure
        Figure containing binding statistics
    """
    if not binding_results:
        raise ValueError("No binding results provided")
    
    fig, axes = plt.subplots(2, 3, figsize=figsize)
    fig.suptitle(title, fontsize=14, fontweight='bold')
    
    # Extract metrics from results
    metrics = {
        'fidelity': [],
        'error': [],
        'norm_ratio': [],
        'binding_strength': [],
        'dimensions': [],
        'success': []
    }
    
    for result in binding_results:
        metrics['fidelity'].append(result.get('reconstruction_fidelity', 0))
        metrics['error'].append(result.get('reconstruction_error', 1))
        metrics['norm_ratio'].append(result.get('expected_norm_ratio', 0))
        metrics['binding_strength'].append(result.get('binding_strength', 1))
        metrics['dimensions'].append(result.get('bound_vector_norm', 0))
        metrics['success'].append(result.get('unbinding_success', False))
    
    # 1. Fidelity distribution
    axes[0, 0].hist(metrics['fidelity'], bins=20, alpha=0.7, color='blue', edgecolor='black')
    axes[0, 0].axvline(np.mean(metrics['fidelity']), color='red', linestyle='--', 
                      label=f'Mean: {np.mean(metrics["fidelity"]):.3f}')
    axes[0, 0].set_title('Reconstruction Fidelity')
    axes[0, 0].set_xlabel('Cosine Similarity')
    axes[0, 0].set_ylabel('Frequency')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. Error distribution
    axes[0, 1].hist(metrics['error'], bins=20, alpha=0.7, color='red', edgecolor='black')
    axes[0, 1].axvline(np.mean(metrics['error']), color='blue', linestyle='--',
                      label=f'Mean: {np.mean(metrics["error"]):.3f}')
    axes[0, 1].set_title('Reconstruction Error')
    axes[0, 1].set_xlabel('Normalized Error')
    axes[0, 1].set_ylabel('Frequency')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # 3. Success rate
    success_rate = np.mean(metrics['success'])
    categories = ['Success', 'Failure']
    values = [success_rate, 1 - success_rate]
    colors = ['green', 'red']
    
    axes[0, 2].pie(values, labels=categories, colors=colors, autopct='%1.1f%%', startangle=90)
    axes[0, 2].set_title(f'Unbinding Success Rate\n({success_rate:.1%})')
    
    # 4. Fidelity vs Error scatter
    axes[1, 0].scatter(metrics['error'], metrics['fidelity'], alpha=0.6, s=30)
    axes[1, 0].set_xlabel('Reconstruction Error')
    axes[1, 0].set_ylabel('Reconstruction Fidelity')
    axes[1, 0].set_title('Error vs Fidelity')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Add correlation info
    if len(metrics['error']) > 1:
        correlation = np.corrcoef(metrics['error'], metrics['fidelity'])[0, 1]
        axes[1, 0].text(0.05, 0.95, f'Correlation: {correlation:.3f}',
                       transform=axes[1, 0].transAxes, bbox=dict(boxstyle='round', alpha=0.8))
    
    # 5. Performance over iterations (if applicable)
    if len(binding_results) > 1:
        x = range(len(binding_results))
        axes[1, 1].plot(x, metrics['fidelity'], 'bo-', label='Fidelity', alpha=0.7)
        axes[1, 1].plot(x, [1 - e for e in metrics['error']], 'ro-', label='1 - Error', alpha=0.7)
        axes[1, 1].set_xlabel('Binding Operation')
        axes[1, 1].set_ylabel('Quality Score')
        axes[1, 1].set_title('Quality Over Operations')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
    else:
        axes[1, 1].text(0.5, 0.5, 'Need multiple operations\nfor trend analysis',
                       ha='center', va='center', transform=axes[1, 1].transAxes)
        axes[1, 1].set_title('Quality Trends')
    
    # 6. Summary statistics table
    summary_stats = {
        'Metric': ['Mean Fidelity', 'Std Fidelity', 'Mean Error', 'Std Error', 
                  'Success Rate', 'Total Operations'],
        'Value': [
            f"{np.mean(metrics['fidelity']):.4f}",
            f"{np.std(metrics['fidelity']):.4f}",
            f"{np.mean(metrics['error']):.4f}",
            f"{np.std(metrics['error']):.4f}",
            f"{success_rate:.2%}",
            f"{len(binding_results)}"
        ]
    }
    
    # Create table
    axes[1, 2].axis('off')
    table_data = list(zip(summary_stats['Metric'], summary_stats['Value']))
    table = axes[1, 2].table(cellText=table_data, colLabels=['Metric', 'Value'],
                            cellLoc='left', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    axes[1, 2].set_title('Summary Statistics')
    
    plt.tight_layout()
    return fig


def plot_reconstruction_accuracy(dimensions: List[int],
                               accuracies: List[float],
                               title: str = "Reconstruction Accuracy vs Dimension",
                               figsize: Tuple[int, int] = (10, 6)) -> plt.Figure:
    """
    Plot reconstruction accuracy as a function of vector dimension.
    
    Parameters
    ----------
    dimensions : List[int]
        List of vector dimensions
    accuracies : List[float]
        Corresponding reconstruction accuracies
    title : str, default="Reconstruction Accuracy vs Dimension"
        Plot title
    figsize : Tuple[int, int], default=(10, 6)
        Figure size
        
    Returns
    -------
    plt.Figure
        Figure containing accuracy analysis
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    fig.suptitle(title, fontsize=14, fontweight='bold')
    
    # 1. Line plot
    ax1.plot(dimensions, accuracies, 'bo-', linewidth=2, markersize=6)
    ax1.set_xlabel('Vector Dimension')
    ax1.set_ylabel('Reconstruction Accuracy')
    ax1.set_title('Accuracy vs Dimension')
    ax1.grid(True, alpha=0.3)
    
    # Add trend line if enough points
    if len(dimensions) > 2:
        z = np.polyfit(dimensions, accuracies, 1)
        p = np.poly1d(z)
        ax1.plot(dimensions, p(dimensions), 'r--', alpha=0.8, label=f'Trend (slope={z[0]:.4f})')
        ax1.legend()
    
    # 2. Bar plot with color coding
    colors = ['green' if acc > 0.8 else 'orange' if acc > 0.6 else 'red' for acc in accuracies]
    bars = ax2.bar(range(len(dimensions)), accuracies, color=colors, alpha=0.7)
    
    ax2.set_xlabel('Dimension Index')
    ax2.set_ylabel('Reconstruction Accuracy')
    ax2.set_title('Accuracy by Dimension')
    ax2.set_xticks(range(len(dimensions)))
    ax2.set_xticklabels(dimensions, rotation=45)
    
    # Add value labels on bars
    for i, (bar, acc) in enumerate(zip(bars, accuracies)):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f'{acc:.3f}', ha='center', va='bottom', fontsize=8)
    
    # Add quality thresholds
    ax2.axhline(y=0.8, color='green', linestyle='--', alpha=0.5, label='Good (>0.8)')
    ax2.axhline(y=0.6, color='orange', linestyle='--', alpha=0.5, label='Fair (>0.6)')
    ax2.legend()
    
    plt.tight_layout()
    return fig


def _assess_quality(cosine_similarity: float, relative_error: float) -> str:
    """Helper function to assess reconstruction quality."""
    if cosine_similarity > 0.9 and relative_error < 0.1:
        return "• Excellent reconstruction quality"
    elif cosine_similarity > 0.8 and relative_error < 0.2:
        return "• Good reconstruction quality"
    elif cosine_similarity > 0.6 and relative_error < 0.4:
        return "• Fair reconstruction quality"
    else:
        return "• Poor reconstruction quality"