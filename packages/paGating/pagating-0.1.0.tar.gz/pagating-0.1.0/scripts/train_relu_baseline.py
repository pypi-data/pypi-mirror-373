#!/usr/bin/env python
"""
CIFAR-10 ReLU baseline training script.

This script trains a baseline CNN with ReLU activations on CIFAR-10 
to compare against paGating units.
"""

import os
import argparse
import json
from datetime import datetime

import torch
import torch.nn as nn
import torch.nn.functional as F
import pytorch_lightning as pl
from pytorch_lightning.loggers import TensorBoardLogger
from pytorch_lightning.callbacks import ModelCheckpoint, EarlyStopping

# Add parent directory to path to import paGating modules
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lightning_modules.datamodule import CIFAR10DataModule


class ReLUBaselineModel(pl.LightningModule):
    """
    CNN baseline model for CIFAR-10 classification using ReLU activations.
    
    This model implements the same architecture as the paGating CIFAR-10 model
    but uses standard ReLU activations for comparison.
    """
    
    def __init__(
        self,
        learning_rate: float = 0.001,
        weight_decay: float = 1e-4,
    ):
        super().__init__()
        self.save_hyperparameters()
        
        # Create layers with ReLU activations
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            nn.Conv2d(128, 256, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )
        
        # Classifier
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(256 * 2 * 2, 512),
            nn.ReLU(),
            nn.Linear(512, 10)
        )

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


def main():
    """Main training function."""
    parser = argparse.ArgumentParser(description="CIFAR-10 ReLU baseline training")
    
    # Model arguments
    parser.add_argument("--learning_rate", type=float, default=0.001)
    parser.add_argument("--weight_decay", type=float, default=1e-4)
    
    # Training arguments
    parser.add_argument("--max_epochs", type=int, default=50)
    parser.add_argument("--batch_size", type=int, default=64)
    parser.add_argument("--num_workers", type=int, default=4)
    
    # Data arguments
    parser.add_argument("--data_dir", type=str, default="data/cifar10")
    parser.add_argument("--val_split", type=float, default=0.1)
    
    # Experiment arguments
    parser.add_argument("--output_dir", type=str, default="benchmark_results/relu_baseline")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--gpus", type=int, default=0)
    
    args = parser.parse_args()
    
    # Set seed for reproducibility
    pl.seed_everything(args.seed)
    
    # Set up output directory
    time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(args.output_dir, f"relu_baseline_{time_str}")
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize data module
    datamodule = CIFAR10DataModule(
        data_dir=args.data_dir,
        batch_size=args.batch_size,
        num_workers=args.num_workers,
        val_split=args.val_split,
    )
    
    # Initialize model
    model = ReLUBaselineModel(
        learning_rate=args.learning_rate,
        weight_decay=args.weight_decay,
    )
    
    # Set up logger
    logger = TensorBoardLogger(output_dir, name="relu_baseline")
    
    # Set up callbacks
    callbacks = [
        ModelCheckpoint(
            monitor="val_acc",
            mode="max",
            save_top_k=1,
            filename="best_model",
        ),
        EarlyStopping(
            monitor="val_loss",
            patience=10,
            mode="min",
        ),
    ]
    
    # Initialize trainer
    trainer = pl.Trainer(
        max_epochs=args.max_epochs,
        logger=logger,
        callbacks=callbacks,
        gpus=args.gpus,
        deterministic=True,
    )
    
    # Train the model
    trainer.fit(model, datamodule)
    
    # Test the model
    trainer.test(model, datamodule)
    
    # Save final results
    val_acc = trainer.callback_metrics.get("val_acc", 0.0)
    test_acc = trainer.callback_metrics.get("test_acc", 0.0)
    
    results = {
        "ReLU_baseline": {
            "val_acc": float(val_acc),
            "test_acc": float(test_acc),
            "config": {
                "learning_rate": args.learning_rate,
                "weight_decay": args.weight_decay,
                "max_epochs": args.max_epochs,
                "batch_size": args.batch_size,
                "seed": args.seed,
            }
        }
    }
    
    results_file = os.path.join(output_dir, "results.json")
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Training completed. Results saved to {results_file}")
    print(f"Validation Accuracy: {val_acc:.4f}")
    print(f"Test Accuracy: {test_acc:.4f}")


if __name__ == "__main__":
    main() 