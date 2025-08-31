"""
Training script for CIFAR-10 models using paGating units.

This script trains models on the CIFAR-10 dataset using different paGating units
and configurations, with PyTorch Lightning for training management.
"""

import os
import argparse
import pytorch_lightning as pl
from pytorch_lightning.loggers import TensorBoardLogger
from pytorch_lightning.callbacks import LearningRateMonitor
import torch

from models.cifar_data_module import CIFAR10DataModule
from models.pa_cifar_module import PACIFARLightningModule


def parse_args():
    parser = argparse.ArgumentParser(description="Train CIFAR-10 models with paGating units")
    
    # Model parameters
    parser.add_argument("--unit", type=str, default="paMishU", 
                        help="paGating unit to use (e.g., paMishU, paGLU, paReGLU)")
    parser.add_argument("--alpha", type=float, default=0.5, 
                        help="Alpha value for the paGating unit")
    parser.add_argument("--use_gate_norm", action="store_true", 
                        help="Whether to use gate normalization")
    
    # Training parameters
    parser.add_argument("--batch_size", type=int, default=128, 
                        help="Training batch size")
    parser.add_argument("--learning_rate", type=float, default=0.1, 
                        help="Initial learning rate")
    parser.add_argument("--weight_decay", type=float, default=5e-4, 
                        help="Weight decay (L2 regularization)")
    parser.add_argument("--epochs", type=int, default=100, 
                        help="Number of training epochs")
    parser.add_argument("--num_workers", type=int, default=4, 
                        help="Number of data loading workers")
    
    # Logging and checkpoint parameters
    parser.add_argument("--log_dir", type=str, default="logs", 
                        help="Directory for storing logs")
    parser.add_argument("--ckpt_dir", type=str, default="checkpoints", 
                        help="Directory for storing checkpoints")
    parser.add_argument("--resume_from", type=str, default=None, 
                        help="Path to checkpoint to resume from")
    
    return parser.parse_args()


def main():
    # Parse arguments
    args = parse_args()
    
    # Set experiment name
    experiment_name = f"{args.unit}_alpha{args.alpha:.2f}"
    if args.use_gate_norm:
        experiment_name += "_gatenorm"
    
    # Create directories
    os.makedirs(args.log_dir, exist_ok=True)
    os.makedirs(args.ckpt_dir, exist_ok=True)
    
    # Set up logger
    logger = TensorBoardLogger(
        save_dir=args.log_dir,
        name=experiment_name,
    )
    
    # Prepare data module
    data_module = CIFAR10DataModule(
        batch_size=args.batch_size,
        num_workers=args.num_workers,
    )
    
    # Create model
    model = PACIFARLightningModule(
        unit_name=args.unit,
        alpha=args.alpha,
        use_gate_norm=args.use_gate_norm,
        learning_rate=args.learning_rate,
        weight_decay=args.weight_decay,
    )
    
    # Get default callbacks
    callbacks = PACIFARLightningModule.get_default_callbacks(
        monitor="val_acc",
        mode="max",
        dirpath=os.path.join(args.ckpt_dir, experiment_name),
    )
    
    # Add learning rate monitor
    callbacks.append(LearningRateMonitor(logging_interval="epoch"))
    
    # Create trainer
    trainer = pl.Trainer(
        max_epochs=args.epochs,
        accelerator="auto",
        devices=1 if torch.cuda.is_available() else None,
        logger=logger,
        callbacks=callbacks,
        precision="16-mixed" if torch.cuda.is_available() else 32,
    )
    
    # Train model
    trainer.fit(model, datamodule=data_module, ckpt_path=args.resume_from)
    
    # Test model
    trainer.test(model, datamodule=data_module)
    
    # Save final model
    final_path = os.path.join(args.ckpt_dir, experiment_name, "final_model.pt")
    torch.save(model.state_dict(), final_path)
    print(f"Saved final model to {final_path}")


if __name__ == "__main__":
    main() 