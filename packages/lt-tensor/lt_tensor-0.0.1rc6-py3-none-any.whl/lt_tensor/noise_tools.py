from lt_utils.common import *
from lt_tensor.model_base import Model
import torch
from torch import nn, Tensor
import math
import random
from lt_tensor.misc_utils import set_seed


def add_gaussian_noise(x: Tensor, noise_level: float = 0.025) -> Tensor:
    noise = torch.randn_like(x) * noise_level
    return x + noise


def add_uniform_noise(x: Tensor, noise_level: float = 0.025) -> Tensor:
    noise = (torch.rand_like(x) - 0.5) * 2 * noise_level
    return x + noise


def add_linear_noise(x, noise_level=0.05) -> Tensor:
    T = x.shape[-1]
    ramp = torch.linspace(0, noise_level, T, device=x.device)
    for _ in range(x.dim() - 1):
        ramp = ramp.unsqueeze(0)
    return x + ramp.expand_as(x)


def add_impulse_noise(x: Tensor, noise_level: float = 0.025) -> Tensor:
    # For image inputs
    probs = torch.rand_like(x)
    x_clone = x.detach().clone()
    x_clone[probs < (noise_level / 2)] = 0.0  # salt
    x_clone[probs > (1 - noise_level / 2)] = 1.0  # pepper
    return x_clone


def add_pink_noise(x: Tensor, noise_level: float = 0.05) -> Tensor:
    # pink noise: divide freq spectrum by sqrt(f)
    if x.ndim == 3:
        x = x.view(-1, x.shape[-1])  # flatten to 2D [B*M, T]
    pink_noised = []

    for row in x:
        white = torch.randn_like(row)
        f = torch.fft.rfft(white)
        freqs = torch.fft.rfftfreq(row.numel(), d=1.0)
        freqs[0] = 1.0  # prevent div by 0
        f /= freqs.sqrt()
        pink = torch.fft.irfft(f, n=row.numel())
        pink_noised.append(pink)

    pink_noised = torch.stack(pink_noised, dim=0).view_as(x)
    return x + pink_noised * noise_level


def add_clipped_gaussian_noise(x: Tensor, noise_level: float = 0.025) -> Tensor:
    noise = torch.randn_like(x) * noise_level
    return torch.clamp(x + noise, 0.0, 1.0)


def add_multiplicative_noise(x: Tensor, noise_level: float = 0.025) -> Tensor:
    noise = 1 + torch.randn_like(x) * noise_level
    return x * noise


_VALID_NOISES = [
    "gaussian",
    "uniform",
    "linear",
    "impulse",
    "pink",
    "clipped_gaussian",
    "multiplicative",
]

_NOISE_MAP = {
    "gaussian": add_gaussian_noise,
    "uniform": add_uniform_noise,
    "linear": add_linear_noise,
    "impulse": add_impulse_noise,
    "pink": add_pink_noise,
    "clipped_gaussian": add_clipped_gaussian_noise,
    "multiplicative": add_multiplicative_noise,
}

_NOISE_DIM_SUPPORT = {
    "gaussian": (1, 2),
    "uniform": (1, 2),
    "multiplicative": (1, 2, 3),
    "clipped_gaussian": (1, 2, 3),
    "linear": (2, 3),
    "impulse": (2, 3),
    "pink": (2, 3),
}


