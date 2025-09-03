"""
📊 Analysis Utilities for Tensor Product Binding
================================================

This module provides analysis and diagnostic utilities for the tensor
product binding system. It includes quality metrics, complexity analysis,
and semantic coherence measures.
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import warnings

from ..core.binding_operations import TPBVector
from .vector_utils import cosine_similarity, vector_similarity_matrix


def analyze_binding_quality(bound_vector: np.ndarray,
                           original_role: np.ndarray,
                           original_filler: np.ndarray,
                           unbind_func: callable = None) -> Dict[str, float]:
    """
    Analyze the quality of a binding operation.
    
    Parameters
    ----------
    bound_vector : np.ndarray
        The result of binding role and filler
    original_role : np.ndarray
        Original role vector
    original_filler : np.ndarray
        Original filler vector
    unbind_func : callable, optional
        Function to unbind vectors (for reconstruction quality)
        
    Returns
    -------
    Dict[str, float]
        Quality metrics including fidelity, distortion, etc.
    """
    metrics = {}
    
    # Basic vector properties
    metrics['bound_vector_norm'] = np.linalg.norm(bound_vector)
    metrics['role_norm'] = np.linalg.norm(original_role)
    metrics['filler_norm'] = np.linalg.norm(original_filler)
    
    # Expected vs actual magnitude relationship
    expected_magnitude = metrics['role_norm'] * metrics['filler_norm']
    if expected_magnitude > 0:
        metrics['magnitude_ratio'] = metrics['bound_vector_norm'] / expected_magnitude
    else:
        metrics['magnitude_ratio'] = 0.0
    
    # Information preservation (entropy-based)
    def _vector_entropy(vec):
        # Normalize to probabilities
        abs_vec = np.abs(vec)
        if np.sum(abs_vec) == 0:
            return 0.0
        probs = abs_vec / np.sum(abs_vec)
        # Add small epsilon to avoid log(0)
        probs = probs + 1e-12
        return -np.sum(probs * np.log2(probs))
    
    role_entropy = _vector_entropy(original_role)
    filler_entropy = _vector_entropy(original_filler)
    bound_entropy = _vector_entropy(bound_vector)
    
    metrics['role_entropy'] = role_entropy
    metrics['filler_entropy'] = filler_entropy
    metrics['bound_entropy'] = bound_entropy
    
    # Information efficiency
    input_entropy = role_entropy + filler_entropy
    if input_entropy > 0:
        metrics['information_efficiency'] = bound_entropy / input_entropy
    else:
        metrics['information_efficiency'] = 0.0
    
    # Reconstruction quality (if unbind function provided)
    if unbind_func is not None:
        try:
            reconstructed_filler = unbind_func(bound_vector, original_role)
            
            # Reconstruction fidelity
            filler_norm = metrics['filler_norm']
            recon_norm = np.linalg.norm(reconstructed_filler)
            
            if filler_norm > 0 and recon_norm > 0:
                metrics['reconstruction_fidelity'] = cosine_similarity(
                    original_filler, reconstructed_filler)
            else:
                metrics['reconstruction_fidelity'] = 0.0
            
            # Reconstruction error (normalized MSE)
            if filler_norm > 0:
                mse = np.mean((original_filler - reconstructed_filler)**2)
                metrics['reconstruction_error'] = mse / (filler_norm**2)
            else:
                metrics['reconstruction_error'] = np.mean(reconstructed_filler**2)
            
            metrics['unbinding_successful'] = True
            
        except Exception as e:
            metrics['reconstruction_fidelity'] = 0.0
            metrics['reconstruction_error'] = float('inf')
            metrics['unbinding_successful'] = False
            warnings.warn(f"Unbinding failed: {e}")
    
    # Dimensional analysis
    metrics['dimensionality_expansion'] = len(bound_vector) / len(original_role)
    
    return metrics


def compute_structure_complexity(structure: List[Any]) -> Dict[str, Any]:
    """
    Compute complexity metrics for a structural representation.
    
    Parameters
    ----------
    structure : List[Any]
        List of bound vectors or structural elements
        
    Returns
    -------
    Dict[str, Any]
        Complexity metrics
    """
    if not structure:
        return {'complexity': 0, 'depth': 0, 'breadth': 0}
    
    metrics = {
        'num_elements': len(structure),
        'max_depth': 0,
        'total_depth': 0,
        'branching_factor': 0,
        'structural_diversity': 0.0
    }
    
    # Analyze depth and structure
    def _analyze_element(element, current_depth=0):
        metrics['max_depth'] = max(metrics['max_depth'], current_depth)
        metrics['total_depth'] += current_depth
        
        if isinstance(element, (list, tuple)):
            children = len(element)
            metrics['branching_factor'] = max(metrics['branching_factor'], children)
            for child in element:
                _analyze_element(child, current_depth + 1)
        elif isinstance(element, dict):
            children = len(element)
            metrics['branching_factor'] = max(metrics['branching_factor'], children)
            for value in element.values():
                _analyze_element(value, current_depth + 1)
    
    for element in structure:
        _analyze_element(element)
    
    # Compute derived metrics
    if metrics['num_elements'] > 0:
        metrics['average_depth'] = metrics['total_depth'] / metrics['num_elements']
    else:
        metrics['average_depth'] = 0
    
    # Structural complexity score (combines depth, breadth, and diversity)
    complexity_score = (metrics['max_depth'] * 
                       np.log(1 + metrics['branching_factor']) * 
                       np.log(1 + metrics['num_elements']))
    
    metrics['complexity_score'] = complexity_score
    
    return metrics


def measure_semantic_coherence(vectors: List[np.ndarray],
                             similarity_threshold: float = 0.3) -> Dict[str, float]:
    """
    Measure semantic coherence of a set of vectors.
    
    Parameters
    ----------
    vectors : List[np.ndarray]
        List of vectors to analyze
    similarity_threshold : float, default=0.3
        Threshold for considering vectors as coherent
        
    Returns
    -------
    Dict[str, float]
        Coherence metrics
    """
    if len(vectors) < 2:
        return {
            'mean_similarity': 1.0 if len(vectors) == 1 else 0.0,
            'coherence_score': 1.0 if len(vectors) == 1 else 0.0,
            'num_coherent_pairs': 0,
            'total_pairs': 0
        }
    
    # Compute similarity matrix
    similarity_matrix = vector_similarity_matrix(vectors)
    
    # Extract upper triangular similarities (excluding diagonal)
    n = len(vectors)
    similarities = []
    for i in range(n):
        for j in range(i + 1, n):
            similarities.append(abs(similarity_matrix[i, j]))
    
    similarities = np.array(similarities)
    
    # Compute metrics
    mean_similarity = np.mean(similarities)
    std_similarity = np.std(similarities)
    min_similarity = np.min(similarities)
    max_similarity = np.max(similarities)
    
    # Count coherent pairs
    coherent_pairs = np.sum(similarities >= similarity_threshold)
    total_pairs = len(similarities)
    
    # Coherence score (higher is more coherent)
    coherence_ratio = coherent_pairs / total_pairs if total_pairs > 0 else 0.0
    coherence_score = mean_similarity * coherence_ratio
    
    return {
        'mean_similarity': float(mean_similarity),
        'std_similarity': float(std_similarity),
        'min_similarity': float(min_similarity),
        'max_similarity': float(max_similarity),
        'coherence_score': float(coherence_score),
        'num_coherent_pairs': int(coherent_pairs),
        'total_pairs': int(total_pairs),
        'coherence_ratio': float(coherence_ratio)
    }


def binding_statistics(bindings: List[Tuple[np.ndarray, np.ndarray, np.ndarray]]) -> Dict[str, Any]:
    """
    Compute statistics for a collection of bindings.
    
    Parameters
    ----------
    bindings : List[Tuple[np.ndarray, np.ndarray, np.ndarray]]
        List of (role, filler, bound) tuples
        
    Returns
    -------
    Dict[str, Any]
        Statistical analysis of bindings
    """
    if not bindings:
        return {'num_bindings': 0}
    
    stats = {
        'num_bindings': len(bindings),
        'role_stats': defaultdict(list),
        'filler_stats': defaultdict(list),
        'bound_stats': defaultdict(list)
    }
    
    # Collect vector statistics
    for role, filler, bound in bindings:
        # Role statistics
        stats['role_stats']['norms'].append(np.linalg.norm(role))
        stats['role_stats']['dimensions'].append(len(role))
        stats['role_stats']['entropies'].append(_vector_entropy(role))
        
        # Filler statistics
        stats['filler_stats']['norms'].append(np.linalg.norm(filler))
        stats['filler_stats']['dimensions'].append(len(filler))
        stats['filler_stats']['entropies'].append(_vector_entropy(filler))
        
        # Bound statistics
        stats['bound_stats']['norms'].append(np.linalg.norm(bound))
        stats['bound_stats']['dimensions'].append(len(bound))
        stats['bound_stats']['entropies'].append(_vector_entropy(bound))
    
    # Compute summary statistics
    for category in ['role_stats', 'filler_stats', 'bound_stats']:
        for metric in stats[category]:
            values = np.array(stats[category][metric])
            stats[category][metric] = {
                'mean': float(np.mean(values)),
                'std': float(np.std(values)),
                'min': float(np.min(values)),
                'max': float(np.max(values)),
                'median': float(np.median(values))
            }
    
    # Cross-binding analysis
    role_norms = [np.linalg.norm(role) for role, _, _ in bindings]
    filler_norms = [np.linalg.norm(filler) for _, filler, _ in bindings]
    bound_norms = [np.linalg.norm(bound) for _, _, bound in bindings]
    
    # Correlation between input and output norms
    if len(bindings) > 1:
        expected_norms = [r * f for r, f in zip(role_norms, filler_norms)]
        norm_correlation = np.corrcoef(expected_norms, bound_norms)[0, 1]
        stats['norm_correlation'] = float(norm_correlation) if not np.isnan(norm_correlation) else 0.0
    else:
        stats['norm_correlation'] = 1.0
    
    return stats


def vector_space_analysis(vector_space: Dict[str, np.ndarray]) -> Dict[str, Any]:
    """
    Analyze properties of a vector space.
    
    Parameters
    ----------
    vector_space : Dict[str, np.ndarray]
        Dictionary of named vectors
        
    Returns
    -------
    Dict[str, Any]
        Analysis of vector space properties
    """
    if not vector_space:
        return {'num_vectors': 0}
    
    vectors = list(vector_space.values())
    names = list(vector_space.keys())
    
    analysis = {
        'num_vectors': len(vectors),
        'vector_names': names,
        'dimensionality_analysis': {},
        'norm_analysis': {},
        'similarity_analysis': {},
        'orthogonality_analysis': {},
        'diversity_analysis': {}
    }
    
    # Dimensionality analysis
    dims = [len(v) for v in vectors]
    analysis['dimensionality_analysis'] = {
        'dimensions': dims,
        'min_dim': min(dims),
        'max_dim': max(dims),
        'mean_dim': np.mean(dims),
        'consistent_dimensions': len(set(dims)) == 1
    }
    
    # Norm analysis
    norms = [np.linalg.norm(v) for v in vectors]
    analysis['norm_analysis'] = {
        'norms': norms,
        'min_norm': min(norms),
        'max_norm': max(norms),
        'mean_norm': np.mean(norms),
        'std_norm': np.std(norms),
        'unit_vectors': sum(1 for n in norms if abs(n - 1.0) < 0.01)
    }
    
    # Similarity analysis
    if len(vectors) >= 2:
        sim_matrix = vector_similarity_matrix(vectors)
        # Get upper triangular similarities (excluding diagonal)
        n = len(vectors)
        similarities = []
        for i in range(n):
            for j in range(i + 1, n):
                similarities.append(abs(sim_matrix[i, j]))
        
        analysis['similarity_analysis'] = {
            'mean_similarity': np.mean(similarities),
            'std_similarity': np.std(similarities),
            'min_similarity': np.min(similarities),
            'max_similarity': np.max(similarities),
            'similarity_matrix': sim_matrix
        }
        
        # Orthogonality analysis
        orthogonal_pairs = sum(1 for s in similarities if s < 0.1)
        analysis['orthogonality_analysis'] = {
            'num_orthogonal_pairs': orthogonal_pairs,
            'total_pairs': len(similarities),
            'orthogonality_ratio': orthogonal_pairs / len(similarities),
            'approximately_orthogonal': orthogonal_pairs > len(similarities) * 0.8
        }
    
    # Diversity analysis (effective rank using SVD)
    if analysis['dimensionality_analysis']['consistent_dimensions']:
        vector_matrix = np.array(vectors)
        try:
            _, singular_values, _ = np.linalg.svd(vector_matrix, full_matrices=False)
            # Effective rank using threshold
            threshold = 0.01 * singular_values[0] if len(singular_values) > 0 else 0
            effective_rank = np.sum(singular_values > threshold)
            
            analysis['diversity_analysis'] = {
                'singular_values': singular_values.tolist(),
                'effective_rank': int(effective_rank),
                'rank_ratio': float(effective_rank / len(vectors)),
                'condition_number': float(singular_values[0] / singular_values[-1]) if singular_values[-1] > 1e-10 else float('inf')
            }
        except Exception as e:
            analysis['diversity_analysis'] = {'error': str(e)}
    
    return analysis


def _vector_entropy(vector: np.ndarray) -> float:
    """Helper function to compute vector entropy."""
    abs_vec = np.abs(vector)
    if np.sum(abs_vec) == 0:
        return 0.0
    probs = abs_vec / np.sum(abs_vec)
    probs = probs + 1e-12  # Avoid log(0)
    return -np.sum(probs * np.log2(probs))


def diagnose_binding_issues(role: np.ndarray,
                           filler: np.ndarray,
                           bound: np.ndarray) -> List[str]:
    """
    Diagnose potential issues with a binding operation.
    
    Parameters
    ----------
    role, filler : np.ndarray
        Input vectors
    bound : np.ndarray
        Result of binding operation
        
    Returns
    -------
    List[str]
        List of potential issues found
    """
    issues = []
    
    # Check for zero or near-zero vectors
    if np.linalg.norm(role) < 1e-10:
        issues.append("Role vector is near zero")
    
    if np.linalg.norm(filler) < 1e-10:
        issues.append("Filler vector is near zero")
    
    if np.linalg.norm(bound) < 1e-10:
        issues.append("Bound vector is near zero")
    
    # Check for NaN or infinite values
    if not np.isfinite(role).all():
        issues.append("Role vector contains non-finite values")
    
    if not np.isfinite(filler).all():
        issues.append("Filler vector contains non-finite values")
    
    if not np.isfinite(bound).all():
        issues.append("Bound vector contains non-finite values")
    
    # Check magnitude relationship
    expected_magnitude = np.linalg.norm(role) * np.linalg.norm(filler)
    actual_magnitude = np.linalg.norm(bound)
    
    if expected_magnitude > 0:
        magnitude_ratio = actual_magnitude / expected_magnitude
        if magnitude_ratio < 0.01:
            issues.append("Bound vector magnitude much smaller than expected")
        elif magnitude_ratio > 100:
            issues.append("Bound vector magnitude much larger than expected")
    
    # Check for dimension compatibility issues
    if len(role) == 0:
        issues.append("Role vector is empty")
    
    if len(filler) == 0:
        issues.append("Filler vector is empty")
    
    if len(bound) == 0:
        issues.append("Bound vector is empty")
    
    return issues