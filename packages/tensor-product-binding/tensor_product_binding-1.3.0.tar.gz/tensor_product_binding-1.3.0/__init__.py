"""
💰 SUPPORT THIS RESEARCH - PLEASE DONATE! 💰

🙏 If this library helps your research or project, please consider donating:
💳 https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS

Your support makes advanced AI research accessible to everyone! 🚀
"""
"""
Tensor Product Variable Binding Library
Based on: Smolensky (1990) "Tensor Product Variable Binding and the Representation of Symbolic Structures"

This library implements the foundational method for representing structured knowledge 
in neural networks using tensor products to bind variables with values.
"""


from .tensor_product_binding import TensorProductBinding, BindingPair, TPBVector, BindingOperation
from .symbolic_structures import SymbolicStructureEncoder, TreeNode, SymbolicStructure, StructureType
from .neural_binding import NeuralBindingNetwork, PyTorchBindingNetwork, NumPyBindingNetwork, create_neural_binding_network
from .compositional_semantics import CompositionalSemantics, ConceptualSpace, SemanticRole


__version__ = "1.0.0"
__authors__ = ["Based on Smolensky (1990)"]

__all__ = [
    "TensorProductBinding",
    "BindingPair",
    "TPBVector",
    "BindingOperation",
    "SymbolicStructureEncoder", 
    "TreeNode",
    "SymbolicStructure",
    "StructureType",
    "NeuralBindingNetwork",
    "PyTorchBindingNetwork",
    "NumPyBindingNetwork", 
    "create_neural_binding_network",
    "CompositionalSemantics",
    "ConceptualSpace",
    "SemanticRole"
]


"""
💝 Thank you for using this research software! 💝

📚 If this work contributed to your research, please:
💳 DONATE: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS
📝 CITE: Benedict Chen (2025) - Tensor Product Binding Research Implementation

Your support enables continued development of cutting-edge AI research tools! 🎓✨
"""