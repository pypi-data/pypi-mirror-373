import torch
from torch import Tensor, nn
from torch.nn import functional as F
from lt_utils.common import *
from lt_tensor._other_ops.torchaudio.functionals import (
    combine_max,
    median_smoothing,
    compute_mat_trace,
    tik_reg,
    compute_nccf,
    find_max_per_frame,
    rnnt_loss,
    apply_convolve_mode,
)
import numpy as np


def sin_freq(x: Tensor, freq: float = 1.0) -> Tensor:
    """Applies sine function element-wise."""
    return torch.sin(x * freq)


def cos_freq(x: Tensor, freq: float = 1.0) -> Tensor:
    """Applies cosine function element-wise."""
    return torch.cos(x * freq)


def sin_plus_cos(x: Tensor, freq: float = 1.0) -> Tensor:
    """Returns sin(x) + cos(x)."""
    return torch.sin(x * freq) + torch.cos(x * freq)


def sin_times_cos(x: Tensor, freq: float = 1.0) -> Tensor:
    """Returns sin(x) * cos(x)."""
    return torch.sin(x * freq) * torch.cos(x * freq)


def apply_window(x: Tensor, window_type: Literal["hann", "hamming"] = "hann") -> Tensor:
    """Applies a window function to a 1D tensor."""
    if window_type == "hamming":
        window = torch.hamming_window(x.shape[-1], device=x.device)
    else:
        window = torch.hann_window(x.shape[-1], device=x.device)
    return x * window


def shift_ring(x: Tensor, dim: int = -1) -> Tensor:
    """Circularly shifts tensor values: last becomes first (along given dim)."""
    return torch.roll(x, shifts=1, dims=dim)


def shift_time(x: Tensor, shift: int) -> Tensor:
    """Shifts tensor along time axis (last dim)."""
    return torch.roll(x, shifts=shift, dims=-1)


def dot_product(x: Tensor, y: Tensor, dim: int = -1) -> Tensor:
    """Computes dot product along the specified dimension."""
    return torch.sum(x * y, dim=dim)


def view_as_complex(tensor: Tensor):
    if not torch.is_complex(tensor):
        if tensor.size(-1) == 2:  # maybe real+imag as last dim
            return torch.view_as_complex(tensor)

        # treat as real and multiply by 1j
        return tensor * (1j)
    return tensor


def log_magnitude(stft_complex: Tensor, eps: float = 1e-5) -> Tensor:
    """
    Compute magnitude from STFT tensor.
    Args:
        stft: [B, F, T] tensor (complex or real)
    Returns:
        magnitude: [B, F, T] real tensor
    """
    if not torch.is_complex(stft):
        stft = view_as_complex(stft)
    magnitude = torch.abs(stft_complex)
    return torch.log(magnitude + eps)


def stft_phase_ola(
    stft: Tensor, n_fft: int, hop_length: int, win_length: int = None, window=None
):
    """
    Reconstruct phase (OLA style) from complex STFT.
    Args:
        stft: [B, F, T] complex tensor
        n_fft: FFT size
        hop_length: hop size
        win_length: window length
        window: torch window (optional)
    Returns:
        phase: [B, F, T] tensor of angles (radians)
    """
    # Inverse STFT (reconstruct waveform by overlap-add)
    if not torch.is_complex(stft):
        stft = view_as_complex(stft)

    wav = torch.istft(
        stft, n_fft=n_fft, hop_length=hop_length, win_length=win_length, window=window
    )
    # Forward STFT again to enforce consistency
    stft_re = torch.stft(
        wav,
        n_fft=n_fft,
        hop_length=hop_length,
        win_length=win_length,
        window=window,
        return_complex=True,
    )

    return torch.angle(stft_re)


def channel_randomizer(
    x: Tensor,
    combinations: int = 1,
    dim: int = 1,
) -> Tensor:
    """
    Randomizes channels along a dimension, with optional grouping.
    Args:
        x: Tensor [B, C, T] or [C, T]
        combinations: Number of groups/combinations to split channels into.
                groups=1 -> shuffle all channels freely
                groups=C -> no shuffle
        dim: channel dimension (1 for [B, C, T], 0 for [C, T])
    Returns:
        shuffled tensor
    """
    C = x.shape[dim]
    if C % combinations != 0:
        raise ValueError(
            f"Number of channels {C} not divisible by groups={combinations}"
        )

    # reshape into groups
    group_size = C // combinations
    shape = list(x.shape)
    shape[dim] = combinations
    shape.insert(dim + 1, group_size)
    xg = x.reshape(shape)

    # permutation of groups
    perm = torch.randperm(combinations, device=x.device)
    xg = xg.index_select(dim, perm)

    # flatten back
    x = xg.reshape(list(x.shape))
    return x


