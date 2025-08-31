import gc
import sys
import torch
import random
import warnings
import numpy as np
from typing import TypeGuard

import torch.nn.functional as F
from torch import nn, optim, Tensor

from lt_utils.common import *


def minimum_device():
    # try to cover every scenario
    if torch.cpu.is_available():
        return torch.device("cpu")
    elif hasattr(torch, "mps") and torch.mps.is_available():
        return torch.device("mps")
    elif hasattr(torch, "cuda") and torch.cuda.is_available():
        return torch.device("cuda")
    elif hasattr(torch, "xpu") and torch.xpu.is_available():
        return torch.device("xpu")
    elif (
        hasattr(torch, "mtia")
        and hasattr(torch.mtia, "is_available")
        and torch.mtia.is_available()
    ):
        return torch.device("mtia")


ROOT_DEVICE = minimum_device()


def get_window(
    win_length: int,
    window_type: Literal["hann", "hamming"] = "hann",
    pin_memory: bool | None = False,
    requires_grad: bool | None = False,
    device: Optional[Union[str, torch.device]] = None,
    d_type: Optional[torch.dtype] = None,
) -> Tensor:
    """Applies a window function to a 1D tensor."""
    if window_type not in ["hann", "hamming"]:
        raise ValueError(
            f"window_type must be: 'hann' or 'hamming'. But received: '{window_type}'."
        )
    kwargs = dict(
        device=device, dtype=d_type, requires_grad=requires_grad, pin_memory=pin_memory
    )
    if window_type == "hamming":
        return torch.hamming_window(win_length, **kwargs)
    return torch.hann_window(win_length, **kwargs)


def to_device(tensor: Tensor, tensor_b: Tensor):
    if tensor.device == tensor_b.device:
        return tensor
    return tensor.to(tensor_b.device)


def is_fused_available():
    import inspect

    return "fused" in inspect.signature(optim.AdamW).parameters


def time_weighted_avg(data: Union[Tensor, np.ndarray], alpha: float = 0.9) -> Tensor:
    """
    Compute time-weighted moving average for smoothing.
    Args:
        data: [T] or [N, T] tensor (time series)
        alpha: smoothing factor (0 < alpha < 1), higher = smoother
    Returns:
        smoothed tensor of same shape
    """
    data = to_tensor(data).squeeze()
    if data.ndim == 1:
        out = torch.zeros_like(data)
        out[0] = data[0]
        for t in range(1, len(data)):
            out[t] = alpha * out[t - 1] + (1 - alpha) * data[t]
        return out
    elif data.ndim == 2:
        out = torch.zeros_like(data)
        out[:, 0] = data[:, 0]
        for t in range(1, data.shape[1]):
            out[:, t] = alpha * out[:, t - 1] + (1 - alpha) * data[:, t]
        return out
    else:
        raise ValueError("Data must be 1D or 2D time series")


def time_weighted_ema(data: Union[Tensor, np.ndarray], alpha: float = 0.5):
    """
    Compute the time-weighted Exponential Moving Average (EMA) for a given data array.

    Parameters:
    - data: array-like, the input data to smooth.
    - alpha: float, the smoothing factor (0 < alpha ≤ 1). Higher alpha discounts older observations faster.

    Returns:
    - ema: numpy array, the smoothed data.
    """
    data = to_numpy(data)
    ema = np.zeros_like(data)
    alpha = min(max(float(alpha), 0.00001), 0.99999)
    ema[0] = data[0]  # Initialize with the first data point
    for t in range(1, len(data)):
        ema[t] = alpha * data[t] + alpha * ema[t - 1]
    return ema


def is_tensor(item: Any) -> TypeGuard[Tensor]:
    return isinstance(item, Tensor)


