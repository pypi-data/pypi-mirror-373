import torch
from torch import Tensor
from lt_utils.common import *


def apply_mask(x: Tensor, mask: Tensor, fill_value: Number = 0) -> Tensor:
    """
    Apply a mask to a tensor, setting masked positions to `fill_value`.
    Args:
        x (Tensor): Input tensor of shape [..., T, D].
        mask (Tensor): Mask of shape [..., T] where True = masked.
        fill_value (Number): Value to fill masked positions with.
    Returns:
        Tensor: Masked tensor.
    """
    return x.masked_fill(mask.unsqueeze(-1), fill_value)


def get_padding_mask(
    lengths: Optional[Tensor] = None,
    tokens: Optional[Tensor] = None,
    padding_id: int = 0,
) -> Tensor:
    """
    Generate a padding mask: 1 for real tokens, 0 for padding.
    Args:
        lengths (Tensor): Tensor of shape [B] with sequence lengths.
        tokens (Tensor): Tensor of shape [B, T] with token ids.
        padding_id (int): Padding token id (default=0).
    Returns:
        Tensor: Boolean mask of shape [B, T].
    """
    assert (
        tokens is not None or lengths is not None
    ), "Either tokens or lengths must be provided."

    if tokens is not None:
        return tokens != padding_id

    B = lengths.size(0)
    max_len = lengths.max().item()
    arange = torch.arange(max_len, device=lengths.device).unsqueeze(0).expand(B, -1)
    return arange < lengths.unsqueeze(1)


def get_padding_mask_fps(lengths: Tensor) -> Tensor:
    """
    Legacy-style padding mask using 1-based comparison.
    """
    mask = (
        torch.arange(lengths.max(), device=lengths.device)
        .unsqueeze(0)
        .expand(lengths.shape[0], -1)
    )
    return (mask + 1) > lengths.unsqueeze(1)


def get_causal_mask(
    size: Union[int, tuple[int, ...]],
    device: Optional[Union[str, torch.device]] = None,
) -> Tensor:
    """
    Generate a causal mask for self-attention.
    Args:
        size (int or tuple): Size (T) or (1, T, T)
    Returns:
        Tensor: [1, T, T] boolean causal mask
    """
    if isinstance(size, int):
        size = (1, size, size)
    return torch.tril(torch.ones(size, dtype=torch.bool, device=device))


def combine_masks(pad_mask: Tensor, causal_mask: Tensor) -> Tensor:
    """
    Combine padding and causal masks.
    Args:
        pad_mask (Tensor): [B, T] padding mask
        causal_mask (Tensor): [1, T, T] causal mask
    Returns:
        Tensor: [B, T, T] combined mask
    """
    return causal_mask & pad_mask.unsqueeze(1).expand(-1, pad_mask.size(1), -1).bool()


def length_to_mask(lengths: Tensor, xm: float = 1.0):
    l_range = torch.arange(lengths.max().item())

    mask = (
        l_range.unsqueeze(0).expand(lengths.shape[0], -1).type_as(lengths).unsqueeze(1)
    )
    return torch.gt(mask + xm, lengths)
