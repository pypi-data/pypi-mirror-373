#!/usr/bin/env python3.12
"""
Tests for the M4 optimization work, including training, benchmarking, and CoreML export.
"""
import pytest
import os
import subprocess
import pathlib
import torch
import coremltools as ct
import numpy as np

# Define paths
TEST_OUTPUT_DIR = pathlib.Path("test_outputs")
TRAIN_SCRIPT_PATH = "scripts/train_pagating.py"
EXPORT_SCRIPT_PATH = "scripts/export_to_coreml.py"
BENCHMARK_SCRIPT_PATH = "scripts/benchmark_optimizations.py"

@pytest.fixture(scope="module")
def trained_model_path():
    """
    Fixture to run the training script and generate a model for testing.
    This runs once per test module.
    """
    model_dir = TEST_OUTPUT_DIR / "trained_model"
    run_name = "pagating_learnable_lr0-0005"
    final_model_path = model_dir / run_name / "final_model"
    
    if not final_model_path.exists():
        cmd = [
            "python", TRAIN_SCRIPT_PATH,
            "--alpha_mode", "learnable",
            "--max_steps", "2",
            "--batch_size", "2",
            "--output_dir", str(model_dir)
        ]
        print(f"Running training script: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        assert result.returncode == 0, f"Training script failed: {result.stderr}"

    assert final_model_path.exists(), "Trained model not found after running script."
    return str(final_model_path)


def test_coreml_export(trained_model_path):
    """
    Test if the CoreML export script runs successfully.
    """
    output_dir = TEST_OUTPUT_DIR / "coreml_export"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    cmd = [
        "python", EXPORT_SCRIPT_PATH,
        "--model_path", trained_model_path,
        "--alpha_mode", "learnable",
        "--output_dir", str(output_dir)
    ]
    
    print(f"Running CoreML export script: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    assert result.returncode == 0, f"CoreML export failed: {result.stderr}"
    
    exported_model_path = output_dir / "pagating_learnable.mlpackage"
    assert exported_model_path.exists(), "Exported CoreML model not found."


@pytest.mark.depends(on=['test_coreml_export'])
def test_coreml_inference():
    """
    Test loading the exported CoreML model and running inference.
    """
    model_path = TEST_OUTPUT_DIR / "coreml_export" / "pagating_learnable.mlpackage"
    assert model_path.exists()

    print(f"Loading CoreML model from: {model_path}")
    model = ct.models.MLModel(str(model_path))

    # Prepare a dummy input
    dummy_input = np.random.randint(0, 50257, (1, 128)).astype(np.int32)
    
    print("Running inference on CoreML model...")
    prediction = model.predict({'input_ids': dummy_input})

    assert "logits" in prediction
    output = prediction["logits"]
    assert output.shape == (1, 128, 50257)


def test_benchmark_script_runs():
    """
    Test if the benchmark script runs without errors.
    """
    env = os.environ.copy()
    env["KMP_DUPLICATE_LIB_OK"] = "TRUE"
    
    # We add a dummy argument to test the script runs, but we don't need a full benchmark
    cmd = ["python", BENCHMARK_SCRIPT_PATH, "--help"]
    
    print(f"Running benchmark script: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    
    assert result.returncode == 0, f"Benchmark script failed to run: {result.stderr}"
    assert "usage: benchmark_optimizations.py" in result.stdout 