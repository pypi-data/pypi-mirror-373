#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
paGating PDF Report Generator

This script generates a comprehensive PDF report from experiment results:
- Merges insights_summary.md, transformer_leaderboard.md
- Includes generated plots
- Creates a clean, professional PDF with WeasyPrint
"""

import os
import sys
import glob
import json
import argparse
import pandas as pd
import markdown
import tempfile
from datetime import datetime
from weasyprint import HTML, CSS
from shutil import copyfile
from jinja2 import Environment, FileSystemLoader


def parse_args():
    parser = argparse.ArgumentParser(description="Generate a PDF report from experiment results")
    
    parser.add_argument("--experiment_dir", type=str, required=True,
                       help="Path to the experiment directory")
    parser.add_argument("--output_file", type=str,
                       help="Output PDF file path (default: experiment_dir/report.pdf)")
    parser.add_argument("--title", type=str, default="paGating Experiment Report",
                       help="Report title")
    parser.add_argument("--author", type=str, default="Aaryan Guglani",
                       help="Report author name")
    
    return parser.parse_args()


def get_css():
    """Get CSS styling for the report."""
    css = """
    @page {
        size: A4;
        margin: 2.5cm 1.5cm;
        @top-center {
            content: "paGating Experiment Report";
            font-family: 'Helvetica', sans-serif;
            font-size: 10pt;
        }
        @bottom-center {
            content: "Page " counter(page) " of " counter(pages);
            font-family: 'Helvetica', sans-serif;
            font-size: 10pt;
        }
    }

    body {
        font-family: 'Helvetica', sans-serif;
        font-size: 11pt;
        line-height: 1.6;
        color: #333;
    }

    .cover {
        height: 100vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        page-break-after: always;
    }

    .cover h1 {
        font-size: 32pt;
        color: #2c3e50;
        margin-bottom: 0.5cm;
    }

    .cover h2 {
        font-size: 20pt;
        color: #7f8c8d;
        margin-bottom: 2cm;
    }

    .cover .author {
        font-size: 14pt;
        margin-bottom: 0.5cm;
    }

    .cover .date {
        font-size: 12pt;
        color: #7f8c8d;
    }

    h1 {
        font-size: 20pt;
        color: #2c3e50;
        margin-top: 1cm;
        margin-bottom: 0.5cm;
        page-break-before: always;
    }

    h2 {
        font-size: 16pt;
        color: #2c3e50;
        margin-top: 0.8cm;
        margin-bottom: 0.3cm;
    }

    h3 {
        font-size: 14pt;
        color: #2c3e50;
        margin-top: 0.6cm;
        margin-bottom: 0.2cm;
    }

    h4 {
        font-size: 12pt;
        color: #2c3e50;
        margin-top: 0.4cm;
        margin-bottom: 0.2cm;
    }

    p {
        margin-bottom: 0.3cm;
    }

    a {
        color: #3498db;
        text-decoration: none;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 1cm;
    }

    table, th, td {
        border: 1pt solid #ddd;
    }

    th {
        background-color: #f2f2f2;
        text-align: left;
        padding: 0.2cm;
        font-weight: bold;
    }

    td {
        padding: 0.2cm;
    }

    tr:nth-child(even) {
        background-color: #f9f9f9;
    }

    .section {
        margin-bottom: 1cm;
    }

    .plot-container {
        width: 100%;
        text-align: center;
        margin: 1cm 0;
        page-break-inside: avoid;
    }

    .plot-container img {
        max-width: 90%;
        height: auto;
    }

    .plot-caption {
        font-size: 10pt;
        color: #7f8c8d;
        margin-top: 0.2cm;
        text-align: center;
    }

    .footer {
        font-size: 10pt;
        color: #7f8c8d;
        text-align: center;
        margin-top: 1cm;
    }

    .toc {
        margin-bottom: 1cm;
    }

    .toc a {
        text-decoration: none;
        color: #333;
    }

    .toc-item {
        margin-bottom: 0.2cm;
    }

    .toc-section {
        font-weight: bold;
    }

    .toc-subsection {
        margin-left: 0.5cm;
    }

    .metadata {
        background-color: #f9f9f9;
        padding: 0.5cm;
        margin-bottom: 1cm;
        border-left: 4pt solid #3498db;
    }

    .highlight {
        background-color: #fff9e6;
        padding: 0.3cm;
        border-left: 4pt solid #f1c40f;
        margin-bottom: 0.5cm;
    }

    code {
        font-family: monospace;
        background-color: #f5f5f5;
        padding: 0.1cm 0.2cm;
        border-radius: 3pt;
        font-size: 10pt;
    }

    pre {
        background-color: #f5f5f5;
        padding: 0.3cm;
        border-radius: 3pt;
        overflow-x: auto;
        font-size: 10pt;
        line-height: 1.4;
        margin-bottom: 0.5cm;
    }
    """
    return css


def create_html_template():
    """Create the HTML template for the report."""
    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{{ title }}</title>
    </head>
    <body>
        <!-- Cover Page -->
        <div class="cover">
            <h1>{{ title }}</h1>
            <h2>Experiment: {{ experiment_name }}</h2>
            <div class="author">{{ author }}</div>
            <div class="date">{{ date }}</div>
        </div>

        <!-- Table of Contents -->
        <h1>Table of Contents</h1>
        <div class="toc">
            <div class="toc-item toc-section">1. Executive Summary</div>
            <div class="toc-item toc-section">2. Experiment Configuration</div>
            <div class="toc-item toc-section">3. Transformer Benchmark Results</div>
            <div class="toc-item toc-subsection">3.1 Performance Leaderboard</div>
            <div class="toc-item toc-subsection">3.2 Alpha Parameter Analysis</div>
            <div class="toc-item toc-section">4. Detailed Unit Analysis</div>
            {% for unit in units %}
            <div class="toc-item toc-subsection">4.{{ loop.index }} {{ unit }}</div>
            {% endfor %}
            <div class="toc-item toc-section">5. Visualizations</div>
            <div class="toc-item toc-section">6. Conclusions</div>
        </div>

        <!-- Executive Summary -->
        <h1>1. Executive Summary</h1>
        <div class="section">
            <p>
                This report presents the results of performance evaluation experiments for paGating units,
                with a focus on transformer model benchmarks. The experiments compare different activation
                units and alpha parameter settings to determine optimal configurations.
            </p>
            
            {% if best_unit %}
            <div class="highlight">
                <p>
                    <strong>Key Finding:</strong> The best performing unit was 
                    <strong>{{ best_unit.unit }}</strong> with α={{ best_unit.alpha }}, 
                    achieving a test accuracy of {{ best_unit.test_acc }}%.
                </p>
            </div>
            {% endif %}
            
            <p>The analysis covers performance benchmarks, stability across different alpha values, 
            and detailed comparisons between units.</p>
        </div>

        <!-- Experiment Configuration -->
        <h1>2. Experiment Configuration</h1>
        <div class="section">
            <div class="metadata">
                <p><strong>Experiment Name:</strong> {{ experiment_name }}</p>
                <p><strong>Date:</strong> {{ date }}</p>
                <p><strong>Units Tested:</strong> {{ ", ".join(units) }}</p>
                <p><strong>Alpha Values:</strong> {{ alpha_values }}</p>
                {% if transformer_config %}
                <p><strong>Transformer Configuration:</strong></p>
                <ul>
                    {% for key, value in transformer_config.items() %}
                    <li>{{ key }}: {{ value }}</li>
                    {% endfor %}
                </ul>
                {% endif %}
            </div>
        </div>

        <!-- Transformer Benchmark Results -->
        <h1>3. Transformer Benchmark Results</h1>
        
        <h2>3.1 Performance Leaderboard</h2>
        <div class="section">
            {{ transformer_leaderboard_html }}
        </div>
        
        <h2>3.2 Alpha Parameter Analysis</h2>
        <div class="section">
            <p>
                The alpha parameter controls the gating strength in paGating units,
                with α=0 being equivalent to a simple linear layer and α=1 being a full
                gating unit. The following analysis shows the impact of different alpha values
                on each unit's performance.
            </p>
            
            {% for plot in alpha_plots %}
            <div class="plot-container">
                <img src="{{ plot }}" alt="Alpha Analysis Plot">
                <div class="plot-caption">Figure: Impact of alpha values on unit performance</div>
            </div>
            {% endfor %}
        </div>

        <!-- Detailed Unit Analysis -->
        <h1>4. Detailed Unit Analysis</h1>
        
        {% for unit in units %}
        <h2>4.{{ loop.index }} {{ unit }}</h2>
        <div class="section">
            {{ unit_details[unit] }}
            
            {% for plot in unit_plots[unit] %}
            <div class="plot-container">
                <img src="{{ plot }}" alt="{{ unit }} Plot">
                <div class="plot-caption">Figure: Performance visualization for {{ unit }}</div>
            </div>
            {% endfor %}
        </div>
        {% endfor %}

        <!-- Visualizations -->
        <h1>5. Visualizations</h1>
        <div class="section">
            {% for plot in other_plots %}
            <div class="plot-container">
                <img src="{{ plot }}" alt="Experiment Plot">
                <div class="plot-caption">Figure: {{ plot|basename }}</div>
            </div>
            {% endfor %}
        </div>

        <!-- Conclusions -->
        <h1>6. Conclusions</h1>
        <div class="section">
            {{ conclusions_html }}
        </div>

        <!-- Footer -->
        <div class="footer">
            paGating Framework Report | Generated on {{ date }}
        </div>
    </body>
    </html>
    """
    return template


