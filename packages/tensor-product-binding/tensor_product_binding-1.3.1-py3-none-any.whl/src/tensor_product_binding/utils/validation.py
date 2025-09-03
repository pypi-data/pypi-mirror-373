"""
✅ Validation Utilities for Tensor Product Binding
==================================================

This module provides validation functions to ensure data integrity
and parameter correctness throughout the tensor product binding system.
It includes dimension checking, parameter validation, and structure
verification functions.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Union
import warnings
from ..config.enums import BindingOperation, BindingMethod
from ..config.config_classes import TensorBindingConfig, BindingPair


def validate_vector_dimensions(vector: np.ndarray, 
                             expected_dim: Optional[int] = None,
                             name: str = "vector") -> bool:
    """
    Validate vector dimensions and properties.
    
    Parameters
    ----------
    vector : np.ndarray
        Vector to validate
    expected_dim : int, optional
        Expected vector dimension
    name : str, default="vector"
        Name for error messages
        
    Returns
    -------
    bool
        True if valid
        
    Raises
    ------
    ValueError
        If validation fails
    """
    if not isinstance(vector, np.ndarray):
        raise TypeError(f"{name} must be a numpy array, got {type(vector)}")
    
    if vector.ndim != 1:
        raise ValueError(f"{name} must be 1-dimensional, got shape {vector.shape}")
    
    if len(vector) == 0:
        raise ValueError(f"{name} cannot be empty")
    
    if expected_dim is not None and len(vector) != expected_dim:
        raise ValueError(f"{name} dimension mismatch: expected {expected_dim}, got {len(vector)}")
    
    if not np.isfinite(vector).all():
        raise ValueError(f"{name} contains non-finite values")
    
    return True


def validate_binding_parameters(role: np.ndarray,
                               filler: np.ndarray,
                               operation: BindingOperation,
                               name: str = "binding") -> bool:
    """
    Validate parameters for a binding operation.
    
    Parameters
    ----------
    role : np.ndarray
        Role vector
    filler : np.ndarray
        Filler vector
    operation : BindingOperation
        Binding operation type
    name : str, default="binding"
        Name for error messages
        
    Returns
    -------
    bool
        True if valid
        
    Raises
    ------
    ValueError
        If validation fails
    """
    # Basic vector validation
    validate_vector_dimensions(role, name=f"{name} role")
    validate_vector_dimensions(filler, name=f"{name} filler")
    
    # Operation-specific validation
    if operation in [BindingOperation.CIRCULAR_CONVOLUTION, 
                    BindingOperation.ADDITION, 
                    BindingOperation.MULTIPLICATION]:
        if len(role) != len(filler):
            raise ValueError(
                f"{operation.value} requires same-dimension vectors: "
                f"role={len(role)}, filler={len(filler)}"
            )
    
    # Check for zero vectors (problematic for most operations)
    if np.allclose(role, 0):
        warnings.warn(f"{name} role vector is near zero - may cause numerical issues")
    
    if np.allclose(filler, 0):
        warnings.warn(f"{name} filler vector is near zero - may cause numerical issues")
    
    return True


def validate_config(config: TensorBindingConfig) -> bool:
    """
    Validate a tensor binding configuration.
    
    Parameters
    ----------
    config : TensorBindingConfig
        Configuration to validate
        
    Returns
    -------
    bool
        True if valid
        
    Raises
    ------
    ValueError
        If configuration is invalid
    """
    # Basic parameter validation
    if config.vector_dim <= 0:
        raise ValueError("vector_dim must be positive")
    
    if not 0 <= config.default_binding_strength <= 2:
        raise ValueError("default_binding_strength should be between 0 and 2")
    
    if not 0 <= config.strength_decay_factor <= 1:
        raise ValueError("strength_decay_factor should be between 0 and 1")
    
    if not 0 <= config.context_sensitivity <= 1:
        raise ValueError("context_sensitivity should be between 0 and 1")
    
    if config.max_recursion_depth < 1:
        raise ValueError("max_recursion_depth must be at least 1")
    
    if not 0 <= config.recursive_strength_decay <= 1:
        raise ValueError("recursive_strength_decay should be between 0 and 1")
    
    if config.max_unbinding_iterations < 1:
        raise ValueError("max_unbinding_iterations must be at least 1")
    
    if config.unbinding_tolerance <= 0:
        raise ValueError("unbinding_tolerance must be positive")
    
    # Validate dimension maps if enabled
    if config.enable_variable_dimensions:
        if config.role_dimension_map:
            for role, dim in config.role_dimension_map.items():
                if dim <= 0:
                    raise ValueError(f"Invalid dimension for role '{role}': {dim}")
        
        if config.filler_dimension_map:
            for filler, dim in config.filler_dimension_map.items():
                if dim <= 0:
                    raise ValueError(f"Invalid dimension for filler '{filler}': {dim}")
    
    # Validate sub-configurations
    if config.vector_space_config.dimension != config.vector_dim:
        warnings.warn("vector_space_config dimension doesn't match main vector_dim")
    
    return True


def validate_binding_pair(pair: BindingPair) -> bool:
    """
    Validate a binding pair.
    
    Parameters
    ----------
    pair : BindingPair
        Binding pair to validate
        
    Returns
    -------
    bool
        True if valid
        
    Raises
    ------
    ValueError
        If binding pair is invalid
    """
    if not pair.variable:
        raise ValueError("BindingPair variable name cannot be empty")
    
    if not 0 <= pair.binding_strength <= 2:
        raise ValueError("binding_strength should be between 0 and 2")
    
    if pair.hierarchical_level < 0:
        raise ValueError("hierarchical_level must be non-negative")
    
    # Validate vectors if provided
    if pair.role_vector is not None:
        validate_vector_dimensions(pair.role_vector, name="role_vector")
    
    if pair.filler_vector is not None:
        validate_vector_dimensions(pair.filler_vector, name="filler_vector")
    
    # Check dimension compatibility if both vectors provided
    if (pair.role_vector is not None and pair.filler_vector is not None 
        and hasattr(pair, 'binding_operation')):
        
        operation = getattr(pair, 'binding_operation', BindingOperation.OUTER_PRODUCT)
        if operation in [BindingOperation.CIRCULAR_CONVOLUTION, 
                        BindingOperation.ADDITION, 
                        BindingOperation.MULTIPLICATION]:
            if len(pair.role_vector) != len(pair.filler_vector):
                raise ValueError("Role and filler vectors must have same dimension for this operation")
    
    return True


def check_orthogonality(vectors: List[np.ndarray], 
                       threshold: float = 0.1,
                       warn: bool = True) -> Dict[str, Any]:
    """
    Check orthogonality of a set of vectors.
    
    Parameters
    ----------
    vectors : List[np.ndarray]
        Vectors to check
    threshold : float, default=0.1
        Orthogonality threshold (cosine similarity)
    warn : bool, default=True
        Whether to issue warnings for non-orthogonal vectors
        
    Returns
    -------
    Dict[str, Any]
        Orthogonality analysis results
    """
    if len(vectors) < 2:
        return {
            'is_orthogonal': True,
            'max_similarity': 0.0,
            'mean_similarity': 0.0,
            'violations': []
        }
    
    similarities = []
    violations = []
    
    for i in range(len(vectors)):
        for j in range(i + 1, len(vectors)):
            # Validate vectors first
            validate_vector_dimensions(vectors[i], name=f"vector_{i}")
            validate_vector_dimensions(vectors[j], name=f"vector_{j}")
            
            # Calculate similarity
            norm_i = np.linalg.norm(vectors[i])
            norm_j = np.linalg.norm(vectors[j])
            
            if norm_i == 0 or norm_j == 0:
                similarity = 0.0
            else:
                similarity = abs(np.dot(vectors[i], vectors[j]) / (norm_i * norm_j))
            
            similarities.append(similarity)
            
            if similarity > threshold:
                violations.append({
                    'indices': (i, j),
                    'similarity': similarity
                })
                
                if warn:
                    warnings.warn(
                        f"Vectors {i} and {j} are not orthogonal "
                        f"(similarity: {similarity:.3f} > {threshold})"
                    )
    
    return {
        'is_orthogonal': len(violations) == 0,
        'max_similarity': max(similarities) if similarities else 0.0,
        'mean_similarity': np.mean(similarities) if similarities else 0.0,
        'violations': violations,
        'num_violations': len(violations),
        'total_pairs': len(similarities)
    }


def validate_structure(structure: Any, 
                      max_depth: int = 10,
                      name: str = "structure") -> bool:
    """
    Validate a structural representation.
    
    Parameters
    ----------
    structure : Any
        Structure to validate (could be nested dict, list, etc.)
    max_depth : int, default=10
        Maximum allowed nesting depth
    name : str, default="structure"
        Name for error messages
        
    Returns
    -------
    bool
        True if valid
        
    Raises
    ------
    ValueError
        If structure is invalid
    """
    def _check_depth(obj, current_depth=0):
        if current_depth > max_depth:
            raise ValueError(f"{name} exceeds maximum depth of {max_depth}")
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                if not isinstance(key, str):
                    raise ValueError(f"{name} dictionary keys must be strings, got {type(key)}")
                _check_depth(value, current_depth + 1)
        
        elif isinstance(obj, (list, tuple)):
            for item in obj:
                _check_depth(item, current_depth + 1)
        
        elif isinstance(obj, np.ndarray):
            validate_vector_dimensions(obj, name=f"{name} vector")
    
    _check_depth(structure)
    return True


def validate_similarity_threshold(threshold: float, 
                                name: str = "threshold") -> bool:
    """
    Validate a similarity threshold parameter.
    
    Parameters
    ----------
    threshold : float
        Threshold to validate
    name : str, default="threshold"
        Name for error messages
        
    Returns
    -------
    bool
        True if valid
        
    Raises
    ------
    ValueError
        If threshold is invalid
    """
    if not isinstance(threshold, (int, float)):
        raise TypeError(f"{name} must be a number, got {type(threshold)}")
    
    if not -1 <= threshold <= 1:
        raise ValueError(f"{name} must be between -1 and 1, got {threshold}")
    
    return True


def validate_noise_parameters(noise_level: float, 
                            noise_tolerance: float) -> bool:
    """
    Validate noise-related parameters.
    
    Parameters
    ----------
    noise_level : float
        Noise level to add
    noise_tolerance : float
        Noise tolerance for operations
        
    Returns
    -------
    bool
        True if valid
        
    Raises
    ------
    ValueError
        If parameters are invalid
    """
    if noise_level < 0:
        raise ValueError("noise_level must be non-negative")
    
    if noise_tolerance < 0:
        raise ValueError("noise_tolerance must be non-negative")
    
    if noise_level > 1.0:
        warnings.warn("noise_level > 1.0 may severely degrade binding quality")
    
    if noise_tolerance > 0.5:
        warnings.warn("High noise_tolerance may accept poor quality bindings")
    
    return True