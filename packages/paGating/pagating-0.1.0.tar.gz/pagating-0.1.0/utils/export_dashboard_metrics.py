#!/usr/bin/env python
"""
Utility script to export metrics from training runs to CSV files for the Streamlit dashboard.

This script processes metrics from Lightning checkpoints, logs, or raw CSV files and exports them
in a standardized format for use in the Streamlit dashboard.

Usage:
    python export_dashboard_metrics.py --input-dir <input_directory> --output-dir <output_directory> [--unit <unit_name>] [--alpha <alpha_value>]
"""

import os
import sys
import glob
import json
import argparse
import csv
import re
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

import torch
import pandas as pd
import numpy as np


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Export metrics for the Streamlit dashboard")
    parser.add_argument("--input-dir", type=str, required=True,
                        help="Directory containing training logs/checkpoints")
    parser.add_argument("--output-dir", type=str, default="logs/cifar10",
                        help="Directory to save formatted metrics for dashboard")
    parser.add_argument("--unit", type=str, default=None,
                        help="Override unit name if not automatically detectable")
    parser.add_argument("--alpha", type=float, default=None,
                        help="Override alpha value if not automatically detectable")
    parser.add_argument("--alpha-type", type=str, choices=["static", "learnable"], default=None,
                        help="Override alpha type if not automatically detectable")
    parser.add_argument("--overwrite", action="store_true", 
                        help="Overwrite existing metrics files")
    parser.add_argument("--recursive", action="store_true",
                        help="Recursively search input directory")
    return parser.parse_args()


def find_metric_files(input_dir: str, recursive: bool = False) -> List[str]:
    """
    Find all potential metric files in the input directory.
    
    Args:
        input_dir: Directory to search for metric files
        recursive: Whether to search recursively
        
    Returns:
        List of paths to potential metric files
    """
    search_pattern = os.path.join(input_dir, "**" if recursive else "", "*")
    all_files = glob.glob(search_pattern, recursive=recursive)
    
    metric_files = []
    
    # Check each file to see if it contains metrics
    for file_path in all_files:
        # Skip directories
        if os.path.isdir(file_path):
            continue
            
        # Process CSV files
        if file_path.endswith(".csv"):
            # Check if file contains expected headers
            with open(file_path, "r") as f:
                try:
                    first_line = f.readline().strip()
                    if "epoch" in first_line.lower() and any(m in first_line.lower() for m in ["loss", "acc"]):
                        metric_files.append(file_path)
                except:
                    pass
                    
        # Process JSON files
        elif file_path.endswith(".json"):
            # Check if file contains metrics data
            with open(file_path, "r") as f:
                try:
                    data = json.load(f)
                    if isinstance(data, dict) and any(k in data for k in ["metrics", "epochs", "train_loss", "val_loss"]):
                        metric_files.append(file_path)
                except:
                    pass
                    
        # Process PyTorch checkpoint files
        elif file_path.endswith(".pt") or file_path.endswith(".ckpt"):
            try:
                # Try to load just the metadata without loading the full model
                metadata = torch.load(file_path, map_location="cpu")
                if "hyper_parameters" in metadata or "logger_metrics" in metadata:
                    metric_files.append(file_path)
            except:
                pass
    
    return metric_files


