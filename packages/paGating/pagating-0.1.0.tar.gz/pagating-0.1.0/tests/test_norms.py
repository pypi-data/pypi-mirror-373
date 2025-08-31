import pytest
import torch
import numpy as np
from torch.autograd import gradcheck

# Import the normalization components and paGating units
from paGating.norms import GateNorm, PrePostNormWrapper
from paGating import paGLU, paGELU

# Set reproducible seed
torch.manual_seed(42)
np.random.seed(42)

# Test parameters
BATCH_SIZE = 32
INPUT_DIM = 16
OUTPUT_DIM = 24
EPS = 1e-5


def test_gate_norm_forward():
    """Test forward pass of GateNorm."""
    # Create a random input tensor
    x = torch.randn(BATCH_SIZE, INPUT_DIM)
    
    # Create a GateNorm instance
    norm = GateNorm(INPUT_DIM)
    
    # Forward pass
    y = norm(x)
    
    # Check shape remains the same
    assert y.shape == x.shape, f"Expected shape {x.shape}, got {y.shape}"
    
    # Check normalization statistics
    mean = y.mean(dim=-1)
    var = y.var(dim=-1, unbiased=False)
    
    # Mean should be close to 0, and variance close to 1
    assert torch.allclose(mean, torch.zeros_like(mean), atol=1e-5), \
        f"Expected mean close to 0, got {mean.mean().item()}"
    assert torch.allclose(var, torch.ones_like(var), atol=1e-3), \
        f"Expected variance close to 1, got {var.mean().item()}"


def test_gate_norm_affine_params():
    """Test the affine parameters of GateNorm."""
    # Create a GateNorm instance with elementwise_affine=True
    norm_with_params = GateNorm(INPUT_DIM, elementwise_affine=True)
    
    # Check that weight and bias exist and are trainable
    assert norm_with_params.weight is not None, "Weight parameter should exist"
    assert norm_with_params.bias is not None, "Bias parameter should exist"
    assert isinstance(norm_with_params.weight, torch.nn.Parameter), "Weight should be a parameter"
    assert isinstance(norm_with_params.bias, torch.nn.Parameter), "Bias should be a parameter"
    
    # Create a GateNorm instance with elementwise_affine=False
    norm_without_params = GateNorm(INPUT_DIM, elementwise_affine=False)
    
    # Check that weight and bias don't exist
    assert norm_without_params.weight is None, "Weight parameter should not exist"
    assert norm_without_params.bias is None, "Bias parameter should not exist"


def test_gate_norm_backward():
    """Test that gradients flow properly through GateNorm."""
    # Create a small tensor for gradient checking
    x = torch.randn(4, 8, requires_grad=True, dtype=torch.float64)
    
    # Create a GateNorm instance
    norm = GateNorm(8).double()  # Use double precision for gradcheck
    
    # Define a function for gradcheck
    def func(x):
        return norm(x).sum()
    
    # Check gradients
    result = gradcheck(func, (x,), eps=1e-6, atol=1e-4)
    assert result, "Gradient check failed"


def test_pre_post_norm_wrapper():
    """Test PrePostNormWrapper with different configurations."""
    # Create a random input tensor
    x = torch.randn(BATCH_SIZE, INPUT_DIM)
    
    # Create a basic paGating unit
    base_unit = paGLU(INPUT_DIM, OUTPUT_DIM, alpha=0.5)
    
    # Test cases: pre_norm, post_norm
    test_cases = [
        (False, False),  # No normalization
        (True, False),   # Pre-norm only
        (False, True),   # Post-norm only
        (True, True)     # Both pre and post norm
    ]
    
    for pre_norm, post_norm in test_cases:
        # Create wrapper
        wrapper = PrePostNormWrapper(
            module=base_unit,
            input_dim=INPUT_DIM,
            output_dim=OUTPUT_DIM,
            pre_norm=pre_norm,
            post_norm=post_norm,
            norm_eps=EPS
        )
        
        # Check that normalization layers exist when they should
        if pre_norm:
            assert wrapper.pre_norm_layer is not None, "Pre-norm layer should exist"
            assert isinstance(wrapper.pre_norm_layer, torch.nn.LayerNorm), "Pre-norm should be LayerNorm"
        else:
            assert wrapper.pre_norm_layer is None, "Pre-norm layer should not exist"
        
        if post_norm:
            assert wrapper.post_norm_layer is not None, "Post-norm layer should exist"
            assert isinstance(wrapper.post_norm_layer, torch.nn.LayerNorm), "Post-norm should be LayerNorm"
        else:
            assert wrapper.post_norm_layer is None, "Post-norm layer should not exist"
        
        # Forward pass should work without errors
        output = wrapper(x)
        
        # Check output shape
        assert output.shape == (BATCH_SIZE, OUTPUT_DIM), \
            f"Expected output shape {(BATCH_SIZE, OUTPUT_DIM)}, got {output.shape}"
        
        # Check statistics for post-norm
        if post_norm:
            mean = output.mean(dim=-1)
            var = output.var(dim=-1, unbiased=False)
            assert torch.allclose(mean, torch.zeros_like(mean), atol=1e-5), \
                f"Expected mean close to 0 for post-norm, got {mean.mean().item()}"
            assert torch.allclose(var, torch.ones_like(var), atol=1e-3), \
                f"Expected variance close to 1 for post-norm, got {var.mean().item()}"


