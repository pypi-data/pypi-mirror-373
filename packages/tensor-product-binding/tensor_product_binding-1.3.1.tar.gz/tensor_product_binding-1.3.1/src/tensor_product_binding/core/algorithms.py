"""
🧮 Core Algorithms for Tensor Product Binding
=============================================

Implementation of core algorithms for tensor product binding operations,
including binding, unbinding, cleanup, and structural analysis.

Key Functions:
- bind_vectors: Core binding algorithm
- unbind_vectors: Unbinding with cleanup
- cleanup_vector: Vector cleanup and normalization
- structural_similarity: Compare structural representations
- compose_structures: Compose multiple bindings

Author: Benedict Chen (benedict@benedictchen.com)
Based on: Smolensky (1990) algorithms for tensor product binding
"""

import numpy as np
from typing import List, Dict, Optional, Tuple, Union, Any
import warnings
from .binding_operations import TPBVector, BindingOperation


def bind_vectors(role: np.ndarray, 
                filler: np.ndarray,
                method: BindingOperation = BindingOperation.OUTER_PRODUCT,
                normalize: bool = True,
                noise_level: float = 0.0) -> np.ndarray:
    """
    Core vector binding algorithm.
    
    Parameters
    ----------
    role : np.ndarray
        Role vector
    filler : np.ndarray
        Filler vector
    method : BindingOperation
        Binding method to use
    normalize : bool
        Whether to normalize result
    noise_level : float
        Amount of noise to add
        
    Returns
    -------
    np.ndarray
        Bound vector representation
    """
    if method == BindingOperation.OUTER_PRODUCT:
        bound = np.outer(role, filler).flatten()
    elif method == BindingOperation.CIRCULAR_CONVOLUTION:
        if len(role) != len(filler):
            raise ValueError("Circular convolution requires same-dimension vectors")
        bound = np.fft.ifft(np.fft.fft(role) * np.fft.fft(filler)).real
    elif method == BindingOperation.ADDITION:
        if len(role) != len(filler):
            raise ValueError("Addition requires same-dimension vectors")
        bound = role + filler
    elif method == BindingOperation.MULTIPLICATION:
        if len(role) != len(filler):
            raise ValueError("Multiplication requires same-dimension vectors")  
        bound = role * filler
    else:
        raise ValueError(f"Unknown binding method: {method}")
    
    # Add noise if specified
    if noise_level > 0:
        noise = np.random.randn(*bound.shape) * noise_level
        bound = bound + noise
    
    # Normalize if specified
    if normalize:
        norm = np.linalg.norm(bound)
        if norm > 0:
            bound = bound / norm
    
    return bound


def unbind_vectors(bound: np.ndarray,
                  role: np.ndarray, 
                  method: BindingOperation = BindingOperation.OUTER_PRODUCT,
                  cleanup_vectors: Optional[Dict[str, np.ndarray]] = None) -> np.ndarray:
    """
    Unbind a filler vector from a bound representation.
    
    Parameters
    ---------- 
    bound : np.ndarray
        Bound vector to unbind from
    role : np.ndarray
        Role vector used for unbinding
    method : BindingOperation
        Original binding method
    cleanup_vectors : dict, optional
        Dictionary of cleanup vectors for better reconstruction
        
    Returns
    -------
    np.ndarray
        Reconstructed filler vector
    """
    if method == BindingOperation.OUTER_PRODUCT:
        # Reshape to matrix and use pseudo-inverse
        role_dim = len(role)
        filler_dim = len(bound) // role_dim
        
        if role_dim * filler_dim != len(bound):
            raise ValueError("Bound vector dimension incompatible with role dimension")
        
        bound_matrix = bound.reshape(role_dim, filler_dim)
        
        # Use pseudo-inverse for unbinding
        role_norm = np.linalg.norm(role)
        if role_norm > 0:
            role_normalized = role / role_norm
            unbound = bound_matrix.T @ role_normalized
        else:
            unbound = np.zeros(filler_dim)
            
    elif method == BindingOperation.CIRCULAR_CONVOLUTION:
        # Circular correlation for unbinding
        if len(bound) != len(role):
            raise ValueError("Bound and role vectors must have same dimension for circular convolution")
        
        role_fft = np.fft.fft(role)
        bound_fft = np.fft.fft(bound)
        
        # Correlation (inverse of convolution)
        role_fft_conj = np.conj(role_fft)
        denominator = np.abs(role_fft)**2
        safe_denominator = np.where(denominator > 1e-12, denominator, 1e-12)
        
        unbound_fft = bound_fft * role_fft_conj / safe_denominator
        unbound = np.fft.ifft(unbound_fft).real
        
    elif method in [BindingOperation.ADDITION, BindingOperation.MULTIPLICATION]:
        warnings.warn(f"Unbinding not reliable for method: {method}")
        unbound = bound  # Return original as fallback
        
    else:
        raise ValueError(f"Unknown binding method: {method}")
    
    # Apply cleanup if available
    if cleanup_vectors:
        unbound = cleanup_vector(unbound, cleanup_vectors)
    
    return unbound