def get_transformer_config(experiment_dir):
    """Extract transformer configuration from the leaderboard markdown."""
    leaderboard_path = os.path.join(experiment_dir, "leaderboard", "transformer_leaderboard.md")
    if not os.path.exists(leaderboard_path):
        return {}
    
    config = {}
    with open(leaderboard_path, 'r') as f:
        content = f.read()
    
    # Look for the configuration section
    config_section = content.split("## Configuration")[-1].split("##")[0].strip()
    
    for line in config_section.split("\n"):
        line = line.strip()
        if line.startswith("- "):
            parts = line[2:].split(": ", 1)
            if len(parts) == 2:
                key, value = parts
                config[key] = value
    
    return config


def extract_unit_details(summary_text, unit_name):
    """Extract details about a specific unit from the summary text."""
    if summary_text is None:
        return ""
    
    # Look for sections about the specified unit
    unit_section_start = summary_text.find(f"## About the {unit_name}")
    
    if unit_section_start == -1:
        # Try searching for unit in other contexts
        unit_section_start = summary_text.find(f"## {unit_name}")
    
    if unit_section_start == -1:
        # Try another format
        unit_section_start = summary_text.find(unit_name)
        if unit_section_start == -1:
            return ""
    
    # Find the next heading or end of text
    next_heading = summary_text.find("\n## ", unit_section_start + 1)
    if next_heading == -1:
        unit_section = summary_text[unit_section_start:]
    else:
        unit_section = summary_text[unit_section_start:next_heading]
    
    return unit_section


