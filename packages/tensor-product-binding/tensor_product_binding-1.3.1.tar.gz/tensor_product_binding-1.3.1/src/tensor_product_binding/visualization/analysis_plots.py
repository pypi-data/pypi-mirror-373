"""
📈 Analysis Visualization for Tensor Product Binding
====================================================

This module provides visualization functions for analysis results,
including quality metrics, complexity analysis, coherence analysis,
and performance benchmarks.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Any, Optional, Tuple
import warnings


def plot_quality_metrics(quality_results: Dict[str, float],
                        title: str = "Binding Quality Metrics",
                        figsize: Tuple[int, int] = (10, 6)) -> plt.Figure:
    """
    Plot binding quality metrics.
    
    Parameters
    ----------
    quality_results : Dict[str, float]
        Dictionary of quality metric names and values
    title : str, default="Binding Quality Metrics"
        Plot title
    figsize : Tuple[int, int], default=(10, 6)
        Figure size
        
    Returns
    -------
    plt.Figure
        Figure containing quality metrics visualization
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    fig.suptitle(title, fontsize=14, fontweight='bold')
    
    metrics = list(quality_results.keys())
    values = list(quality_results.values())
    
    # 1. Bar plot
    colors = ['green' if v > 0.8 else 'orange' if v > 0.5 else 'red' for v in values]
    bars = ax1.bar(metrics, values, color=colors, alpha=0.7)
    
    ax1.set_title('Quality Metrics')
    ax1.set_ylabel('Score')
    ax1.set_ylim(0, max(1.0, max(values) * 1.1))
    ax1.tick_params(axis='x', rotation=45)
    
    # Add value labels
    for bar, value in zip(bars, values):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{value:.3f}', ha='center', va='bottom')
    
    # Add quality thresholds
    ax1.axhline(y=0.8, color='green', linestyle='--', alpha=0.5, label='Good (>0.8)')
    ax1.axhline(y=0.5, color='orange', linestyle='--', alpha=0.5, label='Fair (>0.5)')
    ax1.legend()
    
    # 2. Radar plot (if we have multiple metrics)
    if len(metrics) >= 3:
        angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False)
        values_radar = np.array(values)
        
        # Close the radar plot
        angles = np.concatenate((angles, [angles[0]]))
        values_radar = np.concatenate((values_radar, [values_radar[0]]))
        
        ax2 = plt.subplot(122, projection='polar')
        ax2.plot(angles, values_radar, 'b-', linewidth=2)
        ax2.fill(angles, values_radar, alpha=0.25)
        ax2.set_thetagrids(angles[:-1] * 180/np.pi, metrics)
        ax2.set_ylim(0, 1)
        ax2.set_title('Quality Radar', y=1.08)
        ax2.grid(True)
    else:
        # Fallback: show metrics as text
        metrics_text = "\n".join([f"{metric}: {value:.4f}" 
                                 for metric, value in quality_results.items()])
        ax2.text(0.1, 0.5, metrics_text, transform=ax2.transAxes,
                fontfamily='monospace', fontsize=12, verticalalignment='center')
        ax2.set_title('Quality Summary')
        ax2.axis('off')
    
    plt.tight_layout()
    return fig


