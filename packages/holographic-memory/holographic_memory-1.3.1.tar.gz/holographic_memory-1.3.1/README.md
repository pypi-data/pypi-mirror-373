# 💰 Support This Research - Please Donate!

**🙏 If this library helps your research or project, please consider donating to support continued development:**

<div align="center">

**[💳 DONATE VIA PAYPAL](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS)** | **[❤️ SPONSOR ON GITHUB](https://github.com/sponsors/benedictchen)**

</div>

[![CI](https://github.com/benedictchen/holographic-memory/workflows/CI/badge.svg)](https://github.com/benedictchen/holographic-memory/actions)
[![PyPI version](https://img.shields.io/pypi/v/holographic-memory.svg)](https://pypi.org/project/holographic-memory/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Custom%20Non--Commercial-red.svg)](LICENSE)
[![Research Accurate](https://img.shields.io/badge/research-accurate-brightgreen.svg)](RESEARCH_FOUNDATION.md)

---

# Holographic Memory

🌀 **Holographic Reduced Representations for distributed symbolic processing**

Holographic Reduced Representations (HRR) enable the storage and manipulation of symbolic structures in fixed-size distributed representations. This implementation provides Tony Plate's groundbreaking Vector Symbolic Architecture that allows compositional operations on high-dimensional vectors while preserving relational information.

**Research Foundation**: Plate, T. A. (1995) - *"Holographic Reduced Representations"*

## 🚀 Quick Start

### Installation

```bash
pip install holographic_memory
```

**Requirements**: Python 3.9+, NumPy, SciPy, matplotlib

### Basic HRR Operations

```python
from holographic_memory import HolographicMemory
import numpy as np

# Create HRR system
hrr = HolographicMemory(
    vector_dimension=512,
    encoding_method='random_phases',
    cleanup_threshold=0.3
)

# Basic binding operations
john = hrr.encode("john")
mary = hrr.encode("mary")
loves = hrr.encode("loves")

# Create relational structure: john loves mary
sentence = hrr.bind(john, hrr.bind(loves, mary))

# Query the structure
who_loves = hrr.unbind(sentence, john)  # Should be similar to "loves ⊗ mary"
what_relation = hrr.unbind(sentence, hrr.bind(john, mary))  # Should be "loves"

print(f"Query 'john ? mary': {hrr.cleanup(what_relation)}")
print(f"Similarity: {hrr.similarity(what_relation, loves):.3f}")
```

### Associative Memory Example

```python
from holographic_memory import AssociativeMemory
from holographic_memory.vector_operations import CircularConvolution

# Create associative memory for episodic storage
memory = AssociativeMemory(
    capacity=10000,
    vector_size=1024,
    operation=CircularConvolution(),
    cleanup_memory=True
)

# Store episodic memories
breakfast = memory.create_episode({
    'location': 'kitchen',
    'time': 'morning',
    'action': 'eating',
    'object': 'cereal',
    'agent': 'benedict'
})

# Store the episode
memory.store("breakfast_monday", breakfast)

# Retrieve and query
retrieved = memory.recall("breakfast_monday")
location_cue = memory.probe(retrieved, "location")
print(f"Breakfast location: {memory.cleanup(location_cue)}")

# Associative recall
similar_episodes = memory.find_similar(breakfast, threshold=0.7)
print(f"Found {len(similar_episodes)} similar episodes")
```

### Complex Compositional Structures

```python
from holographic_memory import CompositionalStructures

# Handle nested structures like parse trees
compositor = CompositionalStructures(
    dimension=2048,
    max_depth=5,
    structure_type='tree'
)

# Represent sentence: "The cat that chased the mouse ran home"
# Structure: [S [NP [Det the] [N [cat [RC that [VP chased [NP the mouse]]]]] [VP ran home]]

sentence_tree = compositor.create_structure({
    'type': 'S',
    'children': {
        'subject': {
            'type': 'NP',
            'head': 'cat',
            'determiner': 'the',
            'modifier': {
                'type': 'RC',
                'verb': 'chased',
                'object': 'mouse'
            }
        },
        'predicate': {
            'type': 'VP',
            'verb': 'ran',
            'destination': 'home'
        }
    }
})

# Query the structure
main_verb = compositor.query(sentence_tree, path=['predicate', 'verb'])
relative_verb = compositor.query(sentence_tree, path=['subject', 'modifier', 'verb'])

print(f"Main verb: {compositor.decode(main_verb)}")
print(f"Relative clause verb: {compositor.decode(relative_verb)}")
```

## 🧬 Advanced Features

### Vector Operations Suite

```python
from holographic_memory.vector_operations import (
    CircularConvolution,      # Primary HRR binding operation
    ComplexBinding,           # Complex number encoding
    FourierBinding,           # FFT-based efficient binding
    MatrixBinding,           # Matrix-based binding (experimental)
    PermutationBinding       # Permutation-based operations
)

# Compare different binding operations
operations = [
    CircularConvolution(),
    ComplexBinding(),
    FourierBinding(),
    PermutationBinding()
]

x = np.random.randn(512)
y = np.random.randn(512)

for op in operations:
    bound = op.bind(x, y)
    unbound = op.unbind(bound, x)
    similarity = np.dot(unbound, y) / (np.linalg.norm(unbound) * np.linalg.norm(y))
    print(f"{op.__class__.__name__}: similarity = {similarity:.3f}")
```

### Memory Palace Implementation

```python
from holographic_memory import MemoryPalace

# Create spatial memory system
palace = MemoryPalace(
    spatial_dimensions=3,
    room_capacity=100,
    navigation_method='spatial_graph'
)

# Create rooms and store memories
kitchen = palace.create_room("kitchen", spatial_cues=['warm', 'bright', 'smell_coffee'])
bedroom = palace.create_room("bedroom", spatial_cues=['dark', 'quiet', 'soft'])

# Store memories with spatial context
palace.store_memory(
    room="kitchen",
    memory_id="morning_routine",
    content={
        'activity': 'making_coffee',
        'mood': 'sleepy',
        'time': '7am',
        'objects': ['mug', 'coffee_beans', 'grinder']
    }
)

# Navigate and retrieve
path = palace.find_path("bedroom", "kitchen")
memories_along_path = palace.recall_path_memories(path)

for memory in memories_along_path:
    print(f"Memory: {memory['content']['activity']} at {memory['room']}")
```

## 🔬 Research Foundation

### Scientific Accuracy

This implementation provides **research-accurate** reproduction of HRR theory:

- **Mathematical Fidelity**: Exact circular convolution operations as specified by Plate
- **Binding Properties**: Proper commutativity, associativity, and approximate inverses
- **Noise Characteristics**: Faithful reproduction of HRR noise accumulation properties
- **Cleanup Networks**: Implementation of associative cleanup mechanisms

### Key Research Contributions

- **Distributed Symbolic Processing**: Combine symbolic and connectionist approaches
- **Fixed-Size Representations**: Store variable-length structures in fixed-size vectors
- **Compositional Binding**: Systematic combination and decomposition of representations  
- **Neurally Plausible**: Operations implementable in neural hardware

### Original Research Papers

- **Plate, T. A. (1995)**. "Holographic Reduced Representations." *IEEE Transactions on Neural Networks*, 6(3), 623-641.
- **Plate, T. A. (2003)**. "Holographic Reduced Representation: Distributed Representation for Cognitive Structures." *CSLI Publications*.

## 📊 Implementation Highlights

### Vector Operations
- **Circular Convolution**: Efficient O(n log n) FFT-based binding
- **Multiple Encodings**: Random phases, random permutations, fractal binding
- **Cleanup Networks**: Associative memory for symbol recovery
- **Similarity Measures**: Cosine similarity and other distance metrics

### Code Quality  
- **Research Accurate**: 100% faithful to original HRR mathematical operations
- **Memory Efficient**: Optimized vector operations for large-scale structures
- **Extensively Tested**: Validated against HRR theoretical properties
- **Educational Value**: Clear implementation of abstract VSA concepts

## 🧮 Mathematical Foundation

### Circular Convolution Binding

The core HRR operation uses circular convolution:

```
(a ⊛ b)ᵢ = Σⱼ aⱼ × b₍ᵢ₋ⱼ₎ mod n
```

Where `⊛` denotes circular convolution, enabling approximate inverse operations.

### Approximate Inverse

The approximate inverse enables unbinding:

```
a ≈ (a ⊛ b) ⊛ b#
```

Where `b#` is the approximate inverse of `b`.

### Noise Analysis

HRR representations accumulate noise proportionally to √n for n superposed items:

```
‖noise‖ ≈ √n × ‖single_item‖
```

## 🎯 Use Cases & Applications

### Cognitive Modeling Applications
- **Memory Models**: Episodic and semantic memory systems
- **Language Processing**: Syntactic parsing and semantic composition
- **Analogical Reasoning**: Structure mapping and similarity assessment
- **Concept Formation**: Hierarchical concept representation

### AI System Applications
- **Knowledge Representation**: Symbolic reasoning in neural networks
- **Natural Language Processing**: Compositional semantics and syntax
- **Robotics**: Spatial reasoning and navigation
- **Expert Systems**: Rule representation and inference

### Neuroscience Applications
- **Neural Binding**: Models of variable binding in cortex
- **Working Memory**: Capacity limitations and interference effects
- **Hippocampal Function**: Episodic memory formation and retrieval
- **Cortical Processing**: Distributed representation in cortical areas

## 📖 Documentation & Tutorials

- 📚 **[Complete Documentation](https://holographic-memory.readthedocs.io/)**
- 🎓 **[Tutorial Notebooks](https://github.com/benedictchen/holographic-memory/tree/main/tutorials)**
- 🔬 **[Research Foundation](RESEARCH_FOUNDATION.md)**
- 🎯 **[Advanced Examples](https://github.com/benedictchen/holographic-memory/tree/main/examples)**
- 🐛 **[Issue Tracker](https://github.com/benedictchen/holographic-memory/issues)**

## 🤝 Contributing

We welcome contributions! Please see:

- **[Contributing Guidelines](CONTRIBUTING.md)**
- **[Development Setup](docs/development.md)**  
- **[Code of Conduct](CODE_OF_CONDUCT.md)**

### Development Installation

```bash
git clone https://github.com/benedictchen/holographic-memory.git
cd holographic-memory
pip install -e ".[test,dev]"
pytest tests/
```

## 📜 Citation

If you use this implementation in academic work, please cite:

```bibtex
@software{holographic_memory_benedictchen,
    title={Holographic Memory: Research-Accurate Implementation of HRR and Vector Symbolic Architecture},
    author={Benedict Chen},
    year={2025},
    url={https://github.com/benedictchen/holographic-memory},
    version={1.1.0}
}

@article{plate1995holographic,
    title={Holographic reduced representations},
    author={Plate, Tony A},
    journal={IEEE transactions on neural networks},
    volume={6},
    number={3},
    pages={623--641},
    year={1995},
    publisher={IEEE}
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

### 🎯 Donation Tier Goals (With Holographic Humor)

**☕ $5 - Buy Benedict Coffee**  
*"Caffeine binding with my neurons! coffee ⊛ benedict = productive_coding_session."*  
💳 [PayPal One-time](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS) | ❤️ [GitHub Monthly](https://github.com/sponsors/benedictchen)

**🍕 $25 - Pizza Fund**  
*"Holographic pizza storage: all flavors superposed in one vector! Perfect for my distributed appetite."*  
💳 [PayPal One-time](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS) | ❤️ [GitHub Monthly](https://github.com/sponsors/benedictchen)

**🏠 $500,000 - Buy Benedict a House**  
*"With walls covered in circular convolution equations! My neighbors will love the holographic decorations."*  
💳 [PayPal Challenge](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS) | ❤️ [GitHub Lifetime](https://github.com/sponsors/benedictchen)

**🚀 $10,000,000,000 - Space Program**  
*"To test holographic memory in zero gravity! Do circular convolutions work the same way in space?"*  
💳 [PayPal Cosmic](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS) | ❤️ [GitHub Galactic](https://github.com/sponsors/benedictchen)

### 🎪 Monthly Subscription Tiers (GitHub Sponsors)

**🌀 Vector Architect ($10/month)** - *"Monthly support for my distributed representation lifestyle!"*  
❤️ [Subscribe on GitHub](https://github.com/sponsors/benedictchen)

**🧠 Memory Palace Patron ($50/month)** - *"Help me build the ultimate cognitive architecture!"*  
❤️ [Subscribe on GitHub](https://github.com/sponsors/benedictchen)

<div align="center">

**One-time donation?**  
**[💳 DONATE VIA PAYPAL](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WXQKYYKPHWXHS)**

**Ongoing support?**  
**[❤️ SPONSOR ON GITHUB](https://github.com/sponsors/benedictchen)**

**Can't decide?**  
**Why not both?** 🤷‍♂️

</div>

**Every contribution gets stored in my holographic gratitude vector! success ⊛ support = sustainable_research 🚀**

*P.S. - If you help me get that equation-covered house, I'll name a circular convolution operation after you! convolution_[your_name](a, b) = a ⊛ b*

---

<div align="center">

## 🌟 What the Community is Saying

</div>

---

> **@VectorMemoryMaven** (934K followers) • *1 hour ago* • *(parody)*
> 
> *"BESTIE I just discovered holographic memory and my brain is literally RESTRUCTURING itself! 🧠✨ It's like having infinite storage but make it math - you can store entire memories in vectors that somehow remember EVERYTHING while taking up almost no space! Tony Plate really said 'what if we made memory work like holograms' and honestly that's galaxy brain energy. This is literally how your brain stores the memory of that embarrassing thing you did in 2nd grade AND still has room for TikTok trends. Currently using HRR to understand why certain songs unlock specific memories and the science is actually sending me! 🎵"*
> 
> **127.4K ❤️ • 22.8K 🔄 • 6.7K 🤯**