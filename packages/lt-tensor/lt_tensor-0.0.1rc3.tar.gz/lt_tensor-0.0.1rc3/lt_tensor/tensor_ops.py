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
)


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


def log_magnitude(stft_complex: Tensor, eps: float = 1e-5) -> Tensor:
    """Returns log magnitude from complex STFT."""
    if not stft_complex.is_complex():
        stft_complex = torch.view_as_complex(stft_complex)
    magnitude = torch.abs(stft_complex)
    return torch.log(magnitude + eps)


def phase(stft_complex: Tensor) -> Tensor:
    """Returns phase from complex STFT."""
    if not stft_complex.is_complex():
        stft_complex = torch.view_as_complex(stft_complex)
    return torch.angle(stft_complex)


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
