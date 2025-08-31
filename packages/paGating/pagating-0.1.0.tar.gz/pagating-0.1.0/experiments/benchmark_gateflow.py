#!/usr/bin/env python
"""
Gating Flow Benchmark for paGating Units

This script visualizes the behavior of different paGating units (paGLU, paGTU,
paSwishU, paReGLU, paGELU, paMishU, paSiLU) across a range of alpha values. It plots how the mean and
standard deviation of activations change as alpha varies from 0.0 to 1.0.

Usage:
    python benchmark_gateflow.py [--device DEVICE] [--use-gate-norm] [--pre-norm] [--post-norm]

Options:
    --device DEVICE      Computation device (cpu, cuda, mps) [default: cpu]
    --use-gate-norm      Apply GateNorm to the gating pathway
    --pre-norm           Apply LayerNorm before the activation unit
    --post-norm          Apply LayerNorm after the activation unit
    --output-dir DIR     Directory to save benchmark results and plots [default: benchmarks/norm_variants]
    --batch-size SIZE    Batch size for benchmark [default: 64]
    --dim DIM            Input/output dimensions [default: 64]
"""

import argparse
import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import torch
import csv
from datetime import datetime

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import paGating units
from paGating.paGLU import paGLU
from paGating.paGTU import paGTU
from paGating.paSwishU import paSwishU
from paGating.paReGLU import paReGLU
from paGating.paGELU import paGELU
from paGating.paMishU import paMishU
from paGating.paSiLU import paSiLU
from paGating import PrePostNormWrapper


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Benchmark paGating units across alpha values")
    parser.add_argument(
        "--device", 
        type=str, 
        default="cpu", 
        choices=["cpu", "cuda", "mps"],
        help="Computation device (cpu, cuda, mps)"
    )
    parser.add_argument(
        "--use-gate-norm",
        action="store_true",
        help="Apply GateNorm to the gating pathway"
    )
    parser.add_argument(
        "--pre-norm",
        action="store_true",
        help="Apply LayerNorm before the activation unit"
    )
    parser.add_argument(
        "--post-norm",
        action="store_true",
        help="Apply LayerNorm after the activation unit"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="benchmarks/norm_variants",
        help="Directory to save benchmark results and plots"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=64,
        help="Batch size for benchmark"
    )
    parser.add_argument(
        "--dim",
        type=int,
        default=64,
        help="Input/output dimensions"
    )
    parser.add_argument(
        "--run-matrix",
        action="store_true",
        help="Run all combinations of normalization options"
    )
    return parser.parse_args()


def get_device(device_name):
    """Get the appropriate torch device."""
    if device_name == "cuda" and torch.cuda.is_available():
        return torch.device("cuda")
    elif device_name == "mps" and hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    else:
        return torch.device("cpu")


def benchmark_latency(model, input_tensor, n_runs=100):
    """
    Measure the inference latency of a model.
    
    Args:
        model: The model to benchmark
        input_tensor: Input tensor to use for benchmarking
        n_runs: Number of runs to average over
        
    Returns:
        float: Average latency in milliseconds
    """
    # Warm-up
    for _ in range(10):
        with torch.no_grad():
            _ = model(input_tensor)
    
    # Synchronize before timing
    if input_tensor.device.type == "cuda":
        torch.cuda.synchronize()
    elif input_tensor.device.type == "mps":
        torch.mps.synchronize()
    
    # Benchmark
    start_time = torch.cuda.Event(enable_timing=True)
    end_time = torch.cuda.Event(enable_timing=True)
    
    latencies = []
    
    for _ in range(n_runs):
        if input_tensor.device.type in ["cuda", "mps"]:
            start_time.record()
        else:
            start = torch.tensor([]).float().cpu().sum()
        
        with torch.no_grad():
            _ = model(input_tensor)
        
        if input_tensor.device.type in ["cuda", "mps"]:
            end_time.record()
            torch.cuda.synchronize()
            latencies.append(start_time.elapsed_time(end_time))
        else:
            end = torch.tensor([]).float().cpu().sum()
            latencies.append((end - start) * 1000)  # Convert to ms
    
    return sum(latencies) / len(latencies)


