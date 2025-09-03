import torch
from torch import Tensor, nn
from lt_utils.common import *
from torch.nn import functional as F

def pad_to(x: Tensor, target_length: int, pad_value: float = 0.0) -> Tensor:
    """
    Pad input tensor along time axis (dim=1) to target length.
    Args:
        x (Tensor): Input tensor [B, T, C]
        target_length (int): Target time length
        pad_value (float): Fill value
    Returns:
        Padded tensor [B, target_length, C]
    """
    B, T, C = x.size()
    if T >= target_length:
        return x
    pad = x.new_full((B, target_length - T, C), pad_value)
    return torch.cat([x, pad], dim=1)


def batch_pad(tensors: list[Tensor], padding_value: float = 0.0) -> Tensor:
    """Pads a list of tensors to the same shape (assumes 2D+ tensors)."""
    max_shape = [
        max(s[i] for s in [t.shape for t in tensors]) for i in range(tensors[0].dim())
    ]
    padded = []
    for t in tensors:
        pad_dims = [(0, m - s) for s, m in zip(t.shape, max_shape)]
        pad_flat = [p for pair in reversed(pad_dims) for p in pair]  # reverse for F.pad
        padded.append(F.pad(t, pad_flat, value=padding_value))
    return torch.stack(padded)


def pad_sequence(
    inputs: Tensor,
    size: int,
    direction: Literal["left", "right"] = "left",
    pad_id: Union[int, float] = 0,
) -> Tensor:
    """
    Pads a single tensor to the specified size in 1D.
    Args:
        inputs (Tensor): Tensor of shape [T] or [B, T]
        size (int): Desired size along the last dimension
        direction (str): 'left' or 'right'
        pad_id (int): Value to pad with
    Returns:
        Padded tensor
    """
    total = size - inputs.shape[-1]
    if total < 1:
        return inputs
    pad_config = (total, 0) if direction == "left" else (0, total)
    return torch.nn.functional.pad(inputs, pad_config, value=pad_id)


def pad_batch_1d(
    batch: List[Tensor],
    pad_value: float = 0.0,
    pad_to_multiple: Optional[int] = None,
    direction: Literal["left", "right"] = "right",
) -> Tuple[Tensor, Tensor]:
    """
    Pad list of 1D tensors to same length with optional multiple alignment.
    Returns:
        Padded tensor [B, T], Lengths [B]
    """
    lengths = torch.tensor([t.size(0) for t in batch])
    max_len = lengths.max().item()

    if pad_to_multiple:
        max_len = ((max_len + pad_to_multiple - 1) // pad_to_multiple) * pad_to_multiple

    padded = []
    for t in batch:
        padded.append(pad_sequence(t, max_len, direction, pad_value))
    return torch.stack(padded), lengths


def pad_batch_2d(
    batch: List[Tensor],
    pad_value: float = 0.0,
    pad_to_multiple: Optional[int] = None,
    direction: Literal["left", "right"] = "right",
) -> Tuple[Tensor, Tensor]:
    """
    Pad list of 2D tensors (e.g. [T, D]) to same T.
    Returns:
        Padded tensor [B, T, D], Lengths [B]
    """
    lengths = torch.tensor([t.size(0) for t in batch])
    feat_dim = batch[0].size(1)
    max_len = lengths.max().item()

    if pad_to_multiple:
        max_len = ((max_len + pad_to_multiple - 1) // pad_to_multiple) * pad_to_multiple

    padded = []
    for t in batch:
        pad_len = max_len - t.size(0)
        if direction == "left":
            pad_tensor = t.new_full((pad_len, feat_dim), pad_value)
            padded.append(torch.cat([pad_tensor, t], dim=0))
        else:
            pad_tensor = t.new_full((pad_len, feat_dim), pad_value)
            padded.append(torch.cat([t, pad_tensor], dim=0))
    return torch.stack(padded), lengths


# --- Batching ---


def pad_batch_1d(
    batch: List[Tensor],
    pad_value: float = 0.0,
    pad_to_multiple: Optional[int] = None,
    direction: Literal["left", "right"] = "right",
) -> Tuple[Tensor, Tensor]:
    """Pads list of 1D tensors → [B, T]"""
    lengths = torch.tensor([t.size(0) for t in batch])
    max_len = lengths.max().item()
    if pad_to_multiple:
        max_len = ((max_len + pad_to_multiple - 1) // pad_to_multiple) * pad_to_multiple

    padded = [pad_sequence(t, max_len, direction, pad_value) for t in batch]
    return torch.stack(padded), lengths


def pad_batch_2d(
    batch: List[Tensor],
    pad_value: float = 0.0,
    pad_to_multiple: Optional[int] = None,
    direction: Literal["left", "right"] = "right",
) -> Tuple[Tensor, Tensor]:
    """Pads list of 2D tensors [T, D] → [B, T, D]"""
    lengths = torch.tensor([t.size(0) for t in batch])
    feat_dim = batch[0].size(1)
    max_len = lengths.max().item()
    if pad_to_multiple:
        max_len = ((max_len + pad_to_multiple - 1) // pad_to_multiple) * pad_to_multiple

    padded = []
    for t in batch:
        pad_len = max_len - t.size(0)
        pad_tensor = t.new_full((pad_len, feat_dim), pad_value)
        padded_tensor = (
            torch.cat([pad_tensor, t], dim=0)
            if direction == "left"
            else torch.cat([t, pad_tensor], dim=0)
        )
        padded.append(padded_tensor)
    return torch.stack(padded), lengths


def pad_batch_nd(
    batch: List[Tensor],
    pad_value: float = 0.0,
    dim: int = 0,
    pad_to_multiple: Optional[int] = None,
) -> Tuple[Tensor, Tensor]:
    """
    General N-D padding along time axis (dim=0, usually).
    Handles shapes like:
        [T, C] → [B, T, C]
        [T, H, W] → [B, T, H, W]
    """
    lengths = torch.tensor([t.size(dim) for t in batch])
    max_len = lengths.max().item()
    if pad_to_multiple:
        max_len = ((max_len + pad_to_multiple - 1) // pad_to_multiple) * pad_to_multiple

    padded = []
    for t in batch:
        pad_len = max_len - t.size(dim)
        pad_shape = list(t.shape)
        pad_shape[dim] = pad_len
        pad_tensor = t.new_full(pad_shape, pad_value)
        padded_tensor = torch.cat([t, pad_tensor], dim=dim)
        padded.append(padded_tensor)

    return torch.stack(padded), lengths


def pack_sequence(x: Tensor, lengths: Tensor):
    """
    Pack padded sequence for RNN/LSTM.
    Args:
        x (Tensor): Padded input [B, T, C]
        lengths (Tensor): Actual lengths [B]
    Returns:
        PackedSequence

    """
    return nn.utils.rnn.pack_padded_sequence(
        x,
        lengths.cpu().numpy(),
        batch_first=True,
        enforce_sorted=False,
    )


def unpack_sequence(
    packed: nn.utils.rnn.PackedSequence,
    total_length: Optional[int] = None,
    batch_first: bool = True,
    padding_value: float = 0,
) -> Tensor:
    """Unpacks RNN PackedSequence to padded [B, T, C].
    Returns:
        Tensor: Containing the padded sequence.
    """
    output, _ = nn.utils.rnn.pad_packed_sequence(
        packed,
        batch_first=batch_first,
        total_length=total_length,
        padding_value=padding_value,
    )
    return output
