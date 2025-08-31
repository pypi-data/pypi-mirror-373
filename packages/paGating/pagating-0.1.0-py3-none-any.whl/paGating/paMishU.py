"""
Implementation of the paMishU (Partially Adaptive Mish Gating Unit) activation function.

paMishU extends the paGatingBase with Mish activation for the gating mechanism.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Union, Callable, Optional

from paGating.base import paGatingBase
from paGating.activation_fns import mish


class paMishU(paGatingBase):
    """Partially Adaptive Mish Gating Unit (paMishU).
    
    paMishU computes: output = A(x) * [α * Mish(B(x)) + (1 - α)]
    where:
        - A(x): Value path (linear projection)
        - B(x): Gating path (linear projection)
        - α: Tunable parameter controlling gating strength (0 ≤ α ≤ 1)
        - Mish: x * tanh(softplus(x))
        
    When α=0, paMishU becomes a simple linear layer.
    When α=1, paMishU is equivalent to a standard Mish-gated unit.
    
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
        # Initialize with Mish activation function for gating
        super().__init__(
            input_dim=input_dim,
            output_dim=output_dim,
            activation_fn=mish,
            alpha=alpha,
            use_gate_norm=use_gate_norm,
            norm_eps=norm_eps
        ) 