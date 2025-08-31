#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Meta-Analysis for paGating Hyperparameter Sweep Results

This script analyzes the results of paGating hyperparameter sweeps to extract insights,
identify best configurations, and detect trends in unit performance.

Usage:
    python scripts/analyze_results.py --results_dir results/run_20230101_120000/logs
                                     [--output_dir analysis]
                                     [--min_epochs 10]
                                     [--export_pdf]
"""

import os
import sys
import glob
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from pathlib import Path

try:
    import markdown
    import weasyprint
    HAS_PDF_EXPORT = True
except ImportError:
    HAS_PDF_EXPORT = False


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Analyze paGating hyperparameter sweep results")
    
    # Input/output arguments
    parser.add_argument("--results_dir", type=str, required=True,
                        help="Directory containing CSV logs from sweep")
    parser.add_argument("--output_dir", type=str, default="analysis",
                        help="Directory to save analysis outputs")
    
    # Analysis options
    parser.add_argument("--min_epochs", type=int, default=5,
                        help="Minimum number of epochs for a run to be considered")
    parser.add_argument("--alpha_threshold", type=float, default=0.01,
                        help="Threshold for significant alpha differences")
    parser.add_argument("--perf_threshold", type=float, default=0.005,
                        help="Threshold for significant performance differences")
    
    # Export options
    parser.add_argument("--export_pdf", action="store_true",
                        help="Export Markdown summary as PDF (requires markdown2 and weasyprint)")
    
    return parser.parse_args()


def collect_and_process_results(results_dir, min_epochs=5):
    """
    Collect and process all CSV log files from the sweep results.
    
    Args:
        results_dir: Directory containing CSV log files
        min_epochs: Minimum number of epochs required to include a run
        
    Returns:
        DataFrame with processed results
    """
    csv_files = glob.glob(os.path.join(results_dir, "*.csv"))
    all_results = []
    
    for file_path in csv_files:
        try:
            # Extract model info from filename
            filename = os.path.basename(file_path)
            parts = filename.replace(".csv", "").split("_")
            
            if len(parts) < 2:
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
            
            # Skip if not enough epochs
            if len(df) < min_epochs:
                print(f"Skipping {filename}: only {len(df)} epochs (min: {min_epochs})")
                continue
            
            # Extract metrics from last epoch
            last_epoch = df.iloc[-1]
            
            # Standardize column names
            column_mapping = {
                "train_acc": "train_accuracy",
                "val_acc": "test_accuracy",
                "val_loss": "test_loss"
            }
            
            # Create result entry with renamed columns
            result = {
                "unit": unit_name,
                "alpha": alpha,
                "learnable": learnable,
                "config": f"{unit_name}_alpha{alpha:.2f}" + ("_learnable" if learnable else ""),
                "epochs": len(df),
                "file_path": file_path
            }
            
            # Add metrics with standardized names
            for old_name, new_name in column_mapping.items():
                if old_name in last_epoch:
                    result[new_name] = last_epoch[old_name]
            
            # Add any missing columns
            for key in ["train_accuracy", "test_accuracy", "train_loss", "test_loss"]:
                if key not in result:
                    if key in last_epoch:
                        result[key] = last_epoch[key]
                    else:
                        result[key] = np.nan
            
            # Check if alpha ended up at a different value (for learnable alpha)
            if learnable and "alpha" in last_epoch:
                result["final_alpha"] = last_epoch["alpha"]
                result["alpha_diff"] = last_epoch["alpha"] - alpha
            else:
                result["final_alpha"] = alpha
                result["alpha_diff"] = 0.0
            
            all_results.append(result)
            
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
    
    if not all_results:
        print(f"No valid results found in {results_dir}")
        sys.exit(1)
        
    # Convert to DataFrame
    results_df = pd.DataFrame(all_results)
    return results_df


def find_best_configurations(results_df):
    """
    Find the best configurations for each unit and overall.
    
    Args:
        results_df: DataFrame with processed results
        
    Returns:
        Dictionary with best configurations
    """
    best_configs = {}
    
    # Find best static alpha configuration for each unit
    static_results = results_df[~results_df["learnable"]]
    if not static_results.empty:
        best_static_by_unit = {}
        for unit in static_results["unit"].unique():
            unit_results = static_results[static_results["unit"] == unit]
            if not unit_results.empty:
                best_idx = unit_results["test_accuracy"].idxmax()
                best_static_by_unit[unit] = unit_results.loc[best_idx]
        
        # Find overall best static configuration
        best_static_idx = static_results["test_accuracy"].idxmax()
        best_static_overall = static_results.loc[best_static_idx]
        
        best_configs["static"] = {
            "by_unit": best_static_by_unit,
            "overall": best_static_overall
        }
    
    # Find best learnable alpha configuration for each unit
    learnable_results = results_df[results_df["learnable"]]
    if not learnable_results.empty:
        best_learnable_by_unit = {}
        for unit in learnable_results["unit"].unique():
            unit_results = learnable_results[learnable_results["unit"] == unit]
            if not unit_results.empty:
                best_idx = unit_results["test_accuracy"].idxmax()
                best_learnable_by_unit[unit] = unit_results.loc[best_idx]
        
        # Find overall best learnable configuration
        best_learnable_idx = learnable_results["test_accuracy"].idxmax()
        best_learnable_overall = learnable_results.loc[best_learnable_idx]
        
        best_configs["learnable"] = {
            "by_unit": best_learnable_by_unit,
            "overall": best_learnable_overall
        }
    
    # Find global best configuration
    best_idx = results_df["test_accuracy"].idxmax()
    best_configs["global_best"] = results_df.loc[best_idx]
    
    return best_configs


def detect_trends(results_df, alpha_threshold=0.01, perf_threshold=0.005):
    """
    Detect trends in the results data.
    
    Args:
        results_df: DataFrame with processed results
        alpha_threshold: Threshold for significant alpha differences
        perf_threshold: Threshold for significant performance differences
        
    Returns:
        Dictionary with detected trends
    """
    trends = {}
    
    # Compare static vs learnable alpha for each unit
    units = results_df["unit"].unique()
    learnable_advantage = {}
    
    for unit in units:
        unit_results = results_df[results_df["unit"] == unit]
        
        static_results = unit_results[~unit_results["learnable"]]
        learnable_results = unit_results[unit_results["learnable"]]
        
        if not static_results.empty and not learnable_results.empty:
            best_static_acc = static_results["test_accuracy"].max()
            best_learnable_acc = learnable_results["test_accuracy"].max()
            
            advantage = best_learnable_acc - best_static_acc
            learnable_advantage[unit] = advantage
    
    # Sort units by learnable alpha advantage
    learnable_advantage = {k: v for k, v in sorted(
        learnable_advantage.items(), key=lambda item: item[1], reverse=True
    )}
    
    # Identify units where learnable alpha helps
    helps_units = [unit for unit, adv in learnable_advantage.items() if adv > perf_threshold]
    hurts_units = [unit for unit, adv in learnable_advantage.items() if adv < -perf_threshold]
    neutral_units = [unit for unit, adv in learnable_advantage.items() 
                    if abs(adv) <= perf_threshold]
    
    trends["learnable_advantage"] = learnable_advantage
    trends["helps_units"] = helps_units
    trends["hurts_units"] = hurts_units
    trends["neutral_units"] = neutral_units
    
    # Find best alpha values for each unit
    best_alphas = {}
    for unit in units:
        unit_static = results_df[(results_df["unit"] == unit) & (~results_df["learnable"])]
        if not unit_static.empty:
            # Group by alpha and find mean test accuracy
            alpha_performance = unit_static.groupby("alpha")["test_accuracy"].mean()
            best_alpha = alpha_performance.idxmax()
            best_alphas[unit] = best_alpha
    
    trends["best_alphas"] = best_alphas
    
    # Calculate stability (std dev of test accuracy)
    stability = {}
    for unit in units:
        unit_results = results_df[results_df["unit"] == unit]
        if not unit_results.empty:
            stability[unit] = unit_results["test_accuracy"].std()
    
    # Sort by stability (most stable first)
    stability = {k: v for k, v in sorted(
        stability.items(), key=lambda item: item[1]
    )}
    
    trends["stability"] = stability
    
    return trends


def generate_insights_markdown(results_df, best_configs, trends):
    """
    Generate a Markdown summary of the insights.
    
    Args:
        results_df: DataFrame with processed results
        best_configs: Dictionary with best configurations
        trends: Dictionary with detected trends
        
    Returns:
        Markdown string with insights
    """
    md = "# paGating Meta-Analysis Insights\n\n"
    md += f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    # Top performing unit overall
    md += "## 🌟 Top Performing Configurations\n\n"
    
    global_best = best_configs["global_best"]
    md += f"### Overall Best Configuration\n\n"
    md += f"- **Unit:** {global_best['unit']}\n"
    md += f"- **Alpha:** {global_best['alpha']:.2f}"
    if global_best["learnable"]:
        md += f" (learnable, converged to {global_best['final_alpha']:.2f})"
    md += "\n"
    md += f"- **Test Accuracy:** {global_best['test_accuracy']:.4f}\n"
    md += f"- **Test Loss:** {global_best['test_loss']:.4f}\n\n"
    
    # Best configurations by unit
    md += "### Best Configuration Per Unit\n\n"
    md += "| Unit | Best α | Learnable | Final α | Test Acc | Test Loss |\n"
    md += "|------|-------|-----------|---------|----------|----------|\n"
    
    # Combine best static and learnable configs
    best_by_unit = {}
    for unit in results_df["unit"].unique():
        unit_results = results_df[results_df["unit"] == unit]
        if not unit_results.empty:
            best_idx = unit_results["test_accuracy"].idxmax()
            best_by_unit[unit] = unit_results.loc[best_idx]
    
    # Sort by test accuracy
    best_by_unit_sorted = {k: v for k, v in sorted(
        best_by_unit.items(), key=lambda item: item[1]["test_accuracy"], reverse=True
    )}
    
    for unit, config in best_by_unit_sorted.items():
        learnable_str = "Yes" if config["learnable"] else "No"
        final_alpha = config["final_alpha"] if "final_alpha" in config else config["alpha"]
        
        md += f"| {unit} | {config['alpha']:.2f} | {learnable_str} | "
        md += f"{final_alpha:.2f} | {config['test_accuracy']:.4f} | {config['test_loss']:.4f} |\n"
    
    # Learnable alpha impact
    md += "\n## 🔁 Learnable Alpha Impact\n\n"
    
    if trends["helps_units"]:
        md += "### Units Where Learnable Alpha Improves Performance\n\n"
        md += "| Unit | Accuracy Improvement | Static Best | Learnable Best |\n"
        md += "|------|----------------------|-------------|---------------|\n"
        
        for unit in trends["helps_units"]:
            advantage = trends["learnable_advantage"][unit]
            static_best = best_configs["static"]["by_unit"].get(unit, {}).get("test_accuracy", np.nan)
            learnable_best = best_configs["learnable"]["by_unit"].get(unit, {}).get("test_accuracy", np.nan)
            
            md += f"| {unit} | +{advantage:.4f} | {static_best:.4f} | {learnable_best:.4f} |\n"
    else:
        md += "No units where learnable alpha significantly improves performance.\n\n"
    
    if trends["hurts_units"]:
        md += "\n### Units Where Learnable Alpha Hurts Performance\n\n"
        md += "| Unit | Accuracy Decrease | Static Best | Learnable Best |\n"
        md += "|------|-------------------|-------------|---------------|\n"
        
        for unit in trends["hurts_units"]:
            advantage = trends["learnable_advantage"][unit]
            static_best = best_configs["static"]["by_unit"].get(unit, {}).get("test_accuracy", np.nan)
            learnable_best = best_configs["learnable"]["by_unit"].get(unit, {}).get("test_accuracy", np.nan)
            
            md += f"| {unit} | {advantage:.4f} | {static_best:.4f} | {learnable_best:.4f} |\n"
    
    # Stability insights
    md += "\n## ⚖️ Stability Analysis\n\n"
    md += "Units ranked by stability (lower std dev = more stable):\n\n"
    md += "| Rank | Unit | Std Deviation | Min Accuracy | Max Accuracy | Range |\n"
    md += "|------|------|---------------|-------------|-------------|-------|\n"
    
    for rank, (unit, std_dev) in enumerate(trends["stability"].items(), 1):
        unit_results = results_df[results_df["unit"] == unit]
        min_acc = unit_results["test_accuracy"].min()
        max_acc = unit_results["test_accuracy"].max()
        range_acc = max_acc - min_acc
        
        md += f"| {rank} | {unit} | {std_dev:.4f} | {min_acc:.4f} | {max_acc:.4f} | {range_acc:.4f} |\n"
    
    # Suggested default alphas
    md += "\n## 💡 Suggested Default Alpha Values\n\n"
    md += "Recommended alpha values for each unit based on best performance:\n\n"
    md += "| Unit | Suggested α | Performance at α |\n"
    md += "|------|------------|------------------|\n"
    
    for unit, alpha in trends["best_alphas"].items():
        # Get performance at this alpha
        unit_at_alpha = results_df[(results_df["unit"] == unit) & 
                                  (results_df["alpha"] == alpha) &
                                  (~results_df["learnable"])]
        if not unit_at_alpha.empty:
            perf = unit_at_alpha["test_accuracy"].iloc[0]
            md += f"| {unit} | {alpha:.2f} | {perf:.4f} |\n"
    
    # Auto-detected trends section
    md += "\n## 🔍 Automatically Detected Trends\n\n"
    
    # Generate trend statements
    trend_statements = []
    
    # Learnable alpha trends
    if trends["helps_units"]:
        trend_statements.append(f"- Learnable alpha consistently improved accuracy for: {', '.join(trends['helps_units'])}")
    
    if trends["hurts_units"]:
        trend_statements.append(f"- Learnable alpha decreased accuracy for: {', '.join(trends['hurts_units'])}")
    
    if trends["neutral_units"]:
        trend_statements.append(f"- Learnable alpha had minimal impact on: {', '.join(trends['neutral_units'])}")
    
    # Best alpha trend statements
    for unit, alpha in trends["best_alphas"].items():
        trend_statements.append(f"- {unit} performed best at α={alpha:.2f}")
    
    # Most stable units
    most_stable = list(trends["stability"].keys())[:3]
    trend_statements.append(f"- Most stable units: {', '.join(most_stable)}")
    
    # Add all trend statements to markdown
    for statement in trend_statements:
        md += f"{statement}\n"
    
    return md


def export_pdf(markdown_content, output_path):
    """
    Export the Markdown content as a PDF.
    
    Args:
        markdown_content: Markdown content to export
        output_path: Path to save the PDF
        
    Returns:
        None
    """
    if not HAS_PDF_EXPORT:
        print("PDF export requires markdown and weasyprint libraries.")
        print("Install with: pip install markdown weasyprint")
        return False
    
    try:
        # Convert Markdown to HTML
        html_content = markdown.markdown(markdown_content)
        
        # Add basic styling
        styled_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                h1, h2, h3 {{ color: #333; }}
                h1 {{ border-bottom: 2px solid #333; padding-bottom: 10px; }}
                h2 {{ border-bottom: 1px solid #999; padding-bottom: 5px; margin-top: 30px; }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        # Convert to PDF
        weasyprint.HTML(string=styled_html).write_pdf(output_path)
        print(f"PDF exported to {output_path}")
        return True
    
    except Exception as e:
        print(f"Error exporting PDF: {str(e)}")
        return False


def plot_alpha_performance_curves(results_df, output_dir):
    """
    Plot test accuracy vs alpha for each unit.
    
    Args:
        results_df: DataFrame with processed results
        output_dir: Directory to save the plots
        
    Returns:
        None
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Filter for non-learnable alpha only
    static_results = results_df[~results_df["learnable"]]
    
    # Plot for each unit
    for unit in static_results["unit"].unique():
        unit_data = static_results[static_results["unit"] == unit]
        
        if len(unit_data) > 1:  # Only plot if we have multiple alpha values
            plt.figure(figsize=(10, 6))
            
            # Extract unique alpha values and corresponding accuracies
            alpha_acc = unit_data.sort_values("alpha")[["alpha", "test_accuracy"]]
            
            # Plot the curve
            plt.plot(alpha_acc["alpha"], alpha_acc["test_accuracy"], "o-", linewidth=2)
            
            # Find the best alpha
            best_idx = alpha_acc["test_accuracy"].idxmax()
            best_alpha = alpha_acc.loc[best_idx, "alpha"]
            best_acc = alpha_acc.loc[best_idx, "test_accuracy"]
            
            # Highlight the best point
            plt.scatter([best_alpha], [best_acc], color="red", s=100, zorder=10)
            plt.annotate(f"Best: α={best_alpha:.2f}\nAcc={best_acc:.4f}",
                        xy=(best_alpha, best_acc),
                        xytext=(10, -20),
                        textcoords="offset points",
                        arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"))
            
            plt.title(f"{unit}: Test Accuracy vs Alpha Value")
            plt.xlabel("Alpha Value")
            plt.ylabel("Test Accuracy")
            plt.grid(True)
            
            # Save the plot
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, f"{unit}_alpha_curve.png"), dpi=300)
            plt.close()
    
    # Create a combined plot with all units
    plt.figure(figsize=(12, 8))
    
    for unit in static_results["unit"].unique():
        unit_data = static_results[static_results["unit"] == unit]
        
        if len(unit_data) > 1:
            # Extract unique alpha values and corresponding accuracies
            alpha_acc = unit_data.sort_values("alpha")[["alpha", "test_accuracy"]]
            
            # Plot the curve
            plt.plot(alpha_acc["alpha"], alpha_acc["test_accuracy"], "o-", linewidth=2, label=unit)
    
    plt.title("Test Accuracy vs Alpha Value (All Units)")
    plt.xlabel("Alpha Value")
    plt.ylabel("Test Accuracy")
    plt.grid(True)
    plt.legend()
    
    # Save the plot
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "all_units_alpha_curves.png"), dpi=300)
    plt.close()


