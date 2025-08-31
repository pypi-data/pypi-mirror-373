#!/usr/bin/env python
"""
Compare performance of different paGating activation units.

This script compares the test loss of different paGating activation units
on a regression task using PyTorch Lightning.
"""

import os
import sys
import subprocess
import matplotlib.pyplot as plt
import numpy as np
import argparse
import json
from pathlib import Path

# Constants for the experiment
ALPHA = 0.5
EPOCHS = 50
BATCH_SIZE = 64
LEARNING_RATE = 0.001

def parse_args():
    parser = argparse.ArgumentParser(description='Compare different paGating units')
    parser.add_argument('--results_dir', type=str, default='results', 
                        help='Directory to store results and plots')
    parser.add_argument('--alpha', type=float, default=ALPHA, 
                        help='Alpha value for paGating units')
    return parser.parse_args()

def run_training(unit, alpha=ALPHA, epochs=EPOCHS, batch_size=BATCH_SIZE, lr=LEARNING_RATE):
    """
    Run training using the specified paGating unit and return results.
    This is a placeholder for actual training logic.
    
    Args:
        unit (str): The paGating unit to use
        alpha (float): Alpha parameter for the unit
        epochs (int): Number of training epochs
        batch_size (int): Batch size for training
        lr (float): Learning rate
        
    Returns:
        dict: Dictionary containing training and test metrics
    """
    # This is a placeholder for the actual training logic
    # In a real implementation, you would import your training module and call it
    
    # Simulated results (replace with actual training)
    import random
    random.seed(42)  # For reproducibility
    
    # Simulate different performance for different units
    base_loss = 0.1 + random.uniform(-0.05, 0.05)
    
    # Different units will have different base performances in this simulation
    if unit == 'paGLU':
        base_loss *= 0.95
    elif unit == 'paGELU':
        base_loss *= 1.05
    elif unit == 'paMishU':
        base_loss *= 1.0
    elif unit == 'paReGLU':
        base_loss *= 1.02
    elif unit == 'paSiLU':
        base_loss *= 0.98
    
    return {
        'train_loss': base_loss * 1.2,
        'test_loss': base_loss,
        'train_acc': 100 - (base_loss * 100),
        'test_acc': 95 - (base_loss * 50)
    }

def compare_units(alpha=ALPHA, epochs=EPOCHS, batch_size=BATCH_SIZE, lr=LEARNING_RATE, results_dir='results'):
    """
    Compare different paGating units by running training and plotting results.
    
    Args:
        alpha (float): Alpha parameter for the units
        epochs (int): Number of training epochs
        batch_size (int): Batch size for training
        lr (float): Learning rate
        results_dir (str): Directory to save results and plots
    """
    # List of units to compare
    units = ['paGLU', 'paGTU', 'paSwishU', 'paReGLU', 'paGELU', 'paMishU', 'paSiLU']
    
    # Collect results
    results = {}
    for unit in units:
        print(f"Training with {unit}, alpha={alpha}...")
        metrics = run_training(unit, alpha, epochs, batch_size, lr)
        results[unit] = metrics
        print(f"  Test loss: {metrics['test_loss']:.4f}, Test acc: {metrics['test_acc']:.2f}%")
    
    # Plot results
    plt.figure(figsize=(10, 6))
    
    # Extract test losses for plotting
    test_losses = [results[unit]['test_loss'] for unit in units]
    
    # Create bar plot
    plt.bar(units, test_losses, color='skyblue')
    plt.xlabel('paGating Units')
    plt.ylabel('Test Loss')
    plt.title(f'Comparison of paGating Units (α={alpha}, epochs={epochs})')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    # Ensure the results directory exists
    os.makedirs(results_dir, exist_ok=True)
    
    # Save figure to the specified directory
    plot_path = os.path.join(results_dir, 'unit_comparison.png')
    plt.savefig(plot_path)
    print(f"Plot saved to {plot_path}")
    
    # Save results to JSON for further analysis
    results_path = os.path.join(results_dir, 'unit_comparison_results.json')
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {results_path}")

def main():
    args = parse_args()
    
    # Create results directory if it doesn't exist
    os.makedirs(args.results_dir, exist_ok=True)
    
    # Run comparison with specified parameters
    compare_units(
        alpha=args.alpha, 
        epochs=EPOCHS, 
        batch_size=BATCH_SIZE, 
        lr=LEARNING_RATE,
        results_dir=args.results_dir
    )

if __name__ == '__main__':
    main() 