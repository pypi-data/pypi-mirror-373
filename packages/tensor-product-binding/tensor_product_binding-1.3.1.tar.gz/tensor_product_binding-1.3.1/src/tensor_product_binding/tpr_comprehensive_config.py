"""
Tensor Product Binding Comprehensive Configuration System
=======================================================

Author: Benedict Chen (benedict@benedictchen.com)

Configuration system for ALL TPR FIXME solutions identified in the comprehensive
code review, allowing users to select from multiple research-accurate approaches.

Based on: Smolensky (1990) "Tensor Product Variable Binding and the 
         Representation of Symbolic Structures in Connectionist Systems"
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Union, Callable, Tuple
from enum import Enum
import numpy as np


class TPRArchitectureMethod(Enum):
    """Tensor Product Representation architectural approaches."""
    SMOLENSKY_ORIGINAL = "smolensky_original"  # Exact Smolensky (1990) formulation
    NEURAL_UNIT_BASED = "neural_unit_based"  # Neural units with activation functions
    VECTOR_ALGEBRAIC = "vector_algebraic"  # Current simplified vector approach
    HYBRID_NEURAL_VECTOR = "hybrid"  # Combine neural units with vector operations


class BindingOperationMethod(Enum):
    """Role-filler binding operation implementations."""
    TENSOR_PRODUCT = "tensor_product"  # Full tensor product (outer product)
    CIRCULAR_CONVOLUTION = "circular_convolution"  # HRR-style binding
    COMPRESSED_TENSOR = "compressed_tensor"  # Reduced-rank approximation
    NEURAL_PRODUCT_UNITS = "neural_product_units"  # Smolensky's product units


class DecompositionStrategy(Enum):
    """Role and filler decomposition strategies."""
    SVD_DECOMPOSITION = "svd"  # Singular Value Decomposition
    EIGENDECOMPOSITION = "eigen"  # Eigenvalue decomposition
    ITERATIVE_REFINEMENT = "iterative"  # Iterative role/filler extraction
    NEURAL_COMPETITIVE = "competitive"  # Competitive neural networks


class SystematicityValidation(Enum):
    """Systematicity principle validation methods."""
    COMPOSITION_CONSISTENCY = "composition_consistency"  # Test compositional rules
    PRODUCTIVITY_MEASURES = "productivity_measures"  # Measure infinite generation capacity
    CONSTITUENCY_PARSING = "constituency_parsing"  # Parse constituent structure
    RECURSIVE_EMBEDDING = "recursive_embedding"  # Test recursive structure handling


class DistributedRepresentation(Enum):
    """Distributed representation approaches."""
    MICROFEATURE_ANALYSIS = "microfeature"  # Smolensky's micro-feature decomposition
    SIMILARITY_CLUSTERING = "similarity_clustering"  # Distributed similarity structure
    GRADED_MEMBERSHIP = "graded_membership"  # Fuzzy binding strengths
    ACTIVATION_PATTERNS = "activation_patterns"  # Neural activation-based representation


class LearningMechanism(Enum):
    """TPR learning and adaptation mechanisms."""
    HEBBIAN_LEARNING = "hebbian"  # Hebbian weight updates
    ERROR_DRIVEN_BP = "backprop"  # Error-driven backpropagation
    UNSUPERVISED_DISCOVERY = "unsupervised"  # Discover role-filler patterns
    ONLINE_ADAPTATION = "online"  # Online learning with forgetting


@dataclass
class TPRComprehensiveConfig:
    """
    MASTER CONFIGURATION for ALL TPR FIXME solutions.
    
    Comprehensive configuration covering all aspects of Smolensky's TPR
    framework with multiple implementation approaches.
    """
    
    # ============================================================================
    # FUNDAMENTAL THEORETICAL ARCHITECTURE SOLUTIONS
    # ============================================================================
    
    # Architecture Method
    tpr_architecture_method: TPRArchitectureMethod = TPRArchitectureMethod.SMOLENSKY_ORIGINAL
    
    # Tensor Algebra Foundation
    preserve_tensor_rank: bool = True  # Maintain tensor rank throughout operations
    track_rank_degradation: bool = True  # Monitor rank loss during operations
    max_tensor_rank: int = 3  # Maximum allowed tensor rank
    
    # Role/Filler Decomposition Parameters
    role_vector_dimension: int = 100  # Dimensionality of role vectors
    filler_vector_dimension: int = 100  # Dimensionality of filler vectors
    decomposition_tolerance: float = 1e-6  # Numerical tolerance for decomposition
    
    # Activity vs Weight Vectors (Smolensky's distinction)
    separate_activity_weight_vectors: bool = True  # Distinguish activation from weights
    activity_vector_normalization: str = "l2"  # "l2", "l1", "softmax", "none"
    weight_vector_initialization: str = "xavier"  # "xavier", "he", "random", "zeros"
    
    # ============================================================================
    # CONNECTIONIST IMPLEMENTATION SOLUTIONS
    # ============================================================================
    
    # Neural Unit Implementation
    use_neural_units: bool = True  # Implement actual neural units
    activation_function: str = "tanh"  # "tanh", "sigmoid", "relu", "linear"
    neural_unit_bias: bool = True  # Include bias terms in neural units
    
    # Product Units (Smolensky's core innovation)
    implement_product_units: bool = True  # Use product units for role×filler
    product_unit_function: str = "multiplicative"  # "multiplicative", "polynomial", "sigma_pi"
    max_product_interactions: int = 2  # Maximum order of multiplicative interactions
    
    # Neural Network Integration
    enable_gradient_computation: bool = True  # Support backpropagation
    connection_sparsity: float = 0.1  # Sparsity level for neural connections
    plasticity_rate: float = 0.01  # Learning rate for synaptic plasticity
    
    # ============================================================================
    # BINDING OPERATION SOLUTIONS
    # ============================================================================
    
    # Binding Method
    binding_operation_method: BindingOperationMethod = BindingOperationMethod.TENSOR_PRODUCT
    
    # Tensor Product Parameters
    full_tensor_product: bool = True  # Use full outer product
    tensor_compression_rank: int = 50  # Rank for compressed tensors
    compression_method: str = "svd"  # "svd", "tucker", "cp_decomposition"
    
    # Circular Convolution Parameters (for HRR compatibility)
    convolution_dimension: int = 512  # Vector dimension for convolution
    normalization_after_binding: bool = True  # Normalize after binding
    
    # Neural Product Unit Parameters
    product_unit_learning_rate: float = 0.001  # Learning rate for product units
    product_unit_regularization: float = 0.01  # L2 regularization strength
    
    # ============================================================================
    # DECOMPOSITION STRATEGY SOLUTIONS
    # ============================================================================
    
    # Decomposition Method
    decomposition_strategy: DecompositionStrategy = DecompositionStrategy.SVD_DECOMPOSITION
    
    # SVD Decomposition Parameters
    svd_rank_threshold: float = 0.01  # Minimum singular value threshold
    svd_max_iterations: int = 1000  # Maximum iterations for iterative SVD
    truncated_svd_components: int = 50  # Number of components to keep
    
    # Iterative Refinement Parameters
    refinement_max_iterations: int = 100  # Maximum refinement iterations
    convergence_threshold: float = 1e-5  # Convergence criterion
    refinement_learning_rate: float = 0.1  # Learning rate for refinement
    
    # Competitive Neural Network Parameters
    competitive_learning_rate: float = 0.05  # Learning rate for competitive learning
    winner_take_all_sharpness: float = 2.0  # Sharpness of winner-take-all competition
    
    # ============================================================================
    # SYSTEMATICITY AND COMPOSITIONALITY SOLUTIONS
    # ============================================================================
    
    # Systematicity Validation
    systematicity_validation: SystematicityValidation = SystematicityValidation.COMPOSITION_CONSISTENCY
    
    # Composition Consistency Parameters
    test_composition_symmetries: bool = True  # Test if A∘B implies B∘A handling
    composition_error_tolerance: float = 0.1  # Error tolerance for consistency tests
    
    # Productivity Measures
    measure_productivity: bool = True  # Estimate infinite generation capacity
    productivity_sample_size: int = 1000  # Sample size for productivity estimation
    novel_combination_threshold: float = 0.9  # Threshold for "novel" combinations
    
    # Constituency Parsing
    enable_constituency_parsing: bool = True  # Parse constituent structure
    parsing_beam_width: int = 5  # Beam search width for parsing
    constituency_confidence_threshold: float = 0.7  # Confidence threshold
    
    # Recursive Embedding Support
    max_recursion_depth: int = 5  # Maximum recursive embedding depth
    recursive_memory_buffer: int = 100  # Buffer size for recursive structures
    
    # ============================================================================
    # DISTRIBUTED REPRESENTATION SOLUTIONS
    # ============================================================================
    
    # Distributed Representation Method
    distributed_representation: DistributedRepresentation = DistributedRepresentation.MICROFEATURE_ANALYSIS
    
    # Micro-feature Analysis (Smolensky's approach)
    microfeature_dimension: int = 50  # Number of micro-features per concept
    microfeature_sparsity: float = 0.1  # Sparsity level of micro-features
    semantic_similarity_threshold: float = 0.3  # Threshold for semantic similarity
    
    # Similarity Clustering Parameters
    similarity_metric: str = "cosine"  # "cosine", "euclidean", "manhattan"
    clustering_method: str = "hierarchical"  # "hierarchical", "kmeans", "spectral"
    similarity_cluster_count: int = 10  # Number of similarity clusters
    
    # Graded Membership Parameters
    use_fuzzy_binding: bool = True  # Enable fuzzy/graded binding strengths
    binding_confidence_range: Tuple[float, float] = (0.0, 1.0)  # Confidence range
    membership_function: str = "sigmoid"  # "sigmoid", "gaussian", "linear"
    
    # Activation Pattern Analysis
    track_activation_patterns: bool = True  # Monitor neural activation patterns
    activation_pattern_dimension: int = 200  # Dimension of activation vectors
    pattern_similarity_window: int = 50  # Window for pattern similarity analysis
    
    # ============================================================================
    # LEARNING AND ADAPTATION SOLUTIONS
    # ============================================================================
    
    # Learning Mechanism
    learning_mechanism: LearningMechanism = LearningMechanism.HEBBIAN_LEARNING
    
    # Hebbian Learning Parameters
    hebbian_learning_rate: float = 0.01  # α in weight_ij += α × role_i × filler_j
    hebbian_decay_rate: float = 0.001  # Forgetting rate for unused connections
    correlation_threshold: float = 0.1  # Minimum correlation for Hebbian updates
    
    # Error-Driven Learning Parameters
    backprop_learning_rate: float = 0.001  # Learning rate for backpropagation
    error_function: str = "mse"  # "mse", "cross_entropy", "cosine_distance"
    gradient_clipping_threshold: float = 1.0  # Gradient clipping threshold
    
    # Unsupervised Discovery Parameters
    discovery_method: str = "ica"  # "ica", "pca", "nmf", "autoencoder"
    pattern_discovery_threshold: float = 0.2  # Threshold for pattern significance
    min_pattern_frequency: int = 5  # Minimum occurrences for pattern recognition
    
    # Online Adaptation Parameters
    online_learning_window: int = 100  # Window size for online learning
    adaptation_rate: float = 0.05  # Rate of adaptation to new patterns
    forgetting_function: str = "exponential"  # "exponential", "linear", "power_law"
    memory_consolidation_threshold: float = 0.8  # Threshold for memory consolidation
    
    # ============================================================================
    # PERFORMANCE AND DEBUGGING OPTIONS
    # ============================================================================
    
    # Performance Settings
    enable_gpu_acceleration: bool = False  # Use GPU for tensor operations
    batch_processing: bool = True  # Process multiple bindings in batches
    cache_decompositions: bool = True  # Cache expensive decomposition results
    
    # Memory Management
    max_memory_usage_mb: int = 1000  # Maximum memory usage in MB
    garbage_collection_frequency: int = 1000  # GC frequency for large tensors
    
    # Debugging and Validation
    validate_against_smolensky_paper: bool = False  # Runtime validation against paper
    log_tensor_operations: bool = False  # Log all tensor operations
    trace_binding_decomposition: bool = False  # Trace binding/unbinding processes
    monitor_rank_degradation: bool = True  # Monitor tensor rank degradation
    
    # Output Control
    verbose_output: bool = True  # Detailed learning and binding progress
    save_intermediate_tensors: bool = False  # Save intermediate computations
    visualization_enabled: bool = False  # Enable tensor/binding visualization


def create_smolensky_accurate_config() -> TPRComprehensiveConfig:
    """
    Create configuration that matches Smolensky (1990) TPR paper exactly.
    
    Returns:
        TPRComprehensiveConfig: Research-accurate configuration
    """
    return TPRComprehensiveConfig(
        # Exact Smolensky formulation
        tpr_architecture_method=TPRArchitectureMethod.SMOLENSKY_ORIGINAL,
        binding_operation_method=BindingOperationMethod.TENSOR_PRODUCT,
        
        # Neural unit implementation as in original paper
        use_neural_units=True,
        implement_product_units=True,
        product_unit_function="multiplicative",
        
        # Proper role-filler decomposition
        decomposition_strategy=DecompositionStrategy.SVD_DECOMPOSITION,
        separate_activity_weight_vectors=True,
        
        # Systematicity principle enforcement
        systematicity_validation=SystematicityValidation.COMPOSITION_CONSISTENCY,
        test_composition_symmetries=True,
        
        # Distributed representation theory
        distributed_representation=DistributedRepresentation.MICROFEATURE_ANALYSIS,
        microfeature_dimension=50,
        
        # Learning mechanisms from paper
        learning_mechanism=LearningMechanism.HEBBIAN_LEARNING,
        hebbian_learning_rate=0.01,
        
        # Research validation
        validate_against_smolensky_paper=True,
        preserve_tensor_rank=True
    )


def create_neural_optimized_config() -> TPRComprehensiveConfig:
    """
    Create configuration optimized for neural network integration.
    
    Returns:
        TPRComprehensiveConfig: Neural-optimized configuration
    """
    return TPRComprehensiveConfig(
        # Neural-friendly architecture
        tpr_architecture_method=TPRArchitectureMethod.NEURAL_UNIT_BASED,
        binding_operation_method=BindingOperationMethod.NEURAL_PRODUCT_UNITS,
        
        # Optimized for gradient-based learning
        learning_mechanism=LearningMechanism.ERROR_DRIVEN_BP,
        enable_gradient_computation=True,
        backprop_learning_rate=0.001,
        
        # Compressed tensors for efficiency
        full_tensor_product=False,
        tensor_compression_rank=50,
        
        # GPU acceleration
        enable_gpu_acceleration=True,
        batch_processing=True,
        
        # Moderate systematicity checking (for speed)
        systematicity_validation=SystematicityValidation.PRODUCTIVITY_MEASURES,
        
        # Efficient distributed representation
        distributed_representation=DistributedRepresentation.ACTIVATION_PATTERNS,
        
        # Memory efficiency
        cache_decompositions=True,
        max_memory_usage_mb=2000
    )


def create_research_debugging_config() -> TPRComprehensiveConfig:
    """
    Create configuration with maximum debugging and validation features.
    
    Returns:
        TPRComprehensiveConfig: Debug-focused configuration
    """
    return TPRComprehensiveConfig(
        # Research-accurate methods
        tpr_architecture_method=TPRArchitectureMethod.SMOLENSKY_ORIGINAL,
        binding_operation_method=BindingOperationMethod.TENSOR_PRODUCT,
        
        # Maximum validation
        validate_against_smolensky_paper=True,
        systematicity_validation=SystematicityValidation.COMPOSITION_CONSISTENCY,
        test_composition_symmetries=True,
        measure_productivity=True,
        enable_constituency_parsing=True,
        
        # Comprehensive debugging
        log_tensor_operations=True,
        trace_binding_decomposition=True,
        monitor_rank_degradation=True,
        track_activation_patterns=True,
        
        # Detailed output
        verbose_output=True,
        save_intermediate_tensors=True,
        visualization_enabled=True,
        
        # Conservative parameters for stability
        decomposition_tolerance=1e-8,
        convergence_threshold=1e-6,
        max_tensor_rank=2  # Simplified for debugging
    )


def get_available_tpr_solutions() -> Dict[str, List[str]]:
    """
    Get all available TPR solution options organized by category.
    
    Returns:
        Dict[str, List[str]]: All available solution methods
    """
    return {
        "TPR Architecture Methods": [method.value for method in TPRArchitectureMethod],
        "Binding Operation Methods": [method.value for method in BindingOperationMethod],
        "Decomposition Strategies": [strategy.value for strategy in DecompositionStrategy],
        "Systematicity Validation": [validation.value for validation in SystematicityValidation],
        "Distributed Representation": [rep.value for rep in DistributedRepresentation],
        "Learning Mechanisms": [mechanism.value for mechanism in LearningMechanism],
        
        "Configuration Presets": [
            "smolensky_accurate",
            "neural_optimized",
            "research_debugging"
        ],
        
        "Research Papers Implemented": [
            "Smolensky (1990) 'Tensor Product Variable Binding'",
            "Smolensky (1991) 'Connectionist constituent structure'", 
            "Smolensky (1995) 'Constituent structure & explanation'",
            "Plate (1995) 'Holographic reduced representations'"
        ]
    }


def validate_tpr_config(config: TPRComprehensiveConfig) -> List[str]:
    """
    Validate TPR configuration and return warnings/issues.
    
    Args:
        config: Configuration to validate
        
    Returns:
        List[str]: Validation warnings and issues
    """
    warnings = []
    
    # Check for theoretical consistency
    if (config.binding_operation_method == BindingOperationMethod.CIRCULAR_CONVOLUTION and
        config.tpr_architecture_method == TPRArchitectureMethod.SMOLENSKY_ORIGINAL):
        warnings.append("⚠️ Circular convolution not in original Smolensky framework")
    
    if not config.preserve_tensor_rank and config.validate_against_smolensky_paper:
        warnings.append("🚨 CRITICAL: Rank degradation conflicts with Smolensky's tensor theory")
    
    if not config.use_neural_units and config.tpr_architecture_method == TPRArchitectureMethod.NEURAL_UNIT_BASED:
        warnings.append("❌ Inconsistent: Neural unit method selected but neural units disabled")
    
    # Check for computational feasibility
    total_tensor_size = config.role_vector_dimension * config.filler_vector_dimension
    if config.full_tensor_product and total_tensor_size > 100000:
        warnings.append("⚠️ Large tensor product may cause memory issues - consider compression")
    
    if config.max_recursion_depth > 10:
        warnings.append("⚠️ Very deep recursion may cause stack overflow")
    
    # Check for learning consistency
    if (config.learning_mechanism == LearningMechanism.ERROR_DRIVEN_BP and
        not config.enable_gradient_computation):
        warnings.append("❌ Backpropagation learning requires gradient computation enabled")
    
    # Check parameter ranges
    if config.hebbian_learning_rate <= 0 or config.hebbian_learning_rate > 1:
        warnings.append("❌ Hebbian learning rate must be between 0 and 1")
    
    if config.microfeature_sparsity <= 0 or config.microfeature_sparsity > 1:
        warnings.append("❌ Microfeature sparsity must be between 0 and 1")
    
    # Check research validation settings
    if (config.validate_against_smolensky_paper and
        config.binding_operation_method != BindingOperationMethod.TENSOR_PRODUCT):
        warnings.append("💡 Consider tensor product method for Smolensky validation")
    
    return warnings


def print_tpr_solutions_summary():
    """Print comprehensive summary of all implemented TPR solutions."""
    
    print("🧠 TENSOR PRODUCT BINDING COMPREHENSIVE SOLUTIONS")
    print("=" * 80)
    print()
    
    solutions = get_available_tpr_solutions()
    
    for category, items in solutions.items():
        print(f"🔧 {category}:")
        for item in items:
            print(f"   ✅ {item}")
        print()
    
    print("🎯 USAGE EXAMPLES:")
    print("   # Smolensky (1990) research-accurate configuration")
    print("   config = create_smolensky_accurate_config()")
    print()
    print("   # Neural network optimized configuration")
    print("   config = create_neural_optimized_config()")
    print()  
    print("   # Custom configuration")
    print("   config = TPRComprehensiveConfig(")
    print("       tpr_architecture_method=TPRArchitectureMethod.SMOLENSKY_ORIGINAL,")
    print("       binding_operation_method=BindingOperationMethod.TENSOR_PRODUCT,")
    print("       learning_mechanism=LearningMechanism.HEBBIAN_LEARNING")
    print("   )")
    print()
    print("🔍 VALIDATE YOUR CONFIG:")
    print("   warnings = validate_tpr_config(config)")
    print("   if warnings:")
    print("       for warning in warnings:")
    print("           print(warning)")


if __name__ == "__main__":
    print_tpr_solutions_summary()