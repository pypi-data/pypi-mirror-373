__all__ = [
    "RotaryEmbedding",
    "PositionalEncoding",
    "LearnedPositionalEncoding",
    "PwPosEncoder",
    "PwPosEncoderAlt",
    "ALiBi",
    "get_alibi_slopes",
    "apply_rotary_pos_emb",
]

import math
import torch
from torch import nn, Tensor
from typing import Optional
from torch.nn import functional as F
from lt_tensor.model_base import Model


def get_alibi_slopes(n_heads: int):
    # as in the paper
    def get_slopes_power_of_2(n):
        start = 2 ** (-(2 ** -(math.log2(n) - 3)))
        ratio = start
        return [start * ratio**i for i in range(n)]

    if math.log2(n_heads).is_integer():
        return get_slopes_power_of_2(n_heads)
    else:
        closest_power_of_2 = 2 ** math.floor(math.log2(n_heads))
        return (
            get_slopes_power_of_2(closest_power_of_2)
            + get_slopes_power_of_2(2 * closest_power_of_2)[0::2][
                : n_heads - closest_power_of_2
            ]
        )


# ---- Rotary helpers ----
def rotate_half(x):
    x1 = x[..., ::2]
    x2 = x[..., 1::2]
    return torch.stack((-x2, x1), dim=-1).reshape_as(x)


def apply_rotary_pos_emb(q, k, sin, cos):
    q_sin, q_cos = (q * sin), (q * cos)
    k_sin, k_cos = (k * sin), (k * cos)
    return q_cos + rotate_half(q_sin), k_cos + rotate_half(k_sin)


class PositionalEmbedding(nn.Module):
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        raise NotImplementedError


class PwPosEncoder(PositionalEmbedding):
    def __init__(
        self,
        emb_size: int,
        requires_grad: bool = False,
        bias: bool = True,
        deep_net: bool = False,
    ):
        super().__init__()
        self.emb_size = emb_size
        self._half = self.emb_size // 2
        self._log_1e4 = -math.log(1e4)
        self.pw = math.sqrt(2)
        self.tn = nn.Parameter(
            torch.ones(self._half),
            requires_grad=requires_grad,
        )
        self.proj_out = nn.Linear(self._half, self.emb_size, bias=bias)
        self.deep_net = deep_net
        if deep_net:
            nn.init.xavier_normal_(self.proj_out, gain=nn.init.calculate_gain("linear"))

    def forward(self, x: torch.Tensor):
        freq = torch.exp(self._log_1e4 * self.tn / self._half)
        residual = x[:, ...] / self.pw
        emb = self.proj_out(x[:, ...] * freq[..., :]) + residual
        return emb.view(emb.shape[0], emb.shape[-2], emb.shape[-1]).contiguous()


class PwPosEncoderAlt(PositionalEmbedding):
    def __init__(self, emb_size: int, requires_grad=False, bias=True, deep_net=False):
        super().__init__()
        self.emb_size = emb_size
        self._half = emb_size // 2
        self._log_1e4 = -math.log(1e4)
        self.pw = math.sqrt(2)
        self.tn = nn.Parameter(torch.ones(self._half), requires_grad=requires_grad)
        self.proj_out = nn.Linear(self._half, emb_size, bias=bias)
        if deep_net:
            nn.init.xavier_normal_(
                self.proj_out.weight, gain=nn.init.calculate_gain("linear")
            )

    def forward(self, positions: torch.Tensor):
        freq = torch.exp(self._log_1e4 * self.tn / self._half)
        residual = positions / self.pw
        emb = self.proj_out(positions * freq) + residual
        return emb


