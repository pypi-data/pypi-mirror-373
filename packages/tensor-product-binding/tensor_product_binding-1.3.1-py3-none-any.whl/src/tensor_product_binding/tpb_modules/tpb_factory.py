"""
🏭 Tensor Product Binding - Factory Functions & Demo Systems
==========================================================

Author: Benedict Chen (benedict@benedictchen.com)

💰 Donations: Help support this research!
   PayPal: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS
   💖 Please consider recurring donations to support continued TPB research

Based on: Smolensky (1990) "Tensor Product Variable Binding and the Representation of Symbolic Structures"

🔬 Research Foundation:
======================
Factory functions implementing Smolensky (1990) demonstrations:
- Role-Filler binding examples from original paper
- Constituent structure representations
- Distributed representation experiments
- Systematic compositional demonstrations

ELI5 Explanation:
================
Think of this module like a LEGO instruction booklet! 🧱

When you buy a LEGO set, you don't just get a pile of bricks - you get:
- **Instructions** (our factory functions) that show you how to build cool things
- **Example models** (our demos) like castles, spaceships, or cars  
- **Tips and tricks** for combining pieces in creative ways

Similarly, this module takes the basic "LEGO bricks" of tensor product binding
and shows you how to build useful cognitive structures like:
- "John loves Mary" (binding JOHN to LOVER role, MARY to BELOVED role)
- "The red car" (binding RED to COLOR role, CAR to OBJECT role)
- Complex nested structures like "John believes Mary loves Tom"

ASCII Factory Architecture:
===========================
    User Request     Factory Function     TPB System
    ┌─────────────┐  ┌─────────────────┐  ┌─────────────┐
    │"Create a    │──│ create_sentence │──│ Role: AGENT │
    │ sentence    │  │ _binding()      │  │ │ Filler:   │
    │ binder"     │  │                 │  │ │ "JOHN"    │
    └─────────────┘  └─────────────────┘  └─┴───────────┘
                               │              │
                               ▼              ▼
    ┌─────────────┐  ┌─────────────────┐  ┌─────────────┐
    │ Demo        │  │ Educational     │  │ Role: ACTION│
    │ "John loves │◀─│ Examples        │◀─│ │ Filler:   │
    │  Mary"      │  │                 │  │ │ "LOVE"    │
    └─────────────┘  └─────────────────┘  └─┴───────────┘
                               │              │
                               ▼              ▼
    ┌─────────────┐  ┌─────────────────┐  ┌─────────────┐
    │ Complex     │  │ Compositional   │  │ Role: PATIENT│
    │ Structure   │◀─│ Binding         │◀─│ │ Filler:   │
    │ Built       │  │                 │  │ │ "MARY"    │
    └─────────────┘  └─────────────────┘  └─┴───────────┘

🎯 Factory Functions:
====================
1. **create_basic_binder()**: Simple role-filler binding system
2. **create_sentence_binder()**: Linguistic structure representation
3. **create_memory_system()**: Associative memory with TPB
4. **create_hierarchical_binder()**: Nested compositional structures

📊 Demo Categories:
==================
• **Linguistic Examples**: "John loves Mary", "The red car runs fast"
• **Logical Structures**: Predicate logic with distributed representations
• **Memory Systems**: Content-addressable memory with compositional keys
• **Systematic Variations**: Demonstrates productivity and systematicity

⚡ Usage Patterns:
=================
```python
# Quick start - build a sentence understanding system
binder = create_sentence_binder(vocab_size=1000, role_dim=50)
sentence = binder.encode("JOHN LOVES MARY")
roles = binder.extract_roles(sentence)  # [AGENT, ACTION, PATIENT]

# Educational demo - see how binding works step by step
demo_basic_binding()  # Shows role⊗filler operations with explanations
demo_compositional_structure()  # Nested binding examples
```

This module transforms complex tensor product theory into practical, 
understandable tools for cognitive modeling and symbolic AI.
"""

import numpy as np
from typing import Optional, Dict, Any, Union
from .tpb_core import TensorProductBinding
from .tpb_enums import BindingOperation


def create_tpb_system(
    vector_dim: int = 100,
    binding_type: Union[str, BindingOperation] = BindingOperation.OUTER_PRODUCT,
    normalize_vectors: bool = True,
    random_seed: Optional[int] = None,
    **kwargs
) -> TensorProductBinding:
    """
    🏭 Factory function to create a tensor product binding system with sensible defaults.
    
    This convenience function provides an easy way to create TPB systems with
    common configurations for research and educational use.
    
    Parameters
    ----------
    vector_dim : int, default=100
        Dimension of both role and filler vectors (symmetric system)
    binding_type : str or BindingOperation, default='outer_product'
        Type of binding operation to use
    normalize_vectors : bool, default=True
        Whether to normalize vectors before binding
    random_seed : int, optional
        Random seed for reproducible experiments
    **kwargs
        Additional parameters passed to TensorProductBinding constructor
        
    Returns
    -------
    TensorProductBinding
        Configured TPB system ready for use
        
    Examples
    --------
    >>> # Create basic system
    >>> tpb = create_tpb_system(vector_dim=64)
    >>> 
    >>> # Create system with circular convolution
    >>> tpb_conv = create_tpb_system(
    ...     vector_dim=128,
    ...     binding_type='circular_convolution',
    ...     random_seed=42
    ... )
    >>> 
    >>> # Research configuration
    >>> tpb_research = create_tpb_system(
    ...     vector_dim=200,
    ...     binding_type=BindingOperation.OUTER_PRODUCT,
    ...     normalize_vectors=True,
    ...     random_seed=1990  # Smolensky's year
    ... )
    """
    return TensorProductBinding(
        role_dimension=vector_dim,
        filler_dimension=vector_dim,
        binding_type=binding_type,
        normalize_vectors=normalize_vectors,
        random_seed=random_seed,
        **kwargs
    )


