"""
CNN model for CIFAR-10 classification using paGating units.

This model implements a convolutional neural network for CIFAR-10 image classification
with paGating activation units integrated in the architecture.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Any, Tuple, Optional, Type

from paGating import get_unit


class ConvBlock(nn.Module):
    """
    Convolutional block with paGating activation.
    
    Args:
        in_channels: Number of input channels
        out_channels: Number of output channels
        kernel_size: Size of the convolutional kernel
        stride: Stride of the convolution
        padding: Padding for the convolution
        unit_name: Name of the paGating unit to use
        alpha: Alpha parameter for the paGating unit
        use_gate_norm: Whether to use gate normalization
    """
    
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: int = 3,
        stride: int = 1,
        padding: int = 1,
        unit_name: str = "paGLU",
        alpha: float = 0.5,
        use_gate_norm: bool = False,
    ):
        super().__init__()
        
        # Get the paGating unit
        self.pa_unit = get_unit(unit_name)(
            dim=out_channels, 
            alpha=alpha, 
            use_gate_norm=use_gate_norm
        )
        
        # Create the convolutional layer
        self.conv = nn.Conv2d(
            in_channels, 
            out_channels * 2,  # Double the channels for the gating mechanism
            kernel_size=kernel_size,
            stride=stride,
            padding=padding,
            bias=True
        )
        
        # Batch normalization
        self.bn = nn.BatchNorm2d(out_channels * 2)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through the block."""
        x = self.conv(x)
        x = self.bn(x)
        x = self.pa_unit(x)
        return x


class paCIFAR10Model(nn.Module):
    """
    CNN model for CIFAR-10 classification using paGating units.
    
    Args:
        unit_name: Name of the paGating unit to use
        alpha: Alpha parameter for the paGating unit
        use_gate_norm: Whether to use gate normalization
        num_classes: Number of output classes (10 for CIFAR-10)
        in_channels: Number of input channels (3 for RGB images)
    """
    
    def __init__(
        self,
        unit_name: str = "paGLU",
        alpha: float = 0.5,
        use_gate_norm: bool = False,
        num_classes: int = 10,
        in_channels: int = 3,
    ):
        super().__init__()
        
        self.unit_name = unit_name
        self.alpha = alpha
        self.use_gate_norm = use_gate_norm
        
        # First block: 3 -> 64
        self.block1 = ConvBlock(
            in_channels=in_channels,
            out_channels=64,
            unit_name=unit_name,
            alpha=alpha,
            use_gate_norm=use_gate_norm
        )
        
        # Second block: 64 -> 128
        self.block2 = ConvBlock(
            in_channels=64,
            out_channels=128,
            unit_name=unit_name,
            alpha=alpha,
            use_gate_norm=use_gate_norm
        )
        
        # Max pooling after block 2
        self.pool1 = nn.MaxPool2d(kernel_size=2, stride=2)
        
        # Third block: 128 -> 256
        self.block3 = ConvBlock(
            in_channels=128,
            out_channels=256,
            unit_name=unit_name,
            alpha=alpha,
            use_gate_norm=use_gate_norm
        )
        
        # Fourth block: 256 -> 256
        self.block4 = ConvBlock(
            in_channels=256,
            out_channels=256,
            unit_name=unit_name,
            alpha=alpha,
            use_gate_norm=use_gate_norm
        )
        
        # Max pooling after block 4
        self.pool2 = nn.MaxPool2d(kernel_size=2, stride=2)
        
        # Fifth block: 256 -> 512
        self.block5 = ConvBlock(
            in_channels=256,
            out_channels=512,
            unit_name=unit_name,
            alpha=alpha,
            use_gate_norm=use_gate_norm
        )
        
        # Sixth block: 512 -> 512
        self.block6 = ConvBlock(
            in_channels=512,
            out_channels=512,
            unit_name=unit_name,
            alpha=alpha,
            use_gate_norm=use_gate_norm
        )
        
        # Max pooling after block 6
        self.pool3 = nn.MaxPool2d(kernel_size=2, stride=2)
        
        # Classifier head
        self.avg_pool = nn.AdaptiveAvgPool2d((1, 1))
        self.flatten = nn.Flatten()
        self.fc = nn.Linear(512, num_classes)
        
        # Initialize weights
        self._initialize_weights()
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through the model."""
        # Block 1
        x = self.block1(x)
        
        # Block 2 + pooling
        x = self.block2(x)
        x = self.pool1(x)
        
        # Block 3
        x = self.block3(x)
        
        # Block 4 + pooling
        x = self.block4(x)
        x = self.pool2(x)
        
        # Block 5
        x = self.block5(x)
        
        # Block 6 + pooling
        x = self.block6(x)
        x = self.pool3(x)
        
        # Classifier head
        x = self.avg_pool(x)
        x = self.flatten(x)
        x = self.fc(x)
        
        return x
    
    def _initialize_weights(self):
        """Initialize model weights."""
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, 0, 0.01)
                nn.init.constant_(m.bias, 0)
    
    def get_config(self) -> Dict[str, Any]:
        """Get model configuration."""
        return {
            "unit_name": self.unit_name,
            "alpha": self.alpha,
            "use_gate_norm": self.use_gate_norm,
            "num_classes": self.fc.out_features,
            "in_channels": self.block1.conv.in_channels
        }


if __name__ == "__main__":
    # Test the model
    model = paCIFAR10Model(unit_name="paMishU", alpha=0.5)
    input_tensor = torch.randn(2, 3, 32, 32)
    output = model(input_tensor)
    
    print(f"Input shape: {input_tensor.shape}")
    print(f"Output shape: {output.shape}")
    print(f"Model config: {model.get_config()}")
    
    # Calculate number of parameters
    total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Total trainable parameters: {total_params:,}") 