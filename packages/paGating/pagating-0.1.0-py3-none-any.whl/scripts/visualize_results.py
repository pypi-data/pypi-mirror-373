#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Visualize results from paGating hyperparameter sweeps.
This script generates plots to analyze the performance of different
paGating units across various configurations and training dynamics.
"""

import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
from matplotlib.gridspec import GridSpec


def parse_args():
    parser = argparse.ArgumentParser(description="Visualize results from paGating hyperparameter sweeps")
    parser.add_argument("--results_dir", type=str, default="logs", 
                        help="Directory containing the CSV logs from the sweep")
    parser.add_argument("--output_dir", type=str, default="plots",
                        help="Directory to save the generated plots")
    parser.add_argument("--units", type=str, nargs="+", 
                        help="Specific units to include in visualization (default: all units)")
    parser.add_argument("--alpha_values", type=float, nargs="+",
                        help="Specific alpha values to include in visualization (default: all values)")
    parser.add_argument("--dpi", type=int, default=300,
                        help="DPI for saved plots")
    parser.add_argument("--style", type=str, default="whitegrid",
                        choices=["darkgrid", "whitegrid", "dark", "white", "ticks"],
                        help="Seaborn plot style")
    return parser.parse_args()


def load_and_process_results(results_dir, units=None, alpha_values=None):
    """Load and process all CSV log files from the sweep."""
    csv_files = glob.glob(os.path.join(results_dir, "*.csv"))
    all_data = []
    
    for file_path in csv_files:
        try:
            # Extract model info from the filename
            filename = os.path.basename(file_path)
            parts = filename.replace(".csv", "").split("_")
            
            if len(parts) < 2:
                print(f"Skipping file with unexpected name format: {filename}")
                continue
                
            unit_name = parts[0]
            
            # Skip if not in the requested units
            if units and unit_name not in units:
                continue
                
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
            
            # Skip if not in the requested alpha values
            if alpha_values and alpha not in alpha_values:
                continue
                
            # Read the CSV file
            df = pd.read_csv(file_path)
            
            # Add metadata columns
            df["unit"] = unit_name
            df["alpha"] = alpha
            df["learnable"] = learnable
            df["config"] = f"{unit_name}_alpha{alpha:.2f}" + ("_learnable" if learnable else "")
            
            all_data.append(df)
            
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
    
    # Combine all dataframes
    if not all_data:
        print("No matching results found.")
        return None
        
    combined_df = pd.concat(all_data, ignore_index=True)
    
    # Standardize column names
    column_mapping = {
        "train_acc": "train_accuracy",
        "val_acc": "test_accuracy",
        "val_loss": "test_loss"
    }
    combined_df.rename(columns=column_mapping, inplace=True)
    
    return combined_df


def plot_training_curves(data, output_dir, dpi=300):
    """Plot training and validation curves for each configuration."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Get unique configurations
    configs = data["config"].unique()
    
    plt.figure(figsize=(18, 10))
    
    for config in configs:
        subset = data[data["config"] == config]
        subset = subset.sort_values(by="epoch")
        
        # Create a figure with 2 subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        fig.suptitle(f"Training Curves for {config}", fontsize=16)
        
        # Loss subplot
        ax1.plot(subset["epoch"], subset["train_loss"], label="Train Loss", color="blue")
        ax1.plot(subset["epoch"], subset["test_loss"], label="Validation Loss", color="red")
        ax1.set_xlabel("Epoch")
        ax1.set_ylabel("Loss")
        ax1.set_title("Loss vs Epoch")
        ax1.legend()
        ax1.grid(True)
        
        # Accuracy subplot
        ax2.plot(subset["epoch"], subset["train_accuracy"], label="Train Accuracy", color="blue")
        ax2.plot(subset["epoch"], subset["test_accuracy"], label="Validation Accuracy", color="red")
        ax2.set_xlabel("Epoch")
        ax2.set_ylabel("Accuracy")
        ax2.set_title("Accuracy vs Epoch")
        ax2.legend()
        ax2.grid(True)
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"{config}_training_curves.png"), dpi=dpi)
        plt.close()
        
    print(f"Generated training curves for {len(configs)} configurations.")
    
    # Plot alpha evolution for learnable alpha configurations
    learnable_configs = data[data["learnable"] == True]["config"].unique()
    
    if learnable_configs.size > 0 and "alpha" in data.columns:
        plt.figure(figsize=(12, 8))
        
        for config in learnable_configs:
            subset = data[(data["config"] == config) & (data["learnable"] == True)]
            subset = subset.sort_values(by="epoch")
            
            if "alpha" in subset.columns:
                plt.plot(subset["epoch"], subset["alpha"], label=config)
        
        plt.xlabel("Epoch")
        plt.ylabel("Alpha Value")
        plt.title("Evolution of Learnable Alpha Parameters")
        plt.legend()
        plt.grid(True)
        plt.savefig(os.path.join(output_dir, "alpha_evolution.png"), dpi=dpi)
        plt.close()
        
        print("Generated alpha evolution plot.")


