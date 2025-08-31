"""
Implementation of the paSwishU (Partially Adaptive Swish Unit) activation function.

paSwishU extends the paGatingBase with Swish activation for the gating mechanism.
"""

import torch
import torch.nn as nn
from typing import Union, Callable, Optional

from paGating.base import paGatingBase


def swish(x: torch.Tensor) -> torch.Tensor:
    """Swish activation function: x * sigmoid(x)
    
    Args:
        x (torch.Tensor): Input tensor
        
    Returns:
        torch.Tensor: Activated tensor with same shape as input
    """
    return x * torch.sigmoid(x)


class paSwishU(paGatingBase):
    """Partially Adaptive Swish Unit (paSwishU).
    
    paSwishU computes: output = A(x) * [α * swish(B(x)) + (1 - α)]
    where:
        - A(x): Value path (linear projection)
        - B(x): Gating path (linear projection)
        - α: Tunable parameter controlling gating strength (0 ≤ α ≤ 1)
        - swish(x) = x * sigmoid(x)
        
    When α=0, paSwishU becomes a simple linear layer.
    When α=1, paSwishU uses full Swish gating.
    
    Args:
        input_dim (int): Dimensionality of input features
        output_dim (int): Dimensionality of output features
        alpha (Union[float, str, Callable], optional): Controls gating strength:
            - float: Fixed value between 0 and 1
            - "learnable": Creates a learnable parameter initialized to 0.5
            - Callable: Function that computes alpha dynamically
            Default: 0.5
        beta (float, optional): Scaling factor for the gating function
        use_gate_norm (bool, optional): Whether to use gate normalization
        norm_eps (float, optional): Epsilon for gate normalization
    """
    
    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        alpha: Union[float, str, Callable] = 0.5,
        beta: float = 1.0,
        use_gate_norm: bool = False,
        norm_eps: float = 1e-5,
    ) -> None:
        self.beta = beta
        super().__init__(
            input_dim=input_dim,
            output_dim=output_dim,
            activation_fn=lambda x: x * torch.sigmoid(self.beta * x),
            alpha=alpha,
            use_gate_norm=use_gate_norm,
            norm_eps=norm_eps
        )