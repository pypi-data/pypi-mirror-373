#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Interactive Dashboard for paGating Results

This script creates an interactive Streamlit dashboard for visualizing
and exploring paGating experiment results, allowing users to compare
different gating units and alpha configurations.

Usage:
    streamlit run scripts/streamlit_dashboard.py -- --results_dir results/run_20230101_120000
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
from plotly.subplots import make_subplots
from datetime import datetime
from pathlib import Path

# Import functions from analyze_results.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from analyze_results import collect_and_process_results, find_best_configurations, detect_trends


def parse_args():
    """Parse command line arguments when run directly (not through streamlit)."""
    parser = argparse.ArgumentParser(description="Interactive dashboard for paGating results")
    
    # Input arguments
    parser.add_argument("--results_dir", type=str, required=True,
                        help="Directory containing CSV logs from sweep")
    parser.add_argument("--min_epochs", type=int, default=5,
                        help="Minimum number of epochs for a run to be considered")
    
    return parser.parse_args()


def setup_page():
    """Configure the Streamlit page layout and title."""
    st.set_page_config(
        page_title="paGating Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    st.title("paGating Interactive Results Dashboard")
    st.markdown("Explore performance metrics for different gating units and configurations")


def load_data(results_dir, min_epochs=5):
    """Load and process the results data."""
    with st.spinner("Loading experiment data..."):
        # Use the function from analyze_results.py
        results_df = collect_and_process_results(results_dir, min_epochs)
        
        if results_df.empty:
            st.error(f"No valid results found in {results_dir}")
            st.stop()
        
        # Cache additional analysis
        best_configs = find_best_configurations(results_df)
        trends = detect_trends(results_df)
        
        return results_df, best_configs, trends


def plot_leaderboard(results_df):
    """Plot an interactive leaderboard of all configurations."""
    st.header("🏆 Configuration Leaderboard")
    
    # Add rank column
    leaderboard = results_df.sort_values("test_accuracy", ascending=False).reset_index(drop=True)
    leaderboard["rank"] = leaderboard.index + 1
    
    # Prepare columns for display
    display_cols = [
        "rank", "unit", "alpha", "learnable", "final_alpha", 
        "test_accuracy", "test_loss", "train_accuracy", "train_loss", "epochs"
    ]
    display_cols = [col for col in display_cols if col in leaderboard.columns]
    
    # Format columns
    display_df = leaderboard[display_cols].copy()
    for col in ["test_accuracy", "train_accuracy"]:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(lambda x: f"{x:.4f}")
    for col in ["test_loss", "train_loss"]:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(lambda x: f"{x:.4f}")
    for col in ["alpha", "final_alpha"]:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}")
    
    # Display as table
    st.dataframe(
        display_df,
        column_config={
            "rank": st.column_config.NumberColumn("Rank", help="Position in the leaderboard"),
            "unit": st.column_config.TextColumn("Unit", help="paGating unit"),
            "alpha": st.column_config.TextColumn("α", help="Initial alpha value"),
            "learnable": st.column_config.CheckboxColumn("Learnable", help="Whether alpha is learnable"),
            "final_alpha": st.column_config.TextColumn("Final α", help="Final alpha value (after training)"),
            "test_accuracy": st.column_config.TextColumn("Test Acc", help="Test accuracy"),
            "test_loss": st.column_config.TextColumn("Test Loss", help="Test loss"),
            "train_accuracy": st.column_config.TextColumn("Train Acc", help="Training accuracy"),
            "train_loss": st.column_config.TextColumn("Train Loss", help="Training loss"),
            "epochs": st.column_config.NumberColumn("Epochs", help="Number of training epochs"),
        },
        hide_index=True,
        use_container_width=True,
    )


