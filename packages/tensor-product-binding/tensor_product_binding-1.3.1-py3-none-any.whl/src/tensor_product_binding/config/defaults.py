"""
📋 Default Configurations for Tensor Product Binding
====================================================

This module provides default configuration presets and constants for
the tensor product binding system. These defaults are based on research
best practices and typical use cases.

Usage:
    from tensor_product_binding.config import DEFAULT_CONFIG, OPTIMIZATION_PRESETS
    config = DEFAULT_CONFIG.copy()  # Start with defaults
    config.vector_dim = 200         # Customize as needed
"""

from typing import Dict, Any
from .config_classes import (
    TensorBindingConfig, 
    VectorSpaceConfig, 
    PerformanceConfig,
    NoiseConfig
)
from .enums import (
    BindingOperation,
    BindingMethod,
    UnbindingMethod,
    VectorSpaceType,
    OptimizationLevel,
    NoiseModel
)


# Core default values
DEFAULT_VECTOR_DIM = 100
DEFAULT_BINDING_STRENGTH = 1.0
DEFAULT_NOISE_LEVEL = 0.0
DEFAULT_CLEANUP_THRESHOLD = 0.7


# Default vector space configurations for different space types
DEFAULT_ROLE_SPACE_CONFIG = VectorSpaceConfig(
    dimension=DEFAULT_VECTOR_DIM,
    space_type=VectorSpaceType.ROLE_SPACE,
    orthogonal_constraint=True,
    normalize_vectors=True,
    max_capacity=None
)

DEFAULT_FILLER_SPACE_CONFIG = VectorSpaceConfig(
    dimension=DEFAULT_VECTOR_DIM,
    space_type=VectorSpaceType.FILLER_SPACE,
    orthogonal_constraint=False,  # Allow richer semantic relationships
    normalize_vectors=True,
    max_capacity=None
)

DEFAULT_BINDING_SPACE_CONFIG = VectorSpaceConfig(
    dimension=DEFAULT_VECTOR_DIM * DEFAULT_VECTOR_DIM,  # Outer product dimension
    space_type=VectorSpaceType.BINDING_SPACE,
    orthogonal_constraint=False,
    normalize_vectors=True,
    max_capacity=1000  # Limit to prevent memory issues
)


# Default performance configuration
DEFAULT_PERFORMANCE_CONFIG = PerformanceConfig(
    enable_caching=True,
    cache_size_limit=1000,
    enable_gpu_acceleration=False,
    enable_parallel_processing=False,
    optimization_level=OptimizationLevel.BALANCED,
    memory_efficient_mode=False,
    batch_size=32
)


# Default noise configuration
DEFAULT_NOISE_CONFIG = NoiseConfig(
    noise_model=NoiseModel.GAUSSIAN,
    noise_level=DEFAULT_NOISE_LEVEL,
    noise_tolerance=0.1,
    enable_cleanup_memory=True,
    cleanup_threshold=DEFAULT_CLEANUP_THRESHOLD,
    regularization_lambda=0.001
)


# Main default configuration
DEFAULT_CONFIG = TensorBindingConfig(
    # Core settings
    vector_dim=DEFAULT_VECTOR_DIM,
    binding_method=BindingMethod.BASIC_OUTER_PRODUCT,
    binding_operation=BindingOperation.OUTER_PRODUCT,
    unbinding_method=UnbindingMethod.REGULARIZED,
    
    # Binding modulation
    enable_binding_strength=True,
    default_binding_strength=DEFAULT_BINDING_STRENGTH,
    strength_decay_factor=0.95,
    normalize_bindings=True,
    
    # Context and hierarchy
    context_window_size=3,
    context_sensitivity=0.5,
    enable_role_ambiguity_resolution=True,
    max_recursion_depth=5,
    recursive_strength_decay=0.8,
    enable_hierarchical_unbinding=True,
    
    # Advanced features
    enable_variable_dimensions=False,
    role_dimension_map=None,
    filler_dimension_map=None,
    
    # Unbinding parameters
    max_unbinding_iterations=100,
    unbinding_tolerance=1e-6,
    
    # Sub-configurations
    vector_space_config=DEFAULT_ROLE_SPACE_CONFIG,
    performance_config=DEFAULT_PERFORMANCE_CONFIG,
    noise_config=DEFAULT_NOISE_CONFIG,
    
    # Feature flags
    enable_symbolic_reasoning=False,
    enable_compositional_semantics=True,
    enable_structure_preservation=True
)


