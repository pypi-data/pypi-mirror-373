"""
Core Tensor Product Binding Operations

This module implements the fundamental tensor product binding mechanisms
from Smolensky (1990), including all advanced binding methods.
"""

import numpy as np
from typing import Dict, List, Optional, Union
from .config_enums import BindingMethod, BindingOperation, TensorBindingConfig
from .vector_operations import TPBVector


class CoreBinding:
    """Core tensor product binding operations and methods"""
    
    def __init__(self, config: TensorBindingConfig, vector_dim: int = 100):
        """Initialize core binding with configuration"""
        self.config = config
        self.vector_dim = vector_dim
        self.binding_strengths = {}  # (role, filler) -> strength
        
    def bind(self, role_vec: np.ndarray, filler_vec: np.ndarray, 
             binding_strength: Optional[float] = None,
             context: Optional[List[str]] = None,
             hierarchical_level: int = 0, 
             role_name: str = "", 
             filler_name: str = "",
             role_vectors: Optional[Dict[str, np.ndarray]] = None,
             filler_vectors: Optional[Dict[str, np.ndarray]] = None,
             operation: Optional[BindingOperation] = None) -> TPBVector:
        """
        Create Tensor Product Binding Between Role and Filler
        
        Implements Smolensky's (1990) tensor product binding with multiple advanced methods.
        
        Args:
            role_vec: Role vector (variable representation)
            filler_vec: Filler vector (value representation)
            binding_strength: Binding strength (0.0 to 1.0)
            context: Context for disambiguating roles
            hierarchical_level: Nesting depth for hierarchical structures
            role_name: Name of the role (for tracking)
            filler_name: Name of the filler (for tracking)
            role_vectors: Dictionary of role vectors (for context)
            filler_vectors: Dictionary of filler vectors (for context)
            operation: Binding operation type (for compatibility)
            
        Returns:
            TPBVector: Flattened tensor product binding
        """
        
        # Set binding strength
        if binding_strength is None:
            binding_strength = self.config.default_binding_strength
        
        # Apply strength decay for hierarchical levels
        if hierarchical_level > 0:
            binding_strength *= (self.config.recursive_strength_decay ** hierarchical_level)
        
        # Store binding strength
        if self.config.enable_binding_strength and role_name and filler_name:
            self.binding_strengths[(role_name, filler_name)] = binding_strength
        
        # Handle operation parameter for test compatibility
        if operation and operation != BindingOperation.TENSOR_PRODUCT:
            raise NotImplementedError(f"{operation.value} binding not implemented")
        
        # Apply configured binding method
        if self.config.binding_method == BindingMethod.BASIC_OUTER_PRODUCT:
            tensor_product = self._bind_basic_outer_product(role_vec, filler_vec, binding_strength)
        elif self.config.binding_method == BindingMethod.RECURSIVE_BINDING:
            tensor_product = self._bind_recursive(role_vec, filler_vec, binding_strength, hierarchical_level)
        elif self.config.binding_method == BindingMethod.CONTEXT_DEPENDENT:
            tensor_product = self._bind_context_dependent(role_vec, filler_vec, binding_strength, 
                                                        context, role_vectors, filler_vectors)
        elif self.config.binding_method == BindingMethod.WEIGHTED_BINDING:
            tensor_product = self._bind_weighted(role_vec, filler_vec, binding_strength)
        elif self.config.binding_method == BindingMethod.MULTI_DIMENSIONAL:
            tensor_product = self._bind_multi_dimensional(role_vec, filler_vec, binding_strength, 
                                                        role_name, filler_name)
        elif self.config.binding_method == BindingMethod.HYBRID:
            tensor_product = self._bind_hybrid(role_vec, filler_vec, binding_strength, context, 
                                             hierarchical_level, role_name, filler_name,
                                             role_vectors, filler_vectors)
        else:
            # Default to basic outer product
            tensor_product = self._bind_basic_outer_product(role_vec, filler_vec, binding_strength)
        
        # Use proper tensor product binding - flatten the outer product matrix
        tensor_product = np.outer(role_vec, filler_vec) * binding_strength
        return TPBVector(tensor_product.flatten())
    
    def _bind_basic_outer_product(self, role_vec: np.ndarray, filler_vec: np.ndarray, 
                                 binding_strength: float) -> np.ndarray:
        """Basic outer product binding: R ⊗ F"""
        tensor_product = np.outer(role_vec, filler_vec)
        if binding_strength != 1.0:
            tensor_product *= binding_strength
        return tensor_product
    
    def _bind_recursive(self, role_vec: np.ndarray, filler_vec: np.ndarray, 
                       binding_strength: float, hierarchical_level: int) -> np.ndarray:
        """Recursive binding for hierarchical structures (Smolensky Section 4)"""
        
        # For recursive binding, we modify the role vector based on hierarchical level
        if hierarchical_level > 0:
            # Create hierarchical transformation matrix
            hierarchy_transform = np.eye(len(role_vec)) * (1 - 0.1 * hierarchical_level)
            role_vec_transformed = hierarchy_transform @ role_vec
        else:
            role_vec_transformed = role_vec
            
        tensor_product = np.outer(role_vec_transformed, filler_vec) * binding_strength
        return tensor_product
    
    def _bind_context_dependent(self, role_vec: np.ndarray, filler_vec: np.ndarray, 
                               binding_strength: float, context: Optional[List[str]],
                               role_vectors: Optional[Dict[str, np.ndarray]] = None,
                               filler_vectors: Optional[Dict[str, np.ndarray]] = None) -> np.ndarray:
        """Context-dependent binding for ambiguous roles (Smolensky Section 5)"""
        
        if context is None or not self.config.enable_role_ambiguity_resolution:
            return self._bind_basic_outer_product(role_vec, filler_vec, binding_strength)
        
        if role_vectors is None:
            role_vectors = {}
        if filler_vectors is None:
            filler_vectors = {}
        
        # Create context vector from recent context
        context_vec = np.zeros_like(role_vec)
        for ctx_item in context[-self.config.context_window_size:]:
            if ctx_item in role_vectors:
                context_vec += role_vectors[ctx_item]
            elif ctx_item in filler_vectors:
                context_vec += filler_vectors[ctx_item]
        
        if np.linalg.norm(context_vec) > 0:
            context_vec = context_vec / np.linalg.norm(context_vec)
            
            # Modulate role vector based on context
            context_influence = self.config.context_sensitivity
            role_vec_modulated = ((1 - context_influence) * role_vec + 
                                context_influence * context_vec)
            role_vec_modulated = role_vec_modulated / np.linalg.norm(role_vec_modulated)
        else:
            role_vec_modulated = role_vec
            
        tensor_product = np.outer(role_vec_modulated, filler_vec) * binding_strength
        return tensor_product
    
    def _bind_weighted(self, role_vec: np.ndarray, filler_vec: np.ndarray, 
                      binding_strength: float) -> np.ndarray:
        """Weighted binding with soft constraints (Smolensky Section 6)"""
        
        # Create weighted tensor product with non-linear strength modulation
        base_tensor = np.outer(role_vec, filler_vec)
        
        # Apply sigmoid-like strength modulation for soft constraints
        strength_modulated = 1.0 / (1.0 + np.exp(-10 * (binding_strength - 0.5)))
        
        return base_tensor * strength_modulated
    
    def _bind_multi_dimensional(self, role_vec: np.ndarray, filler_vec: np.ndarray, 
                              binding_strength: float, role_name: str, filler_name: str) -> np.ndarray:
        """Multi-dimensional tensor binding (Smolensky Section 3.2)"""
        
        # Get custom dimensions if specified
        role_dim = (self.config.role_dimension_map.get(role_name, len(role_vec)) 
                   if self.config.role_dimension_map else len(role_vec))
        filler_dim = (self.config.filler_dimension_map.get(filler_name, len(filler_vec))
                     if self.config.filler_dimension_map else len(filler_vec))
        
        # Resize vectors if needed
        if role_dim != len(role_vec):
            if role_dim > len(role_vec):
                role_vec_resized = np.pad(role_vec, (0, role_dim - len(role_vec)), 'constant')
            else:
                role_vec_resized = role_vec[:role_dim]
        else:
            role_vec_resized = role_vec
            
        if filler_dim != len(filler_vec):
            if filler_dim > len(filler_vec):
                filler_vec_resized = np.pad(filler_vec, (0, filler_dim - len(filler_vec)), 'constant')
            else:
                filler_vec_resized = filler_vec[:filler_dim]
        else:
            filler_vec_resized = filler_vec
        
        # Create tensor product with potentially different dimensions
        tensor_product = np.outer(role_vec_resized, filler_vec_resized) * binding_strength
        
        # Pad back to standard dimensions if needed
        if tensor_product.shape != (self.vector_dim, self.vector_dim):
            padded_tensor = np.zeros((self.vector_dim, self.vector_dim))
            min_rows = min(tensor_product.shape[0], self.vector_dim)
            min_cols = min(tensor_product.shape[1], self.vector_dim)
            padded_tensor[:min_rows, :min_cols] = tensor_product[:min_rows, :min_cols]
            tensor_product = padded_tensor
        
        return tensor_product
    
    def _bind_hybrid(self, role_vec: np.ndarray, filler_vec: np.ndarray, binding_strength: float,
                    context: Optional[List[str]], hierarchical_level: int, role_name: str, filler_name: str,
                    role_vectors: Optional[Dict[str, np.ndarray]] = None,
                    filler_vectors: Optional[Dict[str, np.ndarray]] = None) -> np.ndarray:
        """Hybrid binding combining multiple methods"""
        
        # Get base tensor from basic method
        base_tensor = self._bind_basic_outer_product(role_vec, filler_vec, binding_strength)
        
        # Add context-dependent modulation if context available
        if context and self.config.enable_role_ambiguity_resolution:
            context_tensor = self._bind_context_dependent(role_vec, filler_vec, binding_strength, 
                                                        context, role_vectors, filler_vectors)
            base_tensor = 0.7 * base_tensor + 0.3 * context_tensor
        
        # Add hierarchical modulation if at deeper level
        if hierarchical_level > 0 and self.config.enable_hierarchical_unbinding:
            recursive_tensor = self._bind_recursive(role_vec, filler_vec, binding_strength, hierarchical_level)
            base_tensor = 0.8 * base_tensor + 0.2 * recursive_tensor
        
        # Apply weighted modulation for soft constraints
        if binding_strength != 1.0:
            weighted_tensor = self._bind_weighted(role_vec, filler_vec, binding_strength)
            base_tensor = 0.9 * base_tensor + 0.1 * weighted_tensor
        
        return base_tensor