def plot_best_configurations(best_configs):
    """Display cards for the best configurations."""
    st.header("🌟 Best Configurations")
    
    # Display global best
    global_best = best_configs["global_best"]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Overall Best")
        st.metric(
            label=f"{global_best['unit']} (α={global_best['alpha']:.2f})", 
            value=f"{global_best['test_accuracy']:.4f}",
            help="Test accuracy of the best overall configuration"
        )
        st.caption(f"{'Learnable' if global_best['learnable'] else 'Fixed'} alpha")
        if global_best['learnable']:
            st.caption(f"Final α = {global_best['final_alpha']:.2f}")
    
    # Display best static if available
    if "static" in best_configs:
        with col2:
            static_best = best_configs["static"]["overall"]
            st.subheader("Best Fixed Alpha")
            st.metric(
                label=f"{static_best['unit']} (α={static_best['alpha']:.2f})", 
                value=f"{static_best['test_accuracy']:.4f}",
                help="Test accuracy of the best configuration with fixed alpha"
            )
    
    # Display best learnable if available
    if "learnable" in best_configs:
        with col3:
            learnable_best = best_configs["learnable"]["overall"]
            st.subheader("Best Learnable Alpha")
            st.metric(
                label=f"{learnable_best['unit']} (α={learnable_best['alpha']:.2f})", 
                value=f"{learnable_best['test_accuracy']:.4f}",
                help="Test accuracy of the best configuration with learnable alpha"
            )
            st.caption(f"Final α = {learnable_best['final_alpha']:.2f}")


