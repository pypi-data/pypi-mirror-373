#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
paGating Consolidated Summary Export

This script generates:
1. summary.json: A machine-readable summary of key metrics
2. results.zip: A zipped archive of CSVs, Markdown reports, and visualizations
"""

import os
import sys
import json
import glob
import argparse
import pandas as pd
import numpy as np
import zipfile
import shutil
from datetime import datetime


def parse_args():
    parser = argparse.ArgumentParser(description="Generate consolidated export of experiment results")
    
    parser.add_argument("--experiment_dir", type=str, required=True,
                       help="Path to the experiment directory")
    parser.add_argument("--output_dir", type=str, default=None,
                       help="Output directory for exported files (default: experiment_dir)")
    
    return parser.parse_args()


def find_units_and_alphas(experiment_dir):
    """Find all units and alpha values from the transformer results."""
    csv_path = os.path.join(experiment_dir, "transformer", "transformer_results.csv")
    if not os.path.exists(csv_path):
        return [], []
    
    df = pd.read_csv(csv_path)
    if df.empty:
        return [], []
    
    units = df['Unit'].unique().tolist()
    alphas = sorted(df['Alpha'].unique().tolist())
    
    return units, alphas


def extract_test_accuracy_stats(experiment_dir):
    """Extract test accuracy statistics from transformer results."""
    csv_path = os.path.join(experiment_dir, "transformer", "transformer_results.csv")
    if not os.path.exists(csv_path):
        return None
    
    df = pd.read_csv(csv_path)
    if df.empty:
        return None
    
    stats = {
        "mean": float(df['Test Accuracy'].mean()),
        "median": float(df['Test Accuracy'].median()),
        "min": float(df['Test Accuracy'].min()),
        "max": float(df['Test Accuracy'].max()),
        "std": float(df['Test Accuracy'].std())
    }
    
    return stats


def find_best_units(experiment_dir):
    """Find the best performing units from transformer results."""
    csv_path = os.path.join(experiment_dir, "transformer", "transformer_results.csv")
    if not os.path.exists(csv_path):
        return None
    
    df = pd.read_csv(csv_path)
    if df.empty:
        return None
    
    # Find overall best
    best_idx = df['Test Accuracy'].idxmax()
    best_row = df.loc[best_idx]
    
    # Find best for each unit
    best_by_unit = {}
    for unit in df['Unit'].unique():
        unit_df = df[df['Unit'] == unit]
        best_idx = unit_df['Test Accuracy'].idxmax()
        best_row_unit = df.loc[best_idx]
        
        best_by_unit[unit] = {
            'alpha': float(best_row_unit['Alpha']),
            'test_accuracy': float(best_row_unit['Test Accuracy']),
            'test_loss': float(best_row_unit['Test Loss']),
            'train_accuracy': float(best_row_unit['Train Accuracy']) if 'Train Accuracy' in best_row_unit else None,
            'train_loss': float(best_row_unit['Train Loss']) if 'Train Loss' in best_row_unit else None
        }
    
    # Find best for each alpha
    best_by_alpha = {}
    for alpha in df['Alpha'].unique():
        alpha_df = df[df['Alpha'] == alpha]
        best_idx = alpha_df['Test Accuracy'].idxmax()
        best_row_alpha = df.loc[best_idx]
        
        best_by_alpha[str(alpha)] = {
            'unit': best_row_alpha['Unit'],
            'test_accuracy': float(best_row_alpha['Test Accuracy']),
            'test_loss': float(best_row_alpha['Test Loss']),
            'train_accuracy': float(best_row_alpha['Train Accuracy']) if 'Train Accuracy' in best_row_alpha else None,
            'train_loss': float(best_row_alpha['Train Loss']) if 'Train Loss' in best_row_alpha else None
        }
    
    best = {
        'overall': {
            'unit': best_row['Unit'],
            'alpha': float(best_row['Alpha']),
            'test_accuracy': float(best_row['Test Accuracy']),
            'test_loss': float(best_row['Test Loss']),
            'train_accuracy': float(best_row['Train Accuracy']) if 'Train Accuracy' in best_row else None,
            'train_loss': float(best_row['Train Loss']) if 'Train Loss' in best_row else None
        },
        'by_unit': best_by_unit,
        'by_alpha': best_by_alpha
    }
    
    return best


def extract_experiment_config(experiment_dir):
    """Extract experiment configuration from the leaderboard markdown."""
    leaderboard_path = os.path.join(experiment_dir, "leaderboard", "transformer_leaderboard.md")
    if not os.path.exists(leaderboard_path):
        return {}
    
    config = {}
    with open(leaderboard_path, 'r') as f:
        content = f.read()
    
    # Look for the configuration section
    if "## Configuration" in content:
        config_section = content.split("## Configuration")[-1].split("##")[0].strip()
        
        for line in config_section.split("\n"):
            line = line.strip()
            if line.startswith("- "):
                parts = line[2:].split(": ", 1)
                if len(parts) == 2:
                    key, value = parts
                    try:
                        # Try to convert to int or float if possible
                        if value.isdigit():
                            config[key] = int(value)
                        else:
                            try:
                                config[key] = float(value)
                            except ValueError:
                                config[key] = value
                    except:
                        config[key] = value
    
    return config


def find_artifact_paths(experiment_dir):
    """Find paths to all result artifacts in the experiment directory."""
    artifacts = {
        "markdown_files": [],
        "csv_files": [],
        "plot_files": [],
        "other_files": []
    }
    
    # Find all files in the experiment directory and its subdirectories
    for root, _, files in os.walk(experiment_dir):
        for file in files:
            file_path = os.path.join(root, file)
            
            # Skip hidden files
            if os.path.basename(file_path).startswith('.'):
                continue
            
            # Categorize by file extension
            if file.endswith('.md'):
                artifacts["markdown_files"].append(file_path)
            elif file.endswith('.csv'):
                artifacts["csv_files"].append(file_path)
            elif file.endswith(('.png', '.jpg', '.jpeg')):
                artifacts["plot_files"].append(file_path)
            elif file.endswith(('.json', '.log', '.txt')):
                artifacts["other_files"].append(file_path)
    
    return artifacts


def create_summary_json(experiment_dir, output_path):
    """Create a machine-readable summary of key metrics."""
    experiment_name = os.path.basename(experiment_dir)
    units, alphas = find_units_and_alphas(experiment_dir)
    test_accuracy_stats = extract_test_accuracy_stats(experiment_dir)
    best_units = find_best_units(experiment_dir)
    experiment_config = extract_experiment_config(experiment_dir)
    
    summary = {
        "experiment_name": experiment_name,
        "generation_date": datetime.now().isoformat(),
        "units": units,
        "alpha_values": alphas,
        "test_accuracy_stats": test_accuracy_stats,
        "best_units": best_units,
        "experiment_config": experiment_config
    }
    
    # Write to JSON file
    with open(output_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"Summary JSON created: {output_path}")
    return summary


def create_results_zip(experiment_dir, artifact_paths, output_path):
    """Create a zipped archive of result artifacts."""
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add files by category
        for category, files in artifact_paths.items():
            for file_path in files:
                # Create relative path within the zip
                rel_path = os.path.relpath(file_path, os.path.dirname(experiment_dir))
                zipf.write(file_path, rel_path)
    
    print(f"Results ZIP created: {output_path}")
    return output_path


def main():
    args = parse_args()
    
    # Process experiment directory
    experiment_dir = args.experiment_dir
    if not os.path.exists(experiment_dir):
        print(f"Error: Experiment directory '{experiment_dir}' does not exist")
        sys.exit(1)
    
    # Set output directory if not provided
    if not args.output_dir:
        args.output_dir = experiment_dir
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Define output paths
    summary_json_path = os.path.join(args.output_dir, "summary.json")
    results_zip_path = os.path.join(args.output_dir, "results.zip")
    
    # Find all artifact paths
    artifact_paths = find_artifact_paths(experiment_dir)
    
    # Create summary.json
    create_summary_json(experiment_dir, summary_json_path)
    
    # Create results.zip
    create_results_zip(experiment_dir, artifact_paths, results_zip_path)
    
    print(f"Consolidated summary export completed successfully!")


if __name__ == "__main__":
    main() 