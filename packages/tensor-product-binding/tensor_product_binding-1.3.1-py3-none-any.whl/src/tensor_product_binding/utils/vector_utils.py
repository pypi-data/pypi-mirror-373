"""
🎯 Vector Utilities for Tensor Product Binding
==============================================

This module provides essential vector operations and utilities used
throughout the tensor product binding system. It includes functions
for vector creation, manipulation, and analysis.

Based on numerical linear algebra best practices and optimized for
tensor product binding operations.
"""

import numpy as np
from typing import List, Optional, Tuple, Union
import warnings


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Calculate cosine similarity between two numpy arrays.
    
    Parameters
    ----------
    vec1, vec2 : np.ndarray
        Input vectors
        
    Returns
    -------
    float
        Cosine similarity (-1 to 1)
    """
    # Flatten vectors to handle different shapes
    v1 = vec1.flatten()
    v2 = vec2.flatten()
    
    if len(v1) != len(v2):
        raise ValueError(f"Vector dimensions don't match: {len(v1)} vs {len(v2)}")
    
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
        
    return np.dot(v1, v2) / (norm1 * norm2)


def normalize_vector(vector: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    """
    Normalize a vector to unit length.
    
    Parameters
    ----------
    vector : np.ndarray
        Input vector
    eps : float, default=1e-12
        Small epsilon to prevent division by zero
        
    Returns
    -------
    np.ndarray
        Normalized vector
    """
    norm = np.linalg.norm(vector)
    if norm < eps:
        warnings.warn("Vector has near-zero norm, returning zero vector")
        return np.zeros_like(vector)
    return vector / norm


def create_normalized_vector(size: int, random_state: Optional[int] = None) -> np.ndarray:
    """
    Create a normalized random vector of given size.
    
    Parameters
    ----------
    size : int
        Vector dimension
    random_state : int, optional
        Random seed for reproducibility
        
    Returns
    -------
    np.ndarray
        Normalized random vector
    """
    if random_state is not None:
        rng = np.random.RandomState(random_state)
        vector = rng.randn(size)
    else:
        vector = np.random.randn(size)
    
    return normalize_vector(vector)


def random_unit_vector(size: int, random_state: Optional[int] = None) -> np.ndarray:
    """
    Create a random unit vector using uniform distribution on unit sphere.
    
    Parameters
    ----------
    size : int
        Vector dimension
    random_state : int, optional
        Random seed for reproducibility
        
    Returns
    -------
    np.ndarray
        Random unit vector
    """
    if random_state is not None:
        np.random.seed(random_state)
    
    # Use normal distribution and normalize (Muller method)
    vector = np.random.randn(size)
    return normalize_vector(vector)


def create_orthogonal_vectors(n_vectors: int, 
                            dimension: int, 
                            random_state: Optional[int] = None) -> List[np.ndarray]:
    """
    Create a set of orthonormal vectors using Gram-Schmidt orthogonalization.
    
    Parameters
    ----------
    n_vectors : int
        Number of vectors to create
    dimension : int
        Vector dimension
    random_state : int, optional
        Random seed for reproducibility
        
    Returns
    -------
    List[np.ndarray]
        List of orthonormal vectors
        
    Raises
    ------
    ValueError
        If n_vectors > dimension (cannot create more orthogonal vectors than dimensions)
    """
    if n_vectors > dimension:
        raise ValueError(f"Cannot create {n_vectors} orthogonal vectors in {dimension}D space")
    
    if random_state is not None:
        np.random.seed(random_state)
    
    vectors = []
    
    for i in range(n_vectors):
        # Generate random vector
        vector = np.random.randn(dimension)
        
        # Orthogonalize against previous vectors (Gram-Schmidt)
        for prev_vector in vectors:
            projection = np.dot(vector, prev_vector)
            vector = vector - projection * prev_vector
        
        # Normalize
        norm = np.linalg.norm(vector)
        if norm < 1e-10:
            raise RuntimeError(f"Failed to create orthogonal vector {i}")
        
        vector = vector / norm
        vectors.append(vector)
    
    return vectors


def vector_similarity_matrix(vectors: List[np.ndarray]) -> np.ndarray:
    """
    Compute pairwise cosine similarity matrix for a list of vectors.
    
    Parameters
    ----------
    vectors : List[np.ndarray]
        List of vectors
        
    Returns
    -------
    np.ndarray
        Similarity matrix (n_vectors x n_vectors)
    """
    n_vectors = len(vectors)
    similarity_matrix = np.zeros((n_vectors, n_vectors))
    
    for i in range(n_vectors):
        for j in range(n_vectors):
            if i == j:
                similarity_matrix[i, j] = 1.0
            else:
                similarity_matrix[i, j] = cosine_similarity(vectors[i], vectors[j])
    
    return similarity_matrix


def project_vector(vector: np.ndarray, onto: np.ndarray) -> np.ndarray:
    """
    Project vector onto another vector.
    
    Parameters
    ----------
    vector : np.ndarray
        Vector to project
    onto : np.ndarray
        Vector to project onto
        
    Returns
    -------
    np.ndarray
        Projected vector
    """
    onto_norm_sq = np.dot(onto, onto)
    if onto_norm_sq == 0:
        return np.zeros_like(vector)
    
    projection_coefficient = np.dot(vector, onto) / onto_norm_sq
    return projection_coefficient * onto


def remove_component(vector: np.ndarray, component: np.ndarray) -> np.ndarray:
    """
    Remove a component from a vector (orthogonal projection).
    
    Parameters
    ----------
    vector : np.ndarray
        Original vector
    component : np.ndarray
        Component to remove
        
    Returns
    -------
    np.ndarray
        Vector with component removed
    """
    projection = project_vector(vector, component)
    return vector - projection


def angle_between_vectors(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Calculate angle between two vectors in radians.
    
    Parameters
    ----------
    vec1, vec2 : np.ndarray
        Input vectors
        
    Returns
    -------
    float
        Angle in radians [0, π]
    """
    cos_sim = cosine_similarity(vec1, vec2)
    # Clamp to handle numerical precision issues
    cos_sim = np.clip(cos_sim, -1.0, 1.0)
    return np.arccos(abs(cos_sim))


