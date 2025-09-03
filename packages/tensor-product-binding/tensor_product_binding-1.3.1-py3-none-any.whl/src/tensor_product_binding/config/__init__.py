"""
🔧 Configuration Module for Tensor Product Binding
==================================================

This module provides all configuration parameters, enums, and data classes
for the tensor product binding system. It consolidates settings and provides
a clean interface for configuring TPB operations.

Main Components:
- BindingOperation: Different binding operation types  
- TensorBindingConfig: Main configuration class
- BindingPair: Data class for variable-value binding pairs
- Performance settings and optimization parameters
"""

from .enums import (
    BindingOperation,
    BindingMethod,
    UnbindingMethod,
    VectorSpaceType,
    StructureType
)
from .config_classes import (
    TensorBindingConfig,
    BindingPair,
    VectorSpaceConfig,
    PerformanceConfig
)
from .defaults import (
    DEFAULT_CONFIG,
    DEFAULT_VECTOR_DIM,
    DEFAULT_BINDING_STRENGTH,
    OPTIMIZATION_PRESETS,
    apply_preset,
    get_preset_description,
    list_presets
)

__all__ = [
    # Enums
    'BindingOperation',
    'BindingMethod', 
    'UnbindingMethod',
    'VectorSpaceType',
    'StructureType',
    
    # Configuration Classes
    'TensorBindingConfig',
    'BindingPair',
    'VectorSpaceConfig',
    'PerformanceConfig',
    
    # Defaults
    'DEFAULT_CONFIG',
    'DEFAULT_VECTOR_DIM',
    'DEFAULT_BINDING_STRENGTH',
    'OPTIMIZATION_PRESETS',
    
    # Preset utilities
    'apply_preset',
    'get_preset_description',
    'list_presets'
]