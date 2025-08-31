"""
Base class for Partially Adaptive Gating (paGating) activation functions.

This module provides a foundational class that implements the core functionality 
for all paGating units, which use a tunable parameter α to control the strength 
of the gating mechanism.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Union, Callable, Optional, Dict, Any

from .norms import GateNorm


class paGatingBase(nn.Module):
    """Base class for partially adaptive gating (paGating) activation functions.
    
    paGating units compute: output = A(x) * [α * activation_fn(B(x)) + (1 - α)]
    where:
        - A(x): Value path (linear projection)
        - B(x): Gating path (linear projection)
        - α: Tunable parameter controlling gating strength (0 ≤ α ≤ 1)
        - activation_fn: Any differentiable activation function
        
    This base class handles the core computation logic shared across all paGating variants,
    while specific implementations (paGLU, paGTU, etc.) only need to specify their activation function.
    
    Args:
        input_dim (int): Dimensionality of input features
        output_dim (int): Dimensionality of output features
        activation_fn (Callable): Function used in the gating path B(x)
        alpha (Union[float, str, Callable]): Controls gating strength:
            - float: Fixed value between 0 and 1
            - "learnable": Creates a learnable parameter initialized to 0.5
            - Callable: Function that computes alpha dynamically (e.g., based on input)
        use_gate_norm (bool): Whether to apply GateNorm to the gating pathway
        norm_eps (float): Epsilon for numerical stability in normalization
            
    Note:
        When α=0, the unit performs a simple linear projection: output = A(x)
        When α=1, the unit performs full gating: output = A(x) * activation_fn(B(x))
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
        super().__init__()
        
        # Linear projections for value and gate paths
        self.value_proj = nn.Linear(input_dim, output_dim)
        self.gate_proj = nn.Linear(input_dim, output_dim)
        
        # Store activation function
        self.activation_fn = activation_fn
        
        # Optional gate normalization
        self.use_gate_norm = use_gate_norm
        if use_gate_norm:
            self.gate_norm = GateNorm(output_dim, eps=norm_eps)
        else:
            self.gate_norm = None
        
        # Handle alpha parameter based on type
        self.alpha_fn = None
        self.alpha_param = None
        
        if isinstance(alpha, float):
            # Fixed alpha value
            if not 0 <= alpha <= 1:
                raise ValueError(f"Alpha must be between 0 and 1, got {alpha}")
            self.register_buffer('alpha_fixed', torch.tensor(alpha, dtype=torch.float))
        elif alpha == "learnable":
            # Learnable alpha parameter
            self.alpha_param = nn.Parameter(torch.tensor(0.5, dtype=torch.float))
        elif callable(alpha):
            # Callable function to compute alpha dynamically
            self.alpha_fn = alpha
        else:
            raise ValueError(
                f"Alpha must be a float, 'learnable', or callable. Got {type(alpha)}"
            )
    
    def get_alpha(self, x: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Get the current alpha value.
        
        Args:
            x (Optional[torch.Tensor]): Input tensor, required if alpha is callable
            
        Returns:
            torch.Tensor: The alpha value as a tensor (scalar or per-input)
        """
        if self.alpha_fn is not None:
            if x is None:
                raise ValueError("Input tensor is required when alpha is callable")
            return self.alpha_fn(x)
        elif self.alpha_param is not None:
            # Apply sigmoid to ensure alpha is between 0 and 1
            return torch.sigmoid(self.alpha_param)
        else:
            return self.alpha_fixed
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass for paGating units.
        
        Computes: output = A(x) * [α * activation_fn(B(x)) + (1 - α)]
        
        Args:
            x (torch.Tensor): Input tensor of shape (batch_size, input_dim)
            
        Returns:
            torch.Tensor: Output tensor of shape (batch_size, output_dim)
        """
        # Compute value path A(x)
        value = self.value_proj(x)
        
        # Compute gate path B(x)
        gate = self.gate_proj(x)
        gate_activated = self.activation_fn(gate)
        
        # Apply gate normalization if enabled
        if self.use_gate_norm and self.gate_norm is not None:
            gate_activated = self.gate_norm(gate_activated)
        
        # Get alpha value (could be static, learnable, or computed)
        alpha = self.get_alpha(x)
        
        # Ensure alpha has the right shape for broadcasting
        if alpha.dim() == 0:
            alpha = alpha.view(1, 1)
        
        # Compute partially gated output
        # output = value * (α * gate_activated + (1 - α))
        output = value * (alpha * gate_activated + (1.0 - alpha))
        
        return output
    
    def get_config(self) -> Dict[str, Any]:
        """Get configuration of the module for serialization.
        
        Returns:
            Dict[str, Any]: Configuration dictionary
        """
        config = {
            "input_dim": self.value_proj.in_features,
            "output_dim": self.value_proj.out_features,
            "use_gate_norm": self.use_gate_norm,
        }
        
        # Add alpha configuration
        if hasattr(self, 'alpha_fixed'):
            config["alpha"] = self.alpha_fixed.item()
        elif self.alpha_param is not None:
            config["alpha"] = "learnable"
        else:
            config["alpha"] = "callable"
            
        return config
        
    def clone(self) -> 'paGatingBase':
        """Create a new instance of this module with the same configuration.
        
        This is useful for creating multiple instances of the same activation
        unit in a model architecture.
        
        Returns:
            paGatingBase: A new instance with the same configuration
        """
        # Get the current configuration
        config = self.get_config()
        
        # Create a new instance of the same class
        return self.__class__(
            input_dim=config["input_dim"],
            output_dim=config["output_dim"],
            alpha=config["alpha"],
            use_gate_norm=config["use_gate_norm"],
            # activation_fn is handled by the subclass constructor
        )