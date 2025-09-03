"""
🖱️ Interactive Visualization for Tensor Product Binding
=======================================================

This module provides interactive visualization tools for exploring
tensor product binding systems. These tools are designed for
research, debugging, and educational purposes.

Note: Interactive features may require additional dependencies
like ipywidgets for Jupyter notebooks.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Any, Optional, Callable, Tuple
import warnings

# Optional interactive dependencies
try:
    from matplotlib.widgets import Slider, Button, CheckButtons
    WIDGETS_AVAILABLE = True
except ImportError:
    WIDGETS_AVAILABLE = False
    warnings.warn("Matplotlib widgets not available, interactive features limited")

try:
    import ipywidgets as widgets
    from IPython.display import display
    JUPYTER_WIDGETS_AVAILABLE = True
except ImportError:
    JUPYTER_WIDGETS_AVAILABLE = False


def create_interactive_vector_explorer(vectors: Dict[str, np.ndarray],
                                     title: str = "Interactive Vector Explorer") -> Any:
    """
    Create an interactive tool for exploring vectors.
    
    Parameters
    ----------
    vectors : Dict[str, np.ndarray]
        Dictionary of named vectors to explore
    title : str, default="Interactive Vector Explorer"
        Title for the explorer
        
    Returns
    -------
    Any
        Interactive widget or matplotlib figure
    """
    if JUPYTER_WIDGETS_AVAILABLE:
        return _create_jupyter_vector_explorer(vectors, title)
    elif WIDGETS_AVAILABLE:
        return _create_matplotlib_vector_explorer(vectors, title)
    else:
        warnings.warn("No interactive capabilities available, returning static plot")
        return _create_static_vector_plot(vectors, title)


def create_binding_dashboard(binding_system: Any,
                           title: str = "Binding Operation Dashboard") -> Any:
    """
    Create an interactive dashboard for binding operations.
    
    Parameters
    ----------
    binding_system : Any
        Tensor product binding system instance
    title : str, default="Binding Operation Dashboard"
        Dashboard title
        
    Returns
    -------
    Any
        Interactive dashboard widget or figure
    """
    if JUPYTER_WIDGETS_AVAILABLE:
        return _create_jupyter_binding_dashboard(binding_system, title)
    else:
        warnings.warn("Jupyter widgets not available for full dashboard functionality")
        return _create_simple_binding_interface(binding_system, title)


def create_structure_inspector(structure_data: Dict[str, Any],
                              title: str = "Structure Inspector") -> Any:
    """
    Create an interactive tool for inspecting structural representations.
    
    Parameters
    ----------
    structure_data : Dict[str, Any]
        Structure data to inspect
    title : str, default="Structure Inspector"
        Inspector title
        
    Returns
    -------
    Any
        Interactive inspector widget or figure
    """
    if JUPYTER_WIDGETS_AVAILABLE:
        return _create_jupyter_structure_inspector(structure_data, title)
    else:
        return _create_static_structure_view(structure_data, title)


def _create_jupyter_vector_explorer(vectors: Dict[str, np.ndarray], 
                                   title: str) -> Any:
    """Create Jupyter-based interactive vector explorer."""
    if not JUPYTER_WIDGETS_AVAILABLE:
        return None
    
    vector_names = list(vectors.keys())
    
    # Create widgets
    vector_dropdown = widgets.Dropdown(
        options=vector_names,
        value=vector_names[0] if vector_names else None,
        description='Vector:',
    )
    
    plot_type_dropdown = widgets.Dropdown(
        options=['Line Plot', 'Bar Plot', 'Histogram', 'Statistics'],
        value='Line Plot',
        description='Plot Type:',
    )
    
    dim_range_slider = widgets.IntRangeSlider(
        value=[0, min(50, len(vectors[vector_names[0]]) if vector_names else 50)],
        min=0,
        max=len(vectors[vector_names[0]]) if vector_names else 100,
        step=1,
        description='Dimensions:',
    )
    
    output_widget = widgets.Output()
    
    def update_plot(vector_name, plot_type, dim_range):
        with output_widget:
            output_widget.clear_output(wait=True)
            
            if vector_name not in vectors:
                return
            
            vector = vectors[vector_name]
            start_dim, end_dim = dim_range
            vector_slice = vector[start_dim:end_dim]
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            if plot_type == 'Line Plot':
                ax.plot(range(start_dim, end_dim), vector_slice, 'b-', linewidth=2)
                ax.set_title(f'{vector_name} - Line Plot (dims {start_dim}-{end_dim})')
                ax.set_xlabel('Dimension')
                ax.set_ylabel('Value')
                
            elif plot_type == 'Bar Plot':
                ax.bar(range(start_dim, end_dim), vector_slice, alpha=0.7)
                ax.set_title(f'{vector_name} - Bar Plot (dims {start_dim}-{end_dim})')
                ax.set_xlabel('Dimension')
                ax.set_ylabel('Value')
                
            elif plot_type == 'Histogram':
                ax.hist(vector, bins=30, alpha=0.7, density=True)
                ax.set_title(f'{vector_name} - Value Distribution')
                ax.set_xlabel('Value')
                ax.set_ylabel('Density')
                
            elif plot_type == 'Statistics':
                stats_text = f"""
                Vector Statistics for {vector_name}:
                
                Dimension: {len(vector)}
                Norm: {np.linalg.norm(vector):.4f}
                Mean: {np.mean(vector):.4f}
                Std: {np.std(vector):.4f}
                Min: {np.min(vector):.4f}
                Max: {np.max(vector):.4f}
                Median: {np.median(vector):.4f}
                Sparsity: {np.sum(np.abs(vector) < 1e-6) / len(vector):.2%}
                """
                ax.text(0.1, 0.5, stats_text, transform=ax.transAxes,
                       fontfamily='monospace', fontsize=12, verticalalignment='center')
                ax.set_title(f'{vector_name} - Statistics')
                ax.axis('off')
            
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.show()
    
    # Create interactive widget
    interactive_widget = widgets.interact(
        update_plot,
        vector_name=vector_dropdown,
        plot_type=plot_type_dropdown,
        dim_range=dim_range_slider
    )
    
    # Display layout
    ui = widgets.VBox([
        widgets.HTML(f"<h3>{title}</h3>"),
        widgets.HBox([vector_dropdown, plot_type_dropdown]),
        dim_range_slider,
        output_widget
    ])
    
    display(ui)
    return ui


def _create_matplotlib_vector_explorer(vectors: Dict[str, np.ndarray], 
                                      title: str) -> plt.Figure:
    """Create matplotlib-based interactive vector explorer."""
    if not WIDGETS_AVAILABLE or not vectors:
        return _create_static_vector_plot(vectors, title)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    plt.subplots_adjust(bottom=0.3)
    
    vector_names = list(vectors.keys())
    current_vector_idx = [0]  # Use list for mutability in closure
    current_plot_type = ['line']  # 'line', 'bar', 'hist'
    
    def plot_current_vector():
        ax.clear()
        if current_vector_idx[0] >= len(vector_names):
            return
        
        vector_name = vector_names[current_vector_idx[0]]
        vector = vectors[vector_name]
        
        if current_plot_type[0] == 'line':
            ax.plot(vector, 'b-', linewidth=2)
            ax.set_title(f'{vector_name} - Line Plot')
            ax.set_xlabel('Dimension')
            ax.set_ylabel('Value')
            
        elif current_plot_type[0] == 'bar':
            max_dims = min(50, len(vector))
            ax.bar(range(max_dims), vector[:max_dims], alpha=0.7)
            ax.set_title(f'{vector_name} - Bar Plot (first {max_dims} dims)')
            ax.set_xlabel('Dimension')
            ax.set_ylabel('Value')
            
        elif current_plot_type[0] == 'hist':
            ax.hist(vector, bins=30, alpha=0.7, density=True)
            ax.set_title(f'{vector_name} - Value Distribution')
            ax.set_xlabel('Value')
            ax.set_ylabel('Density')
        
        ax.grid(True, alpha=0.3)
        plt.draw()
    
    # Create control buttons
    ax_next = plt.axes([0.7, 0.05, 0.1, 0.04])
    ax_prev = plt.axes([0.6, 0.05, 0.1, 0.04])
    ax_line = plt.axes([0.1, 0.05, 0.1, 0.04])
    ax_bar = plt.axes([0.2, 0.05, 0.1, 0.04])
    ax_hist = plt.axes([0.3, 0.05, 0.1, 0.04])
    
    button_next = Button(ax_next, 'Next')
    button_prev = Button(ax_prev, 'Prev')
    button_line = Button(ax_line, 'Line')
    button_bar = Button(ax_bar, 'Bar')
    button_hist = Button(ax_hist, 'Hist')
    
    def next_vector(event):
        current_vector_idx[0] = (current_vector_idx[0] + 1) % len(vector_names)
        plot_current_vector()
    
    def prev_vector(event):
        current_vector_idx[0] = (current_vector_idx[0] - 1) % len(vector_names)
        plot_current_vector()
    
    def set_line_plot(event):
        current_plot_type[0] = 'line'
        plot_current_vector()
    
    def set_bar_plot(event):
        current_plot_type[0] = 'bar'
        plot_current_vector()
    
    def set_hist_plot(event):
        current_plot_type[0] = 'hist'
        plot_current_vector()
    
    button_next.on_clicked(next_vector)
    button_prev.on_clicked(prev_vector)
    button_line.on_clicked(set_line_plot)
    button_bar.on_clicked(set_bar_plot)
    button_hist.on_clicked(set_hist_plot)
    
    # Initial plot
    plot_current_vector()
    
    plt.suptitle(title, fontsize=14, fontweight='bold')
    return fig


def _create_jupyter_binding_dashboard(binding_system: Any, title: str) -> Any:
    """Create Jupyter-based binding dashboard."""
    if not JUPYTER_WIDGETS_AVAILABLE:
        return None
    
    # Create input widgets
    role_input = widgets.Text(
        value='AGENT',
        placeholder='Enter role name',
        description='Role:',
    )
    
    filler_input = widgets.Text(
        value='John',
        placeholder='Enter filler name',
        description='Filler:',
    )
    
    bind_button = widgets.Button(
        description='Create Binding',
        button_style='success',
        icon='plus'
    )
    
    unbind_button = widgets.Button(
        description='Test Unbinding',
        button_style='info',
        icon='search'
    )
    
    output_widget = widgets.Output()
    
    def create_binding(button):
        with output_widget:
            output_widget.clear_output(wait=True)
            
            role_name = role_input.value.strip()
            filler_name = filler_input.value.strip()
            
            if not role_name or not filler_name:
                print("Please enter both role and filler names")
                return
            
            try:
                # Create binding
                bound_vector = binding_system.bind(role_name, filler_name)
                
                # Visualize result
                fig, axes = plt.subplots(1, 3, figsize=(15, 5))
                
                role_vec = binding_system.role_vectors[role_name]
                filler_vec = binding_system.filler_vectors[filler_name]
                
                # Plot role
                axes[0].plot(role_vec.data[:50], 'b-', linewidth=2)
                axes[0].set_title(f'Role: {role_name}')
                axes[0].set_xlabel('Dimension')
                axes[0].grid(True, alpha=0.3)
                
                # Plot filler
                axes[1].plot(filler_vec.data[:50], 'r-', linewidth=2)
                axes[1].set_title(f'Filler: {filler_name}')
                axes[1].set_xlabel('Dimension')
                axes[1].grid(True, alpha=0.3)
                
                # Plot bound (first 50 dims)
                axes[2].plot(bound_vector.data[:50], 'g-', linewidth=2)
                axes[2].set_title(f'Bound: {role_name}⊗{filler_name}')
                axes[2].set_xlabel('Dimension')
                axes[2].grid(True, alpha=0.3)
                
                plt.tight_layout()
                plt.show()
                
                print(f"✅ Binding created: {role_name} ⊗ {filler_name}")
                print(f"Bound vector norm: {bound_vector.norm:.4f}")
                
            except Exception as e:
                print(f"❌ Error creating binding: {e}")
    
    def test_unbinding(button):
        with output_widget:
            role_name = role_input.value.strip()
            filler_name = filler_input.value.strip()
            
            if not role_name or not filler_name:
                print("Please enter both role and filler names")
                return
            
            try:
                # Create binding and test unbinding
                bound_vector = binding_system.bind(role_name, filler_name)
                role_vec = binding_system.role_vectors[role_name]
                original_filler = binding_system.filler_vectors[filler_name]
                
                reconstructed = binding_system.unbind(bound_vector, role_vec)
                
                if reconstructed is not None:
                    fidelity = original_filler.similarity(reconstructed)
                    
                    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
                    
                    # Original vs reconstructed
                    max_dims = min(50, len(original_filler.data))
                    axes[0].plot(original_filler.data[:max_dims], 'b-', 
                               linewidth=2, label='Original', alpha=0.8)
                    axes[0].plot(reconstructed.data[:max_dims], 'r--', 
                               linewidth=2, label='Reconstructed', alpha=0.8)
                    axes[0].set_title('Unbinding Quality')
                    axes[0].set_xlabel('Dimension')
                    axes[0].legend()
                    axes[0].grid(True, alpha=0.3)
                    
                    # Quality metrics
                    quality_text = f"""
                    Unbinding Results:
                    
                    Reconstruction Fidelity: {fidelity:.4f}
                    Original Norm: {original_filler.norm:.4f}
                    Reconstructed Norm: {reconstructed.norm:.4f}
                    
                    Quality Assessment:
                    {'✅ Excellent' if fidelity > 0.9 else
                     '🟡 Good' if fidelity > 0.7 else
                     '🟠 Fair' if fidelity > 0.5 else
                     '❌ Poor'}
                    """
                    
                    axes[1].text(0.1, 0.5, quality_text, transform=axes[1].transAxes,
                               fontfamily='monospace', fontsize=11, verticalalignment='center')
                    axes[1].set_title('Quality Assessment')
                    axes[1].axis('off')
                    
                    plt.tight_layout()
                    plt.show()
                else:
                    print("❌ Unbinding failed")
                    
            except Exception as e:
                print(f"❌ Error in unbinding test: {e}")
    
    bind_button.on_click(create_binding)
    unbind_button.on_click(test_unbinding)
    
    # Create dashboard layout
    dashboard = widgets.VBox([
        widgets.HTML(f"<h3>{title}</h3>"),
        widgets.HBox([role_input, filler_input]),
        widgets.HBox([bind_button, unbind_button]),
        output_widget
    ])
    
    display(dashboard)
    return dashboard


def _create_simple_binding_interface(binding_system: Any, title: str) -> plt.Figure:
    """Create simple matplotlib-based binding interface."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.text(0.5, 0.5, f"{title}\n\nInteractive binding dashboard requires\nJupyter widgets for full functionality.\n\nUse the binding system directly:\nbinding_system.bind('role', 'filler')",
           ha='center', va='center', transform=ax.transAxes, fontsize=12)
    ax.set_title(title)
    ax.axis('off')
    
    return fig


