"""
Implementation of the paGLU (Partially Adaptive Gated Linear Unit) activation function.

paGLU extends the paGatingBase with sigmoid activation for the gating mechanism.
"""

import torch
import torch.nn as nn
from typing import Union, Callable, Optional
import torch.nn.functional as F

from paGating.base import paGatingBase


class paGLU(paGatingBase):
    """Partially Adaptive Gated Linear Unit (paGLU).
    
    paGLU computes: output = A(x) * [α * sigmoid(B(x)) + (1 - α)]
    where:
        - A(x): Value path (linear projection)
        - B(x): Gating path (linear projection)
        - α: Tunable parameter controlling gating strength (0 ≤ α ≤ 1)
        
    When α=0, paGLU becomes a simple linear layer.
    When α=1, paGLU is equivalent to a standard GLU (Gated Linear Unit).
    
    Args:
        input_dim (int): Dimensionality of input features
        output_dim (int): Dimensionality of output features
        alpha (Union[float, str, Callable], optional): Controls gating strength:
            - float: Fixed value between 0 and 1
            - "learnable": Creates a learnable parameter initialized to 0.5
            - Callable: Function that computes alpha dynamically
            Default: 0.5
        use_gate_norm (bool, optional): Whether to use gate normalization
        norm_eps (float, optional): Epsilon for gate normalization
    """
    
    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        alpha: Union[float, str, Callable] = 0.5,
        use_gate_norm: bool = False,
        norm_eps: float = 1e-5,
    ) -> None:
        # Initialize with sigmoid activation function for gating
        super().__init__(
            input_dim=input_dim,
            output_dim=output_dim,
            activation_fn=F.sigmoid,
            alpha=alpha,
            use_gate_norm=use_gate_norm,
            norm_eps=norm_eps
        )