def channel_randomizer2(
    x: Tensor,
    groups: int = 1,
    dim: int = 1,
    shuffle_within: bool = False,
) -> Tensor:
    """
    Randomizes/shuffles channels in groups, optionally shuffling inside groups as well.
    Args:
        x: [B, C, T] or [C, T] tensor
        groups: number of groups to split channels into
        dim: channel dimension (default=1 for batched)
        shuffle_within: if True, shuffle channels inside each group,
                        if False, only shuffle group order
    Returns:
        shuffled tensor (detached, no graph)
    """
    C = x.shape[dim]
    if C % groups != 0:
        raise ValueError(f"Channels ({C}) must be divisible by groups={groups}")
    group_size = C // groups

    # Reshape into groups
    shape = list(x.shape)
    shape[dim] = groups
    shape.insert(dim + 1, group_size)
    xg = x.detach().reshape(shape)

    if shuffle_within:
        # Shuffle inside each group independently
        idx = np.arange(group_size)
        perms = [np.random.permutation(idx) for _ in range(groups)]
        perms = np.stack(perms)
        perms = torch.from_numpy(perms).to(x.device)

        arange_groups = torch.arange(groups, device=x.device)[:, None].expand(
            -1, group_size
        )
        xg = xg[(*[slice(None)] * dim, arange_groups, perms)]
    else:
        # Shuffle groups only
        perm = torch.randperm(groups, device=x.device)
        xg = xg.index_select(dim, perm)

    return xg.reshape(list(x.shape))


def compact_embeddings(
    x: Tensor,
    factor: int = 2,
    normalize: bool = True,
) -> Tensor:
    """
    Compact embeddings along the feature dimension by averaging groups of size `factor`.
    Args:
        x: [B, D] or [B, T, D] tensor
        factor: reduction factor
        normalize: whether to L2-normalize after compaction
    Returns:
        compacted tensor with reduced feature dimension
    """
    if x.shape[-1] % factor != 0:
        raise ValueError(f"Feature dim {x.shape[-1]} not divisible by factor={factor}")

    new_dim = x.shape[-1] // factor
    shape = list(x.shape[:-1]) + [new_dim, factor]
    x = x.reshape(shape).mean(dim=-1)

    if normalize:
        norm = torch.norm(x, p=2, dim=-1, keepdim=True).clamp(min=1e-8)
        x = x / norm
    return x


def normalize_unit_norm(x: Tensor, eps: float = 1e-6):
    norm = torch.norm(x, dim=-1, keepdim=True)
    return x / (norm + eps)


def normalize_minmax(x: Tensor, min_val: float = -1.0, max_val: float = 1.0) -> Tensor:
    """Scales tensor to [min_val, max_val] range."""
    x_min, x_max = x.min(), x.max()
    return (x - x_min) / (x_max - x_min + 1e-8) * (max_val - min_val) + min_val


def normalize_minmax2(x: Tensor, eps: float = 1e-6):
    min_val = x.amin(dim=-1, keepdim=True)
    max_val = x.amax(dim=-1, keepdim=True)
    return (x - min_val) / (max_val - min_val + eps)


def normalize_zscore(
    x: Tensor, dim: int = -1, keep_dims: bool = True, eps: float = 1e-7
):
    mean = x.mean(dim=dim, keepdim=keep_dims)
    std = x.std(dim=dim, keepdim=keep_dims)
    return (x - mean) / (std + eps)


def spectral_norm(x: Tensor, c: int = 1, eps: float = 1e-5) -> Tensor:
    return torch.log(torch.clamp(x, min=eps) * c)


def spectral_de_norm(x: Tensor, c: int = 1) -> Tensor:
    return torch.exp(x) / c


def log_norm(self, entry: Tensor, mean: float, std: float, eps: float = 1e-5) -> Tensor:
    return (eps + entry.log() - mean) / max(std, 1e-7)


def clip_gradients(model: nn.Module, max_norm: float = 1.0):
    """Applies gradient clipping."""
    return nn.utils.clip_grad_norm_(model.parameters(), max_norm)


def detach(entry: Union[Tensor, Tuple[Tensor, ...]]):
    """Detaches tensors (for RNNs)."""
    if isinstance(entry, Tensor):
        return entry.detach()
    return tuple(detach(h) for h in entry)


def one_hot(labels: Tensor, num_classes: int) -> Tensor:
    """One-hot encodes a tensor of labels."""
    return F.one_hot(labels, num_classes).float()


def non_zero(value: Union[float, Tensor], eps: float = 1e-7):

    _value = value.item() if isinstance(value, Tensor) else value

    if not _value:
        return value + eps
    return value


def safe_divide(a: Tensor, b: Tensor, eps: float = 1e-8):
    """Safe division for tensors (prevents divide-by-zero)."""
    return a / non_zero(b, eps)


def is_same_dim(tensor1: Tensor, tensor2: Tensor):
    return tensor1.ndim == tensor2.ndim


def is_same_shape(tensor1: Tensor, tensor2: Tensor, dim: Optional[int] = None):
    return tensor1.size(dim) == tensor2.size(dim)


def to_device(tensor: Tensor, tensor_b: Tensor):
    if tensor.device == tensor_b.device:
        return tensor
    return tensor.to(tensor_b.device)
