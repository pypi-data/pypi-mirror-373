"""
Neural Binding Configurations
=============================

Author: Benedict Chen (benedict@benedictchen.com)

Configuration classes for neural binding networks.
"""

from dataclasses import dataclass
from typing import List, Optional


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