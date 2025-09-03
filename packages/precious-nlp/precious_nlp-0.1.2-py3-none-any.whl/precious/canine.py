from dataclasses import dataclass
import torch
import torch.nn as nn


class CanineEmbedding(nn.Module):
    def __init__(self, d: int, K: int, B: int, use_ngrams: bool = False):
        super().__init__()
        self.d = d
        self.K = K
        self.B = B
        self.use_ngrams = use_ngrams
        self.embedding = nn.Embedding(B, d)

    def forward(self, x: str) -> torch.Tensor:
        # Convert input string to tensor of indices
        indices = torch.tensor([ord(c) % self.B for c in x], dtype=torch.long)
        return self.embedding(indices)


class CanineDownUp(nn.Module):
    def __init__(self, d: int, down_rate: int):
        super().__init__()
        self.down_rate = down_rate
        self.down_proj = nn.Linear(d, d // down_rate)
        self.up_proj = nn.Linear(d // down_rate, d)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.down_proj(x)
        x = nn.GELU()(x)
        x = self.up_proj(x)
        return x