def apply_noise(
    x: Tensor,
    noise_type: Literal[
        "gaussian",
        "uniform",
        "linear",
        "impulse",
        "pink",
        "clipped_gaussian",
        "multiplicative",
    ] = "gaussian",
    noise_level: float = 0.01,
    seed: Optional[int] = None,
    on_error: Literal["raise", "try_others", "return_unchanged"] = "raise",
    _last_tries: list[str] = [],
):
    noise_type = noise_type.lower().strip()
    last_tries = _last_tries

    if noise_type not in _NOISE_MAP:
        raise ValueError(f"Noise type '{noise_type}' not supported.")

    # Check dimension compatibility
    allowed_dims = _NOISE_DIM_SUPPORT.get(noise_type, (1, 2))
    if x.ndim not in allowed_dims:
        assert (
            on_error != "raise"
        ), f"Noise '{noise_type}' is not supported for {x.ndim}D input."
        if on_error == "return_unchanged":
            return x, None
        elif on_error == "try_others":
            remaining = [
                n
                for n in _VALID_NOISES
                if n not in last_tries and x.ndim in _NOISE_DIM_SUPPORT[n]
            ]
            if not remaining:
                return x, None
            new_type = random.choice(remaining)
            last_tries.append(new_type)
            return (
                apply_noise(
                    x, new_type, noise_level, seed, on_error, last_tries.copy()
                ),
                noise_type,
            )
    try:
        if isinstance(seed, int):
            set_seed(seed)
        return _NOISE_MAP[noise_type](x, noise_level), noise_type
    except Exception as e:
        if on_error == "raise":
            raise e
        elif on_error == "return_unchanged":
            return x, None
        if len(last_tries) == len(_VALID_NOISES):
            return x, None
        remaining = [n for n in _VALID_NOISES if n not in last_tries]
        new_type = random.choice(remaining)
        last_tries.append(new_type)
        return (
            apply_noise(x, new_type, noise_level, seed, on_error, last_tries.copy()),
            noise_type,
        )


class NoiseSchedulerA(nn.Module):
    def __init__(self, samples: int = 64):
        super().__init__()
        self.base_steps = samples

    def plot_noise_progression(noise_seq: list[Tensor], titles: list[str] = None):
        import matplotlib.pyplot as plt

        steps = len(noise_seq)
        plt.figure(figsize=(15, 3))
        for i, tensor in enumerate(noise_seq):
            plt.subplot(1, steps, i + 1)
            plt.imshow(tensor.squeeze().cpu().numpy(), aspect="auto", origin="lower")
            if titles:
                plt.title(titles[i])
            plt.axis("off")
        plt.tight_layout()
        plt.show()

    def forward(
        self,
        source_item: torch.Tensor,
        steps: Optional[int] = None,
        noise_type: Literal[
            "gaussian",
            "uniform",
            "linear",
            "impulse",
            "pink",
            "clipped_gaussian",
            "multiplicative",
        ] = "gaussian",
        seed: Optional[int] = None,
        noise_level: float = 0.01,
        shuffle_noise_types: bool = False,
        return_dict: bool = True,
    ):
        if steps is None:
            steps = self.base_steps
        collected = [source_item.detach().clone()]
        noise_history = []
        for i in range(steps):
            if i > 0 and shuffle_noise_types:
                noise_type = random.choice(_VALID_NOISES)
            current, noise_name = apply_noise(
                collected[-1],
                noise_type,
                noise_level,
                seed=seed,
                on_error="try_others",
            )
            noise_history.append(noise_name)
            collected.append(current)

        if return_dict:
            return {
                "steps": collected,
                "history": noise_history,
                "final": collected[-1],
                "init": collected[0],
            }
        return collected, noise_history


