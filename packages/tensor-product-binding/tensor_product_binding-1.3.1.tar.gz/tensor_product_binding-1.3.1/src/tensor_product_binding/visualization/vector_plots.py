"""
🎯 Vector Visualization for Tensor Product Binding
==================================================

This module provides visualization functions for vectors and vector spaces
in the tensor product binding system. It includes plots for individual vectors,
vector comparisons, similarity matrices, and dimensionality reduction.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from typing import List, Dict, Optional, Tuple, Union
import warnings

try:
    from sklearn.decomposition import PCA
    from sklearn.manifold import TSNE
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    warnings.warn("scikit-learn not available, some visualization features will be limited")


def plot_vector(vector: np.ndarray,
               title: str = "Vector Visualization",
               figsize: Tuple[int, int] = (10, 6),
               show_stats: bool = True) -> plt.Figure:
    """
    Plot a single vector with multiple representations.
    
    Parameters
    ----------
    vector : np.ndarray
        Vector to visualize
    title : str, default="Vector Visualization"
        Plot title
    figsize : Tuple[int, int], default=(10, 6)
        Figure size
    show_stats : bool, default=True
        Whether to show vector statistics
        
    Returns
    -------
    plt.Figure
        Figure containing the visualization
    """
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    fig.suptitle(title, fontsize=14, fontweight='bold')
    
    # 1. Line plot of vector values
    axes[0, 0].plot(vector, 'b-', linewidth=1.5)
    axes[0, 0].set_title('Vector Values')
    axes[0, 0].set_xlabel('Dimension')
    axes[0, 0].set_ylabel('Value')
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. Bar plot for first 50 dimensions (if vector is long)
    dims_to_show = min(50, len(vector))
    axes[0, 1].bar(range(dims_to_show), vector[:dims_to_show], alpha=0.7)
    axes[0, 1].set_title(f'First {dims_to_show} Dimensions')
    axes[0, 1].set_xlabel('Dimension')
    axes[0, 1].set_ylabel('Value')
    
    # 3. Histogram of vector values
    axes[1, 0].hist(vector, bins=30, alpha=0.7, density=True, color='skyblue')
    axes[1, 0].set_title('Value Distribution')
    axes[1, 0].set_xlabel('Value')
    axes[1, 0].set_ylabel('Density')
    axes[1, 0].grid(True, alpha=0.3)
    
    # 4. Vector statistics
    if show_stats:
        stats_text = f"""
        Dimension: {len(vector)}
        Norm: {np.linalg.norm(vector):.4f}
        Mean: {np.mean(vector):.4f}
        Std: {np.std(vector):.4f}
        Min: {np.min(vector):.4f}
        Max: {np.max(vector):.4f}
        Sparsity: {np.sum(np.abs(vector) < 1e-6) / len(vector):.2%}
        """
        axes[1, 1].text(0.1, 0.5, stats_text, fontsize=10, 
                        transform=axes[1, 1].transAxes, verticalalignment='center')
        axes[1, 1].set_title('Statistics')
        axes[1, 1].axis('off')
    else:
        # Cumulative magnitude plot
        cumsum = np.cumsum(np.abs(vector))
        axes[1, 1].plot(cumsum / cumsum[-1], 'g-', linewidth=2)
        axes[1, 1].set_title('Cumulative Magnitude')
        axes[1, 1].set_xlabel('Dimension')
        axes[1, 1].set_ylabel('Cumulative Proportion')
        axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_vector_comparison(vectors: Dict[str, np.ndarray],
                          title: str = "Vector Comparison",
                          figsize: Tuple[int, int] = (12, 8)) -> plt.Figure:
    """
    Compare multiple vectors side by side.
    
    Parameters
    ----------
    vectors : Dict[str, np.ndarray]
        Dictionary of named vectors to compare
    title : str, default="Vector Comparison"
        Plot title
    figsize : Tuple[int, int], default=(12, 8)
        Figure size
        
    Returns
    -------
    plt.Figure
        Figure containing the comparison
    """
    n_vectors = len(vectors)
    if n_vectors == 0:
        raise ValueError("No vectors provided for comparison")
    
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    fig.suptitle(title, fontsize=14, fontweight='bold')
    
    vector_names = list(vectors.keys())
    vector_data = list(vectors.values())
    colors = plt.cm.tab10(np.linspace(0, 1, n_vectors))
    
    # 1. Overlay plot of all vectors
    for i, (name, vector) in enumerate(vectors.items()):
        axes[0, 0].plot(vector, color=colors[i], label=name, alpha=0.8)
    axes[0, 0].set_title('Vector Overlay')
    axes[0, 0].set_xlabel('Dimension')
    axes[0, 0].set_ylabel('Value')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. Norm comparison
    norms = [np.linalg.norm(v) for v in vector_data]
    bars = axes[0, 1].bar(vector_names, norms, color=colors)
    axes[0, 1].set_title('Vector Norms')
    axes[0, 1].set_ylabel('Norm')
    axes[0, 1].tick_params(axis='x', rotation=45)
    
    # Add value labels on bars
    for bar, norm in zip(bars, norms):
        axes[0, 1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                       f'{norm:.3f}', ha='center', va='bottom', fontsize=9)
    
    # 3. Similarity matrix (if more than one vector)
    if n_vectors > 1:
        similarity_matrix = np.zeros((n_vectors, n_vectors))
        for i in range(n_vectors):
            for j in range(n_vectors):
                if i == j:
                    similarity_matrix[i, j] = 1.0
                else:
                    norm_i = np.linalg.norm(vector_data[i])
                    norm_j = np.linalg.norm(vector_data[j])
                    if norm_i > 0 and norm_j > 0:
                        similarity_matrix[i, j] = np.dot(vector_data[i], vector_data[j]) / (norm_i * norm_j)
        
        im = axes[1, 0].imshow(similarity_matrix, cmap='coolwarm', vmin=-1, vmax=1)
        axes[1, 0].set_title('Similarity Matrix')
        axes[1, 0].set_xticks(range(n_vectors))
        axes[1, 0].set_yticks(range(n_vectors))
        axes[1, 0].set_xticklabels(vector_names, rotation=45)
        axes[1, 0].set_yticklabels(vector_names)
        
        # Add similarity values as text
        for i in range(n_vectors):
            for j in range(n_vectors):
                axes[1, 0].text(j, i, f'{similarity_matrix[i, j]:.2f}',
                               ha='center', va='center', fontsize=8)
        
        plt.colorbar(im, ax=axes[1, 0])
    else:
        axes[1, 0].text(0.5, 0.5, 'Need multiple vectors\nfor similarity analysis',
                       ha='center', va='center', transform=axes[1, 0].transAxes)
        axes[1, 0].set_title('Similarity Matrix')
    
    # 4. Statistics comparison
    stats = []
    for name, vector in vectors.items():
        stats.append({
            'Name': name,
            'Dimension': len(vector),
            'Norm': np.linalg.norm(vector),
            'Mean': np.mean(vector),
            'Std': np.std(vector),
            'Min': np.min(vector),
            'Max': np.max(vector)
        })
    
    # Create table
    table_data = []
    headers = ['Vector', 'Dim', 'Norm', 'Mean', 'Std', 'Min', 'Max']
    table_data.append(headers)
    
    for stat in stats:
        row = [
            stat['Name'][:10],  # Truncate long names
            f"{stat['Dimension']}",
            f"{stat['Norm']:.3f}",
            f"{stat['Mean']:.3f}",
            f"{stat['Std']:.3f}",
            f"{stat['Min']:.3f}",
            f"{stat['Max']:.3f}"
        ]
        table_data.append(row)
    
    axes[1, 1].axis('off')
    table = axes[1, 1].table(cellText=table_data[1:], colLabels=table_data[0],
                           cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 2)
    axes[1, 1].set_title('Vector Statistics')
    
    plt.tight_layout()
    return fig


def plot_similarity_matrix(vectors: Dict[str, np.ndarray],
                          title: str = "Vector Similarity Matrix",
                          figsize: Tuple[int, int] = (8, 6),
                          colormap: str = 'coolwarm') -> plt.Figure:
    """
    Plot similarity matrix for a set of vectors.
    
    Parameters
    ----------
    vectors : Dict[str, np.ndarray]
        Dictionary of named vectors
    title : str, default="Vector Similarity Matrix"
        Plot title
    figsize : Tuple[int, int], default=(8, 6)
        Figure size
    colormap : str, default='coolwarm'
        Colormap for the matrix
        
    Returns
    -------
    plt.Figure
        Figure containing the similarity matrix
    """
    if len(vectors) < 2:
        raise ValueError("Need at least 2 vectors for similarity matrix")
    
    vector_names = list(vectors.keys())
    vector_data = list(vectors.values())
    n_vectors = len(vectors)
    
    # Compute similarity matrix
    similarity_matrix = np.zeros((n_vectors, n_vectors))
    for i in range(n_vectors):
        for j in range(n_vectors):
            if i == j:
                similarity_matrix[i, j] = 1.0
            else:
                norm_i = np.linalg.norm(vector_data[i])
                norm_j = np.linalg.norm(vector_data[j])
                if norm_i > 0 and norm_j > 0:
                    similarity_matrix[i, j] = np.dot(vector_data[i], vector_data[j]) / (norm_i * norm_j)
    
    # Create plot
    fig, ax = plt.subplots(figsize=figsize)
    
    im = ax.imshow(similarity_matrix, cmap=colormap, vmin=-1, vmax=1)
    ax.set_title(title, fontsize=14, fontweight='bold')
    
    # Set ticks and labels
    ax.set_xticks(range(n_vectors))
    ax.set_yticks(range(n_vectors))
    ax.set_xticklabels(vector_names, rotation=45, ha='right')
    ax.set_yticklabels(vector_names)
    
    # Add similarity values as text
    for i in range(n_vectors):
        for j in range(n_vectors):
            text_color = 'white' if abs(similarity_matrix[i, j]) > 0.5 else 'black'
            ax.text(j, i, f'{similarity_matrix[i, j]:.2f}',
                   ha='center', va='center', color=text_color, fontweight='bold')
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Cosine Similarity', rotation=270, labelpad=20)
    
    plt.tight_layout()
    return fig


def plot_vector_space(vectors: Dict[str, np.ndarray],
                     title: str = "Vector Space Visualization",
                     method: str = 'pca',
                     figsize: Tuple[int, int] = (10, 8)) -> plt.Figure:
    """
    Visualize high-dimensional vector space using dimensionality reduction.
    
    Parameters
    ----------
    vectors : Dict[str, np.ndarray]
        Dictionary of named vectors
    title : str, default="Vector Space Visualization"
        Plot title
    method : str, default='pca'
        Dimensionality reduction method ('pca' or 'tsne')
    figsize : Tuple[int, int], default=(10, 8)
        Figure size
        
    Returns
    -------
    plt.Figure
        Figure containing the vector space visualization
    """
    if not SKLEARN_AVAILABLE:
        raise ImportError("scikit-learn is required for vector space visualization")
    
    if len(vectors) < 2:
        raise ValueError("Need at least 2 vectors for space visualization")
    
    vector_names = list(vectors.keys())
    vector_data = np.array(list(vectors.values()))
    
    # Apply dimensionality reduction
    if method.lower() == 'pca':
        reducer = PCA(n_components=2)
        reduced_data = reducer.fit_transform(vector_data)
        method_name = 'PCA'
        explained_var = reducer.explained_variance_ratio_
    elif method.lower() == 'tsne':
        if len(vectors) < 4:
            warnings.warn("t-SNE works better with more vectors, consider using PCA")
        reducer = TSNE(n_components=2, random_state=42)
        reduced_data = reducer.fit_transform(vector_data)
        method_name = 't-SNE'
        explained_var = None
    else:
        raise ValueError("Method must be 'pca' or 'tsne'")
    
    # Create plot
    fig, ax = plt.subplots(figsize=figsize)
    
    # Scatter plot
    scatter = ax.scatter(reduced_data[:, 0], reduced_data[:, 1], 
                        s=100, alpha=0.7, c=range(len(vectors)), cmap='tab10')
    
    # Add labels for each point
    for i, name in enumerate(vector_names):
        ax.annotate(name, (reduced_data[i, 0], reduced_data[i, 1]),
                   xytext=(5, 5), textcoords='offset points', fontsize=10)
    
    ax.set_title(f'{title} ({method_name})', fontsize=14, fontweight='bold')
    ax.set_xlabel(f'{method_name} Component 1')
    ax.set_ylabel(f'{method_name} Component 2')
    ax.grid(True, alpha=0.3)
    
    # Add explained variance for PCA
    if explained_var is not None:
        ax.text(0.02, 0.98, f'Explained Variance:\nPC1: {explained_var[0]:.1%}\nPC2: {explained_var[1]:.1%}',
               transform=ax.transAxes, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    return fig


def plot_pca_projection(vectors: Dict[str, np.ndarray],
                       n_components: int = None,
                       title: str = "PCA Analysis",
                       figsize: Tuple[int, int] = (12, 8)) -> plt.Figure:
    """
    Detailed PCA analysis of vector space.
    
    Parameters
    ----------
    vectors : Dict[str, np.ndarray]
        Dictionary of named vectors
    n_components : int, optional
        Number of PCA components (default: min(n_vectors, n_dims, 10))
    title : str, default="PCA Analysis"
        Plot title
    figsize : Tuple[int, int], default=(12, 8)
        Figure size
        
    Returns
    -------
    plt.Figure
        Figure containing PCA analysis
    """
    if not SKLEARN_AVAILABLE:
        raise ImportError("scikit-learn is required for PCA analysis")
    
    if len(vectors) < 2:
        raise ValueError("Need at least 2 vectors for PCA analysis")
    
    vector_names = list(vectors.keys())
    vector_data = np.array(list(vectors.values()))
    
    # Determine number of components
    if n_components is None:
        n_components = min(len(vectors), vector_data.shape[1], 10)
    
    # Fit PCA
    pca = PCA(n_components=n_components)
    reduced_data = pca.fit_transform(vector_data)
    
    # Create subplots
    fig = plt.figure(figsize=figsize)
    gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)
    
    # 1. Explained variance
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.bar(range(1, n_components + 1), pca.explained_variance_ratio_, alpha=0.7)
    ax1.set_title('Explained Variance Ratio')
    ax1.set_xlabel('Principal Component')
    ax1.set_ylabel('Variance Ratio')
    ax1.grid(True, alpha=0.3)
    
    # 2. Cumulative explained variance
    ax2 = fig.add_subplot(gs[0, 1])
    cumulative_var = np.cumsum(pca.explained_variance_ratio_)
    ax2.plot(range(1, n_components + 1), cumulative_var, 'bo-', linewidth=2, markersize=4)
    ax2.axhline(y=0.95, color='r', linestyle='--', alpha=0.7, label='95%')
    ax2.set_title('Cumulative Explained Variance')
    ax2.set_xlabel('Principal Component')
    ax2.set_ylabel('Cumulative Variance')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. 2D projection (PC1 vs PC2)
    ax3 = fig.add_subplot(gs[0, 2])
    scatter = ax3.scatter(reduced_data[:, 0], reduced_data[:, 1], 
                         s=100, alpha=0.7, c=range(len(vectors)), cmap='tab10')
    for i, name in enumerate(vector_names):
        ax3.annotate(name, (reduced_data[i, 0], reduced_data[i, 1]),
                    xytext=(5, 5), textcoords='offset points', fontsize=8)
    ax3.set_title('PC1 vs PC2 Projection')
    ax3.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%})')
    ax3.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%})')
    ax3.grid(True, alpha=0.3)
    
    # 4. Component loadings heatmap
    ax4 = fig.add_subplot(gs[1, :])
    
    # Show first few principal components
    n_show = min(5, n_components)
    loadings = pca.components_[:n_show, :min(50, vector_data.shape[1])]  # First 50 dimensions
    
    im = ax4.imshow(loadings, cmap='coolwarm', aspect='auto')
    ax4.set_title('Principal Component Loadings (First 50 Dimensions)')
    ax4.set_xlabel('Original Dimension')
    ax4.set_ylabel('Principal Component')
    ax4.set_yticks(range(n_show))
    ax4.set_yticklabels([f'PC{i+1}' for i in range(n_show)])
    
    cbar = plt.colorbar(im, ax=ax4)
    cbar.set_label('Loading Weight')
    
    fig.suptitle(title, fontsize=16, fontweight='bold')
    return fig