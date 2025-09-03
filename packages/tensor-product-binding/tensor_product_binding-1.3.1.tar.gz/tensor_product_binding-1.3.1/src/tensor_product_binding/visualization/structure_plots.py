"""
🏗️ Structure Visualization for Tensor Product Binding
=====================================================

This module provides visualization functions for structural representations
in tensor product binding, including tree structures, compositional
hierarchies, and semantic networks.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Any, Optional, Tuple, Union
import warnings

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    warnings.warn("NetworkX not available, some structure visualizations will be limited")


def plot_structure_tree(structure: Dict[str, Any],
                        title: str = "Structure Tree",
                        figsize: Tuple[int, int] = (12, 8)) -> plt.Figure:
    """
    Plot a hierarchical structure as a tree diagram.
    
    Parameters
    ----------
    structure : Dict[str, Any]
        Hierarchical structure to visualize
    title : str, default="Structure Tree"
        Plot title
    figsize : Tuple[int, int], default=(12, 8)
        Figure size
        
    Returns
    -------
    plt.Figure
        Figure containing tree visualization
    """
    if not NETWORKX_AVAILABLE:
        # Fallback to text-based visualization
        fig, ax = plt.subplots(figsize=figsize)
        ax.text(0.5, 0.5, _structure_to_text(structure),
               ha='center', va='center', transform=ax.transAxes,
               fontfamily='monospace', fontsize=10)
        ax.set_title(title)
        ax.axis('off')
        return fig
    
    # Create directed graph
    G = nx.DiGraph()
    labels = {}
    
    def _add_nodes_edges(node_data, parent_id=None, level=0):
        if isinstance(node_data, dict):
            for key, value in node_data.items():
                node_id = f"{key}_{level}_{id(value)}"
                G.add_node(node_id, level=level)
                labels[node_id] = str(key)
                
                if parent_id:
                    G.add_edge(parent_id, node_id)
                
                _add_nodes_edges(value, node_id, level + 1)
        
        elif isinstance(node_data, (list, tuple)):
            for i, item in enumerate(node_data):
                node_id = f"item_{i}_{level}_{id(item)}"
                G.add_node(node_id, level=level)
                labels[node_id] = f"[{i}]"
                
                if parent_id:
                    G.add_edge(parent_id, node_id)
                
                _add_nodes_edges(item, node_id, level + 1)
        
        else:
            # Leaf node
            node_id = f"leaf_{level}_{id(node_data)}"
            G.add_node(node_id, level=level)
            labels[node_id] = str(node_data)[:20]  # Truncate long values
            
            if parent_id:
                G.add_edge(parent_id, node_id)
    
    _add_nodes_edges(structure)
    
    if len(G.nodes()) == 0:
        fig, ax = plt.subplots(figsize=figsize)
        ax.text(0.5, 0.5, "Empty structure", ha='center', va='center')
        ax.set_title(title)
        ax.axis('off')
        return fig
    
    # Create hierarchical layout
    pos = {}
    level_nodes = {}
    
    # Group nodes by level
    for node, data in G.nodes(data=True):
        level = data.get('level', 0)
        if level not in level_nodes:
            level_nodes[level] = []
        level_nodes[level].append(node)
    
    # Position nodes
    max_level = max(level_nodes.keys()) if level_nodes else 0
    for level, nodes in level_nodes.items():
        y = 1.0 - (level / max_level) if max_level > 0 else 0.5
        for i, node in enumerate(nodes):
            x = (i + 1) / (len(nodes) + 1)
            pos[node] = (x, y)
    
    # Create plot
    fig, ax = plt.subplots(figsize=figsize)
    
    # Draw graph
    nx.draw(G, pos, ax=ax, with_labels=True, labels=labels,
            node_color='lightblue', node_size=1000, font_size=8,
            edge_color='gray', arrows=True, arrowsize=20)
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    plt.tight_layout()
    return fig


def plot_compositional_structure(bindings: List[Tuple[str, str, np.ndarray]],
                                title: str = "Compositional Structure",
                                figsize: Tuple[int, int] = (12, 8)) -> plt.Figure:
    """
    Visualize compositional binding structure.
    
    Parameters
    ----------
    bindings : List[Tuple[str, str, np.ndarray]]
        List of (role, filler, bound_vector) tuples
    title : str, default="Compositional Structure"
        Plot title
    figsize : Tuple[int, int], default=(12, 8)
        Figure size
        
    Returns
    -------
    plt.Figure
        Figure containing compositional structure
    """
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    fig.suptitle(title, fontsize=14, fontweight='bold')
    
    if not bindings:
        axes[0, 0].text(0.5, 0.5, "No bindings provided", ha='center', va='center')
        axes[0, 0].set_title("Structure Overview")
        return fig
    
    roles = [b[0] for b in bindings]
    fillers = [b[1] for b in bindings]
    bound_vectors = [b[2] for b in bindings]
    
    # 1. Role-Filler binding network
    if NETWORKX_AVAILABLE:
        G = nx.Graph()
        
        # Add nodes
        for role, filler, _ in bindings:
            G.add_node(f"R:{role}", type='role')
            G.add_node(f"F:{filler}", type='filler')
            G.add_edge(f"R:{role}", f"F:{filler}")
        
        # Position nodes
        pos = nx.spring_layout(G, k=1, iterations=50)
        
        # Color nodes by type
        node_colors = ['lightcoral' if data.get('type') == 'role' else 'lightblue' 
                      for node, data in G.nodes(data=True)]
        
        nx.draw(G, pos, ax=axes[0, 0], with_labels=True, node_color=node_colors,
               node_size=800, font_size=8, edge_color='gray')
        axes[0, 0].set_title("Role-Filler Network")
    else:
        # Fallback visualization
        axes[0, 0].text(0.5, 0.5, f"Roles: {', '.join(roles)}\nFillers: {', '.join(fillers)}",
                       ha='center', va='center', transform=axes[0, 0].transAxes)
        axes[0, 0].set_title("Role-Filler Pairs")
        axes[0, 0].axis('off')
    
    # 2. Binding strength analysis
    norms = [np.linalg.norm(bv) for bv in bound_vectors]
    indices = range(len(bindings))
    
    bars = axes[0, 1].bar(indices, norms, alpha=0.7, color='green')
    axes[0, 1].set_title("Binding Strengths")
    axes[0, 1].set_xlabel("Binding Index")
    axes[0, 1].set_ylabel("Vector Norm")
    axes[0, 1].set_xticks(indices)
    axes[0, 1].set_xticklabels([f"{r}⊗{f}" for r, f in zip(roles, fillers)], 
                              rotation=45, ha='right')
    
    # Add value labels
    for bar, norm in zip(bars, norms):
        axes[0, 1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                       f'{norm:.2f}', ha='center', va='bottom', fontsize=8)
    
    # 3. Compositional complexity
    if len(bound_vectors) > 1:
        # Compute pairwise similarities
        n = len(bound_vectors)
        similarities = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i == j:
                    similarities[i, j] = 1.0
                else:
                    v1, v2 = bound_vectors[i], bound_vectors[j]
                    norm1, norm2 = np.linalg.norm(v1), np.linalg.norm(v2)
                    if norm1 > 0 and norm2 > 0:
                        similarities[i, j] = np.dot(v1, v2) / (norm1 * norm2)
        
        im = axes[1, 0].imshow(similarities, cmap='coolwarm', vmin=-1, vmax=1)
        axes[1, 0].set_title("Binding Similarities")
        axes[1, 0].set_xticks(indices)
        axes[1, 0].set_yticks(indices)
        axes[1, 0].set_xticklabels([f"{r}⊗{f}" for r, f in zip(roles, fillers)], 
                                  rotation=45, ha='right')
        axes[1, 0].set_yticklabels([f"{r}⊗{f}" for r, f in zip(roles, fillers)])
        
        plt.colorbar(im, ax=axes[1, 0])
    else:
        axes[1, 0].text(0.5, 0.5, "Need multiple bindings\nfor similarity analysis",
                       ha='center', va='center', transform=axes[1, 0].transAxes)
        axes[1, 0].set_title("Binding Similarities")
    
    # 4. Structure statistics
    stats_text = f"""
    Compositional Structure Statistics:
    
    Number of Bindings: {len(bindings)}
    Unique Roles: {len(set(roles))}
    Unique Fillers: {len(set(fillers))}
    
    Binding Norms:
    • Mean: {np.mean(norms):.3f}
    • Std: {np.std(norms):.3f}
    • Min: {np.min(norms):.3f}
    • Max: {np.max(norms):.3f}
    
    Role-Filler Distribution:
    • Most frequent role: {max(set(roles), key=roles.count)}
    • Most frequent filler: {max(set(fillers), key=fillers.count)}
    • Avg binding dimension: {np.mean([len(bv) for bv in bound_vectors]):.0f}
    """
    
    axes[1, 1].text(0.05, 0.95, stats_text, transform=axes[1, 1].transAxes,
                    fontsize=9, verticalalignment='top', fontfamily='monospace')
    axes[1, 1].set_title("Structure Statistics")
    axes[1, 1].axis('off')
    
    plt.tight_layout()
    return fig


def plot_hierarchical_binding(hierarchy: Dict[str, Any],
                             title: str = "Hierarchical Binding Structure",
                             figsize: Tuple[int, int] = (10, 8)) -> plt.Figure:
    """
    Visualize hierarchical binding structure.
    
    Parameters
    ----------
    hierarchy : Dict[str, Any]
        Hierarchical structure with nested bindings
    title : str, default="Hierarchical Binding Structure"
        Plot title
    figsize : Tuple[int, int], default=(10, 8)
        Figure size
        
    Returns
    -------
    plt.Figure
        Figure containing hierarchical visualization
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Extract hierarchy information
    levels = _extract_hierarchy_levels(hierarchy)
    max_level = max(levels.keys()) if levels else 0
    
    if max_level == 0:
        ax.text(0.5, 0.5, "No hierarchical structure found", 
               ha='center', va='center', transform=ax.transAxes)
        ax.set_title(title)
        ax.axis('off')
        return fig
    
    # Create hierarchical visualization
    colors = plt.cm.viridis(np.linspace(0, 1, max_level + 1))
    
    y_positions = {}
    for level in range(max_level + 1):
        y_positions[level] = 1.0 - (level / max_level)
    
    # Plot nodes by level
    for level, nodes in levels.items():
        y = y_positions[level]
        n_nodes = len(nodes)
        
        for i, (node_name, node_data) in enumerate(nodes.items()):
            x = (i + 1) / (n_nodes + 1)
            
            # Draw node
            circle = plt.Circle((x, y), 0.03, color=colors[level], alpha=0.7)
            ax.add_patch(circle)
            
            # Add label
            ax.text(x, y - 0.08, node_name[:10], ha='center', va='top', fontsize=8)
            
            # Draw connections to children (if any)
            if isinstance(node_data, dict):
                child_level = level + 1
                if child_level in levels:
                    child_y = y_positions[child_level]
                    child_nodes = list(node_data.keys()) if hasattr(node_data, 'keys') else []
                    
                    for j, child_name in enumerate(child_nodes):
                        if child_name in levels.get(child_level, {}):
                            child_x = (j + 1) / (len(levels[child_level]) + 1)
                            ax.plot([x, child_x], [y - 0.03, child_y + 0.03], 
                                   'k-', alpha=0.5, linewidth=1)
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.axis('off')
    
    # Add level labels
    for level, y in y_positions.items():
        ax.text(0.02, y, f"Level {level}", fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    return fig


def plot_semantic_network(associations: Dict[str, List[str]],
                         title: str = "Semantic Network",
                         figsize: Tuple[int, int] = (12, 8)) -> plt.Figure:
    """
    Plot semantic associations as a network graph.
    
    Parameters
    ----------
    associations : Dict[str, List[str]]
        Dictionary of concept associations
    title : str, default="Semantic Network"
        Plot title
    figsize : Tuple[int, int], default=(12, 8)
        Figure size
        
    Returns
    -------
    plt.Figure
        Figure containing semantic network
    """
    if not NETWORKX_AVAILABLE:
        # Fallback text-based visualization
        fig, ax = plt.subplots(figsize=figsize)
        network_text = "\n".join([f"{concept}: {', '.join(assoc)}" 
                                 for concept, assoc in associations.items()])
        ax.text(0.1, 0.9, network_text, transform=ax.transAxes, fontfamily='monospace',
               fontsize=10, verticalalignment='top')
        ax.set_title(title)
        ax.axis('off')
        return fig
    
    # Create network graph
    G = nx.Graph()
    
    # Add nodes and edges
    for concept, related_concepts in associations.items():
        G.add_node(concept)
        for related in related_concepts:
            G.add_node(related)
            G.add_edge(concept, related)
    
    if len(G.nodes()) == 0:
        fig, ax = plt.subplots(figsize=figsize)
        ax.text(0.5, 0.5, "No associations provided", ha='center', va='center')
        ax.set_title(title)
        ax.axis('off')
        return fig
    
    # Calculate node properties
    degree_centrality = nx.degree_centrality(G)
    betweenness_centrality = nx.betweenness_centrality(G)
    
    # Node sizes based on degree centrality
    node_sizes = [3000 * degree_centrality[node] + 500 for node in G.nodes()]
    
    # Node colors based on betweenness centrality
    node_colors = [betweenness_centrality[node] for node in G.nodes()]
    
    # Create layout
    pos = nx.spring_layout(G, k=2, iterations=50)
    
    # Create plot
    fig, ax = plt.subplots(figsize=figsize)
    
    # Draw network
    nx.draw(G, pos, ax=ax, with_labels=True, node_size=node_sizes,
           node_color=node_colors, cmap='viridis', font_size=8,
           edge_color='gray', alpha=0.7)
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    
    # Add colorbar for centrality
    sm = plt.cm.ScalarMappable(cmap='viridis', 
                              norm=plt.Normalize(vmin=min(node_colors), 
                                               vmax=max(node_colors)))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax)
    cbar.set_label('Betweenness Centrality')
    
    plt.tight_layout()
    return fig


