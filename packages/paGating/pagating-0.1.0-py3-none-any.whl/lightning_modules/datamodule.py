"""
DataModule for CIFAR-10 dataset using PyTorch Lightning.
"""

import os
from typing import Optional, Dict, Any

import torch
from torch.utils.data import DataLoader, random_split
import torchvision
import torchvision.transforms as transforms
import pytorch_lightning as pl


class CIFAR10DataModule(pl.LightningDataModule):
    """
    PyTorch Lightning DataModule for CIFAR-10 dataset.
    
    This DataModule handles downloading, transforming, and preparing the CIFAR-10 dataset
    for training, validation, and testing.
    
    Args:
        data_dir: Directory where the dataset should be stored (default: 'data/cifar10')
        batch_size: Batch size for training and validation (default: 128)
        num_workers: Number of workers for DataLoader (default: 4)
        val_split: Proportion of training data to use for validation (default: 0.1)
        seed: Random seed for reproducibility (default: 42)
        pin_memory: Whether to pin memory in DataLoader (default: True)
    """
    
    def __init__(
        self,
        data_dir: str = 'data/cifar10',
        batch_size: int = 128,
        num_workers: int = 4,
        val_split: float = 0.1,
        seed: int = 42,
        pin_memory: bool = True,
    ):
        super().__init__()
        self.data_dir = data_dir
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.val_split = val_split
        self.seed = seed
        self.pin_memory = pin_memory
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Dataset statistics for normalization
        self.mean = (0.4914, 0.4822, 0.4465)
        self.std = (0.2470, 0.2435, 0.2616)
        
        # Datasets
        self.train_dataset = None
        self.val_dataset = None
        self.test_dataset = None
        
        # Set up transformations
        self._setup_transforms()
    
    def _setup_transforms(self):
        """Set up data transformations for training and testing."""
        # Training transformations with data augmentation
        self.train_transforms = transforms.Compose([
            transforms.RandomCrop(32, padding=4),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize(self.mean, self.std)
        ])
        
        # Testing transformations (no augmentation)
        self.test_transforms = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(self.mean, self.std)
        ])
    
    def prepare_data(self):
        """
        Download the CIFAR-10 dataset if not already available.
        This method is called only once on the main process.
        """
        # Download training data if not already available
        torchvision.datasets.CIFAR10(
            root=self.data_dir, 
            train=True, 
            download=True
        )
        
        # Download test data if not already available
        torchvision.datasets.CIFAR10(
            root=self.data_dir, 
            train=False, 
            download=True
        )
    
    def setup(self, stage: Optional[str] = None):
        """
        Setup datasets for training, validation, and testing.
        This method is called on every process in distributed training.
        
        Args:
            stage: Stage for which to set up the data ('fit', 'validate', 'test')
        """
        # Load training data if needed for training or validation
        if stage == 'fit' or stage is None:
            full_train_dataset = torchvision.datasets.CIFAR10(
                root=self.data_dir,
                train=True,
                transform=self.train_transforms
            )
            
            # Split into training and validation
            train_size = int((1 - self.val_split) * len(full_train_dataset))
            val_size = len(full_train_dataset) - train_size
            
            # Use random_split with generator for reproducibility
            generator = torch.Generator().manual_seed(self.seed)
            self.train_dataset, self.val_dataset = random_split(
                full_train_dataset, 
                [train_size, val_size], 
                generator=generator
            )
            
            # For validation data, apply test transforms (no augmentation)
            # Create a dataset that applies the correct transforms
            self.val_dataset = _TransformedSubset(
                self.val_dataset, 
                torchvision.datasets.CIFAR10(
                    root=self.data_dir,
                    train=True,
                    transform=self.test_transforms
                )
            )
        
        # Load test data if needed for testing
        if stage == 'test' or stage is None:
            self.test_dataset = torchvision.datasets.CIFAR10(
                root=self.data_dir,
                train=False,
                transform=self.test_transforms
            )
    
    def train_dataloader(self):
        """Return DataLoader for training data."""
        return DataLoader(
            self.train_dataset,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=self.num_workers,
            pin_memory=self.pin_memory
        )
    
    def val_dataloader(self):
        """Return DataLoader for validation data."""
        return DataLoader(
            self.val_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_workers,
            pin_memory=self.pin_memory
        )
    
    def test_dataloader(self):
        """Return DataLoader for test data."""
        return DataLoader(
            self.test_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_workers,
            pin_memory=self.pin_memory
        )
    
    @staticmethod
    def add_datamodule_specific_args(parent_parser):
        """
        Add DataModule specific arguments to the parser.
        
        Args:
            parent_parser: ArgumentParser to add arguments to
            
        Returns:
            ArgumentParser with added arguments
        """
        parser = parent_parser.add_argument_group("CIFAR10DataModule")
        parser.add_argument("--data_dir", type=str, default="data/cifar10")
        parser.add_argument("--batch_size", type=int, default=128)
        parser.add_argument("--num_workers", type=int, default=4)
        parser.add_argument("--val_split", type=float, default=0.1)
        return parent_parser


class _TransformedSubset(torch.utils.data.Dataset):
    """
    Helper class to apply transforms to a subset of a dataset.
    This is needed because random_split doesn't preserve transforms.
    """
    
    def __init__(self, subset, dataset_with_transforms):
        self.subset = subset
        self.dataset_with_transforms = dataset_with_transforms
        
    def __getitem__(self, index):
        # Get original data from the subset
        _, target = self.subset[index]
        
        # Get the global index in the original dataset
        global_index = self.subset.indices[index]
        
        # Get the transformed data from the transformed dataset
        data, _ = self.dataset_with_transforms[global_index]
        
        return data, target
    
    def __len__(self):
        return len(self.subset) 