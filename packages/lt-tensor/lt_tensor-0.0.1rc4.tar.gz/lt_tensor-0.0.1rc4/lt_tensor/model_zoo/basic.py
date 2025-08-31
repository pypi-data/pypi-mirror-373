import math
from lt_utils.common import *
from lt_tensor.common import *
from einops import repeat
import torch.nn.functional as F
from torch.nn.utils.parametrizations import weight_norm
from lt_tensor.transform import get_sinusoidal_embedding


class UpSampleConv1D(Model):
    def __init__(self, upsample: bool = False, dim_in: int = 0, dim_out: int = 0):
        super().__init__()
        if upsample:
            self.upsample = lambda x: F.interpolate(x, scale_factor=2, mode="nearest")
        else:
            self.upsample = nn.Identity()

        if dim_in == dim_out:
            self.learned = nn.Identity()
        else:
            self.learned = weight_norm(nn.Conv1d(dim_in, dim_out, 1, 1, 0, bias=False))

    def forward(self, x):
        x = self.upsample(x)
        return self.learned(x)


class MLPBase(Model):
    def __init__(
        self,
        d_model: int,
        ff_dim: int,
        n_classes: int,
        activation: nn.Module = nn.LeakyReLU(0.1),
        norm: nn.Module = nn.Dropout(0.01),
    ):
        """Creates a MLP block, with the chosen activation function and the normalizer."""
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(d_model, ff_dim),
            activation,
            norm,
            nn.Linear(ff_dim, n_classes),
        )

    def forward(self, x: Tensor):
        return self.net(x)


class MLP(Model):
    def __init__(
        self,
        d_model: int,
        ff_dim: int,
        n_classes: int,
        activation: nn.Module = nn.LeakyReLU(0.1),
        norm: nn.Module = nn.Dropout(0.01),
        layers: int = 2,
    ):
        super().__init__()
        assert layers >= 1
        self.net = nn.Sequential()

        nc = n_classes if layers == 1 else ff_dim
        self.net.append(
            MLPBase(
                d_model=d_model,
                ff_dim=ff_dim,
                n_classes=nc,
                norm=norm,
                activation=activation,
            )
        )
        if layers > 1:
            if layers == 2:
                self.net.append(
                    MLPBase(
                        d_model=ff_dim,
                        ff_dim=ff_dim,
                        n_classes=n_classes,
                        norm=norm,
                        activation=activation,
                    )
                )
            else:
                for _ in range(layers - 1):
                    self.net.append(
                        MLPBase(
                            d_model=ff_dim,
                            ff_dim=ff_dim,
                            n_classes=ff_dim,
                            norm=norm,
                            activation=activation,
                        )
                    )
                self.net.append(
                    MLPBase(
                        d_model=ff_dim,
                        ff_dim=ff_dim,
                        n_classes=n_classes,
                        norm=norm,
                        activation=activation,
                    )
                )

    def forward(self, x: Tensor):
        return self.net(x)


class Conv2DBlock(Model):
    def __init__(self, channels):
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv2d(channels, channels, 3, padding=1),
            nn.LeakyReLU(0.1),
            nn.Conv2d(channels, channels, 3, padding=1),
        )

    def forward(self, x):
        return x + self.block(x)


class TimestepEmbedder(Model):
    def __init__(self, dim_emb: int, proj_dim: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(dim_emb, proj_dim),
            nn.SiLU(),
            nn.Linear(proj_dim, proj_dim),
        )

    def forward(self, t: torch.Tensor) -> torch.Tensor:
        # t: [B] (long)
        emb = get_sinusoidal_embedding(t, self.net[0].in_features)  # [B, dim_emb]
        return self.net(emb)  # [B, proj_dim]


class GRUEncoder(Model):
    def __init__(
        self,
        input_dim: int,
        hidden_dim: int,
        num_layers: int = 1,
        bidirectional: bool = False,
        dropout: float = 0.01,
    ):
        super().__init__()
        self.gru = nn.GRU(
            input_dim,
            hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=bidirectional,
            dropout=0 if num_layers < 2 else dropout,
        )
        self.output_dim = hidden_dim * (2 if bidirectional else 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: [B, T, input_dim]
        output, _ = self.gru(x)  # output: [B, T, hidden_dim*D]
        return output


class ConvBlock1D(Model):
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: int = 3,
        stride: int = 1,
        norm: bool = True,
        residual: bool = False,
    ):
        super().__init__()
        padding = (kernel_size - 1) // 2
        self.conv = nn.Conv1d(in_channels, out_channels, kernel_size, stride, padding)
        self.norm = nn.BatchNorm1d(out_channels) if norm else nn.Identity()
        self.act = nn.LeakyReLU(0.1)
        self.residual = residual and in_channels == out_channels

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        y = self.act(self.norm(self.conv(x)))
        return x + y if self.residual else y


