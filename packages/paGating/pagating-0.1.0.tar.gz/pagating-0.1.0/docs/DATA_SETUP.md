# Data Setup Guide

This repository uses symlinks to external storage for large data files and model outputs. This keeps the repository lightweight while maintaining access to necessary data.

## Directory Structure

The following directories are symlinked to external storage:

```
data/ -> /Volumes/MacExt/paGating_data/data/
├── cifar-10-python.tar.gz (170MB)
├── cifar-10-batches-py/
├── cifar10/
├── cifar_datamodule.py
└── cifar10_datamodule.py

.cache/ -> /Volumes/MacExt/paGating_models/.cache/
├── huggingface/
└── torch/

logs/ -> /Volumes/MacExt/paGating_models/logs/
├── experiment_logs/
└── training_outputs/

lightning_outputs/ -> /Volumes/MacExt/paGating_models/lightning_outputs/
├── checkpoints/
└── tensorboard_logs/

coreml_models/ -> /Volumes/MacExt/paGating_models/coreml_models/
├── exported_models/
└── optimization_results/

benchmark_temp/ -> /Volumes/MacExt/paGating_models/benchmark_temp/
└── temporary_benchmark_files/
```

## Setup Instructions

### For Development/Reproduction:

1. **Download Required Datasets:**
   ```bash
   # CIFAR-10 dataset will be automatically downloaded by the scripts
   python scripts/download_data.py
   ```

2. **Create Data Directories:**
   ```bash
   mkdir -p data logs .cache lightning_outputs coreml_models benchmark_temp
   ```

3. **For Large Storage Setup (Optional):**
   If you have external storage and want to replicate the symlink setup:
   ```bash
   # Create external directories
   mkdir -p /path/to/external/storage/paGating_data/data
   mkdir -p /path/to/external/storage/paGating_models/{.cache,logs,lightning_outputs,coreml_models,benchmark_temp}
   
   # Create symlinks
   ln -s /path/to/external/storage/paGating_data/data data
   ln -s /path/to/external/storage/paGating_models/.cache .cache
   ln -s /path/to/external/storage/paGating_models/logs logs
   ln -s /path/to/external/storage/paGating_models/lightning_outputs lightning_outputs
   ln -s /path/to/external/storage/paGating_models/coreml_models coreml_models
   ln -s /path/to/external/storage/paGating_models/benchmark_temp benchmark_temp
   ```

## Data Requirements

- **CIFAR-10**: ~170MB (automatically downloaded)
- **Model Cache**: ~1-5GB (varies with usage)
- **Training Logs**: ~100MB-1GB (depends on experiments)
- **Exported Models**: ~50-500MB (depends on model size)

## Notes

- The symlinks are included in `.gitignore` to prevent broken links in the repository
- All data can be regenerated using the provided scripts
- For cloud deployment, use the provided Docker configuration which handles data mounting 