def _create_jupyter_structure_inspector(structure_data: Dict[str, Any], 
                                       title: str) -> Any:
    """Create Jupyter-based structure inspector."""
    if not JUPYTER_WIDGETS_AVAILABLE:
        return None
    
    # Structure exploration widgets
    structure_keys = list(structure_data.keys())
    key_dropdown = widgets.Dropdown(
        options=structure_keys,
        value=structure_keys[0] if structure_keys else None,
        description='Structure:',
    )
    
    detail_level = widgets.IntSlider(
        value=2,
        min=1,
        max=5,
        step=1,
        description='Detail Level:',
    )
    
    output_widget = widgets.Output()
    
    def inspect_structure(key, level):
        with output_widget:
            output_widget.clear_output(wait=True)
            
            if key not in structure_data:
                return
            
            structure = structure_data[key]
            
            # Display structure information
            print(f"🔍 Inspecting: {key}")
            print("=" * 40)
            
            _display_structure_recursive(structure, level=level, max_level=level)
    
    def _display_structure_recursive(obj, level=0, max_level=2, indent=""):
        if level > max_level:
            print(f"{indent}... (truncated)")
            return
        
        if isinstance(obj, dict):
            print(f"{indent}Dict with {len(obj)} keys:")
            for k, v in list(obj.items())[:10]:  # Show first 10 items
                print(f"{indent}  {k}:")
                _display_structure_recursive(v, level+1, max_level, indent+"    ")
            if len(obj) > 10:
                print(f"{indent}  ... and {len(obj)-10} more items")
                
        elif isinstance(obj, (list, tuple)):
            print(f"{indent}{type(obj).__name__} with {len(obj)} items:")
            for i, item in enumerate(obj[:5]):  # Show first 5 items
                print(f"{indent}  [{i}]:")
                _display_structure_recursive(item, level+1, max_level, indent+"    ")
            if len(obj) > 5:
                print(f"{indent}  ... and {len(obj)-5} more items")
                
        elif isinstance(obj, np.ndarray):
            print(f"{indent}Array: shape={obj.shape}, dtype={obj.dtype}")
            if obj.size <= 10:
                print(f"{indent}  Values: {obj}")
            else:
                print(f"{indent}  First 5: {obj.flatten()[:5]}")
                
        else:
            str_repr = str(obj)
            if len(str_repr) > 100:
                str_repr = str_repr[:100] + "..."
            print(f"{indent}{type(obj).__name__}: {str_repr}")
    
    # Create interactive widget
    interactive_widget = widgets.interact(
        inspect_structure,
        key=key_dropdown,
        level=detail_level
    )
    
    # Display layout
    ui = widgets.VBox([
        widgets.HTML(f"<h3>{title}</h3>"),
        widgets.HBox([key_dropdown, detail_level]),
        output_widget
    ])
    
    display(ui)
    return ui


