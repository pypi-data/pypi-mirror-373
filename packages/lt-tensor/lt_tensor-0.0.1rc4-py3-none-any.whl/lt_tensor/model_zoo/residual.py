__all__ = [
    "ResBlock1",
    "ResBlock2",
    "GatedResBlock",
    "DenseGatedResBlock",
    "AMPBlock1",
    "AMPBlock2",
]
from lt_utils.common import *
import torch
from torch import nn, Tensor
from lt_tensor.model_zoo.convs import ConvBase
from torch.nn.utils.parametrizations import weight_norm


class GatedResBlock(ConvBase):
    def __init__(
        self,
        channels: int,
        kernel_size: int = 3,
        dilations: Tuple[int, ...] = (1, 3, 9),
        activation: nn.Module = nn.LeakyReLU(0.1),
        residual_scale: float = 0.2,
    ):
        super().__init__()
        self.residual_scale = residual_scale
        self.activation = activation

        # Store dilation blocks (dilations=[1,3,9])
        self.dilation_blocks = nn.ModuleList()
        for d in dilations:
            self.dilation_blocks.append(
                nn.Sequential(
                    weight_norm(
                        nn.Conv1d(
                            channels,
                            channels * 2,
                            kernel_size,
                            padding=self.get_padding(kernel_size, d),
                            dilation=d,
                        )
                    ),
                    # Pointwise conv to reduce channel count after GLU
                    weight_norm(nn.Conv1d(channels, channels, 1)),
                )
            )
        self.dilation_blocks.apply(self.apply(self._init_conv_weights_a))

    def forward(self, x):
        residual = x
        for block in self.dilation_blocks:
            h = self.activation(x)
            y = block[0](h)  # [B, C*2, T]
            # Split into two halves (GLU): c and g
            c, g = torch.chunk(y, 2, dim=1)
            gated = c * g.sigmoid()
            # pointwise convolution to reduce channels
            y = block[1](gated)  # [B, C, T]
            x = x + self.residual_scale * y
        return x + residual


class DenseGatedResBlock(ConvBase):
    def __init__(
        self,
        channels: int,
        kernel_size: int = 3,
        dilations: Tuple[int, ...] = (1, 3, 9),
        activation: nn.Module = nn.LeakyReLU(0.1),
        residual_scale: float = 0.2,
        proj_after: bool = True,
    ):
        super().__init__()
        self.residual_scale = residual_scale
        self.activation = activation
        self.blocks = nn.ModuleList()
        self.dilations = list(dilations)
        for d in self.dilations:
            conv = weight_norm(
                nn.Conv1d(
                    channels,
                    channels * 2,
                    kernel_size,
                    padding=self.get_padding(kernel_size, d),
                    dilation=d,
                )
            )
            pw = weight_norm(nn.Conv1d(channels, channels, 1))
            self.blocks.append(nn.ModuleDict({"conv": conv, "pw": pw}))
        self.blocks.apply(self._init_conv_weights_a)
        self.proj_after = proj_after
        if proj_after:
            self.proj = weight_norm(
                nn.Conv1d(channels * (len(self.dilations) + 1), channels, 1)
            )

            self.proj.apply(self._init_conv_weights_a)

    def forward(self, x: Tensor):
        outputs = [x]
        cur = x
        for b in self.blocks:
            xt = self.activation(cur)
            xt = b["conv"](xt)
            a, g = xt.chunk(2, dim=1)
            xt = a * g.sigmoid()
            xt = b["pw"](xt)
            cur = cur + self.residual_scale * xt
            outputs.append(cur)
        out = torch.cat(outputs, dim=1)
        if self.proj_after:
            out = self.proj(out)
        return out


class ResBlock1(ConvBase):
    def __init__(
        self,
        channels,
        kernel_size=3,
        dilation=(1, 3, 5),
        activation: nn.Module = nn.LeakyReLU(0.1),
        groups_c1=1,
        groups_c2=1,
        *args,
        **kwargs,
    ):
        super().__init__()

        self.convs1 = nn.ModuleList()
        self.convs2 = nn.ModuleList()
        cnn2_padding = self.get_padding(kernel_size, 1)

        for i, d in enumerate(dilation):
            mdk = dict(
                in_channels=channels,
                kernel_size=kernel_size,
                dilation=d,
                padding=self.get_padding(kernel_size, d),
                norm="weight_norm",
                groups=groups_c1,
            )
            self.convs2.append(
                nn.Sequential(
                    activation,
                    self.get_1d_conv(
                        channels,
                        kernel_size=kernel_size,
                        dilation=1,
                        padding=cnn2_padding,
                        norm="weight_norm",
                        groups=groups_c2,
                    ),
                )
            )
            if i == 0:
                self.convs1.append(self.get_1d_conv(**mdk))
            else:
                self.convs1.append(nn.Sequential(activation, self.get_1d_conv(**mdk)))
        self.activation = activation
        self.convs1.apply(self._init_conv_weights_a)
        self.convs2.apply(self._init_conv_weights_a)

    def forward(self, x: Tensor):
        for c1, c2 in zip(self.convs1, self.convs2):
            xt = c1(self.activation(x))
            x = c2(self.activation(xt)) + x
        return x


