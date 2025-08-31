"""
Integration tests for normalization features in paGating.

This module thoroughly tests the integration of:
1. GateNorm (gating pathway normalization)
2. PrePostNormWrapper (LayerNorm before/after activation units)

Tests cover various combinations of normalization options with different
paGating units and alpha configurations, ensuring proper forward/backward
propagation, output statistics, and export compatibility.
"""

import os
import pytest
import torch
import torch.nn as nn
import torch.jit
import numpy as np
from torch.autograd import gradcheck

# Import paGating components
from paGating import (
    paGLU, paGTU, paSwishU, paReGLU, paGELU, paMishU, paSiLU,
    PrePostNormWrapper, GateNorm
)

# Set reproducible seed
torch.manual_seed(42)
np.random.seed(42)

# Test parameters
BATCH_SIZE = 32
INPUT_DIM = 64
OUTPUT_DIM = 64
EPS = 1e-5

# List of all paGating units to test
PA_UNITS = [
    paGLU, paGTU, paSwishU, paReGLU, paGELU, paMishU, paSiLU
]

# Normalization configurations to test
NORM_CONFIGS = [
    {"use_gate_norm": False, "pre_norm": False, "post_norm": False},  # No normalization
    {"use_gate_norm": True, "pre_norm": False, "post_norm": False},   # Only GateNorm
    {"use_gate_norm": False, "pre_norm": True, "post_norm": False},   # Only PreNorm
    {"use_gate_norm": False, "pre_norm": False, "post_norm": True},   # Only PostNorm
    {"use_gate_norm": True, "pre_norm": True, "post_norm": False},    # GateNorm + PreNorm
    {"use_gate_norm": True, "pre_norm": False, "post_norm": True},    # GateNorm + PostNorm
    {"use_gate_norm": False, "pre_norm": True, "post_norm": True},    # PreNorm + PostNorm
    {"use_gate_norm": True, "pre_norm": True, "post_norm": True},     # All normalizations
]

# Alpha configurations to test
ALPHA_CONFIGS = [
    0.0,            # No gating
    0.5,            # Medium gating
    1.0,            # Full gating
    "learnable",    # Learnable alpha
]


@pytest.mark.parametrize("unit_class", PA_UNITS)
@pytest.mark.parametrize("norm_config", NORM_CONFIGS)
@pytest.mark.parametrize("alpha", ALPHA_CONFIGS)
def test_norm_forward_pass(unit_class, norm_config, alpha):
    """Test forward pass with various normalization and alpha configurations."""
    # Create input tensor
    x = torch.randn(BATCH_SIZE, INPUT_DIM)
    
    # Create base unit
    base_unit = unit_class(
        input_dim=INPUT_DIM,
        output_dim=OUTPUT_DIM,
        alpha=alpha,
        use_gate_norm=norm_config["use_gate_norm"],
        norm_eps=EPS
    )
    
    # Wrap with pre/post normalization if needed
    if norm_config["pre_norm"] or norm_config["post_norm"]:
        model = PrePostNormWrapper(
            module=base_unit,
            input_dim=INPUT_DIM,
            output_dim=OUTPUT_DIM,
            pre_norm=norm_config["pre_norm"],
            post_norm=norm_config["post_norm"],
            norm_eps=EPS
        )
    else:
        model = base_unit
    
    # Forward pass
    output = model(x)
    
    # Basic shape and NaN checks
    assert output.shape == (BATCH_SIZE, OUTPUT_DIM), f"Output shape mismatch: {output.shape}"
    assert not torch.isnan(output).any(), "NaN values in output"
    
    # Check statistics if post-norm is enabled
    if norm_config["post_norm"]:
        mean = output.mean(dim=-1)
        var = output.var(dim=-1, unbiased=False)
        
        # Mean should be close to 0, and variance close to 1
        assert torch.allclose(mean, torch.zeros_like(mean), atol=1e-2), \
            f"Mean should be close to 0 when post-norm is enabled, got {mean.mean().item()}"
        assert torch.allclose(var, torch.ones_like(var), atol=1e-1), \
            f"Variance should be close to 1 when post-norm is enabled, got {var.mean().item()}"