def plot_learnable_evolution(results_df, output_dir):
    """
    Plot the evolution of learnable alpha parameters.
    
    Args:
        results_df: DataFrame with processed results
        output_dir: Directory to save the plots
        
    Returns:
        None
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Get files with learnable alpha
    learnable_configs = results_df[results_df["learnable"]]
    
    if learnable_configs.empty:
        return
    
    for _, row in learnable_configs.iterrows():
        try:
            # Load the full training data to see alpha evolution
            df = pd.read_csv(row["file_path"])
            
            if "alpha" in df.columns:
                plt.figure(figsize=(10, 6))
                
                plt.plot(df["epoch"], df["alpha"], "o-", linewidth=2)
                
                # Mark start and end values
                start_alpha = df["alpha"].iloc[0]
                end_alpha = df["alpha"].iloc[-1]
                
                plt.scatter([df["epoch"].iloc[0], df["epoch"].iloc[-1]], 
                           [start_alpha, end_alpha],
                           color=["green", "red"], s=100, zorder=10)
                
                plt.annotate(f"Start: α={start_alpha:.2f}",
                            xy=(df["epoch"].iloc[0], start_alpha),
                            xytext=(10, 10),
                            textcoords="offset points",
                            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"))
                
                plt.annotate(f"End: α={end_alpha:.2f}",
                            xy=(df["epoch"].iloc[-1], end_alpha),
                            xytext=(10, -20),
                            textcoords="offset points",
                            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2"))
                
                plt.title(f"{row['unit']}: Learnable Alpha Evolution (init={row['alpha']:.2f})")
                plt.xlabel("Epoch")
                plt.ylabel("Alpha Value")
                plt.grid(True)
                
                # Save the plot
                plt.tight_layout()
                plt.savefig(os.path.join(output_dir, f"{row['config']}_alpha_evolution.png"), dpi=300)
                plt.close()
        
        except Exception as e:
            print(f"Error plotting alpha evolution for {row['config']}: {str(e)}")


def main():
    """Main function to run the analysis."""
    args = parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    print(f"Analyzing results from {args.results_dir}...")
    
    # Collect and process results
    results_df = collect_and_process_results(args.results_dir, args.min_epochs)
    
    if results_df.empty:
        print("No valid results found.")
        sys.exit(1)
    
    print(f"Found {len(results_df)} valid configurations.")
    
    # Find best configurations
    best_configs = find_best_configurations(results_df)
    
    # Detect trends
    trends = detect_trends(results_df, args.alpha_threshold, args.perf_threshold)
    
    # Generate insights Markdown
    insights_md = generate_insights_markdown(results_df, best_configs, trends)
    
    # Save Markdown to file
    md_path = os.path.join(args.output_dir, "insights_summary.md")
    with open(md_path, "w") as f:
        f.write(insights_md)
    
    print(f"Insights summary saved to {md_path}")
    
    # Export PDF if requested
    if args.export_pdf:
        if HAS_PDF_EXPORT:
            pdf_path = os.path.join(args.output_dir, "insights_summary.pdf")
            export_pdf(insights_md, pdf_path)
        else:
            print("PDF export requires markdown and weasyprint libraries.")
            print("Install with: pip install markdown weasyprint")
    
    # Generate plots
    plots_dir = os.path.join(args.output_dir, "plots")
    os.makedirs(plots_dir, exist_ok=True)
    
    print("Generating alpha performance curves...")
    plot_alpha_performance_curves(results_df, plots_dir)
    
    print("Generating learnable alpha evolution plots...")
    plot_learnable_evolution(results_df, plots_dir)
    
    # Print summary to console
    print("\n" + "=" * 80)
    print("ANALYSIS SUMMARY")
    print("=" * 80)
    
    # Global best
    global_best = best_configs["global_best"]
    print(f"\n🌟 Top Performing Configuration:")
    print(f"   Unit: {global_best['unit']}")
    print(f"   Alpha: {global_best['alpha']:.2f}" + 
          (f" (learnable, converged to {global_best['final_alpha']:.2f})" if global_best["learnable"] else ""))
    print(f"   Test Accuracy: {global_best['test_accuracy']:.4f}")
    
    # Units where learnable alpha helps
    if trends["helps_units"]:
        print(f"\n🔁 Units where learnable alpha improves performance:")
        for unit in trends["helps_units"]:
            print(f"   {unit}: +{trends['learnable_advantage'][unit]:.4f} accuracy")
    
    # Most stable units
    most_stable = list(trends["stability"].keys())[:3]
    print(f"\n⚖️ Most stable units (lowest std dev):")
    for unit in most_stable:
        print(f"   {unit}: {trends['stability'][unit]:.4f} std dev")
    
    # Suggested default alphas
    print(f"\n💡 Suggested default alpha values:")
    for unit, alpha in trends["best_alphas"].items():
        print(f"   {unit}: α={alpha:.2f}")
    
    print("\n" + "=" * 80)
    print(f"Full analysis saved to {args.output_dir}")
    print("=" * 80)


if __name__ == "__main__":
    main() 