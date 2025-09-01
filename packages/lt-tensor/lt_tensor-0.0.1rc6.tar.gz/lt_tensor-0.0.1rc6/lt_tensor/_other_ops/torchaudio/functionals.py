import math
import torch
from torch import Tensor, nn
from torch.nn import functional as F
from lt_utils.common import *


def combine_max(
    a: Tuple[Tensor, Tensor], b: Tuple[Tensor, Tensor], thresh: float = 0.99
) -> Tuple[Tensor, Tensor]:
    """
    Take value from first if bigger than a multiplicative factor of the second, elementwise.
    """
    mask = a[0] > thresh * b[0]
    values = mask * a[0] + ~mask * b[0]
    indices = mask * a[1] + ~mask * b[1]
    return values, indices


def median_smoothing(indices: Tensor, win_length: int) -> Tensor:
    """
    Apply median smoothing to the 1D tensor over the given window.
    """

    # Centered windowed
    pad_length = (win_length - 1) // 2

    # "replicate" padding in any dimension
    indices = F.pad(indices, (pad_length, 0), mode="constant", value=0.0)

    indices[..., :pad_length] = torch.cat(
        pad_length * [indices[..., pad_length].unsqueeze(-1)], dim=-1
    )
    roll = indices.unfold(-1, win_length, 1)

    values, _ = torch.median(roll, -1)
    return values


def compute_mat_trace(input: Tensor, dim1: int = -1, dim2: int = -2) -> Tensor:
    r"""Compute the trace of a Tensor along ``dim1`` and ``dim2`` dimensions.

    Args:
        input (Tensor): Tensor with dimensions `(..., channel, channel)`.
        dim1 (int, optional): The first dimension of the diagonal matrix.
            (Default: ``-1``)
        dim2 (int, optional): The second dimension of the diagonal matrix.
            (Default: ``-2``)

    Returns:
        Tensor: The trace of the input Tensor.
    """
    if input.ndim < 2:
        raise ValueError("The dimension of the tensor must be at least 2.")
    if input.shape[dim1] != input.shape[dim2]:
        raise ValueError("The size of ``dim1`` and ``dim2`` must be the same.")
    input = torch.diagonal(input, 0, dim1=dim1, dim2=dim2)
    return input.sum(dim=-1)


def tik_reg(mat: Tensor, reg: float = 1e-7, eps: float = 1e-8) -> Tensor:
    """Perform Tikhonov regularization (only modifying real part).

    Args:
        mat (Tensor): Input matrix with dimensions `(..., channel, channel)`.
        reg (float, optional): Regularization factor. (Default: 1e-8)
        eps (float, optional): Value to avoid the correlation matrix is all-zero. (Default: ``1e-8``)

    Returns:
        Tensor: Regularized matrix with dimensions `(..., channel, channel)`.
    """
    # Add eps
    C = mat.size(-1)
    eye = torch.eye(C, dtype=mat.dtype, device=mat.device)
    epsilon = compute_mat_trace(mat).real[..., None, None] * reg
    # in case that correlation_matrix is all-zero
    epsilon = epsilon + eps
    mat = mat + epsilon * eye[..., :, :]
    return mat


def compute_nccf(
    waveform: Tensor, sample_rate: int, frame_time: float, freq_low: int
) -> Tensor:
    r"""
    Compute Normalized Cross-Correlation Function (NCCF).

    .. math::
        \phi_i(m) = \frac{\sum_{n=b_i}^{b_i + N-1} w(n) w(m+n)}{\sqrt{E(b_i) E(m+b_i)}},

    where
    :math:`\phi_i(m)` is the NCCF at frame :math:`i` with lag :math:`m`,
    :math:`w` is the waveform,
    :math:`N` is the length of a frame,
    :math:`b_i` is the beginning of frame :math:`i`,
    :math:`E(j)` is the energy :math:`\sum_{n=j}^{j+N-1} w^2(n)`.
    """

    EPSILON = 10 ** (-9)

    # Number of lags to check
    lags = int(math.ceil(sample_rate / freq_low))

    frame_size = int(math.ceil(sample_rate * frame_time))

    waveform_length = waveform.size()[-1]
    num_of_frames = int(math.ceil(waveform_length / frame_size))

    p = lags + num_of_frames * frame_size - waveform_length
    waveform = torch.nn.functional.pad(waveform, (0, p))

    # Compute lags
    output_lag = []
    for lag in range(1, lags + 1):
        s1 = waveform[..., :-lag].unfold(-1, frame_size, frame_size)[
            ..., :num_of_frames, :
        ]
        s2 = waveform[..., lag:].unfold(-1, frame_size, frame_size)[
            ..., :num_of_frames, :
        ]

        output_frames = (
            (s1 * s2).sum(-1)
            / (EPSILON + torch.linalg.vector_norm(s1, ord=2, dim=-1)).pow(2)
            / (EPSILON + torch.linalg.vector_norm(s2, ord=2, dim=-1)).pow(2)
        )

        output_lag.append(output_frames.unsqueeze(-1))

    nccf = torch.cat(output_lag, -1)

    return nccf


