__all__ = ["OptimizerWrapper", "get_adamw_optimizer", "get_trainable_modules"]
import inspect
import torch
from torch import optim, Tensor, nn
from torch.optim import Optimizer
from typing import Dict, List, Optional, Any, Tuple, Union
from pathlib import Path
from torch.amp.grad_scaler import GradScaler
from lt_utils.file_ops import is_pathlike, find_files


class OptimizerWrapper:
    def __init__(
        self,
        optimizers: Dict[str, Optimizer] = {},
        schedulers: Dict[str, optim.lr_scheduler.LRScheduler] = {},
    ):
        self.optimizers = optimizers
        self.schedulers = schedulers
        self.keys = list(optimizers.keys())

    def state_dict(self):
        std = {
            "optimizers": [],
            "schedulers": [],
        }
        for k, v in self.optimizers.items():
            try:
                std["optimizers"].append({k: v.state_dict()})
            except:
                pass
        for k, v in self.schedulers.items():
            try:
                std["schedulers"].append({k: v.state_dict()})
            except:
                pass
        return std.copy()

    def load_state_dict(self, state_dict: Dict[str, List[Dict[str, Any]]]):
        optimizers = state_dict["optimizers"]
        schedulers = state_dict["schedulers"]
        if optimizers and self.optimizers:
            for otm in optimizers:
                try:
                    for k, v in otm.items():
                        if k in self.optimizers:
                            self.optimizers[k].load_state_dict(v)
                        else:
                            print(
                                f"Key '{k}' does not exist in the optimizers, it will be ignored."
                            )
                except Exception as e:
                    print(
                        f"(load_state_dict -> optimizers): The key '{k}' was not loaded due to the exception: {e}"
                    )
        if schedulers and self.schedulers:
            for scheduler in schedulers:
                try:
                    for k, v in scheduler.items():
                        if k in self.schedulers:
                            self.schedulers[k].load_state_dict(v)
                        else:
                            print(
                                f"Key '{k}' does not exist in the schedulers, it will be ignored."
                            )
                except Exception as e:
                    print(
                        f"(load_state_dict -> schedulers): The key '{k}' was not loaded due to the exception: {e}"
                    )

    def save_state(self, path: Union[str, Path]):
        is_pathlike(path, validate=True)
        path = Path(path)
        if path.name.endswith((".pt", ".pth", ".ckpt", ".state")):
            name = path.name
            path = path.parent
        else:
            name = "optimizers.pt"
        path.mkdir(exist_ok=True, parents=True)
        path = Path(path, name)
        torch.save(self.state_dict(), str(path))

    def load_state(
        self,
        path: Union[str, Path],
        not_exist_ok: bool = False,
        *,
        map_location: Optional[Any] = None,
        weights_only: bool = False,
    ):
        is_pathlike(path, validate=True)
        path = Path(path)
        exists = path.exists()
        if not exists:
            assert not_exist_ok, f"The provided path '{path}' does not exist!"
            return
        if path.is_file():
            data = torch.load(
                str(path), weights_only=weights_only, map_location=map_location
            )
        else:
            file = find_files(path, ["optimizers.pt"], maximum=1)
            if not file:
                assert (
                    not_exist_ok
                ), f"Unable to find an 'optimizers.pt' or 'optim.pt' ath the path '{str(path)}'"
                return None
            data = torch.load(
                file[0], weights_only=weights_only, map_location=map_location
            )
        self.load_state_dict(data)

    def get_lr(
        self, keys: Optional[Union[str, List[str]]] = None
    ) -> List[Dict[str, float]] | Dict[str, float]:
        lrs = []
        if keys and isinstance(keys, (str, list, tuple)):
            if isinstance(keys, str):
                return self.optimizers[keys].param_groups[0]["lr"]
            for k in keys:
                lrs.append({k: self.optimizers[k].param_groups[0]["lr"]})
            return lrs
        for k, v in self.optimizers.items():
            lrs.append({k: v.param_groups[0]["lr"]})
        return lrs

    def _set_lr(self, new_lr: float, opt: str):
        for p in self.optimizers[opt].param_groups:
            if isinstance(p["lr"], Tensor):
                p["lr"].fill_(new_lr)
            else:
                p["lr"] = new_lr

    def set_lr(
        self, new_lr: float, keys: Optional[Union[str, List[str]]]
    ) -> List[Dict[str, float]] | Dict[str, float]:
        if keys and isinstance(keys, (str, list, tuple)):
            if isinstance(keys, str):
                self._set_lr(new_lr, keys)
                return
            for key in keys:
                self._set_lr(new_lr, key)
            return
        for key in self.keys:
            self._set_lr(new_lr, key)

    def step(
        self,
        keys: Optional[Union[str, List[str]]] = None,
        scaler: Optional[GradScaler] = None,
    ):
        ks = (
            [keys]
            if isinstance(keys, str)
            else keys if isinstance(keys, (list, tuple)) else self.keys
        )

        for k in ks:
            if scaler is not None:
                scaler.step(self.optimizers[k])
                scaler.update()
            else:
                self.optimizers[k].step()

    def zero_grad(self, keys: Optional[Union[str, List[str]]] = None):
        if keys:
            if isinstance(keys, str):
                self.optimizers[keys].zero_grad()
            else:
                for key in keys:
                    self.optimizers[key].zero_grad()
        else:
            for _, v in self.optimizers.items():
                v.zero_grad()

    def scheduler(self, *args, key: Optional[Union[str, List[str]]] = None):
        if key is not None:
            self.schedulers[key].step(*args)
            return self.schedulers[key].optimizer.param_groups[0]["lr"]
        lr = 0
        for i, (_, v) in enumerate(self.schedulers.items()):
            v.step(*args)
            if i == 0:
                lr = v.optimizer.param_groups[0]["lr"]
        return lr


def get_trainable_modules(
    *models: nn.Module,
) -> Tuple[List[nn.Parameter], List[nn.Parameter]]:
    group_sz_sm = []
    group_sz_lg = []
    for model in models:
        for param in model.parameters():
            if not param.requires_grad:
                continue
            if param.ndim < 2:
                group_sz_sm.append(param)
            else:
                group_sz_lg.append(param)

    return group_sz_sm, group_sz_lg


def get_adamw_optimizer(
    *models: nn.Module,
    lr: float = 1e-3,
    weight_decay_1: float = 0.01,
    weight_decay_2: float = 0.01,
    betas: Tuple = (0.9, 0.999),
    device: str = "cpu",
    eps: float = 1e-8,
    use_fused_if_available: bool = True,
):
    group_decay_sm, group_decay_lg = get_trainable_modules(*models)

    optim_groups = [
        {"params": group_decay_lg, "weight_decay": weight_decay_1},
        {"params": group_decay_sm, "weight_decay": weight_decay_2},
    ]

    use_fused = (
        "fused" in inspect.signature(optim.AdamW).parameters
    ) and device == "cuda"
    return optim.AdamW(
        optim_groups,
        lr=lr,
        betas=betas,
        eps=eps,
        fused=(use_fused and use_fused_if_available) or None,
    )
