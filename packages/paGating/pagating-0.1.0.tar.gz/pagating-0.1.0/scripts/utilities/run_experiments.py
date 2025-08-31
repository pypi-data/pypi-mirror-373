#!/usr/bin/env python
"""
Unified Experiment Pipeline for paGating Units

This script runs a comprehensive set of experiments for paGating units:
1. Trains all units with learnable alpha
2. Runs GateNorm ablation studies on selected units
3. Ensures all metrics are properly saved for dashboard visualization
4. Launches the Streamlit dashboard to visualize results

Usage:
    python run_experiments.py [--skip-training] [--skip-dashboard]
"""

import os
import sys
import argparse
import subprocess
import time
from pathlib import Path
import json
from typing import List, Dict, Optional, Union, Tuple

# Define the paGating units to use in experiments
ALL_UNITS = ["paGLU", "paGTU", "paSwishU", "paReGLU", "paGELU", "paMishU", "paSiLU"]

# Units for GateNorm ablation study
GATENORM_UNITS = ["paGLU", "paGTU", "paMishU"]

# Base directory for logs
LOGS_DIR = "logs/cifar10"


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Run paGating experiments pipeline")
    parser.add_argument("--skip-training", action="store_true",
                      help="Skip training and only regenerate metrics/launch dashboard")
    parser.add_argument("--skip-dashboard", action="store_true",
                      help="Skip launching the dashboard")
    parser.add_argument("--epochs", type=int, default=10,
                      help="Number of epochs for training (default: 10)")
    parser.add_argument("--batch-size", type=int, default=128,
                      help="Batch size for training (default: 128)")
    parser.add_argument("--accelerator", type=str, default="mps",
                      choices=["cpu", "gpu", "mps", "auto"],
                      help="Accelerator to use for training (default: mps)")
    parser.add_argument("--force-retrain", action="store_true",
                      help="Force retraining even if metrics exist")
    parser.add_argument("--selected-units", type=str, nargs="+",
                      choices=ALL_UNITS, help="Only train specific units")
    parser.add_argument("--check-gatenorm-support", action="store_true",
                      help="Check if the train_cifar10.py script supports GateNorm")
    return parser.parse_args()


def check_metrics_exist(unit: str, is_learnable: bool = False, use_gate_norm: bool = False) -> bool:
    """
    Check if metrics already exist for a given configuration.
    
    Args:
        unit: Name of the paGating unit
        is_learnable: Whether alpha is learnable
        use_gate_norm: Whether GateNorm is used
    
    Returns:
        True if metrics exist, False otherwise
    """
    # Construct directory name with configuration details
    dir_name = unit
    if is_learnable:
        dir_name += "_learnable"
    if use_gate_norm:
        dir_name += "_gatenorm"
    
    metrics_file = os.path.join(LOGS_DIR, dir_name, "metrics.csv")
    return os.path.exists(metrics_file) and os.path.getsize(metrics_file) > 0


