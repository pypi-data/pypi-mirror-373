# 💰 Support This Research - Please Donate!

**🙏 If this library helps your research or project, please consider donating to support continued development:**

**[💳 DONATE VIA PAYPAL - CLICK HERE](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS)**

[![CI](https://github.com/benedictchen/holographic-memory/workflows/CI/badge.svg)](https://github.com/benedictchen/holographic-memory/actions)
[![PyPI version](https://badge.fury.io/py/holographic-memory.svg)](https://badge.fury.io/py/holographic-memory)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Custom%20Non--Commercial-red.svg)](LICENSE)

---

# Holographic Memory

🌀 Holographic Reduced Representations - Vector symbolic architecture

**Plate, T. A. (1995) - "Holographic Reduced Representations"**

## 📦 Installation

```bash
pip install holographic-memory
```

## 🚀 Quick Start

```python
import holographic_memory
import numpy as np

# Create holographic memory
memory = holographic_memory.create_holographic_memory(
    vector_size=512,
    num_items=1000
)

# Store associations
memory.bind("cat", "animal")
memory.bind("dog", "animal") 
memory.bind("car", "vehicle")

# Retrieve and test
result = memory.probe("cat")
print(f"✅ 'cat' associated with: {result}")

# Clean up noisy retrieval
cleanup = holographic_memory.AssociativeCleanup(memory.get_vocabulary())
cleaned = cleanup.cleanup(result)
print(f"✅ Cleaned result: {cleaned}")
```

## 🎓 About the Implementation

Implemented by **Benedict Chen** - bringing foundational AI research to modern Python.

📧 Contact: benedict@benedictchen.com

## 📖 Citation

If you use this implementation in your research, please cite the original paper:

```bibtex
Plate, T. A. (1995) - "Holographic Reduced Representations"
```

## 📜 License

Custom Non-Commercial License with Donation Requirements - See LICENSE file for details.

---

## 💰 Support This Work - Donation Appreciated!

**This implementation represents hundreds of hours of research and development. If you find it valuable, please consider donating:**

**[💳 DONATE VIA PAYPAL - CLICK HERE](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS)**

**Your support helps maintain and expand these research implementations! 🙏**