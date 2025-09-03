import math
import torch
from torch import Tensor
from lt_utils.common import *
import torch.nn.functional as F

DeviceType: TypeAlias = Union[torch.device, str]


def stft(
    entry: Tensor,
    n_fft: int = 1024,
    hop_length: Optional[int] = None,
    win_length: Optional[int] = None,
    center: bool = True,
    return_complex: bool = True,
) -> Tensor:
    """Performs short-time Fourier transform using PyTorch."""
    results = torch.stft(
        input=entry,
        n_fft=n_fft,
        hop_length=(hop_length or n_fft // 4),
        win_length=(win_length or n_fft),
        window=torch.hann_window(win_length or n_fft, device=entry.device),
        center=center,
        return_complex=True,
    )
    if return_complex:
        return results
    return torch.view_as_real(results)


def istft(
    entry: Tensor,
    n_fft: int = 512,
    hop_length: Optional[int] = None,
    win_length: Optional[int] = None,
    center: bool = True,
    length: Optional[int] = None,
    return_complex: bool = True,
) -> Tensor:
    """Performs inverse short-time Fourier transform using PyTorch."""
    if not entry.is_complex():
        entry = torch.view_as_complex(entry)
    return torch.istft(
        input=entry,
        n_fft=n_fft,
        hop_length=(hop_length or n_fft // 4),
        win_length=(win_length or n_fft),
        window=torch.hann_window(win_length or n_fft, device=entry.device),
        center=center,
        length=length,
        return_complex=return_complex,
    )


def fft(x: Tensor, norm: Optional[str] = "backward") -> Tensor:
    """Returns the FFT of a real tensor."""
    return torch.fft.fft(x, norm=norm)


def ifft(x: Tensor, norm: Optional[str] = "backward") -> Tensor:
    """Returns the inverse FFT of a complex tensor."""
    return torch.fft.ifft(x, norm=norm)


def sp_to_linear(base: Tensor, lin_fb: Tensor, eps: float = 1e-8) -> Tensor:
    """Approximate inversion of 'base' to 'lin_fb' using pseudo-inverse."""
    mel_fb_inv = torch.pinverse(lin_fb)
    return torch.matmul(mel_fb_inv, base + eps)


def stretch_tensor(x: Tensor, rate: float, mode: str = "linear") -> Tensor:
    """Time-stretch tensor using interpolation."""
    B = 1 if x.ndim < 2 else x.shape[0]
    C = 1 if x.ndim < 3 else x.shape[-2]
    T = x.shape[-1]
    new_t = int(T * rate)
    stretched = F.interpolate(x.view(B * C, T), size=new_t, mode=mode)
    return stretched.view(B, C, new_t)


def get_sinusoidal_embedding(timesteps: Tensor, dim: int) -> Tensor:
    # Expect shape [B] or [B, 1]
    if timesteps.dim() > 1:
        timesteps = timesteps.view(-1)  # flatten to [B]

    device = timesteps.device
    half_dim = dim // 2
    emb = torch.exp(
        torch.arange(half_dim, device=device) * -(math.log(10000.0) / half_dim)
    )
    emb = timesteps[:, None].float() * emb[None, :]  # [B, half_dim]
    emb = torch.cat((emb.sin(), emb.cos()), dim=-1)  # [B, dim]
    return emb


def alpha_bar_laplace(t: Number, mu: Number = 0, b: Number = 1):
    snr = mu - b * math.copysign(1, 0.5 - t) * math.log(1 - 2 * abs(t - 0.5) * 0.98)
    return 1 - 1 / (math.exp(snr) + 1.02)


def alpha_bar_cauchy(t: Number, gamma: Number = 1, mu: Number = 3):
    snr = mu + gamma * math.tan(math.pi * (0.5 - t) * 0.9)
    return 1 - 1 / (math.exp(snr) + 1.1)


def alpha_bar_exp(t: Number):
    return math.exp(t * -12.0)


def alpha_bar_cosine(t: Number):
    return math.cos((t + 0.008) / 1.008 * math.pi / 2) ** 2


def betas_for_alpha_bars(num_time_steps: int, alpha_bar_fn: Callable[[Number], Number]):
    betas = []
    for i in range(num_time_steps):
        t1 = i / num_time_steps
        t2 = (i + 1) / num_time_steps
        betas.append(min(1 - alpha_bar_fn(t2) / alpha_bar_fn(t1), num_time_steps))
    return torch.tensor(betas, dtype=torch.float32)


def rescale_zero_terminal_snr(betas: Tensor):
    """

    Rescales betas to have zero terminal SNR Based on https://arxiv.org/pdf/2305.08891.pdf (Algorithm 1)


    Args:
        betas (`Tensor`):
            the betas that the scheduler is being initialized with.

    Returns:
        `Tensor`: rescaled betas with zero terminal SNR

    Note:
        Modified from diffusers.schedulers.scheduling_ddim.rescale_zero_terminal_snr
    """
    # Convert betas to alphas_bar_sqrt
    alphas_bar_sqrt = (1.0 - betas).cumprod(dim=0).sqrt()

    # Store old values.
    alphas_bar_sqrt_0 = alphas_bar_sqrt[0].clone()
    alphas_bar_sqrt_T = alphas_bar_sqrt[-1].clone()

    # Shift so the last timestep is zero.
    alphas_bar_sqrt -= alphas_bar_sqrt_T

    # Scale so the first timestep is back to the old value.
    alphas_bar_sqrt *= alphas_bar_sqrt_0 / (alphas_bar_sqrt_0 - alphas_bar_sqrt_T)

    # Convert alphas_bar_sqrt to betas
    alphas_bar = alphas_bar_sqrt**2  # Revert sqrt
    alphas = alphas_bar[1:] / alphas_bar[:-1]  # Revert cumprod
    alphas = torch.cat([alphas_bar[0:1], alphas])
    betas = 1.0 - alphas

    return betas