def find_max_per_frame(nccf: Tensor, sample_rate: int, freq_high: int) -> Tensor:
    r"""
    For each frame, take the highest value of NCCF,
    apply centered median smoothing, and convert to frequency.

    Note: If the max among all the lags is very close
    to the first half of lags, then the latter is taken.
    """

    lag_min = int(math.ceil(sample_rate / freq_high))

    # Find near enough max that is smallest

    best = torch.max(nccf[..., lag_min:], -1)

    half_size = nccf.shape[-1] // 2
    half = torch.max(nccf[..., lag_min:half_size], -1)

    best = combine_max(half, best)
    indices = best[1]

    # Add back minimal lag
    indices += lag_min
    # Add 1 empirical calibration offset
    indices += 1
    return indices


def rnnt_loss(
    logits: Tensor,
    targets: Tensor,
    logit_lengths: Tensor,
    target_lengths: Tensor,
    blank: int = -1,
    clamp: float = -1,
    reduction: Optional[Literal["mean", "sum"]] = "mean",
    fused_log_softmax: bool = True,
):
    """Compute the RNN Transducer loss from *Sequence Transduction with Recurrent Neural Networks*
    :cite:`graves2012sequence`.

    .. devices:: CPU CUDA

    .. properties:: Autograd TorchScript

    The RNN Transducer loss extends the CTC loss by defining a distribution over output
    sequences of all lengths, and by jointly modelling both input-output and output-output
    dependencies.

    Args:
        logits (Tensor): Tensor of dimension `(batch, max seq length, max target length + 1, class)`
            containing output from joiner
        targets (Tensor): Tensor of dimension `(batch, max target length)` containing targets with zero padded
        logit_lengths (Tensor): Tensor of dimension `(batch)` containing lengths of each sequence from encoder
        target_lengths (Tensor): Tensor of dimension `(batch)` containing lengths of targets for each sequence
        blank (int, optional): blank label (Default: ``-1``)
        clamp (float, optional): clamp for gradients (Default: ``-1``)
        reduction (string, optional): Specifies the reduction to apply to the output:
            ``None`` | ``"mean"`` | ``"sum"``. (Default: ``"mean"``)
        fused_log_softmax (bool): set to False if calling log_softmax outside of loss (Default: ``True``)
    Returns:
        Tensor: Loss with the reduction option applied. If ``reduction`` is  ``"none"``, then size `(batch)`,
        otherwise scalar.
    """
    assert (
        reduction in ["mean", "sum"] or reduction is None
    ), f'reduction should be one of  "mean", or "sum" or None. Received instead {reduction}'

    if blank < 0:  # reinterpret blank index if blank < 0.
        blank = logits.shape[-1] + blank

    costs, _ = torch.ops.torchaudio.rnnt_loss(
        logits=logits,
        targets=targets,
        logit_lengths=logit_lengths,
        target_lengths=target_lengths,
        blank=blank,
        clamp=clamp,
        fused_log_softmax=fused_log_softmax,
    )

    if reduction == "mean":
        return costs.mean()
    elif reduction == "sum":
        return costs.sum()

    return costs


def apply_convolve_mode(
    conv_result: Tensor, x_length: int, y_length: int, mode: str
) -> Tensor:
    valid_convolve_modes = ["full", "valid", "same"]
    assert (
        mode in valid_convolve_modes
    ), f"Unrecognized mode value '{mode}'. Please specify one of {valid_convolve_modes}."
    if mode == "full":
        return conv_result
    elif mode == "valid":
        target_length = max(x_length, y_length) - min(x_length, y_length) + 1
        start_idx = (conv_result.size(-1) - target_length) // 2
        return conv_result[..., start_idx : start_idx + target_length]
    # else 'same'
    start_idx = (conv_result.size(-1) - x_length) // 2
    return conv_result[..., start_idx : start_idx + x_length]
