# 💰 Support This Research - Please Donate!

**🙏 If this library helps your research or project, please consider donating to support continued development:**

<div align="center">

**[💳 DONATE VIA PAYPAL](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS)** | **[❤️ SPONSOR ON GITHUB](https://github.com/sponsors/benedictchen)**

</div>

[![CI](https://github.com/benedictchen/tensor-product-binding/workflows/CI/badge.svg)](https://github.com/benedictchen/tensor-product-binding/actions)
[![PyPI version](https://img.shields.io/pypi/v/tensor-product-binding.svg)](https://pypi.org/project/tensor-product-binding/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Custom%20Non--Commercial-red.svg)](LICENSE)
[![Research Accurate](https://img.shields.io/badge/research-accurate-brightgreen.svg)](RESEARCH_FOUNDATION.md)

---

# Tensor Product Binding

🧠 Neural binding mechanisms for structured knowledge representation in connectionist systems

**Smolensky, P. (1990)** - "Tensor product variable binding and the representation of symbolic structures in connectionist systems"  
**Smolensky, P., & Legendre, G. (2006)** - "The harmonic mind: From neural computation to optimality-theoretic grammar"

## 📦 Installation

```bash
pip install tensor-product-binding
```

## 🚀 Quick Start

### Basic Tensor Product Binding
```python
from tensor_product_binding import TensorProductBinding
import numpy as np

# Create tensor product binding system
tpb = TensorProductBinding(
    role_dimension=64,
    filler_dimension=64,
    binding_type='outer_product'
)

# Create role and filler vectors
agent_role = tpb.create_role_vector("agent")
patient_role = tpb.create_role_vector("patient")
john_filler = tpb.create_filler_vector("john")
mary_filler = tpb.create_filler_vector("mary")

# Bind roles to fillers
john_as_agent = tpb.bind(agent_role, john_filler)
mary_as_patient = tpb.bind(patient_role, mary_filler)

# Compose complex structure: "john loves mary"
sentence_structure = tpb.compose([john_as_agent, mary_as_patient])

# Extract bindings
extracted_agent = tpb.unbind(sentence_structure, agent_role)
similarity = tpb.similarity(extracted_agent, john_filler)
print(f"Agent extraction similarity: {similarity:.3f}")
```

### Compositional Semantics Example
```python
from tensor_product_binding import CompositionalSemantics

# Create compositional semantic system
semantics = CompositionalSemantics(
    vector_dimension=512,
    composition_method='smolensky',
    role_scheme='syntactic'
)

# Define semantic roles
roles = {
    'subject': semantics.create_role("subject"),
    'verb': semantics.create_role("verb"), 
    'object': semantics.create_role("object")
}

# Create semantic representations
concepts = {
    'john': semantics.create_concept("john", category="person"),
    'loves': semantics.create_concept("loves", category="relation"),
    'mary': semantics.create_concept("mary", category="person")
}

# Compose sentence meaning
sentence_meaning = semantics.compose_proposition(
    subject=concepts['john'],
    verb=concepts['loves'],
    object=concepts['mary']
)

# Query the composed structure
who_loves = semantics.query(sentence_meaning, roles['subject'])
print(f"Who loves? {semantics.decode(who_loves)}")

loves_whom = semantics.query(sentence_meaning, roles['object']) 
print(f"Loves whom? {semantics.decode(loves_whom)}")
```

### Neural Binding with Hierarchical Structures
```python
from tensor_product_binding import NeuralBinding

# Create hierarchical binding system
neural_binding = NeuralBinding(
    base_dimension=256,
    hierarchy_levels=3,
    binding_strength=0.8
)

# Build complex hierarchical structure
# Sentence: "The cat [that chased the mouse] ran home"
sentence = neural_binding.create_structure()

# Main clause
main_subject = neural_binding.bind("subject", "cat")
main_verb = neural_binding.bind("verb", "ran")
main_object = neural_binding.bind("object", "home")

# Embedded relative clause  
rel_subject = neural_binding.bind("rel_subject", "cat")
rel_verb = neural_binding.bind("rel_verb", "chased")
rel_object = neural_binding.bind("rel_object", "mouse")

# Compose relative clause
relative_clause = neural_binding.compose([rel_subject, rel_verb, rel_object])

# Bind relative clause as modifier
modified_subject = neural_binding.bind("modifier", relative_clause)
final_subject = neural_binding.compose([main_subject, modified_subject])

# Complete sentence structure
complete_sentence = neural_binding.compose([
    final_subject, main_verb, main_object
])

# Navigate the hierarchical structure
print(f"Main verb: {neural_binding.extract(complete_sentence, 'verb')}")
embedded_clause = neural_binding.extract(final_subject, "modifier")
embedded_verb = neural_binding.extract(embedded_clause, "rel_verb")
print(f"Embedded verb: {embedded_verb}")
```

## 🧬 Advanced Features

### Symbolic Structure Handling
```python
from tensor_product_binding import SymbolicStructures

# Handle complex symbolic structures
symbolic = SymbolicStructures(
    representation='tree_structure',
    binding_method='recursive'
)

# Parse and represent nested structure
# Expression: "(+ (* 3 4) (/ 8 2))"
expression = symbolic.parse_expression("(+ (* 3 4) (/ 8 2))")
tensor_repr = symbolic.tensorize(expression)

# Manipulate symbolic structure
left_subtree = symbolic.get_subtree(tensor_repr, path="left")
operator = symbolic.get_operator(left_subtree)
print(f"Left operator: {operator}")  # Should be "*"

# Transform structure
simplified = symbolic.apply_transformation(tensor_repr, "arithmetic_simplify")
result = symbolic.evaluate(simplified)
print(f"Result: {result}")  # Should be 16
```

### Pattern Completion and Analogy
```python
from tensor_product_binding import PatternCompletion

# Pattern completion using tensor product representations
pattern = PatternCompletion(
    dimension=400,
    completion_method='hopfield',
    noise_tolerance=0.2
)

# Learn analogical patterns
# "man is to woman as king is to ?"
man = pattern.encode("man")
woman = pattern.encode("woman")
king = pattern.encode("king")

# Create analogical relationship vector
relationship = pattern.subtract(woman, man)  # woman - man
queen_predicted = pattern.add(king, relationship)  # king + relationship

# Find closest match
candidates = ["queen", "prince", "castle", "crown"]
matches = pattern.find_nearest(queen_predicted, candidates)
print(f"Best analogy completion: {matches[0]}")  # Should be "queen"
```

## 🔬 Key Algorithmic Features

### Tensor Product Operations
- **Role-Filler Binding**: Systematic binding of roles to filler values
- **Compositional Structure**: Hierarchical composition of complex representations
- **Unbinding Operations**: Extraction of components from composite structures
- **Distributed Representation**: Graceful degradation and similarity-based processing

### Neural Plausibility
- **Connectionist Compatibility**: Designed for neural network implementation
- **Parallel Processing**: Simultaneous constraint satisfaction
- **Noise Tolerance**: Robust performance with imperfect inputs
- **Scalable Architecture**: Handles structures of varying complexity

### Compositional Semantics
- **Systematic Composition**: Predictable meaning combination
- **Productivity**: Generate infinite structures from finite components
- **Systematicity**: Similar structures have similar representations
- **Recursion Support**: Handle arbitrarily nested structures

## 📊 Implementation Highlights

- **Research Accuracy**: Faithful implementation of Smolensky's theoretical framework
- **Educational Value**: Clear code structure for learning tensor product representations
- **Performance Optimized**: Efficient tensor operations using NumPy/SciPy
- **Modular Design**: Separate components for different aspects of binding
- **Extensible Framework**: Easy to extend for domain-specific applications

## 🧮 Theoretical Foundation

This implementation provides research-accurate implementations of:

- **Tensor Product Representations**: Smolensky's foundational framework for symbolic structures in neural networks
- **Compositional Semantics**: Systematic meaning composition in distributed representations  
- **Neural Binding Theory**: Mechanisms for dynamic variable binding in connectionist systems
- **Harmonic Grammar**: Integration with optimality-theoretic approaches to cognitive modeling

### Core Mathematical Operations

**Binding Operation:**
```
bind(role, filler) = role ⊗ filler
```

**Composition Operation:**  
```
compose(bindings) = Σᵢ bindingᵢ
```

**Unbinding Operation:**
```
unbind(structure, role) = structure · role† 
```

Where `⊗` is the tensor product, `·` is the dot product, and `†` indicates the role conjugate.

## 📖 Documentation & Tutorials

- 📚 **[Complete Documentation](https://tensor-product-binding.readthedocs.io/)**
- 🎓 **[Tutorial Notebooks](https://github.com/benedictchen/tensor-product-binding/tree/main/tutorials)**
- 🔬 **[Research Foundation](RESEARCH_FOUNDATION.md)**
- 🎯 **[Advanced Examples](https://github.com/benedictchen/tensor-product-binding/tree/main/examples)**
- 🐛 **[Issue Tracker](https://github.com/benedictchen/tensor-product-binding/issues)**

## 🤝 Contributing

We welcome contributions! Please see:

- **[Contributing Guidelines](CONTRIBUTING.md)**
- **[Development Setup](docs/development.md)**  
- **[Code of Conduct](CODE_OF_CONDUCT.md)**

### Development Installation

```bash
git clone https://github.com/benedictchen/tensor-product-binding.git
cd tensor-product-binding
pip install -e ".[test,dev]"
pytest tests/
```

## 📜 Citation

If you use this implementation in academic work, please cite:

```bibtex
@software{tensor_product_binding_benedictchen,
    title={Tensor Product Binding: Research-Accurate Implementation of Smolensky's Framework},
    author={Benedict Chen},
    year={2025},
    url={https://github.com/benedictchen/tensor-product-binding},
    version={1.5.0}
}

@article{smolensky1990tensor,
    title={Tensor product variable binding and the representation of symbolic structures in connectionist systems},
    author={Smolensky, Paul},
    journal={Artificial intelligence},
    volume={46},
    number={1-2},
    pages={159--216},
    year={1990},
    publisher={Elsevier}
}
```

## 📋 License

**Custom Non-Commercial License with Donation Requirements** - See [LICENSE](LICENSE) file for details.

## 🎓 About the Implementation

**Implemented by Benedict Chen** - Bringing foundational AI research to modern Python.

📧 **Contact**: benedict@benedictchen.com  
🐙 **GitHub**: [@benedictchen](https://github.com/benedictchen)

---

## 💰 Support This Work - Choose Your Adventure!

**This implementation represents hundreds of hours of research and development. If you find it valuable, please consider donating:**

### 🎯 Donation Tier Goals (With Tensor Product Humor)

**☕ $5 - Buy Benedict Coffee**  
*"Coffee binds with my neurons in a perfect tensor product! Input: caffeine, Role: alertness, Output: productive coding."*  
💳 [PayPal One-time](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS) | ❤️ [GitHub Monthly](https://github.com/sponsors/benedictchen)

**🍕 $25 - Pizza Fund**  
*"Pizza provides the hierarchical structure my brain needs! Each slice is a filler, each hunger pang is a role to bind."*  
💳 [PayPal One-time](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS) | ❤️ [GitHub Monthly](https://github.com/sponsors/benedictchen)

**🏠 $500,000 - Buy Benedict a House**  
*"With rooms organized as a tensor product space! Each room will represent a different binding dimension."*  
💳 [PayPal Challenge](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS) | ❤️ [GitHub Lifetime](https://github.com/sponsors/benedictchen)

**🏎️ $200,000 - Lamborghini Fund**  
*"For high-speed compositional semantics! The car's role: transportation, The filler: style. Perfect binding!"*  
💳 [PayPal Supercar](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS) | ❤️ [GitHub Lifetime](https://github.com/sponsors/benedictchen)

**✈️ $50,000,000 - Private Jet**  
*"To visit conferences on neural binding! My flight path will demonstrate perfect compositional systematicity."*  
💳 [PayPal Aerospace](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS) | ❤️ [GitHub Aviation](https://github.com/sponsors/benedictchen)

**🏝️ $100,000,000 - Private Island**  
*"Where every palm tree represents a different tensor dimension! The ultimate distributed representation paradise."*  
💳 [PayPal Paradise](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS) | ❤️ [GitHub Tropical](https://github.com/sponsors/benedictchen)

### 🎪 Monthly Subscription Tiers (GitHub Sponsors)

**🧬 Neural Binder ($10/month)** - *"Monthly support for maintaining perfect role-filler binding in my research!"*  
❤️ [Subscribe on GitHub](https://github.com/sponsors/benedictchen)

**🕰️ Compositional Semanticist ($25/month)** - *"Help me compose the meaning of sustainable research!"*  
❤️ [Subscribe on GitHub](https://github.com/sponsors/benedictchen)

**🏆 Tensor Master ($100/month)** - *"Elite support for the ultimate hierarchical structure of coding excellence!"*  
❤️ [Subscribe on GitHub](https://github.com/sponsors/benedictchen)

<div align="center">

**One-time donation?**  
**[💳 DONATE VIA PAYPAL](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS)**

**Ongoing support?**  
**[❤️ SPONSOR ON GITHUB](https://github.com/sponsors/benedictchen)**

**Can't decide?**  
**Why not both?** 🤷‍♂️

</div>

**Every contribution creates a perfect tensor product with my gratitude! Your support binds beautifully with my motivation for continued research! 🚀**

*P.S. - If you help me get that tensor dimension island, I promise to name a binding operation after you!*

---

<div align="center">

## 🌟 What the Community is Saying

</div>

---

> **@BindingBossBabe** (645K followers) • *4 hours ago* • *(parody)*
> 
> *"OMG this tensor product binding library just solved the variable binding problem and I'm having a whole EXISTENTIAL MOMENT! 🤯 It's literally how your brain keeps track of 'the red car' vs 'the fast car' without getting confused about which properties belong to what object! Smolensky really said 'let me figure out how consciousness organizes information' and honestly that's the most main character energy ever. This is giving 'I understand how thoughts have structure' vibes and it's actually making me question reality in the best way! Been using this to analyze why certain memories stick together and the compositional semantics are beautiful fr! 🧠✨"*
> 
> **118.9K ❤️ • 21.6K 🔄 • 8.2K 🤔**