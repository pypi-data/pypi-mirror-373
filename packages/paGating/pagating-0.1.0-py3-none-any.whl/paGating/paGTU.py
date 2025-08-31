"""
Implementation of the paGTU (Partially Adaptive Gated Tanh Unit) activation function.

paGTU extends the paGatingBase with sigmoid activation for the gating mechanism
and tanh for the value path.
"""

import torch
import torch.nn as nn
from typing import Union, Callable, Optional

from paGating.base import paGatingBase


class paGTU(paGatingBase):
    """Partially Adaptive Gated Tanh Unit (paGTU).
    
    paGTU computes: output = tanh(A(x)) * [α * sigmoid(B(x)) + (1 - α)]
    where:
        - A(x): Value path (linear projection)
        - B(x): Gating path (linear projection)
        - α: Tunable parameter controlling gating strength (0 ≤ α ≤ 1)
        
    When α=0, paGTU becomes tanh(A(x)).
    When α=1, paGTU is equivalent to a standard GTU (Gated Tanh Unit).
    
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
        # Initialize with tanh activation function for gating
        super().__init__(
            input_dim=input_dim,
            output_dim=output_dim,
            activation_fn=torch.tanh,
            alpha=alpha,
            use_gate_norm=use_gate_norm,
            norm_eps=norm_eps
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass for paGTU.
        
        Overrides the base class forward to apply tanh to the value path.
        
        Args:
            x (torch.Tensor): Input tensor of shape (batch_size, input_dim)
            
        Returns:
            torch.Tensor: Output tensor of shape (batch_size, output_dim)
        """
        # Compute value path A(x) with tanh activation
        value = torch.tanh(self.value_proj(x))
        
        # Compute gate path B(x)
        gate = self.gate_proj(x)
        gate_activated = self.activation_fn(gate)
        
        # Get alpha value (could be static, learnable, or computed)
        alpha = self.get_alpha(x)
        
        # Ensure alpha has the right shape for broadcasting
        if alpha.dim() == 0:
            alpha = alpha.view(1, 1)
        
        # Compute partially gated output
        output = value * (alpha * gate_activated + (1.0 - alpha))
        
        return output