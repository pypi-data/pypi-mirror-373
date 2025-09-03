"""
🎯 Tensor Product Binding - Vector Representation Classes
========================================================

Author: Benedict Chen (benedict@benedictchen.com)

💰 Donations: Help support this research!
   PayPal: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS
   💖 Please consider recurring donations to support continued TPB research

Based on: Smolensky (1990) "Tensor Product Variable Binding and the Representation of Symbolic Structures"

🔬 Research Foundation:
======================
Vector representations implementing Smolensky's (1990) framework:
- TPBVector: Distributed representation of roles, fillers, and compositions
- BindingPair: Role-filler relationship with binding metadata  
- Mathematical operations: Tensor products, unbinding, similarity metrics
- Systematic composition: Supports recursive and hierarchical structures

ELI5 Explanation:
================
Think of TPBVectors like special containers that hold information! 📦

🎭 **Role Vectors** (like job descriptions):
- "AGENT" vector represents "who does the action"
- "PATIENT" vector represents "who receives the action"  
- "COLOR" vector represents "what color something is"

👤 **Filler Vectors** (like the actual people/things):
- "JOHN" vector represents the specific person John
- "RED" vector represents the specific color red
- "CAR" vector represents the specific object car

💝 **Bound Vectors** (like gift boxes with labels):
When you bind "JOHN" to "AGENT" role, you create a bound vector that means
"John-in-the-agent-role" - like putting John's name tag in the "driver" slot!

ASCII Vector Operations:
========================
    BINDING OPERATION (⊗ = tensor product):
    
    Role Vector     Filler Vector      Bound Vector
    ┌─────────────┐  ┌─────────────┐   ┌─────────────────┐
    │   AGENT     │  │    JOHN     │   │   JOHN-AS-AGENT │
    │ [1,0,0,...] │⊗ │ [0,1,1,...] │ = │ [0,1,1,0,0,...] │
    └─────────────┘  └─────────────┘   └─────────────────┘
          
    COMPOSITION (+ = vector addition):
    
    John-as-Agent   Mary-as-Patient     Complete Sentence
    ┌─────────────┐ ┌─────────────────┐ ┌─────────────────┐
    │ Role₁⊗Fill₁ │ │  Role₂⊗Fill₂   │ │   Compositional │
    │     +       │ │       +         │=│   Representation│
    │ Love-Action │ │   Past-Tense    │ │ "John loved Mary"│
    └─────────────┘ └─────────────────┘ └─────────────────┘

    UNBINDING OPERATION (approximate inverse):
    
    Bound Vector     Role Vector       Recovered Filler
    ┌─────────────┐  ┌─────────────┐   ┌─────────────┐
    │JOHN-AS-AGENT│  │   AGENT     │   │ ≈ JOHN      │
    │ [0,1,1,0,0] │⊘ │ [1,0,0,0,0] │ ≈ │ [0,1,1,0,0] │
    └─────────────┘  └─────────────┘   └─────────────┘

⚡ Vector Properties:
====================
1. **Distributivity**: Information spread across entire vector
2. **Compositionality**: Complex structures from simple bindings  
3. **Similarity Preservation**: Similar concepts have similar vectors
4. **Unbinding Capability**: Can recover original components (approximately)

📊 Data Structure Architecture:
==============================
```python
@dataclass
class TPBVector:
    vector: np.ndarray      # The actual numerical representation
    label: str              # Human-readable identifier  
    vector_type: str        # 'role', 'filler', or 'bound'
    metadata: Dict          # Additional binding information
    
@dataclass  
class BindingPair:
    role: TPBVector         # What role this represents
    filler: TPBVector       # What fills that role
    bound: TPBVector        # The tensor product result
    binding_strength: float # Confidence/clarity of binding
```

This module provides the fundamental data structures for representing
and manipulating distributed symbolic knowledge using tensor products.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
import numpy as np
from .tpb_enums import BindingOperation


@dataclass
class TPBVector:
    """
    🎯 Tensor Product Binding Vector
    
    Represents vectors in the tensor product binding space with metadata
    about their role (variable vs value) and binding state.
    
    Attributes
    ----------
    data : np.ndarray
        The actual vector data as numpy array
    role : Optional[str]
        Role name if this is a role vector (e.g., "agent", "location")
    filler : Optional[str]  
        Filler name if this is a filler vector (e.g., "john", "kitchen")
    is_bound : bool
        Whether this vector represents a bound role-filler pair
    binding_info : Optional[Dict[str, Any]]
        Metadata about how this vector was created (for bound vectors)
        
    Examples
    --------
    >>> # Create a role vector
    >>> agent_role = TPBVector(
    ...     data=np.random.randn(64),
    ...     role="agent", 
    ...     filler=None,
    ...     is_bound=False
    ... )
    >>> 
    >>> # Create a filler vector
    >>> john_filler = TPBVector(
    ...     data=np.random.randn(64),
    ...     role=None,
    ...     filler="john", 
    ...     is_bound=False
    ... )
    """
    data: np.ndarray
    role: Optional[str] = None
    filler: Optional[str] = None  
    is_bound: bool = False
    binding_info: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate vector after initialization."""
        if not isinstance(self.data, np.ndarray):
            raise TypeError("Vector data must be a numpy array")
        if len(self.data.shape) != 1:
            raise ValueError("Vector data must be 1-dimensional")
        if len(self.data) == 0:
            raise ValueError("Vector data cannot be empty")
    
    def copy(self) -> 'TPBVector':
        """Create a deep copy of this vector."""
        return TPBVector(
            data=self.data.copy(),
            role=self.role,
            filler=self.filler,
            is_bound=self.is_bound,
            binding_info=self.binding_info.copy() if self.binding_info else None
        )
    
    @property
    def dimension(self) -> int:
        """Get vector dimension."""
        return len(self.data) if self.data.ndim == 1 else self.data.size
    
    @property
    def norm(self) -> float:
        """Get vector norm (magnitude)."""
        return np.linalg.norm(self.data)
    
    def normalize(self) -> 'TPBVector':
        """Return a normalized version of this vector."""
        norm = self.norm
        if norm == 0:
            return self.copy()
        
        normalized_data = self.data / norm
        result = self.copy()
        result.data = normalized_data
        return result
    
    def similarity(self, other: 'TPBVector') -> float:
        """
        Compute cosine similarity with another vector.
        
        Parameters
        ----------
        other : TPBVector
            The other vector to compare with
            
        Returns
        -------
        float
            Cosine similarity between -1 and 1
        """
        if not isinstance(other, TPBVector):
            raise TypeError("Can only compute similarity with other TPBVector")
        
        norm_self = self.norm
        norm_other = other.norm
        
        if norm_self == 0 or norm_other == 0:
            return 0.0
        
        return np.dot(self.data, other.data) / (norm_self * norm_other)
    
    def __repr__(self) -> str:
        """String representation of the vector."""
        vector_type = []
        if self.role:
            vector_type.append(f"role='{self.role}'")
        if self.filler:
            vector_type.append(f"filler='{self.filler}'")
        if self.is_bound:
            vector_type.append("bound=True")
        
        type_str = ", ".join(vector_type) if vector_type else "untyped"
        return f"TPBVector(dim={len(self.data)}, {type_str})"


