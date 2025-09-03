from dataclasses import dataclass
from typing import List, Optional, Tuple, Literal, Dict

import torch
import torch.nn as nn
import torch.nn.functional as F

from .tfree import TFreeEncoder, TFreeMLHead
from .canine import CanineEmbedding, CanineDownUp
from .eva_attention import EVAAttention


@dataclass
class PreciousConfig:
    mode: Literal["tfree", "canine", "byte"] = "tfree"
    d_model: int = 512
    n_heads: int = 8
    n_layers: int = 4
    max_len: int = 1024
    tfree_vocab_v: int = 8192
    tfree_m: int = 10
    tfree_k_lower: int = 0
    canine_K: int = 8
    canine_B: int = 16384
    canine_use_ngrams: bool = False
    canine_down_rate: int = 4


class PositionalEncoding(nn.Module):
    def __init__(self, d_model: int, max_len: int = 4096):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-torch.log(torch.tensor(10000.0)) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe.unsqueeze(0))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x + self.pe[:, :x.size(1), :]


class TransformerBlock(nn.Module):
    def __init__(self, d_model: int, n_heads: int, dropout: float = 0.1, causal: bool = False):
        super().__init__()
        self.q = nn.Linear(d_model, d_model)
        self.k = nn.Linear(d_model, d_model)
        self.v = nn.Linear(d_model, d_model)
        self.attn = EVAAttention(dropout=dropout, causal=causal)
        self.proj = nn.Linear(d_model, d_model)
        self.ln1 = nn.LayerNorm(d_model)
        self.ln2 = nn.LayerNorm(d_model)
        self.ff = nn.Sequential(
            nn.Linear(d_model, 4*d_model), nn.GELU(), nn.Linear(4*d_model, d_model)
        )
        self.n_heads = n_heads
        self.d_head = d_model // n_heads

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, N, D = x.shape
        h = self.ln1(x)
        q = self.q(h).view(B, N, self.n_heads, self.d_head).transpose(1, 2)
        k = self.k(h).view(B, N, self.n_heads, self.d_head).transpose(1, 2)
        v = self.v(h).view(B, N, self.n_heads, self.d_head).transpose(1, 2)
        a = self.attn(q, k, v)
        a = a.transpose(1, 2).contiguous().view(B, N, D)
        x = x + self.proj(a)
        h = self.ln2(x)
        x = x + self.ff(h)
        return x