def benchmark_unit(unit_class, input_tensor, alpha_range, device, batch_size, input_dim, output_dim, 
                  use_gate_norm=False, pre_norm=False, post_norm=False):
    """
    Benchmark a paGating unit across a range of alpha values.
    
    Args:
        unit_class: The paGating unit class to benchmark
        input_tensor: Input tensor to use for benchmarking
        alpha_range: Range of alpha values to test
        device: Computation device
        batch_size: Batch size for the input
        input_dim: Input dimension
        output_dim: Output dimension
        use_gate_norm: Whether to use GateNorm
        pre_norm: Whether to use pre-normalization
        post_norm: Whether to use post-normalization
        
    Returns:
        dict: Dictionary containing mean, std, and latency values for each alpha
    """
    results = {
        "alpha": [],
        "mean": [],
        "std": [],
        "latency_ms": []
    }
    
    norm_config = ""
    if use_gate_norm:
        norm_config += "G"
    if pre_norm:
        norm_config += "Pre"
    if post_norm:
        norm_config += "Post"
    
    norm_str = f" ({norm_config})" if norm_config else ""
    print(f"Benchmarking {unit_class.__name__}{norm_str}...")
    
    for alpha in alpha_range:
        # Create base unit with current alpha
        base_unit = unit_class(
            input_dim=input_dim,
            output_dim=output_dim,
            alpha=float(alpha),
            use_gate_norm=use_gate_norm
        ).to(device)
        
        # Wrap with pre/post normalization if needed
        if pre_norm or post_norm:
            model = PrePostNormWrapper(
                module=base_unit,
                input_dim=input_dim,
                output_dim=output_dim,
                pre_norm=pre_norm,
                post_norm=post_norm
            ).to(device)
        else:
            model = base_unit
        
        # Ensure evaluation mode
        model.eval()
        
        # Forward pass for statistics
        with torch.no_grad():
            output = model(input_tensor)
            
        # Calculate statistics
        mean_val = output.mean().item()
        std_val = output.std().item()
        
        # Measure latency
        latency = benchmark_latency(model, input_tensor)
        
        results["alpha"].append(alpha)
        results["mean"].append(mean_val)
        results["std"].append(std_val)
        results["latency_ms"].append(latency)
        
        print(f"  α={alpha:.1f}: mean={mean_val:.4f}, std={std_val:.4f}, latency={latency:.3f} ms")
    
    return results


def save_results_to_csv(unit_name, results, output_dir, norm_config):
    """
    Save benchmark results to a CSV file.
    
    Args:
        unit_name: Name of the paGating unit
        results: Dictionary with benchmark results
        output_dir: Directory to save results
        norm_config: Normalization configuration string
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create filename with normalization config
    norm_str = f"_{norm_config}" if norm_config else ""
    filename = os.path.join(output_dir, f"{unit_name}{norm_str}_results.csv")
    
    # Write to CSV
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['alpha', 'mean', 'std', 'latency_ms']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for i in range(len(results["alpha"])):
            writer.writerow({
                'alpha': results["alpha"][i],
                'mean': results["mean"][i],
                'std': results["std"][i],
                'latency_ms': results["latency_ms"][i]
            })
    
    print(f"Results saved to {filename}")


def plot_results(unit_name, results, output_dir, norm_config=""):
    """
    Plot mean, std, and latency of activations vs alpha.
    
    Args:
        unit_name: Name of the paGating unit
        results: Dictionary with benchmark results
        output_dir: Directory to save plots
        norm_config: Normalization configuration string
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create figure
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
    
    norm_title = f" with {norm_config}" if norm_config else ""
    
    # Plot mean
    ax1.plot(results["alpha"], results["mean"], 'o-', linewidth=2, markersize=8)
    ax1.set_ylabel("Mean Activation")
    ax1.set_title(f"{unit_name}{norm_title} Mean Activation vs α")
    ax1.grid(True)
    
    # Plot std
    ax2.plot(results["alpha"], results["std"], 'o-', linewidth=2, markersize=8, color="orange")
    ax2.set_ylabel("Activation Std Dev")
    ax2.set_title(f"{unit_name}{norm_title} Activation Std Dev vs α")
    ax2.grid(True)
    
    # Plot latency
    ax3.plot(results["alpha"], results["latency_ms"], 'o-', linewidth=2, markersize=8, color="green")
    ax3.set_xlabel("Alpha (α)")
    ax3.set_ylabel("Latency (ms)")
    ax3.set_title(f"{unit_name}{norm_title} Inference Latency vs α")
    ax3.grid(True)
    
    # Set x-ticks
    ax3.set_xticks(results["alpha"])
    ax3.set_xticklabels([f"{a:.1f}" for a in results["alpha"]])
    
    # Adjust layout and save
    plt.tight_layout()
    
    # Create filename with normalization config
    norm_str = f"_{norm_config}" if norm_config else ""
    plt.savefig(os.path.join(output_dir, f"{unit_name}{norm_str}_gateflow.png"), dpi=300)
    plt.close()
    print(f"Plot saved as {unit_name}{norm_str}_gateflow.png")


