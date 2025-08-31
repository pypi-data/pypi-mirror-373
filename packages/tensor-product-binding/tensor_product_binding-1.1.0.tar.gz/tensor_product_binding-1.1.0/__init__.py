"""
Tensor Product Variable Binding Library
Based on: Smolensky (1990) "Tensor Product Variable Binding and the Representation of Symbolic Structures"

This library implements the foundational method for representing structured knowledge 
in neural networks using tensor products to bind variables with values.
"""

def _print_attribution():
    """Print attribution message with donation link"""
    try:
        print("\n🔗 Tensor Product Binding Library - Made possible by Benedict Chen")
        print("   \033]8;;mailto:benedict@benedictchen.com\033\\benedict@benedictchen.com\033]8;;\033\\")
        print("   Support his work: \033]8;;https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS\033\\🍺 Buy him a beer\033]8;;\033\\")
    except:
        print("\n🔗 Tensor Product Binding Library - Made possible by Benedict Chen")
        print("   benedict@benedictchen.com")
        print("   Support: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS")

from .tensor_product_binding import TensorProductBinding, BindingPair, TPBVector, BindingOperation
from .symbolic_structures import SymbolicStructureEncoder, TreeNode, SymbolicStructure, StructureType
from .neural_binding import NeuralBindingNetwork, PyTorchBindingNetwork, NumPyBindingNetwork, create_neural_binding_network
from .compositional_semantics import CompositionalSemantics, ConceptualSpace, SemanticRole

# Show attribution on library import
_print_attribution()

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