def extract_unit_info(file_path: str) -> Dict[str, Any]:
    """
    Extract unit name and alpha information from a file path or content.
    
    Args:
        file_path: Path to the metrics file
        
    Returns:
        Dictionary containing unit_name, alpha_value, and alpha_type if found
    """
    info = {
        "unit_name": None,
        "alpha_value": None,
        "alpha_type": None
    }
    
    # Try to extract unit name and alpha from the file path
    file_name = os.path.basename(file_path)
    dir_name = os.path.basename(os.path.dirname(file_path))
    
    # Check for unit name in format: unitName_alpha0.5
    unit_alpha_match = re.search(r"(pa[A-Za-z]+)_alpha(\d+\.\d+)(?:_learnable)?", file_name)
    if unit_alpha_match:
        info["unit_name"] = unit_alpha_match.group(1)
        info["alpha_value"] = float(unit_alpha_match.group(2))
        info["alpha_type"] = "learnable" if "learnable" in file_name else "static"
    else:
        # Check for unit name in directory
        unit_match = re.search(r"(pa[A-Za-z]+)", dir_name)
        if unit_match:
            info["unit_name"] = unit_match.group(1)
    
    # If CSV file, try to extract alpha from content
    if file_path.endswith(".csv"):
        try:
            df = pd.read_csv(file_path)
            if "alpha" in df.columns:
                # Extract alpha value (use the most common value)
                alpha_values = df["alpha"].dropna().values
                if len(alpha_values) > 0:
                    # If alpha values change over time, it's learnable
                    if np.std(alpha_values) > 0.01:
                        info["alpha_type"] = "learnable"
                        info["alpha_value"] = float(alpha_values[-1])  # Use final value
                    else:
                        info["alpha_type"] = "static"
                        info["alpha_value"] = float(alpha_values[0])
        except:
            pass
    
    # If JSON file, look for alpha in the content
    elif file_path.endswith(".json"):
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                if "alpha" in data:
                    info["alpha_value"] = data["alpha"]
                    info["alpha_type"] = "static"
                elif "alpha_type" in data:
                    info["alpha_type"] = data["alpha_type"]
                if "unit_name" in data:
                    info["unit_name"] = data["unit_name"]
        except:
            pass
    
    # If PyTorch checkpoint file, try to extract from hyperparameters
    elif file_path.endswith(".pt") or file_path.endswith(".ckpt"):
        try:
            checkpoint = torch.load(file_path, map_location="cpu")
            if "hyper_parameters" in checkpoint:
                hparams = checkpoint["hyper_parameters"]
                if "alpha" in hparams:
                    info["alpha_value"] = hparams["alpha"]
                if "unit_name" in hparams:
                    info["unit_name"] = hparams["unit_name"]
                if "use_learnable_alpha" in hparams and hparams["use_learnable_alpha"]:
                    info["alpha_type"] = "learnable"
                else:
                    info["alpha_type"] = "static"
        except:
            pass
    
    return info


def process_csv_metrics(file_path: str, unit_info: Dict[str, Any]) -> pd.DataFrame:
    """
    Process metrics from a CSV file.
    
    Args:
        file_path: Path to the CSV file
        unit_info: Dictionary containing unit name and alpha information
        
    Returns:
        DataFrame with processed metrics
    """
    try:
        df = pd.read_csv(file_path)
        
        # Ensure required columns exist
        required_cols = ["epoch"]
        for col in required_cols:
            if col not in df.columns:
                return None
        
        # Handle metrics column names
        metrics_mapping = {
            "train_loss": ["train_loss", "training_loss", "loss/train", "loss/training"],
            "val_loss": ["val_loss", "validation_loss", "loss/val", "loss/validation"],
            "train_acc": ["train_acc", "training_acc", "acc/train", "accuracy/train"],
            "val_acc": ["val_acc", "validation_acc", "acc/val", "accuracy/validation"],
            "test_loss": ["test_loss", "testing_loss", "loss/test"],
            "test_acc": ["test_acc", "testing_acc", "acc/test", "accuracy/test"]
        }
        
        # Create standardized DataFrame
        standardized_df = pd.DataFrame()
        standardized_df["epoch"] = df["epoch"]
        
        # Map metric columns
        for std_name, possible_names in metrics_mapping.items():
            for col_name in possible_names:
                if col_name in df.columns:
                    standardized_df[std_name] = df[col_name]
                    break
        
        # Handle alpha column
        if "alpha" in df.columns:
            standardized_df["alpha"] = df["alpha"]
        elif unit_info["alpha_value"] is not None:
            standardized_df["alpha"] = unit_info["alpha_value"]
        
        return standardized_df
        
    except Exception as e:
        print(f"Error processing CSV file {file_path}: {e}")
        return None


