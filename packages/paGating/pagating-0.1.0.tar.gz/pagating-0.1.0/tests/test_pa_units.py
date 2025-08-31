import pytest
import torch
import numpy as np
from torch.autograd import gradcheck

from paGating.paGLU import paGLU
from paGating.paGTU import paGTU
from paGating.paSwishU import paSwishU
from paGating.paReGLU import paReGLU
from paGating.paGELU import paGELU
from paGating.paMishU import paMishU
from paGating.paSiLU import paSiLU


# Set reproducible seed
torch.manual_seed(42)
np.random.seed(42)

# Set default dtype to float32 to avoid gradcheck issues
torch.set_default_dtype(torch.float32)

# List of all paGating unit classes to test
PA_UNITS = [paGLU, paGTU, paSwishU, paReGLU, paGELU, paMishU, paSiLU]

# Test parameters
BATCH_SIZE = 32
INPUT_DIM = 16
OUTPUT_DIM = 24


def get_device():
    """Get available device (MPS if available, otherwise CPU)."""
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


@pytest.fixture
def input_tensor():
    """Create a reproducible input tensor for testing."""
    return torch.randn(BATCH_SIZE, INPUT_DIM)


@pytest.mark.parametrize("unit_class", PA_UNITS)
@pytest.mark.parametrize("alpha", [0.0, 0.5, 1.0])
def test_forward_static_alpha(unit_class, alpha, input_tensor):
    """Test forward pass with static alpha values."""
    # Create unit
    unit = unit_class(
        input_dim=INPUT_DIM,
        output_dim=OUTPUT_DIM,
        alpha=alpha
    )
    
    # Run forward pass
    output = unit(input_tensor)
    
    # Check output shape and type
    assert output.shape == (BATCH_SIZE, OUTPUT_DIM), f"Expected shape {(BATCH_SIZE, OUTPUT_DIM)}, got {output.shape}"
    assert output.dtype == torch.float32, f"Expected dtype float32, got {output.dtype}"
    
    # Check that alpha was correctly set
    actual_alpha = unit.get_alpha()
    assert torch.isclose(actual_alpha, torch.tensor(alpha)), f"Expected alpha {alpha}, got {actual_alpha.item()}"


@pytest.mark.parametrize("unit_class", PA_UNITS)
def test_forward_learnable_alpha(unit_class, input_tensor):
    """Test forward pass with learnable alpha."""
    # Create unit with learnable alpha
    unit = unit_class(
        input_dim=INPUT_DIM,
        output_dim=OUTPUT_DIM,
        alpha="learnable"
    )
    
    # Run forward pass
    output = unit(input_tensor)
    
    # Check output shape and type
    assert output.shape == (BATCH_SIZE, OUTPUT_DIM), f"Expected shape {(BATCH_SIZE, OUTPUT_DIM)}, got {output.shape}"
    
    # Verify that alpha_param exists and is a parameter
    assert unit.alpha_param is not None, "Learnable alpha parameter should exist"
    assert isinstance(unit.alpha_param, torch.nn.Parameter), "Alpha should be a torch.nn.Parameter"
    assert unit.alpha_param.requires_grad, "Alpha parameter should have requires_grad=True"
    
    # Check that alpha is in valid range [0,1] after sigmoid
    alpha = unit.get_alpha()
    assert 0.0 <= alpha.item() <= 1.0, f"Alpha value {alpha.item()} not in range [0,1]"


