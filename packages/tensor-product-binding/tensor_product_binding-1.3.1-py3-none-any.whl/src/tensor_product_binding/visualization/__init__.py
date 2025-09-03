"""
📊 Visualization Module for Tensor Product Binding
==================================================

This module provides visualization utilities for the tensor product binding
system. It includes functions for plotting vectors, binding operations,
structural representations, and analysis results.

Main Components:
- Vector visualization and similarity plots
- Binding operation visualizations
- Structural representation diagrams
- Analysis result plots
- Interactive visualization tools
"""

from .vector_plots import (
    plot_vector,
    plot_vector_comparison,
    plot_similarity_matrix,
    plot_vector_space,
    plot_pca_projection
)
from .binding_plots import (
    plot_binding_operation,
    plot_unbinding_quality,
    plot_binding_statistics,
    plot_reconstruction_accuracy
)
from .structure_plots import (
    plot_structure_tree,
    plot_compositional_structure,
    plot_hierarchical_binding,
    plot_semantic_network
)
from .analysis_plots import (
    plot_quality_metrics,
    plot_complexity_analysis,
    plot_coherence_analysis,
    plot_performance_benchmark
)
from .interactive import (
    create_interactive_vector_explorer,
    create_binding_dashboard,
    create_structure_inspector
)

__all__ = [
    # Vector plots
    'plot_vector',
    'plot_vector_comparison', 
    'plot_similarity_matrix',
    'plot_vector_space',
    'plot_pca_projection',
    
    # Binding plots
    'plot_binding_operation',
    'plot_unbinding_quality',
    'plot_binding_statistics',
    'plot_reconstruction_accuracy',
    
    # Structure plots
    'plot_structure_tree',
    'plot_compositional_structure', 
    'plot_hierarchical_binding',
    'plot_semantic_network',
    
    # Analysis plots
    'plot_quality_metrics',
    'plot_complexity_analysis',
    'plot_coherence_analysis', 
    'plot_performance_benchmark',
    
    # Interactive
    'create_interactive_vector_explorer',
    'create_binding_dashboard',
    'create_structure_inspector'
]