def to_tensor(inp: Union[Tensor, np.ndarray, List[Number], Number]):
    if is_tensor(inp):
        return inp
    elif isinstance(inp, (int, float)):
        if isinstance(inp, int):
            return torch.tensor(inp, dtype=torch.long)
        return torch.tensor(inp)
    elif isinstance(inp, (list, tuple)):
        return torch.tensor([float(x) for x in inp if isinstance(x, (int, float))])
    elif isinstance(inp, np.ndarray):
        return torch.from_numpy(inp)
    raise ValueError(f"'{inp}' cannot be converted to tensor! (type: {type(inp)})")


def to_numpy(inp: Union[Tensor, np.ndarray, List[Number], Number]):
    if isinstance(inp, np.ndarray):
        return inp
    elif isinstance(inp, Tensor):
        return inp.detach().clone().to(device=ROOT_DEVICE).numpy(force=True)
    elif isinstance(inp, (list, tuple)):
        return np.array([float(x) for x in inp if isinstance(x, (int, float))])
    elif isinstance(inp, (int, float)):
        return np.array([float(inp)])
    raise ValueError(f"'{inp}' cannot be converted to numpy array! (type: {type(inp)})")


def update_lr(optimizer: optim.Optimizer, new_value: Union[float, Tensor] = 1e-4):
    if isinstance(new_value, (int, float)):
        new_value = float(new_value)

    elif isinstance(new_value, Tensor):
        if new_value.ndim in [0, 1]:
            try:
                new_value = float(new_value.item())
            except:
                pass

    new_value_float = isinstance(new_value, float)
    for param_group in optimizer.param_groups:
        if isinstance(param_group["lr"], Tensor) and new_value_float:
            param_group["lr"].fill_(new_value)
        else:
            param_group["lr"] = new_value
    return optimizer


def plot_view(
    data: Dict[str, List[Any]],
    title: str = "Loss",
    xaxis_title="Step/Epoch",
    yaxis_title="Loss",
    template="plotly_dark",
    smoothing: Optional[Literal["ema", "avg"]] = None,
    alpha: float = 0.5,
    *args,
    **kwargs,
):
    try:
        import plotly.graph_objs as go
    except ModuleNotFoundError:
        warnings.warn(
            "No installation of plotly was found. To use it use 'pip install plotly' and restart this application!"
        )
        return
    fig = go.Figure()
    for mode, values in data.items():
        if values:
            if not smoothing:
                items = values
            elif smoothing == "avg":
                items = time_weighted_avg(values, kwargs.get("smoothing_alpha", alpha))
            else:
                items = time_weighted_ema(values, kwargs.get("smoothing_alpha", alpha))
            fig.add_trace(go.Scatter(y=items, name=mode.capitalize()))
    fig.update_layout(
        title=title,
        xaxis_title=xaxis_title,
        yaxis_title=yaxis_title,
        template=template,
    )
    return fig


def updateDict(self, dct: dict[str, Any]):
    for k, v in dct.items():
        setattr(self, k, v)


def try_torch(fn: str, *args, **kwargs):
    tried_torch = False
    not_present_message = (
        f"Both `torch` and `torch.nn.functional` does not contain the module `{fn}`"
    )
    try:
        if hasattr(F, fn):
            return getattr(F, fn)(*args, **kwargs)
        elif hasattr(torch, fn):
            tried_torch = True
            return getattr(torch, fn)(*args, **kwargs)
        return not_present_message
    except Exception as a:
        try:
            if not tried_torch and hasattr(torch, fn):
                return getattr(torch, fn)(*args, **kwargs)
            return str(a)
        except Exception as e:
            return str(e) + " | " + str(a)


def log_tensor(
    item: Union[Tensor, np.ndarray],
    title: Optional[str] = None,
    print_details: bool = True,
    print_tensor: bool = False,
    dim: Optional[int] = None,
):
    assert isinstance(item, (Tensor, np.ndarray))
    from lt_utils.type_utils import is_str

    has_title = is_str(title)

    if has_title:
        print("========[" + title.title() + "]========")
        _b = 20 + len(title.strip())
    print(f"shape: {item.shape}")
    print(f"dtype: {item.dtype}")
    if print_details:
        print(f"ndim: {item.ndim}")
        if isinstance(item, Tensor):
            print(f"device: {item.device}")
            print(f"min: {item.min():.4f}")
            print(f"max: {item.max():.4f}")
            try:
                print(f"std: {item.std(dim=dim):.4f}")
            except:
                pass
            try:

                print(f"mean: {item.mean(dim=dim):.4f}")
            except:
                pass
    if print_tensor:
        print(item)
    if has_title:
        print("".join(["-"] * _b), "\n")
    else:
        print("\n")
    sys.stdout.flush()


