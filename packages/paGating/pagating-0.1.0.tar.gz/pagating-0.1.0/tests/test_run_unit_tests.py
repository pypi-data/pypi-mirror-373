#!/usr/bin/env python3
"""
Test suite for the run_unit_tests.py script.
This validates that the unit testing framework works correctly.
"""

import os
import sys
import pytest
import subprocess
import shutil
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import run_unit_tests

TEST_UNIT = "paMishU"
TEST_ALPHA = 0.5
TEST_LOG_DIR = "test_results"
TEST_IMAGE = f"{TEST_UNIT}_gateflow.png"

def setup_module(module):
    """Setup before all tests: backup existing file if it exists"""
    # Create backup of image file if it exists
    if os.path.exists(TEST_IMAGE):
        shutil.copy2(TEST_IMAGE, f"{TEST_IMAGE}.bak")
        os.remove(TEST_IMAGE)
    
    # Create backup of log dir if it exists
    if os.path.exists(TEST_LOG_DIR):
        if os.path.exists(f"{TEST_LOG_DIR}.bak"):
            shutil.rmtree(f"{TEST_LOG_DIR}.bak")
        shutil.copytree(TEST_LOG_DIR, f"{TEST_LOG_DIR}.bak")

def teardown_module(module):
    """Cleanup after all tests: restore original files"""
    # Restore image file from backup if it exists
    if os.path.exists(f"{TEST_IMAGE}.bak"):
        if os.path.exists(TEST_IMAGE):
            os.remove(TEST_IMAGE)
        shutil.copy2(f"{TEST_IMAGE}.bak", TEST_IMAGE)
        os.remove(f"{TEST_IMAGE}.bak")
    
    # Restore log dir from backup if it exists
    if os.path.exists(f"{TEST_LOG_DIR}.bak"):
        if os.path.exists(TEST_LOG_DIR):
            shutil.rmtree(TEST_LOG_DIR)
        shutil.copytree(f"{TEST_LOG_DIR}.bak", TEST_LOG_DIR)
        shutil.rmtree(f"{TEST_LOG_DIR}.bak")

class TestRunUnitTests:
    """Test class for run_unit_tests.py script."""
    
    def test_gateflow_generation(self):
        """Test that gateflow image is generated."""
        # Remove existing image if it exists
        if os.path.exists(TEST_IMAGE):
            os.remove(TEST_IMAGE)
        
        # Call the function directly
        result = run_unit_tests.run_gateflow_test(TEST_UNIT, TEST_ALPHA)
        
        # Check that the function ran successfully
        assert result is True
        
        # Check that the image was created
        assert os.path.exists(TEST_IMAGE)
        
        # Check that the image has content (not empty)
        assert os.path.getsize(TEST_IMAGE) > 0
    
    def test_command_line_interface(self):
        """Test the command line interface."""
        # Remove existing files
        log_file = f"{TEST_LOG_DIR}/{TEST_UNIT}_alpha{TEST_ALPHA:.2f}_tests.log"
        if os.path.exists(log_file):
            os.remove(log_file)
        
        # Call the script as a subprocess
        cmd = [
            sys.executable,
            "run_unit_tests.py",
            "--unit", TEST_UNIT,
            "--alpha", str(TEST_ALPHA),
            "--skip_transformer"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Check that the process ran successfully
        assert result.returncode == 0
        
        # Check that the log file was created
        assert os.path.exists(log_file)
        
        # Check content of log file for expected outputs
        with open(log_file, "r") as f:
            content = f.read()
            assert f"Test Results for {TEST_UNIT}" in content
            assert "Gate Flow Test: SUCCESS" in content

if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 