@dataclass
class BindingPair:
    """
    👫 Role-Filler Binding Pair
    
    Represents a bound role-filler relationship in tensor product binding.
    
    Attributes
    ----------
    role : TPBVector
        The role vector (e.g., "agent", "patient", "location")
    filler : TPBVector  
        The filler vector (e.g., "john", "mary", "kitchen")
    bound_vector : TPBVector
        The result of binding role and filler
    binding_operation : BindingOperation
        The operation used to create the binding
        
    Examples
    --------
    >>> agent = TPBVector(np.random.randn(64), role="agent")
    >>> john = TPBVector(np.random.randn(64), filler="john")  
    >>> bound = TPBVector(np.random.randn(4096), is_bound=True)
    >>> 
    >>> pair = BindingPair(
    ...     role=agent,
    ...     filler=john, 
    ...     bound_vector=bound,
    ...     binding_operation=BindingOperation.OUTER_PRODUCT
    ... )
    """
    role: TPBVector
    filler: TPBVector
    bound_vector: TPBVector
    binding_operation: BindingOperation
    
    def __post_init__(self):
        """Validate binding pair after initialization."""
        if not isinstance(self.role, TPBVector):
            raise TypeError("Role must be a TPBVector")
        if not isinstance(self.filler, TPBVector):
            raise TypeError("Filler must be a TPBVector")  
        if not isinstance(self.bound_vector, TPBVector):
            raise TypeError("Bound vector must be a TPBVector")
        if not isinstance(self.binding_operation, BindingOperation):
            raise TypeError("Binding operation must be a BindingOperation enum")
            
        # Semantic validation
        if self.role.role is None:
            import warnings
            warnings.warn("Role vector should have a role name")
        if self.filler.filler is None:
            import warnings
            warnings.warn("Filler vector should have a filler name")
        if not self.bound_vector.is_bound:
            import warnings
            warnings.warn("Bound vector should be marked as bound")
    
    def __repr__(self) -> str:
        """String representation of the binding pair."""
        role_name = self.role.role or "unnamed_role"
        filler_name = self.filler.filler or "unnamed_filler" 
        return f"BindingPair({role_name} × {filler_name} → {self.binding_operation.value})"


# Export the vector classes
__all__ = [
    'TPBVector',
    'BindingPair'
]


if __name__ == "__main__":
    print("🎯 Tensor Product Binding - Vector Classes Module")
    print("=" * 55)
    print("📊 MODULE CONTENTS:")
    print("  • TPBVector - Core vector representation with metadata")
    print("  • BindingPair - Bound role-filler relationship representation") 
    print("  • Research-accurate vector classes for tensor product binding")
    print("")
    print("✅ Vector classes module loaded successfully!")
    print("🔬 Essential data structures for Smolensky (1990) TPB framework!")