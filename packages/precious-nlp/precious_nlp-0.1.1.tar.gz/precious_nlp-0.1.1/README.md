# Precious Package

## Overview
The Precious package provides a minimal model showcasing three tokenizer-free approaches for natural language processing tasks. It includes implementations for T-FREE, CANINE, and byte-level embeddings, along with attention mechanisms for enhanced performance.

## Installation

### From PyPI (Recommended)
```bash
pip install precious-nlp
```

### From Source (Development)
```bash
git clone https://github.com/bimri/precious.git
cd precious
pip install -e .
```

### With Optional Dependencies
```bash
# For development tools
pip install precious-nlp[dev]

# For benchmarking
pip install precious-nlp[benchmarks]

# For documentation
pip install precious-nlp[docs]

# All optional dependencies
pip install precious-nlp[all]
```

## Quick Start

### Installation and Import
```bash
# Install the package
pip install precious-nlp
```

```python
# Import the package (note: install as 'precious-nlp', import as 'precious')
import precious
from precious import PreciousModel, PreciousConfig
```

## Usage
Here is a basic example of how to use the PreciousModel:

```python
import precious
from precious import PreciousModel, PreciousConfig

# Initialize the model with the desired configuration
config = PreciousConfig(mode="byte", d_model=256)  # or "tfree", "canine"
model = PreciousModel(config)

# Prepare your input data
inputs = ["Hello, tokenizer-free world!"]
outputs = model(inputs)

# Access the logits
logits = outputs["logits"]
print(f"Output shape: {logits.shape}")  # [batch_size, seq_len, vocab_size]

# Training with targets
targets = ["Hello, tokenizer-free universe!"]
outputs = model(inputs, targets=targets)
loss = outputs["loss"]
print(f"Training loss: {loss.item()}")
```

## Three Tokenizer-Free Approaches

### 1. Byte-Level Processing
```python
import precious
config = precious.PreciousConfig(mode="byte", d_model=256)
model = precious.PreciousModel(config)
# Processes text at byte level - universal and memory efficient
```

### 2. CANINE Approach
```python
import precious
config = precious.PreciousConfig(mode="canine", d_model=256)
model = precious.PreciousModel(config)
# Character-level processing with Unicode support
```

### 3. T-FREE Method
```python
import precious
config = precious.PreciousConfig(mode="tfree", d_model=256, tfree_vocab_v=8192)
model = precious.PreciousModel(config)
# Vocabulary-aware with character-level fallback
```

## Key Features

- 🚀 **Three tokenizer-free approaches** in one unified library
- 🎯 **Production-ready** with comprehensive testing and documentation  
- 🌍 **Universal text support** - handles any Unicode text
- ⚡ **Efficient processing** with configurable model architectures
- 🧪 **Research-friendly** with benchmarking and comparison tools
- 📚 **Well-documented** with extensive examples and API reference

## Quick Performance Comparison

| Mode | Memory | Speed | Best For |
|------|--------|-------|----------|
| Byte | Lowest | Fastest | General purpose, production |
| CANINE | Medium | Medium | Multilingual, character-aware |
| T-FREE | Highest | Research | Vocabulary analysis, interpretability |

## Documentation

- 📖 [API Reference](docs/API_REFERENCE.md) - Complete API documentation
- 📝 [Examples](docs/EXAMPLES.md) - From basic to advanced usage
- 🔧 [Implementation Details](docs/IMPLEMENTATION_SUMMARY.md) - Technical overview

## Requirements

- Python >= 3.8
- PyTorch >= 1.9.0
- NumPy >= 1.19.0

## Contributing
Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them.
4. Push your branch and create a pull request.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.