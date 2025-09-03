__all__ = [
    "ConvBase",
    "calc_max_groups",
    "get_padding_1d",
    "get_padding_2d",
    "get_conv",
    "remove_norm",
    "is_groups_compatible",
]
import math
from lt_utils.common import *
from torch.nn.utils.parametrize import remove_parametrizations
from torch.nn.utils.parametrizations import weight_norm, spectral_norm
from lt_tensor.common import nn, Model

TP_SHAPE_1: TypeAlias = Union[int, Tuple[int]]
TP_SHAPE_2: TypeAlias = Union[TP_SHAPE_1, Tuple[int, int]]
TP_SHAPE_3: TypeAlias = Union[TP_SHAPE_2, Tuple[int, int, int]]


def _dummy(module: Model, *args, **kwargs):
    return module


def is_groups_compatible(channels_in: int, channels_out: int, groups: int):
    if channels_in < 2 or channels_out < 2:
        return groups == 1
    return groups % channels_in == 0 and groups % channels_out == 0


def calc_max_groups(channels_in: int, channels_out: int):
    return math.gcd(int(channels_in), int(channels_out))


def get_padding_1d(kernel_size: int, dilation: int):
    return int((kernel_size * dilation - dilation) / 2)


def get_padding_multi_dim(
    kernel_size: TP_SHAPE_3,
    dilation: TP_SHAPE_3,
):
    assert isinstance(kernel_size, int) or (
        isinstance(kernel_size, (list, tuple))
        and len(kernel_size) in [1, 2, 3]
        and all([isinstance(x, int) for x in kernel_size])
    ), (
        "kernel_size must be either a integer or a sequence (list or tuple) of 1 up to 3 numbers."
        f" Received instead '{kernel_size}' from type {type(kernel_size)}"
    )
    assert isinstance(dilation, int) or (
        isinstance(dilation, (list, tuple))
        and len(dilation) in [1, 2, 3]
        and all([isinstance(x, int) for x in dilation])
    ), (
        "'dilation' must be either a integer or a sequence (list or tuple) of 1 up to 3 numbers."
        f" Received instead '{dilation}' from type {type(dilation)}"
    )

    is_ks_sg = isinstance(kernel_size, int) or len(kernel_size) == 1
    is_dl_sg = isinstance(dilation, int) or len(dilation) == 1

    if all([is_ks_sg, is_dl_sg]):
        return get_padding_1d(
            (kernel_size[0] if isinstance(kernel_size, (list, tuple)) else kernel_size),
            dilation[0] if isinstance(dilation, (list, tuple)) else dilation,
        )

    if any([is_ks_sg, is_dl_sg]):
        sz1 = 1 if is_ks_sg else len(kernel_size)
        sz2 = 1 if is_dl_sg else len(dilation)
        expand = max(1, sz1, sz2)

        if isinstance(kernel_size, int):
            kernel_size = [kernel_size] + [1 for _ in range(expand - 1)]

        if isinstance(dilation, int):
            dilation = [dilation] + [1 for _ in range(expand - 1)]

    return tuple(get_padding_1d(ks, d) for ks, d in zip(kernel_size, dilation))


def get_weight_norm(
    norm_type: Optional[Literal["weight_norm", "spectral_norm"]] = None, **norm_kwargs
) -> Callable[[Union[nn.Module, Model]], Union[nn.Module, Model]]:
    if not norm_type:
        return _dummy
    if norm_type == "weight_norm":
        return lambda x: weight_norm(x, **norm_kwargs)
    return lambda x: spectral_norm(x, **norm_kwargs)


def remove_norm(module, name: str = "weight"):
    try:
        try:
            remove_parametrizations(module, name, leave_parametrized=False)
        except:
            # many times will fail with 'leave_parametrized'
            remove_parametrizations(module, name, leave_parametrized=True)
    except ValueError:
        pass  # not parametrized


def get_conv(
    in_channels: int = 1,
    out_channels: Optional[int] = None,
    kernel_size: TP_SHAPE_3 = 1,
    stride: TP_SHAPE_3 = 1,
    padding: TP_SHAPE_3 = 0,
    output_padding: TP_SHAPE_3 = 0,
    dilation: TP_SHAPE_3 = 1,
    groups: int = 1,
    bias: bool = True,
    padding_mode: str = "zeros",
    *,
    dim: Literal["1d", "2d", "3d"] = "1d",
    transposed: bool = False,
    norm: Optional[Literal["weight_norm", "spectral_norm"]] = None,
    norm_kwargs: Dict[str, Any] = {},
):
    dim = dim.lower().strip()
    assert dim in [
        "1d",
        "2d",
        "3d",
    ], f"Invalid conv dim '{dim}'. It must be either '1d', '2d' or '3d'."
    assert not norm or norm in ["weight_norm", "spectral_norm"], (
        f"Invalid norm '{norm}'."
        'It must be either "weight_norm" or "spectral_norm" or None.'
    )
    kwargs = dict(
        in_channels=in_channels,
        out_channels=out_channels if out_channels is not None else in_channels,
        kernel_size=kernel_size,
        padding=padding,
        stride=stride,
        dilation=dilation,
        bias=bias,
        groups=groups,
        padding_mode=padding_mode,
    )
    norm_fn = get_weight_norm(norm, **norm_kwargs)
    if transposed:
        kwargs["output_padding"] = output_padding

    match dim:
        case "1d":
            if transposed:
                md = nn.ConvTranspose1d
            else:
                md = nn.Conv1d
        case "2d":
            if transposed:
                md = nn.ConvTranspose2d
            else:
                md = nn.Conv2d
        case _:
            if transposed:
                md = nn.ConvTranspose3d
            else:
                md = nn.Conv3d
    return norm_fn(md(**kwargs))


