"""
PyTorch Lightning Module for training CIFAR-10 classifiers with paGating units.

This module handles the training, validation, and testing loops for
the paCIFARClassifier models, along with optimization and logging.
"""

import os
import sys
import torch
import torch.nn as nn
import torch.nn.functional as F
import pytorch_lightning as pl
from typing import Dict, Any, Union, Optional, List, Tuple
import matplotlib.pyplot as plt
import numpy as np
from torchmetrics import Accuracy, F1Score, Precision, Recall

# Add the project root to Python path if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the model
from models.pa_cifar_classifier import create_model, paCIFARClassifier


class paCIFAR10Module(pl.LightningModule):
    """
    PyTorch Lightning module for training CIFAR-10 classifiers with paGating units.
    
    This module handles the training, validation, and testing loops for the 
    paCIFARClassifier models, along with optimization, learning rate scheduling,
    and logging of metrics and activation statistics.
    
    Args:
        unit_name (str): Name of the paGating unit to use (e.g., "paGLU")
        alpha (Union[float, str]): Alpha value or "learnable"
        use_gate_norm (bool): Whether to use gate normalization
        pre_norm (bool): Whether to use layer normalization before the activation
        post_norm (bool): Whether to use layer normalization after the activation
        norm_eps (float): Epsilon value for normalization layers
        learning_rate (float): Initial learning rate
        weight_decay (float): Weight decay for optimizer
        log_activation_stats (bool): Whether to log activation statistics
        scheduler_type (str): Type of learning rate scheduler to use
        scheduler_patience (int): Patience for ReduceLROnPlateau scheduler
        scheduler_factor (float): Factor for ReduceLROnPlateau scheduler
    """
    
    def __init__(
        self,
        unit_name: str = "paGLU",
        alpha: Union[float, str] = 0.5,
        use_gate_norm: bool = False,
        pre_norm: bool = False,
        post_norm: bool = False,
        norm_eps: float = 1e-5,
        learning_rate: float = 0.001,
        weight_decay: float = 1e-4,
        log_activation_stats: bool = False,
        scheduler_type: str = "reduce_on_plateau",
        scheduler_patience: int = 5,
        scheduler_factor: float = 0.5,
    ):
        super().__init__()
        self.save_hyperparameters()
        
        # Create the model
        self.model = create_model(
            unit_name=unit_name,
            alpha=alpha,
            use_gate_norm=use_gate_norm,
            pre_norm=pre_norm,
            post_norm=post_norm,
            norm_eps=norm_eps,
            num_classes=10
        )
        
        # Loss function
        self.criterion = nn.CrossEntropyLoss()
        
        # Metrics
        self.train_acc = Accuracy(task="multiclass", num_classes=10)
        self.val_acc = Accuracy(task="multiclass", num_classes=10)
        self.test_acc = Accuracy(task="multiclass", num_classes=10)
        
        self.val_f1 = F1Score(task="multiclass", num_classes=10)
        self.test_f1 = F1Score(task="multiclass", num_classes=10)
        
        self.val_precision = Precision(task="multiclass", num_classes=10)
        self.test_precision = Precision(task="multiclass", num_classes=10)
        
        self.val_recall = Recall(task="multiclass", num_classes=10)
        self.test_recall = Recall(task="multiclass", num_classes=10)
        
        # Learning rate and scheduler config
        self.learning_rate = learning_rate
        self.weight_decay = weight_decay
        self.scheduler_type = scheduler_type
        self.scheduler_patience = scheduler_patience
        self.scheduler_factor = scheduler_factor
        
        # Activation logging config
        self.log_activation_stats = log_activation_stats
        self.activation_hooks = []
        
        # Register hooks for logging activation stats if enabled
        if log_activation_stats:
            self._register_activation_hooks()
    
    def _register_activation_hooks(self):
        """Register forward hooks to collect activation statistics."""
        self.activation_stats = {}
        
        def hook_fn(name):
            def hook(module, input, output):
                # For visualization, we collect some samples during validation
                if self.training:
                    # During training, just collect statistics
                    self.activation_stats[name] = {
                        "mean": output.mean().item(),
                        "std": output.std().item(),
                        "min": output.min().item(),
                        "max": output.max().item(),
                        "sparsity": (output == 0).float().mean().item()
                    }
                return None
            return hook
        
        # Register hooks for all paActivationBlock modules
        for name, module in self.model.named_modules():
            if "pablock" in name:
                handle = module.register_forward_hook(hook_fn(name))
                self.activation_hooks.append(handle)
    
    def forward(self, x):
        """Forward pass through the model."""
        return self.model(x)
    
    def configure_optimizers(self):
        """Configure the optimizer and learning rate scheduler."""
        optimizer = torch.optim.AdamW(
            self.parameters(),
            lr=self.learning_rate,
            weight_decay=self.weight_decay
        )
        
        if self.scheduler_type == "reduce_on_plateau":
            scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
                optimizer,
                mode="min",
                factor=self.scheduler_factor,
                patience=self.scheduler_patience,
                verbose=True
            )
            return {
                "optimizer": optimizer,
                "lr_scheduler": {
                    "scheduler": scheduler,
                    "monitor": "val_loss",
                    "frequency": 1
                }
            }
        elif self.scheduler_type == "cosine":
            scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
                optimizer,
                T_max=self.trainer.max_epochs
            )
            return {
                "optimizer": optimizer,
                "lr_scheduler": scheduler
            }
        else:
            return optimizer
    
    def training_step(self, batch, batch_idx):
        """Training step."""
        x, y = batch
        logits = self(x)
        loss = self.criterion(logits, y)
        
        # Calculate accuracy
        preds = torch.argmax(logits, dim=1)
        acc = self.train_acc(preds, y)
        
        # Log metrics
        self.log("train_loss", loss, prog_bar=True)
        self.log("train_acc", acc, prog_bar=True)
        
        # Log learning rate
        self.log("lr", self.optimizers().param_groups[0]["lr"], prog_bar=True)
        
        # Log activation statistics if enabled
        if self.log_activation_stats and batch_idx % 50 == 0:
            for name, stats in self.activation_stats.items():
                for stat_name, value in stats.items():
                    self.log(f"train_{name}_{stat_name}", value)
        
        return loss
    
    def validation_step(self, batch, batch_idx):
        """Validation step."""
        x, y = batch
        logits = self(x)
        loss = self.criterion(logits, y)
        
        # Calculate metrics
        preds = torch.argmax(logits, dim=1)
        acc = self.val_acc(preds, y)
        f1 = self.val_f1(preds, y)
        precision = self.val_precision(preds, y)
        recall = self.val_recall(preds, y)
        
        # Log metrics
        self.log("val_loss", loss, prog_bar=True)
        self.log("val_acc", acc, prog_bar=True)
        self.log("val_f1", f1)
        self.log("val_precision", precision)
        self.log("val_recall", recall)
        
        # Log activation statistics if enabled
        if self.log_activation_stats:
            for name, stats in self.activation_stats.items():
                for stat_name, value in stats.items():
                    self.log(f"val_{name}_{stat_name}", value)
        
        return loss
    
    def test_step(self, batch, batch_idx):
        """Test step."""
        x, y = batch
        logits = self(x)
        loss = self.criterion(logits, y)
        
        # Calculate metrics
        preds = torch.argmax(logits, dim=1)
        acc = self.test_acc(preds, y)
        f1 = self.test_f1(preds, y)
        precision = self.test_precision(preds, y)
        recall = self.test_recall(preds, y)
        
        # Log metrics
        self.log("test_loss", loss)
        self.log("test_acc", acc)
        self.log("test_f1", f1)
        self.log("test_precision", precision)
        self.log("test_recall", recall)
        
        return loss
    
    def on_train_epoch_end(self):
        """Log accumulated metrics at the end of the training epoch."""
        self.log("train_acc_epoch", self.train_acc.compute())
        self.train_acc.reset()
    
    def on_validation_epoch_end(self):
        """Log accumulated metrics at the end of the validation epoch."""
        self.log("val_acc_epoch", self.val_acc.compute())
        self.log("val_f1_epoch", self.val_f1.compute())
        self.log("val_precision_epoch", self.val_precision.compute())
        self.log("val_recall_epoch", self.val_recall.compute())
        
        self.val_acc.reset()
        self.val_f1.reset()
        self.val_precision.reset()
        self.val_recall.reset()
    
    def on_test_epoch_end(self):
        """Log accumulated metrics at the end of the test epoch."""
        self.log("test_acc_epoch", self.test_acc.compute())
        self.log("test_f1_epoch", self.test_f1.compute())
        self.log("test_precision_epoch", self.test_precision.compute())
        self.log("test_recall_epoch", self.test_recall.compute())
        
        self.test_acc.reset()
        self.test_f1.reset()
        self.test_precision.reset()
        self.test_recall.reset()


if __name__ == "__main__":
    # Test the Lightning module
    model = paCIFAR10Module(
        unit_name="paGLU",
        alpha=0.5,
        use_gate_norm=True,
        pre_norm=True,
        post_norm=False
    )
    print(model)
    
    # Create a random input
    x = torch.randn(2, 3, 32, 32)
    
    # Forward pass
    output = model(x)
    
    print(f"Input shape: {x.shape}")
    print(f"Output shape: {output.shape}")
    print(f"Model config: {model.model.get_config()}") 