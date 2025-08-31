#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HTML Report Generator for paGating Hyperparameter Sweep Results

This script generates a comprehensive HTML report with embedded plots
from the results of paGating hyperparameter sweeps.

Usage:
    python scripts/generate_html_report.py --results_dir results/run_20230101_120000/logs
                                          [--output_file pagating_report.html]
                                          [--min_epochs 5]
"""

import os
import sys
import glob
import base64
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from pathlib import Path
from io import BytesIO
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

# Add the parent directory to sys.path to import from scripts
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.analyze_results import collect_and_process_results, find_best_configurations, detect_trends


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Generate HTML report for paGating results")
    
    parser.add_argument("--results_dir", type=str, required=True,
                        help="Directory containing CSV logs from sweep")
    parser.add_argument("--output_file", type=str, default="pagating_report.html",
                        help="Output HTML file path")
    parser.add_argument("--min_epochs", type=int, default=5,
                        help="Minimum number of epochs for a run to be considered")
    
    return parser.parse_args()


def fig_to_base64(fig):
    """Convert matplotlib figure to base64 encoded string for HTML embedding."""
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close(fig)
    return img_str


def plot_unit_comparison_boxplot(results_df):
    """Create a boxplot comparing unit performances."""
    plt.figure(figsize=(12, 6))
    
    # Sort units by median performance
    order = results_df.groupby('unit')['test_accuracy'].median().sort_values(ascending=False).index
    
    # Create the boxplot
    ax = sns.boxplot(data=results_df, x='unit', y='test_accuracy', order=order, palette='viridis')
    
    # Add individual points
    sns.stripplot(data=results_df, x='unit', y='test_accuracy', order=order, 
                 size=4, color='.3', linewidth=0, jitter=True, alpha=0.5)
    
    # Customize the plot
    plt.title('Unit Performance Comparison', fontsize=14)
    plt.xlabel('Unit', fontsize=12)
    plt.ylabel('Test Accuracy', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Get the figure and convert to base64
    fig = plt.gcf()
    return fig_to_base64(fig)


def plot_alpha_performance_curves(results_df, unit=None):
    """Create a plot showing test accuracy vs alpha value."""
    # Filter for non-learnable alpha only
    static_results = results_df[~results_df["learnable"]]
    
    # Filter for a specific unit if provided
    if unit:
        static_results = static_results[static_results["unit"] == unit]
        plt.figure(figsize=(10, 5))
        title = f"{unit}: Test Accuracy vs Alpha Value"
    else:
        # Create figure for all units
        plt.figure(figsize=(12, 6))
        title = "Test Accuracy vs Alpha Value (All Units)"
    
    # Create a plot for each unit
    for unit_name in sorted(static_results["unit"].unique()):
        unit_data = static_results[static_results["unit"] == unit_name]
        if len(unit_data) <= 1:
            continue
            
        # Sort by alpha value
        unit_data = unit_data.sort_values("alpha")
        
        # Plot the curve
        plt.plot(unit_data["alpha"], unit_data["test_accuracy"], 'o-', linewidth=2, label=unit_name)
        
        # Find and highlight the best alpha
        best_idx = unit_data["test_accuracy"].idxmax()
        best_alpha = unit_data.loc[best_idx, "alpha"]
        best_acc = unit_data.loc[best_idx, "test_accuracy"]
        
        plt.scatter([best_alpha], [best_acc], marker='*', s=150, 
                    edgecolor='black', linewidth=1.5, zorder=10)
    
    # Customize the plot
    plt.title(title, fontsize=14)
    plt.xlabel('Alpha Value', fontsize=12)
    plt.ylabel('Test Accuracy', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    
    if not unit:  # Only add legend for multi-unit plot
        plt.legend(title="Unit", loc='best')
    
    plt.tight_layout()
    
    # Get the figure and convert to base64
    fig = plt.gcf()
    return fig_to_base64(fig)


def plot_learnable_alpha_evolution(results_df, unit=None):
    """Create a plot showing the evolution of learnable alpha parameters."""
    # Get files with learnable alpha
    learnable_configs = results_df[results_df["learnable"]]
    
    # Filter for a specific unit if provided
    if unit:
        learnable_configs = learnable_configs[learnable_configs["unit"] == unit]
    
    if learnable_configs.empty:
        return None
    
    plt.figure(figsize=(12, 6))
    
    for _, row in learnable_configs.iterrows():
        try:
            # Load the full training data
            df = pd.read_csv(row["file_path"])
            
            if "alpha" in df.columns:
                label = f"{row['unit']} (init={row['alpha']:.2f})"
                plt.plot(df["epoch"], df["alpha"], 'o-', linewidth=2, label=label)
                
                # Mark start and end points
                plt.scatter([0, df["epoch"].iloc[-1]], 
                           [df["alpha"].iloc[0], df["alpha"].iloc[-1]],
                           s=[80, 120], marker='o', zorder=10,
                           edgecolor='black', linewidth=1.5)
        except Exception as e:
            print(f"Error plotting alpha evolution for {row['config']}: {str(e)}")
    
    # Customize the plot
    title = f"{unit}: Learnable Alpha Evolution" if unit else "Learnable Alpha Evolution"
    plt.title(title, fontsize=14)
    plt.xlabel('Epoch', fontsize=12)
    plt.ylabel('Alpha Value', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    
    if not unit:  # Only add legend for multi-unit plot
        plt.legend(title="Configuration", loc='best')
    
    plt.tight_layout()
    
    # Get the figure and convert to base64
    fig = plt.gcf()
    return fig_to_base64(fig)


def plot_stability_heatmap(results_df):
    """Create a heatmap showing the stability of different units across alpha values."""
    # Filter for non-learnable alpha
    static_results = results_df[~results_df["learnable"]]
    
    # Create a pivot table with units as rows and alpha as columns
    pivot_data = static_results.pivot_table(
        index="unit", 
        columns="alpha", 
        values="test_accuracy",
        aggfunc="mean"
    )
    
    # Calculate stability (std dev across alpha values)
    pivot_data["std_dev"] = pivot_data.std(axis=1)
    pivot_data = pivot_data.sort_values("std_dev")
    
    # Create heatmap without the std_dev column
    heatmap_data = pivot_data.drop(columns=["std_dev"])
    
    plt.figure(figsize=(12, 7))
    
    # Create the heatmap
    ax = sns.heatmap(
        heatmap_data, 
        annot=True, 
        cmap="viridis", 
        fmt=".4f",
        cbar_kws={'label': 'Test Accuracy'}
    )
    
    # Customize the plot
    plt.title('Unit Performance Across Alpha Values', fontsize=14)
    plt.xlabel('Alpha Value', fontsize=12)
    plt.ylabel('Unit', fontsize=12)
    plt.tight_layout()
    
    # Get the figure and convert to base64
    fig = plt.gcf()
    return fig_to_base64(fig), pivot_data


def generate_html_report(results_df, best_configs, trends, output_file):
    """Generate a comprehensive HTML report with embedded plots."""
    # Generate plots
    unit_comparison_plot = plot_unit_comparison_boxplot(results_df)
    alpha_curve_plot = plot_alpha_performance_curves(results_df)
    learnable_plot = plot_learnable_alpha_evolution(results_df)
    stability_plot, stability_data = plot_stability_heatmap(results_df)
    
    # Generate per-unit alpha curves
    unit_alpha_plots = {}
    for unit in sorted(results_df["unit"].unique()):
        unit_plot = plot_alpha_performance_curves(results_df, unit)
        unit_alpha_plots[unit] = unit_plot
    
    # Generate per-unit learnable alpha evolution plots
    unit_learnable_plots = {}
    for unit in sorted(results_df["unit"].unique()):
        if any(results_df[results_df["unit"] == unit]["learnable"]):
            unit_learn_plot = plot_learnable_alpha_evolution(results_df, unit)
            unit_learnable_plots[unit] = unit_learn_plot
    
    # Format data for tables
    global_best = best_configs["global_best"]
    
    # Best configuration per unit table
    best_by_unit = {}
    for unit in results_df["unit"].unique():
        unit_results = results_df[results_df["unit"] == unit]
        if not unit_results.empty:
            best_idx = unit_results["test_accuracy"].idxmax()
            best_by_unit[unit] = unit_results.loc[best_idx]
    
    # Sort by test accuracy
    best_by_unit_sorted = sorted(
        best_by_unit.items(), 
        key=lambda item: item[1]["test_accuracy"], 
        reverse=True
    )
    
    # Learnable alpha impact data
    helps_units_data = []
    for unit in trends.get("helps_units", []):
        advantage = trends["learnable_advantage"][unit]
        static_best = best_configs["static"]["by_unit"].get(unit, {}).get("test_accuracy", np.nan)
        learnable_best = best_configs["learnable"]["by_unit"].get(unit, {}).get("test_accuracy", np.nan)
        
        helps_units_data.append({
            "unit": unit,
            "advantage": advantage,
            "static_best": static_best,
            "learnable_best": learnable_best
        })
    
    # Sort by advantage
    helps_units_data = sorted(helps_units_data, key=lambda x: x["advantage"], reverse=True)
    
    # Units where learnable alpha hurts
    hurts_units_data = []
    for unit in trends.get("hurts_units", []):
        advantage = trends["learnable_advantage"][unit]
        static_best = best_configs["static"]["by_unit"].get(unit, {}).get("test_accuracy", np.nan)
        learnable_best = best_configs["learnable"]["by_unit"].get(unit, {}).get("test_accuracy", np.nan)
        
        hurts_units_data.append({
            "unit": unit,
            "advantage": advantage,
            "static_best": static_best,
            "learnable_best": learnable_best
        })
    
    # Sort by disadvantage
    hurts_units_data = sorted(hurts_units_data, key=lambda x: x["advantage"])
    
    # Stability ranking
    stability_ranking = []
    for unit, std_dev in trends["stability"].items():
        unit_results = results_df[results_df["unit"] == unit]
        min_acc = unit_results["test_accuracy"].min()
        max_acc = unit_results["test_accuracy"].max()
        range_acc = max_acc - min_acc
        
        stability_ranking.append({
            "unit": unit,
            "std_dev": std_dev,
            "min_acc": min_acc,
            "max_acc": max_acc,
            "range": range_acc
        })
    
    # Suggested default alphas
    default_alphas = []
    for unit, alpha in trends["best_alphas"].items():
        # Get performance at this alpha
        unit_at_alpha = results_df[
            (results_df["unit"] == unit) & 
            (results_df["alpha"] == alpha) &
            (~results_df["learnable"])
        ]
        
        if not unit_at_alpha.empty:
            perf = unit_at_alpha["test_accuracy"].iloc[0]
            default_alphas.append({
                "unit": unit,
                "alpha": alpha,
                "performance": perf
            })
    
    # Sort by performance
    default_alphas = sorted(default_alphas, key=lambda x: x["performance"], reverse=True)
    
    # Generate trend statements
    trend_statements = []
    
    # Learnable alpha trends
    if trends.get("helps_units"):
        trend_statements.append(f"Learnable alpha consistently improved accuracy for: {', '.join(trends['helps_units'])}")
    
    if trends.get("hurts_units"):
        trend_statements.append(f"Learnable alpha decreased accuracy for: {', '.join(trends['hurts_units'])}")
    
    if trends.get("neutral_units"):
        trend_statements.append(f"Learnable alpha had minimal impact on: {', '.join(trends['neutral_units'])}")
    
    # Best alpha trend statements
    for unit, alpha in trends["best_alphas"].items():
        trend_statements.append(f"{unit} performed best at α={alpha:.2f}")
    
    # Most stable units
    most_stable = list(trends["stability"].keys())[:3]
    trend_statements.append(f"Most stable units: {', '.join(most_stable)}")
    
    # Begin generating HTML content
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>paGating Analysis Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #2c3e50;
            border-bottom: 1px solid #bdc3c7;
            padding-bottom: 5px;
            margin-top: 30px;
        }}
        h3 {{
            color: #2c3e50;
        }}
        .top-metrics {{
            display: flex;
            justify-content: space-between;
            margin: 20px 0;
            flex-wrap: wrap;
        }}
        .metric-card {{
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            width: 30%;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .metric-card h3 {{
            margin: 0 0 10px 0;
            color: #3498db;
        }}
        .metric-value {{
            font-size: 24px;
            font-weight: bold;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #f2f2f2;
            font-weight: bold;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .plot-container {{
            margin: 20px 0;
            text-align: center;
        }}
        .plot-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .plot-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .trend-item {{
            background-color: #f8f9fa;
            padding: 10px 15px;
            border-radius: 5px;
            margin: 5px 0;
            border-left: 4px solid #3498db;
        }}
        .positive {{
            color: #27ae60;
        }}
        .negative {{
            color: #e74c3c;
        }}
        .timestamp {{
            color: #7f8c8d;
            font-style: italic;
            margin-top: 5px;
        }}
        footer {{
            margin-top: 40px;
            text-align: center;
            color: #7f8c8d;
            border-top: 1px solid #eee;
            padding-top: 20px;
        }}
    </style>
</head>
<body>
    <h1>paGating Meta-Analysis Report</h1>
    <p class="timestamp">Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <h2>🌟 Top Performing Configurations</h2>
    <div class="top-metrics">
        <div class="metric-card">
            <h3>Best Unit</h3>
            <div class="metric-value">{global_best["unit"]}</div>
        </div>
        <div class="metric-card">
            <h3>Best Alpha</h3>
            <div class="metric-value">
                {global_best["alpha"]:.2f}
                {f" → {global_best['final_alpha']:.2f}" if global_best["learnable"] else ""}
            </div>
            <div>{("Learnable" if global_best["learnable"] else "Static")}</div>
        </div>
        <div class="metric-card">
            <h3>Best Test Accuracy</h3>
            <div class="metric-value">{global_best["test_accuracy"]:.4f}</div>
            <div>Test Loss: {global_best["test_loss"]:.4f}</div>
        </div>
    </div>
    
    <h3>Best Configuration Per Unit</h3>
    <table>
        <tr>
            <th>Unit</th>
            <th>Best α</th>
            <th>Learnable</th>
            <th>Final α</th>
            <th>Test Accuracy</th>
            <th>Test Loss</th>
        </tr>
"""

    # Add rows for best configuration per unit
    for unit, config in best_by_unit_sorted:
        learnable_str = "Yes" if config["learnable"] else "No"
        final_alpha = config["final_alpha"] if "final_alpha" in config else config["alpha"]
        
        html_content += f"""
        <tr>
            <td>{unit}</td>
            <td>{config["alpha"]:.2f}</td>
            <td>{learnable_str}</td>
            <td>{final_alpha:.2f}</td>
            <td>{config["test_accuracy"]:.4f}</td>
            <td>{config["test_loss"]:.4f}</td>
        </tr>"""
    
    html_content += """
    </table>
    
    <h2>📈 Unit Performance Comparison</h2>
    <div class="plot-container">
        <img src="data:image/png;base64,""" + unit_comparison_plot + """" alt="Unit Performance Comparison">
    </div>
    
    <h2>📊 Alpha Performance Curves</h2>
    <div class="plot-container">
        <img src="data:image/png;base64,""" + alpha_curve_plot + """" alt="Alpha Performance Curves">
    </div>
    
    <h3>Individual Unit Alpha Curves</h3>
    <div class="plot-grid">
"""

    # Add individual unit alpha curves
    for unit, plot in unit_alpha_plots.items():
        html_content += f"""
        <div class="plot-container">
            <img src="data:image/png;base64,{plot}" alt="{unit} Alpha Curve">
        </div>"""
    
    html_content += """
    </div>
    
    <h2>🔄 Learnable Alpha Evolution</h2>
"""

    # Add learnable alpha evolution plot if available
    if learnable_plot:
        html_content += """
    <div class="plot-container">
        <img src="data:image/png;base64,""" + learnable_plot + """" alt="Learnable Alpha Evolution">
    </div>
    
    <h3>Individual Unit Learnable Alpha Evolution</h3>
    <div class="plot-grid">
"""

        # Add individual unit learnable alpha plots
        for unit, plot in unit_learnable_plots.items():
            if plot:
                html_content += f"""
        <div class="plot-container">
            <img src="data:image/png;base64,{plot}" alt="{unit} Learnable Alpha Evolution">
        </div>"""
        
        html_content += """
    </div>
"""
    else:
        html_content += """
    <p>No learnable alpha configurations found in the results.</p>
"""
    
    html_content += """
    <h2>⚖️ Stability Analysis</h2>
    <div class="plot-container">
        <img src="data:image/png;base64,""" + stability_plot + """" alt="Stability Heatmap">
    </div>
    
    <h3>Unit Stability Ranking</h3>
    <table>
        <tr>
            <th>Rank</th>
            <th>Unit</th>
            <th>Std Deviation</th>
            <th>Min Accuracy</th>
            <th>Max Accuracy</th>
            <th>Range</th>
        </tr>
"""

    # Add rows for stability ranking
    for rank, data in enumerate(stability_ranking, 1):
        html_content += f"""
        <tr>
            <td>{rank}</td>
            <td>{data["unit"]}</td>
            <td>{data["std_dev"]:.4f}</td>
            <td>{data["min_acc"]:.4f}</td>
            <td>{data["max_acc"]:.4f}</td>
            <td>{data["range"]:.4f}</td>
        </tr>"""
    
    html_content += """
    </table>
    
    <h2>🔁 Learnable Alpha Impact</h2>
"""

    # Add learnable alpha impact tables if available
    if helps_units_data:
        html_content += """
    <h3>Units Where Learnable Alpha Improves Performance</h3>
    <table>
        <tr>
            <th>Unit</th>
            <th>Accuracy Improvement</th>
            <th>Static Best</th>
            <th>Learnable Best</th>
        </tr>
"""

        for data in helps_units_data:
            html_content += f"""
        <tr>
            <td>{data["unit"]}</td>
            <td class="positive">+{data["advantage"]:.4f}</td>
            <td>{data["static_best"]:.4f}</td>
            <td>{data["learnable_best"]:.4f}</td>
        </tr>"""
        
        html_content += """
    </table>
"""
    else:
        html_content += """
    <p>No units where learnable alpha significantly improves performance.</p>
"""

    if hurts_units_data:
        html_content += """
    <h3>Units Where Learnable Alpha Hurts Performance</h3>
    <table>
        <tr>
            <th>Unit</th>
            <th>Accuracy Decrease</th>
            <th>Static Best</th>
            <th>Learnable Best</th>
        </tr>
"""

        for data in hurts_units_data:
            html_content += f"""
        <tr>
            <td>{data["unit"]}</td>
            <td class="negative">{data["advantage"]:.4f}</td>
            <td>{data["static_best"]:.4f}</td>
            <td>{data["learnable_best"]:.4f}</td>
        </tr>"""
        
        html_content += """
    </table>
"""
    else:
        html_content += """
    <p>No units where learnable alpha significantly hurts performance.</p>
"""

    html_content += """
    <h2>💡 Suggested Default Alpha Values</h2>
    <table>
        <tr>
            <th>Unit</th>
            <th>Suggested α</th>
            <th>Performance at α</th>
        </tr>
"""

    # Add rows for suggested default alphas
    for data in default_alphas:
        html_content += f"""
        <tr>
            <td>{data["unit"]}</td>
            <td>{data["alpha"]:.2f}</td>
            <td>{data["performance"]:.4f}</td>
        </tr>"""
    
    html_content += """
    </table>
    
    <h2>🔍 Automatically Detected Trends</h2>
"""

    # Add trend statements
    for statement in trend_statements:
        html_content += f"""
    <div class="trend-item">{statement}</div>"""
    
    html_content += """
    <footer>
        <p>paGating Analysis Report • <a href="https://github.com/yourusername/paGating">GitHub</a></p>
    </footer>
</body>
</html>
"""

    # Write HTML content to file
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    print(f"HTML report saved to: {output_file}")
    
    return output_file


def main():
    """Main function to run the report generation."""
    args = parse_args()
    
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
    trends = detect_trends(results_df)
    
    # Generate HTML report
    output_file = generate_html_report(results_df, best_configs, trends, args.output_file)
    
    print(f"HTML report generation complete. Report saved to: {output_file}")


if __name__ == "__main__":
    main() 