#!/usr/bin/env python
"""
CIFAR-10 training script for paGating units.

This script trains various paGating units on the CIFAR-10 classification task
using PyTorch Lightning.
"""

import os
import argparse
from datetime import datetime

import torch
import torch.nn as nn
import torch.nn.functional as F
import pytorch_lightning as pl
from pytorch_lightning.loggers import TensorBoardLogger
from pytorch_lightning.callbacks import ModelCheckpoint, EarlyStopping, LearningRateMonitor

from lightning_modules.paGatingModule import paGatingModule
from lightning_modules.metrics_logger import MetricsCsvLogger
from lightning_modules.datamodule import CIFAR10DataModule
import paGating


class CIFAR10Model(pl.LightningModule):
    """
    CNN model for CIFAR-10 classification using paGating units.
    
    This model implements a simple convolutional neural network with paGating
    units for feature activation and classification on CIFAR-10.
    
    Args:
        unit_name: Name of the paGating unit to use
        alpha: Alpha value for the paGating unit
        learning_rate: Initial learning rate
        weight_decay: Weight decay for optimizer
        use_learnable_alpha: Whether to use a learnable alpha parameter
    """
    
    def __init__(
        self,
        unit_name: str = "paGLU",
        alpha: float = 0.5,
        learning_rate: float = 0.001,
        weight_decay: float = 1e-4,
        use_learnable_alpha: bool = False,
    ):
        super().__init__()
        self.save_hyperparameters()
        
        # Get the paGating unit class
        unit_class = getattr(paGating, unit_name)
        
        # Create layers
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(32),
            self._create_gate_module(unit_class, 32, 32, alpha, use_learnable_alpha),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(64),
            self._create_gate_module(unit_class, 64, 64, alpha, use_learnable_alpha),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(128),
            self._create_gate_module(unit_class, 128, 128, alpha, use_learnable_alpha),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            nn.Conv2d(128, 256, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(256),
            self._create_gate_module(unit_class, 256, 256, alpha, use_learnable_alpha),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )
        
        # Classifier
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(256 * 2 * 2, 512),
            self._create_gate_module(unit_class, 512, 512, alpha, use_learnable_alpha),
            nn.Linear(512, 10)
        )

    def _create_gate_module(self, unit_class, input_dim, output_dim, alpha, use_learnable_alpha):
        """Helper to create a paGating module with the given parameters."""
        if isinstance(input_dim, int) and input_dim != output_dim:
            # Ensure dimensions match for paGating units
            return nn.Sequential(
                nn.Linear(input_dim, output_dim) if len(str(input_dim)) <= 3 else nn.Conv2d(input_dim, output_dim, 1),
                unit_class(output_dim, alpha=alpha if not use_learnable_alpha else None)
            )
        else:
            return unit_class(input_dim, alpha=alpha if not use_learnable_alpha else None)
    
    def forward(self, x):
        """Forward pass through the network."""
        x = self.features(x)
        x = self.classifier(x)
        return x
    
    def training_step(self, batch, batch_idx):
        """Training step."""
        x, y = batch
        logits = self(x)
        loss = F.cross_entropy(logits, y)
        
        # Calculate accuracy
        preds = torch.argmax(logits, dim=1)
        acc = (preds == y).float().mean()
        
        # Log metrics
        self.log('train_loss', loss, on_step=True, on_epoch=True, prog_bar=True)
        self.log('train_acc', acc, on_step=True, on_epoch=True, prog_bar=True)
        
        return loss
    
    def validation_step(self, batch, batch_idx):
        """Validation step."""
        x, y = batch
        logits = self(x)
        loss = F.cross_entropy(logits, y)
        
        # Calculate accuracy
        preds = torch.argmax(logits, dim=1)
        acc = (preds == y).float().mean()
        
        # Log metrics
        self.log('val_loss', loss, on_epoch=True, prog_bar=True)
        self.log('val_acc', acc, on_epoch=True, prog_bar=True)
        
        return loss
    
    def test_step(self, batch, batch_idx):
        """Test step."""
        x, y = batch
        logits = self(x)
        loss = F.cross_entropy(logits, y)
        
        # Calculate accuracy
        preds = torch.argmax(logits, dim=1)
        acc = (preds == y).float().mean()
        
        # Log metrics
        self.log('test_loss', loss, on_epoch=True)
        self.log('test_acc', acc, on_epoch=True)
        
        return loss
    
    def configure_optimizers(self):
        """Configure optimizers."""
        optimizer = torch.optim.Adam(
            self.parameters(),
            lr=self.hparams.learning_rate,
            weight_decay=self.hparams.weight_decay
        )
        
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer,
            mode='min',
            factor=0.5,
            patience=5,
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
    
    @staticmethod
    def add_model_specific_args(parent_parser):
        """Add model specific arguments to parser."""
        parser = parent_parser.add_argument_group("CIFAR10Model")
        parser.add_argument("--unit_name", type=str, default="paGLU")
        parser.add_argument("--alpha", type=float, default=0.5)
        parser.add_argument("--learning_rate", type=float, default=0.001)
        parser.add_argument("--weight_decay", type=float, default=1e-4)
        parser.add_argument("--use_learnable_alpha", action="store_true")
        return parent_parser


