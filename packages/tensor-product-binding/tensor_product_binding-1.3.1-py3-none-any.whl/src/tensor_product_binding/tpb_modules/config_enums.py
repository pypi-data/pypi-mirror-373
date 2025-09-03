"""
Configuration, Enums, and Data Classes for Tensor Product Binding

This module contains all configuration parameters, enumeration types,
and data classes used throughout the TPB system.
"""

import numpy as np
from typing import Dict, List, Tuple, Union, Optional, Any
from dataclasses import dataclass
from enum import Enum


class BindingOperation(Enum):
    """Different binding operation types"""
    TENSOR_PRODUCT = "tensor_product"
    CIRCULAR_CONVOLUTION = "circular_convolution"
    HOLOGRAPHIC_REDUCED = "holographic_reduced"
    VECTOR_MATRIX_MULTIPLICATION = "vector_matrix_multiplication"


class BindingMethod(Enum):
    """Methods for tensor product variable binding"""
    BASIC_OUTER_PRODUCT = "basic_outer"      # Simple outer product R ⊗ F
    RECURSIVE_BINDING = "recursive"          # Hierarchical binding for nested structures 
    CONTEXT_DEPENDENT = "context_dependent"  # Context-sensitive binding for ambiguous roles
    WEIGHTED_BINDING = "weighted"            # Binding with strength modulation
    MULTI_DIMENSIONAL = "multi_dim"          # Different tensor dimensions per binding
    HYBRID = "hybrid"                        # Combine multiple methods


class UnbindingMethod(Enum):
    """Methods for extracting information from tensor structures"""
    BASIC_MULTIPLICATION = "basic_mult"      # Simple matrix multiplication
    LEAST_SQUARES = "least_squares"          # Optimal least-squares unbinding
    REGULARIZED = "regularized"              # Regularized unbinding for noise handling
    ITERATIVE = "iterative"                  # Iterative unbinding for hierarchical structures
    CONTEXT_SENSITIVE = "context_sensitive"  # Context-aware unbinding


@dataclass
class TensorBindingConfig:
    """Configuration for advanced tensor product binding with maximum flexibility"""
    
    # Core binding method
    binding_method: BindingMethod = BindingMethod.HYBRID
    
    # Binding strength and modulation
    enable_binding_strength: bool = True
    default_binding_strength: float = 1.0
    strength_decay_factor: float = 0.95  # For temporal binding sequences
    
    # Context-dependent binding settings
    context_window_size: int = 3
    context_sensitivity: float = 0.5
    enable_role_ambiguity_resolution: bool = True
    
    # Recursive/hierarchical binding settings
    max_recursion_depth: int = 5
    recursive_strength_decay: float = 0.8
    enable_hierarchical_unbinding: bool = True
    
    # Multi-dimensional tensor settings  
    enable_variable_dimensions: bool = False
    role_dimension_map: Optional[Dict[str, int]] = None
    filler_dimension_map: Optional[Dict[str, int]] = None
    
    # Unbinding configuration
    unbinding_method: UnbindingMethod = UnbindingMethod.REGULARIZED
    regularization_lambda: float = 0.001
    max_unbinding_iterations: int = 100
    unbinding_tolerance: float = 1e-6
    
    # Noise and robustness settings
    noise_tolerance: float = 0.1
    enable_cleanup_memory: bool = True
    cleanup_threshold: float = 0.7
    
    # Performance settings  
    enable_caching: bool = True
    enable_gpu_acceleration: bool = False  # For future GPU implementations


@dataclass
class BindingPair:
    """Represents a variable-value binding pair with advanced configuration"""
    variable: str
    value: Union[str, np.ndarray]
    role_vector: Optional[np.ndarray] = None
    filler_vector: Optional[np.ndarray] = None
    binding_strength: float = 1.0
    context: Optional[List[str]] = None
    hierarchical_level: int = 0