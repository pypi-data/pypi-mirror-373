# 💰 Support This Research - Please Donate!

**🙏 If this library helps your research or project, please consider donating to support continued development:**

**[💳 DONATE VIA PAYPAL - CLICK HERE](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS)**

[![CI](https://github.com/benedictchen/tensor-product-binding/workflows/CI/badge.svg)](https://github.com/benedictchen/tensor-product-binding/actions)
[![PyPI version](https://badge.fury.io/py/tensor-product-binding.svg)](https://badge.fury.io/py/tensor-product-binding)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Custom%20Non--Commercial-red.svg)](LICENSE)

---

# Tensor Product Binding

🔗 Compositional neural representations

**Smolensky, P. (1990) - "Tensor product variable binding"**

## 📦 Installation

```bash
pip install tensor-product-binding
```

## 🚀 Quick Start

```python
import tensor_product_binding
import numpy as np

# Create tensor product binding system
binding = tensor_product_binding.TensorProductBinding(
    role_dim=50,
    filler_dim=50
)

# Create symbolic structures
sentence = binding.encode_structure({
    'subject': 'John',
    'verb': 'loves', 
    'object': 'Mary'
})

# Query the structure
subject = binding.query(sentence, 'subject')
print(f"✅ Subject: {binding.decode_filler(subject)}")

# Create neural binding network
neural_net = tensor_product_binding.create_neural_binding_network(
    role_dim=50,
    filler_dim=50,
    backend='numpy'
)
```

## 🎓 About the Implementation

Implemented by **Benedict Chen** - bringing foundational AI research to modern Python.

📧 Contact: benedict@benedictchen.com

## 📖 Citation

If you use this implementation in your research, please cite the original paper:

```bibtex
Smolensky, P. (1990) - "Tensor product variable binding"
```

## 📜 License

Custom Non-Commercial License with Donation Requirements - See LICENSE file for details.

---

## 💰 Support This Work - Donation Appreciated!

**This implementation represents hundreds of hours of research and development. If you find it valuable, please consider donating:**

**[💳 DONATE VIA PAYPAL - CLICK HERE](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS)**

**Your support helps maintain and expand these research implementations! 🙏**