def vector_magnitude(vector: np.ndarray) -> float:
    """
    Calculate vector magnitude (L2 norm).
    
    Parameters
    ----------
    vector : np.ndarray
        Input vector
        
    Returns
    -------
    float
        Vector magnitude
    """
    return np.linalg.norm(vector)


def l1_normalize(vector: np.ndarray) -> np.ndarray:
    """
    L1 normalize a vector (sum of absolute values = 1).
    
    Parameters
    ----------
    vector : np.ndarray
        Input vector
        
    Returns
    -------
    np.ndarray
        L1 normalized vector
    """
    l1_norm = np.sum(np.abs(vector))
    if l1_norm == 0:
        return vector
    return vector / l1_norm


def soft_orthogonalize(vectors: List[np.ndarray], 
                      strength: float = 1.0) -> List[np.ndarray]:
    """
    Apply soft orthogonalization to make vectors more orthogonal.
    
    This is useful when you want vectors to be somewhat orthogonal
    but not completely orthogonal (preserving some semantic content).
    
    Parameters
    ----------
    vectors : List[np.ndarray]
        Input vectors
    strength : float, default=1.0
        Orthogonalization strength (0 = no change, 1 = full orthogonalization)
        
    Returns
    -------
    List[np.ndarray]
        Soft orthogonalized vectors
    """
    if not 0 <= strength <= 1:
        raise ValueError("Strength must be between 0 and 1")
    
    if strength == 0:
        return vectors.copy()
    
    result_vectors = []
    
    for i, vector in enumerate(vectors):
        orthogonalized = vector.copy()
        
        # Remove components from previous vectors
        for j in range(i):
            prev_vector = result_vectors[j]
            projection = project_vector(orthogonalized, prev_vector)
            orthogonalized = orthogonalized - strength * projection
        
        # Normalize
        orthogonalized = normalize_vector(orthogonalized)
        result_vectors.append(orthogonalized)
    
    return result_vectors


def interpolate_vectors(vec1: np.ndarray, 
                       vec2: np.ndarray, 
                       alpha: float) -> np.ndarray:
    """
    Interpolate between two vectors.
    
    Parameters
    ----------
    vec1, vec2 : np.ndarray
        Vectors to interpolate between
    alpha : float
        Interpolation parameter (0 = vec1, 1 = vec2)
        
    Returns
    -------
    np.ndarray
        Interpolated vector
    """
    if not 0 <= alpha <= 1:
        raise ValueError("Alpha must be between 0 and 1")
    
    return (1 - alpha) * vec1 + alpha * vec2