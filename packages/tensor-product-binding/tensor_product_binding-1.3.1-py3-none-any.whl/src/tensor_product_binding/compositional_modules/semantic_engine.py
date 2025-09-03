"""
🧠 Compositional Semantics - Main Semantic Engine Module
=======================================================


Author: Benedict Chen (benedict@benedictchen.com)
Based on: Smolensky (1990) "Tensor Product Variable Binding and the Representation of Symbolic Structures"

🎯 MODULE PURPOSE:
=================
Main compositional semantics engine implementing tensor product binding for
structured semantic representation and compositional meaning construction.

🔬 RESEARCH FOUNDATION:
======================
Implements the core CompositionalSemantics class based on Smolensky (1990):
- Compositional meaning construction through tensor product binding
- Semantic frame-based role-filler binding for structured representation
- Thematic role assignment following linguistic theory
- Systematic compositionality with productivity and recursion

This module contains the main semantic engine class, split from the
1010-line monolith for focused semantic processing functionality.
"""

import numpy as np
from typing import Dict, Any, List, Optional, Union, Tuple, Set
from .semantic_structures import (
    SemanticType, SemanticFrame, ConceptualRole, 
    ConceptualSpace, SemanticRole, SemanticConcept
)

# Import TYPE_CHECKING to allow forward references without circular imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..tensor_product_binding import TensorProductBinding, BindingPair, TPBVector
    from ..symbolic_structures import SymbolicStructureEncoder, SymbolicStructure, StructureType, Role, Filler