def plot_unit_comparison(data, output_dir, dpi=300):
    """Plot comparison of different units' performance."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Get final epoch results for each config
    final_results = []
    
    for config in data["config"].unique():
        subset = data[data["config"] == config]
        last_epoch = subset.loc[subset["epoch"].idxmax()]
        final_results.append(last_epoch)
    
    final_df = pd.DataFrame(final_results)
    
    # Plot test accuracy by unit and alpha
    plt.figure(figsize=(14, 8))
    
    # Use different markers for learnable/fixed
    markers = {True: "o", False: "s"}
    
    # Group by unit and alpha
    for unit in final_df["unit"].unique():
        unit_data = final_df[final_df["unit"] == unit]
        
        for learnable in [False, True]:
            subset = unit_data[unit_data["learnable"] == learnable]
            
            if not subset.empty:
                label = f"{unit}" + (" (Learnable)" if learnable else "")
                plt.scatter(subset["alpha"], subset["test_accuracy"], 
                           label=label, marker=markers[learnable], s=100)
    
    plt.xlabel("Alpha Value")
    plt.ylabel("Test Accuracy")
    plt.title("Final Test Accuracy by Unit and Alpha")
    plt.legend(loc="best")
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, "test_accuracy_comparison.png"), dpi=dpi)
    plt.close()
    
    # Plot test loss by unit and alpha
    plt.figure(figsize=(14, 8))
    
    for unit in final_df["unit"].unique():
        unit_data = final_df[final_df["unit"] == unit]
        
        for learnable in [False, True]:
            subset = unit_data[unit_data["learnable"] == learnable]
            
            if not subset.empty:
                label = f"{unit}" + (" (Learnable)" if learnable else "")
                plt.scatter(subset["alpha"], subset["test_loss"], 
                           label=label, marker=markers[learnable], s=100)
    
    plt.xlabel("Alpha Value")
    plt.ylabel("Test Loss")
    plt.title("Final Test Loss by Unit and Alpha")
    plt.legend(loc="best")
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, "test_loss_comparison.png"), dpi=dpi)
    plt.close()
    
    print("Generated unit comparison plots.")


def plot_heatmap(data, output_dir, dpi=300):
    """Create heatmaps showing performance across units and alpha values."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Get final epoch results
    final_results = []
    for config in data["config"].unique():
        subset = data[data["config"] == config]
        last_epoch = subset.loc[subset["epoch"].idxmax()]
        final_results.append(last_epoch)
    
    final_df = pd.DataFrame(final_results)
    
    # Filter for non-learnable alpha to create the heatmap
    fixed_alpha_df = final_df[~final_df["learnable"]]
    
    if fixed_alpha_df.empty:
        print("No data with fixed alpha values for heatmap.")
        return
    
    # Prepare data for heatmaps
    heatmap_data = fixed_alpha_df.pivot_table(
        index="unit", 
        columns="alpha", 
        values="test_accuracy"
    )
    
    # Test accuracy heatmap
    plt.figure(figsize=(12, 8))
    sns.heatmap(heatmap_data, annot=True, cmap="viridis", fmt=".4f", cbar_kws={'label': 'Test Accuracy'})
    plt.title("Test Accuracy Heatmap by Unit and Alpha")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "test_accuracy_heatmap.png"), dpi=dpi)
    plt.close()
    
    # Test loss heatmap
    heatmap_data_loss = fixed_alpha_df.pivot_table(
        index="unit", 
        columns="alpha", 
        values="test_loss"
    )
    
    plt.figure(figsize=(12, 8))
    sns.heatmap(heatmap_data_loss, annot=True, cmap="rocket_r", fmt=".4f", cbar_kws={'label': 'Test Loss'})
    plt.title("Test Loss Heatmap by Unit and Alpha")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "test_loss_heatmap.png"), dpi=dpi)
    plt.close()
    
    print("Generated heatmap plots.")


