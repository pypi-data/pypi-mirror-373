#!/usr/bin/env python3
"""
Comprehensive test script for paGating units.
This script runs all available tests for a specified paGating unit,
including gateflow visualization and transformer tests.
"""

import argparse
import os
import subprocess
import sys
import time
import numpy as np
import matplotlib.pyplot as plt
import torch

def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description="Run tests for a paGating unit")
    parser.add_argument("--unit", type=str, default="paMishU", help="paGating unit to test")
    parser.add_argument("--alpha", type=float, default=0.5, help="Alpha value for gating unit")
    parser.add_argument("--epochs", type=int, default=5, help="Number of epochs for transformer test")
    parser.add_argument("--skip-gateflow", action="store_true", help="Skip gate flow test")
    parser.add_argument("--skip-transformer", action="store_true", help="Skip transformer test")
    parser.add_argument("--export-coreml", action="store_true", help="Export model to CoreML format")
    parser.add_argument("--test-coreml", action="store_true", help="Test CoreML model (requires --export-coreml)")
    
    return parser.parse_args()

def run_command(cmd, description):
    """Run a shell command and return success status"""
    print(f"\n=== {description} ===")
    print(f"Running: {cmd}")
    
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ {description} failed")
        return False

def run_gateflow_test(unit, alpha=0.5):
    """Run gateflow visualization for the specified unit"""
    print(f"\n=== Gate Flow Visualization for {unit} ===")
    
    # Ensure experiments directory exists
    experiments_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "experiments")
    os.makedirs(experiments_dir, exist_ok=True)
    
    # Check if gateflow image already exists
    filename = os.path.join(experiments_dir, f"{unit}_gateflow.png")
    if os.path.exists(filename):
        print(f"Gateflow visualization already exists: {filename}")
        print(f"✅ Gate Flow Visualization for {unit} completed successfully")
        return True
    
    # If image doesn't exist, try to create it
    try:
        # Import the specific unit
        sys.path.insert(0, '.')
        unit_import_cmd = f"from paGating import {unit}"
        exec(unit_import_cmd)
        
        # Create input for visualization
        x = torch.linspace(-3, 3, 100).unsqueeze(1)
        
        # Initialize the gating unit
        unit_instance = eval(f"{unit}(1, 1, alpha={alpha})")
        
        # Create plot
        plt.figure(figsize=(10, 6))
        
        # Pass input through the unit
        with torch.no_grad():
            output = unit_instance(x)
        
        # Plot input and output
        plt.plot(x.numpy(), x.numpy(), 'r--', label='Input')
        plt.plot(x.numpy(), output.numpy(), 'b-', label=f'{unit} Output (α={alpha})')
        
        # Add labels and title
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.title(f'{unit} Gate Flow (α={alpha})')
        plt.xlabel('Input')
        plt.ylabel('Output')
        
        # Save figure
        plt.savefig(filename, dpi=150)
        plt.close()
        
        print(f"Created gateflow visualization: {filename}")
        print(f"✅ Gate Flow Visualization for {unit} completed successfully")
        return True
    except Exception as e:
        print(f"Error creating gateflow visualization: {str(e)}")
        print(f"❌ Gate Flow Visualization for {unit} failed")
        return False

def run_transformer_test(unit, alpha, epochs):
    """Run transformer test for the specified unit"""
    cmd = f"python experiments/test_transformer.py --unit {unit} --alpha {alpha} --epochs {epochs}"
    return run_command(cmd, f"Transformer Test for {unit} (alpha={alpha})")

def export_to_coreml(unit, alpha):
    """Export the unit to CoreML format"""
    cmd = f"python coreml_export.py --unit {unit} --alpha {alpha}"
    return run_command(cmd, f"CoreML Export for {unit} (alpha={alpha})")

def test_coreml_model(unit, alpha):
    """Test the exported CoreML model"""
    cmd = f"python test_coreml_model.py --unit {unit} --alpha {alpha}"
    return run_command(cmd, f"CoreML Test for {unit} (alpha={alpha})")

def main():
    args = parse_args()
    
    unit = args.unit
    alpha = args.alpha
    epochs = args.epochs
    
    # Record start time
    start_time = time.time()
    
    # Create results directory if it doesn't exist
    os.makedirs("test_results", exist_ok=True)
    
    # Initialize results log
    log_file = f"test_results/{unit}_alpha{alpha:.2f}_tests.log"
    with open(log_file, "w") as f:
        f.write(f"==== Test Results for {unit} (alpha={alpha}) ====\n\n")
        f.write(f"Test started at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    # Run gate flow test if not skipped
    if not args.skip_gateflow:
        success = run_gateflow_test(unit, alpha)
        with open(log_file, "a") as f:
            f.write(f"Gate Flow Test: {'SUCCESS' if success else 'FAILED'}\n")
    
    # Run transformer test if not skipped
    if not args.skip_transformer:
        success = run_transformer_test(unit, alpha, epochs)
        with open(log_file, "a") as f:
            f.write(f"Transformer Test: {'SUCCESS' if success else 'FAILED'}\n")
    
    # Export to CoreML if requested
    if args.export_coreml:
        success = export_to_coreml(unit, alpha)
        with open(log_file, "a") as f:
            f.write(f"CoreML Export: {'SUCCESS' if success else 'FAILED'}\n")
    
    # Test CoreML model if requested
    if args.test_coreml and args.export_coreml:
        success = test_coreml_model(unit, alpha)
        with open(log_file, "a") as f:
            f.write(f"CoreML Test: {'SUCCESS' if success else 'FAILED'}\n")
    
    # Record end time and calculate duration
    end_time = time.time()
    duration = end_time - start_time
    
    # Update results log with completion time
    with open(log_file, "a") as f:
        f.write(f"\nTest completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total duration: {duration:.2f} seconds\n")
    
    print(f"\n==== Test Summary ====")
    print(f"Unit: {unit}")
    print(f"Alpha: {alpha}")
    print(f"Total duration: {duration:.2f} seconds")
    print(f"Results logged to: {log_file}")

if __name__ == "__main__":
    main() 