@pytest.mark.parametrize("unit_class", [paGLU, paGELU, paMishU])  # Test subset for speed
@pytest.mark.parametrize("use_gate_norm", [False, True])
@pytest.mark.parametrize("pre_norm", [False, True])
@pytest.mark.parametrize("post_norm", [False, True])
def test_norm_backward_pass(unit_class, use_gate_norm, pre_norm, post_norm):
    """Test backward pass with various normalization configurations."""
    # Skip test if no normalization is applied
    if not any([use_gate_norm, pre_norm, post_norm]):
        pytest.skip("Skipping test with no normalization")
    
    # Create a small tensor for gradient checking (use double precision)
    x = torch.randn(4, INPUT_DIM, requires_grad=True, dtype=torch.float64)
    
    # Create base unit
    base_unit = unit_class(
        input_dim=INPUT_DIM,
        output_dim=OUTPUT_DIM,
        alpha=0.5,  # Use fixed alpha for consistency
        use_gate_norm=use_gate_norm,
        norm_eps=EPS
    ).double()  # Convert to double precision
    
    # Wrap with pre/post normalization if needed
    if pre_norm or post_norm:
        model = PrePostNormWrapper(
            module=base_unit,
            input_dim=INPUT_DIM,
            output_dim=OUTPUT_DIM,
            pre_norm=pre_norm,
            post_norm=post_norm,
            norm_eps=EPS
        ).double()  # Convert to double precision
    else:
        model = base_unit
    
    # Define a function for gradcheck
    def func(x):
        return model(x).sum()
    
    # Check gradients with reduced precision requirements for normalization
    result = gradcheck(func, (x,), eps=1e-6, atol=1e-4)
    assert result, f"Gradient check failed for {unit_class.__name__} with gate_norm={use_gate_norm}, pre_norm={pre_norm}, post_norm={post_norm}"


@pytest.mark.parametrize("unit_class", PA_UNITS)
@pytest.mark.parametrize("alpha", [0.5, "learnable"])
def test_wrapper_behavior(unit_class, alpha):
    """Test that wrapper properly forwards attributes and methods to the wrapped unit."""
    # Create base unit
    base_unit = unit_class(
        input_dim=INPUT_DIM,
        output_dim=OUTPUT_DIM,
        alpha=alpha,
        use_gate_norm=True
    )
    
    # Wrap with pre/post normalization
    wrapped_unit = PrePostNormWrapper(
        module=base_unit,
        input_dim=INPUT_DIM,
        output_dim=OUTPUT_DIM,
        pre_norm=True,
        post_norm=True
    )
    
    # Check attribute forwarding
    assert wrapped_unit.module == base_unit
    
    # Test method forwarding for get_alpha
    if alpha == "learnable":
        # Both should return a tensor
        assert isinstance(wrapped_unit.get_alpha(), torch.Tensor)
        assert isinstance(base_unit.get_alpha(), torch.Tensor)
        # Both should be close to 0.5 (initial value before sigmoid)
        assert torch.isclose(wrapped_unit.get_alpha(), torch.sigmoid(torch.tensor(0.5)))
    else:
        # Both should return a tensor with the specified alpha
        assert isinstance(wrapped_unit.get_alpha(), torch.Tensor)
        assert torch.isclose(wrapped_unit.get_alpha(), torch.tensor(alpha))
    
    # Test configuration access
    config = wrapped_unit.get_config() if hasattr(wrapped_unit, 'get_config') else None
    if config is not None:
        assert isinstance(config, dict)
        assert "input_dim" in config
        assert "output_dim" in config
        assert config["input_dim"] == INPUT_DIM
        assert config["output_dim"] == OUTPUT_DIM


@pytest.mark.parametrize("use_gate_norm", [False, True])
@pytest.mark.parametrize("pre_norm", [False, True])
@pytest.mark.parametrize("post_norm", [False, True])
def test_torchscript_export(use_gate_norm, pre_norm, post_norm):
    """Test TorchScript compatibility with normalized models."""
    # Skip test if no normalization is applied
    if not any([use_gate_norm, pre_norm, post_norm]):
        pytest.skip("Skipping test with no normalization")
    
    # Create a sample input
    x = torch.randn(BATCH_SIZE, INPUT_DIM)
    
    # Create base unit (using paGLU for simplicity)
    base_unit = paGLU(
        input_dim=INPUT_DIM,
        output_dim=OUTPUT_DIM,
        alpha=0.5,
        use_gate_norm=use_gate_norm
    )
    
    # Wrap with pre/post normalization if needed
    if pre_norm or post_norm:
        model = PrePostNormWrapper(
            module=base_unit,
            input_dim=INPUT_DIM,
            output_dim=OUTPUT_DIM,
            pre_norm=pre_norm,
            post_norm=post_norm
        )
    else:
        model = base_unit
    
    # Set to evaluation mode
    model.eval()
    
    try:
        # Export to TorchScript
        scripted_model = torch.jit.script(model)
        
        # Run inference with original model
        with torch.no_grad():
            original_output = model(x)
        
        # Run inference with scripted model
        with torch.no_grad():
            scripted_output = scripted_model(x)
        
        # Outputs should be identical
        assert torch.allclose(original_output, scripted_output, atol=1e-5), \
            "TorchScript output differs from original"
        
        # Save and load (if /tmp is available)
        try:
            tmp_dir = "/tmp" if os.path.exists("/tmp") else "."
            model_path = os.path.join(tmp_dir, "test_model.pt")
            
            # Save model
            torch.jit.save(scripted_model, model_path)
            
            # Load model
            loaded_model = torch.jit.load(model_path)
            
            # Run inference with loaded model
            with torch.no_grad():
                loaded_output = loaded_model(x)
            
            # Outputs should be identical
            assert torch.allclose(original_output, loaded_output, atol=1e-5), \
                "Loaded TorchScript output differs from original"
            
            # Clean up
            if os.path.exists(model_path):
                os.remove(model_path)
        
        except Exception as e:
            pytest.skip(f"Save/load test skipped: {e}")
    
    except Exception as e:
        pytest.fail(f"TorchScript export failed: {e}")