# Optimization presets for different use cases
OPTIMIZATION_PRESETS: Dict[str, Dict[str, Any]] = {
    "research_accuracy": {
        "description": "Maximum accuracy for research applications",
        "vector_dim": 200,
        "binding_operation": BindingOperation.OUTER_PRODUCT,
        "unbinding_method": UnbindingMethod.LEAST_SQUARES,
        "noise_config.regularization_lambda": 0.0001,
        "performance_config.optimization_level": OptimizationLevel.ACCURACY,
        "max_unbinding_iterations": 1000,
        "unbinding_tolerance": 1e-8
    },
    
    "production_balanced": {
        "description": "Balanced performance for production use",
        "vector_dim": 100,
        "binding_operation": BindingOperation.OUTER_PRODUCT,
        "unbinding_method": UnbindingMethod.REGULARIZED,
        "noise_config.regularization_lambda": 0.001,
        "performance_config.optimization_level": OptimizationLevel.BALANCED,
        "performance_config.enable_caching": True,
        "max_unbinding_iterations": 100
    },
    
    "high_performance": {
        "description": "Maximum speed for real-time applications",
        "vector_dim": 64,
        "binding_operation": BindingOperation.CIRCULAR_CONVOLUTION,
        "unbinding_method": UnbindingMethod.BASIC_MULTIPLICATION,
        "performance_config.optimization_level": OptimizationLevel.PERFORMANCE,
        "performance_config.enable_caching": True,
        "performance_config.memory_efficient_mode": True,
        "max_unbinding_iterations": 10,
        "enable_binding_strength": False
    },
    
    "memory_efficient": {
        "description": "Minimal memory usage for constrained environments",
        "vector_dim": 32,
        "binding_operation": BindingOperation.ADDITION,
        "unbinding_method": UnbindingMethod.BASIC_MULTIPLICATION,
        "performance_config.optimization_level": OptimizationLevel.MEMORY_EFFICIENT,
        "performance_config.memory_efficient_mode": True,
        "performance_config.cache_size_limit": 100,
        "enable_compositional_semantics": False,
        "max_recursion_depth": 2
    },
    
    "robust_noisy": {
        "description": "Robust operation in noisy environments",
        "vector_dim": 150,
        "binding_operation": BindingOperation.OUTER_PRODUCT,
        "unbinding_method": UnbindingMethod.REGULARIZED,
        "noise_config.noise_tolerance": 0.2,
        "noise_config.regularization_lambda": 0.01,
        "noise_config.enable_cleanup_memory": True,
        "noise_config.cleanup_threshold": 0.6,
        "enable_role_ambiguity_resolution": True,
        "context_sensitivity": 0.8
    },
    
    "compositional_nlp": {
        "description": "Optimized for natural language processing",
        "vector_dim": 300,  # Common word embedding dimension
        "binding_operation": BindingOperation.OUTER_PRODUCT,
        "enable_compositional_semantics": True,
        "enable_hierarchical_unbinding": True,
        "max_recursion_depth": 8,
        "context_window_size": 5,
        "enable_role_ambiguity_resolution": True,
        "binding_method": BindingMethod.CONTEXT_DEPENDENT
    }
}


def apply_preset(config: TensorBindingConfig, preset_name: str) -> TensorBindingConfig:
    """
    Apply a configuration preset to modify an existing configuration.
    
    Parameters
    ----------
    config : TensorBindingConfig
        The configuration to modify
    preset_name : str
        Name of the preset to apply
        
    Returns
    -------
    TensorBindingConfig
        Modified configuration with preset applied
        
    Raises
    ------
    ValueError
        If preset_name is not found
    """
    if preset_name not in OPTIMIZATION_PRESETS:
        available = ", ".join(OPTIMIZATION_PRESETS.keys())
        raise ValueError(f"Unknown preset '{preset_name}'. Available: {available}")
    
    preset = OPTIMIZATION_PRESETS[preset_name]
    
    # Apply preset values to config
    for key, value in preset.items():
        if key == "description":
            continue  # Skip description field
            
        # Handle nested attribute setting (e.g., "noise_config.regularization_lambda")
        if "." in key:
            obj_path, attr_name = key.rsplit(".", 1)
            obj = config
            for part in obj_path.split("."):
                obj = getattr(obj, part)
            setattr(obj, attr_name, value)
        else:
            setattr(config, key, value)
    
    return config


def get_preset_description(preset_name: str) -> str:
    """Get description of a configuration preset."""
    if preset_name not in OPTIMIZATION_PRESETS:
        raise ValueError(f"Unknown preset '{preset_name}'")
    return OPTIMIZATION_PRESETS[preset_name].get("description", "No description available")


def list_presets() -> Dict[str, str]:
    """Get dictionary of all available presets and their descriptions."""
    return {
        name: preset.get("description", "No description")
        for name, preset in OPTIMIZATION_PRESETS.items()
    }