@pytest.mark.parametrize("unit_class", PA_UNITS)
def test_forward_callable_alpha(unit_class, input_tensor):
    """Test forward pass with callable alpha."""
    # Define a simple callable alpha function
    def alpha_fn(x):
        # Return an alpha based on mean of input
        return torch.sigmoid(torch.mean(x) * 0.1 + 0.5)
    
    # Create unit with callable alpha
    unit = unit_class(
        input_dim=INPUT_DIM,
        output_dim=OUTPUT_DIM,
        alpha=alpha_fn
    )
    
    # Run forward pass
    output = unit(input_tensor)
    
    # Check output shape
    assert output.shape == (BATCH_SIZE, OUTPUT_DIM), f"Expected shape {(BATCH_SIZE, OUTPUT_DIM)}, got {output.shape}"
    
    # Verify that alpha is computed correctly
    alpha = unit.get_alpha(input_tensor)
    assert 0.0 <= alpha.item() <= 1.0, f"Alpha value {alpha.item()} not in range [0,1]"
    
    # Call alpha_fn directly and compare
    expected_alpha = alpha_fn(input_tensor)
    assert torch.isclose(alpha, expected_alpha), f"Expected alpha {expected_alpha.item()}, got {alpha.item()}"


@pytest.mark.parametrize("unit_class", PA_UNITS)
def test_output_shape(unit_class):
    """Test that output shape is correct for various input batch sizes."""
    batch_sizes = [1, 8, 32, 64]
    
    for batch_size in batch_sizes:
        # Create input
        x = torch.randn(batch_size, INPUT_DIM)
        
        # Create unit
        unit = unit_class(
            input_dim=INPUT_DIM,
            output_dim=OUTPUT_DIM,
            alpha=0.5
        )
        
        # Run forward pass
        output = unit(x)
        
        # Check output shape
        assert output.shape == (batch_size, OUTPUT_DIM), \
            f"Expected shape ({batch_size}, {OUTPUT_DIM}), got {output.shape}"


@pytest.mark.parametrize("unit_class", PA_UNITS)
def test_gradient_flow(unit_class):
    """Test that gradients flow properly through the unit."""
    # Create small tensors for gradient checking
    x = torch.randn(4, 8, requires_grad=True, dtype=torch.float64)
    
    # Create unit
    unit = unit_class(
        input_dim=8,
        output_dim=12,
        alpha=0.5
    ).double()  # Use double precision for gradcheck
    
    # Define a function for gradcheck
    def func(x):
        return unit(x).sum()
    
    # Check gradients
    result = gradcheck(func, (x,), eps=1e-6, atol=1e-4)
    assert result, "Gradient check failed"


@pytest.mark.parametrize("unit_class", PA_UNITS)
def test_backward_pass(unit_class, input_tensor):
    """Test that backward pass works and computes gradients."""
    # Ensure input requires grad
    x = input_tensor.clone().requires_grad_(True)
    
    # Create unit
    unit = unit_class(
        input_dim=INPUT_DIM,
        output_dim=OUTPUT_DIM,
        alpha="learnable"  # Use learnable alpha to test its gradient too
    )
    
    # Run forward pass
    output = unit(x)
    
    # Create a dummy loss and run backward pass
    loss = output.sum()
    loss.backward()
    
    # Check that gradients were computed
    assert x.grad is not None, "Input gradient should not be None"
    assert unit.value_proj.weight.grad is not None, "Value projection weight gradient should not be None"
    assert unit.gate_proj.weight.grad is not None, "Gate projection weight gradient should not be None"
    assert unit.alpha_param.grad is not None, "Alpha parameter gradient should not be None"


@pytest.mark.parametrize("unit_class", PA_UNITS)
def test_device_compatibility(unit_class, input_tensor):
    """Test that units work on both CPU and MPS if available."""
    devices = ["cpu"]
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        devices.append("mps")
    
    for device_str in devices:
        device = torch.device(device_str)
        
        # Create unit on device
        unit = unit_class(
            input_dim=INPUT_DIM,
            output_dim=OUTPUT_DIM,
            alpha=0.5
        ).to(device)
        
        # Move input to device
        x = input_tensor.to(device)
        
        # Run forward pass
        output = unit(x)
        
        # Verify output is on the correct device type (ignoring index)
        assert output.device.type == device.type, \
            f"Output should be on device type {device.type}, but is on {output.device.type}"
        
        # Verify shape is correct
        assert output.shape == (BATCH_SIZE, OUTPUT_DIM), \
            f"Expected shape {(BATCH_SIZE, OUTPUT_DIM)}, got {output.shape}"


if __name__ == "__main__":
    pytest.main(["-v"])