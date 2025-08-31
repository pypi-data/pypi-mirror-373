"""
Generic implementation of the paUnit (Partially Adaptive Gating Unit) activation function.

paUnit extends the paGatingBase with a user-specified activation function for the gating mechanism.
"""

import torch
import torch.nn as nn
from typing import Union, Callable, Optional

from paGating.base import paGatingBase


class paUnit(paGatingBase):
    """Generic Partially Adaptive Gating Unit (paUnit).
    
    paUnit computes: output = A(x) * [α * activation_fn(B(x)) + (1 - α)]
    where:
        - A(x): Value path (linear projection)
        - B(x): Gating path (linear projection)
        - α: Tunable parameter controlling gating strength (0 ≤ α ≤ 1)
        - activation_fn: User-provided activation function
        
    When α=0, paUnit becomes a simple linear layer.
    When α=1, paUnit is equivalent to a standard gated unit with the provided activation.
    
    This class allows for creating custom paGating units with any PyTorch-compatible
    activation function.
    
    Args:
        input_dim (int): Dimensionality of input features
        output_dim (int): Dimensionality of output features
        activation_fn (Callable): Function used in the gating path B(x)
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
        activation_fn: Callable,
        alpha: Union[float, str, Callable] = 0.5,
        use_gate_norm: bool = False,
        norm_eps: float = 1e-5,
    ) -> None:
        # Initialize with the provided activation function for gating
        super().__init__(
            input_dim=input_dim,
            output_dim=output_dim,
            activation_fn=activation_fn,
            alpha=alpha,
            use_gate_norm=use_gate_norm,
            norm_eps=norm_eps
        ) 