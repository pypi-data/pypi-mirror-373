"""
🏗️ Tensor Product Binding Modules - Distributed Symbolic Architecture
=====================================================================

Author: Benedict Chen (benedict@benedictchen.com)

💰 Donations: Help support this research!
   PayPal: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS
   💖 Please consider recurring donations to support continued TPB research

Based on: Smolensky (1990) "Tensor Product Variable Binding and the Representation of Symbolic Structures"

🔬 Research Foundation:
======================
Modular implementation of foundational distributed representation research:
- Smolensky (1990): Original tensor product variable binding theory
- Plate (1995): Holographic Reduced Representations (HRR)
- Kanerva (2009): Hyperdimensional computing and vector symbolic architectures
- Modern VSA: Contemporary applications in neural-symbolic AI

ELI5 Explanation:
================
Think of this module system like a well-organized toolshed for building with concepts! 🔧

🏠 **The Toolshed Organization**:
Instead of having one giant messy toolbox, we organized everything into labeled drawers:
- **Drawer 1 (tpb_core)**: The main power tools (binding operations)
- **Drawer 2 (tpb_vector)**: The basic materials (vector representations)  
- **Drawer 3 (tpb_enums)**: The instruction labels (operation types)
- **Drawer 4 (tpb_factory)**: The project templates (pre-made configurations)

🧠 **Why This Matters for AI**:
Just like organizing tools makes building easier, organizing our TPB code makes
it easier to build AI systems that can understand complex relationships like:
- "John loves Mary" vs "Mary loves John" (different roles, same concepts)
- "The red car drives fast" (binding properties to objects)
- Nested relationships like "John believes Mary loves Tom"

ASCII Module Architecture:
==========================
    User Application          TPB Module System
    ┌─────────────────┐       ┌─────────────────────┐
    │ "I want to      │       │ tpb_core.py         │
    │  represent      │ ───▶  │ ┌─────────────────┐ │
    │  'John loves    │       │ │ TensorProduct   │ │
    │   Mary'"        │       │ │ Binding         │ │
    └─────────────────┘       │ │ - bind()        │ │
             │                │ │ - unbind()      │ │
             │                │ │ - compose()     │ │
             ▼                │ └─────────────────┘ │
    ┌─────────────────┐       └─────────────────────┘
    │ Choose binding  │                │
    │ operation type  │       ┌─────────────────────┐
    └─────────────────┘ ───▶  │ tpb_enums.py        │
             │                │ ┌─────────────────┐ │
             │                │ │ BindingOperation│ │
             ▼                │ │ - OUTER_PRODUCT │ │
    ┌─────────────────┐       │ │ - CIRCULAR_CONV │ │
    │ Create vectors  │       │ │ - ADDITION      │ │
    │ for roles &     │ ───▶  │ │ - MULTIPLICATION│ │
    │ fillers         │       │ └─────────────────┘ │
    └─────────────────┘       └─────────────────────┘
             │                         │
             ▼                         ▼
    ┌─────────────────┐       ┌─────────────────────┐
    │ Get final       │       │ tpb_vector.py       │
    │ bound           │ ◀───  │ ┌─────────────────┐ │
    │ representation  │       │ │ TPBVector       │ │
    └─────────────────┘       │ │ BindingPair     │ │
                              │ │ - vector data   │ │
                              │ │ - metadata      │ │
                              │ └─────────────────┘ │
                              └─────────────────────┘

⚡ Module Organization:
======================
1. **tpb_core.py**: Main TensorProductBinding class and core operations
2. **tpb_vector.py**: Vector data structures (TPBVector, BindingPair)
3. **tpb_enums.py**: Operation type definitions and mathematical options
4. **tpb_factory.py**: Convenience functions and educational demonstrations

📊 Architectural Benefits:
=========================
• **Separation of Concerns**: Each module handles one aspect of TPB
• **Maintainability**: Easy to update one component without affecting others
• **Testability**: Individual modules can be tested in isolation
• **Extensibility**: New binding operations can be added to enums easily
• **Educational Value**: Clear structure helps understand TPB theory

This modular architecture transforms Smolensky's complex mathematical theory
into practical, understandable tools for distributed symbolic AI systems.
"""

# Legacy imports (existing modules)
from .config_enums import (
    BindingOperation,
    BindingMethod, 
    UnbindingMethod,
    TensorBindingConfig,
    BindingPair
)

from .vector_operations import TPBVector

from .core_binding import CoreBinding

try:
    # New modular tensor_product_binding.py components  
    from .tpb_enums import BindingOperation as ModularBindingOperation
    from .tpb_vector import TPBVector as ModularTPBVector, BindingPair as ModularBindingPair
    from .tpb_core import TensorProductBinding
    from .tpb_factory import create_tpb_system, demo_tensor_binding, create_linguistic_example
    
    # Use modular components as primary
    MODULAR_AVAILABLE = True
    
except ImportError:
    MODULAR_AVAILABLE = False
    TensorProductBinding = None
    create_tpb_system = None
    demo_tensor_binding = None
    create_linguistic_example = None


# Export legacy and new components
__all__ = [
    # Legacy components
    'BindingOperation',
    'BindingMethod',
    'UnbindingMethod', 
    'TensorBindingConfig',
    'BindingPair',
    'TPBVector',
    'CoreBinding',
]

# Add modular components if available
if MODULAR_AVAILABLE:
    __all__.extend([
        'TensorProductBinding',      # Main system
        'create_tpb_system',         # Factory function
        'demo_tensor_binding',       # Educational demo
        'create_linguistic_example', # NLP example
        'MODULAR_AVAILABLE'          # Availability flag
    ])


# Convenience factory function
def create_tpb(vector_dim: int = 100, **kwargs):
    """
    🏭 Quick TPB system creation.
    
    Uses modular TensorProductBinding if available, falls back to legacy.
    
    Parameters
    ----------
    vector_dim : int, default=100
        Dimension of vectors
    **kwargs
        Additional parameters
        
    Returns
    -------
    TensorProductBinding or CoreBinding
        TPB system instance
    """
    if MODULAR_AVAILABLE and create_tpb_system:
        return create_tpb_system(vector_dim=vector_dim, **kwargs)
    else:
        # Fallback to legacy
        return CoreBinding(**kwargs)


# Add convenience function to exports
__all__.append('create_tpb')