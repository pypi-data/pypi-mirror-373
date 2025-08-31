"""
CIFAR-10 DataModule for PyTorch Lightning.

This module provides a DataModule for loading and processing the CIFAR-10 dataset
with optional data augmentation.
"""

import os
from typing import Optional, Tuple

import torch
from torch.utils.data import DataLoader, random_split
import torchvision
import torchvision.transforms as transforms
import pytorch_lightning as pl


class CIFAR10DataModule(pl.LightningDataModule):
    """
    PyTorch Lightning DataModule for the CIFAR-10 dataset.
    """
    
    def __init__(
        self,
        data_dir: str = "./data",
        batch_size: int = 64,
        num_workers: int = 4,
        pin_memory: bool = True,
        val_split: float = 0.1,
        seed: int = 42,
    ):
        """
        Initialize the DataModule.
        
        Args:
            data_dir: Directory to store the dataset
            batch_size: Batch size for training and evaluation
            num_workers: Number of workers for data loading
            pin_memory: Whether to pin memory in data loaders
            val_split: Fraction of training data to use for validation
            seed: Random seed for reproducibility
        """
        super().__init__()
        self.data_dir = data_dir
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.pin_memory = pin_memory
        self.val_split = val_split
        self.seed = seed
        
        # Define transformations
        self.train_transform = transforms.Compose([
            transforms.RandomCrop(32, padding=4),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2470, 0.2435, 0.2616)),
        ])
        
        self.test_transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2470, 0.2435, 0.2616)),
        ])
        
        # Define datasets
        self.cifar_train = None
        self.cifar_val = None
        self.cifar_test = None
    
    def prepare_data(self) -> None:
        """
        Download the CIFAR-10 dataset if not already available.
        """
        # Download
        torchvision.datasets.CIFAR10(self.data_dir, train=True, download=True)
        torchvision.datasets.CIFAR10(self.data_dir, train=False, download=True)
    
    def setup(self, stage: Optional[str] = None) -> None:
        """
        Set up the datasets for training, validation, and testing.
        
        Args:
            stage: Current stage ('fit', 'validate', 'test', or 'predict')
        """
        # Load the training dataset
        train_dataset = torchvision.datasets.CIFAR10(
            self.data_dir, train=True, transform=self.train_transform
        )
        
        # Split into train and validation sets
        val_size = int(len(train_dataset) * self.val_split)
        train_size = len(train_dataset) - val_size
        
        # Set the random seed for reproducibility
        generator = torch.Generator().manual_seed(self.seed)
        
        self.cifar_train, self.cifar_val = random_split(
            train_dataset, [train_size, val_size], generator=generator
        )
        
        # Load the test dataset
        self.cifar_test = torchvision.datasets.CIFAR10(
            self.data_dir, train=False, transform=self.test_transform
        )
    
    def train_dataloader(self) -> DataLoader:
        """
        Create the training data loader.
        
        Returns:
            DataLoader for training
        """
        return DataLoader(
            self.cifar_train,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=self.num_workers,
            pin_memory=self.pin_memory,
        )
    
    def val_dataloader(self) -> DataLoader:
        """
        Create the validation data loader.
        
        Returns:
            DataLoader for validation
        """
        return DataLoader(
            self.cifar_val,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_workers,
            pin_memory=self.pin_memory,
        )
    
    def test_dataloader(self) -> DataLoader:
        """
        Create the test data loader.
        
        Returns:
            DataLoader for testing
        """
        return DataLoader(
            self.cifar_test,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_workers,
            pin_memory=self.pin_memory,
        ) 