class CompositionalSemantics:
    """
    Compositional Semantics Engine using Tensor Product Variable Binding
    
    Implements semantic composition following principles of:
    - Frege's principle of compositionality
    - Montague grammar semantic composition 
    - Tensor product binding for structured representations
    - Thematic role assignment and binding
    """
    
    def __init__(self,
                 vector_dim: int = 512,
                 concept_dim: Optional[int] = None,
                 role_dim: Optional[int] = None,
                 semantic_lexicon: Optional[Dict[str, SemanticConcept]] = None,
                 conceptual_roles: Optional[Dict[str, ConceptualRole]] = None,
                 semantic_frames: Optional[Dict[str, SemanticFrame]] = None,
                 random_seed: Optional[int] = None):
        """
        Initialize Compositional Semantics Engine
        
        Args:
            vector_dim: Dimensionality of vector representations
            semantic_lexicon: Dictionary of semantic concepts
            conceptual_roles: Dictionary of conceptual roles
            semantic_frames: Dictionary of semantic frames
            random_seed: Random seed for reproducibility
        """
        self.vector_dim = vector_dim
        self.concept_dim = concept_dim or vector_dim
        self.role_dim = role_dim or vector_dim
        
        if random_seed is not None:
            np.random.seed(random_seed)
        
        # Initialize core components - local imports to avoid circular dependencies
        from ..symbolic_structures import SymbolicStructureEncoder
        from ..tensor_product_binding import TensorProductBinding
        
        self.structure_encoder = SymbolicStructureEncoder(
            vector_dim=vector_dim, 
            random_seed=random_seed
        )
        self.binder = TensorProductBinding(role_dimension=vector_dim, filler_dimension=vector_dim)
        
        # Create conceptual space
        self.conceptual_space = ConceptualSpace(vector_dim=self.concept_dim)
        
        # Semantic knowledge bases
        self.semantic_lexicon = semantic_lexicon or {}
        self.conceptual_roles = conceptual_roles or {}
        self.semantic_frames = semantic_frames or {}
        
        # Initialize standard semantic roles and concepts
        self._initialize_semantic_primitives()
        
        # Composition rules and operators
        self.composition_rules = {}
        self._initialize_composition_rules()
        
        # Storage for composed meanings
        self.composed_meanings = {}  # name -> vector
        
        # Additional properties expected by tests
        self.concepts = {}
        self.semantic_roles = {}
        
    def _initialize_semantic_primitives(self):
        """Initialize basic semantic roles and concepts"""
        
        # Standard thematic roles
        thematic_roles = [
            ("AGENT", "entity that performs action", {"animate", "volitional"}),
            ("THEME", "entity affected by action", {"concrete", "abstract"}),
            ("PATIENT", "entity undergoing change", {"concrete", "abstract"}),
            ("EXPERIENCER", "entity experiencing state", {"animate", "conscious"}),
            ("GOAL", "endpoint or target", {"location", "entity", "state"}),
            ("SOURCE", "starting point", {"location", "entity", "state"}),
            ("INSTRUMENT", "means of action", {"tool", "method"}),
            ("LOCATION", "spatial position", {"spatial", "temporal"}),
            ("TIME", "temporal position", {"temporal"}),
            ("MANNER", "way action is performed", {"adverbial"}),
            ("CAUSE", "reason for event", {"event", "state"}),
            ("PURPOSE", "intended goal", {"intention", "goal"}),
        ]
        
        for role_name, description, constraints in thematic_roles:
            if role_name not in self.structure_encoder.role_vocabulary:
                self.structure_encoder.add_role(
                    role_name, 
                    semantic_type="thematic",
                    constraints={"description": description, "selectional": constraints}
                )
            
            # Add to conceptual roles
            self.conceptual_roles[role_name] = ConceptualRole(
                name=role_name,
                selectional_restrictions=constraints,
                theta_role=role_name.lower()
            )
        
        # Add standard concepts with semantic features
        basic_concepts = [
            ("PERSON", SemanticType.ENTITY, {"animate", "human", "concrete"}),
            ("ANIMAL", SemanticType.ENTITY, {"animate", "non-human", "concrete"}),
            ("OBJECT", SemanticType.ENTITY, {"inanimate", "concrete", "physical"}),
            ("PLACE", SemanticType.ENTITY, {"location", "spatial"}),
            ("TIME", SemanticType.ENTITY, {"temporal"}),
            ("ACTION", SemanticType.PREDICATE, {"dynamic", "eventive"}),
            ("STATE", SemanticType.PREDICATE, {"static", "stative"}),
            ("PROPERTY", SemanticType.MODIFIER, {"descriptive", "attributive"}),
        ]
        
        for concept_name, concept_type, features in basic_concepts:
            if concept_name not in self.semantic_lexicon:
                self.semantic_lexicon[concept_name] = SemanticConcept(
                    name=concept_name,
                    concept_type=concept_type,
                    semantic_features=features
                )
                
                # Create vector for the concept
                concept_vector = np.random.randn(self.concept_dim)
                concept_vector = concept_vector / np.linalg.norm(concept_vector)
                self.conceptual_space.add_concept(concept_name, concept_vector)

    def _initialize_composition_rules(self):
        """Initialize semantic composition rules"""
        
        self.composition_rules = {
            # Functional application: f(x) -> f ⊗ x
            "function_application": self._function_application,
            
            # Predicate application: P(x) -> P ⊗ x  
            "predicate_application": self._predicate_application,
            
            # Modification: ADJ N -> ADJ ⊗ N
            "modification": self._modification,
            
            # Quantification: QUANT N -> QUANT ⊗ N
            "quantification": self._quantification,
            
            # Conjunction: X AND Y -> X ⊕ Y
            "conjunction": self._conjunction,
            
            # Disjunction: X OR Y -> X ⊕ Y (different weight)
            "disjunction": self._disjunction,
            
            # Negation: NOT X -> ¬X
            "negation": self._negation,
            
            # Implication: X IMPLIES Y -> X → Y
            "implication": self._implication,
        }

    def add_semantic_concept(self, 
                           concept_name: str, 
                           concept_type: SemanticType, 
                           features: Optional[Set[str]] = None,
                           vector: Optional[np.ndarray] = None,
                           conceptual_roles: Optional[List[str]] = None,
                           inheritance: Optional[List[str]] = None) -> str:
        """
        Add a new semantic concept to the lexicon
        
        Args:
            concept_name: Name of the concept
            concept_type: Type of semantic concept
            features: Set of semantic features
            vector: Optional pre-defined vector representation
            conceptual_roles: List of roles this concept can fill
            inheritance: Inheritance hierarchy
            
        Returns:
            The concept name (for chaining)
        """
        if features is None:
            features = set()
        if conceptual_roles is None:
            conceptual_roles = []
        if inheritance is None:
            inheritance = []
        
        # Create semantic concept
        concept = SemanticConcept(
            name=concept_name,
            concept_type=concept_type,
            semantic_features=features,
            conceptual_roles=conceptual_roles,
            inheritance_hierarchy=inheritance
        )
        
        self.semantic_lexicon[concept_name] = concept
        
        # Create or use provided vector
        if vector is None:
            vector = np.random.randn(self.concept_dim)
            vector = vector / np.linalg.norm(vector)
        
        self.conceptual_space.add_concept(concept_name, vector)
        
        return concept_name

    def create_concept(self, name: str, features: Optional[List[str]] = None) -> str:
        """Create a concept with basic features"""
        if features is None:
            features = []
        feature_set = set(features)
        
        self.add_semantic_concept(name, SemanticType.ENTITY, feature_set)
        return name

    def get_concept_vector(self, name: str) -> "TPBVector":
        """Get concept as TPBVector"""
        vector_data = self.conceptual_space.get_concept(name)
        if vector_data is None:
            return None
        
        from ..core.binding_operations import TPBVector
        return TPBVector(data=vector_data, filler=name)

    def add_semantic_role(self, role: SemanticRole):
        """Add a semantic role"""
        self.semantic_roles[role.name] = role

    def compose_meaning(self, predicate: str, role_bindings: List[Tuple[str, str]]) -> "TPBVector":
        """
        Compose meaning from predicate and role-filler bindings
        
        Args:
            predicate: Name of predicate
            role_bindings: List of (role, filler) tuples
            
        Returns:
            Composed meaning vector
        """
        # Get predicate vector
        pred_vector = self.get_concept_vector(predicate)
        if pred_vector is None:
            return None
        
        # Bind each role-filler pair
        bound_vectors = [pred_vector]
        
        for role, filler in role_bindings:
            role_vec = self.structure_encoder.get_role_vector(role)
            filler_vec = self.get_concept_vector(filler)
            
            if role_vec is not None and filler_vec is not None:
                bound = self.binder.bind(role_vec, filler_vec)
                bound_vectors.append(bound)
        
        # Compose all bound vectors
        if len(bound_vectors) == 1:
            return bound_vectors[0]
        else:
            return self.binder.compose(bound_vectors)

    def extract_role_filler(self, composition: "TPBVector", role: str) -> "TPBVector":
        """
        Extract filler for a given role from a composed meaning
        
        Args:
            composition: Composed meaning vector
            role: Role name to extract
            
        Returns:
            Extracted filler vector
        """
        role_vector = self.structure_encoder.get_role_vector(role)
        if role_vector is None:
            return None
        
        # Unbind to extract the filler
        return self.binder.unbind(composition, role_vector)

    # Composition rule implementations (abbreviated for space)
    def _function_application(self, function_vec: np.ndarray, argument_vec: np.ndarray) -> np.ndarray:
        """Function application composition rule"""
        return np.outer(function_vec, argument_vec).flatten()

    def _predicate_application(self, predicate_vec: np.ndarray, entity_vec: np.ndarray) -> np.ndarray:
        """Predicate application composition rule"""
        # Use tensor product for structured binding
        return np.outer(predicate_vec, entity_vec).flatten()

    def _modification(self, modifier_vec: np.ndarray, modified_vec: np.ndarray) -> np.ndarray:
        """Modification composition rule"""
        # Weighted combination with modifier bias
        alpha = 0.7  # Modifier strength
        return alpha * modifier_vec + (1 - alpha) * modified_vec

    def _quantification(self, quantifier_vec: np.ndarray, 
                       noun_vec: np.ndarray, scope_vec: Optional[np.ndarray] = None) -> np.ndarray:
        """Quantification composition rule"""
        if scope_vec is None:
            return np.outer(quantifier_vec, noun_vec).flatten()
        else:
            # Complex quantification with scope
            quantified = np.outer(quantifier_vec, noun_vec).flatten()
            return np.outer(quantified, scope_vec).flatten()

    def _conjunction(self, left_vec: np.ndarray, right_vec: np.ndarray) -> np.ndarray:
        """Conjunction composition rule"""
        # Vector addition with normalization
        conjoined = left_vec + right_vec
        norm = np.linalg.norm(conjoined)
        return conjoined / norm if norm > 0 else conjoined

    def _disjunction(self, left_vec: np.ndarray, right_vec: np.ndarray) -> np.ndarray:
        """Disjunction composition rule"""
        # Weighted average
        disjoined = 0.5 * (left_vec + right_vec)
        norm = np.linalg.norm(disjoined)
        return disjoined / norm if norm > 0 else disjoined

    def _negation(self, proposition_vec: np.ndarray) -> np.ndarray:
        """Negation composition rule"""
        # Simple negation via subtraction from null vector
        null_vec = np.zeros_like(proposition_vec)
        negated = null_vec - proposition_vec
        norm = np.linalg.norm(negated)
        return negated / norm if norm > 0 else negated

    def _implication(self, antecedent_vec: np.ndarray, consequent_vec: np.ndarray) -> np.ndarray:
        """Implication composition rule"""
        # Create implication vector
        return np.outer(antecedent_vec, consequent_vec).flatten()

    def similarity(self, meaning1: np.ndarray, meaning2: np.ndarray) -> float:
        """Compute similarity between two meaning vectors"""
        return np.dot(meaning1, meaning2) / (np.linalg.norm(meaning1) * np.linalg.norm(meaning2))

    def entails(self, meaning1: np.ndarray, meaning2: np.ndarray, threshold: float = 0.8) -> bool:
        """Check if meaning1 entails meaning2"""
        # Simple entailment check via similarity threshold
        return self.similarity(meaning1, meaning2) >= threshold

    def encode_semantic_concept(self, concept_name: str) -> Optional[np.ndarray]:
        """Encode a semantic concept as a vector"""
        return self.conceptual_space.get_concept(concept_name)

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the semantic system"""
        return {
            "concepts": len(self.semantic_lexicon),
            "conceptual_roles": len(self.conceptual_roles),
            "semantic_frames": len(self.semantic_frames),
            "composition_rules": len(self.composition_rules),
            "vector_dimension": self.vector_dim,
            "concept_dimension": self.concept_dim,
            "role_dimension": self.role_dim,
            "composed_meanings": len(self.composed_meanings)
        }

    # Include advanced composition methods
    def compose_predicate_argument(self, 
                                 predicate: str,
                                 argument: str,
                                 thematic_role: str = "THEME") -> np.ndarray:
        """Compose predicate with argument using thematic role binding"""
        from .advanced_composition import AdvancedCompositionMixin
        mixin = AdvancedCompositionMixin()
        # Copy necessary attributes
        for attr in ['encode_semantic_concept', 'structure_encoder', 'vector_dim']:
            setattr(mixin, attr, getattr(self, attr))
        return mixin.compose_predicate_argument(predicate, argument, thematic_role)

    def compose_with_frame(self, frame_name: str, role_bindings: Dict[str, str]) -> np.ndarray:
        """Compose meaning using a semantic frame"""
        from .advanced_composition import AdvancedCompositionMixin
        mixin = AdvancedCompositionMixin()
        for attr in ['semantic_frames', 'encode_semantic_concept', 'structure_encoder', 'composed_meanings']:
            setattr(mixin, attr, getattr(self, attr))
        return mixin.compose_with_frame(frame_name, role_bindings)

    def compose_sentence(self, words: List[str], syntax_structure: Optional[str] = None) -> np.ndarray:
        """Compose sentence meaning from word sequence"""
        from .advanced_composition import AdvancedCompositionMixin
        mixin = AdvancedCompositionMixin()
        for attr in ['vector_dim', 'encode_semantic_concept']:
            setattr(mixin, attr, getattr(self, attr))
        return mixin.compose_sentence(words, syntax_structure)

    def compose_logical_form(self, logical_form: str) -> np.ndarray:
        """Compose logical form into semantic representation"""
        from .advanced_composition import AdvancedCompositionMixin
        mixin = AdvancedCompositionMixin()
        for attr in ['encode_semantic_concept', 'vector_dim']:
            setattr(mixin, attr, getattr(self, attr))
        return mixin.compose_logical_form(logical_form)

    def decompose_meaning(self, meaning_vector: np.ndarray, possible_roles: List[str]) -> Dict[str, np.ndarray]:
        """Decompose meaning vector into role-filler components"""
        from .advanced_composition import AdvancedCompositionMixin
        mixin = AdvancedCompositionMixin()
        setattr(mixin, 'structure_encoder', getattr(self, 'structure_encoder'))
        return mixin.decompose_meaning(meaning_vector, possible_roles)

    def create_semantic_lexicon_from_wordnet(self, concepts: List[str]) -> Dict[str, SemanticConcept]:
        """Create semantic lexicon from WordNet concepts"""
        from .advanced_composition import AdvancedCompositionMixin
        mixin = AdvancedCompositionMixin()
        for attr in ['concept_dim', 'conceptual_space']:
            setattr(mixin, attr, getattr(self, attr))
        return mixin.create_semantic_lexicon_from_wordnet(concepts)

    def get_semantic_field(self, concept: str, similarity_threshold: float = 0.7) -> List[str]:
        """Get semantic field (similar concepts) for a given concept"""
        from .advanced_composition import AdvancedCompositionMixin
        mixin = AdvancedCompositionMixin()
        for attr in ['encode_semantic_concept', 'semantic_lexicon', 'similarity']:
            setattr(mixin, attr, getattr(self, attr))
        return mixin.get_semantic_field(concept, similarity_threshold)


# Export the main semantic engine
__all__ = ['CompositionalSemantics']


if __name__ == "__main__":
    print("🧠 Compositional Semantics - Main Semantic Engine Module")
    print("=" * 59)
    print("📊 MODULE CONTENTS:")
    print("  • CompositionalSemantics - Core semantic composition engine")
    print("  • Tensor product binding for structured semantic representation")
    print("  • Role-filler binding with thematic role assignment")
    print("  • Compositional meaning construction and decomposition")
    print("")
    print("✅ Semantic engine module loaded successfully!")
    print("🔬 Smolensky (1990) compositional semantics implementation!")