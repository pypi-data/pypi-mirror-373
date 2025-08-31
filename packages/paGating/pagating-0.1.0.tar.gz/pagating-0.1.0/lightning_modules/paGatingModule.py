"""
PyTorch Lightning Module for paGating Units

This module provides a PyTorch Lightning wrapper for paGating units,
enabling easy training, validation, and testing with all Lightning features.
"""

import os
import sys
import torch
import torch.nn as nn
import torch.nn.functional as F
import pytorch_lightning as pl
from typing import Dict, Any, Union, Optional

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import paGating units
from paGating import (
    paGLU,
    paGTU,
    paSwishU,
    paReGLU,
    paGELU,
    paMishU,
    paSiLU
)


class NormStatisticsHook:
    """Hook to collect statistics about normalization layers.
    
    This class is used to log statistics about the inputs and outputs of
    normalization layers to TensorBoard during training and validation.
    """
    
    def __init__(self):
        self.pre_norm_inputs = []
        self.post_norm_outputs = []
        self.gate_activated_values = []
        
    def clear(self):
        """Clear collected statistics."""
        self.pre_norm_inputs = []
        self.post_norm_outputs = []
        self.gate_activated_values = []
    
    def pre_norm_hook(self, module, input, output):
        """Hook for pre-normalization layer."""
        # Store input tensor statistics
        if isinstance(input, tuple):
            input = input[0]
        self.pre_norm_inputs.append(input.detach())
    
    def post_norm_hook(self, module, input, output):
        """Hook for post-normalization layer."""
        # Store output tensor statistics
        self.post_norm_outputs.append(output.detach())
    
    def gate_activation_hook(self, module, input, output):
        """Hook for the gate activation function."""
        # Store the activated gate values
        self.gate_activated_values.append(output.detach())
    
    def calculate_statistics(self):
        """Calculate statistics from collected tensors."""
        stats = {}
        
        if self.pre_norm_inputs:
            inputs = torch.cat(self.pre_norm_inputs, dim=0)
            stats["pre_norm_mean"] = inputs.mean().item()
            stats["pre_norm_std"] = inputs.std().item()
            stats["pre_norm_min"] = inputs.min().item()
            stats["pre_norm_max"] = inputs.max().item()
        
        if self.post_norm_outputs:
            outputs = torch.cat(self.post_norm_outputs, dim=0)
            stats["post_norm_mean"] = outputs.mean().item()
            stats["post_norm_std"] = outputs.std().item()
            stats["post_norm_min"] = outputs.min().item()
            stats["post_norm_max"] = outputs.max().item()
        
        if self.gate_activated_values:
            gates = torch.cat(self.gate_activated_values, dim=0)
            stats["gate_activated_mean"] = gates.mean().item()
            stats["gate_activated_std"] = gates.std().item()
            stats["gate_activated_min"] = gates.min().item()
            stats["gate_activated_max"] = gates.max().item()
        
        return stats