def plot_unit_rankings(data, output_dir, dpi=300):
    """Create bar plots showing units ranked by performance."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Get final epoch results
    final_results = []
    for config in data["config"].unique():
        subset = data[data["config"] == config]
        last_epoch = subset.loc[subset["epoch"].idxmax()]
        final_results.append(last_epoch)
    
    final_df = pd.DataFrame(final_results)
    
    # Calculate average performance per unit
    unit_summary = final_df.groupby("unit").agg({
        "test_accuracy": ["mean", "max"],
        "test_loss": ["mean", "min"]
    })
    
    # Flatten the column names
    unit_summary.columns = ["avg_test_acc", "max_test_acc", "avg_test_loss", "min_test_loss"]
    unit_summary = unit_summary.reset_index()
    
    # Sort by average test accuracy
    unit_summary_acc = unit_summary.sort_values(by="avg_test_acc", ascending=False)
    
    # Plot average test accuracy
    plt.figure(figsize=(12, 8))
    bars = plt.bar(unit_summary_acc["unit"], unit_summary_acc["avg_test_acc"], alpha=0.7)
    
    # Add error bars showing the max accuracy
    for i, (_, row) in enumerate(unit_summary_acc.iterrows()):
        plt.plot([i, i], [row["avg_test_acc"], row["max_test_acc"]], 'black', linewidth=2)
        plt.plot([i-0.2, i+0.2], [row["max_test_acc"], row["max_test_acc"]], 'black', linewidth=2)
    
    plt.ylabel("Test Accuracy")
    plt.title("Average Test Accuracy by Unit (with Maximum)")
    plt.xticks(rotation=45)
    plt.ylim(bottom=unit_summary_acc["avg_test_acc"].min() * 0.95, 
             top=unit_summary_acc["max_test_acc"].max() * 1.05)
    plt.grid(axis="y")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "unit_accuracy_ranking.png"), dpi=dpi)
    plt.close()
    
    # Sort by average test loss
    unit_summary_loss = unit_summary.sort_values(by="avg_test_loss", ascending=True)
    
    # Plot average test loss
    plt.figure(figsize=(12, 8))
    bars = plt.bar(unit_summary_loss["unit"], unit_summary_loss["avg_test_loss"], alpha=0.7, color="salmon")
    
    # Add error bars showing the min loss
    for i, (_, row) in enumerate(unit_summary_loss.iterrows()):
        plt.plot([i, i], [row["avg_test_loss"], row["min_test_loss"]], 'black', linewidth=2)
        plt.plot([i-0.2, i+0.2], [row["min_test_loss"], row["min_test_loss"]], 'black', linewidth=2)
    
    plt.ylabel("Test Loss")
    plt.title("Average Test Loss by Unit (with Minimum)")
    plt.xticks(rotation=45)
    plt.ylim(bottom=unit_summary_loss["min_test_loss"].min() * 0.95, 
             top=unit_summary_loss["avg_test_loss"].max() * 1.05)
    plt.grid(axis="y")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "unit_loss_ranking.png"), dpi=dpi)
    plt.close()
    
    print("Generated unit ranking plots.")


def plot_learnable_vs_fixed(data, output_dir, dpi=300):
    """Compare performance of learnable vs fixed alpha for each unit."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Get final epoch results
    final_results = []
    for config in data["config"].unique():
        subset = data[data["config"] == config]
        last_epoch = subset.loc[subset["epoch"].idxmax()]
        final_results.append(last_epoch)
    
    final_df = pd.DataFrame(final_results)
    
    # Check if we have both learnable and fixed alpha data
    if not (True in final_df["learnable"].values and False in final_df["learnable"].values):
        print("Not enough data to compare learnable vs fixed alpha.")
        return
    
    # Calculate best performance for each unit by learnable/fixed
    best_configs = final_df.loc[final_df.groupby(["unit", "learnable"])["test_accuracy"].idxmax()]
    
    # Pivot for comparison
    comparison = best_configs.pivot_table(
        index="unit", 
        columns="learnable", 
        values=["test_accuracy", "test_loss", "alpha"]
    )
    
    # Flatten the column names
    comparison.columns = [f"{col[0]}_{col[1]}" for col in comparison.columns]
    comparison = comparison.reset_index()
    
    # Add delta columns
    if "test_accuracy_True" in comparison.columns and "test_accuracy_False" in comparison.columns:
        comparison["accuracy_delta"] = comparison["test_accuracy_True"] - comparison["test_accuracy_False"]
    
    if "test_loss_True" in comparison.columns and "test_loss_False" in comparison.columns:
        comparison["loss_delta"] = comparison["test_loss_False"] - comparison["test_loss_True"]
    
    # Plot accuracy comparison
    plt.figure(figsize=(14, 8))
    width = 0.35
    x = np.arange(len(comparison))
    
    plt.bar(x - width/2, comparison["test_accuracy_False"], width, label="Fixed Alpha", alpha=0.7)
    plt.bar(x + width/2, comparison["test_accuracy_True"], width, label="Learnable Alpha", alpha=0.7)
    
    plt.xlabel("Unit")
    plt.ylabel("Best Test Accuracy")
    plt.title("Best Test Accuracy: Learnable vs Fixed Alpha")
    plt.xticks(x, comparison["unit"], rotation=45)
    plt.legend()
    plt.grid(axis="y")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "learnable_vs_fixed_accuracy.png"), dpi=dpi)
    plt.close()
    
    # Plot loss comparison
    plt.figure(figsize=(14, 8))
    
    plt.bar(x - width/2, comparison["test_loss_False"], width, label="Fixed Alpha", alpha=0.7, color="salmon")
    plt.bar(x + width/2, comparison["test_loss_True"], width, label="Learnable Alpha", alpha=0.7, color="lightcoral")
    
    plt.xlabel("Unit")
    plt.ylabel("Best Test Loss")
    plt.title("Best Test Loss: Learnable vs Fixed Alpha")
    plt.xticks(x, comparison["unit"], rotation=45)
    plt.legend()
    plt.grid(axis="y")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "learnable_vs_fixed_loss.png"), dpi=dpi)
    plt.close()
    
    # Plot accuracy delta (improvement from using learnable alpha)
    if "accuracy_delta" in comparison.columns:
        plt.figure(figsize=(14, 8))
        bars = plt.bar(comparison["unit"], comparison["accuracy_delta"], alpha=0.7)
        
        # Color bars based on positive/negative
        for i, bar in enumerate(bars):
            bar.set_color("green" if comparison["accuracy_delta"].iloc[i] > 0 else "red")
        
        plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        plt.xlabel("Unit")
        plt.ylabel("Accuracy Improvement")
        plt.title("Accuracy Improvement from Using Learnable Alpha")
        plt.xticks(rotation=45)
        plt.grid(axis="y")
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "learnable_accuracy_improvement.png"), dpi=dpi)
        plt.close()
    
    print("Generated learnable vs fixed alpha comparison plots.")


