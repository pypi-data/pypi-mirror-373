"""
Neural Binding Modules
======================

Modular neural binding network implementations.
"""

from .configurations import TrainingConfig, NetworkArchitecture
from .base_network import NeuralBindingNetwork
from .pytorch_network import PyTorchBindingNetwork
from .numpy_network import NumPyBindingNetwork
from .utilities import (
    create_neural_binding_network,
    generate_training_data,
    evaluate_neural_binding
)

# NEW: Complete neural implementations - ALL SOLUTIONS FROM FIXME COMMENTS
from .complete_neural_implementations import (
    NeuralBindingConfig,
    CompleteTensorProductBinder,
    create_mlp_binder,
    create_attention_binder,
    create_cnn_binder,
    create_hybrid_binder
)

__all__ = [
    # Original exports (PRESERVED)
    'TrainingConfig',
    'NetworkArchitecture', 
    'NeuralBindingNetwork',
    'PyTorchBindingNetwork',
    'NumPyBindingNetwork',
    'create_neural_binding_network',
    'generate_training_data', 
    'evaluate_neural_binding',
    
    # NEW: Complete neural implementations (ADDITIVE)
    'NeuralBindingConfig',
    'CompleteTensorProductBinder',
    'create_mlp_binder',
    'create_attention_binder',
    'create_cnn_binder', 
    'create_hybrid_binder'
]