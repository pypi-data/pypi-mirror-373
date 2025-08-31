__all__ = ["get_activation", "ACTIVATIONS_MAP"]
import gc
import torch
import warnings
from abc import ABC
from torch import nn, Tensor
from lt_utils.common import *
from lt_utils.type_utils import is_dict
from lt_utils.misc_utils import get_current_time
from typing import TypeVar, Mapping, OrderedDict
from lt_utils.file_ops import (
    load_json,
    save_json,
    load_yaml,
    save_yaml,
    find_files,
    is_file,
    is_path_valid,
    is_pathlike,
)
from lt_tensor.model_zoo.activations.alias_free import (
    Activation1d as Alias1D,
    Activation2d as Alias2D,
)
from lt_tensor.model_zoo.activations.snake import Snake, SnakeBeta

ACTIVATIONS_MAP = {
    "relu": nn.ReLU,
    "leakyrelu": nn.LeakyReLU,
    "relu6": nn.ReLU6,
    "rrelU": nn.RReLU,
    "tanh": nn.Tanh,
    "hardtanh": nn.Hardtanh,
    "sigmoid": nn.Sigmoid,
    "logsigmoid": nn.LogSigmoid,
    "hardsigmoid": nn.Hardsigmoid,
    "softmin": nn.Softmin,
    "softmax": nn.Softmax,
    "logsoftmax": nn.LogSoftmax,
    "softmax2d": nn.Softmax2d,
    "multiheadattention": nn.MultiheadAttention,
    "mish": nn.Mish,
    "gelu": nn.GELU,
    "celu": nn.CELU,
    "elu": nn.ELU,
    "prelu": nn.PReLU,
    "silu": nn.SiLU,
    "glu": nn.GLU,
    "hardswish": nn.Hardswish,
    "softplus": nn.Softplus,
    "hardshrink": nn.Hardshrink,
    "softshrink": nn.Softshrink,
    "tanhshrink": nn.Tanhshrink,
    "aliasfree1d": Alias1D,
    "aliasfree2d": Alias2D,
    "snake": Snake,
    "snakebeta": SnakeBeta,
    "threshold": nn.Threshold,
}

ACTIV_NAMES_TP: TypeAlias = Literal[
    "relu",
    "leakyrelu",
    "relu6",
    "rrelU",
    "tanh",
    "hardtanh",
    "sigmoid",
    "logsigmoid",
    "hardsigmoid",
    "softmin",
    "softmax",
    "logsoftmax",
    "softmax2d",
    "multiheadattention",
    "mish",
    "gelu",
    "celu",
    "elu",
    "prelu",
    "silu",
    "glu",
    "hardswish",
    "softplus",
    "hardshrink",
    "softshrink",
    "tanhshrink",
    "aliasfree1d",
    "aliasfree2d",
    "snake",
    "snakebeta",
    "threshold",
]


def get_activation(
    activation: ACTIV_NAMES_TP,
    *args,
    **kwargs,
):
    assert activation in ACTIVATIONS_MAP, f"Invalid activation {activation}"
    return ACTIVATIONS_MAP[activation.lower()](*args, **kwargs)
