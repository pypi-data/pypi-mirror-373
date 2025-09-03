"""
🔧 Compositional Semantics - Utility Functions Module
===================================================


Author: Benedict Chen (benedict@benedictchen.com)
Based on: Smolensky (1990) "Tensor Product Variable Binding and the Representation of Symbolic Structures"

🎯 MODULE PURPOSE:
=================
Utility functions for compositional semantic processing.
Provides lexicon creation, frame definition, parsing, and analysis utilities.

🔬 RESEARCH FOUNDATION:
======================
Implements utility functions supporting Smolensky (1990) compositional semantics:
- Semantic lexicon creation from concept specifications
- Standard semantic frame definitions for common predicates
- Simple logical form parsing for compositional structures
- Semantic similarity matrix computation for concept analysis

This module contains the utility functions, split from the
1010-line monolith for clean functional separation.
"""

import numpy as np
from typing import Dict, List, Set, Tuple
from .semantic_structures import SemanticConcept, SemanticFrame, SemanticType

# Import TYPE_CHECKING to allow forward references without circular imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..compositional_semantics import CompositionalSemantics


def create_semantic_lexicon(concepts: List[Tuple[str, SemanticType, Set[str]]]) -> Dict[str, SemanticConcept]:
    """
    Create a semantic lexicon from concept specifications
    
    Args:
        concepts: List of (name, type, features) tuples
        
    Returns:
        Dictionary of semantic concepts
    """
    lexicon = {}
    
    for name, concept_type, features in concepts:
        lexicon[name] = SemanticConcept(
            name=name,
            concept_type=concept_type,
            semantic_features=features
        )
    
    return lexicon


def create_standard_semantic_frames() -> Dict[str, SemanticFrame]:
    """Create standard semantic frames for common predicates"""
    frames = {}
    
    # Transitive action frame
    frames["transitive_action"] = SemanticFrame(
        frame_type="transitive_action",
        core_roles={"AGENT": "animate", "THEME": "any"},
        optional_roles={"INSTRUMENT": "tool", "LOCATION": "spatial", "TIME": "temporal"}
    )
    
    # Intransitive action frame
    frames["intransitive_action"] = SemanticFrame(
        frame_type="intransitive_action",
        core_roles={"AGENT": "animate"},
        optional_roles={"MANNER": "adverbial", "LOCATION": "spatial", "TIME": "temporal"}
    )
    
    # State frame
    frames["state"] = SemanticFrame(
        frame_type="state",
        core_roles={"EXPERIENCER": "animate", "THEME": "property"},
        optional_roles={"DEGREE": "scalar", "TIME": "temporal"}
    )
    
    # Motion frame
    frames["motion"] = SemanticFrame(
        frame_type="motion",
        core_roles={"AGENT": "animate", "SOURCE": "location", "GOAL": "location"},
        optional_roles={"PATH": "trajectory", "MANNER": "adverbial"}
    )
    
    # Causation frame
    frames["causation"] = SemanticFrame(
        frame_type="causation", 
        core_roles={"CAUSE": "event", "EFFECT": "event"},
        optional_roles={"INSTRUMENT": "tool", "MANNER": "adverbial"}
    )
    
    return frames


def parse_simple_logical_form(logical_form: str) -> Tuple[str, List[str]]:
    """
    Parse simple logical form into predicate and arguments
    
    Args:
        logical_form: String like "loves(john, mary)" or "runs(john)"
        
    Returns:
        Tuple of (predicate, arguments_list)
    """
    if "(" not in logical_form or not logical_form.endswith(")"):
        return logical_form.strip(), []
    
    predicate = logical_form[:logical_form.index("(")].strip()
    args_str = logical_form[logical_form.index("(")+1:-1]
    
    if not args_str.strip():
        return predicate, []
    
    arguments = [arg.strip() for arg in args_str.split(",")]
    return predicate, arguments


def semantic_similarity_matrix(semantics: "CompositionalSemantics", 
                              concepts: List[str]) -> np.ndarray:
    """
    Create semantic similarity matrix for a set of concepts
    
    Args:
        semantics: CompositionalSemantics instance
        concepts: List of concept names
        
    Returns:
        Similarity matrix as numpy array
    """
    n = len(concepts)
    similarity_matrix = np.zeros((n, n))
    
    # Get all concept vectors
    vectors = []
    for concept in concepts:
        vector = semantics.encode_semantic_concept(concept)
        if vector is not None:
            vectors.append(vector)
        else:
            vectors.append(np.zeros(semantics.vector_dim))
    
    # Compute pairwise similarities
    for i in range(n):
        for j in range(n):
            if i == j:
                similarity_matrix[i, j] = 1.0
            else:
                similarity_matrix[i, j] = semantics.similarity(vectors[i], vectors[j])
    
    return similarity_matrix


# Export the utility functions
__all__ = [
    'create_semantic_lexicon',
    'create_standard_semantic_frames', 
    'parse_simple_logical_form',
    'semantic_similarity_matrix'
]


if __name__ == "__main__":
    print("🔧 Compositional Semantics - Utility Functions Module")
    print("=" * 56)
    print("📊 MODULE CONTENTS:")
    print("  • create_semantic_lexicon - Create lexicon from concept specifications")
    print("  • create_standard_semantic_frames - Standard semantic frames for predicates")
    print("  • parse_simple_logical_form - Parse logical forms into predicate and arguments") 
    print("  • semantic_similarity_matrix - Compute concept similarity matrices")
    print("")
    print("✅ Utility functions module loaded successfully!")
    print("🔬 Essential utilities for compositional semantic processing!")