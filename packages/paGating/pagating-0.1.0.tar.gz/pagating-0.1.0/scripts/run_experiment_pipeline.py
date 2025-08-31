#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Experiment Pipeline Runner for paGating

This script automates the entire experiment workflow:
1. Run hyperparameter sweep for all paGating units
2. Generate leaderboard from results
3. Create visualizations of the results
4. Run transformer benchmarks (optional)

This makes it easy to fully evaluate a new paGating unit against existing ones.
"""

import os
import argparse
import subprocess
import time
import logging
import json
import csv
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('experiment_pipeline.log')
    ]
)
logger = logging.getLogger("paGating")

def parse_args():
    parser = argparse.ArgumentParser(description="Run the complete paGating experiment pipeline")
    
    # General arguments
    parser.add_argument("--experiment_name", type=str, default=f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        help="Name for this experiment run")
    parser.add_argument("--output_dir", type=str, default="results",
                        help="Directory to store all results")
    parser.add_argument("--skip_sweep", action="store_true",
                        help="Skip the hyperparameter sweep phase (use existing logs)")
    parser.add_argument("--skip_leaderboard", action="store_true",
                        help="Skip the leaderboard generation phase")
    parser.add_argument("--skip_visualization", action="store_true",
                        help="Skip the visualization phase")
    parser.add_argument("--include_transformer", action="store_true",
                        help="Run transformer benchmark tests for each unit/alpha combination")
    parser.add_argument("--export_all", action="store_true",
                        help="Generate dashboard, PDF report, and consolidated summary export")
    
    # Sweep-specific arguments
    parser.add_argument("--units", type=str, nargs="+", 
                        default=["paGLU", "paGTU", "paSwishU", "paReGLU", "paGELU", "paMishU", "paSiLUU", "paSiLU", "paGRU"],
                        help="paGating units to include in the sweep")
    parser.add_argument("--alpha_values", type=float, nargs="+",
                        default=[0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0],
                        help="Alpha values to sweep")
    parser.add_argument("--learnable_alpha", action="store_true",
                        help="Also test with learnable alpha parameter")
    parser.add_argument("--num_epochs", type=int, default=50,
                        help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=64,
                        help="Batch size for training")
    parser.add_argument("--lr", type=float, default=0.001,
                        help="Learning rate")
    parser.add_argument("--log_dir", type=str, default="logs",
                        help="Directory for sweep logs")
    
    # Transformer-specific arguments
    parser.add_argument("--transformer_epochs", type=int, default=10,
                        help="Number of epochs for transformer benchmarks")
    parser.add_argument("--transformer_batch_size", type=int, default=32,
                        help="Batch size for transformer benchmarks")
    parser.add_argument("--transformer_seq_len", type=int, default=16,
                        help="Sequence length for transformer benchmarks")
    parser.add_argument("--transformer_d_model", type=int, default=64,
                        help="Model dimension for transformer benchmarks")
    parser.add_argument("--transformer_n_head", type=int, default=4,
                        help="Number of attention heads for transformer benchmarks")
    
    # Leaderboard-specific arguments
    parser.add_argument("--include_train", action="store_true",
                        help="Include training metrics in the leaderboard")
    parser.add_argument("--sort_by", type=str, default="test_accuracy",
                        choices=["test_accuracy", "test_loss", "train_accuracy", "train_loss"],
                        help="Metric to sort leaderboard by")
    parser.add_argument("--top_k", type=int, default=None,
                        help="Limit leaderboard to top K results")
    
    # Visualization-specific arguments
    parser.add_argument("--plot_dpi", type=int, default=300,
                        help="DPI for saved plots")
    parser.add_argument("--plot_style", type=str, default="whitegrid",
                        choices=["darkgrid", "whitegrid", "dark", "white", "ticks"],
                        help="Seaborn plot style")
    
    return parser.parse_args()

def setup_experiment_dirs(args):
    """Create the directory structure for the experiment."""
    # Create main experiment directory
    experiment_dir = os.path.join(args.output_dir, args.experiment_name)
    os.makedirs(experiment_dir, exist_ok=True)
    
    # Create subdirectories
    log_dir = os.path.join(experiment_dir, "logs")
    plots_dir = os.path.join(experiment_dir, "plots")
    leaderboard_dir = os.path.join(experiment_dir, "leaderboard")
    transformer_dir = os.path.join(experiment_dir, "transformer")
    
    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(plots_dir, exist_ok=True)
    os.makedirs(leaderboard_dir, exist_ok=True)
    
    if args.include_transformer:
        os.makedirs(transformer_dir, exist_ok=True)
        os.makedirs(os.path.join(transformer_dir, "logs"), exist_ok=True)
        os.makedirs(os.path.join(transformer_dir, "plots"), exist_ok=True)
    
    return {
        "main": experiment_dir,
        "logs": log_dir,
        "plots": plots_dir, 
        "leaderboard": leaderboard_dir,
        "transformer": transformer_dir
    }

def run_hyperparameter_sweep(args, experiment_dirs):
    """Run the hyperparameter sweep using run_sweep.py."""
    if args.skip_sweep:
        logger.info("Skipping hyperparameter sweep as requested.")
        return 0
    
    logger.info("Starting hyperparameter sweep...")
    
    # Convert list arguments to comma-separated strings for run_sweep.py
    units_str = ",".join(args.units)
    alphas_str = ",".join(map(str, args.alpha_values))
    learnable_str = "True" if args.learnable_alpha else "False"
    # If only testing static, maybe just pass "False"?
    # Or if testing both, pass "True,False"? 
    # Assuming run_sweep handles testing both if learnable_alpha is True from pipeline
    # Let's check run_sweep.py logic - it seems to test combinations.
    # If args.learnable_alpha is True, we test both static and learnable runs.
    # If args.learnable_alpha is False, we only test static.
    if args.learnable_alpha:
        learnable_str = "True,False"
    else:
        learnable_str = "False"

    # Prepare sweep command for run_sweep.py
    sweep_command = [
        "python", "scripts/run_sweep.py",
        "--output_dir", experiment_dirs["logs"], # Use logs dir as output for sweep results
        "--epochs", str(args.num_epochs),      # Pass num_epochs as epochs
        "--batch_size", str(args.batch_size),
        "--learning_rate", str(args.lr),        # Pass lr as learning_rate
        "--units", units_str,                   # Pass comma-separated units
        "--alphas", alphas_str,                 # Pass comma-separated alphas
        "--learnable", learnable_str            # Pass learnable flag(s)
        # Add other relevant args if needed (e.g., --weight_decay, --seed?)
        # Check run_sweep.py defaults for these.
    ]
    
    # Run the sweep
    start_time = time.time()
    logger.info(f"Running command: {' '.join(sweep_command)}")
    
    process = subprocess.run(
        sweep_command, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Log the output
    if process.stdout:
        logger.info(f"Sweep output:\n{process.stdout}")
    
    if process.stderr:
        if process.returncode != 0:
            logger.error(f"Sweep error:\n{process.stderr}")
        else:
            logger.info(f"Sweep stderr:\n{process.stderr}")
    
    elapsed_time = time.time() - start_time
    logger.info(f"Hyperparameter sweep completed in {elapsed_time:.2f} seconds with return code {process.returncode}")
    
    return process.returncode

def generate_leaderboard(args, experiment_dirs):
    """Generate leaderboard from results using generate_leaderboard.py."""
    if args.skip_leaderboard:
        logger.info("Skipping leaderboard generation as requested.")
        return 0
    
    logger.info("Generating leaderboard from results...")
    
    # Prepare leaderboard command
    leaderboard_command = [
        "python", "scripts/generate_leaderboard.py",
        "--results_dir", experiment_dirs["logs"],
        "--output_file", os.path.join(experiment_dirs["leaderboard"], "leaderboard.md"),
        "--sort_by", args.sort_by
    ]
    
    # Add optional arguments
    if args.include_train:
        leaderboard_command.append("--include_train")
    
    if args.top_k:
        leaderboard_command.extend(["--top_k", str(args.top_k)])
    
    # Run leaderboard generation
    start_time = time.time()
    logger.info(f"Running command: {' '.join(leaderboard_command)}")
    
    process = subprocess.run(
        leaderboard_command, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Log the output
    if process.stdout:
        logger.info(f"Leaderboard output:\n{process.stdout}")
    
    if process.stderr:
        if process.returncode != 0:
            logger.error(f"Leaderboard error:\n{process.stderr}")
        else:
            logger.info(f"Leaderboard stderr:\n{process.stderr}")
    
    elapsed_time = time.time() - start_time
    logger.info(f"Leaderboard generation completed in {elapsed_time:.2f} seconds with return code {process.returncode}")
    
    return process.returncode

def create_visualizations(args, experiment_dirs):
    """Create visualizations from results using visualize_results.py."""
    if args.skip_visualization:
        logger.info("Skipping visualization as requested.")
        return 0
    
    logger.info("Creating visualizations from results...")
    
    # Prepare visualization command
    viz_command = [
        "python", "scripts/visualize_results.py",
        "--results_dir", experiment_dirs["logs"],
        "--output_dir", experiment_dirs["plots"],
        "--dpi", str(args.plot_dpi),
        "--style", args.plot_style
    ]
    
    # Add optional unit filtering if specific units are requested
    if args.units:
        viz_command.extend(["--units"] + args.units)
    
    # Add optional alpha value filtering if specific values are requested
    if args.alpha_values:
        viz_command.extend(["--alpha_values"] + [str(alpha) for alpha in args.alpha_values])
    
    # Run visualization
    start_time = time.time()
    logger.info(f"Running command: {' '.join(viz_command)}")
    
    process = subprocess.run(
        viz_command, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Log the output
    if process.stdout:
        logger.info(f"Visualization output:\n{process.stdout}")
    
    if process.stderr:
        if process.returncode != 0:
            logger.error(f"Visualization error:\n{process.stderr}")
        else:
            logger.info(f"Visualization stderr:\n{process.stderr}")
    
    elapsed_time = time.time() - start_time
    logger.info(f"Visualization completed in {elapsed_time:.2f} seconds with return code {process.returncode}")
    
    return process.returncode

def run_transformer_benchmarks(args, experiment_dirs):
    """Run transformer benchmarks for each unit and alpha combination."""
    if not args.include_transformer:
        logger.info("Skipping transformer benchmarks as not requested.")
        return 0
    
    logger.info("Starting transformer benchmarks...")
    
    # Create logs directory for transformer tests if it doesn't exist
    transformer_logs_dir = os.path.join(experiment_dirs["transformer"], "logs")
    os.makedirs(transformer_logs_dir, exist_ok=True)
    
    # CSV to store all results
    csv_path = os.path.join(experiment_dirs["transformer"], "transformer_results.csv")
    results = []
    
    # Generate markdown for the results
    md_path = os.path.join(experiment_dirs["leaderboard"], "transformer_leaderboard.md")
    
    with open(csv_path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([
            'Unit', 'Alpha', 'Train Loss', 'Train Accuracy', 
            'Test Loss', 'Test Accuracy', 'Epochs'
        ])
        
        # Run benchmark for each unit and alpha combination
        for unit in args.units:
            for alpha in args.alpha_values:
                logger.info(f"Running transformer benchmark for {unit} with alpha={alpha}...")
                
                # Create log file for this run
                log_file = os.path.join(
                    transformer_logs_dir, 
                    f"{unit}_alpha{alpha:.2f}.log"
                )
                
                # Prepare benchmark command
                benchmark_command = [
                    "python", "experiments/test_transformer.py",
                    "--unit", unit,
                    "--alpha", str(alpha),
                    "--epochs", str(args.transformer_epochs),
                    "--batch_size", str(args.transformer_batch_size),
                    "--seq_len", str(args.transformer_seq_len),
                    "--d_model", str(args.transformer_d_model),
                    "--n_head", str(args.transformer_n_head)
                ]
                
                # Run the benchmark
                start_time = time.time()
                logger.info(f"Running command: {' '.join(benchmark_command)}")
                
                with open(log_file, 'w') as log:
                    process = subprocess.run(
                        benchmark_command, 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    
                    # Write output to log file
                    log.write(f"Command: {' '.join(benchmark_command)}\n\n")
                    log.write(f"STDOUT:\n{process.stdout}\n\n")
                    
                    if process.stderr:
                        log.write(f"STDERR:\n{process.stderr}\n\n")
                
                elapsed_time = time.time() - start_time
                logger.info(f"Benchmark for {unit} (alpha={alpha}) completed in {elapsed_time:.2f} seconds")
                
                # Parse results from stdout
                train_loss = None
                train_acc = None
                test_loss = None
                test_acc = None
                
                for line in process.stdout.splitlines():
                    if "Epoch 10/" in line or f"Epoch {args.transformer_epochs}/" in line:
                        # Extract last epoch's training metrics
                        parts = line.split(", ")
                        if len(parts) >= 3:
                            try:
                                train_loss = float(parts[1].split(": ")[1])
                                train_acc = float(parts[2].split(": ")[1].rstrip("%"))
                            except (IndexError, ValueError) as e:
                                logger.warning(f"Could not parse training metrics from line: {line}. Error: {e}")
                    
                    if "Test Loss:" in line:
                        # Extract test metrics
                        parts = line.split(", ")
                        if len(parts) >= 2:
                            try:
                                test_loss = float(parts[0].split(": ")[1])
                                test_acc = float(parts[1].split(": ")[1].rstrip("%"))
                            except (IndexError, ValueError) as e:
                                logger.warning(f"Could not parse test metrics from line: {line}. Error: {e}")
                
                # Store results
                result = {
                    'unit': unit,
                    'alpha': alpha,
                    'train_loss': train_loss,
                    'train_acc': train_acc,
                    'test_loss': test_loss,
                    'test_acc': test_acc,
                    'epochs': args.transformer_epochs
                }
                results.append(result)
                
                # Write to CSV
                writer.writerow([
                    unit, alpha, train_loss, train_acc, test_loss, test_acc, args.transformer_epochs
                ])
    
    # Copy generated plot files to the transformer/plots directory
    plots_dir = os.path.join(experiment_dirs["transformer"], "plots")
    os.makedirs(plots_dir, exist_ok=True)
    
    for unit in args.units:
        for alpha in args.alpha_values:
            # Look for plots in the experiments directory instead of current directory
            src_plot = os.path.join("experiments", f"{unit}_transformer_alpha{alpha:.2f}.png")
            if os.path.exists(src_plot):
                dest_plot = os.path.join(plots_dir, src_plot.split("/")[-1])
                with open(src_plot, 'rb') as src_file:
                    with open(dest_plot, 'wb') as dest_file:
                        dest_file.write(src_file.read())
                logger.info(f"Copied plot {src_plot} to {dest_plot}")
    
    # Generate markdown leaderboard sorted by test accuracy
    results.sort(key=lambda x: x['test_acc'] if x['test_acc'] is not None else 0, reverse=True)
    
    with open(md_path, 'w') as md_file:
        md_file.write("# Transformer Benchmark Results\n\n")
        md_file.write("Results of paGating units in a transformer model for sequence classification.\n\n")
        
        md_file.write("## Leaderboard\n\n")
        md_file.write("| Rank | Unit | Alpha | Test Accuracy | Test Loss | Train Accuracy | Train Loss |\n")
        md_file.write("|------|------|-------|--------------|-----------|----------------|------------|\n")
        
        for i, res in enumerate(results):
            # Handle potential None values before formatting
            unit = res.get('unit', 'N/A')
            alpha = f"{res.get('alpha', 'N/A'):.2f}" if res.get('alpha') is not None else 'N/A'
            test_acc = f"{res.get('test_acc', 'N/A'):.2f}%" if res.get('test_acc') is not None else 'N/A'
            test_loss = f"{res.get('test_loss', 'N/A'):.4f}" if res.get('test_loss') is not None else 'N/A'
            train_acc = f"{res.get('train_acc', 'N/A'):.2f}%" if res.get('train_acc') is not None else 'N/A'
            train_loss = f"{res.get('train_loss', 'N/A'):.4f}" if res.get('train_loss') is not None else 'N/A'
            
            md_file.write(f"| {i+1} | {unit} | {alpha} | {test_acc} | {test_loss} | {train_acc} | {train_loss} |\n")
        
        md_file.write("\n## Configuration\n\n")
        md_file.write(f"- Epochs: {args.transformer_epochs}\n")
        md_file.write(f"- Batch Size: {args.transformer_batch_size}\n")
        md_file.write(f"- Sequence Length: {args.transformer_seq_len}\n")
        md_file.write(f"- Model Dimension: {args.transformer_d_model}\n")
        md_file.write(f"- Attention Heads: {args.transformer_n_head}\n")
        
        md_file.write("\n## Plots\n\n")
        md_file.write("See the `plots` directory for training curves of each model.\n\n")
    
    # Update results_summary.md with transformer results
    # Check if transformer_results is not empty and handle None before updating summary
    if results:
        update_results_summary(args, experiment_dirs, results)
    else:
        logger.warning("No transformer results generated, skipping update of results_summary.md")
    
    logger.info(f"Transformer benchmarks completed. Results saved to {csv_path} and {md_path}")
    return 0

def update_results_summary(args, experiment_dirs, transformer_results):
    """Update results_summary.md with transformer benchmark results."""
    summary_path = os.path.join(experiment_dirs["main"], "results_summary.md")
    
    # Check if results_summary.md exists
    if not os.path.exists(summary_path):
        logger.warning(f"results_summary.md not found at {summary_path}, creating new file.")
        # Copy from original if it exists
        if os.path.exists("results_summary.md"):
            with open("results_summary.md", "r") as src_file:
                content = src_file.read()
            with open(summary_path, "w") as dest_file:
                dest_file.write(content)
        else:
            with open(summary_path, "w") as f:
                f.write("# Experimental Results\n\n")
                f.write("This document summarizes the experimental results.\n\n")
    
    # Read existing content
    with open(summary_path, "r") as f:
        content = f.read()
    
    # Check if transformer section already exists
    if "## Transformer Benchmark Results" in content:
        logger.info("Transformer section already exists in results_summary.md, updating.")
        # Will replace the section
        start = content.find("## Transformer Benchmark Results")
        # Find the next section if any
        next_section = content.find("##", start + 1)
        
        if next_section > 0:
            # Keep content before and after transformer section
            before = content[:start]
            after = content[next_section:]
        else:
            # No next section, keep only content before transformer section
            before = content[:start]
            after = ""
    else:
        # Append to the end
        before = content
        after = ""
    
    # Generate transformer section
    transformer_section = "## Transformer Benchmark Results\n\n"
    transformer_section += "We evaluated the performance of different paGating units in a transformer model for sequence classification.\n\n"
    
    # Find the best unit (handle None)
    valid_results = [r for r in transformer_results if r.get('test_acc') is not None]
    if valid_results:
        best_result = max(valid_results, key=lambda x: x['test_acc'])
        transformer_section += f"The best performing unit was **{best_result.get('unit', 'N/A')}** with alpha={best_result.get('alpha', 'N/A'):.2f}, "
        transformer_section += f"achieving a test accuracy of {best_result['test_acc']:.2f}%\n\n"
    else:
        transformer_section += "No valid transformer results with test accuracy were found.\n\n"

    # Add a table of top 5 results
    transformer_section += "### Top 5 Units by Test Accuracy\n\n"
    transformer_section += "| Unit | Alpha | Test Accuracy | Test Loss |\n"
    transformer_section += "|------|-------|--------------|----------|\n"
    
    sorted_valid_results = sorted(valid_results, key=lambda x: x['test_acc'], reverse=True)
    for res in sorted_valid_results[:5]:
        unit = res.get('unit', 'N/A')
        alpha = f"{res.get('alpha', 'N/A'):.2f}" if res.get('alpha') is not None else 'N/A'
        test_acc = f"{res.get('test_acc', 'N/A'):.2f}%" if res.get('test_acc') is not None else 'N/A'
        test_loss = f"{res.get('test_loss', 'N/A'):.4f}" if res.get('test_loss') is not None else 'N/A'
        transformer_section += f"| {unit} | {alpha} | {test_acc} | {test_loss} |\n"
    if not sorted_valid_results:
         transformer_section += "| N/A | N/A | N/A | N/A |\n"
    
    transformer_section += "\n"
    
    # Add analysis of alpha impact for each unit
    transformer_section += "### Effect of Alpha Parameter\n\n"
    transformer_section += "The following table shows how the alpha parameter affects performance for each unit:\n\n"
    
    # Group by unit and find best alpha for each
    units = {}
    for res in transformer_results:
        unit = res['unit']
        if unit not in units:
            units[unit] = []
        units[unit].append(res)
    
    for unit, results in units.items():
        # Sort by alpha
        results.sort(key=lambda x: x['alpha'])
        
        transformer_section += f"#### {unit}\n\n"
        transformer_section += "| Alpha | Test Accuracy | Test Loss |\n"
        transformer_section += "|-------|--------------|----------|\n"
        
        for res in results:
            # Handle potential None values before formatting
            alpha = f"{res.get('alpha', 'N/A'):.2f}" if res.get('alpha') is not None else 'N/A'
            test_acc = f"{res.get('test_acc', 'N/A'):.2f}%" if res.get('test_acc') is not None else 'N/A'
            test_loss = f"{res.get('test_loss', 'N/A'):.4f}" if res.get('test_loss') is not None else 'N/A'
            transformer_section += f"| {alpha} | {test_acc} | {test_loss} |\n"
        
        transformer_section += "\n"
    
    # Write updated content
    with open(summary_path, "w") as f:
        f.write(before + transformer_section + after)
    
    logger.info(f"Updated results_summary.md with transformer benchmark results.")

def copy_results_summary(args, experiment_dirs):
    """Copy the results_summary.md file to the experiment directory."""
    if os.path.exists("results_summary.md"):
        logger.info("Copying results_summary.md to experiment directory...")
        
        dest_path = os.path.join(experiment_dirs["main"], "results_summary.md")
        
        with open("results_summary.md", "r") as src_file:
            content = src_file.read()
        
        with open(dest_path, "w") as dest_file:
            dest_file.write(content)
            
        logger.info(f"Copied results_summary.md to {dest_path}")
    else:
        logger.warning("results_summary.md not found, skipping copy.")

def export_all_results(args, experiment_dirs):
    """Generate dashboard, PDF report, and consolidated summary export."""
    if not args.export_all:
        logger.info("Skipping export_all as not requested.")
        return 0
    
    logger.info("Starting export of all results...")
    
    # Generate PDF report
    pdf_command = [
        "python", "export_report.py",
        "--experiment_dir", experiment_dirs["main"]
    ]
    
    # Run PDF report generation
    logger.info(f"Generating PDF report for {experiment_dirs['main']}...")
    logger.info(f"Running command: {' '.join(pdf_command)}")
    
    pdf_process = subprocess.run(
        pdf_command, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Log the output
    if pdf_process.stdout:
        logger.info(f"PDF report output:\n{pdf_process.stdout}")
    
    if pdf_process.stderr:
        if pdf_process.returncode != 0:
            logger.error(f"PDF report error:\n{pdf_process.stderr}")
        else:
            logger.info(f"PDF report stderr:\n{pdf_process.stderr}")
    
    # Generate consolidated summary export
    summary_command = [
        "python", "export_summary.py",
        "--experiment_dir", experiment_dirs["main"]
    ]
    
    # Run summary export
    logger.info(f"Generating consolidated summary export for {experiment_dirs['main']}...")
    logger.info(f"Running command: {' '.join(summary_command)}")
    
    summary_process = subprocess.run(
        summary_command, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Log the output
    if summary_process.stdout:
        logger.info(f"Summary export output:\n{summary_process.stdout}")
    
    if summary_process.stderr:
        if summary_process.returncode != 0:
            logger.error(f"Summary export error:\n{summary_process.stderr}")
        else:
            logger.info(f"Summary export stderr:\n{summary_process.stderr}")
    
    # Launch dashboard
    dashboard_command = [
        "streamlit", "run", "dashboard.py", "--",
        "--experiment", experiment_dirs["main"]
    ]
    
    # Run dashboard in the background
    logger.info(f"Launching dashboard for {experiment_dirs['main']}...")
    logger.info(f"Running command: {' '.join(dashboard_command)}")
    
    try:
        dashboard_process = subprocess.Popen(
            dashboard_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Let the dashboard start up
        import time
        time.sleep(2)
        
        logger.info("Dashboard launched successfully. Check the terminal for the URL.")
    except Exception as e:
        logger.error(f"Failed to launch dashboard: {e}")
    
    logger.info("Export of all results completed.")
    return 0

def main():
    """Run the complete experiment pipeline."""
    args = parse_args()
    
    logger.info(f"Starting paGating experiment pipeline with name: {args.experiment_name}")
    
    # Set up directories
    experiment_dirs = setup_experiment_dirs(args)
    logger.info(f"Created experiment directory structure at {experiment_dirs['main']}")
    
    # Run each phase
    sweep_status = run_hyperparameter_sweep(args, experiment_dirs)
    
    if sweep_status == 0 or args.skip_sweep:
        leaderboard_status = generate_leaderboard(args, experiment_dirs)
        
        if leaderboard_status == 0 or args.skip_leaderboard:
            viz_status = create_visualizations(args, experiment_dirs)
            
            # Copy results summary
            copy_results_summary(args, experiment_dirs)
            
            # Run transformer benchmarks if requested
            if args.include_transformer:
                transformer_status = run_transformer_benchmarks(args, experiment_dirs)
            
            # Export all results if requested
            if args.export_all:
                export_status = export_all_results(args, experiment_dirs)
    
    logger.info(f"Experiment pipeline completed. Results are in {experiment_dirs['main']}")
    
    # Print instructions for viewing results
    print("\n" + "="*80)
    print(f"🎉 Experiment '{args.experiment_name}' completed!")
    print("="*80)
    print(f"📊 Results are available in: {experiment_dirs['main']}")
    print(f"📋 Leaderboard: {os.path.join(experiment_dirs['leaderboard'], 'leaderboard.md')}")
    print(f"📈 Visualizations: {experiment_dirs['plots']}")
    print(f"📝 Logs: {experiment_dirs['logs']}")
    
    if args.include_transformer:
        print(f"🤖 Transformer Results: {os.path.join(experiment_dirs['transformer'])}")
        print(f"📋 Transformer Leaderboard: {os.path.join(experiment_dirs['leaderboard'], 'transformer_leaderboard.md')}")
    
    if args.export_all:
        print(f"📊 Interactive Dashboard: Check terminal for Streamlit URL")
        print(f"📄 PDF Report: {os.path.join(experiment_dirs['main'], 'report.pdf')}")
        print(f"📦 Results Archive: {os.path.join(experiment_dirs['main'], 'results.zip')}")
        print(f"🔍 Summary JSON: {os.path.join(experiment_dirs['main'], 'summary.json')}")
    
    print("="*80)

if __name__ == "__main__":
    main() 