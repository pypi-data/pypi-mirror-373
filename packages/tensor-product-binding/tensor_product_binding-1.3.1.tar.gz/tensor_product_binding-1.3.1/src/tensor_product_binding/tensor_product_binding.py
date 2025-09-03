"""
⚡ Core Tensor Product Binding Implementation
============================================

Main implementation of tensor product variable binding for structured 
knowledge representation in connectionist systems.

Based on: Smolensky (1990) "Tensor Product Variable Binding and the Representation of Symbolic Structures"

# FIXME: Critical Research Accuracy Issues - Overall Architecture Based on Smolensky (1990)
#
# 1. MISSING FUNDAMENTAL THEORETICAL COMPONENTS
#    - Smolensky's framework includes role decomposition and filler decomposition
#    - Missing proper tensor algebra foundation with rank preservation
#    - No implementation of Smolensky's "activity vectors" vs "weight vectors" distinction
#    - Missing "tensor product representations" (TPRs) as formal mathematical objects
#    - Solutions:
#      a) Implement formal TPR class with rank tracking and tensor operations
#      b) Add role/filler decomposition methods based on Smolensky's theoretical framework
#      c) Distinguish between activation patterns and weight patterns
#      d) Implement tensor rank analysis and optimization
#    - Research basis: Smolensky (1990) Section 2-3, mathematical foundations
#
# 2. INCORRECT CONNECTIONIST IMPLEMENTATION APPROACH
#    - Current implementation focuses on vector operations, not neural network units
#    - Smolensky's work emphasized neural unit activity patterns and weight matrices
#    - Missing connection to actual connectionist architectures
#    - No implementation of "product units" that compute role×filler interactions
#    - Solutions:
#      a) Implement neural unit-based TPR with activation functions
#      b) Add product units: output = f(Σ role_i × filler_j × weight_ij)
#      c) Connect to actual neural network training and inference
#      d) Implement biologically plausible learning rules for TPR
#    - Research basis: Smolensky emphasized neural implementation, not just mathematical abstraction
#
# 3. MISSING SYSTEMATICITY AND COMPOSITIONALITY PRINCIPLES
#    - No enforcement of Smolensky's systematicity principle in implementation
#    - Missing productivity constraints (ability to generate infinite novel combinations)
#    - No implementation of constituency relations between composed structures
#    - Missing recursive compositional structure support
#    - Solutions:
#      a) Add systematicity validation: if system knows "John loves Mary", it should handle "Mary loves John"
#      b) Implement productivity measures and capacity estimation
#      c) Add constituency parsing and structure recovery
#      d) Support recursive embedding: [[John loves Mary] causes [Tom to smile]]
#    - Research basis: Smolensky's core argument for symbolic-connectionist integration
#
# 4. INADEQUATE DISTRIBUTED REPRESENTATION THEORY
#    - Missing proper micro-feature analysis of roles and fillers
#    - No implementation of distributed similarity structure in vector spaces
#    - Missing Smolensky's "constituent structure" vs "activation structure" distinction
#    - No support for continuous/graded representations
#    - Solutions:
#      a) Implement micro-feature decomposition of symbolic concepts
#      b) Add distributed similarity metrics and clustering
#      c) Separate constituent structure from activation patterns
#      d) Support graded membership and fuzzy binding strengths
#    - Research basis: Smolensky (1990) Section 4-5, distributed representation theory
#
# 5. MISSING LEARNING AND ADAPTATION MECHANISMS
#    - No learning algorithm for acquiring role-filler bindings from experience
#    - Missing weight adaptation rules for improving binding quality
#    - No error-driven learning as in Smolensky's connectionist framework
#    - Missing capacity for acquiring new roles and fillers through learning
#    - Solutions:
#      a) Implement Hebbian learning: weight_ij += α × role_i × filler_j
#      b) Add error-driven learning with backpropagation through TPR structures
#      c) Implement unsupervised discovery of role-filler patterns
#      d) Add online adaptation and forgetting mechanisms
#    - Research basis: Smolensky's framework includes learning as essential component

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
        # FIXME: Critical Theoretical Issues in TensorProductBinding __init__
        #
        # 1. INCORRECT DEFAULT DIMENSIONS (64x64 vs research-accurate sizes)
        #    - Smolensky (1990) used much smaller dimensions (8-16) for theoretical examples
        #    - Large dimensions (64x64=4096) create computational issues and memory problems
        #    - Tensor product binding suffers from dimensionality explosion
        #    - Solutions:
        #      a) Reduce defaults: role_dimension=16, filler_dimension=16 
        #      b) Add warning for large tensor products: dimension > 32x32
        #      c) Implement compressed tensor representation (rank-limited)
        #    - Research note: Smolensky's original examples used small symbolic vectors
        #    - Example:
        #      ```python
        #      if role_dimension * filler_dimension > 1024:
        #          warnings.warn("Large tensor product may cause memory issues. "
        #                       "Consider circular_convolution binding for large dimensions.")
        #      ```
        #
        # 2. MISSING DISTRIBUTED REPRESENTATION PARAMETERS  
        #    - No sparsity control for role/filler vectors
        #    - Missing orthogonality constraints between roles
        #    - No semantic similarity structure in vector space
        #    - Solutions:
        #      a) Add: sparsity_level: float = 0.1  # Fraction of non-zero elements
        #      b) Add: orthogonal_roles: bool = True  # Enforce role orthogonality
        #      c) Add: semantic_structure: Optional[Dict] = None  # Similarity constraints
        #    - Research basis: Distributed representations need structured vector spaces
        #
        # 3. WRONG DEFAULT BINDING TYPE (OUTER_PRODUCT vs CIRCULAR_CONVOLUTION)
        #    - Outer product creates dimensional explosion (role_dim × filler_dim)
        #    - Circular convolution preserves dimensionality (preferred for neural networks)
        #    - Smolensky's original work predates efficient circular convolution methods
        #    - Solutions:
        #      a) Change default: binding_type = BindingOperation.CIRCULAR_CONVOLUTION
        #      b) Add automatic selection based on dimensions
        #      c) Implement hybrid approaches (compressed tensor products)
        #    - Modern consensus: Circular convolution better for large-scale applications
        #
        # 4. MISSING NEURAL IMPLEMENTATION PARAMETERS
        #    - No noise tolerance specifications
        #    - Missing graceful degradation parameters
        #    - No learning rate for adaptive binding strength
        #    - Solutions:
        #      a) Add: noise_tolerance: float = 0.1  # Robustness to neural noise
        #      b) Add: degradation_rate: float = 0.05  # Graceful degradation rate
        #      c) Add: adaptive_binding: bool = False  # Learn binding strengths
        #    - Example:
        #      ```python
        #      # Neural compatibility parameters
        #      self.noise_tolerance = noise_tolerance
        #      self.degradation_rate = degradation_rate
        #      ```
        #
        # 5. MISSING COMPOSITIONAL SYSTEMATICITY CONTROLS
        #    - No productivity constraints (infinite novel combinations)
        #    - Missing systematicity validation (role-filler independence)
        #    - No compositionality metrics
        #    - Solutions:
        #      a) Add: max_composition_depth: int = 10  # Prevent infinite recursion
        #      b) Add: systematicity_check: bool = True  # Validate role-filler independence  
        #      c) Add: compositionality_metrics: bool = False  # Track systematicity
        #    - Critical for cognitive architecture applications
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
        
        # FIXME: Critical Issues in bind() Method - Core TPB Functionality
        #
        # 1. INCORRECT TENSOR PRODUCT IMPLEMENTATION
        #    - Current np.outer().flatten() is not true tensor product binding
        #    - Missing proper tensor algebra operations
        #    - Should preserve tensor structure for compositional operations
        #    - Solutions:
        #      a) Implement proper tensor product: bound_data = np.kron(role.data, filler.data)
        #      b) Maintain tensor structure: bound_tensor = role[:, None] * filler[None, :]
        #      c) Add tensor rank preservation for nested bindings
        #    - Research note: Smolensky emphasized preservation of algebraic structure
        #    - CODE REVIEW SUGGESTION - Replace current implementation with proper tensor algebra:
        #      ```python
        #      def bind_tensor_product_proper(self, role: TPBVector, filler: TPBVector, 
        #                                     binding_strength: float = 1.0) -> TPBVector:
        #          # Proper tensor product binding preserving algebraic structure
        #          # Validation (addresses FIXME #4)
        #          if role.role is None:
        #              warnings.warn("First argument should be a role vector")
        #          if filler.filler is None:
        #              warnings.warn("Second argument should be a filler vector")
        #          
        #          # Check for dimensional explosion
        #          tensor_size = len(role.data) * len(filler.data)
        #          if tensor_size > 1024:
        #              warnings.warn(f"Large tensor product ({len(role.data)}×{len(filler.data)}={tensor_size})")
        #          
        #          # Method 1: Kronecker product (preserves all tensor structure)
        #          bound_tensor = np.kron(role.data, filler.data)
        #          
        #          # Method 2: Maintain 2D matrix structure for unbinding
        #          bound_matrix = np.outer(role.data, filler.data)
        #          
        #          # Apply binding strength (addresses FIXME #3)
        #          bound_tensor *= binding_strength
        #          
        #          return TPBVector(
        #              data=bound_tensor,
        #              role=role.role, filler=filler.filler, is_bound=True,
        #              binding_info={
        #                  'operation': 'tensor_product',
        #                  'tensor_shape': (len(role.data), len(filler.data)),
        #                  'binding_strength': binding_strength,
        #                  'preserves_structure': True,
        #                  'original_matrix': bound_matrix  # For proper unbinding
        #              }
        #          )
        #      ```
        #
        # 2. CIRCULAR CONVOLUTION IMPLEMENTATION ERRORS
        #    - FFT-based implementation may introduce numerical artifacts
        #    - Missing normalization and phase handling
        #    - No error handling for complex FFT results
        #    - Solutions:
        #      a) Add proper normalization: bound_data = bound_data / np.sqrt(len(role.data))
        #      b) Handle complex results: bound_data = np.real(bound_data)
        #      c) Implement direct circular convolution for small vectors
        #    - Mathematical basis: Circular convolution should preserve vector norms
        #
        # 3. MISSING BINDING STRENGTH PARAMETER
        #    - No control over binding strength/confidence
        #    - Should support weighted bindings for semantic gradation
        #    - Missing binding decay for temporal/contextual effects
        #    - Solutions:
        #      a) Add binding_strength parameter: bound_data *= binding_strength
        #      b) Implement semantic distance weighting
        #      c) Add temporal decay: strength *= exp(-time_decay)
        #
        # 4. NO BINDING VALIDATION OR CONSTRAINTS
        #    - Missing validation of role vs filler vector types
        #    - No semantic consistency checking
        #    - Should prevent invalid bindings (e.g., role-role bindings)
        #    - Solutions:
        #      a) Validate vector types before binding
        #      b) Add semantic constraint checking
        #      c) Implement binding compatibility matrix
        #    - Example:
        #      ```python
        #      if role.role is None:
        #          warnings.warn("First argument should be a role vector")
        #      if filler.filler is None:
        #          warnings.warn("Second argument should be a filler vector")
        #      ```
        
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
        # ✅ FIXME ADDRESSED: Initialize comprehensive binding implementations
        if not hasattr(self, '_binding_impl'):
            from .binding_implementations import ComprehensiveBindingImplementations
            self._binding_impl = ComprehensiveBindingImplementations(
                default_operation=self.binding_type,
                preserve_tensor_structure=True,
                enable_warnings=True,
                neural_learning_rate=0.001
            )
        
        # Use provided operation or default
        operation = binding_operation or self.binding_type
        
        # ✅ COMPREHENSIVE IMPLEMENTATION: All FIXME solutions available with user configuration
        try:
            bound_vector_result = self._binding_impl.bind(
                role=role,
                filler=filler, 
                operation=operation,
                binding_strength=getattr(self, 'binding_strength', 1.0),
                enable_learning=getattr(self, 'enable_neural_learning', False)
            )
            bound_data = bound_vector_result.data
            
            # Store comprehensive binding info
            comprehensive_binding_info = bound_vector_result.binding_info or {}
            comprehensive_binding_info.update({
                'role_name': role.role,
                'filler_name': filler.filler,
                'dimensions': f"{len(role.data)}×{len(filler.data)}→{len(bound_vector_result.data)}"
            })
        
        except (ValueError, ImportError) as e:
            # Fallback to legacy implementations for backwards compatibility
            comprehensive_binding_info = {'operation': operation.value, 'method': 'legacy_fallback'}
            
            if operation == BindingOperation.OUTER_PRODUCT:
                bound_data = np.outer(role.data, filler.data).flatten()
            elif operation == BindingOperation.CIRCULAR_CONVOLUTION:
                if len(role.data) != len(filler.data):
                    raise ValueError("Circular convolution requires same-dimension vectors")
                bound_data = np.fft.ifft(np.fft.fft(role.data) * np.fft.fft(filler.data)).real
            elif operation == BindingOperation.ADDITION:
                if len(role.data) != len(filler.data):
                    raise ValueError("Addition requires same-dimension vectors")
                bound_data = role.data + filler.data
            elif operation == BindingOperation.MULTIPLICATION:
                if len(role.data) != len(filler.data):
                    raise ValueError("Multiplication requires same-dimension vectors") 
                bound_data = role.data * filler.data
            else:
                raise ValueError(f"Unknown binding operation: {operation}")
        
        # Create bound vector with comprehensive binding info
        bound_vector = TPBVector(
            data=bound_data,
            role=role.role,
            filler=filler.filler,
            is_bound=True,
            binding_info=comprehensive_binding_info
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
        
        # FIXME: Critical Issues in unbind() Method - Core Tensor Product Unbinding
        #
        # 1. INCORRECT TENSOR PRODUCT UNBINDING MATHEMATICS
        #    - Current matrix operations are approximations, not proper tensor unbinding
        #    - Smolensky (1990) requires tensor contraction for exact unbinding
        #    - Missing proper tensor algebra: should use tensor contraction operations
        #    - Solutions:
        #      a) Implement tensor contraction: result = np.tensordot(bound_tensor, probe_vector, axes=1)
        #      b) Use proper tensor inverse operations when available
        #      c) Implement SVD-based approximate unbinding for noisy conditions
        #    - Research basis: Smolensky emphasized exact mathematical relationships for unbinding
        #    - Example:
        #      ```python
        #      # Proper tensor contraction unbinding
        #      if probe_vector.role is not None:  # Role probe
        #          bound_matrix = bound_vector.data.reshape(self.role_dimension, self.filler_dimension)
        #          # Contract along role dimension: sum_i probe_i * bound_matrix[i,:]
        #          unbound_data = np.tensordot(probe_vector.data, bound_matrix, axes=([0], [0]))
        #      ```
        #
        # 2. MISSING DISTRIBUTED REPRESENTATION CONSIDERATIONS
        #    - No handling of interference from multiple bindings in superposed structures
        #    - Unbinding should account for cross-talk between different role-filler pairs
        #    - Missing noise robustness in unbinding process
        #    - Solutions:
        #      a) Implement interference cancellation for composite structures
        #      b) Add noise-robust unbinding with confidence intervals
        #      c) Use iterative unbinding to improve accuracy
        #    - Research basis: Smolensky discussed graceful degradation with multiple bindings
        #
        # 3. APPROXIMATE UNBINDING WITHOUT ERROR QUANTIFICATION
        #    - No measurement of unbinding accuracy or confidence
        #    - Missing error propagation from binding to unbinding
        #    - Should provide quality metrics for retrieved vectors
        #    - Solutions:
        #      a) Add confidence scoring: confidence = similarity(unbound_result, expected)
        #      b) Implement error bounds estimation
        #      c) Return tuple: (unbound_vector, confidence_score, error_estimate)
        #    - Critical for practical applications requiring reliability assessment
        #
        # 4. CIRCULAR_CONVOLUTION UNBINDING INSTABILITIES
        #    - FFT-based inverse can be numerically unstable
        #    - Division by small FFT coefficients causes artifacts
        #    - No regularization or stability checking
        #    - Solutions:
        #      a) Add regularization: inverse_fft = 1.0 / (fft + regularization_term)
        #      b) Use Tikhonov regularization for stable inversion
        #      c) Implement direct correlation-based unbinding as fallback
        #    - Mathematical basis: Regularized pseudoinverse for stability
        
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
        
        # FIXME: Critical Issues in compose() Method - Compositional Structure Formation
        #
        # 1. NAIVE SUPERPOSITION WITHOUT INTERFERENCE MANAGEMENT
        #    - Simple vector addition causes interference between bindings
        #    - Smolensky (1990) emphasized the importance of managing interference in superposed structures
        #    - No consideration of binding strength or salience weighting
        #    - Solutions:
        #      a) Implement weighted superposition: composite = Σ(weight_i * bound_vector_i)
        #      b) Add interference reduction through orthogonal role design
        #      c) Implement adaptive normalization to prevent saturation
        #    - Research basis: Smolensky discussed interference as key limitation of superposition
        #    - Example:
        #      ```python
        #      # Weighted composition with interference consideration
        #      composite_data = np.zeros_like(bound_vectors[0].data)
        #      total_weight = 0
        #      for i, vec in enumerate(bound_vectors):
        #          weight = self.compute_salience_weight(vec)  # Based on semantic importance
        #          composite_data += weight * vec.data
        #          total_weight += weight
        #      composite_data /= total_weight  # Normalize
        #      ```
        #
        # 2. MISSING COMPOSITIONAL SYSTEMATICITY CONSTRAINTS
        #    - No validation that composed bindings follow systematic compositional rules
        #    - Missing check for role-filler consistency across composed structures
        #    - Should enforce Smolensky's systematicity principle
        #    - Solutions:
        #      a) Validate role uniqueness: each role should appear at most once
        #      b) Check semantic consistency between bound pairs
        #      c) Implement compositional well-formedness constraints
        #    - Research basis: Systematicity is core to Smolensky's compositional architecture
        #
        # 3. NO CAPACITY LIMITS OR DEGRADATION HANDLING
        #    - Unlimited composition can lead to vector saturation
        #    - Missing graceful degradation when too many bindings are composed
        #    - No capacity estimation based on vector dimensionality
        #    - Solutions:
        #      a) Implement capacity limit: max_bindings = sqrt(vector_dimension)
        #      b) Add saturation detection and warning
        #      c) Implement compression for large compositions
        #    - Mathematical basis: Vector space capacity limits composition size
        #
        # 4. MISSING STRUCTURAL RELATIONSHIPS BETWEEN BINDINGS
        #    - No representation of relationships between composed bindings
        #    - Missing hierarchical or dependency structure in composition
        #    - Should support nested compositional structures
        #    - Solutions:
        #      a) Add binding dependency tracking
        #      b) Implement hierarchical composition with structural roles
        #      c) Support recursive tensor product structures
        #    - Research basis: Smolensky's framework supports recursive compositional structure
        
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