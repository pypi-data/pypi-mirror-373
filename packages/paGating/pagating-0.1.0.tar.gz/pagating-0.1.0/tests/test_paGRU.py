import torch
import pytest
from paGating.paGRU import PaGRUCell

# Test parameters
INPUT_SIZE = 10
HIDDEN_SIZE = 20
BATCH_SIZE = 5

@pytest.fixture
def pagru_cell():
    """Fixture to create a PaGRUCell instance."""
    return PaGRUCell(INPUT_SIZE, HIDDEN_SIZE)

@pytest.fixture
def sample_input():
    """Fixture to create sample input tensor."""
    return torch.randn(BATCH_SIZE, INPUT_SIZE)

@pytest.fixture
def sample_hidden():
    """Fixture to create sample hidden state tensor."""
    return torch.randn(BATCH_SIZE, HIDDEN_SIZE)

def test_forward_shape_no_hx(pagru_cell, sample_input):
    """Test forward pass shape when hx is None."""
    output = pagru_cell(sample_input)
    assert output.shape == (BATCH_SIZE, HIDDEN_SIZE), \
        f"Expected output shape {(BATCH_SIZE, HIDDEN_SIZE)}, but got {output.shape}"

def test_forward_shape_with_hx(pagru_cell, sample_input, sample_hidden):
    """Test forward pass shape when hx is provided."""
    output = pagru_cell(sample_input, sample_hidden)
    assert output.shape == (BATCH_SIZE, HIDDEN_SIZE), \
        f"Expected output shape {(BATCH_SIZE, HIDDEN_SIZE)}, but got {output.shape}"

def test_gradients(pagru_cell, sample_input, sample_hidden):
    """Test if gradients flow back to weights and alpha parameters."""
    # Ensure parameters require gradients
    for param in pagru_cell.parameters():
        param.requires_grad_(True)

    # Perform forward and backward pass
    output = pagru_cell(sample_input, sample_hidden)
    dummy_loss = output.sum()
    dummy_loss.backward()

    # Check gradients for weights
    assert pagru_cell.weight_ih.grad is not None, "Gradient missing for weight_ih"
    assert pagru_cell.weight_hh.grad is not None, "Gradient missing for weight_hh"
    if pagru_cell.bias:
        assert pagru_cell.bias_ih.grad is not None, "Gradient missing for bias_ih"
        assert pagru_cell.bias_hh.grad is not None, "Gradient missing for bias_hh"

    # Check gradients for alpha parameters
    assert pagru_cell.alpha_r.grad is not None, "Gradient missing for alpha_r"
    assert pagru_cell.alpha_z.grad is not None, "Gradient missing for alpha_z"
    assert pagru_cell.alpha_h.grad is not None, "Gradient missing for alpha_h"

def test_no_bias(sample_input, sample_hidden):
    """Test PaGRUCell without bias."""
    cell_no_bias = PaGRUCell(INPUT_SIZE, HIDDEN_SIZE, bias=False)
    output = cell_no_bias(sample_input, sample_hidden)
    assert output.shape == (BATCH_SIZE, HIDDEN_SIZE)
    assert cell_no_bias.bias_ih is None
    assert cell_no_bias.bias_hh is None

    # Test gradient flow without bias
    output.sum().backward()
    assert cell_no_bias.weight_ih.grad is not None
    assert cell_no_bias.weight_hh.grad is not None
    assert cell_no_bias.alpha_r.grad is not None
    assert cell_no_bias.alpha_z.grad is not None
    assert cell_no_bias.alpha_h.grad is not None 