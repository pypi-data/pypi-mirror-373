"""
Custom metrics logger for PyTorch Lightning to save metrics in the format needed by the dashboard.
"""

import os
import csv
from typing import Dict, Any, Optional

import pytorch_lightning as pl
from pytorch_lightning.callbacks import Callback
from pytorch_lightning.utilities.types import STEP_OUTPUT

class MetricsCsvLogger(Callback):
    """
    Callback to save training metrics as CSV for the dashboard.
    
    This callback saves metrics after each epoch to a CSV file that can be
    directly used by the dashboard_cifar.py application.
    
    Args:
        output_dir: Directory to save metrics
        unit_name: Name of the paGating unit being trained
        alpha_value: Alpha value used for training (if static)
    """
    
    def __init__(
        self, 
        output_dir: str = "logs/cifar10", 
        unit_name: str = "paGLU",
        alpha_value: Optional[float] = None
    ):
        super().__init__()
        self.output_dir = output_dir
        self.unit_name = unit_name
        self.alpha_value = alpha_value
        self.metrics = []
        self.has_alpha = alpha_value is not None
        
        # Create output directory
        os.makedirs(os.path.join(output_dir, unit_name), exist_ok=True)
    
    def on_train_epoch_end(self, trainer: pl.Trainer, pl_module: pl.LightningModule):
        """Called when the train epoch ends."""
        epoch = trainer.current_epoch
        metrics_dict = {"epoch": epoch + 1}  # 1-indexed epoch for readability

        # Get metrics from callback_metrics
        callback_metrics = trainer.callback_metrics
        for key, value in callback_metrics.items():
            if hasattr(value, "item"):
                value = value.item()
            
            # Extract training metrics
            if key == "train_loss" or key == "train/loss":
                metrics_dict["train_loss"] = value
            elif key == "train_acc" or key == "train/acc":
                metrics_dict["train_acc"] = value
        
        # Check for learnable alpha
        found_learnable_alpha = False
        for name, param in pl_module.named_parameters():
            if "alpha" in name and hasattr(param, "item"):
                metrics_dict["alpha"] = param.item()
                found_learnable_alpha = True
                self.has_alpha = True
                break

        # Always include static alpha if provided
        if not found_learnable_alpha and self.alpha_value is not None:
            metrics_dict["alpha"] = self.alpha_value
            self.has_alpha = True
        
        self.metrics.append(metrics_dict)
        self._save_metrics()
    
    def on_validation_epoch_end(self, trainer: pl.Trainer, pl_module: pl.LightningModule):
        """Called when the validation epoch ends."""
        # Get current metrics
        if not self.metrics:
            return
        
        # Get the latest metrics dict (from current epoch)
        metrics_dict = self.metrics[-1]
        
        # Get logged metrics from callback_metrics
        callback_metrics = trainer.callback_metrics
        
        # Add validation metrics
        for key, value in callback_metrics.items():
            if hasattr(value, "item"):
                value = value.item()
            
            # Map metric names to expected dashboard format
            if key == "val_loss" or key == "val/loss":
                metrics_dict["val_loss"] = value
            elif key == "val_acc" or key == "val/acc":
                metrics_dict["val_acc"] = value
        
        self._save_metrics()
    
    def _save_metrics(self):
        """Save metrics to CSV file."""
        filepath = os.path.join(self.output_dir, self.unit_name, "metrics.csv")
        
        # Create header row
        if not self.metrics:
            return
        
        # Define base header - always include these columns
        header = ["epoch", "train_loss", "val_loss", "train_acc", "val_acc"]
        
        # Add alpha if needed
        if self.has_alpha:
            if "alpha" not in header:
                header.append("alpha")
        
        # Add test metrics if they exist
        if any("test_loss" in m for m in self.metrics):
            if "test_loss" not in header:
                header.append("test_loss")
        
        if any("test_acc" in m for m in self.metrics):
            if "test_acc" not in header:
                header.append("test_acc")
        
        # Write to CSV
        with open(filepath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=header)
            writer.writeheader()
            for metrics_dict in self.metrics:
                writer.writerow({k: metrics_dict.get(k, "") for k in header})
        
        print(f"Saved metrics to {filepath}")
    
    def on_test_end(self, trainer: pl.Trainer, pl_module: pl.LightningModule):
        """Save final metrics including test results."""
        # Get test metrics
        callback_metrics = trainer.callback_metrics
        
        # Add test metrics to last training epoch
        if self.metrics:
            metrics_dict = self.metrics[-1]
            
            for key, value in callback_metrics.items():
                if hasattr(value, "item"):
                    value = value.item()
                
                if key == "test_loss" or key == "test/loss":
                    metrics_dict["test_loss"] = value
                elif key == "test_acc" or key == "test/acc":
                    metrics_dict["test_acc"] = value
            
            # Add test metrics to header and save
            self._save_metrics()
            
    def get_metrics_as_dict(self) -> Dict[str, Any]:
        """
        Returns a dictionary with model configuration and metrics.
        
        Useful for exporting metrics to dashboard or other systems.
        
        Returns:
            Dict containing unit_name, alpha_type, and metrics list
        """
        alpha_type = "static" if self.alpha_value is not None else "learnable"
        
        return {
            "unit_name": self.unit_name,
            "alpha_type": alpha_type,
            "alpha_value": self.alpha_value,
            "metrics": self.metrics
        } 