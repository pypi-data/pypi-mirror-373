# paGating Analysis & Visualization Tools

This README provides instructions on how to explore paGating experiment results interactively and share them with others.

## 🚀 Running a Complete Experiment Pipeline

The paGating framework includes a comprehensive experiment pipeline that now supports interactive visualization and reporting.

```bash
# Run a full experiment with transformer benchmarks and export tools
python scripts/run_experiment_pipeline.py --include_transformer --export_all
```

This will:
1. Run hyperparameter sweep
2. Generate leaderboard
3. Create visualizations
4. Run transformer benchmarks
5. Generate PDF report
6. Create summary.json
7. Package results into a ZIP archive
8. Launch the interactive dashboard

## 📊 Interactive Dashboard

The interactive dashboard provides a visual way to explore experiment results.

### Launch the Dashboard:

```bash
# Launch the dashboard for a specific experiment
streamlit run dashboard.py -- --experiment results/your_experiment_name
```

### Dashboard Features:

- **Transformer Results**: View and filter benchmark results
- **Alpha Analysis**: Interactive heatmaps and performance curves
- **Unit Comparison**: Compare units across different metrics
- **Documentation**: View Markdown documentation
- **Plots**: Browse all generated plots

## 📑 Generating PDF Reports

The PDF report generator creates a professional document summarizing your experiment results.

```bash
# Generate a PDF report for a specific experiment
python export_report.py --experiment_dir results/your_experiment_name
```

The generated PDF includes:
- Executive summary with key findings
- Experiment configuration details
- Performance leaderboards
- Alpha parameter analysis
- Detailed unit-by-unit analysis
- Visualizations and plots
- Conclusions

## 📦 Sharing Results

To share results with colleagues or for documentation:

```bash
# Generate a consolidated export (JSON summary and ZIP archive)
python export_summary.py --experiment_dir results/your_experiment_name
```

This creates:
- **summary.json**: Machine-readable summary of key metrics (best unit, alpha ranges, test accuracy stats)
- **results.zip**: Zipped archive of CSVs, Markdown reports, and visualizations

## 📂 Understanding the Output Structure

After running a full experiment with `--export_all`, the results directory will have this structure:

```
results/your_experiment_name/
├── leaderboard/
│   ├── leaderboard.md
│   └── transformer_leaderboard.md
├── logs/
│   └── (experiment logs)
├── plots/
│   └── (visualization plots)
├── transformer/
│   ├── logs/
│   ├── plots/ 
│   └── transformer_results.csv
├── report.pdf
├── results.zip
├── results_summary.md
└── summary.json
```

## 🔍 Using the Results for Research or Development

### For Research:
- The PDF report provides a comprehensive summary suitable for inclusion in research notes
- The JSON summary provides structured data for quick reference
- The ZIP archive contains all raw data for reproducibility

### For Development:
- The dashboard allows interactive exploration to identify optimal configurations
- The transformer leaderboard helps identify the best unit and alpha value for your use case
- The alpha analysis section shows how different alpha values affect each unit

## 🧩 Extending the Tools

### Adding New Visualizations to the Dashboard:
1. Edit `dashboard.py`
2. Add new visualization function in the appropriate section
3. Update the UI to include your new visualization

### Customizing the PDF Report:
1. Edit `export_report.py`
2. Modify the HTML template in `create_html_template()` function
3. Update the CSS in `get_css()` function
4. Add new data extraction functions as needed

## 🆘 Troubleshooting

### Dashboard Issues:
- Make sure Streamlit is installed: `pip install streamlit`
- Check that the experiment directory exists and contains results
- Look for errors in the terminal output

### PDF Generation Issues:
- Ensure WeasyPrint dependencies are installed (see [WeasyPrint Documentation](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html))
- Check that the experiment directory contains the necessary markdown files and plots
- Review any error messages in the output

### ZIP/JSON Export Issues:
- Verify the experiment directory path
- Ensure you have write permissions in the output directory
- Check the experiment directory structure

## 📚 Additional Resources

- [paGating Documentation](https://github.com/AaryanG/paGating)
- [Streamlit Documentation](https://docs.streamlit.io)
- [WeasyPrint Documentation](https://doc.courtbouillon.org/weasyprint) 