"""
PyTorch Lightning DataModule for CIFAR-10 dataset.

This module provides a consistent interface for loading and preprocessing 
the CIFAR-10 dataset for training, validation, and testing.
"""

import torch
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms
import pytorch_lightning as pl
import os
from typing import Optional, Tuple


class CIFAR10DataModule(pl.LightningDataModule):
    """
    PyTorch Lightning DataModule for CIFAR-10 dataset.
    
    This module handles the downloading, preprocessing, and loading of the CIFAR-10
    dataset with standardized transformations and data loading utilities.
    """
    
    def __init__(
        self,
        data_dir: str = "./data",
        batch_size: int = 128,
        num_workers: int = 4,
        val_split: float = 0.1,
        seed: int = 42,
    ):
        """
        Initialize the CIFAR-10 data module.
        
        Args:
            data_dir (str): Directory to store the dataset.
            batch_size (int): Batch size for data loaders.
            num_workers (int): Number of workers for data loading.
            val_split (float): Proportion of training data to use for validation.
            seed (int): Random seed for reproducibility.
        """
        super().__init__()
        
        self.data_dir = data_dir
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.val_split = val_split
        self.seed = seed
        
        # Data mean and std for normalization
        self.mean = (0.4914, 0.4822, 0.4465)
        self.std = (0.2470, 0.2435, 0.2616)
        
        # Prepare transformations
        self.train_transforms = transforms.Compose([
            transforms.RandomCrop(32, padding=4),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize(self.mean, self.std),
        ])
        
        self.test_transforms = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(self.mean, self.std),
        ])
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize dataset placeholders
        self.cifar_train = None
        self.cifar_val = None
        self.cifar_test = None
    
    def prepare_data(self):
        """
        Download the CIFAR-10 dataset.
        
        This method is called only on a single GPU.
        """
        # Download dataset if not already downloaded
        datasets.CIFAR10(self.data_dir, train=True, download=True)
        datasets.CIFAR10(self.data_dir, train=False, download=True)
    
    def setup(self, stage: Optional[str] = None):
        """
        Set up the dataset for training, validation, and testing.
        
        Args:
            stage (str, optional): Current stage ('fit', 'validate', 'test').
        """
        # Load the dataset
        if stage == 'fit' or stage is None:
            cifar_full = datasets.CIFAR10(
                self.data_dir, train=True, transform=self.train_transforms
            )
            
            # Split into train and validation sets
            val_size = int(len(cifar_full) * self.val_split)
            train_size = len(cifar_full) - val_size
            
            # Use random_split to create the split
            generator = torch.Generator().manual_seed(self.seed)
            self.cifar_train, self.cifar_val = random_split(
                cifar_full, [train_size, val_size], generator=generator
            )
            
            # Update validation set transforms
            # We need to create a dataset with the correct transforms
            # This is a bit tricky since random_split returns a Subset
            self.cifar_val.dataset.transform = self.test_transforms
        
        if stage == 'test' or stage is None:
            self.cifar_test = datasets.CIFAR10(
                self.data_dir, train=False, transform=self.test_transforms
            )
    
    def train_dataloader(self):
        """Get training dataloader."""
        return DataLoader(
            self.cifar_train,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=self.num_workers,
            pin_memory=True,
        )
    
    def val_dataloader(self):
        """Get validation dataloader."""
        return DataLoader(
            self.cifar_val,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_workers,
            pin_memory=True,
        )
    
    def test_dataloader(self):
        """Get test dataloader."""
        return DataLoader(
            self.cifar_test,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_workers,
            pin_memory=True,
        )
    
    @staticmethod
    def get_num_classes():
        """Get the number of classes in CIFAR-10."""
        return 10
    
    @staticmethod
    def get_input_shape():
        """Get the input shape of CIFAR-10 images."""
        return (3, 32, 32)


# For testing the data module
if __name__ == "__main__":
    # Create data module
    dm = CIFAR10DataModule()
    
    # Prepare and setup
    dm.prepare_data()
    dm.setup()
    
    # Get a batch from the training dataloader
    train_loader = dm.train_dataloader()
    batch = next(iter(train_loader))
    
    # Print information
    x, y = batch
    print(f"Training data shape: {x.shape}")
    print(f"Training labels shape: {y.shape}")
    print(f"Data statistics: min={x.min().item():.4f}, max={x.max().item():.4f}, "
          f"mean={x.mean().item():.4f}, std={x.std().item():.4f}")
    
    # Check class distribution
    for i in range(10):
        count = (y == i).sum().item()
        print(f"Class {i}: {count} samples") 