def _create_static_vector_plot(vectors: Dict[str, np.ndarray], title: str) -> plt.Figure:
    """Create static vector visualization as fallback."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle(f"{title} (Static View)", fontsize=14, fontweight='bold')
    
    if not vectors:
        axes[0, 0].text(0.5, 0.5, "No vectors provided", ha='center', va='center')
        return fig
    
    vector_names = list(vectors.keys())[:4]  # Show first 4 vectors
    
    for i, name in enumerate(vector_names):
        ax = axes[i//2, i%2]
        vector = vectors[name]
        
        # Show first 50 dimensions
        dims_to_show = min(50, len(vector))
        ax.plot(vector[:dims_to_show], linewidth=2)
        ax.set_title(f'{name} (dims 0-{dims_to_show})')
        ax.set_xlabel('Dimension')
        ax.set_ylabel('Value')
        ax.grid(True, alpha=0.3)
    
    # Hide unused subplots
    for i in range(len(vector_names), 4):
        axes[i//2, i%2].axis('off')
    
    plt.tight_layout()
    return fig


def _create_static_structure_view(structure_data: Dict[str, Any], title: str) -> plt.Figure:
    """Create static structure visualization as fallback."""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    structure_text = f"{title}\n{'='*len(title)}\n\n"
    
    for key, value in structure_data.items():
        structure_text += f"{key}:\n"
        if isinstance(value, dict):
            structure_text += f"  Dict with {len(value)} keys\n"
        elif isinstance(value, (list, tuple)):
            structure_text += f"  {type(value).__name__} with {len(value)} items\n"
        elif isinstance(value, np.ndarray):
            structure_text += f"  Array: shape={value.shape}\n"
        else:
            structure_text += f"  {type(value).__name__}: {str(value)[:50]}...\n"
        structure_text += "\n"
    
    ax.text(0.05, 0.95, structure_text, transform=ax.transAxes,
           fontfamily='monospace', fontsize=10, verticalalignment='top')
    ax.set_title(title)
    ax.axis('off')
    
    return fig