def process_json_metrics(file_path: str, unit_info: Dict[str, Any]) -> pd.DataFrame:
    """
    Process metrics from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        unit_info: Dictionary containing unit name and alpha information
        
    Returns:
        DataFrame with processed metrics
    """
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        
        # Handle different JSON formats
        
        # Format 1: Metrics are stored directly in the JSON
        if isinstance(data, dict) and all(k in data for k in ["train_loss", "val_loss", "epochs"]):
            standardized_df = pd.DataFrame()
            standardized_df["epoch"] = data.get("epochs", range(1, len(data["train_loss"]) + 1))
            
            metrics_keys = ["train_loss", "val_loss", "train_acc", "val_acc", "test_loss", "test_acc"]
            for key in metrics_keys:
                if key in data and isinstance(data[key], list):
                    standardized_df[key] = data[key]
            
            if "alpha" in data:
                if isinstance(data["alpha"], list):
                    standardized_df["alpha"] = data["alpha"]
                else:
                    standardized_df["alpha"] = data["alpha"]
            elif unit_info["alpha_value"] is not None:
                standardized_df["alpha"] = unit_info["alpha_value"]
            
            return standardized_df
            
        # Format 2: Metrics are stored in a "metrics" list
        elif isinstance(data, dict) and "metrics" in data and isinstance(data["metrics"], list):
            metrics = data["metrics"]
            
            # Convert list of dicts to DataFrame
            standardized_df = pd.DataFrame(metrics)
            
            # Ensure epoch column exists
            if "epoch" not in standardized_df.columns:
                standardized_df["epoch"] = range(1, len(metrics) + 1)
            
            # Handle alpha
            if "alpha" not in standardized_df.columns and unit_info["alpha_value"] is not None:
                standardized_df["alpha"] = unit_info["alpha_value"]
                
            return standardized_df
        
        return None
        
    except Exception as e:
        print(f"Error processing JSON file {file_path}: {e}")
        return None


def process_checkpoint_metrics(file_path: str, unit_info: Dict[str, Any]) -> pd.DataFrame:
    """
    Process metrics from a PyTorch checkpoint file.
    
    Args:
        file_path: Path to the checkpoint file
        unit_info: Dictionary containing unit name and alpha information
        
    Returns:
        DataFrame with processed metrics
    """
    try:
        checkpoint = torch.load(file_path, map_location="cpu")
        
        # Try to extract metrics from the checkpoint
        metrics_data = None
        
        # Check for Lightning logged metrics
        if "logger_metrics" in checkpoint:
            metrics_data = checkpoint["logger_metrics"]
        
        # Check for metrics in hyper_parameters
        elif "hyper_parameters" in checkpoint and "metrics" in checkpoint["hyper_parameters"]:
            metrics_data = checkpoint["hyper_parameters"]["metrics"]
        
        if metrics_data is None:
            return None
        
        # Convert to DataFrame
        metrics_df = pd.DataFrame([metrics_data]) if isinstance(metrics_data, dict) else pd.DataFrame(metrics_data)
        
        # Standardize column names
        standardized_df = pd.DataFrame()
        
        # Ensure epoch column exists
        if "epoch" in metrics_df.columns:
            standardized_df["epoch"] = metrics_df["epoch"]
        else:
            standardized_df["epoch"] = range(1, len(metrics_df) + 1)
        
        # Map metric columns
        metrics_mapping = {
            "train_loss": ["train_loss", "training_loss", "loss/train", "loss/training"],
            "val_loss": ["val_loss", "validation_loss", "loss/val", "loss/validation"],
            "train_acc": ["train_acc", "training_acc", "acc/train", "accuracy/train"],
            "val_acc": ["val_acc", "validation_acc", "acc/val", "accuracy/validation"],
            "test_loss": ["test_loss", "testing_loss", "loss/test"],
            "test_acc": ["test_acc", "testing_acc", "acc/test", "accuracy/test"]
        }
        
        for std_name, possible_names in metrics_mapping.items():
            for col_name in possible_names:
                if col_name in metrics_df.columns:
                    standardized_df[std_name] = metrics_df[col_name]
                    break
        
        # Handle alpha column
        if "alpha" in metrics_df.columns:
            standardized_df["alpha"] = metrics_df["alpha"]
        elif unit_info["alpha_value"] is not None:
            standardized_df["alpha"] = unit_info["alpha_value"]
        
        return standardized_df
        
    except Exception as e:
        print(f"Error processing checkpoint file {file_path}: {e}")
        return None


