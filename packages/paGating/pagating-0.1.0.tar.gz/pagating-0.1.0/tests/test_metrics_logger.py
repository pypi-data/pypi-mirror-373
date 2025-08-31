import os
import sys
import unittest
import tempfile
import csv
import shutil
from unittest.mock import MagicMock, patch

import torch
import numpy as np
import pytorch_lightning as pl

# Add parent directory to path to import paGating
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lightning_modules.metrics_logger import MetricsCsvLogger


class TestMetricsCsvLogger(unittest.TestCase):
    """Tests for the MetricsCsvLogger class."""
    
    def setUp(self):
        """Set up testing environment before each test."""
        # Create a temporary directory for test outputs
        self.test_dir = tempfile.mkdtemp()
        
        # Create mock trainer and module
        self.trainer = MagicMock()
        self.pl_module = MagicMock()
        
        # Set up sample metrics
        self.trainer.current_epoch = 0
        self.sample_metrics = {
            'train_loss': torch.tensor(0.5),
            'train_acc': torch.tensor(0.8),
            'val_loss': torch.tensor(0.4), 
            'val_acc': torch.tensor(0.85)
        }
        self.trainer.callback_metrics = self.sample_metrics
        
    def tearDown(self):
        """Clean up after each test."""
        # Remove the temporary directory and its contents
        shutil.rmtree(self.test_dir)
    
    def test_init(self):
        """Test initialization of the logger."""
        logger = MetricsCsvLogger(
            output_dir=self.test_dir,
            unit_name="paGLU",
            alpha_value=0.5
        )
        
        self.assertEqual(logger.output_dir, self.test_dir)
        self.assertEqual(logger.unit_name, "paGLU")
        self.assertEqual(logger.alpha_value, 0.5)
        self.assertEqual(logger.metrics, [])
        self.assertTrue(logger.has_alpha)
        
        # Check that the output directory was created
        unit_dir = os.path.join(self.test_dir, "paGLU")
        self.assertTrue(os.path.exists(unit_dir))
    
    def test_static_alpha_logging(self):
        """Test that static alpha values are logged for all epochs."""
        # Create logger with static alpha
        logger = MetricsCsvLogger(
            output_dir=self.test_dir,
            unit_name="paGLU",
            alpha_value=0.5
        )
        
        # Simulate multiple epochs
        for epoch in range(3):
            self.trainer.current_epoch = epoch
            
            # Call the callbacks for each epoch
            logger.on_train_epoch_end(self.trainer, self.pl_module)
            logger.on_validation_epoch_end(self.trainer, self.pl_module)
        
        # Check that alpha was logged for all epochs
        for metrics_dict in logger.metrics:
            self.assertIn("alpha", metrics_dict)
            self.assertEqual(metrics_dict["alpha"], 0.5)
        
        # Check the saved CSV file
        csv_path = os.path.join(self.test_dir, "paGLU", "metrics.csv")
        self.assertTrue(os.path.exists(csv_path))
        
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            # Check we have the expected number of rows
            self.assertEqual(len(rows), 3)
            
            # Check all rows have the alpha value
            for row in rows:
                self.assertIn("alpha", row)
                self.assertEqual(row["alpha"], "0.5")
    
    def test_learnable_alpha_logging(self):
        """Test that learnable alpha values are correctly logged."""
        # Create logger without static alpha
        logger = MetricsCsvLogger(
            output_dir=self.test_dir,
            unit_name="paGLU",
            alpha_value=None
        )
        
        # Create a mock parameter with a learnable alpha
        mock_alpha = torch.tensor(0.7, requires_grad=True)
        
        # Add the alpha parameter to the pl_module
        self.pl_module.named_parameters = MagicMock(
            return_value=[("alpha", mock_alpha)]
        )
        
        # Simulate a single epoch
        logger.on_train_epoch_end(self.trainer, self.pl_module)
        logger.on_validation_epoch_end(self.trainer, self.pl_module)
        
        # Check that alpha was logged
        metrics_dict = logger.metrics[0]
        self.assertIn("alpha", metrics_dict)
        # Use assertAlmostEqual to handle floating point precision issues
        self.assertAlmostEqual(metrics_dict["alpha"], 0.7, places=6)
    
    def test_metric_logging(self):
        """Test that metrics are correctly logged and saved."""
        # Create logger
        logger = MetricsCsvLogger(
            output_dir=self.test_dir,
            unit_name="paGLU",
            alpha_value=0.5
        )
        
        # Simulate a single epoch
        logger.on_train_epoch_end(self.trainer, self.pl_module)
        logger.on_validation_epoch_end(self.trainer, self.pl_module)
        
        # Check the metrics dict
        metrics_dict = logger.metrics[0]
        self.assertEqual(metrics_dict["epoch"], 1)  # 1-indexed
        self.assertEqual(metrics_dict["alpha"], 0.5)
        
        # Check that training and validation metrics were correctly extracted
        for key in ['train_loss', 'train_acc', 'val_loss', 'val_acc']:
            self.assertIn(key, metrics_dict)
            self.assertAlmostEqual(metrics_dict[key], self.sample_metrics[key].item(), places=6)
    
    def test_test_metrics_logging(self):
        """Test that test metrics are correctly logged."""
        # Create logger
        logger = MetricsCsvLogger(
            output_dir=self.test_dir,
            unit_name="paGLU",
            alpha_value=0.5
        )
        
        # Simulate a training and validation epoch
        logger.on_train_epoch_end(self.trainer, self.pl_module)
        logger.on_validation_epoch_end(self.trainer, self.pl_module)
        
        # Add test metrics
        test_metrics = {
            'test_loss': torch.tensor(0.3),
            'test_acc': torch.tensor(0.9)
        }
        self.trainer.callback_metrics = test_metrics
        
        # Call test end callback
        logger.on_test_end(self.trainer, self.pl_module)
        
        # Check the metrics dict
        metrics_dict = logger.metrics[0]
        self.assertAlmostEqual(metrics_dict["test_loss"], 0.3, places=6)
        self.assertAlmostEqual(metrics_dict["test_acc"], 0.9, places=6)
        
        # Check the CSV was saved with test metrics
        csv_path = os.path.join(self.test_dir, "paGLU", "metrics.csv")
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            row = next(reader)
            self.assertAlmostEqual(float(row["test_loss"]), 0.3, places=6)
            self.assertAlmostEqual(float(row["test_acc"]), 0.9, places=6)
    
    def test_get_metrics_as_dict(self):
        """Test the get_metrics_as_dict method."""
        # Create logger with static alpha
        logger = MetricsCsvLogger(
            output_dir=self.test_dir,
            unit_name="paGLU",
            alpha_value=0.5
        )
        
        # Simulate a single epoch
        logger.on_train_epoch_end(self.trainer, self.pl_module)
        logger.on_validation_epoch_end(self.trainer, self.pl_module)
        
        # Get metrics dictionary
        metrics_dict = logger.get_metrics_as_dict()
        
        # Check the dictionary contents
        self.assertEqual(metrics_dict["unit_name"], "paGLU")
        self.assertEqual(metrics_dict["alpha_type"], "static")
        self.assertEqual(metrics_dict["alpha_value"], 0.5)
        self.assertEqual(len(metrics_dict["metrics"]), 1)


if __name__ == '__main__':
    unittest.main() 