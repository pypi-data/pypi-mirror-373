"""
🏗️ Neural Binding - Configuration Module
=======================================


Author: Benedict Chen (benedict@benedictchen.com)
Based on: Smolensky (1990) "Tensor Product Variable Binding and the Representation of Symbolic Structures"

🎯 MODULE PURPOSE:
=================
Configuration classes for neural binding networks including training parameters
and network architecture specifications.

🔬 RESEARCH FOUNDATION:
======================
Implements configuration structures for neural tensor product binding based on:
- Smolensky (1990): Theoretical foundation for neural binding operations
- Modern deep learning: Training configuration best practices
- Neural network architecture: Standard hyperparameter management

This module contains the configuration components, split from the
1207-line monolith for specialized configuration management.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class TrainingConfig:
    """Configuration for neural binding training"""
    learning_rate: float = 0.001
    batch_size: int = 32
    n_epochs: int = 100
    weight_decay: float = 1e-5
    dropout_rate: float = 0.1
    validation_split: float = 0.2
    early_stopping_patience: int = 10
    gradient_clip_norm: float = 1.0


@dataclass
class NetworkArchitecture:
    """Configuration for neural network architecture"""
    hidden_layers: List[int]
    activation_function: str = "relu"
    use_batch_norm: bool = False
    use_dropout: bool = True
    initialization_method: str = "xavier"


# Export configuration classes
__all__ = [
    'TrainingConfig',
    'NetworkArchitecture'
]


if __name__ == "__main__":
    print("🏗️ Neural Binding - Configuration Module")
    print("=" * 50)
    print("📊 MODULE CONTENTS:")
    print("  • TrainingConfig - Neural network training parameters")
    print("  • NetworkArchitecture - Network structure configuration")
    print("  • Research-accurate configuration for tensor product binding")
    print("")
    print("✅ Configuration module loaded successfully!")
    print("🔬 Essential configuration for neural binding networks!")