"""
⚡ Core Tensor Product Binding Implementation
============================================

Main implementation of tensor product variable binding for structured 
knowledge representation in connectionist systems.

Based on: Smolensky (1990) "Tensor Product Variable Binding and the Representation of Symbolic Structures"

Key Features:
🧠 Neural-compatible structured representation
⚡ Tensor product operations for variable binding
🔄 Compositional structure encoding/decoding
📊 Distributed symbolic processing

ELI5 Explanation:
=================
Imagine you have a special kind of math that lets you "glue together" concepts
so that a computer can understand "John loves Mary" differently from "Mary loves John"
even though they use the same words. Tensor Product Binding is like a super-glue
that keeps track of WHO does WHAT to WHOM in a way that computers can understand!

Technical Details:
==================
Tensor Product Binding uses the mathematical operation:
    bind(role, filler) = role ⊗ filler

Where ⊗ is the tensor product (outer product for vectors).
This creates a distributed representation that:
- Preserves structural relationships
- Allows compositional operations
- Enables neural network implementation

ASCII Diagram:
==============
    Role Vector        Filler Vector      Bound Representation
    ┌─────────┐       ┌─────────┐        ┌─────────────────┐
    │ AGENT   │   ⊗   │  JOHN   │   →    │   JOHN-AS-AGENT │
    │ [1,0,0] │       │ [1,1,0] │        │  [1,1,0,0,0,0]  │
    └─────────┘       └─────────┘        └─────────────────┘

    Role Vector        Filler Vector      Bound Representation
    ┌─────────┐       ┌─────────┐        ┌─────────────────┐
    │ PATIENT │   ⊗   │  MARY   │   →    │  MARY-AS-PATIENT │
    │ [0,1,0] │       │ [0,1,1] │        │  [0,0,0,0,1,1]  │
    └─────────┘       └─────────┘        └─────────────────┘

Combined Structure:
    JOHN-AS-AGENT + MARY-AS-PATIENT = Complete relational structure

Author: Benedict Chen (benedict@benedictchen.com)
Research Foundation: Smolensky (1990) connectionist cognitive architecture
"""

import numpy as np
from typing import Union, List, Dict, Optional, Tuple, Any
from enum import Enum
import warnings
from dataclasses import dataclass


class BindingOperation(Enum):
    """
    🔗 Types of binding operations available in tensor product binding.
    
    Different mathematical approaches to combine role and filler vectors:
    - OUTER_PRODUCT: Standard tensor product (role ⊗ filler)
    - CIRCULAR_CONVOLUTION: Circular convolution binding (memory efficient) 
    - ADDITION: Simple vector addition (least structured)
    - MULTIPLICATION: Element-wise multiplication (component binding)
    """
    OUTER_PRODUCT = "outer_product"
    CIRCULAR_CONVOLUTION = "circular_convolution"  
    ADDITION = "addition"
    MULTIPLICATION = "multiplication"


