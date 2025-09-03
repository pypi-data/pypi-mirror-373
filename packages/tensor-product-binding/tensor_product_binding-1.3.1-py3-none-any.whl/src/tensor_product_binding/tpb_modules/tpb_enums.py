"""
🏷️ Tensor Product Binding - Operation Type Definitions
======================================================

Author: Benedict Chen (benedict@benedictchen.com)

💰 Donations: Help support this research!
   PayPal: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS
   💖 Please consider recurring donations to support continued TPB research

Based on: Smolensky (1990) "Tensor Product Variable Binding and the Representation of Symbolic Structures"

🔬 Research Foundation:
======================
Enumerations defining mathematical operations from multiple research traditions:
- Smolensky (1990): Classic tensor product binding (role ⊗ filler)
- Plate (1995): Holographic Reduced Representations with circular convolution
- Kanerva (2009): Hyperdimensional computing with element-wise operations
- Modern VSA: Vector Symbolic Architecture variations

ELI5 Explanation:
================
Think of binding operations like different ways to mix paint colors! 🎨

🖌️ **OUTER_PRODUCT** (Classic Tensor Product):
Like mixing oil paints on a palette - when you combine red + blue,
you get a completely new color (purple) that contains information
about both original colors. This creates a larger, richer representation.

🌀 **CIRCULAR_CONVOLUTION** (Memory-Efficient):
Like mixing watercolors in a fixed-size container - you swirl red + blue
together, and the result still fits in the same size container but
contains both colors. The colors are "bound" together efficiently.

➕ **ADDITION** (Simple Superposition):
Like layering transparent films - red film + blue film = you can see
both colors at once, but they don't really "bind" together strongly.

✖️ **MULTIPLICATION** (Element-wise Binding):
Like using a color mixer tool - each part of red multiplies with the
corresponding part of blue, creating a new mixed pattern.

ASCII Operation Comparison:
===========================
    OUTER_PRODUCT (⊗):        CIRCULAR_CONVOLUTION (*):
    
    Role[3]    Filler[3]       Role[3]    Filler[3]  
    ┌─────┐    ┌─────┐         ┌─────┐    ┌─────┐
    │ a₁  │    │ b₁  │         │ a₁  │    │ b₁  │
    │ a₂  │ ⊗  │ b₂  │  →      │ a₂  │ *  │ b₂  │  →
    │ a₃  │    │ b₃  │         │ a₃  │    │ b₃  │
    └─────┘    └─────┘         └─────┘    └─────┘
        │          │              │          │
        ▼          ▼              ▼          ▼
    ┌─────────────────┐       ┌─────────────────┐
    │ a₁b₁  a₁b₂  a₁b₃│       │ a₁b₁+a₂b₃+a₃b₂ │
    │ a₂b₁  a₂b₂  a₂b₃│       │ a₁b₂+a₂b₁+a₃b₃ │
    │ a₃b₁  a₃b₂  a₃b₃│       │ a₁b₃+a₂b₂+a₃b₁ │
    └─────────────────┘       └─────────────────┘
    Result: 9 elements         Result: 3 elements
    (Size increases)           (Size preserved)

    ADDITION (+):              MULTIPLICATION (×):
    
    Role[3]    Filler[3]       Role[3]    Filler[3]
    ┌─────┐    ┌─────┐         ┌─────┐    ┌─────┐
    │ a₁  │    │ b₁  │         │ a₁  │    │ b₁  │
    │ a₂  │ +  │ b₂  │  →      │ a₂  │ ×  │ b₂  │  →
    │ a₃  │    │ b₃  │         │ a₃  │    │ b₃  │
    └─────┘    └─────┘         └─────┘    └─────┘
        │          │              │          │
        ▼          ▼              ▼          ▼
    ┌─────────────────┐       ┌─────────────────┐
    │     a₁ + b₁     │       │     a₁ × b₁     │
    │     a₂ + b₂     │       │     a₂ × b₂     │
    │     a₃ + b₃     │       │     a₃ × b₃     │
    └─────────────────┘       └─────────────────┘
    Result: 3 elements         Result: 3 elements
    (Superposition)            (Element-wise)

⚡ Operation Properties:
=======================
1. **OUTER_PRODUCT**: Maximum information preservation, size increases
2. **CIRCULAR_CONVOLUTION**: Information preserved, constant size, invertible
3. **ADDITION**: Simple superposition, easily separable, no true binding
4. **MULTIPLICATION**: Element-wise binding, size preserved, some information loss

📊 Use Case Guidelines:
======================
• **OUTER_PRODUCT**: When you need maximum precision and can afford larger vectors
• **CIRCULAR_CONVOLUTION**: When memory is limited but you need good binding
• **ADDITION**: For simple superposition of multiple concepts
• **MULTIPLICATION**: For fast, approximate binding in high-dimensional spaces

This module defines the mathematical "vocabulary" for how roles and fillers
can be combined in distributed representations.
"""

from enum import Enum


class BindingOperation(Enum):
    """
    🔗 Types of binding operations available in tensor product binding.
    
    Different mathematical approaches to combine role and filler vectors:
    - OUTER_PRODUCT: Standard tensor product (role ⊗ filler)
    - CIRCULAR_CONVOLUTION: Circular convolution binding (memory efficient) 
    - ADDITION: Simple vector addition (least structured)
    - MULTIPLICATION: Element-wise multiplication (component binding)
    """
    OUTER_PRODUCT = "outer_product"
    CIRCULAR_CONVOLUTION = "circular_convolution"  
    ADDITION = "addition"
    MULTIPLICATION = "multiplication"


# Export the enumeration
__all__ = ['BindingOperation']


if __name__ == "__main__":
    print("🏷️ Tensor Product Binding - Enumerations Module")
    print("=" * 50)
    print("📊 MODULE CONTENTS:")
    print("  • BindingOperation - Core binding operation types")
    print("  • Research-accurate enumeration of TPB mathematical operations")
    print("")
    print("✅ Enumerations module loaded successfully!")
    print("🔬 Essential enums for tensor product binding operations!")