def cleanup_vector(vector: np.ndarray, 
                  cleanup_vectors: Dict[str, np.ndarray],
                  threshold: float = 0.3) -> np.ndarray:
    """
    Clean up a noisy vector using a set of cleanup vectors.
    
    Parameters
    ----------
    vector : np.ndarray
        Noisy vector to clean up
    cleanup_vectors : dict
        Dictionary mapping names to cleanup vectors
    threshold : float
        Similarity threshold for cleanup
        
    Returns
    -------
    np.ndarray
        Cleaned up vector (or original if no match found)
    """
    if not cleanup_vectors:
        return vector
    
    vector_norm = np.linalg.norm(vector)
    if vector_norm == 0:
        return vector
    
    normalized_vector = vector / vector_norm
    best_similarity = -1
    best_cleanup = None
    
    # Find best matching cleanup vector
    for name, cleanup_vec in cleanup_vectors.items():
        cleanup_norm = np.linalg.norm(cleanup_vec)
        if cleanup_norm > 0:
            similarity = np.dot(normalized_vector, cleanup_vec / cleanup_norm)
            if similarity > best_similarity and similarity > threshold:
                best_similarity = similarity
                best_cleanup = cleanup_vec
    
    # Return cleanup vector if good match found
    if best_cleanup is not None:
        return best_cleanup.copy()
    else:
        return vector


