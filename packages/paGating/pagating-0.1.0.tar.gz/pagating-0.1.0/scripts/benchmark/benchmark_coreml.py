#!/usr/bin/env python
"""
CoreML Model Benchmarking Script for paGating Units

This script measures the inference performance of a CoreML model exported
from paGating with different compute units (CPU, GPU, NE, ALL).

Usage:
    python benchmark_coreml.py --model coreml_models/paGELU_alpha0.50.mlpackage --runs 200 --device NE
"""

import os
import sys
import time
import argparse
import numpy as np
import traceback
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple

# Try importing coremltools with error handling
try:
    import coremltools as ct
except ImportError:
    print("Error: coremltools not installed. Please install with:")
    print("  pip install coremltools")
    sys.exit(1)


# Define device options - based on available CT compute units
class ComputeDevice(str, Enum):
    ALL = "ALL"          # Use all available compute units
    CPU = "CPU"          # CPU only
    CPU_AND_GPU = "GPU"  # CPU and GPU
    CPU_AND_NE = "NE"    # CPU and Neural Engine (Apple Silicon only)


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Benchmark a CoreML model exported from paGating"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        required=True,
        help="Path to the CoreML model (.mlpackage or .mlmodel)"
    )
    
    parser.add_argument(
        "--runs",
        type=int,
        default=100,
        help="Number of inference runs to perform (default: 100)"
    )
    
    parser.add_argument(
        "--device",
        type=str,
        choices=[d.value for d in ComputeDevice],
        default=ComputeDevice.ALL.value,
        help="Compute device to use for inference (default: ALL)"
    )
    
    parser.add_argument(
        "--warmup",
        type=int,
        default=10,
        help="Number of warmup runs before benchmarking (default: 10)"
    )
    
    parser.add_argument(
        "--input-dim",
        type=int,
        default=64,
        help="Input dimension (default: 64)"
    )
    
    return parser.parse_args()


def get_compute_unit(device_str: str) -> ct.ComputeUnit:
    """Convert device string to coremltools ComputeUnit."""
    device_map = {
        ComputeDevice.ALL.value: ct.ComputeUnit.ALL,
        ComputeDevice.CPU.value: ct.ComputeUnit.CPU_ONLY,
        ComputeDevice.CPU_AND_GPU.value: ct.ComputeUnit.CPU_AND_GPU,
        ComputeDevice.CPU_AND_NE.value: ct.ComputeUnit.CPU_AND_NE
    }
    return device_map[device_str]


def check_compute_support(device_str: str) -> bool:
    """Check if the requested compute unit is available on this device."""
    is_mac = sys.platform == 'darwin'
    
    if not is_mac:
        print(f"Warning: CoreML is optimized for macOS. Running on {sys.platform}")
        return False
    
    if device_str == ComputeDevice.CPU_AND_NE.value:
        # Check if we're on Apple Silicon (M1/M2/etc)
        try:
            import platform
            cpu_info = platform.processor()
            if 'arm' not in cpu_info.lower():
                print(f"Warning: Neural Engine requires Apple Silicon but found: {cpu_info}")
                print("Using CPU_ONLY instead.")
                return False
        except Exception:
            print("Warning: Could not determine processor type.")
    
    # For other devices, assume they are available on macOS
    return True


