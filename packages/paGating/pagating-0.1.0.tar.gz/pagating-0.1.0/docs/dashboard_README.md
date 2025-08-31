# paGating CIFAR-10 Dashboard

This dashboard allows you to visualize and compare the performance of different paGating units on the CIFAR-10 dataset.

## Overview

The dashboard provides the following features:
- Compare multiple paGating units in a single view
- Visualize training and validation metrics (accuracy and loss) over time
- Track learnable alpha parameters during training
- View final performance metrics in table format
- Export comparison results as CSV

## Prerequisites

Make sure you have the following packages installed:

```bash
pip install streamlit pandas numpy plotly
```

## Usage

### Running the Dashboard

To run the dashboard, execute:

```bash
streamlit run dashboard_cifar.py
```

This will start a local Streamlit server, usually at http://localhost:8501.

### Generating Training Metrics

The dashboard requires metrics in a specific format, stored in the `logs/cifar10/{unit_name}/metrics.csv` directory.

There are three ways to generate these metrics:

1. **Training with metrics logging:**
   ```bash
   python train_cifar10.py --unit paMishU --alpha 0.5 --epochs 10 --save_for_dashboard
   ```

2. **Running the comparison script:**
   ```bash
   python compare_units_cifar10.py --epochs 5 --batch_size 64
   ```

3. **Converting existing metrics:**
   ```bash
   python generate_metrics_csv.py
   ```

### Dashboard Features

The dashboard provides the following visualizations:

- **Training and Validation Accuracy**: Line charts showing the accuracy over epochs
- **Training and Validation Loss**: Line charts showing the loss over epochs
- **Learnable Alpha Evolution**: Line chart showing how alpha changes during training (if applicable)
- **Final Metrics Comparison**: Heatmaps showing relative performance of different units
- **Detailed Metrics Table**: Table with the final metrics for each unit

You can select which units to compare using the dropdown menu in the sidebar.

### Exporting Results

The dashboard provides a button to export the comparison results as a CSV file.

## Folder Structure

```
├── dashboard_cifar.py         # Main dashboard application
├── generate_metrics_csv.py    # Script to generate metrics from different sources
├── lightning_modules/
│   └── metrics_logger.py      # PyTorch Lightning callback for saving metrics
└── logs/
    └── cifar10/               # Metrics for the dashboard
        ├── paGLU/
        │   └── metrics.csv    # Metrics for paGLU
        ├── paGTU/
        │   └── metrics.csv    # Metrics for paGTU
        └── ...
```

## Metrics Format

The metrics CSV files should have the following columns:
- `epoch`: Epoch number (starting from 1)
- `train_loss`: Training loss for the epoch
- `val_loss`: Validation loss for the epoch
- `train_acc`: Training accuracy for the epoch
- `val_acc`: Validation accuracy for the epoch
- `alpha` (optional): Alpha value for the epoch (for learnable alpha) 