class PreciousModel(nn.Module):
    def __init__(self, config: PreciousConfig):
        super().__init__()
        self.cfg = config
        d = config.d_model
        self.pos = PositionalEncoding(d, max_len=config.max_len)
        self.blocks = nn.ModuleList([TransformerBlock(d, config.n_heads, causal=True) for _ in range(config.n_layers)])
        self.ln_f = nn.LayerNorm(d)

        if config.mode == "tfree":
            self.encoder = TFreeEncoder(vocab_size_v=config.tfree_vocab_v, hidden_size=d, m=config.tfree_m, k_lower=config.tfree_k_lower)
            self.head = TFreeMLHead(hidden_size=d, vocab_size_v=config.tfree_vocab_v)
        elif config.mode == "canine":
            self.embedding = CanineEmbedding(d=d, K=config.canine_K, B=config.canine_B, use_ngrams=config.canine_use_ngrams)
            self.downup = CanineDownUp(d=d, down_rate=config.canine_down_rate)
            self.byte_head = nn.Linear(d, 256)
        elif config.mode == "byte":
            self.byte_emb = nn.Embedding(256, d)
            nn.init.normal_(self.byte_emb.weight, mean=0.0, std=0.02)
            self.byte_head = nn.Linear(d, 256)
        else:
            raise ValueError("Unknown mode")

    def forward(self, inputs: List[str], targets: Optional[List[str]] = None) -> Dict[str, torch.Tensor]:
        device = next(self.parameters()).device
        B = len(inputs)
        cfg = self.cfg
        out: Dict[str, torch.Tensor] = {}

        if cfg.mode == "tfree":
            # Build vocabulary if not already built
            if not self.encoder.vocab_built and targets is not None:
                all_texts = inputs + targets
                self.encoder.build_vocabulary(all_texts)

            word_seqs = [self.encoder.split_text(x) for x in inputs]
            max_len = max((len(ws) for ws in word_seqs), default=1)
            X = torch.zeros(B, max_len, cfg.d_model, device=device)
            for b, ws in enumerate(word_seqs):
                if not ws:
                    continue
                embs = self.encoder(ws)
                X[b, :len(ws), :] = embs
            X = self.pos(X)
            for blk in self.blocks:
                X = blk(X)
            X = self.ln_f(X)
            logits_v = self.head(X)
            out["logits"] = logits_v
            if targets is not None:
                loss_total = 0.0
                count = 0
                for b in range(B):
                    ws_in = word_seqs[b]
                    ws_tgt = self.encoder.split_text(targets[b]) if b < len(targets) else []
                    L = min(len(ws_in), logits_v.size(1))
                    for t in range(L):
                        if t + 1 < len(ws_tgt):  # Predict next word
                            ids = self.encoder.word_indices(ws_tgt[t + 1])
                            if len(ids) == 0:
                                # For OOV words, use a dummy loss
                                dummy_target = torch.zeros(cfg.tfree_vocab_v, device=device)
                                dummy_target[0] = 1.0  # UNK token
                                loss_total = loss_total + F.binary_cross_entropy_with_logits(logits_v[b, t], dummy_target)
                            else:
                                y = torch.zeros(cfg.tfree_vocab_v, device=device)
                                y[torch.tensor(ids, dtype=torch.long, device=device)] = 1.0
                                loss_total = loss_total + F.binary_cross_entropy_with_logits(logits_v[b, t], y)
                            count += 1
                if count > 0:
                    out["loss"] = loss_total / count
            return out

        elif cfg.mode == "canine":
            embs_list = [self.embedding(x) for x in inputs]
            max_len = max((e.size(0) for e in embs_list), default=1)
            X = torch.zeros(B, max_len, cfg.d_model, device=device)
            mask = torch.zeros(B, max_len, dtype=torch.bool, device=device)
            for b, e in enumerate(embs_list):
                n = e.size(0)
                X[b, :n, :] = e
                mask[b, :n] = 1
            X = self.downup(X)
            X = self.pos(X)
            for blk in self.blocks:
                X = blk(X)
            X = self.ln_f(X)
            logits = self.byte_head(X)
            out["logits"] = logits
            if targets is not None:
                loss_total = 0.0
                count = 0
                for b, text in enumerate(targets):
                    tgt = torch.tensor([ord(c) % 256 for c in text], dtype=torch.long, device=device)
                    n = min(tgt.numel(), logits.size(1))
                    if n <= 1:
                        continue
                    loss = F.cross_entropy(logits[b, :n-1], tgt[1:n])
                    loss_total += loss
                    count += 1
                if count > 0:
                    out["loss"] = loss_total / count
            return out

        else:
            ids_list = [torch.tensor([ord(c) % 256 for c in x], dtype=torch.long, device=device) for x in inputs]
            max_len = max((ids.numel() for ids in ids_list), default=1)
            X = torch.zeros(B, max_len, cfg.d_model, device=device)
            for b, ids in enumerate(ids_list):
                n = ids.numel()
                if n == 0:
                    continue
                X[b, :n, :] = self.byte_emb(ids)
            X = self.pos(X)
            for blk in self.blocks:
                X = blk(X)
            X = self.ln_f(X)
            logits = self.byte_head(X)
            out["logits"] = logits
            if targets is not None:
                loss_total = 0.0
                count = 0
                for b, text in enumerate(targets):
                    tgt = torch.tensor([ord(c) % 256 for c in text], dtype=torch.long, device=device)
                    n = min(tgt.numel(), logits.size(1))
                    if n <= 1:
                        continue
                    loss = F.cross_entropy(logits[b, :n-1], tgt[1:n])
                    loss_total += loss
                    count += 1
                if count > 0:
                    out["loss"] = loss_total / count
            return out
