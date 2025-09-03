"""
⚙️ Configuration Classes for Tensor Product Binding
===================================================

This module defines the main configuration classes used throughout the
tensor product binding system. These dataclasses provide structured
configuration with sensible defaults and validation.

Based on Smolensky (1990) with modern extensions for neural architectures.
"""

import numpy as np
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field

from .enums import (
    BindingOperation,
    BindingMethod,
    UnbindingMethod,
    VectorSpaceType,
    OptimizationLevel,
    NoiseModel
)


@dataclass
class VectorSpaceConfig:
    """
    🌌 Configuration for vector space management.
    
    Controls how vector spaces are created and managed:
    - Dimensionality settings
    - Orthogonality constraints
    - Normalization options
    - Capacity limits
    """
    dimension: int = 100
    space_type: VectorSpaceType = VectorSpaceType.ROLE_SPACE
    orthogonal_constraint: bool = True
    normalize_vectors: bool = True
    max_capacity: Optional[int] = None
    initialization_method: str = "random_normal"
    random_seed: Optional[int] = None


@dataclass
class PerformanceConfig:
    """
    ⚡ Performance and optimization configuration.
    
    Controls performance-related settings:
    - Caching strategies
    - Memory management
    - GPU acceleration
    - Parallel processing
    """
    enable_caching: bool = True
    cache_size_limit: int = 1000
    enable_gpu_acceleration: bool = False
    enable_parallel_processing: bool = False
    optimization_level: OptimizationLevel = OptimizationLevel.BALANCED
    memory_efficient_mode: bool = False
    batch_size: int = 32


@dataclass
class NoiseConfig:
    """
    🔊 Noise and robustness configuration.
    
    Controls noise handling and robustness features:
    - Noise models and levels
    - Cleanup thresholds
    - Tolerance settings
    """
    noise_model: NoiseModel = NoiseModel.GAUSSIAN
    noise_level: float = 0.0
    noise_tolerance: float = 0.1
    enable_cleanup_memory: bool = True
    cleanup_threshold: float = 0.7
    regularization_lambda: float = 0.001


@dataclass
class TensorBindingConfig:
    """
    🧠 Main configuration class for tensor product binding system.
    
    This is the primary configuration class that controls all aspects
    of the tensor product binding system. It provides comprehensive
    configuration with sensible defaults for research and practical use.
    
    Parameters
    ----------
    vector_dim : int, default=100
        Dimension of role and filler vectors
    binding_method : BindingMethod
        Primary binding strategy to use
    binding_operation : BindingOperation  
        Core binding operation (outer product, convolution, etc.)
    unbinding_method : UnbindingMethod
        Method for extracting information from bound structures
    """
    
    # Core dimensions and methods
    vector_dim: int = 100
    binding_method: BindingMethod = BindingMethod.BASIC_OUTER_PRODUCT
    binding_operation: BindingOperation = BindingOperation.OUTER_PRODUCT
    unbinding_method: UnbindingMethod = UnbindingMethod.REGULARIZED
    
    # Binding strength and modulation
    enable_binding_strength: bool = True
    default_binding_strength: float = 1.0
    strength_decay_factor: float = 0.95  # For temporal binding sequences
    normalize_bindings: bool = True
    
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
    max_unbinding_iterations: int = 100
    unbinding_tolerance: float = 1e-6
    
    # Sub-configurations
    vector_space_config: VectorSpaceConfig = field(default_factory=VectorSpaceConfig)
    performance_config: PerformanceConfig = field(default_factory=PerformanceConfig)
    noise_config: NoiseConfig = field(default_factory=NoiseConfig)
    
    # Advanced features
    enable_symbolic_reasoning: bool = False
    enable_compositional_semantics: bool = True
    enable_structure_preservation: bool = True
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.vector_dim <= 0:
            raise ValueError("vector_dim must be positive")
        
        if not 0 <= self.default_binding_strength <= 2:
            raise ValueError("default_binding_strength should be between 0 and 2")
        
        if not 0 <= self.strength_decay_factor <= 1:
            raise ValueError("strength_decay_factor should be between 0 and 1")
        
        # Update vector space config dimension to match main config
        self.vector_space_config.dimension = self.vector_dim
    
    def get_role_dimension(self, role_name: Optional[str] = None) -> int:
        """Get dimension for a specific role or default."""
        if self.enable_variable_dimensions and self.role_dimension_map and role_name:
            return self.role_dimension_map.get(role_name, self.vector_dim)
        return self.vector_dim
    
    def get_filler_dimension(self, filler_name: Optional[str] = None) -> int:
        """Get dimension for a specific filler or default."""
        if self.enable_variable_dimensions and self.filler_dimension_map and filler_name:
            return self.filler_dimension_map.get(filler_name, self.vector_dim)
        return self.vector_dim


@dataclass
class BindingPair:
    """
    🔗 Represents a variable-value binding pair with metadata.
    
    A binding pair encapsulates a role-filler binding with all necessary
    metadata for advanced tensor product binding operations.
    
    Parameters
    ----------
    variable : str
        The role/variable name (e.g., "SUBJECT", "OBJECT")
    value : Union[str, np.ndarray]
        The filler/value (symbol name or vector)
    role_vector : np.ndarray, optional
        The role vector representation
    filler_vector : np.ndarray, optional
        The filler vector representation
    binding_strength : float, default=1.0
        Strength of this binding (0.0 to 2.0)
    context : List[str], optional
        Context information for contextual binding
    hierarchical_level : int, default=0
        Level in hierarchical structure (0 = root)
    """
    variable: str
    value: Union[str, np.ndarray]
    role_vector: Optional[np.ndarray] = None
    filler_vector: Optional[np.ndarray] = None
    binding_strength: float = 1.0
    context: Optional[List[str]] = None
    hierarchical_level: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate binding pair after initialization."""
        if not 0 <= self.binding_strength <= 2:
            raise ValueError("binding_strength should be between 0 and 2")
        
        if self.hierarchical_level < 0:
            raise ValueError("hierarchical_level must be non-negative")
        
        if self.context is None:
            self.context = []


@dataclass 
class StructureConfig:
    """
    🏗️ Configuration for structural representations.
    
    Controls how complex structures are built and managed:
    - Composition strategies
    - Recursive processing
    - Memory management for structures
    """
    max_structure_depth: int = 10
    enable_structure_caching: bool = True
    structure_similarity_threshold: float = 0.8
    enable_structure_validation: bool = True
    composition_method: str = "weighted_superposition"
    enable_structure_cleanup: bool = True