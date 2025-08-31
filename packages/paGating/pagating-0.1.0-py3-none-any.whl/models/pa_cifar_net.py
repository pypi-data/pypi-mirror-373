"""
CNN model for CIFAR-10 classification using paGating activation units.

This module defines a convolutional neural network architecture that leverages
paGating activation units for improved performance on the CIFAR-10 dataset.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from paGating import get_pa_unit


class ConvBlock(nn.Module):
    """
    Convolutional block with optional batch normalization and paGating activation.
    
    Args:
        in_channels: Number of input channels
        out_channels: Number of output channels
        kernel_size: Size of convolutional kernel
        stride: Stride of convolution
        padding: Padding size
        use_gate_norm: Whether to use gate normalization
        unit_name: Name of the paGating unit to use
        alpha: Alpha parameter for the paGating unit
    """
    
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: int = 3,
        stride: int = 1,
        padding: int = 1,
        use_gate_norm: bool = False,
        unit_name: str = "paGLU",
        alpha: float = 0.5,
    ):
        super().__init__()
        
        # Main convolutional layer
        self.conv = nn.Conv2d(
            in_channels,
            out_channels,
            kernel_size=kernel_size,
            stride=stride,
            padding=padding,
            bias=False,
        )
        
        # Batch normalization
        self.bn = nn.BatchNorm2d(out_channels)
        
        # paGating activation
        self.pa_unit = get_pa_unit(
            unit_name=unit_name,
            in_features=out_channels,
            alpha=alpha,
            use_gate_norm=use_gate_norm
        )
    
    def forward(self, x):
        x = self.conv(x)
        x = self.bn(x)
        
        # Reshape for paGating (B, C, H, W) -> (B*H*W, C)
        batch, channels, height, width = x.size()
        x_reshaped = x.permute(0, 2, 3, 1).contiguous().view(-1, channels)
        
        # Apply paGating
        x_activated = self.pa_unit(x_reshaped)
        
        # Reshape back to (B, C, H, W)
        x = x_activated.view(batch, height, width, channels).permute(0, 3, 1, 2)
        
        return x


class PACIFARNet(nn.Module):
    """
    CNN model for CIFAR-10 using paGating units.
    
    Args:
        num_classes: Number of output classes
        unit_name: Name of the paGating unit to use
        alpha: Alpha parameter for the paGating unit
        use_gate_norm: Whether to use gate normalization
    """
    
    def __init__(
        self,
        num_classes: int = 10,
        unit_name: str = "paGLU",
        alpha: float = 0.5,
        use_gate_norm: bool = False,
    ):
        super().__init__()
        
        self.unit_name = unit_name
        self.alpha = alpha
        self.use_gate_norm = use_gate_norm
        
        # Feature extraction layers
        self.features = nn.Sequential(
            # First block: 32x32x3 -> 32x32x64
            ConvBlock(
                in_channels=3,
                out_channels=64,
                kernel_size=3,
                stride=1,
                padding=1,
                unit_name=unit_name,
                alpha=alpha,
                use_gate_norm=use_gate_norm,
            ),
            
            # Second block: 32x32x64 -> 16x16x128
            ConvBlock(
                in_channels=64,
                out_channels=128,
                kernel_size=3,
                stride=2,
                padding=1,
                unit_name=unit_name,
                alpha=alpha,
                use_gate_norm=use_gate_norm,
            ),
            ConvBlock(
                in_channels=128,
                out_channels=128,
                kernel_size=3,
                stride=1,
                padding=1,
                unit_name=unit_name,
                alpha=alpha,
                use_gate_norm=use_gate_norm,
            ),
            
            # Third block: 16x16x128 -> 8x8x256
            ConvBlock(
                in_channels=128,
                out_channels=256,
                kernel_size=3,
                stride=2,
                padding=1,
                unit_name=unit_name,
                alpha=alpha,
                use_gate_norm=use_gate_norm,
            ),
            ConvBlock(
                in_channels=256,
                out_channels=256,
                kernel_size=3,
                stride=1,
                padding=1,
                unit_name=unit_name,
                alpha=alpha,
                use_gate_norm=use_gate_norm,
            ),
            
            # Fourth block: 8x8x256 -> 4x4x512
            ConvBlock(
                in_channels=256,
                out_channels=512,
                kernel_size=3,
                stride=2,
                padding=1,
                unit_name=unit_name,
                alpha=alpha,
                use_gate_norm=use_gate_norm,
            ),
            ConvBlock(
                in_channels=512,
                out_channels=512,
                kernel_size=3,
                stride=1,
                padding=1,
                unit_name=unit_name,
                alpha=alpha,
                use_gate_norm=use_gate_norm,
            ),
        )
        
        # Global average pooling
        self.global_avg_pool = nn.AdaptiveAvgPool2d(1)
        
        # Classifier
        self.classifier = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(512, num_classes)
        )
    
    def forward(self, x):
        # Feature extraction
        x = self.features(x)
        
        # Global average pooling
        x = self.global_avg_pool(x)
        x = x.view(x.size(0), -1)
        
        # Classification
        x = self.classifier(x)
        
        return x
    
    def get_config(self):
        """Return model configuration as a dictionary."""
        return {
            "unit_name": self.unit_name,
            "alpha": self.alpha,
            "use_gate_norm": self.use_gate_norm,
        }


if __name__ == "__main__":
    # Test the model
    unit_name = "paMishU"
    alpha = 0.5
    use_gate_norm = False
    
    # Create model
    model = PACIFARNet(
        num_classes=10,
        unit_name=unit_name,
        alpha=alpha,
        use_gate_norm=use_gate_norm,
    )
    
    # Print model summary
    print(f"Model: PACIFARNet with {unit_name} (alpha={alpha})")
    print(f"Use gate norm: {use_gate_norm}")
    
    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    print(f"Total parameters: {total_params:,}")
    print(f"Trainable parameters: {trainable_params:,}")
    
    # Test forward pass
    x = torch.randn(2, 3, 32, 32)
    y = model(x)
    
    print(f"Input shape: {x.shape}")
    print(f"Output shape: {y.shape}") 