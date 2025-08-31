"""
Tests for ONNX export with normalization features.

This module validates that paGating units with various normalization
configurations can be successfully exported to ONNX format,
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

# Check if onnx and onnxruntime are available
try:
    import onnx
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False

# Skip all tests if ONNX is not available
pytestmark = pytest.mark.skipif(
    not ONNX_AVAILABLE,
    reason="onnx and/or onnxruntime not installed"
)

# Test parameters
INPUT_DIM = 16
OUTPUT_DIM = 16
ALPHA = 0.5
BATCH_SIZE = 4
OPSET_VERSION = 15

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
    """Get the path to the ONNX export script."""
    # Start with the current file's directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Try to find onnx_export.py in parent directory
    export_script = os.path.join(os.path.dirname(current_dir), "onnx_export.py")
    
    if os.path.isfile(export_script):
        return export_script
    
    # If not found, search for it
    for root, _, files in os.walk(os.path.dirname(current_dir)):
        if "onnx_export.py" in files:
            return os.path.join(root, "onnx_export.py")
    
    raise FileNotFoundError("Could not find onnx_export.py script")


def run_export_command(unit, alpha, norm_config, input_dim, output_dim, opset_version):
    """Run the ONNX export command with the specified parameters."""
    export_script = get_export_script_path()
    
    # Build the command
    cmd = [
        sys.executable,
        export_script,
        "--unit", unit,
        "--alpha", str(alpha),
        "--input-dim", str(input_dim),
        "--output-dim", str(output_dim),
        "--opset", str(opset_version)
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
        if "ONNX model saved to:" in line:
            output_path = line.split(":", 1)[1].strip()
            return output_path
    
    return None


@pytest.mark.parametrize("unit", UNITS_TO_TEST)
@pytest.mark.parametrize("norm_config", NORM_CONFIGS)
def test_onnx_export_succeeds(unit, norm_config):
    """Test that ONNX export succeeds with normalization configurations."""
    # Skip if ONNX is not available
    if not ONNX_AVAILABLE:
        pytest.skip("onnx and/or onnxruntime not installed")
    
    # Run the export command
    output_path = run_export_command(
        unit=unit,
        alpha=ALPHA,
        norm_config=norm_config,
        input_dim=INPUT_DIM,
        output_dim=OUTPUT_DIM,
        opset_version=OPSET_VERSION
    )
    
    # Check that export succeeded
    assert output_path is not None, "ONNX export failed"
    assert os.path.exists(output_path), f"Export file not found: {output_path}"
    assert os.path.getsize(output_path) > 0, "ONNX model file is empty"
    
    try:
        # Load and check the model
        onnx_model = onnx.load(output_path)
        onnx.checker.check_model(onnx_model)
        
        # Clean up
        if os.path.exists(output_path):
            os.remove(output_path)
    
    except Exception as e:
        pytest.fail(f"ONNX model validation failed: {e}")


@pytest.mark.parametrize("unit", ["paGLU"])  # Test with just one unit for speed
@pytest.mark.parametrize("norm_config", NORM_CONFIGS)
def test_onnx_model_inference(unit, norm_config):
    """Test that exported ONNX models can run inference."""
    # Skip if ONNX is not available
    if not ONNX_AVAILABLE:
        pytest.skip("onnx and/or onnxruntime not installed")
    
    # Run the export command
    output_path = run_export_command(
        unit=unit,
        alpha=ALPHA,
        norm_config=norm_config,
        input_dim=INPUT_DIM,
        output_dim=OUTPUT_DIM,
        opset_version=OPSET_VERSION
    )
    
    # Check that export succeeded
    assert output_path is not None, "ONNX export failed"
    assert os.path.exists(output_path), f"Export file not found: {output_path}"
    
    try:
        # Create an ONNX Runtime session
        session = ort.InferenceSession(output_path)
        
        # Generate random input data
        np.random.seed(42)  # For reproducibility
        input_data = np.random.rand(BATCH_SIZE, INPUT_DIM).astype(np.float32)
        
        # Run inference
        input_feed = {"input": input_data}
        outputs = session.run(None, input_feed)
        
        # Check that output exists and has the right shape
        assert len(outputs) > 0, "No output from ONNX model"
        output = outputs[0]
        
        assert output is not None, "ONNX model returned None"
        assert output.shape == (BATCH_SIZE, OUTPUT_DIM), f"Wrong output shape: {output.shape}"
        assert not np.isnan(output).any(), "Output contains NaN values"
        
        # For post-norm configurations, check statistics
        if norm_config["post_norm"]:
            # Output mean should be close to 0 and variance close to 1
            output_mean = np.mean(output, axis=1)
            output_var = np.var(output, axis=1)
            
            assert np.allclose(output_mean, 0, atol=0.1), f"Output mean not close to 0: {output_mean}"
            assert np.allclose(output_var, 1, atol=0.3), f"Output variance not close to 1: {output_var}"
            
        # Clean up
        if os.path.exists(output_path):
            os.remove(output_path)
    
    except Exception as e:
        pytest.fail(f"ONNX inference failed: {e}")


@pytest.mark.parametrize("unit", ["paGLU"])
@pytest.mark.parametrize("norm_config", [
    {"use_gate_norm": False, "pre_norm": True, "post_norm": True},   # Pre+Post Norm
])
def test_onnx_pytorch_output_match(unit, norm_config):
    """Test that ONNX outputs match PyTorch model outputs."""
    # Skip if ONNX is not available
    if not ONNX_AVAILABLE:
        pytest.skip("onnx and/or onnxruntime not installed")
    
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
            output_dim=OUTPUT_DIM,
            opset_version=OPSET_VERSION
        )
        
        # Check that export succeeded
        assert output_path is not None, "ONNX export failed"
        assert os.path.exists(output_path), f"Export file not found: {output_path}"
        
        # Create an ONNX Runtime session
        session = ort.InferenceSession(output_path)
        
        # Generate random input data
        np.random.seed(42)  # For reproducibility
        input_np = np.random.rand(BATCH_SIZE, INPUT_DIM).astype(np.float32)
        input_tensor = torch.tensor(input_np, dtype=torch.float32)
        
        # Run inference with PyTorch model
        with torch.no_grad():
            pt_output = pt_model(input_tensor).numpy()
        
        # Run inference with ONNX model
        input_feed = {"input": input_np}
        onnx_outputs = session.run(None, input_feed)
        onnx_output = onnx_outputs[0]
        
        # Compare outputs
        assert onnx_output.shape == pt_output.shape, "Output shapes don't match"
        assert np.allclose(onnx_output, pt_output, atol=1e-5), "Outputs don't match"
        
        # Clean up
        if os.path.exists(output_path):
            os.remove(output_path)
    
    except Exception as e:
        pytest.fail(f"Comparison failed: {e}")
    finally:
        # Clean up
        if 0 in sys.path:
            sys.path.pop(0)


@pytest.mark.parametrize("unit", ["paGLU"])
@pytest.mark.parametrize("norm_config", [
    {"use_gate_norm": True, "pre_norm": True, "post_norm": True},   # All normalizations
])
def test_onnx_opset_versions(unit, norm_config):
    """Test ONNX export with different opset versions."""
    # Skip if ONNX is not available
    if not ONNX_AVAILABLE:
        pytest.skip("onnx and/or onnxruntime not installed")
    
    # Try multiple opset versions
    opset_versions = [15, 17]  # Common opset versions
    
    for opset_version in opset_versions:
        # Run the export command
        output_path = run_export_command(
            unit=unit,
            alpha=ALPHA,
            norm_config=norm_config,
            input_dim=INPUT_DIM,
            output_dim=OUTPUT_DIM,
            opset_version=opset_version
        )
        
        # Check that export succeeded
        assert output_path is not None, f"ONNX export with opset {opset_version} failed"
        assert os.path.exists(output_path), f"Export file not found: {output_path}"
        
        try:
            # Load and check the model
            onnx_model = onnx.load(output_path)
            onnx.checker.check_model(onnx_model)
            
            # Verify the opset version
            assert onnx_model.opset_import[0].version == opset_version, \
                f"Expected opset version {opset_version}, got {onnx_model.opset_import[0].version}"
            
            # Create an ONNX Runtime session
            session = ort.InferenceSession(output_path)
            
            # Generate random input data
            np.random.seed(42)
            input_data = np.random.rand(BATCH_SIZE, INPUT_DIM).astype(np.float32)
            
            # Run inference
            input_feed = {"input": input_data}
            outputs = session.run(None, input_feed)
            
            # Check output shape
            output = outputs[0]
            assert output.shape == (BATCH_SIZE, OUTPUT_DIM), \
                f"Wrong output shape for opset {opset_version}: {output.shape}"
            
            # Clean up
            if os.path.exists(output_path):
                os.remove(output_path)
        
        except Exception as e:
            pytest.fail(f"ONNX validation with opset {opset_version} failed: {e}")


if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 