class ResBlock2(ConvBase):
    def __init__(
        self,
        channels,
        kernel_size=3,
        dilation=(1, 3),
        activation: nn.Module = nn.LeakyReLU(0.1),
        groups=1,
        *args,
        **kwargs,
    ):
        super().__init__()

        self.convs = nn.ModuleList(
            [
                self.get_1d_conv(
                    channels,
                    kernel_size=kernel_size,
                    dilation=d,
                    padding=self.get_padding(kernel_size, d),
                    norm="weight_norm",
                    groups=groups,
                )
                for d in dilation
            ]
        )
        negative_slope = (
            activation.negative_slope if isinstance(activation, nn.LeakyReLU) else 0.1
        )
        self.convs.apply(self._init_conv_weights_a)
        self.activation = activation

    def forward(self, x):
        for c in self.convs:
            xt = c(self.activation(x))
            x = xt + x
        return x


def get_snake(name: Literal["snake", "snakebeta"] = "snake"):
    assert name.lower() in [
        "snake",
        "snakebeta",
    ], f"'{name}' is not a valid snake activation! use 'snake' or 'snakebeta'"
    from lt_tensor.model_zoo.activations import snake

    if name.lower() == "snake":
        return snake.Snake
    return snake.SnakeBeta


class AMPBlock1(ConvBase):
    """Modified from 'https://github.com/NVIDIA/BigVGAN/blob/main/bigvgan.py' under MIT license, found in 'bigvgan/LICENSE'
    AMPBlock applies Snake / SnakeBeta activation functions with trainable parameters that control periodicity, defined for each layer.
    AMPBlock1 has additional self.convs2 that contains additional Conv1d layers with a fixed dilation=1 followed by each layer in self.convs1

    Args:
        channels (int): Number of convolution channels.
        kernel_size (int): Size of the convolution kernel. Default is 3.
        dilation (tuple): Dilation rates for the convolutions. Each dilation layer has two convolutions. Default is (1, 3, 5).
        snake_logscale: (bool): to use logscale with snake activation. Default to True.
        activation (str, Callable): Activation function type. Should be either 'snake' or 'snakebeta' or a callable. Defaults to 'snakebeta'.
    """

    def __init__(
        self,
        channels: int,
        kernel_size: int = 3,
        dilation: tuple = (1, 3, 5),
        snake_logscale: bool = True,
        activation: Union[
            Literal["snake", "snakebeta"], Callable[[Tensor], Tensor]
        ] = "snakebeta",
        *args,
        **kwargs,
    ):
        super().__init__()
        from lt_tensor.model_zoo.activations import alias_free

        if isinstance(activation, str):
            assert activation in [
                "snake",
                "snakebeta",
            ], f"Invalid activation: '{activation}'."
            actv = lambda: get_snake(activation)(
                channels, alpha_logscale=snake_logscale
            )

        else:
            actv = lambda: activation

        ch1_kwargs = dict(
            in_channels=channels, kernel_size=kernel_size, norm="weight_norm"
        )
        ch2_kwargs = dict(
            in_channels=channels,
            kernel_size=kernel_size,
            padding=self.get_padding(kernel_size, 1),
            norm="weight_norm",
        )

        self.convs: List[Callable[[Tensor], Tensor]] = nn.ModuleList()
        for i, d in enumerate(dilation):
            self.convs.append(
                nn.Sequential(
                    alias_free.Activation1d(activation=actv()),
                    self.get_1d_conv(
                        **ch1_kwargs,
                        dilation=d,
                        padding=self.get_padding(kernel_size, d),
                    ),
                    alias_free.Activation1d(activation=actv()),
                    self.get_1d_conv(**ch2_kwargs),
                )
            )

        self.num_layers = len(self.convs)
        self.convs.apply(self._init_conv_weights_a)

    def forward(self, x):
        for layer in self.convs:
            x = layer(x) + x
        return x


class AMPBlock2(ConvBase):
    """Modified from 'https://github.com/NVIDIA/BigVGAN/blob/main/bigvgan.py' under MIT license, found in 'bigvgan/LICENSE'
    AMPBlock applies Snake / SnakeBeta activation functions with trainable parameters that control periodicity, defined for each layer.
    Unlike AMPBlock1, AMPBlock2 does not contain extra Conv1d layers with fixed dilation=1

    Args:
        channels (int): Number of convolution channels.
        kernel_size (int): Size of the convolution kernel. Default is 3.
        dilation (tuple): Dilation rates for the convolutions. Each dilation layer has two convolutions. Default is (1, 3, 5).
        snake_logscale: (bool): to use logscale with snake activation. Default to True.
        activation (str): Activation function type. Should be either 'snake' or 'snakebeta'. Defaults to 'snakebeta'.
    """

    def __init__(
        self,
        channels: int,
        kernel_size: int = 3,
        dilation: tuple = (1, 3, 5),
        snake_logscale: bool = True,
        activation: Union[
            Literal["snake", "snakebeta"], Callable[[Tensor], Tensor]
        ] = "snakebeta",
        *args,
        **kwargs,
    ):
        super().__init__()
        from lt_tensor.model_zoo.activations import alias_free

        if isinstance(activation, str):
            assert activation in [
                "snake",
                "snakebeta",
            ], f"Invalid activation: '{activation}'."
            actv = lambda: get_snake(activation)(
                channels, alpha_logscale=snake_logscale
            )

        else:
            actv = lambda: activation

        self.convs: List[Callable[[Tensor], Tensor]] = nn.ModuleList(
            [
                nn.Sequential(
                    alias_free.Activation1d(activation=actv()),
                    self.get_1d_conv(
                        in_channels=channels,
                        kernel_size=kernel_size,
                        norm="weight_norm",
                        dilation=d,
                        padding=self.get_padding(kernel_size, d),
                    ),
                )
                for d in dilation
            ]
        )
        self.convs.apply(self._init_conv_weights_a)
        self.num_layers = len(self.convs)

    def forward(self, x: Tensor):
        for cnn in self.convs:
            x = cnn(x) + x
        return x