def extract_conclusions(summary_text):
    """Extract conclusions from the summary markdown."""
    if summary_text is None:
        return ""
    
    # Look for conclusions section
    conclusions_start = summary_text.find("## Conclusions")
    
    if conclusions_start == -1:
        return ""
    
    # Find the next heading or end of text
    next_heading = summary_text.find("\n## ", conclusions_start + 1)
    if next_heading == -1:
        conclusions = summary_text[conclusions_start:]
    else:
        conclusions = summary_text[conclusions_start:next_heading]
    
    return conclusions


def find_best_unit(experiment_dir):
    """Find the best performing unit from transformer results."""
    csv_path = os.path.join(experiment_dir, "transformer", "transformer_results.csv")
    if not os.path.exists(csv_path):
        return None
    
    df = pd.read_csv(csv_path)
    if df.empty:
        return None
    
    best_idx = df['Test Accuracy'].idxmax()
    best_row = df.loc[best_idx]
    
    return {
        'unit': best_row['Unit'],
        'alpha': best_row['Alpha'],
        'test_acc': best_row['Test Accuracy']
    }


def find_unit_plots(experiment_dir, unit_name):
    """Find plots related to a specific unit."""
    plots = []
    
    # Search in the transformer plots directory
    transformer_plots_dir = os.path.join(experiment_dir, "transformer", "plots")
    if os.path.exists(transformer_plots_dir):
        unit_plots = glob.glob(os.path.join(transformer_plots_dir, f"{unit_name}*.png"))
        plots.extend(unit_plots)
    
    # Search in the main plots directory
    main_plots_dir = os.path.join(experiment_dir, "plots")
    if os.path.exists(main_plots_dir):
        unit_plots = glob.glob(os.path.join(main_plots_dir, f"{unit_name}*.png"))
        plots.extend(unit_plots)
    
    # Also look in the root experiment directory
    root_plots = glob.glob(os.path.join(experiment_dir, f"{unit_name}*.png"))
    plots.extend(root_plots)
    
    return plots


def find_alpha_plots(experiment_dir):
    """Find plots related to alpha analysis."""
    plots = []
    
    # Look for alpha-related plots
    patterns = ["*alpha*.png", "*Alpha*.png"]
    
    for pattern in patterns:
        # Search in the main plots directory
        main_plots_dir = os.path.join(experiment_dir, "plots")
        if os.path.exists(main_plots_dir):
            alpha_plots = glob.glob(os.path.join(main_plots_dir, pattern))
            plots.extend(alpha_plots)
        
        # Also look in the root experiment directory
        root_plots = glob.glob(os.path.join(experiment_dir, pattern))
        plots.extend(root_plots)
    
    return plots


