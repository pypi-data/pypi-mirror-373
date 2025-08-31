"""
CIFAR-10 Classifier using paGating units.

This module provides a CNN model for CIFAR-10 classification,
replacing standard activations with paGating units and
supporting various normalization configurations.
"""

import os
import sys
import torch
import torch.nn as nn
import torch.nn.functional as F
import pytorch_lightning as pl
from typing import Dict, Any, Union, Optional, Type, List, Tuple

# Add the project root to Python path if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import paGating units
from paGating import (
    paGLU,
    paGTU,
    paSwishU,
    paReGLU,
    paGELU,
    paMishU,
    paSiLU,
    PrePostNormWrapper
)


class paActivationBlock(nn.Module):
    """
    A block that applies paGating activation with optional normalization.
    
    This block takes a paGating unit and applies optional pre/post normalization
    and gate normalization. It handles the dimensional changes needed between
    convolutional features and activation units.
    
    Args:
        in_channels (int): Number of input channels
        out_channels (int): Number of output channels
        pa_unit_class (Type): The paGating unit class to use
        alpha (Union[float, str]): Alpha value or "learnable"
        use_gate_norm (bool): Whether to use gate normalization
        pre_norm (bool): Whether to use layer normalization before the activation
        post_norm (bool): Whether to use layer normalization after the activation
        norm_eps (float): Epsilon value for normalization layers
    """
    
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        pa_unit_class: Type,
        alpha: Union[float, str] = 0.5,
        use_gate_norm: bool = False,
        pre_norm: bool = False,
        post_norm: bool = False,
        norm_eps: float = 1e-5,
    ):
        super().__init__()
        
        self.in_channels = in_channels
        self.out_channels = out_channels
        
        # Create the paGating unit
        self.pa_unit = pa_unit_class(
            input_dim=in_channels,
            output_dim=out_channels,
            alpha=alpha,
            use_gate_norm=use_gate_norm,
            norm_eps=norm_eps
        )
        
        # Wrap with pre/post normalization if needed
        if pre_norm or post_norm:
            self.module = PrePostNormWrapper(
                module=self.pa_unit,
                input_dim=in_channels,
                output_dim=out_channels,
                pre_norm=pre_norm,
                post_norm=post_norm,
                norm_eps=norm_eps
            )
        else:
            self.module = self.pa_unit
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the activation block.
        
        For convolutional feature maps, we reshape to [B, C, H*W] for the paGating unit,
        then reshape back to [B, C, H, W].
        
        Args:
            x (torch.Tensor): Input tensor of shape [B, C, H, W]
            
        Returns:
            torch.Tensor: Output tensor of shape [B, C, H, W]
        """
        batch_size, channels, height, width = x.shape
        
        # Reshape to [B, C, H*W] and transpose to [B, H*W, C]
        x_reshaped = x.reshape(batch_size, channels, -1).transpose(1, 2)
        
        # Apply the paGating unit
        out = self.module(x_reshaped)
        
        # Transpose back to [B, C, H*W] and reshape to [B, C, H, W]
        out = out.transpose(1, 2).reshape(batch_size, self.out_channels, height, width)
        
        return out


class paCIFARClassifier(nn.Module):
    """
    CIFAR-10 classifier using paGating units.
    
    This model is a small CNN that uses paGating units instead of traditional
    activation functions. It supports various normalization configurations.
    
    Args:
        pa_unit_class (Type): The paGating unit class to use
        alpha (Union[float, str]): Alpha value or "learnable"
        use_gate_norm (bool): Whether to use gate normalization
        pre_norm (bool): Whether to use layer normalization before the activation
        post_norm (bool): Whether to use layer normalization after the activation
        norm_eps (float): Epsilon value for normalization layers
        num_classes (int): Number of output classes
    """
    
    def __init__(
        self,
        pa_unit_class: Type,
        alpha: Union[float, str] = 0.5,
        use_gate_norm: bool = False,
        pre_norm: bool = False,
        post_norm: bool = False,
        norm_eps: float = 1e-5,
        num_classes: int = 10,
    ):
        super().__init__()
        
        # Store configuration
        self.config = {
            "pa_unit_class": pa_unit_class.__name__,
            "alpha": alpha,
            "use_gate_norm": use_gate_norm,
            "pre_norm": pre_norm,
            "post_norm": post_norm,
            "norm_eps": norm_eps,
            "num_classes": num_classes,
        }
        
        # First convolutional layer
        self.conv1 = nn.Conv2d(3, 64, kernel_size=3, padding=1)
        self.pablock1 = paActivationBlock(
            in_channels=64,
            out_channels=64,
            pa_unit_class=pa_unit_class,
            alpha=alpha,
            use_gate_norm=use_gate_norm,
            pre_norm=pre_norm,
            post_norm=post_norm,
            norm_eps=norm_eps
        )
        self.pool1 = nn.MaxPool2d(2)
        
        # Second convolutional layer
        self.conv2 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.pablock2 = paActivationBlock(
            in_channels=128,
            out_channels=128,
            pa_unit_class=pa_unit_class,
            alpha=alpha,
            use_gate_norm=use_gate_norm,
            pre_norm=pre_norm,
            post_norm=post_norm,
            norm_eps=norm_eps
        )
        self.pool2 = nn.MaxPool2d(2)
        
        # Third convolutional layer
        self.conv3 = nn.Conv2d(128, 256, kernel_size=3, padding=1)
        self.pablock3 = paActivationBlock(
            in_channels=256,
            out_channels=256,
            pa_unit_class=pa_unit_class,
            alpha=alpha,
            use_gate_norm=use_gate_norm,
            pre_norm=pre_norm,
            post_norm=post_norm,
            norm_eps=norm_eps
        )
        self.pool3 = nn.MaxPool2d(2)
        
        # Fourth convolutional layer
        self.conv4 = nn.Conv2d(256, 512, kernel_size=3, padding=1)
        self.pablock4 = paActivationBlock(
            in_channels=512,
            out_channels=512,
            pa_unit_class=pa_unit_class,
            alpha=alpha,
            use_gate_norm=use_gate_norm,
            pre_norm=pre_norm,
            post_norm=post_norm,
            norm_eps=norm_eps
        )
        self.pool4 = nn.MaxPool2d(2)
        
        # Global pooling and fully connected layer
        self.global_pool = nn.AdaptiveAvgPool2d(1)
        self.fc = nn.Linear(512, num_classes)
        
        # Dropout for regularization
        self.dropout = nn.Dropout(0.5)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the network.
        
        Args:
            x (torch.Tensor): Input images of shape [B, 3, H, W]
            
        Returns:
            torch.Tensor: Logits of shape [B, num_classes]
        """
        # First block
        x = self.conv1(x)
        x = self.pablock1(x)
        x = self.pool1(x)
        
        # Second block
        x = self.conv2(x)
        x = self.pablock2(x)
        x = self.pool2(x)
        
        # Third block
        x = self.conv3(x)
        x = self.pablock3(x)
        x = self.pool3(x)
        
        # Fourth block
        x = self.conv4(x)
        x = self.pablock4(x)
        x = self.pool4(x)
        
        # Global pooling
        x = self.global_pool(x)
        x = x.view(x.size(0), -1)
        x = self.dropout(x)
        
        # Fully connected layer
        x = self.fc(x)
        
        return x
    
    def get_config(self) -> Dict[str, Any]:
        """Return the model configuration."""
        return self.config


