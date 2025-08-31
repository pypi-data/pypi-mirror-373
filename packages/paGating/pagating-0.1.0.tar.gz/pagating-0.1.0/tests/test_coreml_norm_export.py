"""
Tests for CoreML export with normalization features.

This module validates that paGating units with various normalization
configurations can be successfully exported to CoreML format,
and that the exported models produce outputs consistent with their
PyTorch counterparts.
"""

import os
import sys
import pytest
import torch
import numpy as np
import subprocess
from pathlib import Path

# Set reproducible seed
torch.manual_seed(42)
np.random.seed(42)

# Check if coremltools is available
try:
    import coremltools as ct
    COREMLTOOLS_AVAILABLE = True
except ImportError:
    COREMLTOOLS_AVAILABLE = False

# Skip all tests if coremltools is not available
pytestmark = pytest.mark.skipif(
    not COREMLTOOLS_AVAILABLE,
    reason="coremltools not installed"
)

# Test parameters
INPUT_DIM = 16
OUTPUT_DIM = 16
ALPHA = 0.5
BATCH_SIZE = 1  # CoreML models expect batch size 1 for testing

# Units to test
UNITS_TO_TEST = ["paGLU", "paGELU", "paMishU", "paSiLU"]

# Normalization configurations to test
NORM_CONFIGS = [
    {"use_gate_norm": True, "pre_norm": False, "post_norm": False},   # Only GateNorm
    {"use_gate_norm": False, "pre_norm": True, "post_norm": False},   # Only PreNorm
    {"use_gate_norm": False, "pre_norm": False, "post_norm": True},   # Only PostNorm
    {"use_gate_norm": True, "pre_norm": True, "post_norm": True},     # All normalizations
]


def get_export_script_path():
    """Get the path to the CoreML export script."""
    # Start with the current file's directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Try to find coreml_export.py in parent directory
    export_script = os.path.join(os.path.dirname(current_dir), "coreml_export.py")
    
    if os.path.isfile(export_script):
        return export_script
    
    # If not found, search for it
    for root, _, files in os.walk(os.path.dirname(current_dir)):
        if "coreml_export.py" in files:
            return os.path.join(root, "coreml_export.py")
    
    raise FileNotFoundError("Could not find coreml_export.py script")


def run_export_command(unit, alpha, norm_config, input_dim, output_dim):
    """Run the CoreML export command with the specified parameters."""
    export_script = get_export_script_path()
    
    # Build the command
    cmd = [
        sys.executable,
        export_script,
        "--unit", unit,
        "--alpha", str(alpha),
        "--input-dim", str(input_dim),
        "--output-dim", str(output_dim),
    ]
    
    # Add normalization flags if needed
    if norm_config["use_gate_norm"]:
        cmd.append("--use-gate-norm")
    if norm_config["pre_norm"]:
        cmd.append("--pre-norm")
    if norm_config["post_norm"]:
        cmd.append("--post-norm")
    
    # Run the command
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Check for errors
    if result.returncode != 0:
        print(f"Export command failed: {result.stderr}")
        return None
    
    # Extract the output path from the output
    output_lines = result.stdout.split("\n")
    for line in output_lines:
        if "CoreML model saved to:" in line:
            output_path = line.split(":", 1)[1].strip()
            return output_path
    
    return None


@pytest.mark.parametrize("unit", UNITS_TO_TEST)
@pytest.mark.parametrize("norm_config", NORM_CONFIGS)
def test_coreml_export_succeeds(unit, norm_config):
    """Test that CoreML export succeeds with normalization configurations."""
    # Skip if CoreML tools are not available
    if not COREMLTOOLS_AVAILABLE:
        pytest.skip("coremltools not installed")
    
    # Only run on macOS (CoreML's primary platform)
    if sys.platform != "darwin":
        pytest.skip("CoreML tests are only run on macOS")
    
    # Run the export command
    output_path = run_export_command(
        unit=unit,
        alpha=ALPHA,
        norm_config=norm_config,
        input_dim=INPUT_DIM,
        output_dim=OUTPUT_DIM
    )
    
    # Check that export succeeded
    assert output_path is not None, "CoreML export failed"
    assert os.path.exists(output_path), f"Export file not found: {output_path}"
    
    # Clean up
    if os.path.exists(output_path) and os.path.isdir(output_path):
        # For .mlpackage (directory), just check its existence
        assert True, "CoreML export succeeded"
    elif os.path.exists(output_path):
        # For .mlmodel (file), check its size
        assert os.path.getsize(output_path) > 0, "CoreML model file is empty"