def plot_comparison(unit_name, results_dict, alpha_range, output_dir):
    """
    Plot comparison of different normalization configurations for a single unit.
    
    Args:
        unit_name: Name of the paGating unit
        results_dict: Dictionary with results for each normalization config
        alpha_range: Range of alpha values tested
        output_dir: Directory to save plots
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create figure
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 15), sharex=True)
    
    # Plot mean, std, and latency for each configuration
    for config, results in results_dict.items():
        label = config if config else "No Norm"
        ax1.plot(results["alpha"], results["mean"], 'o-', linewidth=2, markersize=6, label=label)
        ax2.plot(results["alpha"], results["std"], 'o-', linewidth=2, markersize=6, label=label)
        ax3.plot(results["alpha"], results["latency_ms"], 'o-', linewidth=2, markersize=6, label=label)
    
    # Set labels and titles
    ax1.set_ylabel("Mean Activation")
    ax1.set_title(f"{unit_name} Mean Activation vs α (Normalization Comparison)")
    ax1.grid(True)
    ax1.legend()
    
    ax2.set_ylabel("Activation Std Dev")
    ax2.set_title(f"{unit_name} Activation Std Dev vs α (Normalization Comparison)")
    ax2.grid(True)
    ax2.legend()
    
    ax3.set_xlabel("Alpha (α)")
    ax3.set_ylabel("Latency (ms)")
    ax3.set_title(f"{unit_name} Inference Latency vs α (Normalization Comparison)")
    ax3.grid(True)
    ax3.legend()
    
    # Set x-ticks
    ax3.set_xticks(alpha_range)
    ax3.set_xticklabels([f"{a:.1f}" for a in alpha_range])
    
    # Adjust layout and save
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"{unit_name}_norm_comparison.png"), dpi=300)
    plt.close()
    print(f"Comparison plot saved as {unit_name}_norm_comparison.png")


def get_norm_config_str(use_gate_norm, pre_norm, post_norm):
    """Generate a string representation of the normalization configuration."""
    parts = []
    if use_gate_norm:
        parts.append("GateNorm")
    if pre_norm:
        parts.append("PreNorm")
    if post_norm:
        parts.append("PostNorm")
    
    return "_".join(parts) if parts else "NoNorm"


def main():
    """Main function to run benchmarks and generate plots."""
    args = parse_args()
    
    # Setup device
    device = get_device(args.device)
    print(f"Using device: {device}")
    
    # Configuration
    batch_size = args.batch_size
    input_dim = args.dim
    output_dim = args.dim
    alpha_range = np.arange(0.0, 1.1, 0.1)
    
    # Generate random input
    torch.manual_seed(42)  # For reproducibility
    input_tensor = torch.randn(batch_size, input_dim).to(device)
    
    # Define units to benchmark
    units = [
        (paGLU, "paGLU"),
        (paGTU, "paGTU"),
        (paSwishU, "paSwishU"),
        (paReGLU, "paReGLU"),
        (paGELU, "paGELU"),
        (paMishU, "paMishU"),
        (paSiLU, "paSiLU")
    ]
    
    # Define normalization configurations to run
    if args.run_matrix:
        # Run all combinations of normalizations
        norm_configs = [
            (False, False, False),  # No normalization
            (True, False, False),   # Only GateNorm
            (False, True, False),   # Only PreNorm
            (False, False, True),   # Only PostNorm
            (True, True, False),    # GateNorm + PreNorm
            (True, False, True),    # GateNorm + PostNorm
            (False, True, True),    # PreNorm + PostNorm
            (True, True, True),     # All normalizations
        ]
    else:
        # Run only the specified configuration
        norm_configs = [(args.use_gate_norm, args.pre_norm, args.post_norm)]
    
    # Timestamp for output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(args.output_dir, timestamp)
    os.makedirs(output_dir, exist_ok=True)
    
    # For each unit, run all specified norm configurations
    for unit_class, unit_name in units:
        unit_results = {}
        
        for use_gate_norm, pre_norm, post_norm in norm_configs:
            # Get the normalization config string
            norm_config = get_norm_config_str(use_gate_norm, pre_norm, post_norm)
            
            # Run benchmark
            results = benchmark_unit(
                unit_class, 
                input_tensor, 
                alpha_range, 
                device, 
                batch_size,
                input_dim,
                output_dim,
                use_gate_norm=use_gate_norm,
                pre_norm=pre_norm,
                post_norm=post_norm
            )
            
            # Save results
            unit_results[norm_config] = results
            
            # Plot individual results
            plot_results(unit_name, results, output_dir, norm_config)
            
            # Save to CSV
            save_results_to_csv(unit_name, results, output_dir, norm_config)
        
        # Plot comparison of all norm configurations
        if len(norm_configs) > 1:
            plot_comparison(unit_name, unit_results, alpha_range, output_dir)
    
    # Create a summary file
    with open(os.path.join(output_dir, "benchmark_summary.txt"), "w") as f:
        f.write(f"paGating Benchmark Summary\n")
        f.write(f"========================\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Device: {device}\n")
        f.write(f"Batch Size: {batch_size}\n")
        f.write(f"Input/Output Dimensions: {input_dim}/{output_dim}\n")
        f.write(f"Alpha Range: {alpha_range[0]} to {alpha_range[-1]}\n")
        f.write(f"Normalization Configurations: {len(norm_configs)}\n")
        
        for i, (use_gate_norm, pre_norm, post_norm) in enumerate(norm_configs):
            config_str = get_norm_config_str(use_gate_norm, pre_norm, post_norm)
            f.write(f"  {i+1}. {config_str}\n")
        
        f.write(f"\nUnits Benchmarked: {len(units)}\n")
        for unit_class, unit_name in units:
            f.write(f"  - {unit_name}\n")
    
    print(f"\nBenchmarks completed. Results saved to {output_dir}")


if __name__ == "__main__":
    main()