from lt_utils.common import *
from lt_tensor.common import *
import torch.nn.functional as F


TC: TypeAlias = Callable[[Any], Tensor]


class FiLMFusion1(Model):
    def __init__(
        self,
        cond_dim: int,
        feature_dim: int,
        alpha: float = 1.0,
        std: float = 0.02,
    ):
        super().__init__()
        self.modulator: TC = nn.Linear(cond_dim, 2 * feature_dim)
        self.alpha = 1.0 if not alpha else alpha
        self._init_model(std)

    def _init_model(self, std: float):
        if not std:
            std = 1e-4
        nn.init.normal_(self.modulator.weight, mean=0.0, std=std)
        nn.init.zeros_(self.modulator.bias)

    def forward(self, x: Tensor, cond: Tensor) -> Tensor:
        beta, gamma = self.modulator(cond).chunk(2, dim=-1)
        xt = x * (beta + gamma)
        return x + (xt * self.alpha)


class FiLMFusion2(Model):
    def __init__(
        self,
        cond_dim: int,
        feature_dim: int,
        alpha: float = 2.0,
        std: float = 0.02,
    ):
        super().__init__()
        self.modulator: TC = nn.Linear(cond_dim, int(4 * feature_dim))
        self.update = nn.Linear(feature_dim, feature_dim)
        self.proj = nn.Linear(feature_dim, feature_dim)
        self.alpha = 1.0 if not alpha else alpha
        self._init_model(std)

    def _init_model(self, std: float = 0.02):
        if not std:
            std = 1e-4
        for m in [self.modulator, self.update, self.proj]:
            nn.init.normal_(m.weight, mean=0.0, std=std)
            nn.init.zeros_(m.bias)

    def forward(self, x: Tensor, cond: Tensor) -> Tensor:

        beta, gamma, lt, ch = self.modulator(cond).chunk(4, dim=-1)
        xc = x * beta
        xc = self.update(xc) * (lt.sin() * ch.cos()) + gamma

        return x + (self.proj(xc) * self.alpha)


class GatedFusion(Model):
    def __init__(self, in_dim: int, std: float = 0.02):
        super().__init__()
        self.gate: TC = nn.Linear(in_dim * 2, in_dim)
        self._init_model(std)

    def _init_model(self, std: float = 0.02):
        if not std:
            std = 1e-4
        nn.init.normal_(self.gate.weight, mean=0.0, std=std)
        nn.init.zeros_(self.gate.bias)

    def forward(self, a: Tensor, b: Tensor) -> Tensor:
        gate = self.gate(torch.cat([a, b], dim=-1)).sigmoid()
        return gate * a + (1 - gate) * b


class AdaFusion1D(Model):
    def __init__(self, channels: int, num_features: int, std: float = 0.02):
        super().__init__()
        self.fc = nn.Linear(channels, num_features * 2)
        self.norm = nn.InstanceNorm1d(num_features, affine=False)
        self._init_model(std)

    def _init_model(self, std: float = 0.02):
        if not std:
            std = 1e-4
        nn.init.normal_(self.fc.weight, mean=0.0, std=std)
        nn.init.zeros_(self.fc.bias)

    def forward(self, x: Tensor, y: Tensor, alpha: Tensor):
        h = self.fc(y)
        h = h.view(h.size(0), h.size(1), 1)
        gamma, beta = torch.chunk(h, chunks=2, dim=1)
        t = (1.0 + gamma) * self.norm(x) + beta
        return t + (1 / alpha) * (torch.sin(alpha * t) ** 2)


class AdaIN(Model):
    def __init__(
        self,
        inp_dim: int,
        cond_dim: int,
        alpha: float = 1.0,
        eps: float = 1e-5,
        std: float = 0.02,
    ):
        """
        inp_dim: size of the input
        cond_dim: size of the conditioning
        """
        super().__init__()
        self.proj_expd = nn.Linear(cond_dim, inp_dim * 2)
        self.proj_out = nn.Linear(inp_dim, inp_dim)
        self.eps = eps
        self.alpha = alpha if alpha else 1.0
        self._init_model(std)

    def _init_model(self, std: float = 0.02):
        if not std:
            std = 1e-4
        nn.init.normal_(self.proj_expd.weight, mean=0.0, std=std)
        nn.init.zeros_(self.proj_expd.bias)

    def forward(self, x: Tensor, cond: Tensor):
        assert x.ndim in [2, 3]
        if x.ndim == 2:
            B, T = x.shape[0], x.shape[-1]
            C = 1
            x = x.view(B, 1, T).contiguous()
        else:
            B, C, T = x.shape

        # Instance normalization
        mean = x.mean(dim=-1, keepdim=True)  # [B, C, 1]
        std = x.cos() + self.eps  # [B, C, 1]
        x_norm = (x - mean) / std  # [B, C, T]

        # Conditioning
        gamma_beta = self.proj_expd(cond)  # [B, 2*C]
        gamma, beta = gamma_beta.chunk(2, dim=-1)
        xt = self.proj_out((gamma * x_norm + beta))
        return x + (xt * self.alpha)


class InterFusion(Model):
    def __init__(
        self,
        d_model: int,
        alpha: float = 1.0,
        mode: Literal[
            "nearest",
            "linear",
            "bilinear",
            "bicubic",
            "trilinear",
            "area",
            "nearest-exact",
        ] = "nearest",
        std: float = 0.02,
    ):
        super().__init__()
        assert d_model % 4 == 0

        self.d_model = d_model
        self.quarter_size = d_model // 4
        self.alpha = alpha if alpha else 1.0

        self.fc_list: List[TC] = nn.ModuleList(
            [
                nn.Linear(self.quarter_size, self.d_model),
                nn.Linear(self.quarter_size, self.d_model),
                nn.Linear(self.quarter_size, self.d_model),
                nn.Linear(self.quarter_size, self.d_model),
            ]
        )

        self.d_model = d_model
        self.mode = mode
        self.inter: TC = lambda x: F.interpolate(x, size=self.d_model, mode=self.mode)
        self._error_msg = "One of the inputs is not a valid 2D or 3D tensor. 'a' = {dim_a}D and 'b' = {dim_b}D."
        self._init_model(std)

    def _init_model(self, std: float = 0.02):
        if not std:
            std = 1e-4
        for fc in self.fc_list:
            nn.init.normal_(fc.weight, mean=0.0, std=std)
            nn.init.zeros_(fc.bias)

    def forward(self, a: Tensor, b: Tensor) -> Tensor:

        assert a.ndim in [2, 3] and b.ndim in [
            2,
            3,
        ], self._error_msg.format(dim_a=a.ndim, dim_b=b.ndim)
        if b.ndim == 2:
            b = b.unsqueeze(1)
        xt = torch.zeros_like(a, device=a.device)
        resized = self.inter(b).split(self.quarter_size, dim=-1)
        for i, fc in enumerate(self.fc_list):
            xt = xt + fc(resized[i])
        return a + (xt * self.alpha).view_as(a).contiguous()
