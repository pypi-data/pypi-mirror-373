#!/usr/bin/env python
"""
Hyperparameter Sweep for paGating Units on CIFAR-10

This script performs a hyperparameter sweep across different paGating units,
alpha values, and alpha configurations (static or learnable).

Usage:
    python scripts/run_sweep.py [--epochs EPOCHS] [--batch_size BATCH_SIZE] 
                               [--output_dir OUTPUT_DIR] [--parallel]
                               [--num_workers NUM_WORKERS] [--gpu_ids GPU_IDS]
"""

import os
import sys
import argparse
import itertools
import json
import time
from datetime import datetime
from multiprocessing import Pool, cpu_count
import subprocess

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run hyperparameter sweep for paGating units")
    
    # Training parameters
    parser.add_argument("--epochs", type=int, default=10,
                        help="Number of epochs for each run (default: 10)")
    parser.add_argument("--batch_size", type=int, default=64,
                        help="Batch size for training (default: 64)")
    parser.add_argument("--learning_rate", type=float, default=0.001,
                        help="Learning rate (default: 0.001)")
    parser.add_argument("--weight_decay", type=float, default=1e-4,
                        help="Weight decay (default: 1e-4)")
    
    # Output parameters
    parser.add_argument("--output_dir", type=str, default="cifar10_results",
                        help="Directory to save results (default: cifar10_results)")
    
    # Parallelization parameters
    parser.add_argument("--parallel", action="store_true",
                        help="Run jobs in parallel using multiprocessing")
    parser.add_argument("--num_workers", type=int, default=None,
                        help="Number of parallel workers (default: number of CPUs)")
    parser.add_argument("--gpu_ids", type=str, default="",
                        help="Comma-separated list of GPU IDs to use (e.g., '0,1,2')")
    
    # Data parameters
    parser.add_argument("--data_dir", type=str, default="data/cifar10",
                        help="Directory for CIFAR-10 data (default: data/cifar10)")
    parser.add_argument("--val_split", type=float, default=0.1,
                        help="Validation split ratio (default: 0.1)")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed (default: 42)")
    
    # Sweep parameters (override defaults)
    parser.add_argument("--units", type=str, 
                        default="paMishU,paGLU,paGTU,paSwishU,paReGLU,paGELU",
                        help="Comma-separated list of units to sweep")
    parser.add_argument("--alphas", type=str, default="0.1,0.3,0.5,0.7,0.9",
                        help="Comma-separated list of alpha values to sweep")
    parser.add_argument("--learnable", type=str, default="False,True",
                        help="Comma-separated list of learnable alpha settings (True/False)")
    
    return parser.parse_args()

def run_training_job(config):
    """
    Run a single training job with the given configuration.
    
    Args:
        config: Dictionary containing job configuration
    
    Returns:
        Dictionary with job results
    """
    start_time = time.time()
    
    # Extract parameters
    unit_name = config["unit_name"]
    alpha = config["alpha"]
    use_learnable_alpha = config["use_learnable_alpha"]
    epochs = config["epochs"]
    batch_size = config["batch_size"]
    learning_rate = config["learning_rate"]
    weight_decay = config["weight_decay"]
    output_dir = config["output_dir"]
    data_dir = config["data_dir"]
    val_split = config["val_split"]
    seed = config["seed"]
    gpu_id = config.get("gpu_id", None)
    
    # Create command
    cmd = [
        "python", "train_cifar10.py",
        f"--unit_name={unit_name}",
        f"--alpha={alpha}",
        f"--batch_size={batch_size}",
        f"--learning_rate={learning_rate}",
        f"--weight_decay={weight_decay}",
        f"--max_epochs={epochs}",
        f"--output_dir={output_dir}",
        f"--data_dir={data_dir}",
        f"--val_split={val_split}",
        f"--seed={seed}"
    ]
    
    # Add learnable alpha if requested
    if use_learnable_alpha:
        cmd.append("--use_learnable_alpha")
    
    # Set CUDA_VISIBLE_DEVICES if GPU ID is specified
    env = os.environ.copy()
    if gpu_id is not None:
        env["CUDA_VISIBLE_DEVICES"] = str(gpu_id)
    
    # Print command
    print(f"Running: {' '.join(cmd)}")
    print(f"GPU ID: {gpu_id if gpu_id is not None else 'CPU'}")
    
    # Run command
    try:
        result = subprocess.run(cmd, env=env, check=True, capture_output=True, text=True)
        success = True
        error = None
        output = result.stdout
    except subprocess.CalledProcessError as e:
        success = False
        error = str(e)
        output = e.stdout + "\n" + e.stderr
    
    # Get end time
    end_time = time.time()
    runtime_sec = end_time - start_time
    
    # Create result dictionary
    result_dict = {
        "unit_name": unit_name,
        "alpha": alpha,
        "use_learnable_alpha": use_learnable_alpha,
        "success": success,
        "runtime_sec": runtime_sec,
        "start_time": datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S'),
        "end_time": datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')
    }
    
    if not success:
        result_dict["error"] = error
    
    # Save output log
    log_dir = os.path.join(
        output_dir, 
        f"logs_{datetime.now().strftime('%Y%m%d')}"
    )
    os.makedirs(log_dir, exist_ok=True)
    
    log_filename = f"{unit_name}_alpha{alpha}_{'learnable' if use_learnable_alpha else 'static'}.log"
    log_path = os.path.join(log_dir, log_filename)
    
    with open(log_path, "w") as f:
        f.write(output)
    
    print(f"Completed {unit_name}, α={alpha}, learnable={use_learnable_alpha} in {runtime_sec:.2f}s")
    
    return result_dict

