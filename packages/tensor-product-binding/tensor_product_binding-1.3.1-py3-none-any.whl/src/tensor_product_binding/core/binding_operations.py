"""
🔗 Core Tensor Product Binding Operations
=========================================

Implementation of the fundamental binding operations for tensor product
variable binding, based on Smolensky (1990).

Key Features:
- Multiple binding methods (outer product, circular convolution, etc.)
- Efficient vector operations
- Memory-optimized representations
- Research-accurate implementations

Author: Benedict Chen (benedict@benedictchen.com)
Based on: Smolensky (1990) tensor product binding theory
"""

import numpy as np
from typing import Union, List, Dict, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass
import warnings


class BindingOperation(Enum):
    """
    🔗 Types of binding operations for tensor product binding.
    
    Mathematical approaches to combine role and filler vectors:
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
    
    Represents a vector in the TPB space with metadata.
    
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
        
        # Ensure data is numpy array
        if not isinstance(self.data, np.ndarray):
            self.data = np.array(self.data)
    
    @property
    def dimension(self) -> int:
        """Get vector dimension"""
        return len(self.data) if self.data.ndim == 1 else self.data.size
    
    @property
    def norm(self) -> float:
        """Get vector norm"""
        return np.linalg.norm(self.data)
    
    def normalize(self) -> 'TPBVector':
        """Return normalized copy of vector"""
        norm = self.norm
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
        """Compute cosine similarity with another TPB vector"""
        if self.data.shape != other.data.shape:
            raise ValueError("Vectors must have same shape for similarity")
        
        norm_self = self.norm
        norm_other = other.norm
        
        if norm_self == 0 or norm_other == 0:
            return 0.0
        
        return np.dot(self.data.flatten(), other.data.flatten()) / (norm_self * norm_other)


class TensorProductBinding:
    """
    🧠 Main Tensor Product Binding System
    
    Implements Smolensky's tensor product variable binding for neural-compatible
    structured representation. Supports multiple binding operations and provides
    efficient encoding/decoding of symbolic structures.
    
    Parameters
    ----------
    vector_dim : int, default=100
        Dimension of role and filler vectors
    binding_method : BindingOperation, default=OUTER_PRODUCT
        Method used for binding operations
    cleanup_vectors : dict, optional
        Dictionary of cleanup vectors for unbinding
    normalize : bool, default=True
        Whether to normalize vectors after operations
    noise_level : float, default=0.0
        Noise level for robust representations
    """
    
    def __init__(self,
                 vector_dim: int = 100,
                 binding_method: BindingOperation = BindingOperation.OUTER_PRODUCT,
                 cleanup_vectors: Optional[Dict[str, np.ndarray]] = None,
                 normalize: bool = True,
                 noise_level: float = 0.0):
        
        self.vector_dim = vector_dim
        self.binding_method = binding_method
        self.normalize = normalize
        self.noise_level = noise_level
        
        # Initialize vector storage
        self.role_vectors: Dict[str, TPBVector] = {}
        self.filler_vectors: Dict[str, TPBVector] = {} 
        self.cleanup_vectors = cleanup_vectors or {}
        
        # Binding operation statistics
        self.binding_stats = {
            'total_bindings': 0,
            'successful_unbindings': 0,
            'failed_unbindings': 0
        }
    
    def create_role_vector(self, role_name: str, vector_data: Optional[np.ndarray] = None) -> TPBVector:
        """
        Create or retrieve a role vector.
        
        Parameters
        ----------
        role_name : str
            Name of the role
        vector_data : np.ndarray, optional
            Specific vector data, otherwise random vector generated
            
        Returns
        -------
        TPBVector
            The role vector
        """
        if role_name in self.role_vectors:
            return self.role_vectors[role_name]
        
        if vector_data is None:
            # Generate random role vector
            vector_data = np.random.randn(self.vector_dim)
            if self.normalize:
                vector_data = vector_data / np.linalg.norm(vector_data)
        
        role_vector = TPBVector(
            data=vector_data,
            role=role_name,
            is_bound=False,
            binding_info={'type': 'role', 'created': 'auto-generated'}
        )
        
        self.role_vectors[role_name] = role_vector
        return role_vector
    
    def create_filler_vector(self, filler_name: str, vector_data: Optional[np.ndarray] = None) -> TPBVector:
        """
        Create or retrieve a filler vector.
        
        Parameters
        ----------
        filler_name : str
            Name of the filler
        vector_data : np.ndarray, optional
            Specific vector data, otherwise random vector generated
            
        Returns
        -------
        TPBVector
            The filler vector
        """
        if filler_name in self.filler_vectors:
            return self.filler_vectors[filler_name]
        
        if vector_data is None:
            # Generate random filler vector
            vector_data = np.random.randn(self.vector_dim)
            if self.normalize:
                vector_data = vector_data / np.linalg.norm(vector_data)
        
        filler_vector = TPBVector(
            data=vector_data,
            filler=filler_name,
            is_bound=False,
            binding_info={'type': 'filler', 'created': 'auto-generated'}
        )
        
        self.filler_vectors[filler_name] = filler_vector
        return filler_vector
    
    def bind(self, role: Union[str, TPBVector], filler: Union[str, TPBVector]) -> TPBVector:
        """
        Bind a role vector to a filler vector.
        
        Parameters
        ----------
        role : str or TPBVector
            Role to bind (creates if string)
        filler : str or TPBVector
            Filler to bind (creates if string)
            
        Returns
        -------
        TPBVector
            Bound representation
        """
        # Convert strings to vectors
        if isinstance(role, str):
            role = self.create_role_vector(role)
        if isinstance(filler, str):
            filler = self.create_filler_vector(filler)
        
        # Perform binding based on method
        if self.binding_method == BindingOperation.OUTER_PRODUCT:
            bound_data = self._outer_product_bind(role.data, filler.data)
        elif self.binding_method == BindingOperation.CIRCULAR_CONVOLUTION:
            bound_data = self._circular_convolution_bind(role.data, filler.data)
        elif self.binding_method == BindingOperation.ADDITION:
            bound_data = self._addition_bind(role.data, filler.data)
        elif self.binding_method == BindingOperation.MULTIPLICATION:
            bound_data = self._multiplication_bind(role.data, filler.data)
        else:
            raise ValueError(f"Unknown binding method: {self.binding_method}")
        
        # Add noise if specified
        if self.noise_level > 0:
            noise = np.random.randn(*bound_data.shape) * self.noise_level
            bound_data = bound_data + noise
        
        # Normalize if specified
        if self.normalize and np.linalg.norm(bound_data) > 0:
            bound_data = bound_data / np.linalg.norm(bound_data)
        
        # Create bound vector
        bound_vector = TPBVector(
            data=bound_data,
            role=role.role,
            filler=filler.filler,
            is_bound=True,
            binding_info={
                'method': self.binding_method.value,
                'role_dim': len(role.data),
                'filler_dim': len(filler.data),
                'noise_level': self.noise_level
            }
        )
        
        self.binding_stats['total_bindings'] += 1
        return bound_vector
    
    def _outer_product_bind(self, role_data: np.ndarray, filler_data: np.ndarray) -> np.ndarray:
        """Outer product binding (standard tensor product)"""
        return np.outer(role_data, filler_data).flatten()
    
    def _circular_convolution_bind(self, role_data: np.ndarray, filler_data: np.ndarray) -> np.ndarray:
        """Circular convolution binding"""
        if len(role_data) != len(filler_data):
            raise ValueError("Circular convolution requires same-dimension vectors")
        return np.fft.ifft(np.fft.fft(role_data) * np.fft.fft(filler_data)).real
    
    def _addition_bind(self, role_data: np.ndarray, filler_data: np.ndarray) -> np.ndarray:
        """Simple addition binding"""
        if len(role_data) != len(filler_data):
            raise ValueError("Addition binding requires same-dimension vectors")
        return role_data + filler_data
    
    def _multiplication_bind(self, role_data: np.ndarray, filler_data: np.ndarray) -> np.ndarray:
        """Element-wise multiplication binding"""
        if len(role_data) != len(filler_data):
            raise ValueError("Multiplication binding requires same-dimension vectors")
        return role_data * filler_data
    
    def unbind(self, bound_vector: TPBVector, role: Union[str, TPBVector]) -> TPBVector:
        """
        Attempt to unbind a filler from a bound vector using a role.
        
        Parameters
        ----------
        bound_vector : TPBVector
            The bound vector to unbind from
        role : str or TPBVector
            The role vector to use for unbinding
            
        Returns
        -------
        TPBVector
            Reconstructed filler vector
        """
        if isinstance(role, str):
            if role in self.role_vectors:
                role = self.role_vectors[role]
            else:
                warnings.warn(f"Role '{role}' not found in stored vectors")
                return None
        
        # Perform unbinding based on original binding method
        method = bound_vector.binding_info.get('method', self.binding_method.value)
        
        try:
            if method == 'outer_product':
                unbound_data = self._outer_product_unbind(bound_vector.data, role.data)
            elif method == 'circular_convolution':
                unbound_data = self._circular_convolution_unbind(bound_vector.data, role.data)
            elif method in ['addition', 'multiplication']:
                # These methods are not easily reversible
                warnings.warn(f"Unbinding not reliable for method: {method}")
                unbound_data = bound_vector.data  # Return original
            else:
                raise ValueError(f"Unknown unbinding method: {method}")
            
            # Create unbound vector
            unbound_vector = TPBVector(
                data=unbound_data,
                role=None,
                filler=f"unbound_from_{bound_vector.filler or 'unknown'}",
                is_bound=False,
                binding_info={
                    'type': 'unbound_filler',
                    'original_method': method,
                    'unbound_with_role': role.role
                }
            )
            
            self.binding_stats['successful_unbindings'] += 1
            return unbound_vector
            
        except Exception as e:
            self.binding_stats['failed_unbindings'] += 1
            warnings.warn(f"Unbinding failed: {e}")
            return None
    
    def _outer_product_unbind(self, bound_data: np.ndarray, role_data: np.ndarray) -> np.ndarray:
        """Unbind using outer product (approximate)"""
        # Reshape bound data back to matrix form
        bound_matrix = bound_data.reshape(len(role_data), -1)
        
        # Use pseudo-inverse to approximate unbinding
        role_norm = np.linalg.norm(role_data)
        if role_norm > 0:
            role_normalized = role_data / role_norm
            return bound_matrix.T @ role_normalized
        else:
            return np.zeros(bound_matrix.shape[1])
    
    def _circular_convolution_unbind(self, bound_data: np.ndarray, role_data: np.ndarray) -> np.ndarray:
        """Unbind using circular convolution"""
        # Circular convolution unbinding uses correlation
        role_fft = np.fft.fft(role_data)
        bound_fft = np.fft.fft(bound_data)
        
        # Avoid division by zero
        role_fft_conj = np.conj(role_fft)
        denominator = np.abs(role_fft)**2
        safe_denominator = np.where(denominator > 1e-12, denominator, 1e-12)
        
        unbound_fft = bound_fft * role_fft_conj / safe_denominator
        return np.fft.ifft(unbound_fft).real
    
    def superpose(self, vectors: List[TPBVector], weights: Optional[List[float]] = None) -> TPBVector:
        """
        Create superposition of multiple bound vectors.
        
        Parameters
        ----------
        vectors : List[TPBVector]
            Vectors to superpose
        weights : List[float], optional
            Weights for each vector
            
        Returns
        -------
        TPBVector
            Superposed vector
        """
        if not vectors:
            raise ValueError("Cannot superpose empty vector list")
        
        if weights is None:
            weights = [1.0] * len(vectors)
        
        if len(weights) != len(vectors):
            raise ValueError("Number of weights must match number of vectors")
        
        # Initialize with first vector
        superposed_data = weights[0] * vectors[0].data.copy()
        
        # Add remaining vectors
        for i in range(1, len(vectors)):
            if vectors[i].data.shape != superposed_data.shape:
                raise ValueError("All vectors must have same shape for superposition")
            superposed_data += weights[i] * vectors[i].data
        
        # Normalize if specified
        if self.normalize and np.linalg.norm(superposed_data) > 0:
            superposed_data = superposed_data / np.linalg.norm(superposed_data)
        
        # Create superposed vector
        role_names = [v.role for v in vectors if v.role]
        filler_names = [v.filler for v in vectors if v.filler]
        
        superposed_vector = TPBVector(
            data=superposed_data,
            role=f"superposed_roles_{'+'.join(role_names[:3])}" if role_names else None,
            filler=f"superposed_fillers_{'+'.join(filler_names[:3])}" if filler_names else None,
            is_bound=any(v.is_bound for v in vectors),
            binding_info={
                'type': 'superposition',
                'num_vectors': len(vectors),
                'weights': weights,
                'component_methods': [v.binding_info.get('method', 'unknown') for v in vectors]
            }
        )
        
        return superposed_vector
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get binding operation statistics"""
        total_attempts = (self.binding_stats['successful_unbindings'] + 
                         self.binding_stats['failed_unbindings'])
        
        return {
            'total_bindings': self.binding_stats['total_bindings'],
            'total_unbinding_attempts': total_attempts,
            'successful_unbindings': self.binding_stats['successful_unbindings'],
            'failed_unbindings': self.binding_stats['failed_unbindings'],
            'unbinding_success_rate': (
                self.binding_stats['successful_unbindings'] / total_attempts 
                if total_attempts > 0 else 0.0
            ),
            'stored_role_vectors': len(self.role_vectors),
            'stored_filler_vectors': len(self.filler_vectors),
            'vector_dimension': self.vector_dim,
            'binding_method': self.binding_method.value,
            'normalization_enabled': self.normalize,
            'noise_level': self.noise_level
        }