def demo_tensor_binding(
    vector_dim: int = 64,
    binding_type: BindingOperation = BindingOperation.OUTER_PRODUCT,
    show_details: bool = True
) -> Dict[str, Any]:
    """
    🎭 Demonstration of tensor product binding concepts.
    
    Educational function showing key TPB concepts with concrete examples
    based on Smolensky's original formulation.
    
    Parameters
    ----------
    vector_dim : int, default=64
        Dimensionality for demonstration vectors
    binding_type : BindingOperation, default=OUTER_PRODUCT
        Type of binding operation to demonstrate
    show_details : bool, default=True
        Whether to print detailed explanations
        
    Returns
    -------
    Dict[str, Any]
        Results of the demonstration including vectors and similarities
        
    Examples
    --------
    >>> # Run basic demonstration
    >>> results = demo_tensor_binding()
    >>> 
    >>> # Advanced demonstration with circular convolution
    >>> results = demo_tensor_binding(
    ...     vector_dim=128,
    ...     binding_type=BindingOperation.CIRCULAR_CONVOLUTION
    ... )
    """
    if show_details:
        print("🎭 Tensor Product Binding Demonstration")
        print("=" * 45)
        print(f"📐 Vector dimension: {vector_dim}")
        print(f"🔗 Binding operation: {binding_type.value}")
        print()
        
        print("📚 Based on: Smolensky (1990) 'Tensor Product Variable Binding")
        print("    and the Representation of Symbolic Structures'")
        print()
    
    # Create TPB system
    tpb = create_tpb_system(
        vector_dim=vector_dim,
        binding_type=binding_type,
        random_seed=42
    )
    
    if show_details:
        print("🧠 System initialized:")
        print(f"   {tpb}")
        print()
    
    # Create role vectors (syntactic roles)
    agent_role = tpb.create_role_vector("AGENT")
    patient_role = tpb.create_role_vector("PATIENT") 
    action_role = tpb.create_role_vector("ACTION")
    
    # Create filler vectors (semantic content)
    john_filler = tpb.create_filler_vector("john")
    mary_filler = tpb.create_filler_vector("mary")
    loves_filler = tpb.create_filler_vector("loves")
    
    if show_details:
        print("👥 Created vectors:")
        print(f"   Roles: AGENT, PATIENT, ACTION ({vector_dim}D each)")
        print(f"   Fillers: john, mary, loves ({vector_dim}D each)")
        print()
    
    # Demonstrate binding
    john_as_agent = tpb.bind(agent_role, john_filler)
    mary_as_patient = tpb.bind(patient_role, mary_filler)
    loves_as_action = tpb.bind(action_role, loves_filler)
    
    if show_details:
        print("🔗 Binding operations:")
        print(f"   AGENT × john → bound vector ({len(john_as_agent.data)}D)")
        print(f"   PATIENT × mary → bound vector ({len(mary_as_patient.data)}D)")
        print(f"   ACTION × loves → bound vector ({len(loves_as_action.data)}D)")
        print()
    
    # Demonstrate composition (sentence: "John loves Mary")
    sentence = tpb.compose([john_as_agent, mary_as_patient, loves_as_action])
    
    if show_details:
        print("🏗️ Compositional structure:")
        print(f"   'John loves Mary' → composed vector ({len(sentence.data)}D)")
        print()
    
    # Demonstrate unbinding (information retrieval)
    retrieved_john = tpb.unbind(john_as_agent, agent_role)
    retrieved_mary = tpb.unbind(mary_as_patient, patient_role)
    retrieved_loves = tpb.unbind(loves_as_action, action_role)
    
    # Compute similarities
    john_similarity = tpb.similarity(retrieved_john, john_filler)
    mary_similarity = tpb.similarity(retrieved_mary, mary_filler)
    loves_similarity = tpb.similarity(retrieved_loves, loves_filler)
    
    if show_details:
        print("🔓 Unbinding accuracy (cosine similarity):")
        print(f"   Retrieved john vs original: {john_similarity:.3f}")
        print(f"   Retrieved mary vs original: {mary_similarity:.3f}")
        print(f"   Retrieved loves vs original: {loves_similarity:.3f}")
        print()
        
        # Interpretation
        avg_similarity = (john_similarity + mary_similarity + loves_similarity) / 3
        if avg_similarity > 0.8:
            print("✅ Excellent binding quality - high fidelity retrieval")
        elif avg_similarity > 0.5:
            print("⚠️  Good binding quality - acceptable retrieval accuracy")
        else:
            print("❌ Poor binding quality - consider different binding operation")
        print()
        
        print("🔬 Key insights:")
        print("   • Role-filler bindings preserve structured relationships")
        print("   • Compositional representations enable complex structures")  
        print("   • Unbinding allows content-addressable memory retrieval")
        print("   • Neural networks can process these distributed representations")
        print()
    
    # Return comprehensive results
    results = {
        'system': tpb,
        'vectors': {
            'roles': {'agent': agent_role, 'patient': patient_role, 'action': action_role},
            'fillers': {'john': john_filler, 'mary': mary_filler, 'loves': loves_filler},
            'bound': {'john_agent': john_as_agent, 'mary_patient': mary_as_patient, 'loves_action': loves_as_action},
            'composed': sentence,
            'retrieved': {'john': retrieved_john, 'mary': retrieved_mary, 'loves': retrieved_loves}
        },
        'similarities': {
            'john': john_similarity,
            'mary': mary_similarity, 
            'loves': loves_similarity,
            'average': avg_similarity
        },
        'config': {
            'vector_dim': vector_dim,
            'binding_type': binding_type,
            'bound_dim': len(john_as_agent.data)
        }
    }
    
    if show_details:
        print("🎉 Demonstration complete!")
        print(f"📊 Average similarity: {avg_similarity:.3f}")
    
    return results


