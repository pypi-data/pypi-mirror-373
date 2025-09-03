# Implementation adapted and modified from https://github.com/EdwardDixon/snake under the MIT license.

import torch
from torch import nn, sin, pow


class Snake(nn.Module):
    """
    Implementation of a sine-based periodic activation function
    Shape:
        - Input: (B, C, T)
        - Output: (B, C, T), same shape as the input
    Parameters:
        - alpha - trainable parameter
    References:
        - This activation function is from this paper by Liu Ziyin, Tilman Hartwig, Masahito Ueda:
        https://arxiv.org/abs/2006.08195
    Examples:
        >>> a1 = snake(256)
        >>> x = torch.randn(256)
        >>> x = a1(x)
    """

    def __init__(
        self,
        in_features: int,
        alpha: float = 1.0,
        requires_grad: bool = True,
        alpha_logscale: bool = False,
    ):
        """
        Initialization.
        INPUT:
            - in_features: shape of the input
            - alpha: trainable parameter
            alpha is initialized to 1 by default, higher values = higher-frequency.
            alpha will be trained along with the rest of your model.
        """
        super().__init__()
        self.in_features = in_features
        self.alpha_logscale = alpha_logscale
        param_fn = torch.zeros if self.alpha_logscale else torch.ones
        self.alpha = nn.Parameter(
            param_fn((1, in_features, 1)) * alpha, requires_grad=requires_grad
        )
        self.eps = 1e-8

    def _log_scale(self):
        if self.alpha_logscale:
            return self.alpha.exp()
        return self.alpha

    def forward(self, x: torch.Tensor):
        """
        Forward pass of the function.
        Applies the function to the input elementwise.
        Snake ∶= x + 1/a * sin^2 (xa)
        """
        alpha = self._log_scale()
        x = x + (1.0 / (alpha + self.eps)) * pow(sin(x * alpha), 2)
        return x


class SnakeBeta(nn.Module):
    """
    A modified Snake function which uses separate parameters for the magnitude of the periodic components
    Shape:
        - Input: (B, C, T)
        - Output: (B, C, T), same shape as the input
    Parameters:
        - alpha - trainable parameter that controls frequency
        - beta - trainable parameter that controls magnitude
    References:
        - This activation function is a modified version based on this paper by Liu Ziyin, Tilman Hartwig, Masahito Ueda:
        https://arxiv.org/abs/2006.08195
    Examples:
        >>> a1 = snakebeta(256)
        >>> x = torch.randn(256)
        >>> x = a1(x)
    """

    def __init__(
        self,
        in_features: int,
        alpha: float = 1.0,
        requires_grad: bool = True,
        alpha_logscale: bool = False,
    ):
        """
        Initialization.
        INPUT:
            - in_features: shape of the input
            - alpha - trainable parameter that controls frequency
            - beta - trainable parameter that controls magnitude
            alpha is initialized to 1 by default, higher values = higher-frequency.
            beta is initialized to 1 by default, higher values = higher-magnitude.
            alpha will be trained along with the rest of your model.
        """
        super().__init__()
        self.in_features = in_features

        # initialize alpha
        self.alpha_logscale = alpha_logscale
        """
        if log scale alphas initialized to zeros
        else linear scale alphas is initialized to ones
        """
        param_fn = torch.zeros if alpha_logscale else torch.ones
        self.alpha = nn.Parameter(
            param_fn((1, in_features, 1)) * alpha, requires_grad=requires_grad
        )
        self.beta = nn.Parameter(
            param_fn((1, in_features, 1)) * alpha, requires_grad=requires_grad
        )
        self.eps = 1e-8

    def _log_scale(self):
        if self.alpha_logscale:
            return self.alpha.exp(), self.beta.exp()
        return self.alpha, self.beta

    def forward(self, x: torch.Tensor):
        """
        Forward pass of the function.
        Applies the function to the input elementwise.
        SnakeBeta ∶= x + 1/b * sin^2 (xa)
        """
        alpha, beta = self._log_scale()
        return x + (1.0 / (beta + self.eps)) * pow(sin(x * alpha), 2)