def structural_similarity(structure1: List[TPBVector],
                         structure2: List[TPBVector],
                         weight_by_magnitude: bool = True) -> float:
    """
    Compute similarity between two structural representations.
    
    Parameters
    ----------
    structure1 : List[TPBVector]
        First structural representation
    structure2 : List[TPBVector]  
        Second structural representation
    weight_by_magnitude : bool
        Whether to weight by vector magnitudes
        
    Returns
    -------
    float
        Structural similarity score (0-1)
    """
    if not structure1 or not structure2:
        return 0.0
    
    # Create superposition of each structure
    if len(structure1) == 1:
        super1 = structure1[0].data
    else:
        weights1 = [v.norm for v in structure1] if weight_by_magnitude else None
        super1 = _create_superposition([v.data for v in structure1], weights1)
    
    if len(structure2) == 1:
        super2 = structure2[0].data
    else:
        weights2 = [v.norm for v in structure2] if weight_by_magnitude else None
        super2 = _create_superposition([v.data for v in structure2], weights2)
    
    # Ensure same dimensions
    if super1.shape != super2.shape:
        # Pad or truncate to match
        min_dim = min(len(super1), len(super2))
        super1 = super1[:min_dim]
        super2 = super2[:min_dim]
    
    # Compute cosine similarity
    norm1 = np.linalg.norm(super1)
    norm2 = np.linalg.norm(super2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    similarity = np.dot(super1, super2) / (norm1 * norm2)
    return max(0.0, similarity)  # Ensure non-negative


def compose_structures(bindings: List[Tuple[np.ndarray, np.ndarray]],
                      method: BindingOperation = BindingOperation.OUTER_PRODUCT,
                      superposition_weights: Optional[List[float]] = None) -> np.ndarray:
    """
    Compose multiple role-filler bindings into a single structure.
    
    Parameters
    ----------
    bindings : List[Tuple[np.ndarray, np.ndarray]]
        List of (role, filler) pairs to bind and compose
    method : BindingOperation
        Binding method to use
    superposition_weights : List[float], optional
        Weights for superposition
        
    Returns
    -------
    np.ndarray
        Composed structural representation
    """
    if not bindings:
        raise ValueError("Cannot compose empty binding list")
    
    # Bind each role-filler pair
    bound_vectors = []
    for role, filler in bindings:
        bound_vec = bind_vectors(role, filler, method=method, normalize=True)
        bound_vectors.append(bound_vec)
    
    # Create superposition
    return _create_superposition(bound_vectors, superposition_weights)


def _create_superposition(vectors: List[np.ndarray], 
                         weights: Optional[List[float]] = None) -> np.ndarray:
    """Create weighted superposition of vectors"""
    if not vectors:
        raise ValueError("Cannot create superposition of empty vector list")
    
    if weights is None:
        weights = [1.0] * len(vectors)
    
    if len(weights) != len(vectors):
        raise ValueError("Number of weights must match number of vectors")
    
    # Ensure all vectors have same shape
    reference_shape = vectors[0].shape
    for i, vec in enumerate(vectors):
        if vec.shape != reference_shape:
            raise ValueError(f"Vector {i} has shape {vec.shape}, expected {reference_shape}")
    
    # Create weighted sum
    superposition = weights[0] * vectors[0].copy()
    for i in range(1, len(vectors)):
        superposition += weights[i] * vectors[i]
    
    return superposition


def analyze_binding_quality(bound_vector: np.ndarray,
                           original_role: np.ndarray,
                           original_filler: np.ndarray,
                           method: BindingOperation = BindingOperation.OUTER_PRODUCT) -> Dict[str, float]:
    """
    Analyze the quality of a binding operation.
    
    Parameters
    ----------
    bound_vector : np.ndarray
        The bound vector to analyze
    original_role : np.ndarray
        Original role vector
    original_filler : np.ndarray
        Original filler vector  
    method : BindingOperation
        Binding method used
        
    Returns
    -------
    Dict[str, float]
        Quality metrics
    """
    # Reconstruct filler by unbinding
    try:
        reconstructed_filler = unbind_vectors(bound_vector, original_role, method)
        
        # Compare with original
        filler_norm = np.linalg.norm(original_filler)
        recon_norm = np.linalg.norm(reconstructed_filler)
        
        if filler_norm > 0 and recon_norm > 0:
            fidelity = np.dot(original_filler, reconstructed_filler) / (filler_norm * recon_norm)
        else:
            fidelity = 0.0
        
        # Reconstruction error
        if filler_norm > 0:
            reconstruction_error = np.linalg.norm(original_filler - reconstructed_filler) / filler_norm
        else:
            reconstruction_error = np.linalg.norm(reconstructed_filler)
            
        unbinding_success = True
        
    except Exception as e:
        fidelity = 0.0
        reconstruction_error = 1.0
        unbinding_success = False
    
    # Binding strength (how much information is preserved)
    expected_bound_norm = np.linalg.norm(original_role) * np.linalg.norm(original_filler)
    actual_bound_norm = np.linalg.norm(bound_vector)
    
    if expected_bound_norm > 0:
        binding_strength = actual_bound_norm / expected_bound_norm
    else:
        binding_strength = 0.0
    
    return {
        'reconstruction_fidelity': max(0.0, fidelity),
        'reconstruction_error': reconstruction_error,
        'binding_strength': binding_strength,
        'unbinding_success': unbinding_success,
        'bound_vector_norm': actual_bound_norm,
        'expected_norm_ratio': binding_strength
    }


def extract_role_statistics(bound_structures: List[np.ndarray],
                           role_vectors: Dict[str, np.ndarray]) -> Dict[str, Any]:
    """
    Extract statistics about role usage in bound structures.
    
    Parameters
    ----------
    bound_structures : List[np.ndarray]
        List of bound structural representations
    role_vectors : Dict[str, np.ndarray]
        Dictionary of known role vectors
        
    Returns
    -------
    Dict[str, Any]
        Statistics about role usage and activation
    """
    if not bound_structures or not role_vectors:
        return {}
    
    role_activations = {name: [] for name in role_vectors.keys()}
    
    # For each structure, compute activation of each role
    for structure in bound_structures:
        for role_name, role_vec in role_vectors.items():
            try:
                # Attempt to unbind with this role
                unbound = unbind_vectors(structure, role_vec)
                
                # Measure activation strength
                activation = np.linalg.norm(unbound)
                role_activations[role_name].append(activation)
                
            except:
                role_activations[role_name].append(0.0)
    
    # Compute statistics
    stats = {}
    for role_name, activations in role_activations.items():
        if activations:
            stats[role_name] = {
                'mean_activation': float(np.mean(activations)),
                'std_activation': float(np.std(activations)),
                'max_activation': float(np.max(activations)),
                'min_activation': float(np.min(activations)),
                'usage_frequency': float(np.sum(np.array(activations) > 0.1) / len(activations))
            }
    
    return stats