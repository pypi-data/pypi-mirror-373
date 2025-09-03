"""
🌌 Vector Spaces for Tensor Product Binding
===========================================

Implementation of vector space management for tensor product binding systems.
Handles role and filler vector spaces, orthogonality constraints, and 
dimensional analysis.

Key Features:
- Orthogonal vector space construction
- Random vector generation with constraints
- Vector space analysis and validation
- Efficient storage and retrieval

Author: Benedict Chen (benedict@benedictchen.com)
Based on: Smolensky (1990) vector space theory for TPB
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import warnings


class VectorSpaceType(Enum):
    """Types of vector spaces in TPB"""
    ROLE_SPACE = "role_space"
    FILLER_SPACE = "filler_space"  
    BINDING_SPACE = "binding_space"
    SUPERPOSITION_SPACE = "superposition_space"


@dataclass
class SymbolicVector:
    """
    A symbolic vector with semantic meaning in TPB system.
    
    Attributes
    ----------
    name : str
        Symbolic name/identifier
    vector : np.ndarray
        Vector representation
    space_type : VectorSpaceType
        Which vector space this belongs to
    semantic_info : dict
        Additional semantic metadata
    """
    name: str
    vector: np.ndarray
    space_type: VectorSpaceType
    semantic_info: Optional[Dict] = None
    
    def __post_init__(self):
        if self.semantic_info is None:
            self.semantic_info = {}
    
    @property
    def dimension(self) -> int:
        """Get vector dimension"""
        return len(self.vector)
    
    @property
    def norm(self) -> float:
        """Get vector norm"""
        return np.linalg.norm(self.vector)
    
    def normalize(self) -> 'SymbolicVector':
        """Return normalized copy"""
        norm = self.norm
        if norm > 0:
            normalized_vector = self.vector / norm
        else:
            normalized_vector = self.vector.copy()
        
        return SymbolicVector(
            name=self.name,
            vector=normalized_vector,
            space_type=self.space_type,
            semantic_info=self.semantic_info.copy()
        )
    
    def similarity(self, other: 'SymbolicVector') -> float:
        """Compute cosine similarity with another symbolic vector"""
        if len(self.vector) != len(other.vector):
            raise ValueError("Vectors must have same dimension")
        
        norm_self = self.norm
        norm_other = other.norm
        
        if norm_self == 0 or norm_other == 0:
            return 0.0
        
        return np.dot(self.vector, other.vector) / (norm_self * norm_other)


class VectorSpace:
    """
    🌌 Vector Space Management for TPB
    
    Manages collections of vectors within specific semantic spaces,
    ensuring orthogonality constraints and providing efficient
    storage and retrieval.
    
    Parameters
    ----------
    dimension : int
        Dimension of vectors in this space
    space_type : VectorSpaceType
        Type of vector space
    orthogonal_constraint : bool, default=False
        Whether vectors should be orthogonal
    normalize_vectors : bool, default=True
        Whether to normalize vectors upon creation
    max_capacity : int, optional
        Maximum number of vectors in space
    """
    
    def __init__(self,
                 dimension: int,
                 space_type: VectorSpaceType,
                 orthogonal_constraint: bool = False,
                 normalize_vectors: bool = True,
                 max_capacity: Optional[int] = None):
        
        self.dimension = dimension
        self.space_type = space_type
        self.orthogonal_constraint = orthogonal_constraint
        self.normalize_vectors = normalize_vectors
        self.max_capacity = max_capacity
        
        # Storage for vectors
        self.vectors: Dict[str, SymbolicVector] = {}
        self.vector_matrix: Optional[np.ndarray] = None  # For efficient operations
        self._matrix_needs_update = False
        
        # Statistics
        self.creation_stats = {
            'vectors_created': 0,
            'orthogonality_violations': 0,
            'capacity_warnings': 0
        }
    
    def add_vector(self, 
                   name: str, 
                   vector: Optional[np.ndarray] = None,
                   semantic_info: Optional[Dict] = None) -> SymbolicVector:
        """
        Add a vector to the space.
        
        Parameters
        ----------
        name : str
            Name for the vector
        vector : np.ndarray, optional
            Vector data (generates random if None)
        semantic_info : dict, optional
            Semantic metadata
            
        Returns
        -------
        SymbolicVector
            The created symbolic vector
        """
        if name in self.vectors:
            return self.vectors[name]
        
        # Check capacity
        if self.max_capacity and len(self.vectors) >= self.max_capacity:
            self.creation_stats['capacity_warnings'] += 1
            warnings.warn(f"Vector space at capacity ({self.max_capacity})")
        
        # Generate or validate vector
        if vector is None:
            vector = self._generate_vector(name)
        else:
            if len(vector) != self.dimension:
                raise ValueError(f"Vector dimension {len(vector)} doesn't match space dimension {self.dimension}")
        
        # Apply constraints
        if self.orthogonal_constraint:
            vector = self._orthogonalize_vector(vector, name)
        
        if self.normalize_vectors:
            norm = np.linalg.norm(vector)
            if norm > 0:
                vector = vector / norm
        
        # Create symbolic vector
        symbolic_vector = SymbolicVector(
            name=name,
            vector=vector,
            space_type=self.space_type,
            semantic_info=semantic_info or {}
        )
        
        # Store vector
        self.vectors[name] = symbolic_vector
        self._matrix_needs_update = True
        self.creation_stats['vectors_created'] += 1
        
        return symbolic_vector
    
    def _generate_vector(self, name: str) -> np.ndarray:
        """Generate a random vector for the space"""
        # Use name as seed for reproducible vectors
        np.random.seed(hash(name) % 2**32)
        vector = np.random.randn(self.dimension)
        np.random.seed()  # Reset seed
        return vector
    
    def _orthogonalize_vector(self, vector: np.ndarray, name: str) -> np.ndarray:
        """Orthogonalize vector against existing vectors in space"""
        if not self.vectors:
            return vector  # First vector can be anything
        
        # Get existing vectors
        existing_vectors = np.array([v.vector for v in self.vectors.values()])
        
        # Gram-Schmidt orthogonalization
        orthogonal_vector = vector.copy()
        
        for existing_vector in existing_vectors:
            # Project onto existing vector
            projection = np.dot(orthogonal_vector, existing_vector) / np.dot(existing_vector, existing_vector)
            orthogonal_vector = orthogonal_vector - projection * existing_vector
        
        # Check if orthogonalization was successful
        orthogonal_norm = np.linalg.norm(orthogonal_vector)
        if orthogonal_norm < 1e-10:
            self.creation_stats['orthogonality_violations'] += 1
            warnings.warn(f"Could not create orthogonal vector for '{name}' - space may be full")
            # Return random vector as fallback
            return np.random.randn(self.dimension)
        
        return orthogonal_vector
    
    def get_vector(self, name: str) -> Optional[SymbolicVector]:
        """Retrieve a vector by name"""
        return self.vectors.get(name)
    
    def remove_vector(self, name: str) -> bool:
        """Remove a vector from the space"""
        if name in self.vectors:
            del self.vectors[name]
            self._matrix_needs_update = True
            return True
        return False
    
    def find_similar_vectors(self, 
                           query_vector: np.ndarray, 
                           top_k: int = 5,
                           min_similarity: float = 0.1) -> List[Tuple[str, float]]:
        """
        Find vectors similar to query vector.
        
        Parameters
        ----------
        query_vector : np.ndarray
            Vector to find similarities for
        top_k : int
            Number of top matches to return
        min_similarity : float
            Minimum similarity threshold
            
        Returns
        -------
        List[Tuple[str, float]]
            List of (name, similarity) pairs
        """
        if len(query_vector) != self.dimension:
            raise ValueError("Query vector dimension mismatch")
        
        similarities = []
        query_norm = np.linalg.norm(query_vector)
        
        if query_norm == 0:
            return []
        
        for name, symbolic_vector in self.vectors.items():
            similarity = np.dot(query_vector, symbolic_vector.vector) / (query_norm * symbolic_vector.norm)
            if similarity >= min_similarity:
                similarities.append((name, similarity))
        
        # Sort by similarity (descending) and return top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def get_vector_matrix(self) -> np.ndarray:
        """Get matrix of all vectors for efficient operations"""
        if self._matrix_needs_update or self.vector_matrix is None:
            if self.vectors:
                self.vector_matrix = np.array([v.vector for v in self.vectors.values()])
            else:
                self.vector_matrix = np.empty((0, self.dimension))
            self._matrix_needs_update = False
        
        return self.vector_matrix
    
    def analyze_space(self) -> Dict:
        """Analyze properties of the vector space"""
        if not self.vectors:
            return {'empty_space': True}
        
        vectors_matrix = self.get_vector_matrix()
        
        # Basic statistics
        norms = [v.norm for v in self.vectors.values()]
        mean_norm = np.mean(norms)
        std_norm = np.std(norms)
        
        # Pairwise similarities
        n_vectors = len(self.vectors)
        similarities = []
        
        for i, v1 in enumerate(self.vectors.values()):
            for j, v2 in enumerate(list(self.vectors.values())[i+1:], i+1):
                sim = v1.similarity(v2)
                similarities.append(sim)
        
        # Orthogonality analysis
        if similarities:
            mean_similarity = np.mean(similarities)
            max_similarity = np.max(similarities)
            min_similarity = np.min(similarities)
        else:
            mean_similarity = max_similarity = min_similarity = 0.0
        
        # Effective dimensionality (using SVD)
        if n_vectors > 1:
            _, s, _ = np.linalg.svd(vectors_matrix, full_matrices=False)
            # Effective rank using 1% threshold
            effective_rank = np.sum(s / s[0] > 0.01) if s[0] > 0 else 0
        else:
            effective_rank = n_vectors
        
        return {
            'num_vectors': n_vectors,
            'space_dimension': self.dimension,
            'space_type': self.space_type.value,
            'orthogonal_constraint': self.orthogonal_constraint,
            'mean_norm': mean_norm,
            'std_norm': std_norm,
            'mean_similarity': mean_similarity,
            'max_similarity': max_similarity,
            'min_similarity': min_similarity,
            'effective_dimensionality': effective_rank,
            'capacity_utilization': len(self.vectors) / self.max_capacity if self.max_capacity else None,
            'creation_stats': self.creation_stats.copy()
        }
    
    def clear(self):
        """Clear all vectors from the space"""
        self.vectors.clear()
        self.vector_matrix = None
        self._matrix_needs_update = False
    
    def __len__(self) -> int:
        """Number of vectors in space"""
        return len(self.vectors)
    
    def __contains__(self, name: str) -> bool:
        """Check if vector name exists in space"""
        return name in self.vectors
    
    def __iter__(self):
        """Iterate over vector names"""
        return iter(self.vectors)
    
    def items(self):
        """Iterate over (name, vector) pairs"""
        return self.vectors.items()


class MultiVectorSpace:
    """
    🌐 Multiple Vector Space Manager
    
    Manages multiple vector spaces for different types of vectors
    (roles, fillers, etc.) in a tensor product binding system.
    """
    
    def __init__(self, dimension: int):
        self.dimension = dimension
        self.spaces: Dict[VectorSpaceType, VectorSpace] = {}
        
        # Create default spaces
        self._create_default_spaces()
    
    def _create_default_spaces(self):
        """Create default vector spaces"""
        # Role space (typically orthogonal for clean binding)
        self.spaces[VectorSpaceType.ROLE_SPACE] = VectorSpace(
            dimension=self.dimension,
            space_type=VectorSpaceType.ROLE_SPACE,
            orthogonal_constraint=True,
            normalize_vectors=True
        )
        
        # Filler space (can be non-orthogonal for richer semantics)
        self.spaces[VectorSpaceType.FILLER_SPACE] = VectorSpace(
            dimension=self.dimension,
            space_type=VectorSpaceType.FILLER_SPACE,
            orthogonal_constraint=False,
            normalize_vectors=True
        )
        
        # Binding space (for bound vectors)
        self.spaces[VectorSpaceType.BINDING_SPACE] = VectorSpace(
            dimension=self.dimension * self.dimension,  # Outer product dimension
            space_type=VectorSpaceType.BINDING_SPACE,
            orthogonal_constraint=False,
            normalize_vectors=True
        )
    
    def get_space(self, space_type: VectorSpaceType) -> VectorSpace:
        """Get a specific vector space"""
        if space_type not in self.spaces:
            raise ValueError(f"Space type {space_type} not found")
        return self.spaces[space_type]
    
    def add_custom_space(self, 
                        space_type: VectorSpaceType,
                        **space_kwargs) -> VectorSpace:
        """Add a custom vector space"""
        space = VectorSpace(
            dimension=self.dimension,
            space_type=space_type,
            **space_kwargs
        )
        self.spaces[space_type] = space
        return space
    
    def analyze_all_spaces(self) -> Dict[str, Dict]:
        """Analyze all vector spaces"""
        return {space_type.value: space.analyze_space() 
                for space_type, space in self.spaces.items()}
    
    def clear_all_spaces(self):
        """Clear all vector spaces"""
        for space in self.spaces.values():
            space.clear()