def main(args):
    """Main training function."""
    pl.seed_everything(args.seed)
    
    # Set up output directory
    time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(
        args.output_dir,
        f"{args.unit_name}_alpha{args.alpha}{'_learnable' if args.use_learnable_alpha else ''}_{time_str}"
    )
    os.makedirs(output_dir, exist_ok=True)
    
    # Set up data module
    datamodule = CIFAR10DataModule(
        data_dir=args.data_dir,
        batch_size=args.batch_size,
        num_workers=args.num_workers,
        val_split=args.val_split,
        seed=args.seed
    )
    
    # Set up model
    model = CIFAR10Model(
        unit_name=args.unit_name,
        alpha=args.alpha,
        learning_rate=args.learning_rate,
        weight_decay=args.weight_decay,
        use_learnable_alpha=args.use_learnable_alpha
    )
    
    # Logger
    logger = TensorBoardLogger(
        save_dir=output_dir,
        name="logs",
        default_hp_metric=False
    )
    
    # Callbacks
    callbacks = [
        ModelCheckpoint(
            dirpath=os.path.join(output_dir, "checkpoints"),
            filename="{epoch:02d}-{val_loss:.4f}-{val_acc:.4f}",
            monitor="val_loss",
            mode="min",
            save_top_k=3,
            save_last=True
        ),
        EarlyStopping(
            monitor="val_loss",
            patience=10,
            mode="min"
        ),
        LearningRateMonitor(logging_interval="epoch"),
        MetricsCsvLogger(
            output_dir=output_dir,
            unit_name=args.unit_name,
            alpha_value=args.alpha if not args.use_learnable_alpha else None
        )
    ]
    
    # Trainer
    trainer = pl.Trainer(
        max_epochs=args.max_epochs,
        accelerator="gpu" if torch.cuda.is_available() and not args.cpu else "cpu",
        devices=1,
        logger=logger,
        callbacks=callbacks,
        log_every_n_steps=50,
        deterministic=True
    )
    
    # Train and test
    trainer.fit(model, datamodule)
    trainer.test(model, datamodule, ckpt_path="best")
    
    print(f"Training completed. Results saved to {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CIFAR-10 Training Script for paGating Units")
    
    # Add datamodule arguments
    parser = CIFAR10DataModule.add_datamodule_specific_args(parser)
    
    # Add model arguments
    parser = CIFAR10Model.add_model_specific_args(parser)
    
    # Add trainer arguments
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max_epochs", type=int, default=100)
    parser.add_argument("--output_dir", type=str, default="cifar10_results")
    parser.add_argument("--cpu", action="store_true", help="Force CPU training")
    
    args = parser.parse_args()
    main(args) 