def export_metrics(metrics_df: pd.DataFrame, unit_info: Dict[str, Any], output_dir: str):
    """
    Export processed metrics to a CSV file for the dashboard.
    
    Args:
        metrics_df: DataFrame containing processed metrics
        unit_info: Dictionary containing unit name and alpha information
        output_dir: Directory to save the metrics
    """
    # Extract unit name
    unit_name = unit_info["unit_name"]
    if unit_name is None:
        print("Error: Could not determine unit name")
        return
    
    # Create output directory
    unit_dir = os.path.join(output_dir, unit_name)
    os.makedirs(unit_dir, exist_ok=True)
    
    # Save metrics to CSV
    output_path = os.path.join(unit_dir, "metrics.csv")
    metrics_df.to_csv(output_path, index=False)
    print(f"Metrics exported to {output_path}")
    
    # Save metadata
    metadata = {
        "unit_name": unit_name,
        "alpha_type": unit_info["alpha_type"] or "unknown",
        "alpha_value": unit_info["alpha_value"],
        "export_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    metadata_path = os.path.join(unit_dir, "metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Metadata saved to {metadata_path}")


def main():
    """Main function."""
    args = parse_args()
    
    input_dir = args.input_dir
    output_dir = args.output_dir
    
    print(f"Searching for metrics in {input_dir}")
    metric_files = find_metric_files(input_dir, args.recursive)
    print(f"Found {len(metric_files)} potential metrics file(s)")
    
    for file_path in metric_files:
        print(f"\nProcessing {file_path}")
        
        # Extract unit info
        unit_info = extract_unit_info(file_path)
        
        # Override with command-line arguments if provided
        if args.unit is not None:
            unit_info["unit_name"] = args.unit
        if args.alpha is not None:
            unit_info["alpha_value"] = args.alpha
        if args.alpha_type is not None:
            unit_info["alpha_type"] = args.alpha_type
        
        # Skip if can't determine unit name
        if unit_info["unit_name"] is None:
            print(f"Skipping {file_path}: Could not determine unit name")
            continue
            
        print(f"Unit info: {unit_info}")
        
        # Process metrics based on file type
        metrics_df = None
        
        if file_path.endswith(".csv"):
            metrics_df = process_csv_metrics(file_path, unit_info)
        elif file_path.endswith(".json"):
            metrics_df = process_json_metrics(file_path, unit_info)
        elif file_path.endswith(".pt") or file_path.endswith(".ckpt"):
            metrics_df = process_checkpoint_metrics(file_path, unit_info)
        
        if metrics_df is None or len(metrics_df) == 0:
            print(f"Skipping {file_path}: No valid metrics found")
            continue
        
        # Check for existing metrics
        unit_dir = os.path.join(output_dir, unit_info["unit_name"])
        if os.path.exists(os.path.join(unit_dir, "metrics.csv")) and not args.overwrite:
            print(f"Skipping {file_path}: Metrics file already exists (use --overwrite to overwrite)")
            continue
        
        # Export metrics
        export_metrics(metrics_df, unit_info, output_dir)
    
    print("\nDone!")


if __name__ == "__main__":
    main() 