def plot_unit_comparison(results_df):
    """Plot interactive comparison of different units."""
    st.header("📊 Unit Performance Comparison")
    
    # Filter controls
    col1, col2 = st.columns(2)
    with col1:
        selected_units = st.multiselect(
            "Select units to compare:",
            options=sorted(results_df["unit"].unique()),
            default=sorted(results_df["unit"].unique())
        )
    
    with col2:
        show_learnable = st.checkbox("Include learnable alpha", value=True)
    
    if not selected_units:
        st.warning("Please select at least one unit to display.")
        return
    
    # Filter data
    filtered_df = results_df[results_df["unit"].isin(selected_units)]
    if not show_learnable:
        filtered_df = filtered_df[~filtered_df["learnable"]]
    
    # Get best config for each unit
    unit_best = []
    for unit in selected_units:
        unit_data = filtered_df[filtered_df["unit"] == unit]
        if not unit_data.empty:
            best_idx = unit_data["test_accuracy"].idxmax()
            unit_best.append(unit_data.loc[best_idx])
    
    best_df = pd.DataFrame(unit_best)
    if not best_df.empty:
        best_df = best_df.sort_values("test_accuracy", ascending=False)
    
    # Bar chart of best performances
    if not best_df.empty:
        fig = px.bar(
            best_df,
            x="unit",
            y="test_accuracy",
            color="unit",
            labels={"test_accuracy": "Test Accuracy", "unit": "Unit"},
            title="Best Test Accuracy by Unit",
            text_auto='.4f',
            height=500,
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Alpha performance curves
    st.subheader("Alpha Performance Curves")
    st.caption("How test accuracy varies with different alpha values for each unit")
    
    # Only plot for non-learnable alpha
    static_df = filtered_df[~filtered_df["learnable"]]
    
    # Create plot
    fig = px.line(
        static_df,
        x="alpha",
        y="test_accuracy",
        color="unit",
        markers=True,
        labels={"test_accuracy": "Test Accuracy", "alpha": "Alpha Value", "unit": "Unit"},
        title="Test Accuracy vs Alpha Value",
        height=500,
    )
    
    # Add best points
    for unit in selected_units:
        unit_data = static_df[static_df["unit"] == unit]
        if not unit_data.empty:
            best_idx = unit_data["test_accuracy"].idxmax()
            best_row = unit_data.loc[best_idx]
            
            fig.add_trace(
                go.Scatter(
                    x=[best_row["alpha"]],
                    y=[best_row["test_accuracy"]],
                    mode="markers",
                    marker=dict(size=12, symbol="star", line=dict(width=2, color="black")),
                    name=f"{unit} Best",
                    showlegend=False,
                )
            )
    
    st.plotly_chart(fig, use_container_width=True)


def plot_learnable_analysis(results_df, trends):
    """Plot analysis of learnable alpha behavior."""
    st.header("🔄 Learnable Alpha Analysis")
    
    # Skip if no learnable configs
    learnable_df = results_df[results_df["learnable"]]
    if learnable_df.empty:
        st.info("No learnable alpha configurations found in the results.")
        return
    
    # Advantage of learnable alpha
    if trends.get("learnable_advantage"):
        st.subheader("Learnable Alpha Advantage")
        
        advantage_data = []
        for unit, advantage in trends["learnable_advantage"].items():
            advantage_data.append({"unit": unit, "advantage": advantage})
        
        advantage_df = pd.DataFrame(advantage_data)
        advantage_df = advantage_df.sort_values("advantage", ascending=False)
        
        fig = px.bar(
            advantage_df,
            x="unit",
            y="advantage",
            color="advantage",
            color_continuous_scale="RdBu",
            labels={"advantage": "Test Accuracy Difference", "unit": "Unit"},
            title="Learnable Alpha Advantage (Positive = Learnable Better)",
            height=500,
        )
        fig.update_layout(xaxis_tickangle=-45)
        fig.update_coloraxes(colorbar_title="Advantage")
        st.plotly_chart(fig, use_container_width=True)
    
    # Plot alpha change during training
    st.subheader("Alpha Evolution During Training")
    
    # Let user select a unit
    units_with_learnable = sorted(learnable_df["unit"].unique())
    if not units_with_learnable:
        st.info("No units with learnable alpha found.")
        return
    
    selected_unit = st.selectbox(
        "Select unit to view alpha evolution:",
        options=units_with_learnable
    )
    
    # Get configurations for this unit
    unit_configs = learnable_df[learnable_df["unit"] == selected_unit]
    
    if unit_configs.empty:
        st.info(f"No learnable alpha configurations found for {selected_unit}.")
        return
    
    # Let user select a specific config
    config_options = [f"α={row['alpha']:.2f} (final={row['final_alpha']:.2f})" 
                     for _, row in unit_configs.iterrows()]
    
    if not config_options:
        st.info(f"No configurations available for {selected_unit}.")
        return
    
    selected_config_idx = st.selectbox(
        "Select configuration:",
        options=range(len(config_options)),
        format_func=lambda x: config_options[x]
    )
    
    # Get the selected configuration
    selected_config = unit_configs.iloc[selected_config_idx]
    
    # Load the full CSV data
    try:
        csv_path = selected_config["file_path"]
        if os.path.exists(csv_path):
            full_data = pd.read_csv(csv_path)
            
            if "alpha" in full_data.columns:
                # Plot alpha evolution
                fig = px.line(
                    full_data,
                    x="epoch",
                    y="alpha",
                    markers=True,
                    labels={"alpha": "Alpha Value", "epoch": "Epoch"},
                    title=f"{selected_unit} Alpha Evolution (init={selected_config['alpha']:.2f})",
                    height=400,
                )
                
                # Add horizontal line at initial alpha
                fig.add_hline(
                    y=selected_config["alpha"],
                    line_dash="dash",
                    line_color="gray",
                    annotation_text="Initial α",
                    annotation_position="bottom right"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Plot alpha vs accuracy
                if "val_acc" in full_data.columns or "test_accuracy" in full_data.columns:
                    acc_col = "val_acc" if "val_acc" in full_data.columns else "test_accuracy"
                    
                    fig = px.scatter(
                        full_data,
                        x="alpha",
                        y=acc_col,
                        color="epoch",
                        labels={"alpha": "Alpha Value", acc_col: "Test Accuracy", "epoch": "Epoch"},
                        title=f"{selected_unit} Alpha vs Test Accuracy",
                        height=400,
                    )
                    
                    # Add arrow showing direction of training
                    fig.add_annotation(
                        x=full_data["alpha"].iloc[0],
                        y=full_data[acc_col].iloc[0],
                        ax=full_data["alpha"].iloc[-1],
                        ay=full_data[acc_col].iloc[-1],
                        xref="x", yref="y",
                        axref="x", ayref="y",
                        showarrow=True,
                        arrowhead=2,
                        arrowsize=1,
                        arrowwidth=2,
                        arrowcolor="black"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No alpha evolution data found in the log file.")
        else:
            st.error(f"Log file not found: {csv_path}")
    except Exception as e:
        st.error(f"Error loading alpha evolution data: {str(e)}")


def plot_insights(trends, best_configs):
    """Display insights and recommendations."""
    st.header("💡 Insights & Recommendations")
    
    # Best alpha values
    if trends.get("best_alphas"):
        st.subheader("Recommended Default Alpha Values")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            alpha_data = []
            for unit, alpha in trends["best_alphas"].items():
                alpha_data.append({"unit": unit, "alpha": alpha})
            
            alpha_df = pd.DataFrame(alpha_data)
            
            st.dataframe(
                alpha_df,
                column_config={
                    "unit": st.column_config.TextColumn("Unit", help="paGating unit"),
                    "alpha": st.column_config.NumberColumn("Recommended α", help="Best alpha value", format="%.2f"),
                },
                hide_index=True,
                use_container_width=True,
            )
        
        with col2:
            fig = px.bar(
                alpha_df,
                x="unit",
                y="alpha",
                color="unit",
                labels={"alpha": "Alpha Value", "unit": "Unit"},
                title="Recommended Alpha Values by Unit",
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
    
    # Stability analysis
    if trends.get("stability"):
        st.subheader("Unit Stability Analysis")
        st.caption("Lower standard deviation means more consistent performance across configurations")
        
        stability_data = []
        for unit, std_dev in trends["stability"].items():
            stability_data.append({"unit": unit, "std_dev": std_dev})
        
        stability_df = pd.DataFrame(stability_data)
        stability_df = stability_df.sort_values("std_dev")
        
        fig = px.bar(
            stability_df,
            x="unit",
            y="std_dev",
            color="std_dev",
            color_continuous_scale="Viridis",
            labels={"std_dev": "Standard Deviation", "unit": "Unit"},
            title="Unit Stability (Standard Deviation of Test Accuracy)",
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Auto-detected trends
    st.subheader("Automatically Detected Trends")
    
    trends_text = []
    
    # Learnable alpha trends
    if trends.get("helps_units"):
        trends_text.append(f"- Learnable alpha improved accuracy for: {', '.join(trends['helps_units'])}")
    
    if trends.get("hurts_units"):
        trends_text.append(f"- Learnable alpha decreased accuracy for: {', '.join(trends['hurts_units'])}")
    
    if trends.get("neutral_units"):
        trends_text.append(f"- Learnable alpha had minimal impact on: {', '.join(trends['neutral_units'])}")
    
    # Most stable units
    if trends.get("stability"):
        most_stable = list(trends["stability"].keys())[:3]
        trends_text.append(f"- Most stable units: {', '.join(most_stable)}")
    
    for trend in trends_text:
        st.markdown(trend)


@st.cache_data
def load_training_history(file_path):
    """Load training history from a CSV file with caching."""
    return pd.read_csv(file_path)


def plot_training_curves(results_df):
    """Plot training curves for selected configurations."""
    st.header("📈 Training History")
    
    # Let user select units
    selected_units = st.multiselect(
        "Select units:",
        options=sorted(results_df["unit"].unique()),
        default=[results_df["unit"].iloc[0]] if not results_df.empty else []
    )
    
    if not selected_units:
        st.info("Please select at least one unit to view training history.")
        return
    
    # Filter by selected units
    filtered_df = results_df[results_df["unit"].isin(selected_units)]
    
    # Let user select configs for each unit
    selected_configs = []
    
    for unit in selected_units:
        unit_configs = filtered_df[filtered_df["unit"] == unit]
        
        if not unit_configs.empty:
            st.subheader(f"{unit} Configurations")
            
            config_options = [
                f"α={row['alpha']:.2f} {'(learnable)' if row['learnable'] else ''}" 
                for _, row in unit_configs.iterrows()
            ]
            
            if not config_options:
                st.info(f"No configurations available for {unit}.")
                continue
            
            selected_indices = st.multiselect(
                f"Select {unit} configurations:",
                options=range(len(config_options)),
                format_func=lambda x: config_options[x],
                default=[0]  # Select first option by default
            )
            
            for idx in selected_indices:
                selected_configs.append(unit_configs.iloc[idx])
    
    if not selected_configs:
        st.info("Please select at least one configuration to view training history.")
        return
    
    # Create tabs for different metrics
    metric_tabs = st.tabs(["Test Accuracy", "Test Loss", "Train Accuracy", "Train Loss"])
    
    # Create figures for each metric
    metrics = ["test_accuracy", "test_loss", "train_accuracy", "train_loss"]
    metric_names = ["Test Accuracy", "Test Loss", "Train Accuracy", "Train Loss"]
    csv_columns = ["val_acc", "val_loss", "train_acc", "train_loss"]
    
    for tab_idx, (metric, name, csv_col) in enumerate(zip(metrics, metric_names, csv_columns)):
        with metric_tabs[tab_idx]:
            fig = go.Figure()
            
            for config in selected_configs:
                try:
                    # Load training history
                    file_path = config["file_path"]
                    if os.path.exists(file_path):
                        history = load_training_history(file_path)
                        
                        if csv_col in history.columns and "epoch" in history.columns:
                            # Create trace name
                            trace_name = f"{config['unit']} α={config['alpha']:.2f}"
                            if config['learnable']:
                                trace_name += " (learnable)"
                            
                            # Add trace to figure
                            fig.add_trace(
                                go.Scatter(
                                    x=history["epoch"],
                                    y=history[csv_col],
                                    mode="lines",
                                    name=trace_name
                                )
                            )
                except Exception as e:
                    st.error(f"Error loading training history: {str(e)}")
            
            fig.update_layout(
                title=f"{name} vs Epoch",
                xaxis_title="Epoch",
                yaxis_title=name,
                height=500,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig, use_container_width=True)


def main():
    """Main function to run the Streamlit app."""
    # Parse command line args when run directly
    if len(sys.argv) > 1:
        args = parse_args()
        results_dir = args.results_dir
        min_epochs = args.min_epochs
    else:
        # Use streamlit sidebar for config when run through streamlit
        st.sidebar.title("Configuration")
        
        # Allow user to select results directory
        results_dir = st.sidebar.text_input(
            "Results Directory:",
            value="results/latest",
            help="Path to directory containing CSV logs from sweep"
        )
        
        min_epochs = st.sidebar.slider(
            "Minimum Epochs:",
            min_value=1,
            max_value=50,
            value=5,
            help="Minimum number of epochs for a run to be considered"
        )
    
    # Setup page
    setup_page()
    
    # Display info about results directory
    st.sidebar.info(f"Analyzing results from: {results_dir}")
    
    # Check if directory exists
    if not os.path.exists(results_dir):
        st.error(f"Results directory not found: {results_dir}")
        st.stop()
    
    # Load data
    results_df, best_configs, trends = load_data(results_dir, min_epochs)
    
    # Create tabs for different views
    tabs = st.tabs([
        "Overview", 
        "Unit Comparison", 
        "Learnable Alpha", 
        "Training Curves", 
        "Insights"
    ])
    
    # Overview tab
    with tabs[0]:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            plot_best_configurations(best_configs)
        
        with col2:
            st.header("📊 Dataset Stats")
            st.metric("Total Configurations", len(results_df))
            st.metric("Units", len(results_df["unit"].unique()))
            st.metric("Alpha Values", len(results_df["alpha"].unique()))
            
            learnable_count = len(results_df[results_df["learnable"]])
            fixed_count = len(results_df[~results_df["learnable"]])
            
            st.metric("Learnable Alpha Configs", learnable_count)
            st.metric("Fixed Alpha Configs", fixed_count)
        
        plot_leaderboard(results_df)
    
    # Unit comparison tab
    with tabs[1]:
        plot_unit_comparison(results_df)
    
    # Learnable alpha tab
    with tabs[2]:
        plot_learnable_analysis(results_df, trends)
    
    # Training curves tab
    with tabs[3]:
        plot_training_curves(results_df)
    
    # Insights tab
    with tabs[4]:
        plot_insights(trends, best_configs)
    
    # Add footer
    st.sidebar.markdown("---")
    st.sidebar.caption("paGating Dashboard v1.0")
    st.sidebar.caption(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main() 