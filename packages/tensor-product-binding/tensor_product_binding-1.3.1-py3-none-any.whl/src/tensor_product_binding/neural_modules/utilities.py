"""
Neural Binding Utilities
========================

Author: Benedict Chen (benedict@benedictchen.com)

Utility functions for neural binding networks.
"""

import numpy as np
from typing import Dict, Any, Tuple
from .base_network import NeuralBindingNetwork
from .pytorch_network import PyTorchBindingNetwork 
from .numpy_network import NumPyBindingNetwork
from .configurations import TrainingConfig


def create_neural_binding_network(backend: str = "auto", **kwargs) -> NeuralBindingNetwork:
    """
    Factory function to create neural binding networks
    
    Args:
        backend: Backend to use ('pytorch', 'numpy', 'auto')
        **kwargs: Additional arguments for network initialization
        
    Returns:
        NeuralBindingNetwork instance
    """
    if backend == "auto":
        try:
            import torch
            backend = "pytorch"
        except ImportError:
            backend = "numpy"
    
    if backend == "pytorch":
        return PyTorchBindingNetwork(**kwargs)
    elif backend == "numpy":
        return NumPyBindingNetwork(**kwargs)
    else:
        raise ValueError(f"Unknown backend: {backend}")


def generate_training_data(n_samples: int = 1000,
                          vector_dim: int = 512,
                          role_vocab_size: int = 1000,
                          filler_vocab_size: int = 1000,
                          seed: int = 42) -> Dict[str, np.ndarray]:
    """
    Generate synthetic training data for neural binding
    
    Args:
        n_samples: Number of training samples
        vector_dim: Dimension of vectors
        role_vocab_size: Size of role vocabulary
        filler_vocab_size: Size of filler vocabulary
        seed: Random seed
        
    Returns:
        Dictionary containing training data
    """
    np.random.seed(seed)
    
    # Generate random one-hot encoded roles and fillers
    roles = np.zeros((n_samples, role_vocab_size))
    fillers = np.zeros((n_samples, filler_vocab_size))
    
    for i in range(n_samples):
        role_idx = np.random.randint(0, role_vocab_size)
        filler_idx = np.random.randint(0, filler_vocab_size)
        
        roles[i, role_idx] = 1.0
        fillers[i, filler_idx] = 1.0
    
    # Generate target binding representations (simplified)
    targets = np.random.randn(n_samples, vector_dim, vector_dim)
    
    return {
        "roles": roles,
        "fillers": fillers, 
        "targets": targets,
        "n_samples": n_samples
    }


def evaluate_neural_binding(network: NeuralBindingNetwork,
                           test_data: Dict[str, Any],
                           metrics: list = None) -> Dict[str, float]:
    """
    Evaluate neural binding network performance
    
    Args:
        network: Neural binding network
        test_data: Test data dictionary
        metrics: List of metrics to compute
        
    Returns:
        Dictionary of evaluation results
    """
    if metrics is None:
        metrics = ["accuracy", "binding_error", "unbinding_error"]
    
    results = {}
    
    if not network.is_network_trained():
        results["warning"] = "Network not trained"
    
    # Perform binding evaluation
    if "binding_error" in metrics:
        # Simplified binding evaluation
        bound = network.bind(test_data["roles"][:100], test_data["fillers"][:100])
        binding_error = np.mean(np.abs(bound - test_data.get("targets", bound)[:100]))
        results["binding_error"] = binding_error
    
    # Default evaluation from network
    network_results = network.evaluate(test_data)
    results.update(network_results)
    
    return results