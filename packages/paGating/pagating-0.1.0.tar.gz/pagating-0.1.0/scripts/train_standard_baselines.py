#!/usr/bin/env python
"""
Training script for standard activation function baselines on CIFAR-10.

This script trains CNN models with standard activations (ReLU, GELU, SiLU) 
for comparison with paGating variants.
"""

import os
import sys
import argparse
import torch
import torch.nn as nn
import torch.nn.functional as F
import pytorch_lightning as pl
from pytorch_lightning.callbacks import ModelCheckpoint, EarlyStopping
from pytorch_lightning.loggers import TensorBoardLogger
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
import json
from pathlib import Path

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Train CIFAR-10 with standard activations")
    
    parser.add_argument("--activation", type=str, required=True,
                        choices=["ReLU", "GELU", "SiLU", "Swish", "Tanh", "LeakyReLU"],
                        help="Activation function to use")
    parser.add_argument("--max_epochs", type=int, default=50,
                        help="Maximum training epochs")
    parser.add_argument("--batch_size", type=int, default=64,
                        help="Batch size")
    parser.add_argument("--learning_rate", type=float, default=1e-3,
                        help="Learning rate")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed")
    parser.add_argument("--output_dir", type=str, required=True,
                        help="Output directory")
    parser.add_argument("--num_workers", type=int, default=4,
                        help="Number of data loader workers")
    
    return parser.parse_args()


class StandardCNN(nn.Module):
    """CNN with configurable activation functions."""
    
    def __init__(self, activation_name="ReLU", num_classes=10):
        super().__init__()
        self.activation_name = activation_name
        
        # Get activation function
        self.activation = self._get_activation(activation_name)
        
        # Convolutional layers
        self.conv1 = nn.Conv2d(3, 32, 3, padding=1)
        self.bn1 = nn.BatchNorm2d(32)
        self.conv2 = nn.Conv2d(32, 64, 3, padding=1)
        self.bn2 = nn.BatchNorm2d(64)
        self.conv3 = nn.Conv2d(64, 128, 3, padding=1)
        self.bn3 = nn.BatchNorm2d(128)
        
        # Fully connected layers
        self.fc1 = nn.Linear(128 * 4 * 4, 512)
        self.dropout = nn.Dropout(0.5)
        self.fc2 = nn.Linear(512, num_classes)
        
        # Pooling
        self.pool = nn.MaxPool2d(2, 2)
        
    def _get_activation(self, name):
        """Get activation function by name."""
        activations = {
            "ReLU": nn.ReLU(),
            "GELU": nn.GELU(),
            "SiLU": nn.SiLU(),
            "Swish": nn.SiLU(),  # SiLU is Swish
            "Tanh": nn.Tanh(),
            "LeakyReLU": nn.LeakyReLU(0.1)
        }
        
        if name not in activations:
            raise ValueError(f"Unknown activation: {name}")
        
        return activations[name]
    
    def forward(self, x):
        # Conv block 1
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.activation(x)
        x = self.pool(x)
        
        # Conv block 2
        x = self.conv2(x)
        x = self.bn2(x)
        x = self.activation(x)
        x = self.pool(x)
        
        # Conv block 3
        x = self.conv3(x)
        x = self.bn3(x)
        x = self.activation(x)
        x = self.pool(x)
        
        # Flatten and FC layers
        x = x.view(x.size(0), -1)
        x = self.fc1(x)
        x = self.activation(x)
        x = self.dropout(x)
        x = self.fc2(x)
        
        return x


class StandardCIFARModule(pl.LightningModule):
    """PyTorch Lightning module for CIFAR-10 training."""
    
    def __init__(self, activation_name, learning_rate=1e-3):
        super().__init__()
        self.save_hyperparameters()
        
        self.model = StandardCNN(activation_name)
        self.criterion = nn.CrossEntropyLoss()
        self.learning_rate = learning_rate
        
        # Metrics
        self.train_acc = pl.metrics.Accuracy(task="multiclass", num_classes=10)
        self.val_acc = pl.metrics.Accuracy(task="multiclass", num_classes=10)
        self.test_acc = pl.metrics.Accuracy(task="multiclass", num_classes=10)
        
        # Track best metrics
        self.best_val_acc = 0.0
        self.final_test_acc = 0.0
    
    def forward(self, x):
        return self.model(x)
    
    def training_step(self, batch, batch_idx):
        x, y = batch
        logits = self(x)
        loss = self.criterion(logits, y)
        
        # Calculate accuracy
        preds = torch.argmax(logits, dim=1)
        acc = self.train_acc(preds, y)
        
        # Log metrics
        self.log("train_loss", loss, on_step=True, on_epoch=True, prog_bar=True)
        self.log("train_acc", acc, on_step=True, on_epoch=True, prog_bar=True)
        
        return loss
    
    def validation_step(self, batch, batch_idx):
        x, y = batch
        logits = self(x)
        loss = self.criterion(logits, y)
        
        # Calculate accuracy
        preds = torch.argmax(logits, dim=1)
        acc = self.val_acc(preds, y)
        
        # Log metrics
        self.log("val_loss", loss, on_epoch=True, prog_bar=True)
        self.log("val_acc", acc, on_epoch=True, prog_bar=True)
        
        return loss
    
    def test_step(self, batch, batch_idx):
        x, y = batch
        logits = self(x)
        loss = self.criterion(logits, y)
        
        # Calculate accuracy
        preds = torch.argmax(logits, dim=1)
        acc = self.test_acc(preds, y)
        
        # Log metrics
        self.log("test_loss", loss, on_epoch=True)
        self.log("test_acc", acc, on_epoch=True)
        
        return loss
    
    def on_validation_epoch_end(self):
        # Track best validation accuracy
        current_val_acc = self.trainer.callback_metrics.get("val_acc", 0.0)
        if current_val_acc > self.best_val_acc:
            self.best_val_acc = float(current_val_acc)
    
    def on_test_epoch_end(self):
        # Track final test accuracy
        self.final_test_acc = float(self.trainer.callback_metrics.get("test_acc", 0.0))
    
    def configure_optimizers(self):
        optimizer = torch.optim.Adam(self.parameters(), lr=self.learning_rate)
        scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=20, gamma=0.5)
        return [optimizer], [scheduler]