def main():
    """Main function to run hyperparameter sweep."""
    args = parse_args()
    
    # Parse sweep parameters
    units = [unit.strip() for unit in args.units.split(",")]
    alphas = [float(alpha.strip()) for alpha in args.alphas.split(",")]
    learnable_options = [s.strip().lower() == "true" for s in args.learnable.split(",")]
    
    # Create output directory
    sweep_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(args.output_dir, f"sweep_{sweep_time}")
    os.makedirs(output_dir, exist_ok=True)
    
    # Save sweep configuration
    sweep_config = {
        "units": units,
        "alphas": alphas,
        "learnable_options": [str(opt) for opt in learnable_options],
        "epochs": args.epochs,
        "batch_size": args.batch_size,
        "learning_rate": args.learning_rate,
        "weight_decay": args.weight_decay,
        "data_dir": args.data_dir,
        "val_split": args.val_split,
        "seed": args.seed,
        "start_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }
    
    with open(os.path.join(output_dir, "sweep_config.json"), "w") as f:
        json.dump(sweep_config, f, indent=2)
    
    # Generate job configurations
    job_configs = []
    
    # Parse GPU IDs if provided
    gpu_ids = []
    if args.gpu_ids:
        gpu_ids = [id.strip() for id in args.gpu_ids.split(",")]
    
    # Create parameter combinations
    param_combinations = list(itertools.product(units, alphas, learnable_options))
    num_jobs = len(param_combinations)
    
    print(f"Running sweep with {num_jobs} parameter combinations")
    print(f"Units: {units}")
    print(f"Alphas: {alphas}")
    print(f"Learnable options: {learnable_options}")
    print(f"Output directory: {output_dir}")
    
    # Create jobs
    for i, (unit_name, alpha, use_learnable_alpha) in enumerate(param_combinations):
        # Assign GPU ID if available
        gpu_id = None
        if gpu_ids:
            gpu_id = gpu_ids[i % len(gpu_ids)]
        
        config = {
            "unit_name": unit_name,
            "alpha": alpha,
            "use_learnable_alpha": use_learnable_alpha,
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "learning_rate": args.learning_rate,
            "weight_decay": args.weight_decay,
            "output_dir": output_dir,
            "data_dir": args.data_dir,
            "val_split": args.val_split,
            "seed": args.seed,
            "gpu_id": gpu_id
        }
        
        job_configs.append(config)
    
    # Run jobs
    results = []
    
    if args.parallel:
        # Determine number of workers
        num_workers = args.num_workers or min(cpu_count(), num_jobs)
        print(f"Running {num_jobs} jobs in parallel with {num_workers} workers")
        
        # Run jobs in parallel
        with Pool(num_workers) as pool:
            results = pool.map(run_training_job, job_configs)
    else:
        # Run jobs sequentially
        print(f"Running {num_jobs} jobs sequentially")
        for config in job_configs:
            result = run_training_job(config)
            results.append(result)
    
    # Save results
    sweep_results = {
        "config": sweep_config,
        "results": results,
        "end_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    with open(os.path.join(output_dir, "sweep_results.json"), "w") as f:
        json.dump(sweep_results, f, indent=2)
    
    # Print summary
    success_count = sum(1 for r in results if r["success"])
    
    print("\nSweep Summary:")
    print(f"Total jobs: {num_jobs}")
    print(f"Successful jobs: {success_count}")
    print(f"Failed jobs: {num_jobs - success_count}")
    print(f"Results saved to: {output_dir}")


if __name__ == "__main__":
    main() 