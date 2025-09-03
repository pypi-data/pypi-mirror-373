"""
🏗️ Compositional Semantics - Semantic Data Structures Module
===========================================================


Author: Benedict Chen (benedict@benedictchen.com)
Based on: Smolensky (1990) "Tensor Product Variable Binding and the Representation of Symbolic Structures"

🎯 MODULE PURPOSE:
=================
Core data structures for compositional semantic representation.
Defines semantic types, frames, roles, and concepts used in TPB semantics.

🔬 RESEARCH FOUNDATION:
======================
Implements semantic structures based on Smolensky (1990):
- SemanticType: Enumeration of semantic structure types
- SemanticFrame: Role-filler frame representations 
- ConceptualRole: Thematic roles with constraints
- ConceptualSpace: Vector space for concept representations
- SemanticRole: Basic role definitions
- SemanticConcept: Complete concept definitions with features

This module contains the foundational data structures, split from the
1010-line monolith for clean semantic architecture separation.
"""

import numpy as np
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum


class SemanticType(Enum):
    """Types of semantic structures"""
    ENTITY = "entity"
    PREDICATE = "predicate" 
    PROPOSITION = "proposition"
    FUNCTION = "function"
    QUANTIFIER = "quantifier"
    OPERATOR = "operator"
    MODIFIER = "modifier"
    RELATION = "relation"


@dataclass
class SemanticFrame:
    """Represents a semantic frame with roles and fillers"""
    frame_type: str
    core_roles: Dict[str, Any]
    optional_roles: Dict[str, Any] = field(default_factory=dict)
    frame_constraints: Dict[str, Any] = field(default_factory=dict)
    semantic_type: SemanticType = SemanticType.PROPOSITION
    

@dataclass
class ConceptualRole:
    """Represents a conceptual role in semantic binding"""
    name: str
    semantic_constraints: Set[str] = field(default_factory=set)
    selectional_restrictions: Set[str] = field(default_factory=set)
    theta_role: Optional[str] = None  # Thematic role (agent, theme, goal, etc.)
    

class ConceptualSpace:
    """Conceptual space for semantic representations"""
    
    def __init__(self, vector_dim: int):
        self.vector_dim = vector_dim
        self.concepts: Dict[str, np.ndarray] = {}
    
    def add_concept(self, name: str, vector: np.ndarray):
        """Add concept to the space"""
        self.concepts[name] = vector
    
    def get_concept(self, name: str) -> Optional[np.ndarray]:
        """Get concept vector by name"""
        return self.concepts.get(name)


class SemanticRole:
    """Semantic role in compositional semantics"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.constraints: Set[str] = set()


@dataclass  
class SemanticConcept:
    """Represents a semantic concept"""
    name: str
    concept_type: SemanticType
    semantic_features: Set[str] = field(default_factory=set)
    conceptual_roles: List[str] = field(default_factory=list)
    inheritance_hierarchy: List[str] = field(default_factory=list)


# Export the semantic structures
__all__ = [
    'SemanticType',
    'SemanticFrame', 
    'ConceptualRole',
    'ConceptualSpace',
    'SemanticRole',
    'SemanticConcept'
]


if __name__ == "__main__":
    print("🏗️ Compositional Semantics - Semantic Data Structures Module")
    print("=" * 63)
    print("📊 MODULE CONTENTS:")
    print("  • SemanticType - Enumeration of semantic structure types")
    print("  • SemanticFrame - Role-filler frame representations")
    print("  • ConceptualRole - Thematic roles with semantic constraints") 
    print("  • ConceptualSpace - Vector space for concept representations")
    print("  • SemanticRole - Basic semantic role definitions")
    print("  • SemanticConcept - Complete concept definitions with features")
    print("")
    print("✅ Semantic data structures module loaded successfully!")
    print("🔬 Essential data structures for compositional semantic representation!")