def plot_complexity_analysis(complexity_results: Dict[str, Any],
                           title: str = "Structure Complexity Analysis",
                           figsize: Tuple[int, int] = (12, 8)) -> plt.Figure:
    """
    Plot structure complexity analysis results.
    
    Parameters
    ----------
    complexity_results : Dict[str, Any]
        Complexity analysis results
    title : str, default="Structure Complexity Analysis"
        Plot title
    figsize : Tuple[int, int], default=(12, 8)
        Figure size
        
    Returns
    -------
    plt.Figure
        Figure containing complexity analysis
    """
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    fig.suptitle(title, fontsize=14, fontweight='bold')
    
    # 1. Complexity metrics bar chart
    complexity_metrics = {
        'Elements': complexity_results.get('num_elements', 0),
        'Max Depth': complexity_results.get('max_depth', 0),
        'Avg Depth': complexity_results.get('average_depth', 0),
        'Branching': complexity_results.get('branching_factor', 0)
    }
    
    bars = axes[0, 0].bar(complexity_metrics.keys(), complexity_metrics.values(), 
                         alpha=0.7, color='skyblue')
    axes[0, 0].set_title('Complexity Metrics')
    axes[0, 0].set_ylabel('Count/Value')
    
    # Add value labels
    for bar, value in zip(bars, complexity_metrics.values()):
        axes[0, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                       f'{value:.1f}', ha='center', va='bottom')
    
    # 2. Complexity score visualization
    complexity_score = complexity_results.get('complexity_score', 0)
    max_theoretical_complexity = 100  # Adjust based on your scale
    
    # Create a gauge-like visualization
    theta = np.linspace(0, np.pi, 100)
    radius = 1
    
    # Background arc
    axes[0, 1].plot(radius * np.cos(theta), radius * np.sin(theta), 
                   'lightgray', linewidth=20, alpha=0.3)
    
    # Complexity arc
    complexity_ratio = min(complexity_score / max_theoretical_complexity, 1.0)
    complexity_theta = theta[:int(len(theta) * complexity_ratio)]
    
    color = 'green' if complexity_ratio < 0.3 else 'orange' if complexity_ratio < 0.7 else 'red'
    axes[0, 1].plot(radius * np.cos(complexity_theta), radius * np.sin(complexity_theta),
                   color, linewidth=20)
    
    axes[0, 1].set_xlim(-1.2, 1.2)
    axes[0, 1].set_ylim(-0.2, 1.2)
    axes[0, 1].set_aspect('equal')
    axes[0, 1].text(0, -0.1, f'{complexity_score:.1f}', ha='center', va='center', 
                   fontsize=16, fontweight='bold')
    axes[0, 1].set_title('Complexity Score')
    axes[0, 1].axis('off')
    
    # 3. Depth distribution (if available)
    if 'depth_distribution' in complexity_results:
        depth_dist = complexity_results['depth_distribution']
        depths = list(depth_dist.keys())
        counts = list(depth_dist.values())
        
        axes[1, 0].bar(depths, counts, alpha=0.7, color='lightgreen')
        axes[1, 0].set_title('Depth Distribution')
        axes[1, 0].set_xlabel('Depth Level')
        axes[1, 0].set_ylabel('Number of Elements')
    else:
        # Show structural properties instead
        properties = []
        if complexity_results.get('num_elements', 0) > 0:
            properties.append(f"Elements: {complexity_results['num_elements']}")
        if complexity_results.get('max_depth', 0) > 0:
            properties.append(f"Max Depth: {complexity_results['max_depth']}")
        if complexity_results.get('branching_factor', 0) > 0:
            properties.append(f"Branching Factor: {complexity_results['branching_factor']}")
        
        properties_text = "\n".join(properties)
        axes[1, 0].text(0.5, 0.5, properties_text, ha='center', va='center',
                       transform=axes[1, 0].transAxes, fontsize=12)
        axes[1, 0].set_title('Structure Properties')
        axes[1, 0].axis('off')
    
    # 4. Complexity assessment
    def _assess_complexity(score):
        if score < 10:
            return "Low complexity\n(Simple structure)"
        elif score < 50:
            return "Moderate complexity\n(Structured hierarchy)"
        elif score < 100:
            return "High complexity\n(Rich structure)"
        else:
            return "Very high complexity\n(Highly nested)"
    
    assessment = _assess_complexity(complexity_score)
    axes[1, 1].text(0.5, 0.6, assessment, ha='center', va='center',
                   transform=axes[1, 1].transAxes, fontsize=12, fontweight='bold')
    
    # Add complexity breakdown
    breakdown_text = f"""
    Complexity Breakdown:
    • Structural depth: {complexity_results.get('max_depth', 0)}
    • Element count: {complexity_results.get('num_elements', 0)}
    • Branching factor: {complexity_results.get('branching_factor', 0):.1f}
    • Total score: {complexity_score:.1f}
    """
    
    axes[1, 1].text(0.05, 0.3, breakdown_text, transform=axes[1, 1].transAxes,
                   fontfamily='monospace', fontsize=9, verticalalignment='top')
    axes[1, 1].set_title('Complexity Assessment')
    axes[1, 1].axis('off')
    
    plt.tight_layout()
    return fig


