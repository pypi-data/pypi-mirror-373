"""
Precious: A tokenizer-free NLP library
======================================

Precious provides three tokenizer-free approaches for natural language processing:
- T-FREE: Vocabulary-aware approach with character-level fallback
- CANINE: Character-level processing with downsampling/upsampling
- Byte-level: Direct byte-level text processing

Example usage:
    >>> from precious import PreciousModel, PreciousConfig
    >>> config = PreciousConfig(mode="byte", d_model=256)
    >>> model = PreciousModel(config)
    >>> outputs = model(["Hello, tokenizer-free world!"])
"""

__version__ = "0.1.2"
__author__ = "bimri"
__email__ = "bimri@outlook.com"
__license__ = "MIT"

from .models import PreciousModel, PreciousConfig
from .tfree import TFreeEncoder, TFreeMLHead
from .canine import CanineEmbedding, CanineDownUp
from .eva_attention import EVAAttention

__all__ = [
    "PreciousModel",
    "PreciousConfig",
    "TFreeEncoder",
    "TFreeMLHead",
    "CanineEmbedding",
    "CanineDownUp",
    "EVAAttention",
    "__version__",
]
