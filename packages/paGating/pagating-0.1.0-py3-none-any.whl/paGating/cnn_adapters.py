"""
CNN adapters for paGating units.

This module provides adapter classes to use paGating units in CNN architectures,
handling the conversion between 4D tensors (batch, channels, height, width)
and the 2D tensors (batch, features) that paGating units expect.
"""

import torch
import torch.nn as nn
from typing import Any, Dict, Optional, Union, Type, Callable

from paGating.base import paGatingBase


class paGating2D(nn.Module):
    """
    2D adapter for paGating units in CNN architectures.
    
    This adapter applies a paGating unit to each spatial location of a 
    convolutional feature map, preserving the spatial dimensions.
    
    Args:
        unit_class: The paGating unit class to instantiate
        in_channels: Number of input channels
        out_channels: Number of output channels
        alpha: Alpha value for the paGating unit
        use_gate_norm: Whether to use gate normalization
        norm_eps: Epsilon for gate normalization
        **kwargs: Additional keyword arguments for the paGating unit
    """
    
    def __init__(
        self,
        unit_class: Type[paGatingBase],
        in_channels: int,
        out_channels: int,
        alpha: Union[float, str, Callable, torch.Tensor] = 0.5,
        use_gate_norm: bool = False,
        norm_eps: float = 1e-5,
        **kwargs
    ):
        super().__init__()
        
        # Convert tensor alpha to float if needed
        if isinstance(alpha, torch.Tensor):
            alpha = alpha.item()  # Extract the scalar value
        
        # Create the paGating unit
        self.pa_unit = unit_class(
            input_dim=in_channels,
            output_dim=out_channels,
            alpha=alpha,
            use_gate_norm=use_gate_norm,
            norm_eps=norm_eps,
            **kwargs
        )
        
        self.in_channels = in_channels
        self.out_channels = out_channels
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Apply the paGating unit to a 4D tensor.
        
        Args:
            x: Input tensor of shape (batch, channels, height, width)
            
        Returns:
            Output tensor of shape (batch, out_channels, height, width)
        """
        # Get input dimensions
        batch_size, channels, height, width = x.shape
        
        # Reshape to (batch * height * width, channels)
        x_flat = x.permute(0, 2, 3, 1).reshape(-1, channels)
        
        # Apply paGating unit
        out_flat = self.pa_unit(x_flat)
        
        # Reshape back to (batch, out_channels, height, width)
        out = out_flat.reshape(batch_size, height, width, self.out_channels).permute(0, 3, 1, 2)
        
        return out
    
    def clone(self) -> 'paGating2D':
        """Create a new instance with the same configuration."""
        # Get alpha value - handle tensor case
        alpha = self.pa_unit.get_alpha()
        if isinstance(alpha, torch.Tensor):
            alpha = alpha.item()  # Extract the scalar value
        
        return paGating2D(
            unit_class=self.pa_unit.__class__,
            in_channels=self.in_channels,
            out_channels=self.out_channels,
            alpha=alpha,
            use_gate_norm=self.pa_unit.use_gate_norm,
            norm_eps=getattr(self.pa_unit, 'norm_eps', 1e-5)
        )


# Factory functions for specific paGating units
def create_paGating2D(
    unit_name: str,
    in_channels: int,
    out_channels: int,
    alpha: Union[float, str, Callable] = 0.5,
    use_gate_norm: bool = False,
    norm_eps: float = 1e-5
) -> paGating2D:
    """
    Create a paGating2D adapter for a specific unit.
    
    Args:
        unit_name: Name of the paGating unit ('paGLU', 'paMishU', etc.)
        in_channels: Number of input channels
        out_channels: Number of output channels
        alpha: Alpha value for the paGating unit
        use_gate_norm: Whether to use gate normalization
        norm_eps: Epsilon for gate normalization
        
    Returns:
        paGating2D adapter for the specified unit
    """
    from paGating import activation_map
    
    if unit_name not in activation_map:
        raise ValueError(f"Unknown paGating unit: {unit_name}")
    
    unit_class = activation_map[unit_name]
    
    return paGating2D(
        unit_class=unit_class,
        in_channels=in_channels,
        out_channels=out_channels,
        alpha=alpha,
        use_gate_norm=use_gate_norm,
        norm_eps=norm_eps
    ) 