class ConvBase(Model):

    @staticmethod
    def get_1d_conv(
        in_channels: int,
        out_channels: Optional[int] = None,
        kernel_size: int = 1,
        stride: int = 1,
        padding: int = 0,
        output_padding: int = 0,
        dilation: int = 1,
        groups: int = 1,
        bias: bool = True,
        padding_mode: str = "zeros",
        *,
        transposed: bool = False,
        norm: Optional[Literal["weight_norm", "spectral_norm"]] = None,
        norm_kwargs: Dict[str, Any] = {},
    ):
        return get_conv(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=kernel_size,
            padding=padding,
            stride=stride,
            dilation=dilation,
            bias=bias,
            groups=groups,
            padding_mode=padding_mode,
            output_padding=output_padding,
            transposed=transposed,
            norm=norm,
            norm_kwargs=norm_kwargs,
            dim="1d",
        )

    @staticmethod
    def get_2d_conv(
        in_channels: int,
        out_channels: Optional[int] = None,
        kernel_size: TP_SHAPE_2 = 1,
        stride: TP_SHAPE_2 = 1,
        padding: TP_SHAPE_2 = 0,
        output_padding: TP_SHAPE_2 = 0,
        dilation: TP_SHAPE_2 = 1,
        groups: int = 1,
        bias: bool = True,
        padding_mode: str = "zeros",
        *,
        transposed: bool = False,
        norm: Optional[Literal["weight_norm", "spectral_norm"]] = None,
        norm_kwargs: Dict[str, Any] = {},
    ):
        return get_conv(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=kernel_size,
            padding=padding,
            stride=stride,
            dilation=dilation,
            bias=bias,
            groups=groups,
            padding_mode=padding_mode,
            output_padding=output_padding,
            transposed=transposed,
            norm=norm,
            norm_kwargs=norm_kwargs,
            dim="2d",
        )

    @staticmethod
    def get_3d_conv(
        in_channels: int,
        out_channels: Optional[int] = None,
        kernel_size: TP_SHAPE_3 = 1,
        stride: TP_SHAPE_3 = 1,
        padding: TP_SHAPE_3 = 0,
        output_padding: TP_SHAPE_3 = 0,
        dilation: TP_SHAPE_3 = 1,
        groups: int = 1,
        bias: bool = True,
        padding_mode: str = "zeros",
        *,
        transposed: bool = False,
        norm: Optional[Literal["weight_norm", "spectral_norm"]] = None,
        norm_kwargs: Dict[str, Any] = {},
    ):
        return get_conv(
            in_channels=in_channels,
            out_channels=out_channels,
            kernel_size=kernel_size,
            padding=padding,
            stride=stride,
            dilation=dilation,
            bias=bias,
            groups=groups,
            padding_mode=padding_mode,
            output_padding=output_padding,
            transposed=transposed,
            norm=norm,
            norm_kwargs=norm_kwargs,
            dim="3d",
        )

    @staticmethod
    def get_max_groups(in_channels: int, out_channels: int):
        return calc_max_groups(in_channels, out_channels)

    @staticmethod
    def get_padding(kernel_size: int, dilation: int):
        if isinstance(kernel_size, int) and isinstance(dilation, int):
            return get_padding_1d(kernel_size, dilation)
        return get_padding_multi_dim(kernel_sizes, dilations)

    def remove_norms(self, name: str = "weight"):
        for module in self.modules():
            try:
                if "Conv" in module.__class__.__name__:
                    remove_norm(module, name)
            except:
                pass

    @staticmethod
    def _init_conv_weights_a(m: nn.Module, mean=0.0, std=0.02):

        if "Conv" in m.__class__.__name__:
            m.weight.data.normal_(mean, std)

    @staticmethod
    def _init_conv_weights_b(m: nn.Module, mean=0.0, std=0.02):
        for param in m.parameters():
            if param.ndim > 1:
                try:
                    param.data.normal_(mean, std)
                except:
                    pass