def get_cifar10_dataloaders(batch_size, num_workers=4):
    """Get CIFAR-10 data loaders."""
    
    # Data transforms
    transform_train = transforms.Compose([
        transforms.RandomCrop(32, padding=4),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010))
    ])
    
    transform_test = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010))
    ])
    
    # Datasets
    train_dataset = torchvision.datasets.CIFAR10(
        root='./data', train=True, download=True, transform=transform_train
    )
    
    test_dataset = torchvision.datasets.CIFAR10(
        root='./data', train=False, download=True, transform=transform_test
    )
    
    # Split train into train/val
    train_size = int(0.9 * len(train_dataset))
    val_size = len(train_dataset) - train_size
    train_subset, val_subset = torch.utils.data.random_split(
        train_dataset, [train_size, val_size]
    )
    
    # Data loaders
    train_loader = DataLoader(
        train_subset, batch_size=batch_size, shuffle=True, 
        num_workers=num_workers, persistent_workers=True
    )
    
    val_loader = DataLoader(
        val_subset, batch_size=batch_size, shuffle=False,
        num_workers=num_workers, persistent_workers=True
    )
    
    test_loader = DataLoader(
        test_dataset, batch_size=batch_size, shuffle=False,
        num_workers=num_workers, persistent_workers=True
    )
    
    return train_loader, val_loader, test_loader


def main():
    """Main training function."""
    args = parse_args()
    
    # Set seed
    pl.seed_everything(args.seed)
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"🚀 Training CIFAR-10 with {args.activation} activation")
    print(f"📁 Output directory: {output_dir}")
    print(f"🎲 Seed: {args.seed}")
    print(f"📊 Batch size: {args.batch_size}")
    print(f"🔄 Max epochs: {args.max_epochs}")
    print(f"📈 Learning rate: {args.learning_rate}")
    
    # Get data loaders
    train_loader, val_loader, test_loader = get_cifar10_dataloaders(
        args.batch_size, args.num_workers
    )
    
    # Create model
    model = StandardCIFARModule(args.activation, args.learning_rate)
    
    # Callbacks
    checkpoint_callback = ModelCheckpoint(
        dirpath=output_dir / "checkpoints",
        filename=f"{args.activation}_best",
        monitor="val_acc",
        mode="max",
        save_top_k=1
    )
    
    early_stopping = EarlyStopping(
        monitor="val_acc",
        mode="max",
        patience=10,
        verbose=True
    )
    
    # Logger
    logger = TensorBoardLogger(
        save_dir=output_dir,
        name=f"{args.activation}_logs"
    )
    
    # Trainer
    trainer = pl.Trainer(
        max_epochs=args.max_epochs,
        callbacks=[checkpoint_callback, early_stopping],
        logger=logger,
        accelerator="auto",
        devices=1,
        deterministic=True,
        enable_progress_bar=True
    )
    
    # Train
    print("🏋️ Starting training...")
    trainer.fit(model, train_loader, val_loader)
    
    # Test
    print("🧪 Running final test...")
    trainer.test(model, test_loader, ckpt_path="best")
    
    # Save results
    results = {
        "activation": args.activation,
        "seed": args.seed,
        "hyperparameters": {
            "batch_size": args.batch_size,
            "learning_rate": args.learning_rate,
            "max_epochs": args.max_epochs
        },
        "metrics": {
            "best_val_acc": float(model.best_val_acc),
            "final_test_acc": float(model.final_test_acc)
        },
        "model_parameters": sum(p.numel() for p in model.parameters())
    }
    
    # Save to JSON
    results_file = output_dir / "results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"✅ Training completed!")
    print(f"📊 Best validation accuracy: {model.best_val_acc:.4f}")
    print(f"🎯 Final test accuracy: {model.final_test_acc:.4f}")
    print(f"💾 Results saved to: {results_file}")
    
    # Print final results for parsing
    print(f"Final validation accuracy: {model.best_val_acc:.4f}")
    print(f"Final test accuracy: {model.final_test_acc:.4f}")


if __name__ == "__main__":
    main() 