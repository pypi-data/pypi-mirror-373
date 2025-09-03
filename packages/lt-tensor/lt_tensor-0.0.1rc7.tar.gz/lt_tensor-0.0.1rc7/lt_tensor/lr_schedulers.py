import math
from torch.optim import Optimizer
from torch.optim.lr_scheduler import LRScheduler
from typing import Optional, Literal
from numbers import Number
from lt_tensor.misc_utils import update_lr


class WarmupDecayScheduler(LRScheduler):
    def __init__(
        self,
        optimizer: Optimizer,
        warmup_steps: int,
        total_steps: int,
        decay_type: Literal["cosine", "linear"] = "linear",  # or "cosine"
        min_lr: float = 0.0,
        last_epoch: int = -1,
    ):
        assert decay_type in [
            "cosine",
            "linear",
        ], f"Unknown decay type: {self.decay_type}"
        self.warmup_steps = warmup_steps
        self.total_steps = total_steps
        self.decay_type = decay_type
        self.min_lr = min_lr
        super().__init__(optimizer, last_epoch)

    def get_lr(self):
        step = self.last_epoch + 1
        warmup = self.warmup_steps
        total = self.total_steps
        lrs = []

        for base_lr in self.base_lrs:
            if step < warmup:
                lr = base_lr * step / warmup
            else:
                progress = (step - warmup) / max(1, total - warmup)
                if self.decay_type == "linear":
                    lr = base_lr * (1.0 - progress)
                else:
                    lr = base_lr * 0.5 * (1 + math.cos(math.pi * progress))

            lr = max(self.min_lr, lr)
            lrs.append(lr)

        return lrs


class AdaptiveDropScheduler(LRScheduler):
    def __init__(
        self,
        optimizer,
        drop_factor=0.5,
        patience=10,
        min_lr=1e-6,
        cooldown=5,
        last_epoch=-1,
    ):
        self.drop_factor = drop_factor
        self.patience = patience
        self.min_lr = min_lr
        self.cooldown = cooldown
        self.cooldown_counter = 0
        self.best_loss = float("inf")
        self.bad_steps = 0
        super().__init__(optimizer, last_epoch)

    def step(self, val_loss=None):
        if val_loss is not None:
            if val_loss < self.best_loss:
                self.best_loss = val_loss
                self.bad_steps = 0
                self.cooldown_counter = 0
            else:
                self.bad_steps += 1
                if self.bad_steps >= self.patience and self.cooldown_counter == 0:
                    for i, group in enumerate(self.optimizer.param_groups):
                        new_lr = max(group["lr"] * self.drop_factor, self.min_lr)
                        group["lr"] = new_lr
                    self.cooldown_counter = self.cooldown
                    self.bad_steps = 0
        if self.cooldown_counter > 0:
            self.cooldown_counter -= 1

    def get_lr(self):
        return [group["lr"] for group in self.optimizer.param_groups]


class SinusoidalDecayLR(LRScheduler):
    def __init__(
        self,
        optimizer: Optimizer,
        initial_lr: float = 1e-3,
        target_lr: float = 1e-5,
        floor_lr: float = 1e-7,
        decay_rate: float = 1e-6,  # decay per period
        wave_amplitude: float = 1e-5,
        period: int = 256,
        last_epoch: int = -1,
    ):
        assert decay_rate != 0.0, "decay_rate must be different from 0.0"
        assert (
            initial_lr >= target_lr >= floor_lr
        ), "Must satisfy: initial_lr ≥ target_lr ≥ floor_lr"

        self.initial_lr = initial_lr
        self.target_lr = target_lr
        self.floor_lr = floor_lr
        self.decay_rate = decay_rate
        self.wave_amplitude = wave_amplitude
        self.period = period

        super().__init__(optimizer, last_epoch)

    def get_lr(self):
        step = self.last_epoch + 1
        cycles = step // self.period
        t = step % self.period
        # Decay center down to target_lr, then freeze
        center_decay = math.exp(-self.decay_rate * cycles)
        center = max(self.target_lr, self.initial_lr * center_decay)
        # Decay amplitude in sync with center (relative to initial)
        amplitude_decay = math.exp(-self.decay_rate * cycles)
        current_amplitude = self.wave_amplitude * self.initial_lr * amplitude_decay
        sin_offset = math.sin(2 * math.pi * t / self.period)
        lr = max(center + current_amplitude * sin_offset, self.floor_lr)
        return [lr for _ in self.optimizer.param_groups]


class GuidedWaveringLR(LRScheduler):
    def __init__(
        self,
        optimizer: Optimizer,
        initial_lr: float = 1e-3,
        target_lr: float = 1e-5,
        floor_lr: float = 1e-7,
        decay_rate: float = 0.01,
        wave_amplitude: float = 0.02,
        period: int = 256,
        stop_decay_after: int = None,
        last_epoch: int = -1,
    ):
        assert decay_rate != 0.0, "decay_rate must be non-zero"
        assert (
            initial_lr >= target_lr >= floor_lr
        ), "Must satisfy: initial ≥ target ≥ floor"

        self.initial_lr = initial_lr
        self.target_lr = target_lr
        self.floor_lr = floor_lr
        self.decay_rate = decay_rate
        self.wave_amplitude = wave_amplitude
        self.period = period
        self.stop_decay_after = stop_decay_after

        super().__init__(optimizer, last_epoch)

    def get_lr(self):
        step = self.last_epoch + 1
        cycles = step // self.period
        t = step % self.period

        decay_cycles = (
            min(cycles, self.stop_decay_after) if self.stop_decay_after else cycles
        )
        center = max(
            self.target_lr, self.initial_lr * math.exp(-self.decay_rate * decay_cycles)
        )
        amp = (
            self.wave_amplitude
            * self.initial_lr
            * math.exp(-self.decay_rate * decay_cycles)
        )
        phase = 2 * math.pi * t / self.period
        wave = math.sin(phase) * math.cos(phase)
        lr = max(center + amp * wave, self.floor_lr)
        return [lr for _ in self.optimizer.param_groups]


class FloorExponentialLR(LRScheduler):
    """Modified version from exponential lr, to have a minimum and reset functions.

    Decays the learning rate of each parameter group by gamma every epoch.

    When last_epoch=-1, sets initial lr as lr.

    Args:
        optimizer (Optimizer): Wrapped optimizer.
        gamma (float): Multiplicative factor of learning rate decay.
        last_epoch (int): The index of last epoch. Default: -1.
    """

    def __init__(
        self,
        optimizer: Optimizer,
        initial_lr: float = 1e-4,
        gamma: float = 0.99998,
        last_epoch: int = -1,
        floor_lr: float = 1e-6,
    ):
        self.gamma = gamma
        self.floor_lr = floor_lr
        self.initial_lr = initial_lr

        super().__init__(optimizer, last_epoch)

    def set_floor(self, new_value: float):
        assert isinstance(new_value, Number)
        self.floor_lr = new_value

    def reset_lr(self, new_value: Optional[float] = None):
        new_lr = new_value if isinstance(new_value, Number) else self.initial_lr
        self.initial_lr = new_lr
        update_lr(self.optimizer, new_lr)

    def get_lr(self):

        if self.last_epoch == 0:
            return [
                max(group["lr"], self.floor_lr) for group in self.optimizer.param_groups
            ]

        return [
            max(group["lr"] * self.gamma, self.floor_lr)
            for group in self.optimizer.param_groups
        ]

    def _get_closed_form_lr(self):
        return [
            max(base_lr * self.gamma**self.last_epoch, self.floor_lr)
            for base_lr in self.base_lrs
        ]
