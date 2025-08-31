import pytest
import torch
import numpy as np

from paGating.alpha_schedulers import (
    ConstantAlpha,
    LearnableAlpha,
    CosineAlphaScheduler,
    EntropyBasedAlpha,
    ConfidenceBasedAlpha,
    LinearRampScheduler,
    get_scheduler
)


# Set reproducible seed
torch.manual_seed(42)
np.random.seed(42)

# Set default dtype to float32
torch.set_default_dtype(torch.float32)

# Test parameters
BATCH_SIZE = 16
INPUT_DIM = 32


@pytest.fixture
def input_tensor():
    """Create a reproducible input tensor for testing."""
    return torch.randn(BATCH_SIZE, INPUT_DIM)


def test_constant_alpha():
    """Test that ConstantAlpha returns the correct fixed value."""
    alpha_values = [0.0, 0.3, 0.5, 0.7, 1.0]
    
    for alpha in alpha_values:
        scheduler = ConstantAlpha(alpha=alpha)
        result = scheduler()
        
        # Check that result is a tensor with the right value
        assert isinstance(result, torch.Tensor), "Result should be a torch.Tensor"
        # Using isclose instead of direct equality to handle floating point precision
        assert torch.isclose(result, torch.tensor(alpha, dtype=torch.float32)), \
            f"Expected alpha close to {alpha}, got {result.item()}"
        
        # Check that alpha is in valid range [0,1]
        assert 0.0 <= result.item() <= 1.0, f"Alpha value {result.item()} not in range [0,1]"


def test_constant_alpha_invalid():
    """Test that ConstantAlpha raises an error for invalid values."""
    invalid_values = [-0.1, 1.1]
    
    for alpha in invalid_values:
        with pytest.raises(ValueError):
            ConstantAlpha(alpha=alpha)


def test_learnable_alpha(input_tensor):
    """Test LearnableAlpha functionality."""
    scheduler = LearnableAlpha(initial_value=0.0)
    
    # Check that alpha_param exists and is learnable
    assert scheduler.alpha_param is not None, "Parameter should exist"
    assert isinstance(scheduler.alpha_param, torch.nn.Parameter), "Should be a torch Parameter"
    assert scheduler.alpha_param.requires_grad, "Parameter should have requires_grad=True"
    
    # Check initial value
    initial_alpha = scheduler()
    assert isinstance(initial_alpha, torch.Tensor), "Result should be a torch.Tensor"
    assert 0.0 <= initial_alpha.item() <= 1.0, f"Alpha value {initial_alpha.item()} not in range [0,1]"
    
    # Check that we can retrieve parameters for optimizer
    params = scheduler.parameters()
    assert len(list(params)) == 1, "Should have exactly one parameter"


