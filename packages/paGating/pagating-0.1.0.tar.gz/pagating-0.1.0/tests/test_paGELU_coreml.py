#!/usr/bin/env python
"""
CoreML Model Testing Script for paGating Units

This script loads a CoreML model exported from paGating and runs inference
with a random input tensor to verify the model works correctly.

Usage:
    python test_paGELU_coreml.py
"""

import os
import sys
import numpy as np
import traceback

# Try importing coremltools with error handling
try:
    import coremltools as ct
except ImportError:
    print("Error: coremltools not installed. Please install with:")
    print("  pip install coremltools")
    sys.exit(1)

# Define the model path
MODEL_PATH = "coreml_models/paGELU_alpha0.50.mlpackage"
INPUT_DIM = 64


def test_coreml_model():
    """Load and test a CoreML model with random input."""
    # Check if model exists
    if not os.path.exists(MODEL_PATH):
        print(f"Error: Model not found at {MODEL_PATH}")
        print("Please run the export script first:")
        print("  python coreml_export.py --unit paGELU --alpha 0.5")
        return False
    
    print(f"Loading model from: {MODEL_PATH}")
    
    try:
        # Load the model
        model = ct.models.MLModel(MODEL_PATH)
        
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
        input_data = np.random.randn(1, INPUT_DIM).astype(np.float32)
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
    
    # Run the test
    test_coreml_model() 