"""
🧠 Tensor Product Binding - Core Module
=======================================

Core algorithms and implementations for tensor product variable binding.

Based on Smolensky (1990) "Tensor Product Variable Binding and the 
Representation of Symbolic Structures in Connectionist Systems"

This module provides:
- Main TensorProductBinding class
- Core binding operations
- Vector space management
- Binding/unbinding algorithms
"""

from .binding_operations import TensorProductBinding, TPBVector, BindingOperation
from .vector_spaces import VectorSpace, SymbolicVector
from .algorithms import bind_vectors, unbind_vectors, cleanup_vector

__all__ = [
    'TensorProductBinding',
    'TPBVector', 
    'BindingOperation',
    'VectorSpace',
    'SymbolicVector',
    'bind_vectors',
    'unbind_vectors',
    'cleanup_vector'
]