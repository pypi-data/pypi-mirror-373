"""
Neural Binding Networks - Modular Implementation
===============================================

Author: Benedict Chen (benedict@benedictchen.com)

This module provides backward-compatible access to neural binding functionality
through a modular architecture. The original 1207-line neural_binding.py file has been 
split into focused modules for better maintainability.

Original file: old_archive/neural_binding_original_1207_lines.py

Based on:
Smolensky, P. (1990) "Tensor Product Variable Binding and the Representation 
of Symbolic Structures in Connectionist Systems"
"""

# Import all components from modular structure for backward compatibility
from .neural_modules.configurations import TrainingConfig, NetworkArchitecture
from .neural_modules.base_network import NeuralBindingNetwork
from .neural_modules.pytorch_network import PyTorchBindingNetwork
from .neural_modules.numpy_network import NumPyBindingNetwork
from .neural_modules.utilities import (
    create_neural_binding_network,
    generate_training_data,
    evaluate_neural_binding
)

# Export all classes and functions for backward compatibility
__all__ = [
    # Configuration classes
    'TrainingConfig',
    'NetworkArchitecture',
    
    # Network classes
    'NeuralBindingNetwork',
    'PyTorchBindingNetwork',
    'NumPyBindingNetwork',
    
    # Utility functions
    'create_neural_binding_network',
    'generate_training_data',
    'evaluate_neural_binding'
]

# Modularization Summary:
# ======================
# Original neural_binding.py (1207 lines) split into:
# 1. configurations.py (28 lines) - Configuration classes
# 2. base_network.py (64 lines) - Abstract base class
# 3. pytorch_network.py (179 lines) - PyTorch implementation
# 4. numpy_network.py (62 lines) - NumPy implementation  
# 5. utilities.py (82 lines) - Factory functions and utilities
# 6. __init__.py (25 lines) - Module exports
#
# Total modular lines: ~440 lines (64% reduction through cleanup)
# Largest module: 179 lines (85% reduction from original)
# Benefits: Better separation, easier testing, cleaner imports