class paGatingModule(pl.LightningModule):
    """PyTorch Lightning module for paGating units.
    
    This module wraps any paGating unit in a LightningModule,
    providing standard interfaces for training, validation, and testing.
    
    Args:
        config (Dict[str, Any]): Configuration dictionary with the following keys:
            - unit (str): Name of the paGating unit to use
            - input_dim (int): Input dimension
            - output_dim (int): Output dimension
            - alpha (Union[float, str]): Alpha value or "learnable"
            - optimizer (str): Name of the optimizer to use
            - lr (float): Learning rate
            - weight_decay (float, optional): Weight decay for optimizer
            - use_gate_norm (bool, optional): Whether to use GateNorm
            - pre_norm (bool, optional): Whether to use LayerNorm before the unit
            - post_norm (bool, optional): Whether to use LayerNorm after the unit
            - norm_eps (float, optional): Epsilon for normalization layers
            - log_norm_stats (bool, optional): Whether to log normalization statistics
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.save_hyperparameters(config)
        self.config = config
        
        # Initialize model
        unit_name = config["unit"]
        input_dim = config["input_dim"]
        output_dim = config["output_dim"]
        alpha = config["alpha"]
        
        # Get normalization options
        use_gate_norm = config.get("use_gate_norm", False)
        pre_norm = config.get("pre_norm", False)
        post_norm = config.get("post_norm", False)
        norm_eps = config.get("norm_eps", 1e-5)
        self.log_norm_stats = config.get("log_norm_stats", False)
        
        # Get the paGating unit class
        unit_mapping = {
            "paGLU": paGLU,
            "paGTU": paGTU,
            "paSwishU": paSwishU,
            "paReGLU": paReGLU,
            "paGELU": paGELU,
            "paMishU": paMishU,
            "paSiLU": paSiLU
        }
        
        # Create the model
        unit_class = unit_mapping.get(unit_name)
        if unit_class is None:
            raise ValueError(f"Unknown unit: {unit_name}")
        
        # Create base unit
        self.base_unit = unit_class(
            input_dim=input_dim,
            output_dim=output_dim,
            alpha=alpha,
            use_gate_norm=use_gate_norm,
            norm_eps=norm_eps
        )
        
        # Wrap with pre/post normalization if requested
        if pre_norm or post_norm:
            from paGating import PrePostNormWrapper
            self.model = PrePostNormWrapper(
                module=self.base_unit,
                input_dim=input_dim,
                output_dim=output_dim,
                pre_norm=pre_norm,
                post_norm=post_norm,
                norm_eps=norm_eps
            )
        else:
            self.model = self.base_unit
        
        # Initialize statistics hook
        self.norm_stats_hook = NormStatisticsHook()
        
        # Register hooks if logging is enabled
        if self.log_norm_stats:
            self._register_hooks()
        
        # Add loss function
        self.loss_fn = nn.MSELoss()
        
        # Tracking metrics
        self.train_loss = None
        self.val_loss = None
        
        # Log alpha parameter if learnable
        self.is_alpha_learnable = alpha == "learnable"
    
    def _register_hooks(self):
        """Register hooks to collect statistics about normalization layers."""
        # Find and register hooks for pre/post norm layers
        if hasattr(self.model, "pre_norm_layer") and self.model.pre_norm_layer is not None:
            self.model.pre_norm_layer.register_forward_hook(self.norm_stats_hook.pre_norm_hook)
        
        if hasattr(self.model, "post_norm_layer") and self.model.post_norm_layer is not None:
            self.model.post_norm_layer.register_forward_hook(self.norm_stats_hook.post_norm_hook)
        
        # Register hook for gate activation
        if hasattr(self.base_unit, "activation_fn"):
            # We can't directly hook the function, so we'll hook the forward method
            # This is a bit of a hack, but it works for our purpose
            self.base_unit.register_forward_hook(
                lambda module, input, output: self.norm_stats_hook.gate_activation_hook(
                    module, 
                    input, 
                    module.activation_fn(module.gate_proj(input[0]))
                )
            )
        
    def forward(self, x):
        """Forward pass through the model.
        
        Args:
            x (torch.Tensor): Input tensor of shape (batch_size, input_dim)
            
        Returns:
            torch.Tensor: Output tensor of shape (batch_size, output_dim)
        """
        return self.model(x)
    
    def on_train_epoch_start(self):
        """Clear statistics at the start of each training epoch."""
        if self.log_norm_stats:
            self.norm_stats_hook.clear()
    
    def on_validation_epoch_start(self):
        """Clear statistics at the start of each validation epoch."""
        if self.log_norm_stats:
            self.norm_stats_hook.clear()
    
    def on_train_epoch_end(self):
        """Log statistics at the end of each training epoch."""
        if self.log_norm_stats:
            stats = self.norm_stats_hook.calculate_statistics()
            for name, value in stats.items():
                self.log(f"train_{name}", value, on_step=False, on_epoch=True)
    
    def on_validation_epoch_end(self):
        """Log statistics at the end of each validation epoch."""
        if self.log_norm_stats:
            stats = self.norm_stats_hook.calculate_statistics()
            for name, value in stats.items():
                self.log(f"val_{name}", value, on_step=False, on_epoch=True)
    
    def training_step(self, batch, batch_idx):
        """Training step.
        
        Args:
            batch (tuple): Tuple of (input, target)
            batch_idx (int): Batch index
            
        Returns:
            torch.Tensor: Loss value
        """
        x, y = batch
        y_hat = self(x)
        loss = self.loss_fn(y_hat, y)
        
        # Log metrics
        self.log("train_loss", loss, on_step=True, on_epoch=True, prog_bar=True)
        
        # Log alpha if learnable
        if self.is_alpha_learnable:
            alpha = self.model.get_alpha()
            self.log("train_alpha", alpha.item(), on_step=False, on_epoch=True)
        
        return loss
    
    def validation_step(self, batch, batch_idx):
        """Validation step.
        
        Args:
            batch (tuple): Tuple of (input, target)
            batch_idx (int): Batch index
            
        Returns:
            torch.Tensor: Loss value
        """
        x, y = batch
        y_hat = self(x)
        loss = self.loss_fn(y_hat, y)
        
        # Log metrics
        self.log("val_loss", loss, on_step=False, on_epoch=True, prog_bar=True)
        
        # Log alpha if learnable
        if self.is_alpha_learnable:
            alpha = self.model.get_alpha()
            self.log("val_alpha", alpha.item(), on_step=False, on_epoch=True)
        
        return loss
    
    def test_step(self, batch, batch_idx):
        """Test step.
        
        Args:
            batch (tuple): Tuple of (input, target)
            batch_idx (int): Batch index
            
        Returns:
            torch.Tensor: Loss value
        """
        x, y = batch
        y_hat = self(x)
        loss = self.loss_fn(y_hat, y)
        
        # Log metrics
        self.log("test_loss", loss, on_step=False, on_epoch=True)
        
        return loss
    
    def configure_optimizers(self):
        """Configure optimizers.
        
        Returns:
            torch.optim.Optimizer: Configured optimizer
        """
        optimizer_name = self.config.get("optimizer", "adam").lower()
        lr = self.config.get("lr", 1e-3)
        weight_decay = self.config.get("weight_decay", 0.0)
        
        # Handle different optimizers
        if optimizer_name == "adam":
            optimizer = torch.optim.Adam(
                self.parameters(),
                lr=lr,
                weight_decay=weight_decay
            )
        elif optimizer_name == "sgd":
            momentum = self.config.get("momentum", 0.9)
            optimizer = torch.optim.SGD(
                self.parameters(),
                lr=lr,
                momentum=momentum,
                weight_decay=weight_decay
            )
        elif optimizer_name == "adamw":
            optimizer = torch.optim.AdamW(
                self.parameters(),
                lr=lr,
                weight_decay=weight_decay
            )
        else:
            raise ValueError(f"Unsupported optimizer: {optimizer_name}")
        
        # Optional learning rate scheduler
        scheduler_type = self.config.get("scheduler", None)
        if scheduler_type is None:
            return optimizer
        
        scheduler_type = scheduler_type.lower()
        
        if scheduler_type == "reduce_on_plateau":
            patience = self.config.get("patience", 10)
            factor = self.config.get("factor", 0.5)
            scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
                optimizer,
                mode="min",
                patience=patience,
                factor=factor,
                verbose=True
            )
            return {
                "optimizer": optimizer,
                "lr_scheduler": {
                    "scheduler": scheduler,
                    "monitor": "val_loss",
                    "interval": "epoch",
                    "frequency": 1
                }
            }
        
        elif scheduler_type == "cosine":
            max_epochs = self.config.get("max_epochs", 100)
            scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
                optimizer,
                T_max=max_epochs
            )
            return {
                "optimizer": optimizer,
                "lr_scheduler": {
                    "scheduler": scheduler,
                    "interval": "epoch",
                    "frequency": 1
                }
            }
        
        else:
            return optimizer 