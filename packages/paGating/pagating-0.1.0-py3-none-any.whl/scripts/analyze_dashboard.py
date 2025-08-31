#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Interactive Streamlit Dashboard for paGating Hyperparameter Sweep Results

This script creates an interactive dashboard to visualize and explore 
the results of paGating hyperparameter sweeps.

Usage:
    streamlit run scripts/analyze_dashboard.py -- --results_dir results/run_20230101_120000/logs
"""

import os
import sys
import glob
import argparse
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path

# Add the parent directory to sys.path to import from scripts
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.analyze_results import collect_and_process_results, find_best_configurations, detect_trends


def parse_args():
    """Parse command line arguments when run from command line."""
    parser = argparse.ArgumentParser(description="Interactive dashboard for paGating results analysis")
    
    parser.add_argument("--results_dir", type=str, required=False,
                        help="Directory containing CSV logs from sweep")
    parser.add_argument("--min_epochs", type=int, default=5,
                        help="Minimum number of epochs for a run to be considered")
    
    # Parse args only if streamlit is calling this script with args
    if len(sys.argv) > 1 and sys.argv[1] == "--":
        return parser.parse_args(sys.argv[2:])
    else:
        return parser.parse_args([])


@st.cache_data
def load_results(results_dir, min_epochs=5):
    """Load and process results data, with caching for performance."""
    results_df = collect_and_process_results(results_dir, min_epochs)
    best_configs = find_best_configurations(results_df)
    trends = detect_trends(results_df)
    
    return results_df, best_configs, trends


def plot_unit_comparison(results_df):
    """Create a plotly boxplot comparing unit performances."""
    fig = go.Figure()
    
    # Add box plot for each unit
    fig.add_trace(go.Box(
        x=results_df["unit"],
        y=results_df["test_accuracy"],
        boxmean=True,
        marker_color='lightseagreen',
        boxpoints='all'
    ))
    
    # Update layout
    fig.update_layout(
        title="Performance Comparison Across Units",
        xaxis_title="Unit",
        yaxis_title="Test Accuracy",
        template="plotly_white",
        height=500,
    )
    
    return fig


def plot_alpha_curves(results_df, selected_units=None):
    """Plot test accuracy vs alpha value."""
    # Filter for non-learnable alpha only
    static_results = results_df[~results_df["learnable"]]
    
    # Filter for selected units if provided
    if selected_units and len(selected_units) > 0:
        static_results = static_results[static_results["unit"].isin(selected_units)]
    
    # Create figure
    fig = px.line(
        static_results, 
        x="alpha", 
        y="test_accuracy", 
        color="unit",
        markers=True,
        title="Test Accuracy vs Alpha Value"
    )
    
    return fig


def dashboard_layout(results_df, best_configs, trends):
    """Create the main dashboard layout."""
    st.set_page_config(
        page_title="paGating Analysis Dashboard",
        page_icon="📊",
        layout="wide"
    )
    
    # Header
    st.title("📊 paGating Analysis Dashboard")
    st.markdown(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    
    # Top metrics row
    st.header("🌟 Top Performing Configurations")
    
    global_best = best_configs["global_best"]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Best Unit", global_best["unit"])
    
    with col2:
        alpha_label = f"{global_best['alpha']:.2f}"
        if global_best["learnable"]:
            alpha_label += f" → {global_best['final_alpha']:.2f}"
        
        st.metric("Best Alpha", alpha_label)
    
    with col3:
        st.metric("Best Test Accuracy", f"{global_best['test_accuracy']:.4f}")
    
    # Unit comparison section
    st.header("📈 Unit Performance Comparison")
    tabs = st.tabs(["Box Plot", "Alpha Curves"])
    
    with tabs[0]:
        st.plotly_chart(plot_unit_comparison(results_df), use_container_width=True)
    
    with tabs[1]:
        # Unit selection for filtering visualizations
        all_units = sorted(results_df["unit"].unique())
        selected_units = st.multiselect(
            "Select Units to Display",
            options=all_units,
            default=all_units[:min(5, len(all_units))]
        )
        
        st.plotly_chart(plot_alpha_curves(results_df, selected_units), use_container_width=True)
    
    # Suggested default alphas
    st.header("💡 Suggested Default Alpha Values")
    
    default_data = []
    for unit, alpha in trends["best_alphas"].items():
        unit_at_alpha = results_df[
            (results_df["unit"] == unit) & 
            (results_df["alpha"] == alpha) &
            (~results_df["learnable"])
        ]
        
        if not unit_at_alpha.empty:
            perf = unit_at_alpha["test_accuracy"].iloc[0]
            default_data.append({
                "Unit": unit,
                "Suggested Alpha": alpha,
                "Performance": perf
            })
    
    default_df = pd.DataFrame(default_data)
    default_df = default_df.sort_values("Performance", ascending=False)
    
    st.dataframe(default_df)
    
    # Footer
    st.markdown("---")
    st.caption("paGating Analysis Dashboard")


def main():
    """Main function to run the dashboard."""
    args = parse_args()
    
    if args.results_dir:
        # If results_dir is provided via command line, use it
        results_dir = args.results_dir
        min_epochs = args.min_epochs
    else:
        # Otherwise, use a file uploader or directory selector in the app
        st.sidebar.title("paGating Analysis")
        
        # Option 1: Select from predefined results directories
        default_results_dirs = [
            d for d in glob.glob("results/*/logs") 
            if os.path.isdir(d) and len(glob.glob(os.path.join(d, "*.csv"))) > 0
        ]
        
        if default_results_dirs:
            results_dir = st.sidebar.selectbox(
                "Select Results Directory",
                options=default_results_dirs,
                format_func=lambda x: os.path.basename(os.path.dirname(x))
            )
        else:
            # Option 2: Enter a custom path
            results_dir = st.sidebar.text_input(
                "Enter Results Directory Path",
                value="results/latest/logs" if os.path.exists("results/latest/logs") else ""
            )
        
        # Option for minimum epochs
        min_epochs = st.sidebar.slider(
            "Minimum Epochs Required",
            min_value=1,
            max_value=50,
            value=5
        )
        
        # Check if the directory exists and contains CSV files
        if not os.path.isdir(results_dir):
            st.error(f"Directory not found: {results_dir}")
            st.info("Please provide a valid results directory path.")
            return
        
        if not glob.glob(os.path.join(results_dir, "*.csv")):
            st.error(f"No CSV files found in: {results_dir}")
            st.info("The results directory should contain CSV log files.")
            return
    
    # Load the results data
    results_df, best_configs, trends = load_results(results_dir, min_epochs)
    
    # Create the dashboard layout
    dashboard_layout(results_df, best_configs, trends)


if __name__ == "__main__":
    main()
