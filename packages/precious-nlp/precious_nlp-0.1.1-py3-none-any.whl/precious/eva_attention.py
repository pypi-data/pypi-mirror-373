import torch
import torch.nn as nn
import torch.nn.functional as F


class EVAAttention(nn.Module):
    """
    Enhanced Vanilla Attention (EVA) module with optional causal masking.

    Args:
        dropout (float): Dropout probability for attention weights
        causal (bool): Whether to apply causal (autoregressive) masking
    """

    def __init__(self, dropout: float = 0.1, causal: bool = False):
        super().__init__()
        self.dropout = nn.Dropout(dropout)
        self.causal = causal

    def forward(self, q: torch.Tensor, k: torch.Tensor, v: torch.Tensor) -> torch.Tensor:
        """
        Forward pass of EVA attention.

        Args:
            q: Query tensor of shape [batch_size, n_heads, seq_len, head_dim]
            k: Key tensor of shape [batch_size, n_heads, seq_len, head_dim]
            v: Value tensor of shape [batch_size, n_heads, seq_len, head_dim]

        Returns:
            Attention output tensor of shape [batch_size, n_heads, seq_len, head_dim]
        """
        # Compute attention scores
        scores = torch.matmul(q, k.transpose(-2, -1)) / (q.size(-1) ** 0.5)

        # Apply causal mask if specified
        if self.causal:
            seq_len = scores.size(-1)
            mask = torch.triu(torch.ones(seq_len, seq_len, device=scores.device), diagonal=1).bool()
            scores = scores.masked_fill(mask, float('-inf'))

        # Apply softmax to get attention weights
        attn_weights = F.softmax(scores, dim=-1)
        attn_weights = self.dropout(attn_weights)

        # Compute the weighted sum of values
        output = torch.matmul(attn_weights, v)
        return output
