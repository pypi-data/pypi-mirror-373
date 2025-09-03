"""
💰 SUPPORT THIS RESEARCH - PLEASE DONATE! 💰

🙏 If this library helps your research or project, please consider donating:
💳 https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS
❤️ https://github.com/sponsors/benedictchen

Your support makes advanced AI research accessible to everyone! 🚀

Tensor Product Variable Binding Library
=======================================

Based on: Smolensky (1990) "Tensor Product Variable Binding and the Representation of Symbolic Structures"

This library implements the foundational method for representing structured knowledge 
in neural networks using tensor products to bind variables with values.

🔬 Research Foundation:
- Paul Smolensky's Tensor Product Variable Binding
- Tony Plate's Holographic Reduced Representations (HRR) 
- Vector Symbolic Architecture (VSA) principles
- Distributed representation of symbolic structures

🎯 Key Features:
- Tensor product binding operations
- Vector symbolic representation
- Compositional semantics
- Neural binding networks
- Modular architecture for flexibility

🏗️ Modular Architecture:
This package is organized into clean, focused modules:
- core: Core binding operations and algorithms
- config: Configuration classes and enums
- utils: Utility functions and helpers
- visualization: Plotting and analysis tools
"""

# Core tensor product binding functionality
from .core import (
    TensorProductBinding,
    TPBVector,
    BindingOperation,
    VectorSpace,
    SymbolicVector,
    bind_vectors,
    unbind_vectors,
    cleanup_vector
)

# Configuration and enums
from .config import (
    BindingMethod,
    UnbindingMethod,
    VectorSpaceType,
    StructureType,
    TensorBindingConfig,
    BindingPair,
    VectorSpaceConfig,
    PerformanceConfig,
    DEFAULT_CONFIG,
    DEFAULT_VECTOR_DIM,
    DEFAULT_BINDING_STRENGTH,
    OPTIMIZATION_PRESETS,
    apply_preset,
    get_preset_description,
    list_presets
)

# Utility functions
from .utils import (
    # Vector utilities
    cosine_similarity,
    create_normalized_vector,
    create_orthogonal_vectors,
    vector_similarity_matrix,
    normalize_vector,
    random_unit_vector,
    
    # Validation
    validate_vector_dimensions,
    validate_binding_parameters,
    validate_config,
    check_orthogonality,
    validate_structure,
    
    # Math utilities
    soft_threshold,
    gaussian_noise,
    outer_product_flatten,
    matrix_to_vector,
    vector_to_matrix,
    safe_divide,
    entropy,
    
    # Performance
    benchmark_binding_operation,
    profile_memory_usage,
    timing_decorator,
    batch_process,
    parallel_map,
    
    # Data utilities
    save_binding_state,
    load_binding_state,
    export_vectors_csv,
    import_vectors_csv,
    serialize_config,
    deserialize_config,
    
    # Analysis
    analyze_binding_quality,
    compute_structure_complexity,
    measure_semantic_coherence,
    binding_statistics,
    vector_space_analysis
)

# Visualization (optional - may not be available if dependencies missing)
try:
    from .visualization import (
        # Vector plots
        plot_vector,
        plot_vector_comparison,
        plot_similarity_matrix,
        plot_vector_space,
        plot_pca_projection,
        
        # Binding plots
        plot_binding_operation,
        plot_unbinding_quality,
        plot_binding_statistics,
        plot_reconstruction_accuracy,
        
        # Structure plots
        plot_structure_tree,
        plot_compositional_structure,
        plot_hierarchical_binding,
        plot_semantic_network,
        
        # Analysis plots
        plot_quality_metrics,
        plot_complexity_analysis,
        plot_coherence_analysis,
        plot_performance_benchmark,
        
        # Interactive
        create_interactive_vector_explorer,
        create_binding_dashboard,
        create_structure_inspector
    )
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False

# Legacy and compatibility imports (connect to old implementations)
try:
    from .symbolic_structures import SymbolicStructureEncoder, TreeNode
    from .neural_binding import NeuralBindingNetwork
    from .compositional_semantics import CompositionalSemantics
    LEGACY_MODULES_AVAILABLE = True
except ImportError:
    LEGACY_MODULES_AVAILABLE = False


def _print_attribution():
    """Print attribution message with donation link"""
    try:
        print("\n🧮 Tensor Product Binding Library - Made possible by Benedict Chen")
        print("   \033]8;;mailto:benedict@benedictchen.com\033\\benedict@benedictchen.com\033]8;;\033\\")
        print("")
        print("💰 PLEASE DONATE! Your support keeps this research alive! 💰")
        print("   🔗 \033]8;;https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS\033\\💳 CLICK HERE TO DONATE VIA PAYPAL\033]8;;\033\\")
        print("   ❤️ \033]8;;https://github.com/sponsors/benedictchen\033\\💖 SPONSOR ON GITHUB\033]8;;\033\\")
        print("")
        print("   ☕ Buy me a coffee → 🍺 Buy me a beer → 🏎️ Buy me a Lamborghini → ✈️ Buy me a private jet!")
        print("   (Start small, dream big! Every donation helps! 😄)")
        print("")
    except:
        print("\n🧮 Tensor Product Binding Library - Made possible by Benedict Chen")
        print("   benedict@benedictchen.com")
        print("")
        print("💰 PLEASE DONATE! Your support keeps this research alive! 💰")
        print("   💳 PayPal: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS")
        print("   ❤️ GitHub: https://github.com/sponsors/benedictchen")
        print("")
        print("   ☕ Buy me a coffee → 🍺 Buy me a beer → 🏎️ Buy me a Lamborghini → ✈️ Buy me a private jet!")
        print("   (Start small, dream big! Every donation helps! 😄)")


