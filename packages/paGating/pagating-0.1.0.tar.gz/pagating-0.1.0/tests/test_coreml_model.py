#!/usr/bin/env python
"""
Generic CoreML Model Testing Script for paGating Units

This script loads a CoreML model exported from paGating and runs inference
with a random input tensor to verify the model works correctly.

Usage:
    python test_coreml_model.py --unit paGELU --alpha 0.5
    python test_coreml_model.py --model coreml_models/paGLU_alpha0.25.mlpackage
"""

import os
import sys
import argparse
import numpy as np
import traceback

# Try importing coremltools with error handling
try:
    import coremltools as ct
except ImportError:
    print("Error: coremltools not installed. Please install with:")
    print("  pip install coremltools")
    sys.exit(1)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Test a CoreML model exported from paGating"
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    
    group.add_argument(
        "--model",
        type=str,
        help="Path to the CoreML model (.mlpackage or .mlmodel)"
    )
    
    group.add_argument(
        "--unit",
        type=str,
        choices=["paGLU", "paGTU", "paSwishU", "paReGLU", "paGELU", "paMishU", "paSiLU"],
        help="paGating unit to test (requires --alpha)"
    )
    
    parser.add_argument(
        "--alpha",
        type=float,
        help="Alpha value used for export (required when --unit is used)"
    )
    
    parser.add_argument(
        "--input-dim",
        type=int,
        default=64,
        help="Input dimension (default: 64)"
    )
    
    return parser.parse_args()


def get_model_path(args):
    """Determine the model path based on arguments."""
    if args.model:
        return args.model
    
    if args.unit and args.alpha is not None:
        # Determine file extension based on apparent coremltools version
        try:
            ct_version = float('.'.join(ct.__version__.split('.')[:2]))
            extension = ".mlpackage" if ct_version >= 6.0 else ".mlmodel"
        except (ValueError, AttributeError):
            # Default to .mlpackage if version parsing fails
            extension = ".mlpackage"
        
        return f"coreml_models/{args.unit}_alpha{args.alpha:.2f}{extension}"
    
    print("Error: When using --unit, you must also specify --alpha")
    sys.exit(1)


def test_coreml_model(model_path, input_dim=64):
    """Load and test a CoreML model with random input."""
    # Check if model exists
    if not os.path.exists(model_path):
        print(f"Error: Model not found at {model_path}")
        if "alpha" in model_path:
            unit = model_path.split("/")[-1].split("_")[0]
            alpha = float(model_path.split("alpha")[-1].split(".")[0])
            print(f"Please run the export script first:")
            print(f"  python coreml_export.py --unit {unit} --alpha {alpha}")
        return False
    
    print(f"Loading model from: {model_path}")
    
    try:
        # Load the model
        model = ct.models.MLModel(model_path)
        
        # Print model metadata
        print("\nModel Metadata:")
        print(f"  Author: {model.author}")
        print(f"  License: {model.license}")
        print(f"  Version: {model.version}")
        print(f"  Description: {model.short_description}")
        
        # Get input/output descriptions
        spec = model.get_spec()
        input_descriptions = spec.description.input
        output_descriptions = spec.description.output
        
        print("\nInput Specification:")
        for input_desc in input_descriptions:
            print(f"  Name: {input_desc.name}")
            shape = [dim for dim in input_desc.type.multiArrayType.shape]
            print(f"  Shape: {shape}")
            print(f"  Type: {input_desc.type.multiArrayType.dataType}")
        
        print("\nOutput Specification:")
        for output_desc in output_descriptions:
            print(f"  Name: {output_desc.name}")
            shape = [dim for dim in output_desc.type.multiArrayType.shape]
            print(f"  Shape: {shape}")
            print(f"  Type: {output_desc.type.multiArrayType.dataType}")
        
        # Generate random input
        print("\nGenerating random input tensor...")
        np.random.seed(42)  # For reproducibility
        input_data = np.random.randn(1, input_dim).astype(np.float32)
        print(f"Input shape: {input_data.shape}")
        print(f"Input preview (first 5 values): {input_data[0, :5]}")
        
        # Prepare input dictionary
        input_dict = {"input": input_data}
        
        # Check if we can run inference natively
        can_use_native = check_coreml_runtime()
        
        # Run inference
        print("\nRunning inference...")
        predictions = model.predict(input_dict)
        
        # Get the output
        output_name = output_descriptions[0].name
        output = predictions[output_name]
        
        # Print results
        print("\nInference Results:")
        print(f"  Output shape: {output.shape}")
        print(f"  Output preview (first 5 values): {output[0, :5]}")
        print(f"  Output mean: {np.mean(output):.6f}")
        print(f"  Output std: {np.std(output):.6f}")
        print(f"  Output min: {np.min(output):.6f}")
        print(f"  Output max: {np.max(output):.6f}")
        
        print("\n✅ CoreML model test completed successfully!")
        return True
    
    except Exception as e:
        print(f"\nError testing CoreML model: {e}")
        traceback.print_exc()
        return False


def check_coreml_runtime():
    """Check if CoreML runtime is available for native execution."""
    try:
        # Try to import the CT runtime
        import coremltools.libcoremlpython as _
        
        # Check if we're on macOS
        if sys.platform != 'darwin':
            print("\nWarning: Native CoreML inference is only supported on macOS.")
            print("Falling back to the coremltools Python runtime.")
            return False
        
        # On macOS, we can use CT runtime directly
        print("\nNative CoreML runtime is available. Using optimized execution.")
        return True
    
    except ImportError:
        print("\nWarning: Native CoreML runtime not available.")
        print("Falling back to the coremltools Python runtime.")
        return False


if __name__ == "__main__":
    print(f"coremltools version: {ct.__version__}")
    
    # Parse arguments
    args = parse_arguments()
    
    # Get model path
    model_path = get_model_path(args)
    
    # Run the test
    test_coreml_model(model_path, args.input_dim) 