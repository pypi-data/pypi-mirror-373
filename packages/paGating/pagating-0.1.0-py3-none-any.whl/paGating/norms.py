"""
Normalization components for paGating units.

This module provides normalization wrappers and specialized normalization
techniques for paGating activation units.
"""

import torch
import torch.nn as nn
from typing import Optional, Tuple, Union, Callable


class GateNorm(nn.Module):
    """Layer normalization applied specifically to the gating pathway of paGating units.
    
    Unlike standard LayerNorm, GateNorm is applied only to the gating signal 
    before combining with the value path, normalizing the gate activations
    to ensure consistent signal strength regardless of input distribution.
    
    Args:
        normalized_shape (int): The expected shape of the gate activations
        eps (float): Small constant added for numerical stability
        elementwise_affine (bool): If True, use learnable affine parameters
    """
    
    def __init__(
        self,
        normalized_shape: int,
        eps: float = 1e-5,
        elementwise_affine: bool = True
    ) -> None:
        super().__init__()
        self.normalized_shape = normalized_shape
        self.eps = eps
        self.elementwise_affine = elementwise_affine
        
        if elementwise_affine:
            self.weight = nn.Parameter(torch.ones(normalized_shape))
            self.bias = nn.Parameter(torch.zeros(normalized_shape))
        else:
            self.register_parameter('weight', None)
            self.register_parameter('bias', None)
    
    def forward(self, gate_signal: torch.Tensor) -> torch.Tensor:
        """Normalize the gate signal.
        
        Args:
            gate_signal (torch.Tensor): The gate activation tensor [batch_size, features]
            
        Returns:
            torch.Tensor: Normalized gate signal
        """
        # Compute mean and variance along feature dimension
        mean = gate_signal.mean(dim=-1, keepdim=True)
        var = gate_signal.var(dim=-1, keepdim=True, unbiased=False)
        
        # Normalize
        normalized = (gate_signal - mean) / torch.sqrt(var + self.eps)
        
        # Apply affine transformation if enabled
        if self.elementwise_affine:
            normalized = normalized * self.weight + self.bias
            
        return normalized


class PrePostNormWrapper(nn.Module):
    """Wrapper that optionally applies LayerNorm before and/or after a paGating unit.
    
    This wrapper implements a flexible normalization scheme that can:
    1. Apply LayerNorm before the paGating unit (pre-norm)
    2. Apply LayerNorm after the paGating unit (post-norm)
    3. Do both pre and post normalization
    4. Skip normalization entirely
    
    Args:
        module (nn.Module): The paGating unit to wrap
        input_dim (int): Input dimension
        output_dim (int): Output dimension
        pre_norm (bool): Whether to apply normalization before the wrapped module
        post_norm (bool): Whether to apply normalization after the wrapped module
        norm_eps (float): Epsilon for numerical stability in normalization
    """
    
    def __init__(
        self,
        module: nn.Module,
        input_dim: int,
        output_dim: int,
        pre_norm: bool = False,
        post_norm: bool = False,
        norm_eps: float = 1e-5
    ) -> None:
        super().__init__()
        self.module = module
        self.pre_norm = pre_norm
        self.post_norm = post_norm
        
        # Create normalization layers if enabled
        self.pre_norm_layer = nn.LayerNorm(input_dim, eps=norm_eps) if pre_norm else None
        self.post_norm_layer = nn.LayerNorm(output_dim, eps=norm_eps) if post_norm else None
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass with optional pre/post normalization.
        
        Args:
            x (torch.Tensor): Input tensor
            
        Returns:
            torch.Tensor: Output tensor after applying normalization and the wrapped module
        """
        # Apply pre-normalization if enabled
        if self.pre_norm and self.pre_norm_layer is not None:
            x = self.pre_norm_layer(x)
        
        # Apply the wrapped module
        output = self.module(x)
        
        # Apply post-normalization if enabled
        if self.post_norm and self.post_norm_layer is not None:
            output = self.post_norm_layer(output)
        
        return output
    
    # Expose the wrapped module's attributes
    def __getattr__(self, name):
        """Forward attribute access to the wrapped module."""
        try:
            return super().__getattr__(name)
        except AttributeError:
            return getattr(self.module, name) 