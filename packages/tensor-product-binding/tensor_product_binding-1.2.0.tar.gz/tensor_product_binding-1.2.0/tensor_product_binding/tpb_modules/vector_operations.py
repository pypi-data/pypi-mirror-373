"""
Vector Operations for Tensor Product Binding

This module contains the TPBVector class and related vector operations
used throughout the tensor product binding system.
"""

import numpy as np
from typing import Union, Optional


class TPBVector:
    """Tensor Product Binding Vector with operations"""
    
    def __init__(self, data: np.ndarray):
        """Initialize TPB vector with data"""
        if not isinstance(data, np.ndarray):
            data = np.array(data)
        self.data = data.astype(float)
    
    @property
    def dimension(self) -> int:
        """Get vector dimension"""
        return len(self.data)
    
    def magnitude(self) -> float:
        """Get vector magnitude/norm"""
        return np.linalg.norm(self.data)
    
    def normalize(self) -> 'TPBVector':
        """Return normalized copy of vector"""
        norm = self.magnitude()
        if norm > 0:
            return TPBVector(self.data / norm)
        return TPBVector(self.data.copy())
    
    def dot(self, other: 'TPBVector') -> float:
        """Compute dot product with another vector"""
        return np.dot(self.data, other.data)
    
    def cosine_similarity(self, other: 'TPBVector') -> float:
        """Compute cosine similarity with another vector"""
        norm1 = self.magnitude()
        norm2 = other.magnitude()
        if norm1 == 0 or norm2 == 0:
            return 0.0
        similarity = self.dot(other) / (norm1 * norm2)
        # Return absolute value for tensor product binding - orientation invariant
        return abs(similarity)
    
    def __add__(self, other: 'TPBVector') -> 'TPBVector':
        """Vector addition"""
        return TPBVector(self.data + other.data)
    
    def __sub__(self, other: 'TPBVector') -> 'TPBVector':
        """Vector subtraction"""
        return TPBVector(self.data - other.data)
    
    def __mul__(self, scalar: float) -> 'TPBVector':
        """Scalar multiplication"""
        return TPBVector(self.data * scalar)
    
    def __rmul__(self, scalar: float) -> 'TPBVector':
        """Right scalar multiplication"""
        return self.__mul__(scalar)
    
    def __repr__(self) -> str:
        return f"TPBVector({self.data})"


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Calculate cosine similarity between two numpy arrays"""
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
        
    return np.dot(vec1, vec2) / (norm1 * norm2)


def create_normalized_vector(size: int, random_state: Optional[int] = None) -> np.ndarray:
    """Create a normalized random vector of given size"""
    if random_state is not None:
        rng = np.random.RandomState(random_state)
        vector = rng.randn(size)
    else:
        vector = np.random.randn(size)
    
    norm = np.linalg.norm(vector)
    if norm > 0:
        vector = vector / norm
    return vector