def find_units_and_alphas(experiment_dir):
    """Find all units and alpha values from the transformer results."""
    csv_path = os.path.join(experiment_dir, "transformer", "transformer_results.csv")
    if not os.path.exists(csv_path):
        return [], ""
    
    df = pd.read_csv(csv_path)
    if df.empty:
        return [], ""
    
    units = df['Unit'].unique().tolist()
    alphas = ", ".join(map(str, sorted(df['Alpha'].unique().tolist())))
    
    return units, alphas


def main():
    args = parse_args()
    
    # Process experiment directory
    experiment_dir = args.experiment_dir
    if not os.path.exists(experiment_dir):
        print(f"Error: Experiment directory '{experiment_dir}' does not exist")
        sys.exit(1)
    
    experiment_name = os.path.basename(experiment_dir)
    
    # Set output file path if not provided
    if not args.output_file:
        args.output_file = os.path.join(experiment_dir, "report.pdf")
    
    # Load the markdown files
    summary_path = os.path.join(experiment_dir, "results_summary.md")
    leaderboard_path = os.path.join(experiment_dir, "leaderboard", "transformer_leaderboard.md")
    
    summary_text = ""
    if os.path.exists(summary_path):
        with open(summary_path, 'r') as f:
            summary_text = f.read()
    
    leaderboard_text = ""
    if os.path.exists(leaderboard_path):
        with open(leaderboard_path, 'r') as f:
            leaderboard_text = f.read()
    
    # Convert markdown to HTML
    leaderboard_html = markdown.markdown(leaderboard_text, extensions=['tables'])
    
    # Extract conclusions
    conclusions_text = extract_conclusions(summary_text)
    conclusions_html = markdown.markdown(conclusions_text)
    
    # Get transformer configuration
    transformer_config = get_transformer_config(experiment_dir)
    
    # Find units and alpha values
    units, alpha_values = find_units_and_alphas(experiment_dir)
    
    # Find the best performing unit
    best_unit = find_best_unit(experiment_dir)
    
    # Find plots for each unit
    unit_plots = {}
    for unit in units:
        unit_plots[unit] = find_unit_plots(experiment_dir, unit)
    
    # Find alpha analysis plots
    alpha_plots = find_alpha_plots(experiment_dir)
    
    # Collect all other plots that aren't specifically for a unit or alpha analysis
    all_plots = glob.glob(os.path.join(experiment_dir, "plots", "*.png"))
    all_plots.extend(glob.glob(os.path.join(experiment_dir, "transformer", "plots", "*.png")))
    
    # Filter out unit-specific and alpha-specific plots
    used_plots = []
    for plots in unit_plots.values():
        used_plots.extend(plots)
    used_plots.extend(alpha_plots)
    
    other_plots = [p for p in all_plots if p not in used_plots]
    
    # Extract unit-specific details from the summary
    unit_details = {}
    for unit in units:
        unit_section = extract_unit_details(summary_text, unit)
        unit_details[unit] = markdown.markdown(unit_section)
    
    # Set up the Jinja environment
    env = Environment(loader=FileSystemLoader("."))
    template_str = create_html_template()
    template = env.from_string(template_str)
    
    # Add custom filter for basename
    env.filters['basename'] = lambda path: os.path.basename(path)
    
    # Render the template
    html = template.render(
        title=args.title,
        experiment_name=experiment_name,
        author=args.author,
        date=datetime.now().strftime("%B %d, %Y"),
        transformer_leaderboard_html=leaderboard_html,
        units=units,
        alpha_values=alpha_values,
        transformer_config=transformer_config,
        best_unit=best_unit,
        unit_plots=unit_plots,
        alpha_plots=alpha_plots,
        other_plots=other_plots,
        unit_details=unit_details,
        conclusions_html=conclusions_html
    )
    
    # Create a temporary directory for the HTML and assets
    with tempfile.TemporaryDirectory() as temp_dir:
        # Write the HTML to a temp file
        html_file = os.path.join(temp_dir, "report.html")
        with open(html_file, "w") as f:
            f.write(html)
        
        # Copy all image files to the temp directory
        all_image_files = []
        for plots in unit_plots.values():
            all_image_files.extend(plots)
        all_image_files.extend(alpha_plots)
        all_image_files.extend(other_plots)
        
        for image_file in all_image_files:
            dest_file = os.path.join(temp_dir, os.path.basename(image_file))
            copyfile(image_file, dest_file)
        
        # Create the CSS file
        css_file = os.path.join(temp_dir, "style.css")
        with open(css_file, "w") as f:
            f.write(get_css())
        
        # Generate the PDF
        print(f"Generating PDF report to {args.output_file}...")
        html = HTML(filename=html_file)
        css = CSS(filename=css_file)
        html.write_pdf(args.output_file, stylesheets=[css])
        
        print(f"PDF report successfully generated: {args.output_file}")


if __name__ == "__main__":
    main() 