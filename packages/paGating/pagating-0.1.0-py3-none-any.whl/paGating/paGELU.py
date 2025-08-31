"""
Implementation of the paGELU (Partially Adaptive GELU Gating Unit) activation function.

paGELU extends the paGatingBase with GELU activation for the gating mechanism.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Union, Callable, Optional

from paGating.base import paGatingBase


class paGELU(paGatingBase):
    """Partially Adaptive GELU Gating Unit (paGELU).
    
    paGELU computes: output = A(x) * [α * GELU(B(x)) + (1 - α)]
    where:
        - A(x): Value path (linear projection)
        - B(x): Gating path (linear projection)
        - α: Tunable parameter controlling gating strength (0 ≤ α ≤ 1)
        - GELU: Gaussian Error Linear Unit
        
    When α=0, paGELU becomes a simple linear layer.
    When α=1, paGELU is equivalent to a standard GELU-gated unit.
    
    Args:
        input_dim (int): Dimensionality of input features
        output_dim (int): Dimensionality of output features
        alpha (Union[float, str, Callable], optional): Controls gating strength:
            - float: Fixed value between 0 and 1
            - "learnable": Creates a learnable parameter initialized to 0.5
            - Callable: Function that computes alpha dynamically
            Default: 0.5
        use_gate_norm (bool, optional): Whether to apply GateNorm to the gating pathway
            Default: False
        norm_eps (float, optional): Epsilon for numerical stability in normalization
            Default: 1e-5
        approximate (bool, optional): Whether to use the approximate GELU implementation
            Default: False
    """
    
    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        alpha: Union[float, str, Callable] = 0.5,
        use_gate_norm: bool = False,
        norm_eps: float = 1e-5,
        approximate: bool = False,
    ) -> None:
        # Choose the appropriate GELU implementation
        if approximate:
            activation_fn = F.gelu
        else:
            activation_fn = lambda x: F.gelu(x, approximate="none")
            
        super().__init__(
            input_dim=input_dim,
            output_dim=output_dim,
            activation_fn=activation_fn,
            alpha=alpha,
            use_gate_norm=use_gate_norm,
            norm_eps=norm_eps
        ) 