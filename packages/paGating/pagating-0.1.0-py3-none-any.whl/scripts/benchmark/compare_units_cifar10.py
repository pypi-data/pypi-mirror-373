#!/usr/bin/env python
"""
Compare different paGating units on CIFAR-10.

This script runs short training sessions for each paGating unit on the CIFAR-10 dataset
and compares their performance.
"""

import os
import argparse
import subprocess
import json
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Define the units to compare
UNITS = [
    "paGLU",
    "paGTU", 
    "paSwishU",
    "paReGLU",
    "paGELU",
    "paMishU",
    "paSiLU"
]

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Compare paGating units on CIFAR-10")
    
    parser.add_argument("--epochs", type=int, default=2,
                       help="Number of epochs for each unit (default: 2)")
    
    parser.add_argument("--batch_size", type=int, default=128,
                       help="Batch size for training (default: 128)")
    
    parser.add_argument("--alpha", type=float, default=0.5,
                       help="Alpha value for all units (default: 0.5)")
    
    parser.add_argument("--accelerator", type=str, default="cpu",
                        choices=["cpu", "gpu", "mps", "auto"],
                        help="Accelerator to use (default: cpu)")
    
    parser.add_argument("--output_dir", type=str, default="unit_comparison",
                       help="Directory to store results (default: unit_comparison)")
    
    return parser.parse_args()


def train_unit(unit, epochs, batch_size, alpha, accelerator):
    """Train a single unit and return the results."""
    cmd = [
        "python", "train_cifar10.py",
        "--unit", unit,
        "--alpha", str(alpha),
        "--epochs", str(epochs),
        "--batch_size", str(batch_size),
        "--accelerator", accelerator,
        "--log_dir", f"comparison_logs/{unit}",
        "--save_for_dashboard",
        "--dashboard_log_dir", "logs/cifar10"
    ]
    
    print(f"Training {unit} with alpha={alpha}...")
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    
    # Parse the output to get the results
    output = stdout.decode()
    lines = output.strip().split('\n')
    
    results = {}
    for line in lines:
        if "Best validation accuracy" in line:
            val_acc = float(line.split(":")[1].strip())
            results["val_acc"] = val_acc
        elif "Test accuracy" in line:
            test_acc = float(line.split(":")[1].strip())
            results["test_acc"] = test_acc
    
    if "val_acc" not in results or "test_acc" not in results:
        print(f"Warning: Could not parse results for {unit}")
        print(f"Output: {output}")
        results = {"val_acc": 0.0, "test_acc": 0.0}
    
    return results


def compare_units(args):
    """Compare all units and generate plots."""
    os.makedirs(args.output_dir, exist_ok=True)
    
    results = {}
    for unit in UNITS:
        unit_results = train_unit(
            unit=unit,
            epochs=args.epochs,
            batch_size=args.batch_size,
            alpha=args.alpha,
            accelerator=args.accelerator
        )
        results[unit] = unit_results
    
    # Save results to JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = os.path.join(args.output_dir, f"results_{timestamp}.json")
    with open(results_file, "w") as f:
        json.dump(results, f, indent=4)
    
    # Create a DataFrame for plotting
    data = []
    for unit, unit_results in results.items():
        data.append({
            "Unit": unit,
            "Validation Accuracy": unit_results["val_acc"],
            "Test Accuracy": unit_results["test_acc"]
        })
    
    df = pd.DataFrame(data)
    
    # Plot results
    plt.figure(figsize=(12, 8))
    
    x = np.arange(len(UNITS))
    width = 0.35
    
    plt.bar(x - width/2, df["Validation Accuracy"], width, label="Validation Accuracy")
    plt.bar(x + width/2, df["Test Accuracy"], width, label="Test Accuracy")
    
    plt.xlabel("paGating Unit")
    plt.ylabel("Accuracy")
    plt.title(f"CIFAR-10 Performance Comparison (alpha={args.alpha}, epochs={args.epochs})")
    plt.xticks(x, UNITS)
    plt.ylim(0, 1.0)
    plt.legend()
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    
    plot_file = os.path.join(args.output_dir, f"comparison_{timestamp}.png")
    plt.savefig(plot_file)
    plt.close()
    
    print(f"Results saved to {results_file}")
    print(f"Plot saved to {plot_file}")
    

if __name__ == "__main__":
    args = parse_args()
    compare_units(args) 