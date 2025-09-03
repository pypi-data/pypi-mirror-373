"""
🛠️ Utilities Module for Tensor Product Binding
==============================================

This module provides utility functions and helper classes for the tensor
product binding system. It includes vector operations, validation functions,
mathematical utilities, and common helper operations.

Main Components:
- Vector operations and mathematical utilities
- Validation and error checking functions
- Data conversion and formatting utilities
- Performance optimization helpers
- Debugging and analysis tools
"""

from .vector_utils import (
    cosine_similarity,
    create_normalized_vector,
    create_orthogonal_vectors,
    vector_similarity_matrix,
    normalize_vector,
    random_unit_vector
)
from .validation import (
    validate_vector_dimensions,
    validate_binding_parameters,
    validate_config,
    check_orthogonality,
    validate_structure
)
from .math_utils import (
    soft_threshold,
    gaussian_noise,
    outer_product_flatten,
    matrix_to_vector,
    vector_to_matrix,
    safe_divide,
    entropy
)
from .performance import (
    benchmark_binding_operation,
    profile_memory_usage,
    timing_decorator,
    batch_process,
    parallel_map
)
from .data_utils import (
    save_binding_state,
    load_binding_state,
    export_vectors_csv,
    import_vectors_csv,
    serialize_config,
    deserialize_config
)
from .analysis import (
    analyze_binding_quality,
    compute_structure_complexity,
    measure_semantic_coherence,
    binding_statistics,
    vector_space_analysis
)

__all__ = [
    # Vector utilities
    'cosine_similarity',
    'create_normalized_vector',
    'create_orthogonal_vectors',
    'vector_similarity_matrix',
    'normalize_vector',
    'random_unit_vector',
    
    # Validation
    'validate_vector_dimensions',
    'validate_binding_parameters',
    'validate_config',
    'check_orthogonality',
    'validate_structure',
    
    # Math utilities
    'soft_threshold',
    'gaussian_noise',
    'outer_product_flatten',
    'matrix_to_vector',
    'vector_to_matrix',
    'safe_divide',
    'entropy',
    
    # Performance
    'benchmark_binding_operation',
    'profile_memory_usage',
    'timing_decorator',
    'batch_process',
    'parallel_map',
    
    # Data utilities
    'save_binding_state',
    'load_binding_state',
    'export_vectors_csv',
    'import_vectors_csv',
    'serialize_config',
    'deserialize_config',
    
    # Analysis
    'analyze_binding_quality',
    'compute_structure_complexity',
    'measure_semantic_coherence',
    'binding_statistics',
    'vector_space_analysis'
]