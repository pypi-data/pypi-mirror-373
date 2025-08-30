__all__ = ["HifiganGenerator", "HifiganConfig"]


from lt_utils.common import *
import torch
from torch import nn, Tensor
from lt_tensor.model_zoo.convs import ConvBase
from lt_utils.file_ops import is_file, load_json
from lt_tensor.model_base import ModelConfig
from torch.nn.utils.parametrizations import weight_norm
from lt_tensor.model_zoo.residual import ResBlock1, ResBlock2


class HifiganConfig(ModelConfig):
    in_channels: int = 80
    upsample_rates: List[Union[int, List[int]]] = [8, 8, 2, 2]
    upsample_kernel_sizes: List[Union[int, List[int]]] = [16, 16, 4, 4]
    upsample_initial_channel: int = 768
    resblock_kernel_sizes: List[Union[int, List[int]]] = [3, 7, 11]
    resblock_dilation_sizes: List[Union[int, List[int]]] = [
        [1, 3, 5],
        [1, 3, 5],
        [1, 3, 5],
    ]
    activation: Union[nn.Module, str] = "leakyrelu"
    resblock_activation: Union[nn.Module, str] = "leakyrelu"
    resblock: int = 0
    activation_kwargs: Dict[str, Any] = dict()
    resblock_activation_kwargs: Dict[str, Any] = dict()
    use_tanh: bool = True
    use_bias_on_final_layer: bool = False
    _activation: nn.Module = None
    _resblock_activation: nn.Module = None

    def __init__(
        self,
        in_channels: int = 80,
        upsample_rates: List[Union[int, List[int]]] = [8, 8, 2, 2],
        upsample_kernel_sizes: List[Union[int, List[int]]] = [16, 16, 4, 4],
        upsample_initial_channel: int = 512,
        resblock_kernel_sizes: List[Union[int, List[int]]] = [3, 7, 11],
        resblock_dilation_sizes: List[Union[int, List[int]]] = [
            [1, 3, 5],
            [1, 3, 5],
            [1, 3, 5],
        ],
        activation: str = "leakyrelu",
        resblock_activation: str = "leakyrelu",
        activation_kwargs: Dict[str, Any] = dict(negative_slope=0.1),
        resblock_activation_kwargs: Dict[str, Any] = dict(negative_slope=0.1),
        resblock: Union[int, str] = 0,
        use_bias_on_final_layer: bool = False,
        use_tanh: bool = True,
        *args,
        **kwargs,
    ):
        settings = {
            "in_channels": kwargs.get("n_mels", in_channels),
            "upsample_rates": upsample_rates,
            "upsample_kernel_sizes": upsample_kernel_sizes,
            "upsample_initial_channel": upsample_initial_channel,
            "resblock_kernel_sizes": resblock_kernel_sizes,
            "resblock_dilation_sizes": resblock_dilation_sizes,
            "activation": activation,
            "resblock_activation": resblock_activation,
            "resblock": resblock,
            "resblock_activation_kwargs": resblock_activation_kwargs,
            "activation_kwargs": activation_kwargs,
            "use_tanh": use_tanh,
            "use_bias_on_final_layer": use_bias_on_final_layer,
        }
        super().__init__(**settings)
        self._forbidden_list.append("_activation")
        self._forbidden_list.append("_resblock_activation")

    def post_process(self):
        assert (isinstance(self.resblock, int) and self.resblock in [0, 1]) or (
            isinstance(self.resblock, str) and self.resblock in ["0", "1", "2"]
        )
        if isinstance(self.resblock, str):
            self.resblock = 0 if self.resblock in ["0", "1"] else 1

        self._activation = (
            self.get_activation(activation=self.activation)
            if isinstance(self.activation, str)
            else self.activation
        )
        self._resblock_activation = (
            self.get_activation(
                activation=self.resblock_activation, **self.resblock_activation_kwargs
            )
            if isinstance(self.resblock_activation, str)
            else self.resblock_activation
        )

    @staticmethod
    def get_cfg_v1():
        return {
            "upsample_rates": [8, 8, 2, 2],
            "upsample_kernel_sizes": [16, 16, 4, 4],
            "upsample_initial_channel": 512,
            "resblock_kernel_sizes": [3, 7, 11],
            "resblock_dilation_sizes": [[1, 3, 5], [1, 3, 5], [1, 3, 5]],
            "resblock": 0,
            "use_tanh": True,
            "use_bias_on_final_layer": True,
        }

    @staticmethod
    def get_cfg_v2():
        return {
            "upsample_rates": [8, 8, 2, 2],
            "upsample_kernel_sizes": [16, 16, 4, 4],
            "upsample_initial_channel": 128,
            "resblock_kernel_sizes": [3, 7, 11],
            "resblock_dilation_sizes": [[1, 3, 5], [1, 3, 5], [1, 3, 5]],
            "resblock": 0,
            "use_tanh": True,
            "use_bias_on_final_layer": True,
        }

    @staticmethod
    def get_cfg_v3():
        return {
            "upsample_rates": [8, 8, 4],
            "upsample_kernel_sizes": [16, 16, 8],
            "upsample_initial_channel": 256,
            "resblock_kernel_sizes": [3, 5, 7],
            "resblock_dilation_sizes": [[1, 2], [2, 6], [3, 12]],
            "resblock": 1,
            "use_tanh": True,
            "use_bias_on_final_layer": True,
            
        }