class NoiseSchedulerB(Model):
    def __init__(self, timesteps: int = 50, l_min: float = 0.0005, l_max: float = 0.05):
        super().__init__()

        betas = torch.linspace(l_min, l_max, timesteps)
        alphas = 1.0 - betas
        alpha_cumprod = torch.cumprod(alphas, dim=0)

        self.register_buffer("sqrt_alpha_cumprod", torch.sqrt(alpha_cumprod))
        self.register_buffer(
            "sqrt_one_minus_alpha_cumprod", torch.sqrt(1.0 - alpha_cumprod)
        )

        self.timesteps = timesteps
        self.default_noise = math.sqrt(1.25)

    def _get_random_noise(
        self,
        min_max: Tuple[float, float] = (-3, 3),
        seed: Optional[int] = None,
    ) -> float:
        if isinstance(seed, int):
            random.seed(seed)
        return random.uniform(*min_max)

    def set_noise(
        self,
        noise: Optional[Union[Tensor, Number]] = None,
        seed: Optional[int] = None,
        min_max: Tuple[float, float] = (-3, 3),
        default: bool = False,
    ):
        if noise is not None:
            self.default_noise = noise
        else:
            self.default_noise = (
                math.sqrt(1.25) if default else self._get_random_noise(min_max, seed)
            )

    def forward(
        self, x_0: Tensor, t: int, noise: Optional[Union[Tensor, float]] = None
    ) -> Tensor:
        assert (
            0 <= t < self.timesteps
        ), f"Time step t={t} is out of bounds for scheduler with {self.timesteps} steps."

        if noise is None:
            noise = torch.randn_like(x_0) * self.default_noise

        elif isinstance(noise, (float, int)):
            noise = torch.randn_like(x_0) * noise

        alpha_term = self.sqrt_alpha_cumprod[t] * x_0
        noise_term = self.sqrt_one_minus_alpha_cumprod[t] * noise
        return alpha_term + noise_term


class NoiseSchedulerC(Model):
    def __init__(self, timesteps: int = 512):
        super().__init__()

        betas = torch.linspace(1e-4, 0.02, timesteps)
        alphas = 1.0 - betas
        alpha_cumprod = torch.cumprod(alphas, dim=0)

        self.register_buffer("sqrt_alpha_cumprod", torch.sqrt(alpha_cumprod))
        self.register_buffer(
            "sqrt_one_minus_alpha_cumprod", torch.sqrt(1.0 - alpha_cumprod)
        )

        self.timesteps = timesteps
        self.default_noise_strength = math.sqrt(1.25)
        self.default_noise_type = "gaussian"
        self.noise_seed = None

    def _get_random_uniform(self, shape, min_val=-1.0, max_val=1.0):
        return torch.empty(shape).uniform_(min_val, max_val)

    def _get_noise(self, x: Tensor, noise_type: str, noise_level: float) -> Tensor:
        # Basic noise types
        if noise_type == "gaussian":
            return torch.randn_like(x) * noise_level
        elif noise_type == "uniform":
            return self._get_random_uniform(x.shape) * noise_level
        elif noise_type == "multiplicative":
            return x * (1 + (torch.randn_like(x) * noise_level))
        elif noise_type == "clipped_gaussian":
            noise = torch.randn_like(x) * noise_level
            return noise.clamp(-1.0, 1.0)
        elif noise_type == "impulse":
            mask = torch.rand_like(x) < noise_level
            impulses = torch.randn_like(x) * noise_level
            return x + impulses * mask
        else:
            raise ValueError(f"Unsupported noise type: '{noise_type}'")

    def set_noise(
        self,
        noise_strength: Optional[Union[Tensor, float]] = None,
        noise_type: Optional[str] = None,
        seed: Optional[int] = None,
        default: bool = False,
    ):
        if noise_strength is not None:
            self.default_noise_strength = noise_strength
        elif default:
            self.default_noise_strength = math.sqrt(1.25)

        if noise_type is not None:
            self.default_noise_type = noise_type.lower().strip()

        if isinstance(seed, int):
            self.noise_seed = seed
            torch.manual_seed(seed)
            random.seed(seed)

    def forward(
        self,
        x_0: Tensor,
        t: int,
        noise: Optional[Union[Tensor, float]] = None,
        noise_type: Optional[str] = None,
    ) -> Tensor:
        assert 0 <= t < self.timesteps, f"t={t} is out of bounds [0, {self.timesteps})"

        noise_type = noise_type or self.default_noise_type
        noise_level = self.default_noise_strength

        if noise is None:
            noise = self._get_noise(x_0, noise_type, noise_level)
        elif isinstance(noise, (float, int)):
            noise = self._get_noise(x_0, noise_type, noise)

        alpha_term = self.sqrt_alpha_cumprod[t] * x_0
        noise_term = self.sqrt_one_minus_alpha_cumprod[t] * noise
        return alpha_term + noise_term