def plot_coherence_analysis(coherence_results: Dict[str, float],
                          title: str = "Semantic Coherence Analysis", 
                          figsize: Tuple[int, int] = (10, 6)) -> plt.Figure:
    """
    Plot semantic coherence analysis results.
    
    Parameters
    ----------
    coherence_results : Dict[str, float]
        Coherence analysis results
    title : str, default="Semantic Coherence Analysis"
        Plot title
    figsize : Tuple[int, int], default=(10, 6)
        Figure size
        
    Returns
    -------
    plt.Figure
        Figure containing coherence analysis
    """
    fig, axes = plt.subplots(1, 3, figsize=figsize)
    fig.suptitle(title, fontsize=14, fontweight='bold')
    
    # 1. Overall coherence score
    coherence_score = coherence_results.get('coherence_score', 0)
    mean_similarity = coherence_results.get('mean_similarity', 0)
    
    # Gauge visualization
    theta = np.linspace(0, 2*np.pi, 100)
    radius = 1
    
    # Background circle
    axes[0].plot(radius * np.cos(theta), radius * np.sin(theta), 
                'lightgray', linewidth=15, alpha=0.3)
    
    # Coherence arc
    coherence_theta = theta[:int(len(theta) * coherence_score)]
    color = 'green' if coherence_score > 0.7 else 'orange' if coherence_score > 0.4 else 'red'
    axes[0].plot(radius * np.cos(coherence_theta), radius * np.sin(coherence_theta),
                color, linewidth=15)
    
    axes[0].text(0, 0, f'{coherence_score:.2f}', ha='center', va='center',
                fontsize=16, fontweight='bold')
    axes[0].set_xlim(-1.2, 1.2)
    axes[0].set_ylim(-1.2, 1.2)
    axes[0].set_aspect('equal')
    axes[0].set_title('Coherence Score')
    axes[0].axis('off')
    
    # 2. Similarity distribution
    if 'similarity_distribution' in coherence_results:
        similarities = coherence_results['similarity_distribution']
        axes[1].hist(similarities, bins=20, alpha=0.7, color='skyblue', density=True)
        axes[1].axvline(mean_similarity, color='red', linestyle='--', 
                       label=f'Mean: {mean_similarity:.3f}')
        axes[1].set_title('Similarity Distribution')
        axes[1].set_xlabel('Cosine Similarity')
        axes[1].set_ylabel('Density')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
    else:
        # Show coherence metrics instead
        metrics = {
            'Mean Sim.': coherence_results.get('mean_similarity', 0),
            'Std Sim.': coherence_results.get('std_similarity', 0),
            'Min Sim.': coherence_results.get('min_similarity', 0),
            'Max Sim.': coherence_results.get('max_similarity', 0)
        }
        
        bars = axes[1].bar(metrics.keys(), metrics.values(), alpha=0.7, color='lightcoral')
        axes[1].set_title('Similarity Metrics')
        axes[1].set_ylabel('Value')
        axes[1].tick_params(axis='x', rotation=45)
        
        # Add value labels
        for bar, value in zip(bars, metrics.values()):
            axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                        f'{value:.3f}', ha='center', va='bottom', fontsize=8)
    
    # 3. Coherence assessment
    num_coherent_pairs = coherence_results.get('num_coherent_pairs', 0)
    total_pairs = coherence_results.get('total_pairs', 1)
    coherence_ratio = coherence_results.get('coherence_ratio', 0)
    
    def _assess_coherence(score, ratio):
        if score > 0.8 and ratio > 0.8:
            return "Excellent coherence\n(Highly consistent)"
        elif score > 0.6 and ratio > 0.6:
            return "Good coherence\n(Well structured)"
        elif score > 0.4 and ratio > 0.4:
            return "Fair coherence\n(Some structure)"
        else:
            return "Poor coherence\n(Inconsistent)"
    
    assessment = _assess_coherence(coherence_score, coherence_ratio)
    axes[2].text(0.5, 0.7, assessment, ha='center', va='center',
                transform=axes[2].transAxes, fontsize=11, fontweight='bold')
    
    # Add detailed metrics
    details_text = f"""
    Coherence Details:
    
    • Total vector pairs: {total_pairs}
    • Coherent pairs: {num_coherent_pairs}
    • Coherence ratio: {coherence_ratio:.1%}
    
    • Mean similarity: {mean_similarity:.3f}
    • Std similarity: {coherence_results.get('std_similarity', 0):.3f}
    
    • Overall score: {coherence_score:.3f}
    """
    
    axes[2].text(0.05, 0.5, details_text, transform=axes[2].transAxes,
                fontfamily='monospace', fontsize=8, verticalalignment='top')
    axes[2].set_title('Assessment')
    axes[2].axis('off')
    
    plt.tight_layout()
    return fig


