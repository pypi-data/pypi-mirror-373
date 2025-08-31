"""
Activation functions for paGating units.

This module provides implementations of various activation functions used by 
the paGating units, including GELU, Mish, and Swish.
"""

import torch
import torch.nn.functional as F
import math


def gelu(x: torch.Tensor) -> torch.Tensor:
    """Gaussian Error Linear Unit (GELU) activation function.
    
    Implementation follows:
    x * 0.5 * (1 + torch.tanh(math.sqrt(2 / math.pi) * (x + 0.044715 * torch.pow(x, 3))))
    
    Args:
        x (torch.Tensor): Input tensor
        
    Returns:
        torch.Tensor: Output tensor after applying GELU activation
    """
    return F.gelu(x)


def mish(x: torch.Tensor) -> torch.Tensor:
    """Mish activation function.
    
    Computes: x * tanh(softplus(x)) = x * tanh(ln(1 + e^x))
    
    Args:
        x (torch.Tensor): Input tensor
        
    Returns:
        torch.Tensor: Output tensor after applying Mish activation
    """
    return x * torch.tanh(F.softplus(x))


def swish(x: torch.Tensor) -> torch.Tensor:
    """Swish (or SiLU) activation function.
    
    Computes: x * sigmoid(x)
    
    Args:
        x (torch.Tensor): Input tensor
        
    Returns:
        torch.Tensor: Output tensor after applying Swish activation
    """
    return F.silu(x)  # PyTorch provides SiLU which is equivalent to Swish 