@pytest.mark.parametrize("min_alpha,max_alpha,reverse", [
    (0.0, 1.0, False),
    (0.2, 0.8, False),
    (0.0, 1.0, True),
])
def test_cosine_alpha_scheduler(min_alpha, max_alpha, reverse):
    """Test CosineAlphaScheduler behavior over steps."""
    max_steps = 100
    scheduler = CosineAlphaScheduler(
        max_steps=max_steps, 
        min_alpha=min_alpha, 
        max_alpha=max_alpha, 
        reverse=reverse
    )
    
    # Fix: The initial state in CosineAlphaScheduler should be at current_step=0
    # When current_step=0, cosine value is 1.0, so alpha = max_alpha if not reversed
    expected_initial = min_alpha if reverse else max_alpha
    initial_alpha = scheduler()
    assert torch.isclose(initial_alpha, torch.tensor(expected_initial, dtype=torch.float32)), \
        f"Initial alpha should be {expected_initial}, got {initial_alpha.item()}"
    
    # Check middle state (at step 50)
    scheduler.set_step(max_steps // 2)
    mid_alpha = scheduler()
    expected_mid = (min_alpha + max_alpha) / 2
    assert torch.isclose(mid_alpha, torch.tensor(expected_mid, dtype=torch.float32), atol=1e-1), \
        f"Middle alpha should be around {expected_mid}, got {mid_alpha.item()}"
    
    # Check final state
    scheduler.set_step(max_steps)
    final_alpha = scheduler()
    expected_final = max_alpha if reverse else min_alpha
    assert torch.isclose(final_alpha, torch.tensor(expected_final, dtype=torch.float32)), \
        f"Final alpha should be {expected_final}, got {final_alpha.item()}"
    
    # Check that all values are in range [0, 1]
    for step in range(0, max_steps + 1, 10):
        scheduler.set_step(step)
        alpha = scheduler()
        assert 0.0 <= alpha.item() <= 1.0, f"Alpha value {alpha.item()} not in range [0,1]"


def test_entropy_based_alpha(input_tensor):
    """Test EntropyBasedAlpha behavior with different inputs."""
    scheduler = EntropyBasedAlpha(scale=1.0)
    
    # Create different entropy distributions
    # Uniform distribution (high entropy)
    uniform_logits = torch.ones(BATCH_SIZE, INPUT_DIM)
    # Peaked distribution (low entropy)
    peaked_logits = torch.zeros(BATCH_SIZE, INPUT_DIM)
    peaked_logits[:, 0] = 10.0  # One class has much higher probability
    
    # Get alpha values
    uniform_alpha = scheduler(uniform_logits)
    peaked_alpha = scheduler(peaked_logits)
    
    # Verify higher entropy gives higher alpha
    assert uniform_alpha.mean().item() > peaked_alpha.mean().item(), \
        "Uniform distribution (high entropy) should have higher alpha than peaked distribution"
    
    # Check that alpha is in valid range [0,1]
    assert 0.0 <= uniform_alpha.mean().item() <= 1.0, f"Alpha value not in range [0,1]"
    assert 0.0 <= peaked_alpha.mean().item() <= 1.0, f"Alpha value not in range [0,1]"
    
    # Check shape
    assert uniform_alpha.shape == (BATCH_SIZE,), f"Expected shape ({BATCH_SIZE},), got {uniform_alpha.shape}"


def test_confidence_based_alpha(input_tensor):
    """Test ConfidenceBasedAlpha behavior with different inputs."""
    scheduler = ConfidenceBasedAlpha(scale=1.0)
    
    # Create different confidence distributions
    # Uniform distribution (low confidence)
    uniform_logits = torch.ones(BATCH_SIZE, INPUT_DIM)
    # Peaked distribution (high confidence)
    peaked_logits = torch.zeros(BATCH_SIZE, INPUT_DIM)
    peaked_logits[:, 0] = 10.0  # One class has much higher probability
    
    # Get alpha values
    uniform_alpha = scheduler(uniform_logits)
    peaked_alpha = scheduler(peaked_logits)
    
    # Verify lower confidence gives higher alpha
    assert uniform_alpha.mean().item() > peaked_alpha.mean().item(), \
        "Uniform distribution (low confidence) should have higher alpha than peaked distribution"
    
    # Check that alpha is in valid range [0,1]
    assert 0.0 <= uniform_alpha.mean().item() <= 1.0, f"Alpha value not in range [0,1]"
    assert 0.0 <= peaked_alpha.mean().item() <= 1.0, f"Alpha value not in range [0,1]"
    
    # Check shape
    assert uniform_alpha.shape == (BATCH_SIZE,), f"Expected shape ({BATCH_SIZE},), got {uniform_alpha.shape}"


@pytest.mark.parametrize("min_alpha,max_alpha,reverse", [
    (0.0, 1.0, False),
    (0.2, 0.8, False),
    (0.0, 1.0, True),
])
def test_linear_ramp_scheduler(min_alpha, max_alpha, reverse):
    """Test LinearRampScheduler behavior over steps."""
    warmup_steps = 100
    scheduler = LinearRampScheduler(
        warmup_steps=warmup_steps, 
        min_alpha=min_alpha, 
        max_alpha=max_alpha, 
        reverse=reverse
    )
    
    # Check initial state
    initial_alpha = scheduler()
    expected_initial = max_alpha if reverse else min_alpha
    assert torch.isclose(initial_alpha, torch.tensor(expected_initial)), \
        f"Initial alpha should be {expected_initial}, got {initial_alpha.item()}"
    
    # Check that step() increments counter correctly
    scheduler.step()
    assert scheduler.current_step == 1, "current_step should be 1 after calling step()"
    
    # Check middle state - linear interpolation
    scheduler.set_step(warmup_steps // 2)
    mid_alpha = scheduler()
    expected_mid = (min_alpha + max_alpha) / 2
    assert torch.isclose(mid_alpha, torch.tensor(expected_mid)), \
        f"Middle alpha should be {expected_mid}, got {mid_alpha.item()}"
    
    # Check final state
    scheduler.set_step(warmup_steps)
    final_alpha = scheduler()
    expected_final = min_alpha if reverse else max_alpha
    assert torch.isclose(final_alpha, torch.tensor(expected_final)), \
        f"Final alpha should be {expected_final}, got {final_alpha.item()}"
    
    # Check beyond warmup
    scheduler.set_step(warmup_steps * 2)
    beyond_alpha = scheduler()
    assert torch.isclose(beyond_alpha, torch.tensor(expected_final)), \
        f"Alpha beyond warmup should still be {expected_final}, got {beyond_alpha.item()}"


@pytest.mark.parametrize("scheduler_name", [
    "constant", "learnable", "cosine", "entropy", "confidence", "linear"
])
def test_get_scheduler_factory(scheduler_name):
    """Test that the factory method correctly creates all schedulers."""
    # Default params for each scheduler type
    params = {
        "constant": {"alpha": 0.5},
        "learnable": {"initial_value": 0.0},
        "cosine": {"max_steps": 100},
        "entropy": {"scale": 1.0},
        "confidence": {"scale": 1.0},
        "linear": {"warmup_steps": 100}
    }
    
    # Create scheduler using factory
    scheduler = get_scheduler(scheduler_name, **params[scheduler_name])
    
    # Check that created object is of the correct type
    expected_types = {
        "constant": ConstantAlpha,
        "learnable": LearnableAlpha,
        "cosine": CosineAlphaScheduler,
        "entropy": EntropyBasedAlpha,
        "confidence": ConfidenceBasedAlpha,
        "linear": LinearRampScheduler
    }
    
    assert isinstance(scheduler, expected_types[scheduler_name]), \
        f"Expected type {expected_types[scheduler_name]}, got {type(scheduler)}"


def test_get_scheduler_invalid():
    """Test that the factory method raises an error for invalid scheduler names."""
    with pytest.raises(ValueError):
        get_scheduler("nonexistent_scheduler")


def test_scheduler_output_tensor_type():
    """Test that all schedulers return torch.Tensor with appropriate shape."""
    batch_size = 8
    input_dim = 10
    x = torch.randn(batch_size, input_dim)
    
    # Test each scheduler type
    schedulers = [
        ConstantAlpha(alpha=0.5),
        LearnableAlpha(),
        CosineAlphaScheduler(max_steps=100),
        EntropyBasedAlpha(),
        ConfidenceBasedAlpha(),
        LinearRampScheduler(warmup_steps=100)
    ]
    
    for scheduler in schedulers:
        # For schedulers that need input
        if isinstance(scheduler, (EntropyBasedAlpha, ConfidenceBasedAlpha)):
            result = scheduler(x)
            # Check batch dimension
            assert result.shape[0] == batch_size, f"Output shape should have batch dimension {batch_size}"
        else:
            result = scheduler()
        
        # Check result is a tensor
        assert isinstance(result, torch.Tensor), f"{type(scheduler).__name__} should return a torch.Tensor"
        
        # Check that alpha is in valid range [0,1]
        if result.dim() == 0:
            assert 0.0 <= result.item() <= 1.0, f"Alpha value {result.item()} not in range [0,1]"
        else:
            assert torch.all((0.0 <= result) & (result <= 1.0)), "All alpha values should be in range [0,1]"


if __name__ == "__main__":
    pytest.main(["-v"])