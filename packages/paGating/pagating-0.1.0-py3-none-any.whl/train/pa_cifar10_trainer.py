"""
PyTorch Lightning trainer for CIFAR-10 classification using paGating models.

This module provides a PyTorch Lightning module for training paGating models on the CIFAR-10 dataset,
including training configuration, optimization, and evaluation metrics.
"""

import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import pytorch_lightning as pl
from typing import Dict, Any, Tuple, List, Optional
from pytorch_lightning.callbacks import ModelCheckpoint, LearningRateMonitor
from pytorch_lightning.loggers import TensorBoardLogger
from torch.optim.lr_scheduler import OneCycleLR, CosineAnnealingLR

# Import our model and data module
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.pa_cifar10_model import paCIFAR10Model
from data.cifar10_datamodule import CIFAR10DataModule


class CIFAR10LitModule(pl.LightningModule):
    """
    PyTorch Lightning module for training CIFAR-10 classification models using paGating units.
    
    Args:
        unit_name: Name of the paGating unit to use
        alpha: Alpha parameter for the paGating unit
        use_gate_norm: Whether to use gate normalization
        learning_rate: Initial learning rate
        weight_decay: Weight decay factor
        max_epochs: Maximum number of training epochs
        scheduler: Learning rate scheduler type ('onecycle' or 'cosine')
    """
    
    def __init__(
        self,
        unit_name: str = "paGLU",
        alpha: float = 0.5,
        use_gate_norm: bool = False,
        learning_rate: float = 1e-3,
        weight_decay: float = 1e-4,
        max_epochs: int = 100,
        scheduler: str = "onecycle",
    ):
        super().__init__()
        self.save_hyperparameters()
        
        # Create the model
        self.model = paCIFAR10Model(
            unit_name=unit_name,
            alpha=alpha,
            use_gate_norm=use_gate_norm
        )
        
        # Loss function
        self.criterion = nn.CrossEntropyLoss()
        
        # Metrics
        self.train_acc = pl.metrics.Accuracy(task="multiclass", num_classes=10)
        self.val_acc = pl.metrics.Accuracy(task="multiclass", num_classes=10)
        self.test_acc = pl.metrics.Accuracy(task="multiclass", num_classes=10)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass"""
        return self.model(x)
    
    def training_step(self, batch: Tuple[torch.Tensor, torch.Tensor], batch_idx: int) -> Dict[str, torch.Tensor]:
        """Training step"""
        x, y = batch
        logits = self(x)
        loss = self.criterion(logits, y)
        
        # Calculate accuracy
        preds = torch.argmax(logits, dim=1)
        acc = self.train_acc(preds, y)
        
        # Log metrics
        self.log("train_loss", loss, prog_bar=True)
        self.log("train_acc", acc, prog_bar=True)
        
        return {"loss": loss, "preds": preds, "targets": y}
    
    def validation_step(self, batch: Tuple[torch.Tensor, torch.Tensor], batch_idx: int) -> Dict[str, torch.Tensor]:
        """Validation step"""
        x, y = batch
        logits = self(x)
        loss = self.criterion(logits, y)
        
        # Calculate accuracy
        preds = torch.argmax(logits, dim=1)
        acc = self.val_acc(preds, y)
        
        # Log metrics
        self.log("val_loss", loss, prog_bar=True)
        self.log("val_acc", acc, prog_bar=True)
        
        return {"val_loss": loss, "val_preds": preds, "val_targets": y}
    
    def test_step(self, batch: Tuple[torch.Tensor, torch.Tensor], batch_idx: int) -> Dict[str, torch.Tensor]:
        """Test step"""
        x, y = batch
        logits = self(x)
        loss = self.criterion(logits, y)
        
        # Calculate accuracy
        preds = torch.argmax(logits, dim=1)
        acc = self.test_acc(preds, y)
        
        # Log metrics
        self.log("test_loss", loss, prog_bar=True)
        self.log("test_acc", acc, prog_bar=True)
        
        return {"test_loss": loss, "test_preds": preds, "test_targets": y}
    
    def configure_optimizers(self) -> Dict[str, Any]:
        """Configure optimizers and learning rate schedulers"""
        optimizer = torch.optim.AdamW(
            self.parameters(), 
            lr=self.hparams.learning_rate,
            weight_decay=self.hparams.weight_decay
        )
        
        if self.hparams.scheduler == "onecycle":
            scheduler = OneCycleLR(
                optimizer,
                max_lr=self.hparams.learning_rate,
                total_steps=self.trainer.estimated_stepping_batches,
                pct_start=0.3,
                div_factor=25.0,
                final_div_factor=10000.0,
                three_phase=False
            )
            scheduler_config = {
                "scheduler": scheduler,
                "interval": "step",
                "frequency": 1,
            }
        else:  # cosine
            scheduler = CosineAnnealingLR(
                optimizer,
                T_max=self.hparams.max_epochs,
                eta_min=self.hparams.learning_rate / 100
            )
            scheduler_config = {
                "scheduler": scheduler,
                "interval": "epoch",
                "frequency": 1,
            }
        
        return {"optimizer": optimizer, "lr_scheduler": scheduler_config}


def train_model(
    unit_name: str = "paGLU",
    alpha: float = 0.5,
    use_gate_norm: bool = False,
    batch_size: int = 128,
    learning_rate: float = 1e-3,
    weight_decay: float = 1e-4,
    max_epochs: int = 100,
    num_workers: int = 4,
    data_dir: str = "./data/cifar10",
    scheduler: str = "onecycle",
    precision: int = 16,
    accelerator: str = "auto",
):
    """
    Train a CIFAR-10 model with paGating units.
    
    Args:
        unit_name: Name of the paGating unit to use
        alpha: Alpha parameter for the paGating unit
        use_gate_norm: Whether to use gate normalization
        batch_size: Batch size for training
        learning_rate: Initial learning rate
        weight_decay: Weight decay factor
        max_epochs: Maximum number of training epochs
        num_workers: Number of workers for data loading
        data_dir: Directory to store the dataset
        scheduler: Learning rate scheduler type ('onecycle' or 'cosine')
        precision: Numerical precision for training (16 or 32)
        accelerator: Hardware to use for training ('cpu', 'gpu', 'auto')
    """
    # Create the data module
    data_module = CIFAR10DataModule(
        data_dir=data_dir,
        batch_size=batch_size,
        num_workers=num_workers,
        augment=True,
        normalize=True
    )
    
    # Create the model
    model = CIFAR10LitModule(
        unit_name=unit_name,
        alpha=alpha,
        use_gate_norm=use_gate_norm,
        learning_rate=learning_rate,
        weight_decay=weight_decay,
        max_epochs=max_epochs,
        scheduler=scheduler
    )
    
    # Callbacks
    checkpoint_callback = ModelCheckpoint(
        monitor="val_acc",
        mode="max",
        save_top_k=3,
        save_last=True,
        filename=f"{unit_name}_alpha{alpha:.2f}_{{epoch:02d}}_{{val_acc:.4f}}",
        dirpath=f"./checkpoints/{unit_name}/alpha{alpha:.2f}"
    )
    
    lr_monitor = LearningRateMonitor(logging_interval="step")
    
    # Logger
    logger = TensorBoardLogger(
        save_dir="./logs",
        name=f"{unit_name}_alpha{alpha:.2f}"
    )
    
    # Create the trainer
    trainer = pl.Trainer(
        max_epochs=max_epochs,
        accelerator=accelerator,
        devices=1,
        precision=precision,
        callbacks=[checkpoint_callback, lr_monitor],
        logger=logger,
        log_every_n_steps=10,
        deterministic=False
    )
    
    # Train the model
    trainer.fit(model, data_module)
    
    # Test the model
    trainer.test(model, data_module)
    
    return model, trainer


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Train CIFAR-10 model with paGating units")
    parser.add_argument("--unit", type=str, default="paGLU", help="paGating unit to use")
    parser.add_argument("--alpha", type=float, default=0.5, help="Alpha parameter for the paGating unit")
    parser.add_argument("--use_gate_norm", action="store_true", help="Use gate normalization")
    parser.add_argument("--batch_size", type=int, default=128, help="Batch size for training")
    parser.add_argument("--lr", type=float, default=1e-3, help="Learning rate")
    parser.add_argument("--weight_decay", type=float, default=1e-4, help="Weight decay factor")
    parser.add_argument("--epochs", type=int, default=100, help="Maximum number of epochs")
    parser.add_argument("--workers", type=int, default=4, help="Number of data loading workers")
    parser.add_argument("--data_dir", type=str, default="./data/cifar10", help="Directory to store the dataset")
    parser.add_argument("--scheduler", type=str, default="onecycle", choices=["onecycle", "cosine"], help="Learning rate scheduler")
    parser.add_argument("--precision", type=int, default=16, choices=[16, 32], help="Numerical precision for training")
    parser.add_argument("--accelerator", type=str, default="auto", choices=["cpu", "gpu", "auto"], help="Hardware to use for training")
    
    args = parser.parse_args()
    
    # Train the model
    model, trainer = train_model(
        unit_name=args.unit,
        alpha=args.alpha,
        use_gate_norm=args.use_gate_norm,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        weight_decay=args.weight_decay,
        max_epochs=args.epochs,
        num_workers=args.workers,
        data_dir=args.data_dir,
        scheduler=args.scheduler,
        precision=args.precision,
        accelerator=args.accelerator
    ) 