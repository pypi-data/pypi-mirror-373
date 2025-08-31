#!/usr/bin/env python
"""
Compare performance of a paGating unit with different alpha values.

This script runs training for a specific paGating unit with different alpha 
values and compares their performance.
"""

import os
import sys
import subprocess
import matplotlib.pyplot as plt
import numpy as np

# Configuration
UNIT = "paMishU"  # The unit to test with different alpha values
ALPHAS = [0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0]  # Alpha values to test
EPOCHS = 5  # Number of epochs for each run

def run_training(unit, alpha, epochs=EPOCHS):
    """Run training for a specific unit and alpha value, and extract the test loss."""
    cmd = [
        "python", "train_lightning.py",
        "--unit", unit,
        "--alpha", str(alpha),
        "--accelerator", "mps",
        "--epochs", str(epochs),
        "--batch-size", "128"
    ]
    
    print(f"\nTraining {unit} with alpha={alpha}...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    output = result.stdout
    
    # Extract test loss from the output
    for line in output.split('\n'):
        if "Test loss:" in line:
            test_loss = float(line.split("Test loss:")[1].strip())
            return test_loss
    
    return None

def compare_alpha_values():
    """Compare performance of a paGating unit with different alpha values."""
    results = {}
    
    for alpha in ALPHAS:
        test_loss = run_training(UNIT, alpha)
        if test_loss is not None:
            results[alpha] = test_loss
            print(f"{UNIT} with alpha={alpha}: Test loss = {test_loss:.4f}")
    
    # Create a plot to visualize the results
    alphas = list(results.keys())
    losses = [results[alpha] for alpha in alphas]
    
    plt.figure(figsize=(10, 6))
    plt.plot(alphas, losses, 'o-', color='blue', linewidth=2, markersize=8)
    
    # Add the loss value near each point
    for i, (alpha, loss) in enumerate(zip(alphas, losses)):
        plt.text(
            alpha + 0.02,
            loss + 0.5,
            f'{loss:.2f}',
            ha='center',
            va='bottom'
        )
    
    plt.xlabel('Alpha Value')
    plt.ylabel('Test Loss')
    plt.title(f'Performance of {UNIT} with Different Alpha Values (Epochs={EPOCHS})')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(alphas)
    plt.tight_layout()
    
    # Save the figure to script directory regardless of where script is run from
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, f'{UNIT}_alpha_comparison.png')
    plt.savefig(output_path)
    print(f"Comparison chart saved as '{output_path}'")

if __name__ == "__main__":
    compare_alpha_values() 