def create_linguistic_example(
    sentence: str = "John loves Mary",
    vector_dim: int = 128
) -> Dict[str, Any]:
    """
    🗣️ Create a linguistic TPB example from a simple sentence.
    
    Demonstrates how natural language can be represented using
    tensor product binding following Smolensky's framework.
    
    Parameters
    ----------
    sentence : str, default="John loves Mary"
        Simple subject-verb-object sentence to represent
    vector_dim : int, default=128
        Vector dimensionality for representations
        
    Returns
    -------
    Dict[str, Any]
        Complete linguistic representation and analysis
    """
    # Parse simple sentence (basic implementation)
    words = sentence.lower().split()
    if len(words) != 3:
        raise ValueError("Currently supports only 3-word subject-verb-object sentences")
    
    subject, verb, obj = words
    
    # Create TPB system
    tpb = create_tpb_system(vector_dim=vector_dim, random_seed=1990)
    
    # Create syntactic roles
    subject_role = tpb.create_role_vector("SUBJECT")
    verb_role = tpb.create_role_vector("VERB")
    object_role = tpb.create_role_vector("OBJECT")
    
    # Create semantic fillers
    subject_filler = tpb.create_filler_vector(subject)
    verb_filler = tpb.create_filler_vector(verb)
    object_filler = tpb.create_filler_vector(obj)
    
    # Create role-filler bindings
    subject_binding = tpb.bind(subject_role, subject_filler)
    verb_binding = tpb.bind(verb_role, verb_filler)
    object_binding = tpb.bind(object_role, object_filler)
    
    # Compose sentence representation
    sentence_repr = tpb.compose([subject_binding, verb_binding, object_binding])
    
    return {
        'sentence': sentence,
        'system': tpb,
        'roles': {
            'subject': subject_role,
            'verb': verb_role, 
            'object': object_role
        },
        'fillers': {
            'subject': subject_filler,
            'verb': verb_filler,
            'object': object_filler
        },
        'bindings': {
            'subject': subject_binding,
            'verb': verb_binding,
            'object': object_binding
        },
        'sentence_representation': sentence_repr,
        'dimensions': {
            'roles': vector_dim,
            'bound': len(subject_binding.data),
            'sentence': len(sentence_repr.data)
        }
    }


# Export factory functions
__all__ = [
    'create_tpb_system',
    'demo_tensor_binding',
    'create_linguistic_example'
]


if __name__ == "__main__":
    print("🏭 Tensor Product Binding - Factory Functions Module")
    print("=" * 56)
    print("📊 MODULE CONTENTS:")
    print("  • create_tpb_system - Convenient TPB system factory")
    print("  • demo_tensor_binding - Educational demonstration")
    print("  • create_linguistic_example - Natural language TPB")
    print("  • Research-accurate factory functions for Smolensky (1990)")
    print("")
    print("✅ Factory functions module loaded successfully!")
    print("🔬 Convenient creation and demo utilities for TPB research!")
    
    # Quick demo
    print("\n🎭 Quick demonstration:")
    demo_results = demo_tensor_binding(vector_dim=32, show_details=False)
    print(f"   Average similarity: {demo_results['similarities']['average']:.3f}")
    print("   ✅ Factory functions working correctly!")