@dataclass
class TPBVector:
    """
    🎯 Tensor Product Binding Vector
    
    Represents a vector in the TPB space with associated metadata.
    
    Attributes
    ----------
    data : np.ndarray
        The actual vector data
    role : str, optional
        Role name if this is a role vector
    filler : str, optional
        Filler name if this is a filler vector
    is_bound : bool
        Whether this represents a bound role-filler pair
    binding_info : dict
        Metadata about binding operations
    """
    data: np.ndarray
    role: Optional[str] = None
    filler: Optional[str] = None
    is_bound: bool = False
    binding_info: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.binding_info is None:
            self.binding_info = {}
    
    def __len__(self) -> int:
        return len(self.data)
    
    def __add__(self, other: 'TPBVector') -> 'TPBVector':
        """Add two TPB vectors (superposition)."""
        return TPBVector(
            data=self.data + other.data,
            is_bound=self.is_bound or other.is_bound,
            binding_info={'operation': 'superposition', 'components': [self, other]}
        )
    
    def normalize(self) -> 'TPBVector':
        """Normalize the vector."""
        norm = np.linalg.norm(self.data)
        if norm > 0:
            normalized_data = self.data / norm
        else:
            normalized_data = self.data.copy()
        
        return TPBVector(
            data=normalized_data,
            role=self.role,
            filler=self.filler,
            is_bound=self.is_bound,
            binding_info=self.binding_info.copy()
        )
    
    def similarity(self, other: 'TPBVector') -> float:
        """Compute cosine similarity with another TPB vector."""
        norm_self = np.linalg.norm(self.data)
        norm_other = np.linalg.norm(other.data)
        
        if norm_self == 0 or norm_other == 0:
            return 0.0
        
        return np.dot(self.data, other.data) / (norm_self * norm_other)


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
    """
    role: TPBVector
    filler: TPBVector
    bound_vector: TPBVector
    binding_operation: BindingOperation


class TensorProductBinding:
    """
    🧠 Main Tensor Product Binding System
    
    Implements Smolensky's tensor product variable binding framework for
    representing structured knowledge in neural networks.
    
    This system allows creation of distributed representations that preserve
    compositional structure while remaining compatible with neural processing.
    
    Parameters
    ----------
    role_dimension : int, default=64
        Dimensionality of role vectors (e.g., agent, patient, action).
        
    filler_dimension : int, default=64
        Dimensionality of filler vectors (e.g., john, mary, running).
        
    binding_type : str or BindingOperation, default='outer_product'
        Type of binding operation to use:
        - 'outer_product': Standard tensor product (creates role_dim × filler_dim)
        - 'circular_convolution': Circular convolution (preserves dimensionality)
        - 'addition': Simple addition (requires same dimensions)
        - 'multiplication': Element-wise multiplication
        
    normalize_vectors : bool, default=True
        Whether to normalize vectors before binding operations.
        
    random_seed : int, optional
        Random seed for reproducible vector generation.
        
    Attributes
    ----------
    role_vectors_ : Dict[str, TPBVector]
        Dictionary of role vectors created by the system.
        
    filler_vectors_ : Dict[str, TPBVector]
        Dictionary of filler vectors created by the system.
        
    bindings_ : List[BindingPair]
        List of all binding pairs created.
        
    Examples
    --------
    >>> # Basic tensor product binding
    >>> tpb = TensorProductBinding(role_dimension=64, filler_dimension=64)
    >>> 
    >>> # Create role and filler vectors
    >>> agent_role = tpb.create_role_vector("agent")
    >>> john_filler = tpb.create_filler_vector("john")
    >>> 
    >>> # Bind them together
    >>> john_as_agent = tpb.bind(agent_role, john_filler)
    >>> 
    >>> # Create a complete structure
    >>> patient_role = tpb.create_role_vector("patient")  
    >>> mary_filler = tpb.create_filler_vector("mary")
    >>> mary_as_patient = tpb.bind(patient_role, mary_filler)
    >>> 
    >>> # Compose: "john loves mary"
    >>> sentence = tpb.compose([john_as_agent, mary_as_patient])
    >>> 
    >>> # Query the structure
    >>> who_is_agent = tpb.unbind(sentence, agent_role)
    >>> similarity = tpb.similarity(who_is_agent, john_filler)
    >>> print(f"Agent similarity to John: {similarity:.3f}")
    
    Research Notes
    --------------
    This implementation follows Smolensky (1990):
    - Preserves the mathematical formulation of tensor product binding
    - Maintains biological plausibility for neural implementation
    - Supports compositional systematicity and productivity
    - Enables graceful degradation with partial information
    """
    
    def __init__(
        self,
        role_dimension: int = 64,
        filler_dimension: int = 64,
        binding_type: Union[str, BindingOperation] = BindingOperation.OUTER_PRODUCT,
        normalize_vectors: bool = True,
        random_seed: Optional[int] = None
    ):
        # Validate inputs
        if role_dimension <= 0 or filler_dimension <= 0:
            raise ValueError("Dimensions must be positive")
        
        if isinstance(binding_type, str):
            try:
                binding_type = BindingOperation(binding_type)
            except ValueError:
                raise ValueError(f"Unknown binding type: {binding_type}")
        
        # Store configuration
        self.role_dimension = role_dimension
        self.filler_dimension = filler_dimension
        self.binding_type = binding_type
        self.normalize_vectors = normalize_vectors
        self.random_seed = random_seed
        
        # Set random seed if provided
        if random_seed is not None:
            np.random.seed(random_seed)
        
        # Initialize storage
        self.role_vectors_ = {}
        self.filler_vectors_ = {}
        self.bindings_ = []
        
        # Compute bound vector dimension based on binding type
        if binding_type == BindingOperation.OUTER_PRODUCT:
            self.bound_dimension = role_dimension * filler_dimension
        else:
            # Other operations preserve dimensionality (assuming same input dimensions)
            if role_dimension != filler_dimension:
                warnings.warn(f"Role and filler dimensions differ ({role_dimension} vs {filler_dimension}). "
                            f"Some binding operations may not work as expected.")
            self.bound_dimension = max(role_dimension, filler_dimension)
        
        print(f"🧠 TensorProductBinding initialized: {role_dimension}D roles × {filler_dimension}D fillers "
              f"→ {self.bound_dimension}D bound vectors ({binding_type.value})")
    
    def create_role_vector(self, role_name: str, vector_data: Optional[np.ndarray] = None) -> TPBVector:
        """
        Create a role vector for binding operations.
        
        Parameters
        ----------
        role_name : str
            Name/identifier for the role (e.g., "agent", "patient", "action").
            
        vector_data : np.ndarray, optional
            Pre-specified vector data. If None, generates random vector.
            
        Returns
        -------
        role_vector : TPBVector
            The created role vector.
            
        Examples
        --------
        >>> tpb = TensorProductBinding()
        >>> agent = tpb.create_role_vector("agent")
        >>> patient = tpb.create_role_vector("patient")
        >>> action = tpb.create_role_vector("action")
        """
        if role_name in self.role_vectors_:
            return self.role_vectors_[role_name]
        
        # Generate or use provided vector data
        if vector_data is None:
            # Generate random role vector
            vector_data = np.random.randn(self.role_dimension)
        else:
            if len(vector_data) != self.role_dimension:
                raise ValueError(f"Vector data must have length {self.role_dimension}")
            vector_data = np.array(vector_data)
        
        # Normalize if requested
        if self.normalize_vectors:
            norm = np.linalg.norm(vector_data)
            if norm > 0:
                vector_data = vector_data / norm
        
        # Create TPB vector
        role_vector = TPBVector(
            data=vector_data,
            role=role_name,
            binding_info={'type': 'role', 'dimension': self.role_dimension}
        )
        
        # Store for reuse
        self.role_vectors_[role_name] = role_vector
        
        return role_vector
    
    def create_filler_vector(self, filler_name: str, vector_data: Optional[np.ndarray] = None) -> TPBVector:
        """
        Create a filler vector for binding operations.
        
        Parameters
        ----------
        filler_name : str
            Name/identifier for the filler (e.g., "john", "mary", "running").
            
        vector_data : np.ndarray, optional
            Pre-specified vector data. If None, generates random vector.
            
        Returns
        -------
        filler_vector : TPBVector
            The created filler vector.
        """
        if filler_name in self.filler_vectors_:
            return self.filler_vectors_[filler_name]
        
        # Generate or use provided vector data
        if vector_data is None:
            vector_data = np.random.randn(self.filler_dimension)
        else:
            if len(vector_data) != self.filler_dimension:
                raise ValueError(f"Vector data must have length {self.filler_dimension}")
            vector_data = np.array(vector_data)
        
        # Normalize if requested
        if self.normalize_vectors:
            norm = np.linalg.norm(vector_data)
            if norm > 0:
                vector_data = vector_data / norm
        
        # Create TPB vector
        filler_vector = TPBVector(
            data=vector_data,
            filler=filler_name,
            binding_info={'type': 'filler', 'dimension': self.filler_dimension}
        )
        
        # Store for reuse
        self.filler_vectors_[filler_name] = filler_vector
        
        return filler_vector
    
    def bind(
        self, 
        role: TPBVector, 
        filler: TPBVector,
        binding_operation: Optional[BindingOperation] = None
    ) -> TPBVector:
        """
        Bind a role vector with a filler vector.
        
        Parameters
        ----------
        role : TPBVector
            Role vector to bind.
            
        filler : TPBVector
            Filler vector to bind.
            
        binding_operation : BindingOperation, optional
            Override the default binding operation for this binding.
            
        Returns
        -------
        bound_vector : TPBVector
            Result of binding role and filler.
            
        Examples
        --------
        >>> tpb = TensorProductBinding()
        >>> agent = tpb.create_role_vector("agent")
        >>> john = tpb.create_filler_vector("john")
        >>> john_as_agent = tpb.bind(agent, john)
        """
        # Use provided operation or default
        operation = binding_operation or self.binding_type
        
        # Perform binding based on operation type
        if operation == BindingOperation.OUTER_PRODUCT:
            # Standard tensor product: role ⊗ filler
            bound_data = np.outer(role.data, filler.data).flatten()
            
        elif operation == BindingOperation.CIRCULAR_CONVOLUTION:
            # Circular convolution (requires same dimensions)
            if len(role.data) != len(filler.data):
                raise ValueError("Circular convolution requires same-dimension vectors")
            bound_data = np.fft.ifft(np.fft.fft(role.data) * np.fft.fft(filler.data)).real
            
        elif operation == BindingOperation.ADDITION:
            # Simple vector addition
            if len(role.data) != len(filler.data):
                raise ValueError("Addition requires same-dimension vectors")
            bound_data = role.data + filler.data
            
        elif operation == BindingOperation.MULTIPLICATION:
            # Element-wise multiplication
            if len(role.data) != len(filler.data):
                raise ValueError("Multiplication requires same-dimension vectors") 
            bound_data = role.data * filler.data
            
        else:
            raise ValueError(f"Unknown binding operation: {operation}")
        
        # Create bound vector
        bound_vector = TPBVector(
            data=bound_data,
            role=role.role,
            filler=filler.filler,
            is_bound=True,
            binding_info={
                'operation': operation.value,
                'role_name': role.role,
                'filler_name': filler.filler,
                'dimensions': f"{len(role.data)}×{len(filler.data)}→{len(bound_data)}"
            }
        )
        
        # Create and store binding pair
        binding_pair = BindingPair(
            role=role,
            filler=filler,
            bound_vector=bound_vector,
            binding_operation=operation
        )
        self.bindings_.append(binding_pair)
        
        return bound_vector
    
    def unbind(
        self, 
        bound_vector: TPBVector, 
        probe_vector: TPBVector,
        operation: Optional[BindingOperation] = None
    ) -> TPBVector:
        """
        Unbind a bound vector using a probe vector to retrieve the associated component.
        
        Parameters
        ----------
        bound_vector : TPBVector
            The bound vector to unbind.
            
        probe_vector : TPBVector
            Probe vector (either role or filler) to retrieve its binding partner.
            
        operation : BindingOperation, optional
            Binding operation to use for unbinding. If None, uses default.
            
        Returns
        -------
        unbound_vector : TPBVector
            The retrieved component (approximate).
            
        Examples
        --------
        >>> # After binding john as agent
        >>> john_as_agent = tpb.bind(agent_role, john_filler)
        >>> # Unbind with agent role to get john back
        >>> retrieved_filler = tpb.unbind(john_as_agent, agent_role)
        >>> similarity = tpb.similarity(retrieved_filler, john_filler)
        """
        operation = operation or self.binding_type
        
        if operation == BindingOperation.OUTER_PRODUCT:
            # For tensor product, unbinding involves matrix operations
            # This is a simplified approximation
            if probe_vector.role is not None:
                # Probing with role, want to retrieve filler
                # Reshape bound vector back to matrix form
                bound_matrix = bound_vector.data.reshape(self.role_dimension, self.filler_dimension)
                # Project onto probe role
                unbound_data = bound_matrix.T @ probe_vector.data
            else:
                # Probing with filler, want to retrieve role
                bound_matrix = bound_vector.data.reshape(self.role_dimension, self.filler_dimension)
                unbound_data = bound_matrix @ probe_vector.data
                
        elif operation == BindingOperation.CIRCULAR_CONVOLUTION:
            # For circular convolution, unbinding uses approximate inverse
            probe_inverse = np.fft.ifft(1.0 / (np.fft.fft(probe_vector.data) + 1e-10)).real
            unbound_data = np.fft.ifft(np.fft.fft(bound_vector.data) * np.fft.fft(probe_inverse)).real
            
        elif operation in [BindingOperation.ADDITION, BindingOperation.MULTIPLICATION]:
            # For addition/multiplication, unbinding is approximate
            if operation == BindingOperation.ADDITION:
                unbound_data = bound_vector.data - probe_vector.data
            else:  # multiplication
                # Avoid division by zero
                safe_probe = probe_vector.data + 1e-10 * np.sign(probe_vector.data)
                unbound_data = bound_vector.data / safe_probe
                
        else:
            raise ValueError(f"Unknown binding operation: {operation}")
        
        # Create unbound vector
        unbound_vector = TPBVector(
            data=unbound_data,
            binding_info={
                'operation': 'unbind',
                'probe': probe_vector.role or probe_vector.filler,
                'original_operation': operation.value
            }
        )
        
        return unbound_vector
    
    def compose(self, bound_vectors: List[TPBVector]) -> TPBVector:
        """
        Compose multiple bound vectors into a single composite structure.
        
        This implements superposition - adding multiple bound vectors together
        to create a composite representation.
        
        Parameters
        ----------
        bound_vectors : List[TPBVector]
            List of bound vectors to compose.
            
        Returns
        -------
        composite : TPBVector
            Composite structure representing all bound vectors.
            
        Examples
        --------
        >>> # Create "john loves mary"
        >>> john_as_agent = tpb.bind(agent_role, john_filler)
        >>> mary_as_patient = tpb.bind(patient_role, mary_filler)
        >>> loves_as_action = tpb.bind(action_role, loves_filler)
        >>> sentence = tpb.compose([john_as_agent, mary_as_patient, loves_as_action])
        """
        if not bound_vectors:
            raise ValueError("Need at least one bound vector to compose")
        
        # Start with first vector
        composite_data = bound_vectors[0].data.copy()
        
        # Add remaining vectors (superposition)
        for bound_vec in bound_vectors[1:]:
            if len(bound_vec.data) != len(composite_data):
                raise ValueError(f"All vectors must have same dimension for composition")
            composite_data += bound_vec.data
        
        # Create composite vector
        composite = TPBVector(
            data=composite_data,
            is_bound=True,
            binding_info={
                'operation': 'composition',
                'n_components': len(bound_vectors),
                'components': [vec.binding_info.get('role_name', 'unknown') + '-' + 
                             vec.binding_info.get('filler_name', 'unknown') 
                             for vec in bound_vectors]
            }
        )
        
        return composite
    
    def similarity(self, vector1: TPBVector, vector2: TPBVector) -> float:
        """
        Compute cosine similarity between two TPB vectors.
        
        Parameters
        ----------
        vector1, vector2 : TPBVector
            Vectors to compare.
            
        Returns
        -------
        similarity : float
            Cosine similarity [-1, 1].
        """
        return vector1.similarity(vector2)
    
    def get_role_vector(self, role_name: str) -> Optional[TPBVector]:
        """Get a previously created role vector by name."""
        return self.role_vectors_.get(role_name)
    
    def get_filler_vector(self, filler_name: str) -> Optional[TPBVector]:
        """Get a previously created filler vector by name."""
        return self.filler_vectors_.get(filler_name)
    
    def list_roles(self) -> List[str]:
        """List all created role vector names."""
        return list(self.role_vectors_.keys())
    
    def list_fillers(self) -> List[str]:
        """List all created filler vector names.""" 
        return list(self.filler_vectors_.keys())
    
    def get_binding_history(self) -> List[Dict[str, Any]]:
        """
        Get history of all binding operations performed.
        
        Returns
        -------
        history : List[Dict[str, Any]]
            List of binding operation records.
        """
        history = []
        for binding in self.bindings_:
            record = {
                'role': binding.role.role,
                'filler': binding.filler.filler,
                'operation': binding.binding_operation.value,
                'bound_dimension': len(binding.bound_vector.data),
                'similarity_to_role': binding.bound_vector.similarity(binding.role),
                'similarity_to_filler': binding.bound_vector.similarity(binding.filler)
            }
            history.append(record)
        return history
    
    def cleanup_memory(self):
        """Clear stored vectors and binding history to free memory."""
        self.role_vectors_.clear()
        self.filler_vectors_.clear()
        self.bindings_.clear()
        print("🧹 Memory cleaned up - all vectors and bindings cleared")
    
    def __repr__(self) -> str:
        """String representation of the TensorProductBinding system."""
        return (f"TensorProductBinding(roles={self.role_dimension}D, "
                f"fillers={self.filler_dimension}D, "
                f"binding={self.binding_type.value}, "
                f"n_roles={len(self.role_vectors_)}, "
                f"n_fillers={len(self.filler_vectors_)}, "
                f"n_bindings={len(self.bindings_)})")


# Convenience functions for quick usage
def create_tpb_system(
    role_dim: int = 64,
    filler_dim: int = 64,
    binding_type: str = "outer_product"
) -> TensorProductBinding:
    """
    🚀 Quick creation of a TensorProductBinding system.
    
    Parameters
    ----------
    role_dim : int
        Role vector dimension
    filler_dim : int  
        Filler vector dimension
    binding_type : str
        Type of binding operation
        
    Returns
    -------
    tpb : TensorProductBinding
        Configured TPB system
        
    Example
    -------
    >>> tpb = create_tpb_system(role_dim=32, filler_dim=32, binding_type="circular_convolution")
    """
    return TensorProductBinding(
        role_dimension=role_dim,
        filler_dimension=filler_dim,
        binding_type=binding_type
    )


def demo_tensor_binding():
    """
    🎯 Demonstration of basic tensor product binding operations.
    
    Shows how to create roles, fillers, bind them, and query structures.
    """
    print("🎯 Tensor Product Binding Demo")
    print("=" * 40)
    
    # Create TPB system
    tpb = TensorProductBinding(role_dimension=8, filler_dimension=8)
    
    # Create vectors
    print("\n1. Creating role and filler vectors...")
    agent = tpb.create_role_vector("agent")
    patient = tpb.create_role_vector("patient")
    john = tpb.create_filler_vector("john")
    mary = tpb.create_filler_vector("mary")
    
    print(f"   Agent role: {agent.data[:4]}... (dim={len(agent.data)})")
    print(f"   John filler: {john.data[:4]}... (dim={len(john.data)})")
    
    # Bind vectors
    print("\n2. Binding role-filler pairs...")
    john_as_agent = tpb.bind(agent, john)
    mary_as_patient = tpb.bind(patient, mary)
    
    print(f"   John-as-agent: {john_as_agent.data[:4]}... (dim={len(john_as_agent.data)})")
    
    # Compose structure
    print("\n3. Composing complete structure...")
    sentence = tpb.compose([john_as_agent, mary_as_patient])
    
    print(f"   Complete sentence: {sentence.data[:4]}... (dim={len(sentence.data)})")
    
    # Query structure
    print("\n4. Querying the structure...")
    who_is_agent = tpb.unbind(sentence, agent)
    similarity_to_john = tpb.similarity(who_is_agent, john)
    
    print(f"   Agent query similarity to John: {similarity_to_john:.3f}")
    
    who_is_patient = tpb.unbind(sentence, patient)
    similarity_to_mary = tpb.similarity(who_is_patient, mary)
    
    print(f"   Patient query similarity to Mary: {similarity_to_mary:.3f}")
    
    # Show binding history
    print("\n5. Binding history:")
    history = tpb.get_binding_history()
    for i, record in enumerate(history):
        print(f"   {i+1}. {record['role']} ⊗ {record['filler']} "
              f"(op: {record['operation']}, dim: {record['bound_dimension']})")
    
    print("\n✅ Demo complete! Tensor product binding successfully demonstrated.")
    return tpb


if __name__ == "__main__":
    # Run demo if script is executed directly
    demo_tensor_binding()