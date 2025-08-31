import torch
import unittest
from paGating.base import paGatingBase

class TestPaGatingBase(unittest.TestCase):
    """Test cases for the paGatingBase class."""
    
    def test_fixed_alpha(self):
        """Test paGatingBase with fixed alpha value."""
        batch_size, in_dim, out_dim = 2, 4, 6
        x = torch.randn(batch_size, in_dim)
        
        # Create with fixed alpha = 0.7
        model = paGatingBase(
            input_dim=in_dim,
            output_dim=out_dim,
            activation_fn=torch.sigmoid,
            alpha=0.7
        )
        
        # Test forward pass
        output = model(x)
        
        # Check output shape
        self.assertEqual(output.shape, (batch_size, out_dim))
        
        # Check alpha value
        alpha = model.get_alpha()
        self.assertAlmostEqual(alpha.item(), 0.7, places=5)
        
    def test_learnable_alpha(self):
        """Test paGatingBase with learnable alpha."""
        batch_size, in_dim, out_dim = 2, 4, 6
        x = torch.randn(batch_size, in_dim)
        
        # Create with learnable alpha
        model = paGatingBase(
            input_dim=in_dim,
            output_dim=out_dim,
            activation_fn=torch.sigmoid,
            alpha="learnable"
        )
        
        # Test forward pass
        output = model(x)
        
        # Check output shape
        self.assertEqual(output.shape, (batch_size, out_dim))
        
        # Learnable alpha should be a parameter
        self.assertIsNotNone(model.alpha_param)
        
    def test_callable_alpha(self):
        """Test paGatingBase with callable alpha."""
        batch_size, in_dim, out_dim = 2, 4, 6
        x = torch.randn(batch_size, in_dim)
        
        # Simple callable that returns a constant for testing
        def alpha_fn(x):
            return torch.tensor(0.3)
            
        # Create with callable alpha
        model = paGatingBase(
            input_dim=in_dim,
            output_dim=out_dim,
            activation_fn=torch.sigmoid,
            alpha=alpha_fn
        )
        
        # Test forward pass
        output = model(x)
        
        # Check output shape
        self.assertEqual(output.shape, (batch_size, out_dim))
        
        # Check alpha value
        alpha = model.get_alpha(x)
        self.assertAlmostEqual(alpha.item(), 0.3, places=5)

if __name__ == "__main__":
    unittest.main()