def _structure_to_text(structure: Any, indent: int = 0) -> str:
    """Convert structure to indented text representation."""
    indent_str = "  " * indent
    
    if isinstance(structure, dict):
        lines = []
        for key, value in structure.items():
            if isinstance(value, (dict, list, tuple)):
                lines.append(f"{indent_str}{key}:")
                lines.append(_structure_to_text(value, indent + 1))
            else:
                lines.append(f"{indent_str}{key}: {value}")
        return "\n".join(lines)
    
    elif isinstance(structure, (list, tuple)):
        lines = []
        for i, item in enumerate(structure):
            if isinstance(item, (dict, list, tuple)):
                lines.append(f"{indent_str}[{i}]:")
                lines.append(_structure_to_text(item, indent + 1))
            else:
                lines.append(f"{indent_str}[{i}]: {item}")
        return "\n".join(lines)
    
    else:
        return f"{indent_str}{structure}"


def _extract_hierarchy_levels(hierarchy: Dict[str, Any]) -> Dict[int, Dict[str, Any]]:
    """Extract nodes by hierarchical level."""
    levels = {}
    
    def _traverse(node_data, level=0):
        if level not in levels:
            levels[level] = {}
        
        if isinstance(node_data, dict):
            for key, value in node_data.items():
                levels[level][key] = value
                if isinstance(value, dict):
                    _traverse(value, level + 1)
    
    _traverse(hierarchy)
    return levels