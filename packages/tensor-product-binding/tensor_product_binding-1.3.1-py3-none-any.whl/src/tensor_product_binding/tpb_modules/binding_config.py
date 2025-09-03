"""
🔧 Tensor Product Binding Configuration System
==============================================

Configuration system for selecting between multiple tensor product binding
algorithms and their variants. Enables users to choose the most appropriate
method for their specific use case.

Author: Benedict Chen
Based on: Smolensky (1990), Plate (1995), Eliasmith & Anderson (2003)
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any
import numpy as np


class BindingMethod(Enum):
    """
    Available tensor product binding methods with research citations
    """
    # Smolensky (1990) - Original tensor product binding
    OUTER_PRODUCT = "outer_product"
    
    # Plate (1995) - Holographic Reduced Representations  
    CIRCULAR_CONVOLUTION = "circular_convolution"
    HOLOGRAPHIC_REDUCED = "holographic_reduced"
    
    # Eliasmith & Anderson (2003) - Neural Engineering Framework
    NEURAL_ENGINEERING = "neural_engineering"
    
    # Hybrid approaches
    ADAPTIVE_HYBRID = "adaptive_hybrid"


class UnbindingMethod(Enum):
    """
    Available unbinding methods for tensor product recovery
    """
    # Basic mathematical approaches
    PSEUDO_INVERSE = "pseudo_inverse"
    LEAST_SQUARES = "least_squares"
    
    # Circular correlation (Plate 1995)
    CIRCULAR_CORRELATION = "circular_correlation"
    
    # Neural network approaches  
    NEURAL_NETWORK = "neural_network"
    LEARNED_INVERSE = "learned_inverse"
    
    # Iterative methods
    ITERATIVE_REFINEMENT = "iterative_refinement"


class NoiseHandling(Enum):
    """
    Noise handling strategies for robust binding/unbinding
    """
    NONE = "none"
    GAUSSIAN_NOISE = "gaussian_noise"
    CLEANUP_MEMORY = "cleanup_memory"
    THRESHOLDING = "thresholding"
    REGULARIZATION = "regularization"


@dataclass
class TensorProductBindingConfig:
    """
    Comprehensive configuration for tensor product binding operations
    
    This configuration system allows users to select from multiple research-backed
    implementations and fine-tune parameters for their specific use case.
    
    Example:
        # Basic outer product binding (Smolensky 1990)
        config = TensorProductBindingConfig(
            binding_method=BindingMethod.OUTER_PRODUCT,
            unbinding_method=UnbindingMethod.PSEUDO_INVERSE
        )
        
        # Advanced holographic binding (Plate 1995) 
        config = TensorProductBindingConfig(
            binding_method=BindingMethod.HOLOGRAPHIC_REDUCED,
            unbinding_method=UnbindingMethod.CIRCULAR_CORRELATION,
            use_complex_vectors=True,
            cleanup_threshold=0.3
        )
        
        # Neural engineering framework (Eliasmith 2003)
        config = TensorProductBindingConfig(
            binding_method=BindingMethod.NEURAL_ENGINEERING,
            unbinding_method=UnbindingMethod.NEURAL_NETWORK,
            neural_noise_sigma=0.1
        )
    """
    
    # === CORE ALGORITHM SELECTION ===
    binding_method: BindingMethod = BindingMethod.OUTER_PRODUCT
    unbinding_method: UnbindingMethod = UnbindingMethod.PSEUDO_INVERSE
    
    # === VECTOR SPACE CONFIGURATION ===
    vector_dimension: int = 512
    use_complex_vectors: bool = False  # For holographic methods
    normalize_vectors: bool = True
    
    # === OUTER PRODUCT SPECIFIC (Smolensky 1990) ===
    flatten_tensor_product: bool = True
    preserve_tensor_structure: bool = False
    
    # === CIRCULAR CONVOLUTION SPECIFIC (Plate 1995) ===
    convolution_mode: str = "full"  # 'full', 'valid', 'same'
    use_fft_convolution: bool = True  # Faster for large vectors
    
    # === HOLOGRAPHIC REDUCED REPRESENTATIONS (Plate 1995) ===
    cleanup_threshold: float = 0.3
    cleanup_memory_size: int = 1000
    superposition_weight: float = 1.0
    
    # === NEURAL ENGINEERING FRAMEWORK (Eliasmith 2003) ===
    neural_noise_sigma: float = 0.1
    neuron_saturation: float = 1.0
    synaptic_filter_tau: float = 0.1
    
    # === NOISE HANDLING ===
    noise_handling: NoiseHandling = NoiseHandling.NONE
    noise_variance: float = 0.01
    regularization_lambda: float = 0.001
    
    # === UNBINDING OPTIMIZATION ===
    unbind_iterations: int = 100  # For iterative methods
    unbind_tolerance: float = 1e-6
    unbind_learning_rate: float = 0.01
    
    # === PERFORMANCE OPTIMIZATION ===
    use_gpu_acceleration: bool = False
    batch_processing: bool = True
    cache_computations: bool = True
    
    # === VALIDATION AND DEBUGGING ===
    validate_binding_quality: bool = True
    binding_quality_threshold: float = 0.8
    verbose_logging: bool = False
    
    def __post_init__(self):
        """Validate configuration and set dependent parameters"""
        # Validate combinations
        if self.binding_method == BindingMethod.HOLOGRAPHIC_REDUCED:
            if not self.use_complex_vectors:
                self.use_complex_vectors = True
                if self.verbose_logging:
                    print("Auto-enabling complex vectors for holographic binding")
                    
        if self.unbinding_method == UnbindingMethod.CIRCULAR_CORRELATION:
            if self.binding_method != BindingMethod.CIRCULAR_CONVOLUTION:
                if self.verbose_logging:
                    print("Warning: Circular correlation unbinding works best with circular convolution binding")
                    
        # Set optimal defaults based on method
        if self.binding_method == BindingMethod.NEURAL_ENGINEERING:
            if self.noise_handling == NoiseHandling.NONE:
                self.noise_handling = NoiseHandling.GAUSSIAN_NOISE
                
    def get_algorithm_description(self) -> str:
        """Get human-readable description of selected algorithms"""
        descriptions = {
            BindingMethod.OUTER_PRODUCT: "Smolensky (1990) Outer Product - Original tensor product binding",
            BindingMethod.CIRCULAR_CONVOLUTION: "Plate (1995) Circular Convolution - Memory-efficient binding",
            BindingMethod.HOLOGRAPHIC_REDUCED: "Plate (1995) Holographic - Complex-valued binding with cleanup",
            BindingMethod.NEURAL_ENGINEERING: "Eliasmith (2003) Neural Engineering - Biologically plausible binding",
            BindingMethod.ADAPTIVE_HYBRID: "Hybrid approach combining multiple methods"
        }
        
        return f"{descriptions.get(self.binding_method, 'Unknown')} + {self.unbinding_method.value} unbinding"
    
    def estimate_memory_usage(self, num_bindings: int = 1) -> Dict[str, float]:
        """Estimate memory usage in MB for different configurations"""
        base_vector_mb = (self.vector_dimension * 8) / (1024 * 1024)  # 8 bytes per float64
        
        if self.binding_method == BindingMethod.OUTER_PRODUCT:
            if self.flatten_tensor_product:
                binding_mb = (self.vector_dimension ** 2 * 8) / (1024 * 1024)
            else:
                binding_mb = (self.vector_dimension ** 2 * 8) / (1024 * 1024)  # Same for matrix
        else:
            binding_mb = base_vector_mb  # Most other methods preserve dimensionality
            
        total_mb = (base_vector_mb * 2 + binding_mb) * num_bindings
        
        if self.cleanup_memory_size > 0:
            cleanup_mb = (self.cleanup_memory_size * base_vector_mb)
            total_mb += cleanup_mb
            
        return {
            'base_vector_mb': base_vector_mb,
            'binding_mb': binding_mb,
            'total_mb': total_mb,
            'cleanup_mb': self.cleanup_memory_size * base_vector_mb if self.cleanup_memory_size > 0 else 0
        }


# Preset configurations for common use cases
class PresetConfigs:
    """
    Preset configurations for common tensor product binding scenarios
    """
    
    @staticmethod
    def smolensky_original() -> TensorProductBindingConfig:
        """Original Smolensky (1990) tensor product binding"""
        return TensorProductBindingConfig(
            binding_method=BindingMethod.OUTER_PRODUCT,
            unbinding_method=UnbindingMethod.PSEUDO_INVERSE,
            flatten_tensor_product=True,
            normalize_vectors=True,
            validate_binding_quality=True
        )
    
    @staticmethod  
    def plate_holographic() -> TensorProductBindingConfig:
        """Plate (1995) Holographic Reduced Representations"""
        return TensorProductBindingConfig(
            binding_method=BindingMethod.HOLOGRAPHIC_REDUCED,
            unbinding_method=UnbindingMethod.CIRCULAR_CORRELATION,
            use_complex_vectors=True,
            cleanup_threshold=0.3,
            cleanup_memory_size=1000,
            noise_handling=NoiseHandling.CLEANUP_MEMORY
        )
    
    @staticmethod
    def plate_convolution() -> TensorProductBindingConfig:
        """Plate (1995) Circular Convolution binding"""
        return TensorProductBindingConfig(
            binding_method=BindingMethod.CIRCULAR_CONVOLUTION,
            unbinding_method=UnbindingMethod.CIRCULAR_CORRELATION,
            use_fft_convolution=True,
            convolution_mode='same',
            normalize_vectors=True
        )
    
    @staticmethod
    def eliasmith_neural() -> TensorProductBindingConfig:
        """Eliasmith (2003) Neural Engineering Framework"""
        return TensorProductBindingConfig(
            binding_method=BindingMethod.NEURAL_ENGINEERING,
            unbinding_method=UnbindingMethod.NEURAL_NETWORK,
            neural_noise_sigma=0.1,
            noise_handling=NoiseHandling.GAUSSIAN_NOISE,
            neuron_saturation=1.0
        )
    
    @staticmethod
    def performance_optimized() -> TensorProductBindingConfig:
        """High-performance configuration for large-scale applications"""
        return TensorProductBindingConfig(
            binding_method=BindingMethod.CIRCULAR_CONVOLUTION,
            unbinding_method=UnbindingMethod.CIRCULAR_CORRELATION,
            use_fft_convolution=True,
            batch_processing=True,
            cache_computations=True,
            use_gpu_acceleration=True,
            validate_binding_quality=False  # Disable for speed
        )
    
    @staticmethod
    def robust_noisy() -> TensorProductBindingConfig:
        """Configuration optimized for noisy environments"""
        return TensorProductBindingConfig(
            binding_method=BindingMethod.HOLOGRAPHIC_REDUCED,
            unbinding_method=UnbindingMethod.ITERATIVE_REFINEMENT,
            use_complex_vectors=True,
            noise_handling=NoiseHandling.REGULARIZATION,
            regularization_lambda=0.01,
            cleanup_threshold=0.4,
            unbind_iterations=200
        )


# Export key components
__all__ = [
    'BindingMethod',
    'UnbindingMethod', 
    'NoiseHandling',
    'TensorProductBindingConfig',
    'PresetConfigs'
]