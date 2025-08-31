#!/usr/bin/env python
"""
PyTorch Lightning Training Script for paGating Units

This script trains paGating units using PyTorch Lightning on synthetic data.
It demonstrates how to use the paGatingModule with a simple regression task.

Usage:
    python train_lightning.py --unit paGELU --alpha 0.5 --epochs 10 --batch-size 32
    python train_lightning.py --unit paSiLU --alpha learnable --optimizer adamw --lr 0.001

Requirements:
    - PyTorch 1.9+
    - PyTorch Lightning
    - paGating package
"""

import os
import sys
import argparse
import torch
import torch.nn as nn
import torch.utils.data as data
import pytorch_lightning as pl
from pytorch_lightning.callbacks import ModelCheckpoint, EarlyStopping, LearningRateMonitor
from pytorch_lightning.loggers import TensorBoardLogger

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import paGating Lightning module
from lightning_modules.paGatingModule import paGatingModule


class SyntheticRegressionDataset(data.Dataset):
    """Synthetic regression dataset for demonstrating paGating training.
    
    This dataset generates random input features and computes target values
    using a non-linear function, making it suitable for testing activation functions.
    
    Args:
        num_samples (int): Number of samples to generate
        input_dim (int): Input dimension
        output_dim (int): Output dimension
        noise_level (float): Standard deviation of Gaussian noise added to targets
        seed (int, optional): Random seed for reproducibility
    """
    
    def __init__(self, num_samples, input_dim, output_dim, noise_level=0.1, seed=None):
        super().__init__()
        self.num_samples = num_samples
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.noise_level = noise_level
        
        # Set random seed if provided
        if seed is not None:
            torch.manual_seed(seed)
        
        # Generate random inputs
        self.inputs = torch.randn(num_samples, input_dim)
        
        # Generate random projection matrices
        self.W1 = torch.randn(input_dim, input_dim)
        self.W2 = torch.randn(input_dim, output_dim)
        
        # Compute targets using a non-linear function
        h = torch.tanh(self.inputs @ self.W1)
        self.targets = h @ self.W2
        
        # Add noise to make the task more challenging
        if noise_level > 0:
            self.targets += torch.randn_like(self.targets) * noise_level
    
    def __len__(self):
        return self.num_samples
    
    def __getitem__(self, idx):
        return self.inputs[idx], self.targets[idx]


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Train paGating units with PyTorch Lightning"
    )
    
    # Model parameters
    parser.add_argument(
        "--unit",
        type=str,
        default="paGELU",
        choices=["paGLU", "paGTU", "paSwishU", "paReGLU", "paGELU", "paMishU", "paSiLU"],
        help="paGating unit to train (default: paGELU)"
    )
    
    parser.add_argument(
        "--alpha",
        type=str,
        default="0.5",
        help="Alpha value (0.0-1.0) or 'learnable' (default: 0.5)"
    )
    
    parser.add_argument(
        "--input-dim",
        type=int,
        default=64,
        help="Input dimension (default: 64)"
    )
    
    parser.add_argument(
        "--output-dim",
        type=int,
        default=32,
        help="Output dimension (default: 32)"
    )
    
    # Dataset parameters
    parser.add_argument(
        "--train-samples",
        type=int,
        default=10000,
        help="Number of training samples (default: 10000)"
    )
    
    parser.add_argument(
        "--val-samples",
        type=int,
        default=2000,
        help="Number of validation samples (default: 2000)"
    )
    
    parser.add_argument(
        "--test-samples",
        type=int,
        default=2000,
        help="Number of test samples (default: 2000)"
    )
    
    parser.add_argument(
        "--noise-level",
        type=float,
        default=0.1,
        help="Noise level for synthetic data (default: 0.1)"
    )
    
    # Training parameters
    parser.add_argument(
        "--batch-size",
        type=int,
        default=128,
        help="Batch size (default: 128)"
    )
    
    parser.add_argument(
        "--epochs",
        type=int,
        default=20,
        help="Number of training epochs (default: 20)"
    )
    
    parser.add_argument(
        "--optimizer",
        type=str,
        default="adam",
        choices=["adam", "sgd", "adamw"],
        help="Optimizer to use (default: adam)"
    )
    
    parser.add_argument(
        "--lr",
        type=float,
        default=0.001,
        help="Learning rate (default: 0.001)"
    )
    
    parser.add_argument(
        "--weight-decay",
        type=float,
        default=0.0,
        help="Weight decay (default: 0.0)"
    )
    
    parser.add_argument(
        "--scheduler",
        type=str,
        default=None,
        choices=[None, "cosine", "reduce_on_plateau"],
        help="Learning rate scheduler (default: None)"
    )
    
    # Hardware parameters
    parser.add_argument(
        "--gpus",
        type=int,
        default=None,
        help="Number of GPUs to use (default: None, use CPU)"
    )
    
    parser.add_argument(
        "--accelerator",
        type=str,
        default=None,
        choices=[None, "cpu", "gpu", "mps"],
        help="Accelerator to use (default: None, auto-detect)"
    )
    
    parser.add_argument(
        "--precision",
        type=str,
        default="32-true",
        choices=["32-true", "16-mixed", "bf16-mixed"],
        help="Precision to use for training (default: 32-true)"
    )
    
    # Other parameters
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)"
    )
    
    parser.add_argument(
        "--early-stopping",
        action="store_true",
        help="Enable early stopping"
    )
    
    parser.add_argument(
        "--patience",
        type=int,
        default=10,
        help="Patience for early stopping (default: 10)"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="lightning_outputs",
        help="Output directory for logs and checkpoints (default: lightning_outputs)"
    )
    
    # Normalization options
    parser.add_argument(
        "--use-gate-norm",
        action="store_true",
        help="Apply GateNorm to the gating pathway"
    )
    
    parser.add_argument(
        "--pre-norm",
        action="store_true",
        help="Apply LayerNorm before the gating unit"
    )
    
    parser.add_argument(
        "--post-norm",
        action="store_true",
        help="Apply LayerNorm after the gating unit"
    )
    
    parser.add_argument(
        "--norm-eps",
        type=float,
        default=1e-5,
        help="Epsilon value for normalization layers (default: 1e-5)"
    )
    
    return parser.parse_args()


