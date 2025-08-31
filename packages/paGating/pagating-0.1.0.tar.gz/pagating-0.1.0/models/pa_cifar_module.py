"""
PyTorch Lightning module for CIFAR-10 classification with paGating units.

This module defines a CNN architecture for CIFAR-10 classification that uses
paGating activation units.
"""

import os
from typing import List, Dict, Any, Optional, Union, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchmetrics
import pytorch_lightning as pl
from pytorch_lightning.callbacks import (
    ModelCheckpoint,
    EarlyStopping,
    LearningRateMonitor,
)

from paGating.cnn_adapters import paGating2D


class SimpleCIFARCNN(nn.Module):
    """
    A simple CNN architecture for CIFAR-10 classification that uses
    paGating activation units.
    """
    
    def __init__(self, activation_unit, num_classes: int = 10):
        """
        Initialize the CNN model.
        
        Args:
            activation_unit: paGating unit to use for activation
            num_classes: Number of output classes (default: 10 for CIFAR-10)
        """
        super().__init__()
        
        # Check if the activation unit is already a paGating2D
        if not isinstance(activation_unit, paGating2D):
            # If it's a regular paGating unit, we need to use its class to create paGating2D adapters
            unit_class = activation_unit.__class__
            # Store the alpha configuration
            if hasattr(activation_unit, 'alpha_fixed'):
                alpha = activation_unit.alpha_fixed.item()
            elif hasattr(activation_unit, 'alpha_param'):
                alpha = "learnable"
            else:
                alpha = 0.5  # Default alpha
            
            # Create 2D adapters for different layers
            self.pa1 = paGating2D(unit_class, 32, 32, alpha)
            self.pa2 = paGating2D(unit_class, 64, 64, alpha)
            self.pa3 = paGating2D(unit_class, 128, 128, alpha)
            
            # For the fully connected layer, we can use the original unit
            if hasattr(activation_unit, 'clone'):
                self.pa4 = activation_unit.clone()
            else:
                # If clone isn't available, create a new instance
                self.pa4 = unit_class(input_dim=256, output_dim=256, alpha=alpha)
        else:
            # If it's already a paGating2D, we can clone it and adjust the channels
            # Get alpha value, handling tensor case
            if hasattr(activation_unit.pa_unit, 'alpha_fixed'):
                alpha = activation_unit.pa_unit.alpha_fixed.item()
            elif hasattr(activation_unit.pa_unit, 'alpha_param'):
                alpha = "learnable"
            else:
                alpha = 0.5
            
            self.pa1 = paGating2D(
                activation_unit.pa_unit.__class__,
                32, 32, 
                alpha,
                activation_unit.pa_unit.use_gate_norm
            )
            self.pa2 = paGating2D(
                activation_unit.pa_unit.__class__,
                64, 64, 
                alpha,
                activation_unit.pa_unit.use_gate_norm
            )
            self.pa3 = paGating2D(
                activation_unit.pa_unit.__class__,
                128, 128, 
                alpha,
                activation_unit.pa_unit.use_gate_norm
            )
            self.pa4 = activation_unit.pa_unit.__class__(
                input_dim=256, 
                output_dim=256, 
                alpha=alpha,
                use_gate_norm=activation_unit.pa_unit.use_gate_norm
            )
        
        # Convolutional layers
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
        self.pool1 = nn.MaxPool2d(kernel_size=2, stride=2)
        
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.pool2 = nn.MaxPool2d(kernel_size=2, stride=2)
        
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.pool3 = nn.MaxPool2d(kernel_size=2, stride=2)
        
        # Calculate size after convolutions and pooling
        # CIFAR-10 is 32x32x3
        # After 3 pooling layers with stride 2: 32 / (2^3) = 4
        feature_size = 128 * 4 * 4
        
        # Fully connected layers
        self.fc1 = nn.Linear(feature_size, 256)
        self.dropout = nn.Dropout(0.5)
        self.fc2 = nn.Linear(256, num_classes)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass of the CNN.
        
        Args:
            x: Input tensor of shape (B, C, H, W)
            
        Returns:
            Logits of shape (B, num_classes)
        """
        # First convolutional block
        x = self.conv1(x)
        x = self.pa1(x)
        x = self.pool1(x)
        
        # Second convolutional block
        x = self.conv2(x)
        x = self.pa2(x)
        x = self.pool2(x)
        
        # Third convolutional block
        x = self.conv3(x)
        x = self.pa3(x)
        x = self.pool3(x)
        
        # Flatten and fully connected layers
        x = x.reshape(x.size(0), -1)
        x = self.fc1(x)
        x = self.pa4(x)
        x = self.dropout(x)
        x = self.fc2(x)
        
        return x


class PACIFARLightningModule(pl.LightningModule):
    """
    PyTorch Lightning module for training a CNN model on CIFAR-10
    with paGating activation units.
    """
    
    def __init__(
        self,
        activation_unit,
        learning_rate: float = 1e-3,
        weight_decay: float = 1e-4,
    ):
        """
        Initialize the Lightning module.
        
        Args:
            activation_unit: paGating unit to use for activation
            learning_rate: Learning rate for optimizer
            weight_decay: Weight decay for regularization
        """
        super().__init__()
        self.save_hyperparameters(ignore=['activation_unit'])
        
        # Model
        self.model = SimpleCIFARCNN(activation_unit=activation_unit)
        
        # Store activation unit info for logging
        self.activation_name = activation_unit.__class__.__name__
        
        # Get alpha value from the activation unit
        if hasattr(activation_unit, 'alpha_fixed'):
            self.activation_alpha = activation_unit.alpha_fixed.item()
        elif hasattr(activation_unit, 'alpha_param'):
            self.activation_alpha = "learnable"
        else:
            self.activation_alpha = "dynamic"
        
        # Loss function
        self.criterion = nn.CrossEntropyLoss()
        
        # Metrics
        self.train_acc = torchmetrics.Accuracy(task="multiclass", num_classes=10)
        self.val_acc = torchmetrics.Accuracy(task="multiclass", num_classes=10)
        self.test_acc = torchmetrics.Accuracy(task="multiclass", num_classes=10)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass of the model.
        
        Args:
            x: Input tensor
            
        Returns:
            Model output
        """
        return self.model(x)
    
    def _common_step(
        self, batch: Tuple[torch.Tensor, torch.Tensor], batch_idx: int
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Common step for training, validation, and testing.
        
        Args:
            batch: Tuple of (inputs, targets)
            batch_idx: Batch index
            
        Returns:
            Tuple of (loss, logits, targets)
        """
        inputs, targets = batch
        logits = self(inputs)
        loss = self.criterion(logits, targets)
        return loss, logits, targets
    
    def training_step(
        self, batch: Tuple[torch.Tensor, torch.Tensor], batch_idx: int
    ) -> Dict[str, torch.Tensor]:
        """
        Training step.
        
        Args:
            batch: Tuple of (inputs, targets)
            batch_idx: Batch index
            
        Returns:
            Dictionary with loss and metrics
        """
        loss, logits, targets = self._common_step(batch, batch_idx)
        preds = torch.argmax(logits, dim=1)
        acc = self.train_acc(preds, targets)
        
        self.log("train_loss", loss, prog_bar=True)
        self.log("train_acc", acc, prog_bar=True)
        
        return {"loss": loss, "acc": acc}
    
    def validation_step(
        self, batch: Tuple[torch.Tensor, torch.Tensor], batch_idx: int
    ) -> Dict[str, torch.Tensor]:
        """
        Validation step.
        
        Args:
            batch: Tuple of (inputs, targets)
            batch_idx: Batch index
            
        Returns:
            Dictionary with loss and metrics
        """
        loss, logits, targets = self._common_step(batch, batch_idx)
        preds = torch.argmax(logits, dim=1)
        acc = self.val_acc(preds, targets)
        
        self.log("val_loss", loss, prog_bar=True)
        self.log("val_acc", acc, prog_bar=True)
        
        return {"val_loss": loss, "val_acc": acc}
    
    def test_step(
        self, batch: Tuple[torch.Tensor, torch.Tensor], batch_idx: int
    ) -> Dict[str, torch.Tensor]:
        """
        Test step.
        
        Args:
            batch: Tuple of (inputs, targets)
            batch_idx: Batch index
            
        Returns:
            Dictionary with loss and metrics
        """
        loss, logits, targets = self._common_step(batch, batch_idx)
        preds = torch.argmax(logits, dim=1)
        acc = self.test_acc(preds, targets)
        
        self.log("test_loss", loss)
        self.log("test_acc", acc)
        
        return {"test_loss": loss, "test_acc": acc}
    
    def configure_optimizers(self) -> Dict[str, Any]:
        """
        Configure optimizers and learning rate schedulers.
        
        Returns:
            Dictionary with optimizer and scheduler configuration
        """
        optimizer = torch.optim.Adam(
            self.parameters(),
            lr=self.hparams.learning_rate,
            weight_decay=self.hparams.weight_decay,
        )
        
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer,
            mode="min",
            factor=0.1,
            patience=5,
            verbose=True,
        )
        
        return {
            "optimizer": optimizer,
            "lr_scheduler": {
                "scheduler": scheduler,
                "monitor": "val_loss",
                "interval": "epoch",
                "frequency": 1,
            },
        }
    
    @staticmethod
    def default_callbacks(
        monitor: str = "val_loss",
        mode: str = "min",
        patience: int = 10,
        save_dir: str = "./outputs",
    ) -> List[pl.Callback]:
        """
        Get default callbacks for training.
        
        Args:
            monitor: Metric to monitor
            mode: Mode for monitoring ('min' or 'max')
            patience: Patience for early stopping
            save_dir: Directory to save checkpoints
            
        Returns:
            List of callbacks
        """
        checkpoint_callback = ModelCheckpoint(
            dirpath=os.path.join(save_dir, "checkpoints"),
            filename="best-{epoch:02d}-{" + monitor + ":.4f}",
            monitor=monitor,
            mode=mode,
            save_top_k=1,
            save_last=True,
        )
        
        early_stopping = EarlyStopping(
            monitor=monitor,
            mode=mode,
            patience=patience,
            verbose=True,
        )
        
        lr_monitor = LearningRateMonitor(logging_interval="epoch")
        
        return [checkpoint_callback, early_stopping, lr_monitor]
    
    def on_save_checkpoint(self, checkpoint: Dict[str, Any]) -> None:
        """
        Save additional information to checkpoint.
        
        Args:
            checkpoint: Checkpoint dictionary
        """
        checkpoint["activation_name"] = self.activation_name
        checkpoint["activation_alpha"] = self.activation_alpha


# For testing the model architecture
if __name__ == "__main__":
    model = SimpleCIFARCNN(activation_unit=paGating.paMishU(alpha=0.5))
    
    # Print model summary
    x = torch.randn(1, 3, 32, 32)
    print(model)
    
    # Test forward pass
    y = model(x)
    print(f"Output shape: {y.shape}") 