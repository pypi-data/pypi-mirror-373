"""
Tensor Product Binding (TPB) Modules

Modular implementation of Tony Plate's Holographic Reduced Representations (HRR)
and Paul Smolensky's Tensor Product Binding for distributed symbolic representation.
"""

from .config_enums import (
    BindingOperation,
    BindingMethod, 
    UnbindingMethod,
    TensorBindingConfig,
    BindingPair
)

from .vector_operations import TPBVector

from .core_binding import CoreBinding

# Import only completed modules for now
__all__ = [
    'BindingOperation',
    'BindingMethod',
    'UnbindingMethod', 
    'TensorBindingConfig',
    'BindingPair',
    'TPBVector',
    'CoreBinding'
]