def main():
    """Main function to train paGating unit with PyTorch Lightning."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Set random seeds for reproducibility
    pl.seed_everything(args.seed)
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Convert alpha to float if it's not "learnable"
    alpha = args.alpha
    if alpha != "learnable":
        try:
            alpha = float(alpha)
            if not 0 <= alpha <= 1:
                print(f"Error: Alpha must be between 0 and 1, got {alpha}")
                sys.exit(1)
        except ValueError:
            print(f"Error: Alpha must be a float between 0 and 1 or 'learnable', got {alpha}")
            sys.exit(1)
    
    # Get normalization options
    use_gate_norm = args.use_gate_norm
    pre_norm = args.pre_norm
    post_norm = args.post_norm
    norm_eps = args.norm_eps
    
    # Create training configuration
    config = {
        "unit": args.unit,
        "input_dim": args.input_dim,
        "output_dim": args.output_dim,
        "alpha": alpha,
        "optimizer": args.optimizer,
        "lr": args.lr,
        "weight_decay": args.weight_decay,
        "scheduler": args.scheduler,
        "max_epochs": args.epochs,
        "use_gate_norm": use_gate_norm,
        "pre_norm": pre_norm,
        "post_norm": post_norm,
        "norm_eps": norm_eps
    }
    
    # Print training configuration
    print(f"\n{'=' * 50}")
    print(f"paGating Lightning Training")
    print(f"{'=' * 50}")
    print(f"Unit: {args.unit}")
    print(f"Alpha: {alpha}")
    print(f"Input dimension: {args.input_dim}")
    print(f"Output dimension: {args.output_dim}")
    print(f"Batch size: {args.batch_size}")
    print(f"Epochs: {args.epochs}")
    print(f"Optimizer: {args.optimizer}")
    print(f"Learning rate: {args.lr}")
    if use_gate_norm:
        print(f"Using GateNorm for gating pathway")
    if pre_norm:
        print(f"Using pre-normalization (LayerNorm)")
    if post_norm:
        print(f"Using post-normalization (LayerNorm)")
    print(f"{'=' * 50}\n")
    
    # Create synthetic datasets
    print("Generating synthetic datasets...")
    train_dataset = SyntheticRegressionDataset(
        num_samples=args.train_samples,
        input_dim=args.input_dim,
        output_dim=args.output_dim,
        noise_level=args.noise_level,
        seed=args.seed
    )
    
    val_dataset = SyntheticRegressionDataset(
        num_samples=args.val_samples,
        input_dim=args.input_dim,
        output_dim=args.output_dim,
        noise_level=args.noise_level,
        seed=args.seed + 1  # Different seed for validation
    )
    
    test_dataset = SyntheticRegressionDataset(
        num_samples=args.test_samples,
        input_dim=args.input_dim,
        output_dim=args.output_dim,
        noise_level=args.noise_level,
        seed=args.seed + 2  # Different seed for test
    )
    
    # Create data loaders
    train_loader = data.DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=4,
        pin_memory=True
    )
    
    val_loader = data.DataLoader(
        val_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=4,
        pin_memory=True
    )
    
    test_loader = data.DataLoader(
        test_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=4,
        pin_memory=True
    )
    
    # Initialize model
    model = paGatingModule(config)
    
    # Create logger
    experiment_name = f"{args.unit}_alpha{alpha}_{args.optimizer}_lr{args.lr}"
    logger = TensorBoardLogger(
        save_dir=args.output_dir,
        name="logs",
        version=experiment_name
    )
    
    # Define callbacks
    callbacks = []
    
    # Add checkpoint callback
    checkpoint_callback = ModelCheckpoint(
        dirpath=os.path.join(args.output_dir, "checkpoints", experiment_name),
        filename="{epoch:02d}-{val_loss:.4f}",
        save_top_k=3,
        monitor="val_loss",
        mode="min"
    )
    callbacks.append(checkpoint_callback)
    
    # Add early stopping callback if enabled
    if args.early_stopping:
        early_stopping_callback = EarlyStopping(
            monitor="val_loss",
            patience=args.patience,
            mode="min"
        )
        callbacks.append(early_stopping_callback)
    
    # Add learning rate monitor if using a scheduler
    if args.scheduler:
        lr_monitor = LearningRateMonitor(logging_interval="epoch")
        callbacks.append(lr_monitor)
    
    # Create trainer
    trainer = pl.Trainer(
        max_epochs=args.epochs,
        logger=logger,
        callbacks=callbacks,
        deterministic=True,
        accelerator=args.accelerator,
        devices=args.gpus if args.gpus else "auto",
        precision=args.precision,
        log_every_n_steps=10
    )
    
    # Train model
    print("\nStarting training...")
    trainer.fit(model, train_loader, val_loader)
    
    # Test model
    print("\nEvaluating on test set...")
    test_result = trainer.test(model, test_loader, verbose=True)
    
    # Print final results
    print(f"\n{'=' * 50}")
    print(f"Training completed!")
    print(f"{'=' * 50}")
    print(f"Best validation loss: {checkpoint_callback.best_model_score:.6f}")
    print(f"Test loss: {test_result[0]['test_loss']:.6f}")
    
    # Print alpha if learnable
    if alpha == "learnable":
        final_alpha = model.model.get_alpha().item()
        print(f"Final alpha value: {final_alpha:.6f}")
    
    print(f"Model saved to: {checkpoint_callback.best_model_path}")
    print(f"{'=' * 50}")
    
    return test_result


if __name__ == "__main__":
    main() 