@pytest.mark.parametrize("unit", ["paGLU"])  # Test with just one unit for speed
@pytest.mark.parametrize("norm_config", NORM_CONFIGS)
def test_coreml_model_inference(unit, norm_config):
    """Test that exported CoreML models can run inference."""
    # Skip if CoreML tools are not available
    if not COREMLTOOLS_AVAILABLE:
        pytest.skip("coremltools not installed")
    
    # Only run on macOS (CoreML's primary platform)
    if sys.platform != "darwin":
        pytest.skip("CoreML tests are only run on macOS")
    
    # Run the export command
    output_path = run_export_command(
        unit=unit,
        alpha=ALPHA,
        norm_config=norm_config,
        input_dim=INPUT_DIM,
        output_dim=OUTPUT_DIM
    )
    
    # Check that export succeeded
    assert output_path is not None, "CoreML export failed"
    assert os.path.exists(output_path), f"Export file not found: {output_path}"
    
    try:
        # Load the CoreML model
        model = ct.models.MLModel(output_path)
        
        # Generate random input data
        np.random.seed(42)  # For reproducibility
        input_data = np.random.rand(BATCH_SIZE, INPUT_DIM).astype(np.float32)
        
        # Run inference
        input_dict = {"input": input_data}
        predictions = model.predict(input_dict)
        
        # Check that output exists and has the right shape
        output_key = list(predictions.keys())[0] if isinstance(predictions, dict) else None
        output = predictions[output_key] if output_key else predictions
        
        assert output is not None, "CoreML model returned None"
        assert output.shape == (BATCH_SIZE, OUTPUT_DIM), f"Wrong output shape: {output.shape}"
        assert not np.isnan(output).any(), "Output contains NaN values"
        
        # For post-norm configurations, check statistics
        if norm_config["post_norm"]:
            # Output mean should be close to 0 and variance close to 1
            output_mean = np.mean(output, axis=1)
            output_var = np.var(output, axis=1)
            
            assert np.allclose(output_mean, 0, atol=0.1), f"Output mean not close to 0: {output_mean}"
            assert np.allclose(output_var, 1, atol=0.3), f"Output variance not close to 1: {output_var}"
    
    except Exception as e:
        pytest.fail(f"CoreML inference failed: {e}")


@pytest.mark.parametrize("unit", ["paGLU"])  # Test with just one unit for speed
@pytest.mark.parametrize("norm_config", [
    {"use_gate_norm": False, "pre_norm": True, "post_norm": True},   # Pre+Post Norm
])
def test_coreml_pytorch_output_match(unit, norm_config):
    """Test that CoreML outputs match PyTorch model outputs."""
    # Skip if CoreML tools are not available
    if not COREMLTOOLS_AVAILABLE:
        pytest.skip("coremltools not installed")
    
    # Only run on macOS (CoreML's primary platform)
    if sys.platform != "darwin":
        pytest.skip("CoreML tests are only run on macOS")
    
    # Get the PyTorch model
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    try:
        # Import required modules
        from paGating import PrePostNormWrapper
        
        if unit == "paGLU":
            from paGating import paGLU as unit_class
        elif unit == "paGELU":
            from paGating import paGELU as unit_class
        elif unit == "paMishU":
            from paGating import paMishU as unit_class
        elif unit == "paSiLU":
            from paGating import paSiLU as unit_class
        else:
            pytest.fail(f"Unknown unit: {unit}")
        
        # Create the PyTorch model
        base_unit = unit_class(
            input_dim=INPUT_DIM,
            output_dim=OUTPUT_DIM,
            alpha=ALPHA,
            use_gate_norm=norm_config["use_gate_norm"]
        )
        
        # Wrap with pre/post normalization if needed
        if norm_config["pre_norm"] or norm_config["post_norm"]:
            pt_model = PrePostNormWrapper(
                module=base_unit,
                input_dim=INPUT_DIM,
                output_dim=OUTPUT_DIM,
                pre_norm=norm_config["pre_norm"],
                post_norm=norm_config["post_norm"]
            )
        else:
            pt_model = base_unit
        
        # Set to evaluation mode
        pt_model.eval()
        
        # Run the export command
        output_path = run_export_command(
            unit=unit,
            alpha=ALPHA,
            norm_config=norm_config,
            input_dim=INPUT_DIM,
            output_dim=OUTPUT_DIM
        )
        
        # Check that export succeeded
        assert output_path is not None, "CoreML export failed"
        assert os.path.exists(output_path), f"Export file not found: {output_path}"
        
        # Load the CoreML model
        coreml_model = ct.models.MLModel(output_path)
        
        # Generate random input data
        np.random.seed(42)  # For reproducibility
        input_np = np.random.rand(BATCH_SIZE, INPUT_DIM).astype(np.float32)
        input_tensor = torch.tensor(input_np, dtype=torch.float32)
        
        # Run inference with PyTorch model
        with torch.no_grad():
            pt_output = pt_model(input_tensor).numpy()
        
        # Run inference with CoreML model
        input_dict = {"input": input_np}
        coreml_predictions = coreml_model.predict(input_dict)
        
        # Get the output from CoreML predictions
        output_key = list(coreml_predictions.keys())[0] if isinstance(coreml_predictions, dict) else None
        coreml_output = coreml_predictions[output_key] if output_key else coreml_predictions
        
        # Compare outputs
        assert coreml_output.shape == pt_output.shape, "Output shapes don't match"
        
        # Note: CoreML may not produce exactly the same results due to precision differences
        # So we allow for a larger tolerance
        assert np.allclose(coreml_output, pt_output, atol=0.1), "Outputs don't match"
    
    except Exception as e:
        pytest.fail(f"Comparison failed: {e}")
    finally:
        # Clean up
        if 0 in sys.path:
            sys.path.pop(0)


if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 