def create_dashboard(data, output_dir, dpi=300):
    """Create a dashboard summarizing key findings."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Get final epoch results
    final_results = []
    for config in data["config"].unique():
        subset = data[data["config"] == config]
        last_epoch = subset.loc[subset["epoch"].idxmax()]
        final_results.append(last_epoch)
    
    final_df = pd.DataFrame(final_results)
    
    # Create a large figure for the dashboard
    fig = plt.figure(figsize=(20, 16))
    gs = GridSpec(3, 2, figure=fig)
    
    # 1. Best configurations by accuracy
    ax1 = fig.add_subplot(gs[0, 0])
    top_configs = final_df.sort_values(by="test_accuracy", ascending=False).head(10)
    y_pos = np.arange(len(top_configs))
    
    ax1.barh(y_pos, top_configs["test_accuracy"], align="center")
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels([f"{row['unit']} (α={row['alpha']:.2f}{'L' if row['learnable'] else ''})" 
                         for _, row in top_configs.iterrows()])
    ax1.invert_yaxis()  # Labels read top-to-bottom
    ax1.set_xlabel("Test Accuracy")
    ax1.set_title("Top 10 Configurations by Accuracy")
    
    # 2. Alpha impact on accuracy
    ax2 = fig.add_subplot(gs[0, 1])
    fixed_alpha = final_df[~final_df["learnable"]]
    
    for unit in fixed_alpha["unit"].unique():
        unit_data = fixed_alpha[fixed_alpha["unit"] == unit]
        ax2.plot(unit_data["alpha"], unit_data["test_accuracy"], "o-", label=unit)
    
    ax2.set_xlabel("Alpha Value")
    ax2.set_ylabel("Test Accuracy")
    ax2.set_title("Impact of Alpha on Accuracy")
    ax2.legend(loc="best")
    ax2.grid(True)
    
    # 3. Unit performance
    ax3 = fig.add_subplot(gs[1, 0])
    unit_performance = final_df.groupby("unit").agg({
        "test_accuracy": ["mean", "max"]
    }).reset_index()
    unit_performance.columns = ["unit", "mean_acc", "max_acc"]
    unit_performance = unit_performance.sort_values(by="mean_acc", ascending=False)
    
    ax3.bar(unit_performance["unit"], unit_performance["mean_acc"], alpha=0.7)
    
    for i, (_, row) in enumerate(unit_performance.iterrows()):
        ax3.plot([i, i], [row["mean_acc"], row["max_acc"]], 'black', linewidth=2)
        ax3.plot([i-0.2, i+0.2], [row["max_acc"], row["max_acc"]], 'black', linewidth=2)
    
    ax3.set_ylabel("Test Accuracy")
    ax3.set_title("Average and Max Accuracy by Unit")
    ax3.set_xticklabels(unit_performance["unit"], rotation=45)
    ax3.grid(axis="y")
    
    # 4. Learnable vs Fixed
    ax4 = fig.add_subplot(gs[1, 1])
    
    if True in final_df["learnable"].values and False in final_df["learnable"].values:
        learnable_summary = final_df.groupby("learnable").agg({
            "test_accuracy": ["mean", "std", "max"]
        }).reset_index()
        learnable_summary.columns = ["learnable", "mean_acc", "std_acc", "max_acc"]
        
        labels = ["Fixed Alpha", "Learnable Alpha"]
        ax4.bar([0, 1], learnable_summary["mean_acc"], yerr=learnable_summary["std_acc"],
               alpha=0.7, capsize=10)
        ax4.set_xticks([0, 1])
        ax4.set_xticklabels(labels)
        ax4.set_ylabel("Test Accuracy")
        ax4.set_title("Fixed vs Learnable Alpha")
        ax4.grid(axis="y")
    else:
        ax4.text(0.5, 0.5, "Not enough data for comparison", 
                ha="center", va="center", fontsize=12)
        ax4.set_title("Fixed vs Learnable Alpha")
    
    # 5. Training curves for top model
    ax5 = fig.add_subplot(gs[2, :])
    
    top_config = final_df.iloc[final_df["test_accuracy"].idxmax()]["config"]
    top_data = data[data["config"] == top_config].sort_values(by="epoch")
    
    ax5.plot(top_data["epoch"], top_data["train_accuracy"], label="Train Acc", color="blue")
    ax5.plot(top_data["epoch"], top_data["test_accuracy"], label="Test Acc", color="red")
    
    # Add loss curve on secondary y-axis
    ax5_2 = ax5.twinx()
    ax5_2.plot(top_data["epoch"], top_data["train_loss"], label="Train Loss", 
              color="lightblue", linestyle="--")
    ax5_2.plot(top_data["epoch"], top_data["test_loss"], label="Test Loss", 
              color="salmon", linestyle="--")
    
    # Add alpha evolution if available
    if "alpha" in top_data.columns and top_data["learnable"].iloc[0]:
        ax5_3 = ax5.twinx()
        ax5_3.spines["right"].set_position(("axes", 1.1))
        ax5_3.plot(top_data["epoch"], top_data["alpha"], label="Alpha", 
                  color="green", linestyle="-.")
        ax5_3.set_ylabel("Alpha Value", color="green")
    
    ax5.set_xlabel("Epoch")
    ax5.set_ylabel("Accuracy")
    ax5_2.set_ylabel("Loss")
    
    # Combine legends
    lines1, labels1 = ax5.get_legend_handles_labels()
    lines2, labels2 = ax5_2.get_legend_handles_labels()
    lines = lines1 + lines2
    labels = labels1 + labels2
    
    if "alpha" in top_data.columns and top_data["learnable"].iloc[0]:
        lines3, labels3 = ax5_3.get_legend_handles_labels()
        lines += lines3
        labels += labels3
    
    ax5.legend(lines, labels, loc="best")
    ax5.set_title(f"Training Curves for Best Model: {top_config}")
    ax5.grid(True)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "performance_dashboard.png"), dpi=dpi)
    plt.close()
    
    print("Generated performance dashboard.")


def main():
    args = parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Set seaborn style
    sns.set_style(args.style)
    
    # Load and process results
    print(f"Loading data from {args.results_dir}...")
    data = load_and_process_results(args.results_dir, args.units, args.alpha_values)
    
    if data is None or data.empty:
        print("No data found. Check the paths to the CSV files or unit/alpha filters.")
        return
    
    print(f"Found data from {len(data['config'].unique())} configurations.")
    
    # Generate all plots
    plot_training_curves(data, args.output_dir, args.dpi)
    plot_unit_comparison(data, args.output_dir, args.dpi)
    plot_heatmap(data, args.output_dir, args.dpi)
    plot_unit_rankings(data, args.output_dir, args.dpi)
    plot_learnable_vs_fixed(data, args.output_dir, args.dpi)
    create_dashboard(data, args.output_dir, args.dpi)
    
    print(f"All visualizations have been saved to {args.output_dir}")


if __name__ == "__main__":
    main() 