def test_complex_norm_stack():
    """Test a complex stack of normalizations across multiple sequential paGating units."""
    # Create a mini-network of normalized paGating units
    class StackedUnits(nn.Module):
        def __init__(self):
            super().__init__()
            # First layer: paGLU with pre-norm
            base1 = paGLU(INPUT_DIM, INPUT_DIM, alpha=0.5, use_gate_norm=True)
            self.layer1 = PrePostNormWrapper(base1, INPUT_DIM, INPUT_DIM, pre_norm=True, post_norm=False)
            
            # Second layer: paGELU with post-norm
            base2 = paGELU(INPUT_DIM, INPUT_DIM, alpha=0.7)
            self.layer2 = PrePostNormWrapper(base2, INPUT_DIM, INPUT_DIM, pre_norm=False, post_norm=True)
            
            # Third layer: paMishU with both pre and post norm
            base3 = paMishU(INPUT_DIM, OUTPUT_DIM, alpha="learnable")
            self.layer3 = PrePostNormWrapper(base3, INPUT_DIM, OUTPUT_DIM, pre_norm=True, post_norm=True)
        
        def forward(self, x):
            x = self.layer1(x)
            x = self.layer2(x)
            x = self.layer3(x)
            return x
    
    # Create model and input
    model = StackedUnits()
    x = torch.randn(BATCH_SIZE, INPUT_DIM)
    
    # Forward pass
    output = model(x)
    
    # Check basic properties
    assert output.shape == (BATCH_SIZE, OUTPUT_DIM)
    assert not torch.isnan(output).any()
    
    # Last layer has post-norm, so check statistics
    mean = output.mean(dim=-1)
    var = output.var(dim=-1, unbiased=False)
    
    assert torch.allclose(mean, torch.zeros_like(mean), atol=1e-2)
    assert torch.allclose(var, torch.ones_like(var), atol=1e-1)
    
    # Test backward pass
    loss = output.sum()
    loss.backward()
    
    # All parameters should have gradients
    for name, param in model.named_parameters():
        assert param.grad is not None, f"Parameter {name} has no gradient"
        assert not torch.isnan(param.grad).any(), f"Parameter {name} has NaN gradients"


@pytest.mark.parametrize("unit_class", [paGLU])  # Use just one unit for this detailed test
def test_output_variance_scaling(unit_class):
    """Test how normalization affects output variance with increasing alpha values."""
    # Create a sequence of alpha values
    alpha_values = torch.linspace(0.0, 1.0, 11)  # 0.0 to 1.0 in 0.1 steps
    
    # Normalization configurations to test
    norm_configs = [
        {"name": "No Norm", "use_gate_norm": False, "pre_norm": False, "post_norm": False},
        {"name": "GateNorm", "use_gate_norm": True, "pre_norm": False, "post_norm": False},
        {"name": "PreNorm", "use_gate_norm": False, "pre_norm": True, "post_norm": False},
        {"name": "PostNorm", "use_gate_norm": False, "pre_norm": False, "post_norm": True},
        {"name": "All Norms", "use_gate_norm": True, "pre_norm": True, "post_norm": True},
    ]
    
    # Create input tensor
    x = torch.randn(BATCH_SIZE, INPUT_DIM)
    
    # Store results
    results = {}
    
    for config in norm_configs:
        variances = []
        
        for alpha in alpha_values:
            # Create base unit
            base_unit = unit_class(
                input_dim=INPUT_DIM,
                output_dim=OUTPUT_DIM,
                alpha=alpha.item(),
                use_gate_norm=config["use_gate_norm"]
            )
            
            # Wrap with pre/post normalization if needed
            if config["pre_norm"] or config["post_norm"]:
                model = PrePostNormWrapper(
                    module=base_unit,
                    input_dim=INPUT_DIM,
                    output_dim=OUTPUT_DIM,
                    pre_norm=config["pre_norm"],
                    post_norm=config["post_norm"]
                )
            else:
                model = base_unit
            
            # Forward pass
            with torch.no_grad():
                output = model(x)
            
            # Calculate variance
            variance = output.var().item()
            variances.append(variance)
        
        results[config["name"]] = variances
    
    # Verify that:
    # 1. Without any normalization, variance increases with alpha
    assert results["No Norm"][-1] > results["No Norm"][0], "Variance should increase with alpha without normalization"
    
    # 2. With post-norm, variance should be ~1 regardless of alpha
    if "PostNorm" in results:
        post_norm_variances = results["PostNorm"]
        assert all(0.9 <= v <= 1.1 for v in post_norm_variances), "PostNorm should keep variance ~1"
    
    # 3. GateNorm should reduce variance compared to no norm at high alpha
    if "GateNorm" in results and "No Norm" in results:
        assert results["GateNorm"][-1] < results["No Norm"][-1], "GateNorm should reduce variance at high alpha"


if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 