def check_gatenorm_support():
    """Check if the train_cifar10.py script supports the GateNorm argument."""
    try:
        # Run the script with --help and capture the output
        result = subprocess.run(
            ["python", "train_cifar10.py", "--help"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        
        # Check if the output contains reference to gate_norm or use_gate_norm
        help_text = result.stdout.lower()
        return "gate_norm" in help_text or "use_gate_norm" in help_text
    except subprocess.CalledProcessError:
        # If the command fails, assume no support for safety
        return False


def run_training(
    unit: str, 
    epochs: int, 
    batch_size: int, 
    accelerator: str,
    is_learnable: bool = False, 
    use_gate_norm: bool = False,
    force_retrain: bool = False,
    supports_gatenorm: bool = False
) -> bool:
    """
    Run training for a specific configuration.
    
    Args:
        unit: Name of the paGating unit
        epochs: Number of epochs to train
        batch_size: Batch size for training
        accelerator: Accelerator to use (cpu, gpu, mps)
        is_learnable: Whether alpha is learnable
        use_gate_norm: Whether to use GateNorm
        force_retrain: Whether to force retraining even if metrics exist
        supports_gatenorm: Whether the train_cifar10.py script supports GateNorm
    
    Returns:
        True if training was successful, False otherwise
    """
    # Construct directory name with configuration details
    dir_name = unit
    if is_learnable:
        dir_name += "_learnable"
    if use_gate_norm:
        dir_name += "_gatenorm"
    
    # Skip if metrics already exist and force_retrain is False
    if not force_retrain and check_metrics_exist(unit, is_learnable, use_gate_norm):
        print(f"ℹ️ Metrics already exist for {dir_name}. Skipping training.")
        return True
    
    # Create command with appropriate arguments
    cmd = [
        "python", "train_cifar10.py",
        "--unit", unit,
        "--epochs", str(epochs),
        "--batch_size", str(batch_size),
        "--accelerator", accelerator,
        "--save_for_dashboard",
        "--dashboard_log_dir", LOGS_DIR
    ]
    
    # Add alpha argument based on whether it's learnable
    if is_learnable:
        cmd.extend(["--alpha", "learnable"])
    else:
        cmd.extend(["--alpha", "0.5"])
    
    # Add GateNorm flag if needed and supported
    if use_gate_norm and supports_gatenorm:
        cmd.append("--use_gate_norm")
    elif use_gate_norm and not supports_gatenorm:
        print(f"⚠️ GateNorm is not supported by train_cifar10.py, skipping GateNorm for {dir_name}")
    
    # Create directory for this configuration if it doesn't exist
    os.makedirs(os.path.join(LOGS_DIR, dir_name), exist_ok=True)
    
    # Print and run command
    print(f"🚀 Running: {' '.join(cmd)}")
    
    # Create a log file for this training run
    log_file_path = os.path.join(LOGS_DIR, f"{dir_name}_training.log")
    with open(log_file_path, "w") as log_file:
        # Run the command and capture output
        try:
            process = subprocess.run(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT,
                text=True,
                check=True
            )
            # Write the output to the log file
            log_file.write(process.stdout)
            print(f"✅ Training completed for {dir_name}")
            return True
        except subprocess.CalledProcessError as e:
            # Write the error output to the log file
            log_file.write(e.stdout)
            print(f"❌ Training failed for {dir_name}. See {log_file_path} for details.")
            return False


def generate_metrics_csv():
    """Generate or regenerate metrics CSV files using the fallback script."""
    cmd = ["python", "generate_metrics_csv.py"]
    print(f"🔄 Running: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ Successfully regenerated metrics CSV files")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to regenerate metrics CSV files")
        return False


def launch_dashboard():
    """Launch the Streamlit dashboard for result visualization."""
    cmd = ["streamlit", "run", "dashboard_cifar.py"]
    print(f"📊 Launching dashboard: {' '.join(cmd)}")
    
    try:
        # Run the dashboard in a new process
        dashboard_process = subprocess.Popen(cmd)
        print("✅ Dashboard launched. Press Ctrl+C to stop.")
        
        # Wait for user to interrupt
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping dashboard...")
            dashboard_process.terminate()
            dashboard_process.wait()
            print("✅ Dashboard stopped.")
    except Exception as e:
        print(f"❌ Failed to launch dashboard: {e}")
        return False
    
    return True


def main():
    """Main function to execute the pipeline."""
    args = parse_args()
    
    # Create logs directory if it doesn't exist
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    # Check if train_cifar10.py supports GateNorm
    supports_gatenorm = check_gatenorm_support()
    if args.check_gatenorm_support:
        print(f"🔍 GateNorm support in train_cifar10.py: {'✅ Supported' if supports_gatenorm else '❌ Not supported'}")
        if not supports_gatenorm:
            print("⚠️ Warning: GateNorm ablation study will be skipped or may fail.")
    
    # Determine which units to train
    units_to_train = args.selected_units if args.selected_units else ALL_UNITS
    
    # Run training if not skipped
    if not args.skip_training:
        print("=" * 80)
        print("🧪 RUNNING PARATING EXPERIMENTS 🧪")
        print("=" * 80)
        
        # 1. Train all units with learnable alpha
        print("\n📝 Training units with learnable alpha...")
        for unit in units_to_train:
            run_training(
                unit=unit,
                epochs=args.epochs,
                batch_size=args.batch_size,
                accelerator=args.accelerator,
                is_learnable=True,
                use_gate_norm=False,
                force_retrain=args.force_retrain,
                supports_gatenorm=supports_gatenorm
            )
        
        # 2. Run GateNorm ablation study on selected units if supported
        if supports_gatenorm:
            print("\n📝 Running GateNorm ablation study...")
            for unit in [u for u in units_to_train if u in GATENORM_UNITS]:
                # Without GateNorm (already done if all units were trained)
                run_training(
                    unit=unit,
                    epochs=args.epochs,
                    batch_size=args.batch_size,
                    accelerator=args.accelerator,
                    is_learnable=False,
                    use_gate_norm=False,
                    force_retrain=args.force_retrain,
                    supports_gatenorm=supports_gatenorm
                )
                
                # With GateNorm
                run_training(
                    unit=unit,
                    epochs=args.epochs,
                    batch_size=args.batch_size,
                    accelerator=args.accelerator,
                    is_learnable=False,
                    use_gate_norm=True,
                    force_retrain=args.force_retrain,
                    supports_gatenorm=supports_gatenorm
                )
        else:
            print("\n⚠️ Skipping GateNorm ablation study as it's not supported.")
    
    # 3. Generate or regenerate metrics CSV files
    print("\n📝 Regenerating metrics CSV files...")
    generate_metrics_csv()
    
    # 4. Launch dashboard if not skipped
    if not args.skip_dashboard:
        print("\n📝 Launching Streamlit dashboard...")
        launch_dashboard()


if __name__ == "__main__":
    main() 