def test_integration_with_pagating():
    """Test integration of normalization with paGating units."""
    # Create a random input tensor
    x = torch.randn(BATCH_SIZE, INPUT_DIM)
    
    # Create paGELU with GateNorm
    unit_with_gate_norm = paGELU(
        input_dim=INPUT_DIM,
        output_dim=OUTPUT_DIM,
        alpha=0.5,
        use_gate_norm=True,
        norm_eps=EPS
    )
    
    # Forward pass
    output = unit_with_gate_norm(x)
    
    # Check output shape
    assert output.shape == (BATCH_SIZE, OUTPUT_DIM), \
        f"Expected output shape {(BATCH_SIZE, OUTPUT_DIM)}, got {output.shape}"
    
    # Create with PrePostNormWrapper
    base_unit = paGELU(
        input_dim=INPUT_DIM,
        output_dim=OUTPUT_DIM,
        alpha=0.5
    )
    
    wrapped_unit = PrePostNormWrapper(
        module=base_unit,
        input_dim=INPUT_DIM,
        output_dim=OUTPUT_DIM,
        pre_norm=True,
        post_norm=True,
        norm_eps=EPS
    )
    
    # Forward pass
    output_wrapped = wrapped_unit(x)
    
    # Check output shape
    assert output_wrapped.shape == (BATCH_SIZE, OUTPUT_DIM), \
        f"Expected output shape {(BATCH_SIZE, OUTPUT_DIM)}, got {output_wrapped.shape}"
    
    # Check if attribute access to wrapped module works
    alpha = wrapped_unit.get_alpha()
    assert alpha.item() == 0.5, f"Expected alpha=0.5, got {alpha.item()}"


def test_complex_norm_setup():
    """Test a complex setup with both GateNorm and PrePostNormWrapper."""
    # Create a random input tensor
    x = torch.randn(BATCH_SIZE, INPUT_DIM)
    
    # Create a paGating unit with GateNorm
    base_unit = paGELU(
        input_dim=INPUT_DIM,
        output_dim=OUTPUT_DIM,
        alpha=0.5,
        use_gate_norm=True,
        norm_eps=EPS
    )
    
    # Wrap with pre/post normalization
    wrapped_unit = PrePostNormWrapper(
        module=base_unit,
        input_dim=INPUT_DIM,
        output_dim=OUTPUT_DIM,
        pre_norm=True,
        post_norm=True,
        norm_eps=EPS
    )
    
    # Forward pass should work without errors
    output = wrapped_unit(x)
    
    # Check output shape
    assert output.shape == (BATCH_SIZE, OUTPUT_DIM), \
        f"Expected output shape {(BATCH_SIZE, OUTPUT_DIM)}, got {output.shape}"
    
    # Check that normalization was applied (post-norm should dominate the statistics)
    mean = output.mean(dim=-1)
    var = output.var(dim=-1, unbiased=False)
    assert torch.allclose(mean, torch.zeros_like(mean), atol=1e-5), \
        f"Expected mean close to 0, got {mean.mean().item()}"
    assert torch.allclose(var, torch.ones_like(var), atol=1e-3), \
        f"Expected variance close to 1, got {var.mean().item()}" 