def plot_performance_benchmark(benchmark_results: Dict[str, Any],
                             title: str = "Performance Benchmark Results",
                             figsize: Tuple[int, int] = (14, 8)) -> plt.Figure:
    """
    Plot performance benchmark results.
    
    Parameters
    ----------
    benchmark_results : Dict[str, Any]
        Benchmark results dictionary
    title : str, default="Performance Benchmark Results"
        Plot title
    figsize : Tuple[int, int], default=(14, 8)
        Figure size
        
    Returns
    -------
    plt.Figure
        Figure containing benchmark visualization
    """
    fig, axes = plt.subplots(2, 3, figsize=figsize)
    fig.suptitle(title, fontsize=14, fontweight='bold')
    
    results = benchmark_results.get('results', [])
    if not results:
        axes[0, 0].text(0.5, 0.5, "No benchmark results available", 
                       ha='center', va='center')
        return fig
    
    # Extract data for plotting
    dimensions = [r['role_dim'] for r in results]
    mean_times = [r['mean_time_sec'] for r in results]
    std_times = [r['std_time_sec'] for r in results]
    memory_deltas = [r.get('mean_memory_delta_mb', 0) for r in results]
    
    # 1. Execution time vs dimension
    axes[0, 0].errorbar(dimensions, mean_times, yerr=std_times, 
                       fmt='bo-', capsize=5, capthick=2)
    axes[0, 0].set_title('Execution Time vs Dimension')
    axes[0, 0].set_xlabel('Vector Dimension')
    axes[0, 0].set_ylabel('Time (seconds)')
    axes[0, 0].grid(True, alpha=0.3)
    
    # Add trend line
    if len(dimensions) > 2:
        z = np.polyfit(dimensions, mean_times, 2)  # Quadratic fit
        p = np.poly1d(z)
        dim_range = np.linspace(min(dimensions), max(dimensions), 100)
        axes[0, 0].plot(dim_range, p(dim_range), 'r--', alpha=0.8, label='Trend')
        axes[0, 0].legend()
    
    # 2. Memory usage vs dimension
    axes[0, 1].bar(range(len(dimensions)), memory_deltas, alpha=0.7, color='green')
    axes[0, 1].set_title('Memory Usage vs Dimension')
    axes[0, 1].set_xlabel('Dimension Index')
    axes[0, 1].set_ylabel('Memory Delta (MB)')
    axes[0, 1].set_xticks(range(len(dimensions)))
    axes[0, 1].set_xticklabels(dimensions, rotation=45)
    
    # Add value labels
    for i, memory in enumerate(memory_deltas):
        axes[0, 1].text(i, memory + 0.01, f'{memory:.2f}', 
                       ha='center', va='bottom', fontsize=8)
    
    # 3. Performance efficiency (operations per second)
    ops_per_second = [1.0 / t if t > 0 else 0 for t in mean_times]
    axes[0, 2].plot(dimensions, ops_per_second, 'go-', linewidth=2, markersize=6)
    axes[0, 2].set_title('Operations per Second')
    axes[0, 2].set_xlabel('Vector Dimension')
    axes[0, 2].set_ylabel('Ops/sec')
    axes[0, 2].grid(True, alpha=0.3)
    
    # 4. Time distribution box plot
    if len(results) >= 4:  # Need enough data for box plot
        time_data = []
        labels = []
        for r in results[:5]:  # Show first 5 for readability
            if 'time_samples' in r:
                time_data.append(r['time_samples'])
                labels.append(f"D={r['role_dim']}")
        
        if time_data:
            axes[1, 0].boxplot(time_data, labels=labels)
            axes[1, 0].set_title('Time Distribution by Dimension')
            axes[1, 0].set_ylabel('Time (seconds)')
            axes[1, 0].tick_params(axis='x', rotation=45)
        else:
            # Fallback: show time statistics
            axes[1, 0].bar(range(len(mean_times)), mean_times, 
                          yerr=std_times, alpha=0.7, color='orange')
            axes[1, 0].set_title('Mean Times with Std Dev')
            axes[1, 0].set_ylabel('Time (seconds)')
    else:
        axes[1, 0].bar(range(len(mean_times)), mean_times, alpha=0.7, color='orange')
        axes[1, 0].set_title('Execution Times')
        axes[1, 0].set_ylabel('Time (seconds)')
    
    # 5. Scaling analysis
    if len(dimensions) > 2:
        # Compute complexity scaling
        log_dims = np.log(dimensions)
        log_times = np.log(mean_times)
        
        # Linear fit in log space
        coeffs = np.polyfit(log_dims, log_times, 1)
        scaling_exponent = coeffs[0]
        
        axes[1, 1].loglog(dimensions, mean_times, 'bo-', label='Actual')
        
        # Show theoretical scalings
        axes[1, 1].loglog(dimensions, np.array(dimensions)**2 * min(mean_times) / min(np.array(dimensions)**2), 
                         'r--', alpha=0.7, label='O(n²)')
        axes[1, 1].loglog(dimensions, np.array(dimensions) * min(mean_times) / min(dimensions), 
                         'g--', alpha=0.7, label='O(n)')
        
        axes[1, 1].set_title(f'Scaling Analysis (α≈{scaling_exponent:.2f})')
        axes[1, 1].set_xlabel('Vector Dimension')
        axes[1, 1].set_ylabel('Time (seconds)')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
    else:
        axes[1, 1].text(0.5, 0.5, "Need more data points\nfor scaling analysis",
                       ha='center', va='center', transform=axes[1, 1].transAxes)
        axes[1, 1].set_title('Scaling Analysis')
    
    # 6. Performance summary
    operation_name = benchmark_results.get('operation', 'Unknown')
    num_iterations = benchmark_results.get('num_iterations', 0)
    
    fastest_time = min(mean_times) if mean_times else 0
    slowest_time = max(mean_times) if mean_times else 0
    avg_time = np.mean(mean_times) if mean_times else 0
    
    summary_text = f"""
    Benchmark Summary:
    
    Operation: {operation_name}
    Iterations per test: {num_iterations}
    
    Performance:
    • Fastest: {fastest_time:.4f}s
    • Slowest: {slowest_time:.4f}s
    • Average: {avg_time:.4f}s
    
    Memory:
    • Min usage: {min(memory_deltas):.2f} MB
    • Max usage: {max(memory_deltas):.2f} MB
    • Avg usage: {np.mean(memory_deltas):.2f} MB
    
    Dimensions tested: {len(set(dimensions))}
    Total tests: {len(results)}
    """
    
    axes[1, 2].text(0.05, 0.95, summary_text, transform=axes[1, 2].transAxes,
                   fontfamily='monospace', fontsize=9, verticalalignment='top')
    axes[1, 2].set_title('Performance Summary')
    axes[1, 2].axis('off')
    
    plt.tight_layout()
    return fig