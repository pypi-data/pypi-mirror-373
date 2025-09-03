"""
🏗️ Neural Binding - NumPy Implementation Module
=============================================


Author: Benedict Chen (benedict@benedictchen.com)
Based on: Smolensky (1990) "Tensor Product Variable Binding and the Representation of Symbolic Structures"

🎯 MODULE PURPOSE:
=================
NumPy-based neural network implementation for tensor product binding,
providing CPU-optimized learning without external deep learning dependencies.

🔬 RESEARCH FOUNDATION:
======================
Implements NumPy neural tensor product binding based on:
- Smolensky (1990): Theoretical foundation for neural binding operations
- Classical neural networks: Feedforward networks with backpropagation
- NumPy linear algebra: Efficient matrix operations for binding

This module contains the NumPy implementation and utilities, split from the
1207-line monolith for specialized CPU-based neural functionality.
"""

import numpy as np
from typing import List, Tuple, Dict, Any, Optional, Callable
from .abstract_base import NeuralBindingNetwork
from .configuration import TrainingConfig, NetworkArchitecture


class NumPyBindingNetwork(NeuralBindingNetwork):
    """
    🧮 NumPy Neural Network for Tensor Product Binding - Pure Python!
    
    CPU-optimized neural implementation using only NumPy for learning
    binding patterns with classical backpropagation algorithms.
    
    🏗️ **Network Architecture**:
    ```
    Role Input → [Dense Layer] → [Activation] → Binding Output
                      ↑              ↓
    Filler Input → [Dense Layer] → [Activation] → 
    ```
    
    ⚡ **Key Features**:
    - Zero external dependencies (NumPy only)
    - Classical backpropagation implementation
    - Memory-efficient CPU operations
    - Educational transparency of algorithms
    """
    
    def __init__(self,
                 vector_dim: int = 512,
                 role_vocab_size: int = 1000,
                 filler_vocab_size: int = 1000,
                 config: Optional[TrainingConfig] = None,
                 architecture: Optional[NetworkArchitecture] = None):
        """
        Initialize NumPy Neural Binding Network
        
        Args:
            vector_dim: Dimensionality of vector representations
            role_vocab_size: Size of role vocabulary
            filler_vocab_size: Size of filler vocabulary
            config: Training configuration
            architecture: Network architecture configuration
        """
        super().__init__(vector_dim, role_vocab_size, filler_vocab_size, config)
        
        # Network architecture configuration
        self.architecture = architecture or NetworkArchitecture(
            hidden_layers=[256, 128, 64],
            activation_function='relu',
            use_batch_norm=False,  # Not implemented for NumPy
            use_dropout=True
        )
        
        # Network weights and biases
        self.binding_weights = []
        self.binding_biases = []
        self.unbinding_weights = []
        self.unbinding_biases = []
        
        # Build network architecture
        self._initialize_networks()
        
        print(f"✅ NumPy Binding Network initialized")
        print(f"🏗️ Architecture: {len(self.architecture.hidden_layers)} hidden layers")
        print(f"⚡ Parameters: ~{self._count_parameters():,} trainable")
    
    def _initialize_networks(self):
        """
        🏗️ Initialize NumPy Network Weights - Xavier Initialization
        
        Creates weight matrices and bias vectors for binding and unbinding
        networks using Xavier initialization for stable training.
        """
        np.random.seed(42)  # Reproducible initialization
        
        # Binding network dimensions
        input_dim = self.vector_dim * 2  # Concatenated role and filler
        output_dim = self.vector_dim * self.vector_dim  # Tensor product
        
        binding_dims = [input_dim] + self.architecture.hidden_layers + [output_dim]
        
        # Initialize binding network weights
        for i in range(len(binding_dims) - 1):
            fan_in, fan_out = binding_dims[i], binding_dims[i + 1]
            
            # Xavier initialization
            limit = np.sqrt(6.0 / (fan_in + fan_out))
            weight = np.random.uniform(-limit, limit, (fan_in, fan_out))
            bias = np.zeros(fan_out)
            
            self.binding_weights.append(weight)
            self.binding_biases.append(bias)
        
        # Unbinding network dimensions (reversed for symmetry)
        unbinding_input_dim = output_dim + self.vector_dim  # Bound + role
        unbinding_output_dim = self.vector_dim  # Recovered filler
        
        unbinding_dims = ([unbinding_input_dim] + 
                         list(reversed(self.architecture.hidden_layers)) + 
                         [unbinding_output_dim])
        
        # Initialize unbinding network weights
        for i in range(len(unbinding_dims) - 1):
            fan_in, fan_out = unbinding_dims[i], unbinding_dims[i + 1]
            
            # Xavier initialization
            limit = np.sqrt(6.0 / (fan_in + fan_out))
            weight = np.random.uniform(-limit, limit, (fan_in, fan_out))
            bias = np.zeros(fan_out)
            
            self.unbinding_weights.append(weight)
            self.unbinding_biases.append(bias)
    
    def _count_parameters(self) -> int:
        """Count total trainable parameters"""
        binding_params = sum(w.size for w in self.binding_weights + self.binding_biases)
        unbinding_params = sum(w.size for w in self.unbinding_weights + self.unbinding_biases)
        return binding_params + unbinding_params
    
    def _activation_function(self, x: np.ndarray) -> np.ndarray:
        """Apply activation function"""
        if self.architecture.activation_function.lower() == 'relu':
            return np.maximum(0, x)
        elif self.architecture.activation_function.lower() == 'tanh':
            return np.tanh(x)
        elif self.architecture.activation_function.lower() == 'sigmoid':
            return 1 / (1 + np.exp(-np.clip(x, -500, 500)))
        else:
            return x  # Linear activation
    
    def _activation_derivative(self, x: np.ndarray) -> np.ndarray:
        """Compute activation function derivative"""
        if self.architecture.activation_function.lower() == 'relu':
            return (x > 0).astype(float)
        elif self.architecture.activation_function.lower() == 'tanh':
            return 1 - np.tanh(x) ** 2
        elif self.architecture.activation_function.lower() == 'sigmoid':
            s = 1 / (1 + np.exp(-np.clip(x, -500, 500)))
            return s * (1 - s)
        else:
            return np.ones_like(x)  # Linear derivative
    
    def _forward_pass(self, input_data: np.ndarray, network: str) -> Tuple[np.ndarray, List[np.ndarray]]:
        """
        🔄 Forward Pass Through Network
        
        Args:
            input_data: Input data [batch_size, input_dim]
            network: 'binding' or 'unbinding'
            
        Returns:
            Tuple[output, activations]: Final output and intermediate activations
        """
        if network == 'binding':
            weights, biases = self.binding_weights, self.binding_biases
        else:
            weights, biases = self.unbinding_weights, self.unbinding_biases
        
        activations = [input_data]
        current_input = input_data
        
        # Forward through all layers
        for i, (weight, bias) in enumerate(zip(weights, biases)):
            # Linear transformation
            linear_output = np.dot(current_input, weight) + bias
            
            # Apply activation (except for output layer)
            if i < len(weights) - 1:
                activated_output = self._activation_function(linear_output)
                
                # Dropout during training
                if self.architecture.use_dropout and hasattr(self, '_training_mode') and self._training_mode:
                    dropout_mask = np.random.binomial(1, 1 - self.config.dropout_rate, activated_output.shape)
                    activated_output *= dropout_mask / (1 - self.config.dropout_rate)
                
                current_input = activated_output
            else:
                current_input = linear_output  # No activation on output layer
            
            activations.append(current_input)
        
        return current_input, activations
    
    def bind(self, role_vectors: np.ndarray, filler_vectors: np.ndarray) -> np.ndarray:
        """
        🧠 NumPy Neural Binding - Pure Python Implementation!
        
        Implements CPU-optimized neural tensor product binding using
        classical feedforward networks and NumPy operations.
        
        Args:
            role_vectors: Role vectors [batch_size, role_dim] or [role_dim]
            filler_vectors: Filler vectors [batch_size, filler_dim] or [filler_dim]
            
        Returns:
            np.ndarray: Bound representations [batch_size, product_dim]
            
        🧮 **NumPy Advantages**:
        - No external dependencies
        - Educational transparency
        - Memory-efficient CPU operations
        - Deterministic behavior
        
        📊 **Network Process**:
        ```
        [Role, Filler] → Dense → ReLU → Dense → ReLU → Output
        ```
        """
        if not self.is_trained:
            # Use parent class fallback implementation
            return super().bind(role_vectors, filler_vectors)
        
        # Ensure 2D arrays
        if role_vectors.ndim == 1:
            role_vectors = role_vectors.reshape(1, -1)
        if filler_vectors.ndim == 1:
            filler_vectors = filler_vectors.reshape(1, -1)
        
        # Concatenate role and filler
        input_data = np.concatenate([role_vectors, filler_vectors], axis=1)
        
        # Forward pass through binding network
        output, _ = self._forward_pass(input_data, 'binding')
        
        # Return original shape if input was 1D
        if output.shape[0] == 1 and role_vectors.shape[0] == 1:
            return output.squeeze(0)
        
        return output
    
    def unbind(self, bound_vector: np.ndarray, role_vector: np.ndarray) -> np.ndarray:
        """
        🔓 NumPy Neural Unbinding - Classical Algorithm Implementation!
        
        Uses trained NumPy network to recover filler vectors from
        bound representations using classical neural networks.
        
        Args:
            bound_vector: Bound representation [batch_size, product_dim] or [product_dim]
            role_vector: Role vector [batch_size, role_dim] or [role_dim]
            
        Returns:
            np.ndarray: Recovered filler vectors [batch_size, filler_dim]
            
        🎯 **Recovery Algorithm**:
        1. Concatenate bound representation with role vector
        2. Forward pass through unbinding network
        3. Classical backpropagation-trained weights
        
        📈 **Accuracy Features**:
        - Learned inverse transformations
        - Multi-layer approximation
        - Robust to noise and distortion
        """
        if not self.is_trained:
            # Use parent class fallback implementation
            return super().unbind(bound_vector, role_vector)
        
        # Ensure 2D arrays
        if bound_vector.ndim == 1:
            bound_vector = bound_vector.reshape(1, -1)
        if role_vector.ndim == 1:
            role_vector = role_vector.reshape(1, -1)
        
        # Concatenate bound vector and role
        input_data = np.concatenate([bound_vector, role_vector], axis=1)
        
        # Forward pass through unbinding network
        output, _ = self._forward_pass(input_data, 'unbinding')
        
        # Return original shape if input was 1D
        if output.shape[0] == 1 and bound_vector.shape[0] == 1:
            return output.squeeze(0)
        
        return output
    
    def train(self, training_data: List[Tuple[np.ndarray, np.ndarray, np.ndarray]]) -> Dict[str, Any]:
        """
        🎓 NumPy Neural Training - Classical Backpropagation!
        
        Trains binding and unbinding networks using classical backpropagation
        algorithm implemented in pure NumPy for educational clarity.
        
        Args:
            training_data: List of (role_vector, filler_vector, target_binding) tuples
                          
        Returns:
            Dict containing training metrics:
                - 'loss': Final training loss
                - 'binding_loss': Binding network loss
                - 'unbinding_loss': Unbinding network loss
                - 'epochs': Number of training epochs
                - 'convergence': Whether training converged
                
        🧮 **Classical Training Process**:
        ```
        Phase 1: Binding Network Training
        ├── Forward Pass: Role+Filler → Bound
        ├── Loss: MSE(Predicted, Target)
        └── Backprop: Update Weights via Gradients
        
        Phase 2: Unbinding Network Training  
        ├── Forward Pass: Bound+Role → Filler
        ├── Loss: MSE(Predicted, Original Filler)
        └── Backprop: Update Weights via Gradients
        
        Phase 3: Joint Optimization
        └── Alternate between binding and unbinding updates
        ```
        
        📚 **Educational Benefits**:
        - Transparent algorithm implementation
        - Step-by-step gradient computation
        - Classical neural network theory
        """
        print(f"🎓 Training NumPy Neural Binding Network on {len(training_data)} examples...")
        print("🧮 Using classical backpropagation with pure NumPy")
        
        # Enable training mode for dropout
        self._training_mode = True
        
        # Prepare training data
        roles, fillers, targets = zip(*training_data)
        roles = np.array([r.flatten() if r.ndim > 1 else r for r in roles])
        fillers = np.array([f.flatten() if f.ndim > 1 else f for f in fillers])
        targets = np.array([t.flatten() if t.ndim > 1 else t for t in targets])
        
        # Training configuration
        n_epochs = self.config.n_epochs
        learning_rate = self.config.learning_rate
        batch_size = self.config.batch_size
        
        # Training history
        binding_losses = []
        unbinding_losses = []
        total_losses = []
        
        n_samples = len(training_data)
        n_batches = max(1, n_samples // batch_size)
        
        # Training loop
        for epoch in range(n_epochs):
            epoch_binding_loss = 0.0
            epoch_unbinding_loss = 0.0
            
            # Shuffle data
            indices = np.random.permutation(n_samples)
            
            # Training phase selection
            if epoch < n_epochs // 3:
                train_binding, train_unbinding = True, False
                phase = "Binding"
            elif epoch < 2 * n_epochs // 3:
                train_binding, train_unbinding = False, True
                phase = "Unbinding"
            else:
                train_binding, train_unbinding = True, True
                phase = "Joint"
            
            # Mini-batch training
            for batch_idx in range(n_batches):
                start_idx = batch_idx * batch_size
                end_idx = min(start_idx + batch_size, n_samples)
                batch_indices = indices[start_idx:end_idx]
                
                role_batch = roles[batch_indices]
                filler_batch = fillers[batch_indices]
                target_batch = targets[batch_indices]
                
                # Binding network training
                if train_binding:
                    binding_loss = self._train_binding_batch(
                        role_batch, filler_batch, target_batch, learning_rate
                    )
                    epoch_binding_loss += binding_loss
                
                # Unbinding network training
                if train_unbinding:
                    unbinding_loss = self._train_unbinding_batch(
                        role_batch, filler_batch, target_batch, learning_rate
                    )
                    epoch_unbinding_loss += unbinding_loss
            
            # Average losses
            avg_binding_loss = epoch_binding_loss / n_batches if train_binding else 0.0
            avg_unbinding_loss = epoch_unbinding_loss / n_batches if train_unbinding else 0.0
            avg_total_loss = avg_binding_loss + avg_unbinding_loss
            
            binding_losses.append(avg_binding_loss)
            unbinding_losses.append(avg_unbinding_loss)
            total_losses.append(avg_total_loss)
            
            # Progress reporting
            if (epoch + 1) % 10 == 0:
                print(f"Epoch {epoch+1}/{n_epochs} [{phase}]: "
                      f"Binding={avg_binding_loss:.6f}, "
                      f"Unbinding={avg_unbinding_loss:.6f}, "
                      f"Total={avg_total_loss:.6f}")
        
        # Disable training mode
        self._training_mode = False
        
        # Mark as trained
        self.is_trained = True
        
        print(f"✅ NumPy training complete!")
        print(f"🎯 Final Loss: Binding={binding_losses[-1]:.6f}, Unbinding={unbinding_losses[-1]:.6f}")
        
        return {
            'loss': total_losses[-1] if total_losses else 0.0,
            'binding_loss': binding_losses[-1] if binding_losses else 0.0,
            'unbinding_loss': unbinding_losses[-1] if unbinding_losses else 0.0,
            'epochs': n_epochs,
            'binding_accuracy': max(0.0, 1.0 - binding_losses[-1]) if binding_losses else 0.0,
            'unbinding_accuracy': max(0.0, 1.0 - unbinding_losses[-1]) if unbinding_losses else 0.0,
            'convergence': total_losses[-1] < 0.01 if total_losses else False,
            'parameters': self._count_parameters(),
            'training_history': {
                'binding_losses': binding_losses,
                'unbinding_losses': unbinding_losses,
                'total_losses': total_losses
            }
        }
    
    def _train_binding_batch(self, role_batch: np.ndarray, filler_batch: np.ndarray, 
                           target_batch: np.ndarray, learning_rate: float) -> float:
        """Train binding network on a batch using backpropagation"""
        # Concatenate inputs
        input_data = np.concatenate([role_batch, filler_batch], axis=1)
        
        # Forward pass
        output, activations = self._forward_pass(input_data, 'binding')
        
        # Compute loss (MSE)
        loss = np.mean((output - target_batch) ** 2)
        
        # Backward pass
        self._backward_pass(activations, target_batch, output, 'binding', learning_rate)
        
        return loss
    
    def _train_unbinding_batch(self, role_batch: np.ndarray, filler_batch: np.ndarray,
                             target_batch: np.ndarray, learning_rate: float) -> float:
        """Train unbinding network on a batch using backpropagation"""
        # Generate bound representations using current binding network
        role_filler_input = np.concatenate([role_batch, filler_batch], axis=1)
        bound_batch, _ = self._forward_pass(role_filler_input, 'binding')
        
        # Create unbinding input
        unbinding_input = np.concatenate([bound_batch, role_batch], axis=1)
        
        # Forward pass through unbinding network
        output, activations = self._forward_pass(unbinding_input, 'unbinding')
        
        # Compute loss (MSE with original filler)
        loss = np.mean((output - filler_batch) ** 2)
        
        # Backward pass
        self._backward_pass(activations, filler_batch, output, 'unbinding', learning_rate)
        
        return loss
    
    def _backward_pass(self, activations: List[np.ndarray], targets: np.ndarray,
                      outputs: np.ndarray, network: str, learning_rate: float):
        """
        🔄 Backpropagation Algorithm - Classical Implementation
        
        Implements classical backpropagation for weight updates using
        chain rule and gradient descent optimization.
        """
        if network == 'binding':
            weights, biases = self.binding_weights, self.binding_biases
        else:
            weights, biases = self.unbinding_weights, self.unbinding_biases
        
        batch_size = targets.shape[0]
        
        # Output layer error
        output_error = (outputs - targets) / batch_size
        
        # Backpropagate through layers
        layer_error = output_error
        
        for i in reversed(range(len(weights))):
            # Current layer activations
            current_activations = activations[i]
            next_activations = activations[i + 1]
            
            # Compute gradients
            weight_gradient = np.dot(current_activations.T, layer_error)
            bias_gradient = np.sum(layer_error, axis=0)
            
            # Update weights and biases
            weights[i] -= learning_rate * weight_gradient
            biases[i] -= learning_rate * bias_gradient
            
            # Propagate error to previous layer (if not input layer)
            if i > 0:
                # Linear error propagation
                layer_error = np.dot(layer_error, weights[i].T)
                
                # Apply activation derivative
                if i > 0:  # Not input layer
                    pre_activation = np.dot(activations[i-1], weights[i-1]) + biases[i-1]
                    activation_derivative = self._activation_derivative(pre_activation)
                    layer_error *= activation_derivative
    
    def predict(self, role_vectors: np.ndarray, filler_vectors: np.ndarray) -> np.ndarray:
        """
        🔮 NumPy Neural Prediction - Pure Python Binding!
        
        Uses trained NumPy networks for compositional representation
        learning with transparent, educational implementations.
        
        Args:
            role_vectors: Role vectors [batch_size, role_dim] or [role_dim]
            filler_vectors: Filler vectors [batch_size, filler_dim] or [filler_dim]
            
        Returns:
            np.ndarray: Predicted bound representations [batch_size, product_dim]
            
        🧮 **Educational Benefits**:
        ```python
        # Transparent neural binding process
        network = NumPyBindingNetwork(vector_dim=64)
        
        # Every operation is visible and debuggable
        bound_representation = network.predict(
            role_vector, filler_vector
        )
        ```
        
        📚 **Learning Advantages**:
        - Complete algorithmic transparency
        - No external dependencies
        - Classical neural network implementation
        - Research-accurate tensor product binding
        """
        if not self.is_trained:
            print("⚠️  Warning: NumPy network not trained. Using fallback binding.")
        
        return self.bind(role_vectors, filler_vectors)


# Utility functions for neural binding networks
def create_binding_training_data(n_samples: int = 1000, 
                               vector_dim: int = 64,
                               seed: int = 42) -> List[Tuple[np.ndarray, np.ndarray, np.ndarray]]:
    """
    🎲 Create Synthetic Training Data for Binding Networks
    
    Generates synthetic role-filler pairs and their tensor product bindings
    for training neural binding networks.
    
    Args:
        n_samples: Number of training samples to generate
        vector_dim: Dimensionality of vectors
        seed: Random seed for reproducibility
        
    Returns:
        List of (role_vector, filler_vector, target_binding) tuples
    """
    np.random.seed(seed)
    
    training_data = []
    
    for _ in range(n_samples):
        # Generate random role and filler vectors
        role = np.random.randn(vector_dim)
        filler = np.random.randn(vector_dim)
        
        # Create target binding (outer product)
        target_binding = np.outer(role, filler).flatten()
        
        training_data.append((role, filler, target_binding))
    
    return training_data


def evaluate_binding_quality(network: NeuralBindingNetwork,
                           test_data: List[Tuple[np.ndarray, np.ndarray, np.ndarray]]) -> Dict[str, float]:
    """
    📊 Evaluate Neural Binding Network Quality
    
    Comprehensive evaluation of binding and unbinding accuracy using
    multiple metrics including cosine similarity and MSE.
    
    Args:
        network: Trained neural binding network
        test_data: List of (role, filler, target) test tuples
        
    Returns:
        Dict containing evaluation metrics:
            - binding_mse: Mean squared error for binding
            - unbinding_mse: Mean squared error for unbinding
            - binding_cosine: Average cosine similarity for binding
            - unbinding_cosine: Average cosine similarity for unbinding
    """
    if not test_data:
        return {'binding_mse': 0.0, 'unbinding_mse': 0.0, 
               'binding_cosine': 0.0, 'unbinding_cosine': 0.0}
    
    binding_mses = []
    unbinding_mses = []
    binding_cosines = []
    unbinding_cosines = []
    
    for role, filler, target_binding in test_data:
        # Test binding
        predicted_binding = network.bind(role, filler)
        
        # Binding MSE
        binding_mse = np.mean((predicted_binding - target_binding) ** 2)
        binding_mses.append(binding_mse)
        
        # Binding cosine similarity
        norm_pred = np.linalg.norm(predicted_binding)
        norm_target = np.linalg.norm(target_binding)
        if norm_pred > 0 and norm_target > 0:
            cosine_sim = np.dot(predicted_binding, target_binding) / (norm_pred * norm_target)
            binding_cosines.append(cosine_sim)
        
        # Test unbinding
        recovered_filler = network.unbind(predicted_binding, role)
        
        # Unbinding MSE
        unbinding_mse = np.mean((recovered_filler - filler) ** 2)
        unbinding_mses.append(unbinding_mse)
        
        # Unbinding cosine similarity
        norm_recovered = np.linalg.norm(recovered_filler)
        norm_original = np.linalg.norm(filler)
        if norm_recovered > 0 and norm_original > 0:
            cosine_sim = np.dot(recovered_filler, filler) / (norm_recovered * norm_original)
            unbinding_cosines.append(cosine_sim)
    
    return {
        'binding_mse': np.mean(binding_mses),
        'unbinding_mse': np.mean(unbinding_mses),
        'binding_cosine': np.mean(binding_cosines) if binding_cosines else 0.0,
        'unbinding_cosine': np.mean(unbinding_cosines) if unbinding_cosines else 0.0,
        'n_samples': len(test_data)
    }


# Export NumPy implementation and utilities
__all__ = [
    'NumPyBindingNetwork',
    'create_binding_training_data',
    'evaluate_binding_quality'
]


if __name__ == "__main__":
    print("🧮 Neural Binding - NumPy Implementation Module")
    print("=" * 50)
    print("📊 MODULE CONTENTS:")
    print("  • NumPyBindingNetwork - Pure Python neural binding")
    print("  • Classical backpropagation implementation")
    print("  • Educational transparency and debugging")
    print("  • Utility functions for training data and evaluation")
    print("  • Research-accurate implementation of Smolensky (1990)")
    print("")
    print("✅ NumPy implementation module loaded successfully!")
    print("🧮 Classical neural networks with complete algorithmic transparency!")