# Convenience factory functions
def create_tpb_system(vector_dim: int = 100, **kwargs) -> TensorProductBinding:
    """
    Create a tensor product binding system with sensible defaults.
    
    Parameters
    ----------
    vector_dim : int, default=100
        Dimension of role and filler vectors
    **kwargs
        Additional configuration parameters
        
    Returns
    -------
    TensorProductBinding
        Configured TPB system
    """
    return TensorProductBinding(vector_dim=vector_dim, **kwargs)


def create_neural_binding_network(network_type="pytorch", *args, **kwargs):
    """
    Create a neural binding network (if legacy modules are available).
    
    Parameters
    ----------
    network_type : str, default="pytorch"
        Type of network to create
    *args, **kwargs
        Arguments to pass to the network constructor
        
    Returns
    -------
    Neural binding network instance
    """
    if not LEGACY_MODULES_AVAILABLE:
        raise ImportError("Neural binding network modules not available")
    
    from .neural_binding import PyTorchBindingNetwork, NumPyBindingNetwork
    
    if network_type.lower() == "pytorch":
        return PyTorchBindingNetwork(*args, **kwargs)
    elif network_type.lower() == "numpy":
        return NumPyBindingNetwork(*args, **kwargs)
    else:
        return NeuralBindingNetwork(*args, **kwargs)


# Show attribution on library import
_print_attribution()

__version__ = "1.2.0"  # Updated for modular architecture
__authors__ = ["Benedict Chen", "Based on Smolensky (1990)"]

# Clean, organized exports
__all__ = [
    # === CORE FUNCTIONALITY ===
    
    # Main classes
    "TensorProductBinding",
    "TPBVector", 
    "VectorSpace",
    "SymbolicVector",
    
    # Core operations
    "bind_vectors",
    "unbind_vectors", 
    "cleanup_vector",
    
    # === CONFIGURATION ===
    
    # Enumerations
    "BindingOperation",
    "BindingMethod",
    "UnbindingMethod", 
    "VectorSpaceType",
    "StructureType",
    
    # Configuration classes
    "TensorBindingConfig",
    "BindingPair",
    "VectorSpaceConfig",
    "PerformanceConfig",
    
    # Default configurations
    "DEFAULT_CONFIG",
    "DEFAULT_VECTOR_DIM", 
    "DEFAULT_BINDING_STRENGTH",
    "OPTIMIZATION_PRESETS",
    
    # Configuration utilities
    "apply_preset",
    "get_preset_description",
    "list_presets",
    
    # === UTILITIES ===
    
    # Vector utilities
    "cosine_similarity",
    "create_normalized_vector",
    "create_orthogonal_vectors", 
    "vector_similarity_matrix",
    "normalize_vector",
    "random_unit_vector",
    
    # Validation
    "validate_vector_dimensions",
    "validate_binding_parameters",
    "validate_config",
    "check_orthogonality",
    "validate_structure",
    
    # Math utilities
    "soft_threshold",
    "gaussian_noise",
    "outer_product_flatten",
    "matrix_to_vector",
    "vector_to_matrix",
    "safe_divide", 
    "entropy",
    
    # Performance utilities
    "benchmark_binding_operation",
    "profile_memory_usage",
    "timing_decorator",
    "batch_process",
    "parallel_map",
    
    # Data utilities
    "save_binding_state",
    "load_binding_state",
    "export_vectors_csv",
    "import_vectors_csv",
    "serialize_config",
    "deserialize_config",
    
    # Analysis utilities
    "analyze_binding_quality",
    "compute_structure_complexity", 
    "measure_semantic_coherence",
    "binding_statistics",
    "vector_space_analysis",
    
    # === FACTORY FUNCTIONS ===
    "create_tpb_system",
    "create_neural_binding_network",
]

# Add visualization exports if available
if VISUALIZATION_AVAILABLE:
    __all__.extend([
        # Vector plots
        "plot_vector",
        "plot_vector_comparison",
        "plot_similarity_matrix",
        "plot_vector_space", 
        "plot_pca_projection",
        
        # Binding plots
        "plot_binding_operation",
        "plot_unbinding_quality",
        "plot_binding_statistics",
        "plot_reconstruction_accuracy",
        
        # Structure plots
        "plot_structure_tree",
        "plot_compositional_structure",
        "plot_hierarchical_binding",
        "plot_semantic_network",
        
        # Analysis plots
        "plot_quality_metrics",
        "plot_complexity_analysis", 
        "plot_coherence_analysis",
        "plot_performance_benchmark",
        
        # Interactive
        "create_interactive_vector_explorer",
        "create_binding_dashboard",
        "create_structure_inspector",
    ])

# Add legacy exports if available
if LEGACY_MODULES_AVAILABLE:
    __all__.extend([
        "SymbolicStructureEncoder",
        "TreeNode", 
        "NeuralBindingNetwork",
        "CompositionalSemantics",
    ])

"""
💝 Thank you for using this research software! 💝

📚 If this work contributed to your research, please:
💳 DONATE: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS
❤️ SPONSOR: https://github.com/sponsors/benedictchen
📝 CITE: Benedict Chen (2025) - Tensor Product Binding Research Implementation

Your support enables continued development of cutting-edge AI research tools! 🎓✨

🏗️ Modular Architecture Benefits:
- Clean separation of concerns
- Easy testing and debugging
- Extensible design patterns
- Comprehensive utility functions
- Professional visualization tools
- Research-grade implementations
"""