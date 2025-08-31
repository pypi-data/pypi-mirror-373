"""
PyTorch Lightning data module for CIFAR-10 dataset.

This module handles the loading, preprocessing, and preparation of the CIFAR-10 dataset
for training and evaluation.
"""

import os
from typing import Optional, Dict, Any, Callable, Tuple

import torch
from torch.utils.data import DataLoader, random_split
import torchvision
import torchvision.transforms as transforms
import pytorch_lightning as pl


class CIFAR10DataModule(pl.LightningDataModule):
    """
    PyTorch Lightning data module for the CIFAR-10 dataset.
    
    This module handles downloading, transforming, and loading the CIFAR-10 dataset.
    """
    
    def __init__(
        self,
        data_dir: str = "./data",
        batch_size: int = 128,
        num_workers: int = 4,
        pin_memory: bool = True,
        val_split: float = 0.1,
        seed: int = 42,
    ):
        """
        Initialize the CIFAR-10 data module.
        
        Args:
            data_dir: Directory to store the dataset
            batch_size: Batch size for training and evaluation
            num_workers: Number of workers for data loading
            pin_memory: Whether to pin memory for faster data transfer to GPU
            val_split: Fraction of training data to use for validation
            seed: Random seed for reproducibility
        """
        super().__init__()
        self.save_hyperparameters()
        
        self.data_dir = data_dir
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.pin_memory = pin_memory
        self.val_split = val_split
        self.seed = seed
        
        # Datasets
        self.train_dataset = None
        self.val_dataset = None
        self.test_dataset = None
        
        # Define transforms
        self.train_transforms = transforms.Compose([
            transforms.RandomCrop(32, padding=4),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2470, 0.2435, 0.2616)),
        ])
        
        self.test_transforms = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2470, 0.2435, 0.2616)),
        ])
    
    def prepare_data(self) -> None:
        """
        Download the CIFAR-10 dataset if not already available.
        
        This method is called only once on the main process.
        """
        # Download
        torchvision.datasets.CIFAR10(root=self.data_dir, train=True, download=True)
        torchvision.datasets.CIFAR10(root=self.data_dir, train=False, download=True)
    
    def setup(self, stage: Optional[str] = None) -> None:
        """
        Setup the dataset splits for training, validation, and testing.
        
        Args:
            stage: Either 'fit', 'validate', 'test', or None
        """
        # Load train dataset
        if stage == "fit" or stage is None:
            cifar_full = torchvision.datasets.CIFAR10(
                root=self.data_dir, train=True, transform=self.train_transforms
            )
            
            # Split into train and validation sets
            val_size = int(len(cifar_full) * self.val_split)
            train_size = len(cifar_full) - val_size
            
            # Use random_split with generator for reproducibility
            generator = torch.Generator().manual_seed(self.seed)
            self.train_dataset, self.val_dataset = random_split(
                cifar_full, [train_size, val_size], generator=generator
            )
            
            # Override validation set transforms
            self.val_dataset.dataset.transform = self.test_transforms
        
        # Load test dataset
        if stage == "test" or stage is None:
            self.test_dataset = torchvision.datasets.CIFAR10(
                root=self.data_dir, train=False, transform=self.test_transforms
            )
    
    def train_dataloader(self) -> DataLoader:
        """
        Create the training data loader.
        
        Returns:
            DataLoader for training
        """
        return DataLoader(
            self.train_dataset,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=self.num_workers,
            pin_memory=self.pin_memory,
            persistent_workers=self.num_workers > 0,
        )
    
    def val_dataloader(self) -> DataLoader:
        """
        Create the validation data loader.
        
        Returns:
            DataLoader for validation
        """
        return DataLoader(
            self.val_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_workers,
            pin_memory=self.pin_memory,
            persistent_workers=self.num_workers > 0,
        )
    
    def test_dataloader(self) -> DataLoader:
        """
        Create the test data loader.
        
        Returns:
            DataLoader for testing
        """
        return DataLoader(
            self.test_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_workers,
            pin_memory=self.pin_memory,
            persistent_workers=self.num_workers > 0,
        )
    
    @staticmethod
    def get_classes() -> Tuple[str, ...]:
        """
        Get the class names for CIFAR-10.
        
        Returns:
            Tuple of class names
        """
        return (
            'airplane', 'automobile', 'bird', 'cat', 'deer',
            'dog', 'frog', 'horse', 'ship', 'truck'
        ) 