class HifiganGenerator(ConvBase):
    def __init__(
        self,
        cfg: Union[HifiganConfig, Dict[str, object]] = HifiganConfig(),
        extra_layer: nn.Module = nn.Identity(),
    ):
        super().__init__()
        cfg = cfg if isinstance(cfg, HifiganConfig) else HifiganConfig(**cfg)
        self.cfg = cfg

        self.num_kernels = len(cfg.resblock_kernel_sizes)
        self.num_upsamples = len(cfg.upsample_rates)
        self.conv_pre = weight_norm(
            nn.Conv1d(cfg.in_channels, cfg.upsample_initial_channel, 7, 1, padding=3)
        )
        resblock = ResBlock1 if cfg.resblock == 0 else ResBlock2
        self.activation = cfg._activation
        self.ups = nn.ModuleList()
        for i, (u, k) in enumerate(zip(cfg.upsample_rates, cfg.upsample_kernel_sizes)):
            self.ups.append(
                weight_norm(
                    nn.ConvTranspose1d(
                        cfg.upsample_initial_channel // (2**i),
                        cfg.upsample_initial_channel // (2 ** (i + 1)),
                        k,
                        u,
                        padding=(k - u) // 2,
                    )
                )
            )

        self.resblocks = nn.ModuleList()
        for i in range(len(self.ups)):
            ch = cfg.upsample_initial_channel // (2 ** (i + 1))
            for j, (k, d) in enumerate(
                zip(cfg.resblock_kernel_sizes, cfg.resblock_dilation_sizes)
            ):
                self.resblocks.append(resblock(ch, k, d, cfg._resblock_activation))

        self.conv_post = weight_norm(
            nn.Conv1d(ch, 1, 7, 1, padding=3, bias=self.cfg.use_bias_on_final_layer)
        )
        self.extra_layer = extra_layer

        self.ups.apply(self._init_conv_weights_a)
        self.conv_pre.apply(self._init_conv_weights_a)
        self.conv_post.apply(self._init_conv_weights_a)
        self.resblocks.apply(self._init_conv_weights_a)

    def forward(self, x: Tensor):
        x = self.conv_pre(x)
        for i in range(self.num_upsamples):
            x = self.ups[i](self.activation(x))
            xs = torch.zeros_like(x, device=x.device)
            for j in range(self.num_kernels):
                xs += self.resblocks[i * self.num_kernels + j](x)
            x = xs / self.num_kernels
        x = self.conv_post(self.activation(x))
        x = self.extra_layer(x)  # maybe a post-processor, or an adapter?
        if self.cfg.use_tanh:
            return x.tanh()
        return x

    @classmethod
    def from_pretrained(
        cls,
        model_file: PathLike,
        model_config: Union[
            HifiganConfig, Dict[str, Any], Dict[str, Any], PathLike
        ] = HifiganConfig(),
        *,
        remove_norms: bool = False,
        strict: bool = False,
        map_location: Union[str, torch.device] = torch.device("cpu"),
        weights_only: bool = False,
        mmap: Optional[bool] = None,
        assign: bool = False,
        **kwargs,
    ):
        is_file(model_file, validate=True)
        if isinstance(map_location, str):
            map_location = torch.device(map_location)
        model_state_dict = torch.load(
            model_file,
            weights_only=weights_only,
            map_location=map_location,
            mmap=mmap,
        )

        if isinstance(model_config, (HifiganConfig, dict)):
            h = model_config
        elif isinstance(model_config, (str, Path, bytes)):
            h = HifiganConfig(**load_json(model_config, {}))

        model = cls(h)
        if remove_norms:
            model.remove_norms()
        try:
            model.load_state_dict(model_state_dict, strict=strict, assign=assign)
            return model
        except RuntimeError as e:
            if remove_norms:
                raise e
            print(
                f"[INFO] the pretrained checkpoint does not contain weight norm. Loading the checkpoint after removing weight norm!"
            )
            model.remove_norms()
            model.load_state_dict(model_state_dict, strict=strict, assign=assign)
        return model
