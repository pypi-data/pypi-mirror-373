#!/usr/bin/env python3
"""
Data Download Script for paGating Framework

This script downloads and sets up all required datasets for the paGating experiments.
"""

import os
import sys
import urllib.request
import tarfile
import zipfile
from pathlib import Path

def download_file(url, filename, description):
    """Download a file with progress bar."""
    print(f"Downloading {description}...")
    
    def progress_hook(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            percent = min(100, (downloaded * 100) // total_size)
            sys.stdout.write(f"\r{description}: {percent}% ({downloaded // 1024 // 1024}MB)")
            sys.stdout.flush()
    
    urllib.request.urlretrieve(url, filename, progress_hook)
    print(f"\n✅ Downloaded {description}")

def setup_cifar10():
    """Download and extract CIFAR-10 dataset."""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    cifar_url = "https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz"
    cifar_file = data_dir / "cifar-10-python.tar.gz"
    
    if not cifar_file.exists():
        download_file(cifar_url, cifar_file, "CIFAR-10 dataset")
        
        # Extract the dataset
        print("Extracting CIFAR-10...")
        with tarfile.open(cifar_file, 'r:gz') as tar:
            tar.extractall(data_dir)
        print("✅ CIFAR-10 extracted")
    else:
        print("✅ CIFAR-10 already exists")

def setup_directories():
    """Create necessary directories."""
    directories = [
        "data",
        "logs", 
        ".cache",
        "lightning_outputs",
        "coreml_models", 
        "benchmark_temp",
        "results",
        "models"
    ]
    
    for dir_name in directories:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"✅ Created directory: {dir_name}")

def main():
    """Main function to set up all data."""
    print("🚀 Setting up paGating data directories and datasets...")
    
    # Create directories
    setup_directories()
    
    # Download datasets
    setup_cifar10()
    
    print("\n🎉 Data setup complete!")
    print("\nNext steps:")
    print("1. Run experiments: python comprehensive_experiments_for_paper.py")
    print("2. View results: python dashboard.py")
    print("3. Export models: python scripts/export_models.py")

if __name__ == "__main__":
    main() 