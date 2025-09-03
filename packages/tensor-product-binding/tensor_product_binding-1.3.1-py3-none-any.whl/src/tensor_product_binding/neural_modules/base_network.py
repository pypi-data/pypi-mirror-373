"""
Base Neural Binding Network
===========================

Author: Benedict Chen (benedict@benedictchen.com)

Abstract base class for neural binding implementations.
"""

from abc import ABC, abstractmethod
from typing import Optional, Any, Dict, Tuple
import numpy as np
from .configurations import TrainingConfig


class NeuralBindingNetwork(ABC):
    """
    Abstract base class for neural networks that perform tensor product binding
    
    This class provides the interface for neural implementations of variable binding
    that can learn binding patterns from data.
    """
    
    def __init__(self,
                 vector_dim: int = 512,
                 role_vocab_size: int = 1000,
                 filler_vocab_size: int = 1000,
                 config: Optional[TrainingConfig] = None):
        """
        Initialize Neural Binding Network
        
        Args:
            vector_dim: Dimensionality of vector representations
            role_vocab_size: Size of role vocabulary
            filler_vocab_size: Size of filler vocabulary
            config: Training configuration
        """
        self.vector_dim = vector_dim
        self.role_vocab_size = role_vocab_size
        self.filler_vocab_size = filler_vocab_size
        self.config = config or TrainingConfig()
        
        # Initialize base components
        self.is_trained = False
        self.training_history = []
        
    @abstractmethod
    def train(self, training_data: Dict[str, Any]) -> Dict[str, Any]:
        """Train the neural binding network"""
        pass
        
    @abstractmethod
    def bind(self, roles: np.ndarray, fillers: np.ndarray) -> np.ndarray:
        """Perform neural binding operation"""
        pass
        
    @abstractmethod 
    def unbind(self, bound_representation: np.ndarray, query_role: np.ndarray) -> np.ndarray:
        """Perform neural unbinding operation"""
        pass
        
    @abstractmethod
    def evaluate(self, test_data: Dict[str, Any]) -> Dict[str, float]:
        """Evaluate network performance"""
        pass
        
    def get_training_history(self) -> list:
        """Get training history"""
        return self.training_history
        
    def is_network_trained(self) -> bool:
        """Check if network has been trained"""
        return self.is_trained