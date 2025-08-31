#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
paGating Command Line Interface (CLI)

A unified command-line interface to run paGating experiments, analysis, and reporting.

Usage:
    python scripts/pagate.py eval-all --results_dir results/run_20230101_120000/logs
    python scripts/pagate.py analyze --results_dir results/run_20230101_120000/logs
    python scripts/pagate.py report --results_dir results/run_20230101_120000/logs
    python scripts/pagate.py dashboard --results_dir results/run_20230101_120000/logs

Examples:
    # Run comprehensive evaluation of all results (analysis, report, dashboard)
    python scripts/pagate.py eval-all --results_dir results/latest/logs

    # Run just the analysis to generate insights_summary.md
    python scripts/pagate.py analyze --results_dir results/latest/logs --output_dir analysis

    # Generate an HTML report with visualizations
    python scripts/pagate.py report --results_dir results/latest/logs --output_file report.html

    # Launch the interactive dashboard
    python scripts/pagate.py dashboard --results_dir results/latest/logs

Commands:
    eval-all    Run complete evaluation (analysis, report, dashboard)
    analyze     Run just the analysis to generate insights_summary.md
    report      Generate an HTML report with visualizations
    dashboard   Launch the interactive Streamlit dashboard
"""

import os
import sys
import glob
import argparse
import subprocess
import webbrowser
from pathlib import Path
from datetime import datetime


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="paGating CLI for experiment evaluation and analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Common arguments for all commands
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument(
        "--results_dir", 
        type=str, 
        required=True,
        help="Directory containing CSV logs from sweep"
    )
    common_parser.add_argument(
        "--min_epochs", 
        type=int, 
        default=5,
        help="Minimum number of epochs for a run to be considered"
    )
    
    # eval-all command (run everything)
    eval_all_parser = subparsers.add_parser(
        "eval-all", 
        parents=[common_parser],
        help="Run complete evaluation (analysis, report, dashboard)"
    )
    eval_all_parser.add_argument(
        "--output_dir", 
        type=str, 
        default="evaluation",
        help="Directory to save all outputs"
    )
    eval_all_parser.add_argument(
        "--no_dashboard", 
        action="store_true",
        help="Skip launching the dashboard"
    )
    eval_all_parser.add_argument(
        "--no_browser", 
        action="store_true",
        help="Don't open browser for HTML report and dashboard"
    )
    
    # analyze command
    analyze_parser = subparsers.add_parser(
        "analyze", 
        parents=[common_parser],
        help="Run analysis to generate insights_summary.md"
    )
    analyze_parser.add_argument(
        "--output_dir", 
        type=str, 
        default="analysis",
        help="Directory to save analysis outputs"
    )
    analyze_parser.add_argument(
        "--export_pdf", 
        action="store_true",
        help="Export Markdown summary as PDF"
    )
    
    # report command
    report_parser = subparsers.add_parser(
        "report", 
        parents=[common_parser],
        help="Generate HTML report with visualizations"
    )
    report_parser.add_argument(
        "--output_file", 
        type=str, 
        default="pagating_report.html",
        help="Output HTML file path"
    )
    report_parser.add_argument(
        "--open_browser", 
        action="store_true",
        help="Open the HTML report in browser after generation"
    )
    
    # dashboard command
    dashboard_parser = subparsers.add_parser(
        "dashboard", 
        parents=[common_parser],
        help="Launch interactive Streamlit dashboard"
    )
    dashboard_parser.add_argument(
        "--port", 
        type=int, 
        default=8501,
        help="Port to run the Streamlit dashboard on"
    )
    
    return parser.parse_args()


def run_command(cmd, capture_output=False):
    """Run a shell command and handle errors."""
    try:
        result = subprocess.run(
            cmd, 
            check=True, 
            capture_output=capture_output,
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(cmd)}")
        print(f"Error message: {e}")
        if e.stdout:
            print(f"Standard output:\n{e.stdout}")
        if e.stderr:
            print(f"Standard error:\n{e.stderr}")
        sys.exit(1)


def find_script_path(script_name):
    """Find the absolute path to a script."""
    # Try direct path first
    direct_path = os.path.join("scripts", script_name)
    if os.path.exists(direct_path):
        return os.path.abspath(direct_path)
    
    # Try parent directory
    parent_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts", script_name)
    if os.path.exists(parent_path):
        return os.path.abspath(parent_path)
    
    # Try current working directory
    cwd_path = os.path.join(os.getcwd(), "scripts", script_name)
    if os.path.exists(cwd_path):
        return os.path.abspath(cwd_path)
    
    # As a last resort, just return the script name and let subprocess handle it
    return script_name


def run_analysis(args):
    """Run the analysis script."""
    print("\n" + "=" * 80)
    print("RUNNING ANALYSIS")
    print("=" * 80)
    
    cmd = [
        sys.executable,
        find_script_path("analyze_results.py"),
        "--results_dir", args.results_dir,
        "--output_dir", args.output_dir,
        "--min_epochs", str(args.min_epochs)
    ]
    
    if hasattr(args, "export_pdf") and args.export_pdf:
        cmd.append("--export_pdf")
    
    print(f"Running: {' '.join(cmd)}")
    run_command(cmd)
    
    output_path = os.path.join(args.output_dir, "insights_summary.md")
    print(f"\nAnalysis completed. Results saved to: {output_path}")
    
    return output_path


def generate_report(args):
    """Generate HTML report."""
    print("\n" + "=" * 80)
    print("GENERATING HTML REPORT")
    print("=" * 80)
    
    # Determine output file path
    if hasattr(args, "output_dir") and not hasattr(args, "output_file"):
        # For eval-all command, use the output_dir
        os.makedirs(args.output_dir, exist_ok=True)
        output_file = os.path.join(args.output_dir, "pagating_report.html")
    else:
        # For report command, use the provided output_file
        output_file = args.output_file
    
    cmd = [
        sys.executable,
        find_script_path("generate_html_report.py"),
        "--results_dir", args.results_dir,
        "--output_file", output_file,
        "--min_epochs", str(args.min_epochs)
    ]
    
    print(f"Running: {' '.join(cmd)}")
    run_command(cmd)
    
    print(f"\nHTML report generated: {output_file}")
    
    # Open report in browser if requested
    if (hasattr(args, "open_browser") and args.open_browser) or \
       (hasattr(args, "command") and args.command == "eval-all" and not args.no_browser):
        print("Opening report in browser...")
        webbrowser.open(f"file://{os.path.abspath(output_file)}")
    
    return output_file


def launch_dashboard(args):
    """Launch the Streamlit dashboard."""
    print("\n" + "=" * 80)
    print("LAUNCHING INTERACTIVE DASHBOARD")
    print("=" * 80)
    
    port = getattr(args, "port", 8501)
    
    cmd = [
        "streamlit", "run", 
        find_script_path("analyze_dashboard.py"),
        "--",
        "--results_dir", args.results_dir,
        "--min_epochs", str(args.min_epochs)
    ]
    
    print(f"Running: {' '.join(cmd)}")
    print("\nDashboard is starting. Press Ctrl+C to stop.\n")
    
    # Open browser if requested
    if hasattr(args, "command") and args.command == "eval-all" and not args.no_browser:
        # Give the dashboard a moment to start
        import time
        time.sleep(2)
        webbrowser.open(f"http://localhost:{port}")
    
    # Run streamlit (this will block until the user stops it)
    run_command(cmd)


def check_dependencies():
    """Check if all required dependencies are installed."""
    missing_deps = []
    
    # Check for streamlit
    try:
        import streamlit
    except ImportError:
        missing_deps.append("streamlit")
    
    # Check for matplotlib and seaborn
    try:
        import matplotlib
        import seaborn
    except ImportError:
        missing_deps.append("matplotlib and/or seaborn")
    
    # Check for pandas and numpy
    try:
        import pandas
        import numpy
    except ImportError:
        missing_deps.append("pandas and/or numpy")
    
    # Check for plotly
    try:
        import plotly
    except ImportError:
        missing_deps.append("plotly")
    
    if missing_deps:
        print("\nWARNING: The following dependencies are missing:")
        for dep in missing_deps:
            print(f"  - {dep}")
        
        print("\nTo install all dependencies, run:")
        print("  pip install streamlit pandas numpy matplotlib seaborn plotly weasyprint")
        
        # Continue anyway, individual scripts will fail if they need a missing dependency
        print("\nContinuing anyway...\n")


def main():
    """Main function to parse arguments and run the appropriate command."""
    args = parse_args()
    
    if not args.command:
        print("Error: No command specified.")
        print("Use one of: eval-all, analyze, report, dashboard")
        print("For help, run: python scripts/pagate.py --help")
        sys.exit(1)
    
    # Check if the results directory exists and contains CSV files
    if not os.path.isdir(args.results_dir):
        print(f"Error: Results directory not found: {args.results_dir}")
        sys.exit(1)
    
    csv_files = glob.glob(os.path.join(args.results_dir, "*.csv"))
    if not csv_files:
        print(f"Error: No CSV files found in: {args.results_dir}")
        sys.exit(1)
    
    # Check dependencies before running
    check_dependencies()
    
    # Process commands
    if args.command == "analyze":
        run_analysis(args)
    
    elif args.command == "report":
        generate_report(args)
    
    elif args.command == "dashboard":
        launch_dashboard(args)
    
    elif args.command == "eval-all":
        # Create output directory
        os.makedirs(args.output_dir, exist_ok=True)
        
        # Run all steps
        run_analysis(args)
        generate_report(args)
        
        if not args.no_dashboard:
            launch_dashboard(args)
    
    print("\nAll requested operations completed successfully.")


if __name__ == "__main__":
    main() 