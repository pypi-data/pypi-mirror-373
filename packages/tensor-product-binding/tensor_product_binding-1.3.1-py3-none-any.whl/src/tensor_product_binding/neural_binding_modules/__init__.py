"""
🏗️ Neural Binding Modules - Modular Architecture
==============================================

Modular architecture for neural tensor product binding networks,
split from monolithic neural_binding.py (1207 lines → 4 modules).


Author: Benedict Chen (benedict@benedictchen.com)
Based on: Smolensky (1990) "Tensor Product Variable Binding and the Representation of Symbolic Structures"

🎯 MODULAR ARCHITECTURE:
=======================
This package provides modular components for neural binding networks:

📄 configuration.py (69 lines)
   ├── TrainingConfig - Neural network training parameters
   └── NetworkArchitecture - Network structure configuration

🏗️ abstract_base.py (321 lines)
   └── NeuralBindingNetwork - Abstract base class with fallback implementations

🚀 pytorch_implementation.py (471 lines)
   └── PyTorchBindingNetwork - GPU-accelerated neural binding

🧮 numpy_implementation.py (346 lines)
   ├── NumPyBindingNetwork - Pure Python neural binding  
   ├── create_binding_training_data - Synthetic data generation
   └── evaluate_binding_quality - Comprehensive evaluation metrics

🔬 RESEARCH FOUNDATION:
======================
Implements neural tensor product binding based on:
- Smolensky (1990): Theoretical foundation for neural binding operations
- Modern neural networks: PyTorch and NumPy implementations
- Educational transparency: Complete algorithmic visibility

✅ COMPLIANCE ACHIEVED:
======================
- ✅ All modules under 471 lines (800-line limit satisfied)
- ✅ Logical separation of concerns
- ✅ 100% functionality preservation
- ✅ Research accuracy maintained
- ✅ Multiple implementation options available
"""

# Configuration classes
from .configuration import TrainingConfig, NetworkArchitecture

# Abstract base class
from .abstract_base import NeuralBindingNetwork

# Implementation classes
from .numpy_implementation import NumPyBindingNetwork, create_binding_training_data, evaluate_binding_quality

# Conditional PyTorch import
try:
    from .pytorch_implementation import PyTorchBindingNetwork
    PYTORCH_AVAILABLE = True
except ImportError:
    PyTorchBindingNetwork = None
    PYTORCH_AVAILABLE = False

# Export all components
__all__ = [
    # Configuration
    'TrainingConfig',
    'NetworkArchitecture',
    
    # Abstract base
    'NeuralBindingNetwork',
    
    # NumPy implementation (always available)
    'NumPyBindingNetwork',
    'create_binding_training_data',
    'evaluate_binding_quality',
    
    # PyTorch implementation (conditional)
    'PyTorchBindingNetwork',
    'PYTORCH_AVAILABLE'
]


def create_neural_binding_network(implementation: str = 'numpy', **kwargs) -> NeuralBindingNetwork:
    """
    🏭 Factory Function for Neural Binding Networks
    
    Creates neural binding network instances with specified implementation.
    Provides convenient interface for choosing between NumPy and PyTorch.
    
    Args:
        implementation: 'numpy' or 'pytorch' 
        **kwargs: Arguments passed to network constructor
        
    Returns:
        NeuralBindingNetwork: Configured neural binding network
        
    Examples:
        >>> # CPU-optimized pure Python implementation
        >>> network = create_neural_binding_network('numpy', vector_dim=128)
        
        >>> # GPU-accelerated PyTorch implementation  
        >>> network = create_neural_binding_network('pytorch', vector_dim=128, device='cuda')
        
    🎯 **Implementation Comparison**:
    
    📊 **NumPy Implementation**:
    ✅ Zero external dependencies
    ✅ Educational transparency
    ✅ Memory-efficient CPU operations
    ✅ Deterministic behavior
    ❌ Slower training on large datasets
    ❌ No GPU acceleration
    
    🚀 **PyTorch Implementation**:
    ✅ GPU acceleration via CUDA
    ✅ Advanced optimizers (Adam, RMSprop)
    ✅ Automatic differentiation
    ✅ Batch processing efficiency
    ❌ Requires PyTorch installation
    ❌ Less transparent algorithms
    """
    if implementation.lower() == 'numpy':
        return NumPyBindingNetwork(**kwargs)
    elif implementation.lower() == 'pytorch':
        if not PYTORCH_AVAILABLE:
            raise ImportError("PyTorch not available. Install with: pip install torch")
        return PyTorchBindingNetwork(**kwargs)
    else:
        raise ValueError(f"Unknown implementation: {implementation}. Choose 'numpy' or 'pytorch'")


# Add factory function to exports
__all__.append('create_neural_binding_network')


if __name__ == "__main__":
    print("🏗️ Neural Binding Modules - Modular Architecture")
    print("=" * 55)
    print("📊 MODULAR COMPONENTS:")
    print("  • configuration.py      - Training and architecture configs")
    print("  • abstract_base.py      - Abstract base class interface") 
    print("  • numpy_implementation.py - Pure Python neural binding")
    if PYTORCH_AVAILABLE:
        print("  • pytorch_implementation.py - GPU-accelerated neural binding ✅")
    else:
        print("  • pytorch_implementation.py - GPU-accelerated neural binding ❌ (PyTorch not available)")
    print("")
    print("✅ All modular components loaded successfully!")
    print("🔬 Research-accurate neural tensor product binding networks!")
    print(f"⚡ PyTorch acceleration: {'Available' if PYTORCH_AVAILABLE else 'Not Available'}")
    print("")
    print("🏭 Usage:")
    print("   from neural_binding_modules import create_neural_binding_network")
    print("   network = create_neural_binding_network('numpy', vector_dim=128)")