def create_model(
    unit_name: str,
    alpha: Union[float, str] = 0.5,
    use_gate_norm: bool = False,
    pre_norm: bool = False,
    post_norm: bool = False,
    norm_eps: float = 1e-5,
    num_classes: int = 10,
) -> paCIFARClassifier:
    """
    Create a paCIFARClassifier with the specified configuration.
    
    Args:
        unit_name (str): Name of the paGating unit to use (e.g., "paGLU")
        alpha (Union[float, str]): Alpha value or "learnable"
        use_gate_norm (bool): Whether to use gate normalization
        pre_norm (bool): Whether to use layer normalization before the activation
        post_norm (bool): Whether to use layer normalization after the activation
        norm_eps (float): Epsilon value for normalization layers
        num_classes (int): Number of output classes
        
    Returns:
        paCIFARClassifier: Configured model
    """
    # Map unit names to classes
    unit_mapping = {
        "paGLU": paGLU,
        "paGTU": paGTU,
        "paSwishU": paSwishU,
        "paReGLU": paReGLU,
        "paGELU": paGELU,
        "paMishU": paMishU,
        "paSiLU": paSiLU
    }
    
    # Get the unit class
    unit_class = unit_mapping.get(unit_name)
    if unit_class is None:
        raise ValueError(f"Unknown paGating unit: {unit_name}")
    
    # Create the model
    model = paCIFARClassifier(
        pa_unit_class=unit_class,
        alpha=alpha,
        use_gate_norm=use_gate_norm,
        pre_norm=pre_norm,
        post_norm=post_norm,
        norm_eps=norm_eps,
        num_classes=num_classes
    )
    
    return model


if __name__ == "__main__":
    # Test the model
    model = create_model("paGLU", alpha=0.5, use_gate_norm=True, pre_norm=True, post_norm=True)
    print(model)
    
    # Create a random input
    x = torch.randn(2, 3, 32, 32)
    
    # Forward pass
    output = model(x)
    
    print(f"Input shape: {x.shape}")
    print(f"Output shape: {output.shape}")
    print(f"Model config: {model.get_config()}")
    
    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    print(f"Total parameters: {total_params:,}") 