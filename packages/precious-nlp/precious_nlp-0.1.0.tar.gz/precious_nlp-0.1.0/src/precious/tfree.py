import re
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import List, Dict, Set
from collections import defaultdict


class TFreeEncoder(nn.Module):
    """
    T-FREE (Tokenizer-FREE) Encoder implementation.

    This encoder processes text without traditional tokenization by:
    1. Splitting text into words using simple whitespace/punctuation rules
    2. Creating embeddings for frequent words and character-level fallbacks
    3. Using a multi-level vocabulary approach

    Args:
        vocab_size_v: Size of the word-level vocabulary
        hidden_size: Hidden dimension size
        m: Maximum word length for character-level encoding
        k_lower: Minimum frequency threshold for word inclusion
    """

    def __init__(self, vocab_size_v: int, hidden_size: int, m: int, k_lower: int):
        super().__init__()
        self.vocab_size_v = vocab_size_v
        self.hidden_size = hidden_size
        self.m = m
        self.k_lower = k_lower

        # Word-level embedding for frequent words
        self.word_embedding = nn.Embedding(vocab_size_v, hidden_size)

        # Character-level embedding for OOV words
        self.char_embedding = nn.Embedding(256, hidden_size // 4)  # Smaller char embeddings

        # Character-level LSTM for composing word embeddings
        self.char_lstm = nn.LSTM(
            input_size=hidden_size // 4,
            hidden_size=hidden_size // 2,
            num_layers=1,
            batch_first=True,
            bidirectional=True
        )

        # Projection layer to combine word and character representations
        self.projection = nn.Linear(hidden_size, hidden_size)

        # Initialize vocabulary mappings
        self.word_to_idx: Dict[str, int] = {}
        self.idx_to_word: Dict[int, str] = {}
        self.word_frequencies: Dict[str, int] = defaultdict(int)
        self.vocab_built = False

        # Special tokens
        self.UNK_IDX = 0
        self.PAD_IDX = 1
        self.word_to_idx["<UNK>"] = self.UNK_IDX
        self.word_to_idx["<PAD>"] = self.PAD_IDX
        self.idx_to_word[self.UNK_IDX] = "<UNK>"
        self.idx_to_word[self.PAD_IDX] = "<PAD>"

        # Initialize embeddings
        nn.init.normal_(self.word_embedding.weight, mean=0.0, std=0.02)
        nn.init.normal_(self.char_embedding.weight, mean=0.0, std=0.02)

    def split_text(self, text: str) -> List[str]:
        """
        Split text into words using simple rules.

        Args:
            text: Input text string

        Returns:
            List of word tokens
        """
        if not text.strip():
            return []

        # Simple splitting on whitespace and basic punctuation
        # This is a simplified approach - could be made more sophisticated
        words = re.findall(r'\b\w+\b|[^\w\s]', text.lower())
        return [word for word in words if word.strip()]

    def build_vocabulary(self, texts: List[str]):
        """
        Build vocabulary from a list of texts.

        Args:
            texts: List of text strings for vocabulary building
        """
        # Count word frequencies
        for text in texts:
            words = self.split_text(text)
            for word in words:
                self.word_frequencies[word] += 1

        # Select frequent words for vocabulary
        frequent_words = [
            word for word, freq in self.word_frequencies.items()
            if freq >= self.k_lower
        ]

        # Sort by frequency for consistent ordering
        frequent_words.sort(key=lambda x: (-self.word_frequencies[x], x))

        # Add frequent words to vocabulary (reserve space for special tokens)
        next_idx = 2  # After UNK and PAD
        for word in frequent_words[:self.vocab_size_v - 2]:
            self.word_to_idx[word] = next_idx
            self.idx_to_word[next_idx] = word
            next_idx += 1

        self.vocab_built = True

    def encode_word_char_level(self, word: str) -> torch.Tensor:
        """
        Encode a word using character-level LSTM.

        Args:
            word: Input word string

        Returns:
            Word embedding tensor of shape [hidden_size]
        """
        if len(word) == 0:
            return torch.zeros(self.hidden_size, device=self.char_embedding.weight.device)

        # Truncate or pad word to maximum length
        chars = list(word.lower()[:self.m])

        # Convert characters to indices
        char_indices = torch.tensor(
            [min(ord(c), 255) for c in chars],
            dtype=torch.long,
            device=self.char_embedding.weight.device
        ).unsqueeze(0)  # Add batch dimension

        # Get character embeddings
        char_embeds = self.char_embedding(char_indices)  # [1, seq_len, embed_dim]

        # Pass through LSTM
        lstm_out, (hidden, _) = self.char_lstm(char_embeds)

        # Use the final hidden state (concatenated from both directions)
        word_embed = hidden.transpose(0, 1).contiguous().view(1, -1).squeeze(0)  # [hidden_size]

        return word_embed

    def forward(self, word_seqs: List[str]) -> torch.Tensor:
        """
        Forward pass of the T-FREE encoder.

        Args:
            word_seqs: List of word strings

        Returns:
            Word embeddings tensor of shape [len(word_seqs), hidden_size]
        """
        if not word_seqs:
            return torch.zeros(0, self.hidden_size, device=self.word_embedding.weight.device)

        device = self.word_embedding.weight.device
        embeddings = []

        for word in word_seqs:
            if word in self.word_to_idx:
                # Use word-level embedding
                word_idx = torch.tensor(self.word_to_idx[word], dtype=torch.long, device=device)
                word_embed = self.word_embedding(word_idx)
            else:
                # Use character-level encoding for OOV words
                word_embed = self.encode_word_char_level(word)

            embeddings.append(word_embed)

        # Stack embeddings
        embeddings_tensor = torch.stack(embeddings, dim=0)  # [seq_len, hidden_size]

        # Apply projection layer
        embeddings_tensor = self.projection(embeddings_tensor)

        return embeddings_tensor

    def word_indices(self, word: str) -> List[int]:
        """
        Get vocabulary indices for a word.

        Args:
            word: Input word string

        Returns:
            List of vocabulary indices (empty if OOV)
        """
        word_lower = word.lower()
        if word_lower in self.word_to_idx:
            return [self.word_to_idx[word_lower]]
        else:
            return []  # OOV word

    def get_vocab_size(self) -> int:
        """Get the current vocabulary size."""
        return len(self.word_to_idx)

    def get_word_frequency(self, word: str) -> int:
        """Get the frequency of a word in the training data."""
        return self.word_frequencies.get(word.lower(), 0)


class TFreeMLHead(nn.Module):
    """
    Multi-label head for T-FREE model that can predict multiple vocabulary items.
    """

    def __init__(self, hidden_size: int, vocab_size_v: int):
        super().__init__()
        self.hidden_size = hidden_size
        self.vocab_size_v = vocab_size_v

        # Multi-layer perceptron for vocabulary prediction
        self.mlp = nn.Sequential(
            nn.Linear(hidden_size, hidden_size * 2),
            nn.GELU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_size * 2, hidden_size),
            nn.GELU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_size, vocab_size_v)
        )

        # Initialize weights
        for module in self.mlp:
            if isinstance(module, nn.Linear):
                nn.init.normal_(module.weight, mean=0.0, std=0.02)
                nn.init.zeros_(module.bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass of the multi-label head.

        Args:
            x: Input tensor of shape [batch_size, seq_len, hidden_size]

        Returns:
            Logits tensor of shape [batch_size, seq_len, vocab_size_v]
        """
        return self.mlp(x)