class TemporalPredictor(Model):
    def __init__(
        self,
        d_model: int,
        hidden_dim: int = 128,
        n_layers: int = 2,
        dropout: float = 0.1,
    ):
        super().__init__()
        layers = []
        for _ in range(n_layers):
            layers.append(nn.Conv1d(d_model, hidden_dim, kernel_size=3, padding=1))
            layers.append(nn.LeakyReLU(0.1))
            layers.append(nn.LayerNorm(hidden_dim))
            layers.append(nn.Dropout(dropout))
            d_model = hidden_dim
        self.network = nn.Sequential(*layers)
        self.proj = nn.Linear(hidden_dim, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: [B, T, D]
        x = x.transpose(1, 2)  # [B, D, T]
        x = self.network(x)  # [B, H, T]
        x = x.transpose(1, 2)  # [B, T, H]
        return self.proj(x).squeeze(-1)  # [B, T]


class ExClassifier(Model):
    def __init__(self, in_features: int = 1, num_classes=5):
        super().__init__()
        self.model = nn.Sequential(
            nn.Conv1d(in_features, 256, kernel_size=3, padding=1),
            nn.LeakyReLU(0.2),
            nn.Conv1d(256, 256, kernel_size=3, padding=1, groups=4),
            nn.BatchNorm1d(256),
            nn.LeakyReLU(0.2),
            nn.Conv1d(256, 256, kernel_size=3, padding=1),
            nn.BatchNorm1d(256),
            nn.LeakyReLU(0.2),
            nn.AdaptiveAvgPool1d(1),  # Output shape: [B, 64, 1]
            nn.Flatten(),  # -> [B, 64]
            nn.Linear(256, num_classes),
        )
        self.eval()

    def forward(self, x):
        return self.model(x)


class LoRALinearLayer(Model):

    def __init__(
        self,
        in_features: int,
        out_features: int,
        rank: int = 4,
        alpha: float = 1.0,
    ):
        super().__init__()
        self.down = nn.Linear(in_features, rank, bias=False)
        self.up = nn.Linear(rank, out_features, bias=False)
        self.alpha = alpha
        self.rank = rank
        self.out_features = out_features
        self.in_features = in_features
        self.ah = self.alpha / self.rank
        self._down_dt = self.down.weight.dtype

        nn.init.normal_(self.down.weight, std=1 / rank)
        nn.init.zeros_(self.up.weight)

    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        orig_dtype = hidden_states.dtype
        down_hidden_states = self.down(hidden_states.to(self._down_dt))
        up_hidden_states = self.up(down_hidden_states) * self.ah
        return up_hidden_states.to(orig_dtype)


class LoRAConv1DLayer(Model):
    def __init__(
        self,
        in_features: int,
        out_features: int,
        kernel_size: Union[int, Tuple[int, ...]] = 1,
        rank: int = 4,
        alpha: float = 1.0,
    ):
        super().__init__()
        self.down = nn.Conv1d(
            in_features, rank, kernel_size, padding=kernel_size // 2, bias=False
        )
        self.up = nn.Conv1d(
            rank, out_features, kernel_size, padding=kernel_size // 2, bias=False
        )
        self.ah = alpha / rank
        self._down_dt = self.down.weight.dtype
        nn.init.kaiming_uniform_(self.down.weight, a=math.sqrt(5))
        nn.init.zeros_(self.up.weight)

    def forward(self, inputs: Tensor) -> Tensor:
        orig_dtype = inputs.dtype
        down_hidden_states = self.down(inputs.to(self._down_dt))
        up_hidden_states = self.up(down_hidden_states) * self.ah
        return up_hidden_states.to(orig_dtype)


class LoRAConv2DLayer(Model):
    def __init__(
        self,
        in_features: int,
        out_features: int,
        kernel_size: Union[int, Tuple[int, ...]] = (1, 1),
        rank: int = 4,
        alpha: float = 1.0,
    ):
        super().__init__()
        self.down = nn.Conv2d(
            in_features,
            rank,
            kernel_size,
            padding="same",
            bias=False,
        )
        self.up = nn.Conv2d(
            rank,
            out_features,
            kernel_size,
            padding="same",
            bias=False,
        )
        self.ah = alpha / rank

        nn.init.kaiming_normal_(self.down.weight, a=0.2)
        nn.init.zeros_(self.up.weight)

    def forward(self, inputs: Tensor) -> Tensor:
        orig_dtype = inputs.dtype
        down_hidden_states = self.down(inputs.to(self._down_dt))
        up_hidden_states = self.up(down_hidden_states) * self.ah
        return up_hidden_states.to(orig_dtype)