def print_device_info() -> None:
    """Print information about the device being used."""
    import platform
    
    print("\nDevice Information:")
    print(f"  OS: {platform.system()} {platform.release()}")
    print(f"  Processor: {platform.processor()}")
    
    # Try to get more detailed Apple Silicon info if available
    if sys.platform == 'darwin':
        try:
            import subprocess
            result = subprocess.run(['sysctl', '-n', 'machdep.cpu.brand_string'], 
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            cpu_info = result.stdout.decode('utf-8').strip()
            if cpu_info:
                print(f"  CPU: {cpu_info}")
        except Exception:
            pass


def load_and_prepare_model(
    model_path: str, 
    compute_unit: ct.ComputeUnit
) -> Tuple[ct.models.MLModel, Dict[str, Any], List[str]]:
    """
    Load the CoreML model and prepare for benchmarking.
    
    Args:
        model_path: Path to CoreML model
        compute_unit: Compute unit to use for inference
        
    Returns:
        Tuple of (model, input_dict, output_names)
    """
    print(f"Loading model from: {model_path}")
    
    # Load the model with the specified compute unit
    model = ct.models.MLModel(model_path, compute_units=compute_unit)
    
    # Get model spec
    spec = model.get_spec()
    
    # Get input and output information
    input_descriptions = spec.description.input
    output_descriptions = spec.description.output
    
    print("\nModel Information:")
    print(f"  Description: {model.short_description}")
    
    print("\nInput Specification:")
    input_dict = {}
    for input_desc in input_descriptions:
        print(f"  Name: {input_desc.name}")
        shape = [dim for dim in input_desc.type.multiArrayType.shape]
        print(f"  Shape: {shape}")
        
        # Create random input for this shape
        input_data = np.random.randn(*shape).astype(np.float32)
        input_dict[input_desc.name] = input_data
    
    print("\nOutput Specification:")
    output_names = []
    for output_desc in output_descriptions:
        print(f"  Name: {output_desc.name}")
        shape = [dim for dim in output_desc.type.multiArrayType.shape]
        print(f"  Shape: {shape}")
        output_names.append(output_desc.name)
    
    return model, input_dict, output_names


def analyze_performance(latencies: List[float]) -> Dict[str, float]:
    """
    Analyze performance metrics from latency measurements.
    
    Args:
        latencies: List of latency measurements in seconds
        
    Returns:
        Dictionary of performance metrics
    """
    if not latencies:
        return {
            "avg_ms": 0.0,
            "min_ms": 0.0,
            "max_ms": 0.0,
            "std_ms": 0.0,
            "throughput": 0.0
        }
    
    latencies_ms = [lat * 1000.0 for lat in latencies]  # Convert to ms
    
    avg_ms = np.mean(latencies_ms)
    min_ms = np.min(latencies_ms)
    max_ms = np.max(latencies_ms)
    std_ms = np.std(latencies_ms)
    throughput = 1.0 / np.mean(latencies) if np.mean(latencies) > 0 else 0.0
    
    return {
        "avg_ms": avg_ms,
        "min_ms": min_ms,
        "max_ms": max_ms,
        "std_ms": std_ms,
        "throughput": throughput
    }


def benchmark_model(
    model: ct.models.MLModel, 
    input_dict: Dict[str, Any],
    runs: int,
    warmup: int
) -> Dict[str, float]:
    """
    Benchmark the model with the provided inputs.
    
    Args:
        model: CoreML model to benchmark
        input_dict: Dictionary of input tensors
        runs: Number of benchmark runs
        warmup: Number of warmup runs
    
    Returns:
        Dictionary of performance metrics
    """
    # Perform warmup runs
    print(f"\nPerforming {warmup} warmup runs...")
    for _ in range(warmup):
        model.predict(input_dict)
    
    # Run actual benchmark
    print(f"Running benchmark for {runs} iterations...")
    latencies = []
    try:
        for i in range(runs):
            start_time = time.time()
            model.predict(input_dict)
            end_time = time.time()
            latency = end_time - start_time
            latencies.append(latency)
            
            # Print progress every 10% of runs
            if (i + 1) % max(1, runs // 10) == 0:
                progress = (i + 1) / runs * 100
                print(f"  Progress: {progress:.1f}% ({i + 1}/{runs})")
    except Exception as e:
        print(f"Error during benchmark: {e}")
        traceback.print_exc()
    
    # Analyze results
    metrics = analyze_performance(latencies)
    return metrics


def print_benchmark_results(metrics: Dict[str, float], device: str, runs: int) -> None:
    """Print the benchmark results in a formatted way."""
    print("\n" + "=" * 50)
    print(f"Benchmark Results ({device}, {runs} runs)")
    print("=" * 50)
    print(f"  Average latency:    {metrics['avg_ms']:.3f} ms")
    print(f"  Minimum latency:    {metrics['min_ms']:.3f} ms")
    print(f"  Maximum latency:    {metrics['max_ms']:.3f} ms")
    print(f"  Latency std dev:    {metrics['std_ms']:.3f} ms")
    print(f"  Throughput:         {metrics['throughput']:.2f} inferences/sec")
    print("=" * 50)


def main() -> None:
    """Main function to run the benchmark."""
    print(f"coremltools version: {ct.__version__}")
    
    # Parse arguments
    args = parse_arguments()
    
    # Validate model path
    if not os.path.exists(args.model):
        print(f"Error: Model not found at {args.model}")
        sys.exit(1)
    
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Print device information
    print_device_info()
    
    # Check if the requested compute unit is supported
    device_supported = check_compute_support(args.device)
    compute_unit = get_compute_unit(args.device if device_supported else ComputeDevice.ALL.value)
    
    try:
        # Load model and prepare inputs
        model, input_dict, output_names = load_and_prepare_model(args.model, compute_unit)
        
        # Check if we're using the requested compute unit
        actual_unit = "Unknown"
        if hasattr(model, '_computation_units'):
            actual_unit = str(model._computation_units)
        
        print(f"\nRequested compute unit: {args.device}")
        print(f"Actual compute unit: {actual_unit}")
        
        # Run the benchmark
        metrics = benchmark_model(model, input_dict, args.runs, args.warmup)
        
        # Print results
        print_benchmark_results(metrics, args.device, args.runs)
        
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 