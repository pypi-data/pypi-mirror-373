"""
CIFAR-10 DataModule for PyTorch Lightning.

This module provides a LightningDataModule for the CIFAR-10 dataset,
with standard transforms and configurable batch size.
"""

import os
from typing import Optional, Dict, Any

import torch
from torch.utils.data import DataLoader, random_split
from torchvision.datasets import CIFAR10
from torchvision import transforms
import pytorch_lightning as pl


class CIFAR10DataModule(pl.LightningDataModule):
    """
    PyTorch Lightning DataModule for the CIFAR-10 dataset.
    
    This DataModule handles downloading, preprocessing, and loading
    the CIFAR-10 dataset with appropriate transforms.
    
    Args:
        data_dir (str): Directory where the dataset is stored or should be downloaded to
        batch_size (int): Batch size for all dataloaders
        num_workers (int): Number of workers for all dataloaders
        val_split (float): Fraction of training data to use for validation
        pin_memory (bool): Whether to pin memory for all dataloaders
    """
    
    def __init__(
        self,
        data_dir: str = "data",
        batch_size: int = 128,
        num_workers: int = 4,
        val_split: float = 0.1,
        pin_memory: bool = True,
    ):
        super().__init__()
        
        self.data_dir = data_dir
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.val_split = val_split
        self.pin_memory = pin_memory
        
        # CIFAR-10 specific mean and std for normalization
        self.mean = (0.4914, 0.4822, 0.4465)
        self.std = (0.2470, 0.2435, 0.2616)
        
        # Sets up the transforms
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
        
        # Set to hold the datasets
        self.cifar_train = None
        self.cifar_val = None
        self.cifar_test = None
    
    def prepare_data(self):
        """
        Download data if needed.
        
        This method is called once by Lightning before distributed training starts.
        """
        # Download if not already done
        CIFAR10(self.data_dir, train=True, download=True)
        CIFAR10(self.data_dir, train=False, download=True)
    
    def setup(self, stage: Optional[str] = None):
        """
        Load and split datasets.
        
        This method is called by Lightning before each stage (fit/test/predict) begins.
        
        Args:
            stage (Optional[str]): Current stage ('fit', 'validate', 'test', or 'predict')
        """
        # Load datasets only if they haven't been loaded already
        if stage == 'fit' or stage is None:
            cifar_full = CIFAR10(self.data_dir, train=True, transform=self.train_transforms)
            
            # Calculate split sizes
            val_size = int(len(cifar_full) * self.val_split)
            train_size = len(cifar_full) - val_size
            
            # Split into train and validation sets
            self.cifar_train, self.cifar_val = random_split(
                cifar_full, 
                [train_size, val_size],
                generator=torch.Generator().manual_seed(42)  # For reproducibility
            )
            
            # Update validation transform
            self.cifar_val.dataset.transform = self.test_transforms
        
        if stage == 'test' or stage is None:
            self.cifar_test = CIFAR10(self.data_dir, train=False, transform=self.test_transforms)
    
    def train_dataloader(self):
        """Create the training dataloader."""
        return DataLoader(
            self.cifar_train,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=self.num_workers,
            pin_memory=self.pin_memory,
        )
    
    def val_dataloader(self):
        """Create the validation dataloader."""
        return DataLoader(
            self.cifar_val,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_workers,
            pin_memory=self.pin_memory,
        )
    
    def test_dataloader(self):
        """Create the test dataloader."""
        return DataLoader(
            self.cifar_test,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_workers,
            pin_memory=self.pin_memory,
        )
    
    def get_num_classes(self) -> int:
        """Return the number of classes in the dataset."""
        return 10


if __name__ == "__main__":
    # Simple test to verify the datamodule works
    datamodule = CIFAR10DataModule()
    datamodule.prepare_data()
    datamodule.setup()
    
    train_loader = datamodule.train_dataloader()
    val_loader = datamodule.val_dataloader()
    test_loader = datamodule.test_dataloader()
    
    batch = next(iter(train_loader))
    images, labels = batch
    
    print(f"Training set size: {len(datamodule.cifar_train)}")
    print(f"Validation set size: {len(datamodule.cifar_val)}")
    print(f"Test set size: {len(datamodule.cifar_test)}")
    print(f"Batch shape: {images.shape}")
    print(f"Labels shape: {labels.shape}") 