def get_losses(base: Tensor, target: Tensor, return_valid_only: bool = False):
    losses = {}
    losses["mse_loss"] = try_torch("mse_loss", base, target)
    losses["l1_loss"] = try_torch("l1_loss", base, target)
    losses["huber_loss"] = try_torch("huber_loss", base, target)
    losses["poisson_nll_loss"] = try_torch("poisson_nll_loss", base, target)
    losses["smooth_l1_loss"] = try_torch("smooth_l1_loss", base, target)
    losses["cross_entropy"] = try_torch("cross_entropy", base, target)
    losses["soft_margin_loss"] = try_torch("soft_margin_loss", base, target)
    losses["nll_loss"] = try_torch("nll_loss", base, target)
    losses["gaussian_nll_loss"] = try_torch("gaussian_nll_loss", base, target, var=1.0)
    losses["gaussian_nll_loss-var_0.25"] = try_torch(
        "gaussian_nll_loss", base, target, var=0.25
    )
    losses["gaussian_nll_loss-var_4.0"] = try_torch(
        "gaussian_nll_loss", base, target, var=4.0
    )
    if not return_valid_only:
        return losses
    valid = {}
    for name, loss in losses.items():
        if isinstance(loss, str):
            continue
        valid[name] = loss
    return valid


def set_seed(seed: int):
    """Set random seed for reproducibility."""
    torch.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    if torch.mps.is_available():
        torch.mps.manual_seed(seed)
    if torch.xpu.is_available():
        torch.xpu.manual_seed_all(seed)


def count_parameters(model: nn.Module) -> int:
    """Returns total number of trainable parameters."""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def freeze_all_except(model: nn.Module, except_layers: Optional[list[str]] = None):
    """Freezes all model parameters except specified layers."""
    no_exceptions = not except_layers
    for name, param in model.named_parameters():
        if no_exceptions:
            param.requires_grad_(False)
        elif any(layer in name for layer in except_layers):
            param.requires_grad_(False)


def freeze_selected_weights(model: nn.Module, target_layers: list[str]):
    """Freezes only parameters on specified layers."""
    for name, param in model.named_parameters():
        if any(layer in name for layer in target_layers):
            param.requires_grad_(False)


def unfreeze_all_except(model: nn.Module, except_layers: Optional[list[str]] = None):
    """Unfreezes all model parameters except specified layers."""
    no_exceptions = not except_layers
    for name, param in model.named_parameters():
        if no_exceptions:
            param.requires_grad_(True)
        elif not any(layer in name for layer in except_layers):
            param.requires_grad_(True)


def unfreeze_selected_weights(model: nn.Module, target_layers: list[str]):
    """Unfreezes only parameters on specified layers."""
    for name, param in model.named_parameters():
        if not any(layer in name for layer in target_layers):
            param.requires_grad_(True)


def sample_tensor(tensor: Tensor, num_samples: int = 5):
    """Randomly samples values from tensor for preview."""
    flat = tensor.flatten()
    idx = torch.randperm(len(flat))[:num_samples]
    return flat[idx]


def clear_cache():
    if torch.cuda.is_available():
        try:
            torch.cuda.empty_cache()
        except:
            pass
    if torch.mps.is_available():
        try:
            torch.mps.empty_cache()
        except:
            pass
    if torch.xpu.is_available():
        try:
            torch.xpu.empty_cache()
        except:
            pass
    if hasattr(torch, "mtia"):
        try:
            torch.mtia.empty_cache()
        except:
            pass
    gc.collect()
