#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Generate a leaderboard from the results of the hyperparameter sweep.
This script parses the CSV logs and produces a clean markdown table
with performance metrics sorted by test accuracy.
"""

import os
import glob
import pandas as pd
import argparse
from datetime import datetime


def parse_args():
    parser = argparse.ArgumentParser(description="Generate leaderboard from sweep results")
    parser.add_argument("--results_dir", type=str, default="logs", 
                        help="Directory containing the CSV logs from the sweep")
    parser.add_argument("--output_file", type=str, default="leaderboard.md",
                        help="Path to save the leaderboard markdown")
    parser.add_argument("--include_train", action="store_true", 
                        help="Include training metrics in the leaderboard")
    parser.add_argument("--sort_by", type=str, default="test_accuracy",
                        choices=["test_accuracy", "test_loss", "train_accuracy", "train_loss"],
                        help="Metric to sort the leaderboard by")
    parser.add_argument("--top_k", type=int, default=None,
                        help="Show only top K results")
    return parser.parse_args()


def collect_results(results_dir):
    """Collect and process all CSV log files from the sweep."""
    csv_files = glob.glob(os.path.join(results_dir, "*.csv"))
    all_results = []
    
    for file_path in csv_files:
        try:
            # Extract model info from the filename
            filename = os.path.basename(file_path)
            parts = filename.replace(".csv", "").split("_")
            
            if len(parts) < 3:
                print(f"Skipping file with unexpected name format: {filename}")
                continue
                
            unit_name = parts[0]
            
            # Handle different naming formats
            if "learnable" in filename:
                # Format: unit_alpha0.50_learnable.csv
                alpha_str = parts[1].replace("alpha", "")
                alpha = float(alpha_str)
                learnable = True
            else:
                # Format: unit_alpha0.50.csv
                alpha_str = parts[1].replace("alpha", "")
                alpha = float(alpha_str)
                learnable = False
            
            # Read the CSV file
            df = pd.read_csv(file_path)
            
            # Get the last epoch results
            last_epoch = df.iloc[-1]
            
            # Extract metrics
            result = {
                "unit": unit_name,
                "alpha": alpha,
                "learnable_alpha": learnable,
                "train_loss": last_epoch.get("train_loss", float("nan")),
                "train_accuracy": last_epoch.get("train_acc", float("nan")),
                "test_loss": last_epoch.get("val_loss", float("nan")),
                "test_accuracy": last_epoch.get("val_acc", float("nan")),
                "epochs": len(df),
                "log_file": file_path
            }
            
            # Check if alpha ended up at a different value (for learnable alpha)
            if learnable and "alpha" in last_epoch:
                result["final_alpha"] = last_epoch["alpha"]
            
            all_results.append(result)
            
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
    
    # Convert to DataFrame
    results_df = pd.DataFrame(all_results)
    return results_df


def generate_markdown_table(results_df, include_train=False, sort_by="test_accuracy", top_k=None):
    """Generate a markdown table from the results DataFrame."""
    # Sort results by the specified metric
    if sort_by == "test_accuracy":
        ascending = False
    elif sort_by == "test_loss":
        ascending = True
    elif sort_by == "train_accuracy":
        ascending = False
    else:  # train_loss
        ascending = True
    
    results_df = results_df.sort_values(by=sort_by, ascending=ascending)
    
    # Take only top k if specified
    if top_k is not None:
        results_df = results_df.head(top_k)
    
    # Start building markdown
    md = "# paGating Leaderboard\n\n"
    md += f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    # Table header
    header = "| Rank | Unit | Alpha | Learnable | "
    if include_train:
        header += "Train Acc | Train Loss | "
    header += "Test Acc | Test Loss | Epochs |"
    md += header + "\n"
    
    # Table separator
    separator = "|" + "---|" * (6 if include_train else 4) + "---|---|---|\n"
    md += separator
    
    # Table rows
    for i, (_, row) in enumerate(results_df.iterrows()):
        # Format alpha value with final alpha if available
        if row.get("learnable_alpha", False) and "final_alpha" in row:
            alpha_text = f"{row['alpha']:.2f} → {row['final_alpha']:.2f}"
        else:
            alpha_text = f"{row['alpha']:.2f}"
        
        # Construct table row
        table_row = f"| {i+1} | {row['unit']} | {alpha_text} | {row['learnable_alpha']} | "
        
        if include_train:
            table_row += f"{row['train_accuracy']:.4f} | {row['train_loss']:.4f} | "
        
        table_row += f"{row['test_accuracy']:.4f} | {row['test_loss']:.4f} | {row['epochs']} |"
        md += table_row + "\n"
    
    return md


def generate_unit_summaries(results_df):
    """Generate summaries for each unit type."""
    md = "\n## Unit Performance Summaries\n\n"
    
    # Group by unit and calculate mean performance
    unit_summary = results_df.groupby("unit").agg({
        "test_accuracy": ["mean", "max"],
        "test_loss": ["mean", "min"]
    }).reset_index()
    
    # Make the column names more readable
    unit_summary.columns = ["unit", "avg_test_acc", "max_test_acc", "avg_test_loss", "min_test_loss"]
    
    # Sort by average test accuracy
    unit_summary = unit_summary.sort_values(by="avg_test_acc", ascending=False)
    
    # Create a summary table
    md += "| Unit | Avg Test Acc | Max Test Acc | Avg Test Loss | Min Test Loss |\n"
    md += "|------|-------------|-------------|--------------|-------------|\n"
    
    for _, row in unit_summary.iterrows():
        md += (f"| {row['unit']} | {row['avg_test_acc']:.4f} | {row['max_test_acc']:.4f} | "
               f"{row['avg_test_loss']:.4f} | {row['min_test_loss']:.4f} |\n")
    
    return md


def generate_alpha_analysis(results_df):
    """Analyze the effect of alpha values."""
    md = "\n## Alpha Value Analysis\n\n"
    
    # Filter for non-learnable alpha only
    fixed_alpha_df = results_df[~results_df["learnable_alpha"]]
    
    # Group by alpha value
    alpha_summary = fixed_alpha_df.groupby("alpha").agg({
        "test_accuracy": ["mean", "std"],
        "test_loss": ["mean", "std"]
    }).reset_index()
    
    # Make the column names more readable
    alpha_summary.columns = ["alpha", "avg_test_acc", "std_test_acc", "avg_test_loss", "std_test_loss"]
    
    # Sort by alpha value
    alpha_summary = alpha_summary.sort_values(by="alpha")
    
    # Create a summary table
    md += "| Alpha | Avg Test Acc | Std Test Acc | Avg Test Loss | Std Test Loss |\n"
    md += "|-------|-------------|-------------|--------------|-------------|\n"
    
    for _, row in alpha_summary.iterrows():
        md += (f"| {row['alpha']:.2f} | {row['avg_test_acc']:.4f} | {row['std_test_acc']:.4f} | "
               f"{row['avg_test_loss']:.4f} | {row['std_test_loss']:.4f} |\n")
    
    return md


def generate_learnable_analysis(results_df):
    """Compare learnable vs fixed alpha."""
    md = "\n## Learnable vs Fixed Alpha\n\n"
    
    # Group by learnable flag
    learnable_summary = results_df.groupby("learnable_alpha").agg({
        "test_accuracy": ["mean", "max", "std"],
        "test_loss": ["mean", "min", "std"]
    }).reset_index()
    
    # Make the column names more readable
    learnable_summary.columns = ["learnable_alpha", "avg_test_acc", "max_test_acc", "std_test_acc", 
                                "avg_test_loss", "min_test_loss", "std_test_loss"]
    
    # Create a summary table
    md += "| Alpha Type | Avg Test Acc | Max Test Acc | Std Test Acc | Avg Test Loss | Min Test Loss | Std Test Loss |\n"
    md += "|-----------|-------------|-------------|-------------|--------------|--------------|-------------|\n"
    
    for _, row in learnable_summary.iterrows():
        alpha_type = "Learnable" if row["learnable_alpha"] else "Fixed"
        md += (f"| {alpha_type} | {row['avg_test_acc']:.4f} | {row['max_test_acc']:.4f} | "
               f"{row['std_test_acc']:.4f} | {row['avg_test_loss']:.4f} | {row['min_test_loss']:.4f} | "
               f"{row['std_test_loss']:.4f} |\n")
    
    return md


def main():
    args = parse_args()
    
    # Collect results from CSV logs
    print(f"Collecting results from {args.results_dir}...")
    results_df = collect_results(args.results_dir)
    
    if results_df.empty:
        print("No results found. Check the paths to the CSV files.")
        return
    
    print(f"Found {len(results_df)} results.")
    
    # Generate main leaderboard table
    md_content = generate_markdown_table(
        results_df, 
        include_train=args.include_train,
        sort_by=args.sort_by,
        top_k=args.top_k
    )
    
    # Add unit summaries
    md_content += generate_unit_summaries(results_df)
    
    # Add alpha value analysis
    md_content += generate_alpha_analysis(results_df)
    
    # Add learnable vs fixed alpha analysis
    md_content += generate_learnable_analysis(results_df)
    
    # Write to file
    with open(args.output_file, "w") as f:
        f.write(md_content)
    
    print(f"Leaderboard generated and saved to {args.output_file}")


if __name__ == "__main__":
    main() 