class RotaryEmbedding(nn.Module):
    def __init__(self, dim: int, base: int = 10000):
        """
        Rotary Positional Embedding Module.
        Args:
            dim (int): The dimension of the rotary embedding (must be even).
            base (int): The base frequency scale (default: 10000).
        """
        super().__init__()
        assert dim % 2 == 0, "Rotary dimension must be even"
        self.dim = dim
        self.base = base

    def forward(self, x, seq_len=None):
        """
        Apply rotary embeddings to input tensor.
        Args:
            x (torch.Tensor): Input tensor of shape [batch, seq_len, dim].
            seq_len (int, optional): Override for sequence length.
        Returns:
            torch.Tensor: Tensor with rotary embeddings applied.
        """
        bsz, seq_len = x.shape[0], seq_len or x.shape[1]
        device = x.device

        pos = torch.arange(seq_len, dtype=torch.float32, device=device).unsqueeze(1)
        freqs = torch.pow(
            self.base, -torch.arange(0, self.dim, 2, device=device).float() / self.dim
        )
        angle = pos * freqs  # [seq_len, dim/2]

        sin = torch.sin(angle)
        cos = torch.cos(angle)

        # Expand and interleave to [seq_len, dim]
        sin = torch.stack((sin, sin), dim=-1).reshape(seq_len, self.dim)
        cos = torch.stack((cos, cos), dim=-1).reshape(seq_len, self.dim)

        sin = sin.unsqueeze(0).expand(bsz, -1, -1)  # [batch, seq_len, dim]
        cos = cos.unsqueeze(0).expand(bsz, -1, -1)
        return sin, cos

    def apply_rotary_b(self, x: torch.Tensor, seq_len: int):
        sin, cos = self.forward(x, seq_len)
        x1, x2 = x.chunk(2, dim=-1)
        return torch.cat((x1 * cos - x2 * sin, x2 * cos + x1 * sin), dim=-1)

    def apply_rotary_a(self, x: torch.Tensor, seq_len: int):
        sin, cos = self.forward(x, seq_len)

        b, s, d = x.shape
        x = x.view(b, s, d // 2, 2)  # [b, s, d//2, 2]
        sin = sin.view(b, s, d // 2, 2)
        cos = cos.view(b, s, d // 2, 2)

        # Apply rotation: even, odd = x[..., 0], x[..., 1]
        x_rotated = torch.stack(
            [
                x[..., 0] * cos[..., 0] - x[..., 1] * sin[..., 0],
                x[..., 0] * sin[..., 0] + x[..., 1] * cos[..., 0],
            ],
            dim=-1,
        )

        return x_rotated.view(b, s, d)  # Back to [b, s, d]


class ALiBi(Model):
    def __init__(self, num_heads: int):
        super().__init__()
        self.num_heads = num_heads
        slopes = self._get_slopes(num_heads)
        self.register_buffer("slopes", slopes, persistent=False)

    @staticmethod
    def _get_slopes(n):
        def get_slopes_power_of_2(n):
            start = 2.0 ** (-(2.0 ** -(math.log2(n) - 3)))
            ratio = start
            return [start * (ratio**i) for i in range(n)]

        if math.log2(n).is_integer():
            slopes = get_slopes_power_of_2(n)
        else:
            closest_power_of_2 = 2 ** math.floor(math.log2(n))
            slopes = get_slopes_power_of_2(closest_power_of_2)
            slopes += get_slopes_power_of_2(2 * closest_power_of_2)[0::2][
                : n - closest_power_of_2
            ]
        return torch.tensor(slopes, dtype=torch.float32)

    def forward(self, seq_len: int, device=None):
        # [seq_len, seq_len] relative distances: key positions minus query positions
        pos = torch.arange(seq_len, device=device)
        rel_pos = (
            pos[None, :] - pos[:, None]
        )  # shape: [seq_len, seq_len], negative below diagonal

        # Expand slopes: [num_heads, 1, 1]
        slopes = self.slopes[:, None, None].to(device)

        # ALiBi bias = slope * relative_distance (broadcasted)
        bias = (
            slopes * rel_pos[None, :, :].float()
        )  # shape: [num_heads, seq_len, seq_len]
        return bias

    def apply_alibi(self, attn_scores: torch.Tensor):
        b, h, s_q, s_k = attn_scores.shape
        bias = self.forward(s_k, device=attn_scores.device)
        return attn_scores + bias.unsqueeze(0)  # broadcast batch dim


class PositionalEncoding(nn.Module):
    def __init__(self, d_model: int, max_len: int = 8192):
        super().__init__()
        # create a matrix of [seq_len, hidden_dim] representing positional encoding for each token in sequence
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(
            1
        )  # (max_len, 1)
        div_term = torch.exp(
            torch.arange(0, d_model, 2, dtype=torch.float)
            * (-math.log(10000.0) / d_model)
        )
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)
        self.register_buffer("pe", pe, persistent=False)  # Shape: (1, max_len, d_model)

    def forward(self, x: Tensor, seq_len: Optional[Tensor] = None):
        # x shape: (batch_size, seq_len, d_model)
        s_sz = seq_len or x.size(1)
        x = x + self.pe[:, :s_sz]
        return x


class LearnedPositionalEncoding(nn.Module):
    def __init__(self, max_len: int, dim_model: int, dropout: float = 0.1):
        super().__init__()
        self.embedding = nn.Embedding(max_len, dim_model)
        self.dropout = nn.Dropout(dropout)
        self.max_len = max_len

    def forward(self, x: torch.Tensor, offset: int = 0) -> torch.Tensor:
        # x: [B, T, D] or [T, D]
        seq_len = x.size(1 if x.dim() == 3 else 0)
        if seq_len + offset > self.max_len:
            raise ValueError(
                f"Sequence length {seq_len + offset} exceeds max length {self.max_len}"
            )
        positions = torch.arange(offset, offset + seq_len, device=x.device)
        pos_embed = self.embedding(positions)
        if x.dim() == 3:
            pos_embed = pos_embed.unsqueeze(0).expand(x.size(0), -1, -1)  # [B, T, D]
        return self.dropout(x + pos_embed)
