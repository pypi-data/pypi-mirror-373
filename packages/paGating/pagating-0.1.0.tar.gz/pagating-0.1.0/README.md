# paGating: Parameterized Activation Gating Framework

[![PyTorch](https://img.shields.io/badge/PyTorch-1.9%2B-orange)](https://pytorch.org/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org/)
[![Tests](https://img.shields.io/badge/Tests-93%25%20Coverage-green)](./tests/)
[![Paper](https://img.shields.io/badge/Paper-IEEE%20TNNLS-red)](https://github.com/guglxni/paGating)

> **🚀 Production-Ready Framework for Parameterized Activation Gating in Neural Networks**

A comprehensive, open-source framework that unifies gated activation functions through a single parameterization scheme. Featured in our IEEE TNNLS submission: *"paGating: A Parameterized Activation Gating Framework for Flexible and Efficient Neural Networks for GenAI"*.

## 🎯 Key Results

Our framework demonstrates significant improvements across multiple domains:

| Domain | Metric | Improvement | Hardware |
|--------|--------|-------------|----------|
| **Language Modeling** | WikiText-103 Eval Loss | **1.9% improvement** | GPT-2 Small |
| **Image Classification** | CIFAR-10 Accuracy | **+1.9 percentage points** | ResNet variants |
| **Hardware Efficiency** | Apple M4 Inference | **3.11× speedup** | 15% memory reduction |

## 🚀 Features

- **🔬 7 Core Gating Units + Specialized Components**: paGLU, paGTU, paSwishU, paReGLU, paGELU, paMishU, paSiLU, paUnit (template), PaGRUCell
- **⚡ Production Ready**: ONNX and CoreML export pipelines for deployment
- **🧪 Comprehensive Testing**: 93% test coverage with continuous integration
- **📊 Benchmarking Tools**: Built-in performance analysis and visualization
- **🔄 PyTorch Lightning**: Seamless integration with modern training workflows
- **📱 Cross-Platform**: CPU, CUDA, MPS (Apple Silicon) support
- **🎛️ Flexible Alpha**: Fixed, learnable, or scheduled parameter control

## Project Structure

The project has been organized into the following structure:

```
paGating/
├── assets/                  # Static assets
│   └── images/              # Image files
│       ├── figures/         # Paper figures
│       └── plots/           # Plot outputs from experiments
├── benchmark_results/       # Results from various benchmarks
│   ├── coreml/              # CoreML benchmark results
│   ├── regression/          # Regression task results
│   └── transformer/         # Transformer model results
├── coreml_models/           # Exported CoreML models
├── datamodules/             # PyTorch Lightning data modules
├── docs/                    # Documentation
│   ├── paper/               # Research paper and references
│   └── results_summary.md   # Summary of experiment results
├── experiments/             # Experiment configurations
├── lightning_modules/       # PyTorch Lightning modules
├── models/                  # Model implementations
├── onnx_models/             # Exported ONNX models
├── paGating/                # Core package
│   ├── __init__.py          # Package exports
│   ├── base.py              # Base classes
│   ├── paGLU.py             # Gated Linear Unit implementation
│   ├── paGTU.py             # Gated Tanh Unit implementation
│   ├── paSwishU.py          # Swish Unit implementation
│   ├── paReGLU.py           # ReLU Gated Linear Unit implementation
│   ├── paGELU.py            # GELU Gated Unit implementation
│   ├── paMishU.py           # Mish Unit implementation
│   ├── paSiLU.py            # SiLU/Swish gating implementation
│   ├── paUnit.py            # Generic gating unit template
│   └── paGRU.py             # Parameterized GRU cell
├── scripts/                 # Utility scripts
│   ├── benchmark/           # Benchmarking scripts
│   └── utilities/           # Utility scripts
├── src/                     # Source code (application-specific)
├── tests/                   # Test suite
├── requirements.txt         # Project dependencies
└── README.md                # This file
```

## Implemented Gating Units

| Unit | Description | Formula |
|------|-------------|---------|
| paGLU | Parameterized Gated Linear Unit | x * (α * sigmoid(x) + (1-α)) |
| paGTU | Parameterized Gated Tanh Unit | x * (α * tanh(x) + (1-α)) |
| paSwishU | Parameterized Swish Unit | x * (α * sigmoid(x) + (1-α) * x) |
| paReGLU | Parameterized ReLU Gated Linear Unit | x * (α * ReLU(x) + (1-α)) |
| paGELU | Parameterized Gated GELU | x * (α * GELU(x) + (1-α)) |
| paMishU | Parameterized Mish Unit | x * (α * mish(x) + (1-α)) |
| paSiLU | Parameterized SiLU/Swish gating | x * (α * SiLU(x) + (1-α) * x) |
| paUnit | Generic Template for Custom Units | x * (α * custom_fn(x) + (1-α)) |
| PaGRUCell | Parameterized GRU Cell | Specialized recurrent architecture |

## Installation

Clone the repository:
```bash
git clone https://github.com/guglxni/paGating.git
cd paGating
```

Install requirements:
```bash
pip install -r requirements.txt
```

Set up data directories and download datasets:
```bash
python scripts/download_data.py
```

> **Note**: This repository uses symlinks for large data files. See [docs/DATA_SETUP.md](docs/DATA_SETUP.md) for detailed setup instructions.

## Quick Start

### Using a paGating unit in your model

```python
import torch
from paGating import paGLU

# Create a layer with fixed alpha
gating_layer = paGLU(input_dim=512, output_dim=512, alpha=0.5)

# Or with learnable alpha
learnable_gating_layer = paGLU(input_dim=512, output_dim=512, learnable_alpha=True)

# Use in a model
x = torch.randn(32, 512)  # batch_size, input_dim
output = gating_layer(x)  # shape: (32, 512)
```

### Integration with PyTorch models

```python
import torch
import torch.nn as nn
from paGating import paGLU

class MyModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(784, 512)
        self.gate = paGLU(512, 512, alpha=0.5)  # paGating unit
        self.fc2 = nn.Linear(512, 10)
        
    def forward(self, x):
        x = self.fc1(x)
        x = self.gate(x)
        x = self.fc2(x)
        return x
```

## Experimenting with paGating

### Running Benchmarks

The framework includes tools for benchmarking different gating units:

```bash
python scripts/benchmark/benchmark_gateflow.py
```

This generates plots comparing the performance of different units.

### Running a Hyperparameter Sweep

To compare different units and alpha values:

```bash
python scripts/utilities/run_experiment_pipeline.py --experiment_name my_experiment --units paGLU paGTU paMishU --alpha_values 0.0 0.2 0.5 0.8 1.0
```

This will:
1. Run a hyperparameter sweep
2. Generate a leaderboard
3. Create visualizations

### Testing with Transformer Models

To test a gating unit in a transformer for sequence classification:

```bash
python experiments/test_transformer.py --unit paMishU --alpha 0.5 --epochs 20
```

## Export to CoreML

You can export trained models to CoreML format for deployment on Apple devices:

```bash
python scripts/coreml_export.py --unit paGLU --alpha 0.5
```

Test the exported model:

```bash
python tests/test_coreml_model.py --unit paGLU --alpha 0.5
```

## Results Summary

For detailed results and comparisons of different gating units, see [docs/results_summary.md](docs/results_summary.md).

## Creating Your Own Gating Unit

To create a custom gating unit:

1. Create a new file in the paGating directory (e.g., `paGating/paMyCustomU.py`)
2. Extend the `paGatingBase` class
3. Implement the required methods
4. Update `__init__.py` to expose your new unit

Example:

```python
from .base import paGatingBase
import torch
import torch.nn as nn
import torch.nn.functional as F

class paMyCustomU(paGatingBase):
    """
    My custom parameterized activation gating unit.
    """
    
    def __init__(self, input_dim, output_dim, alpha=0.5, learnable_alpha=False, alpha_init=None, bias=True):
        super().__init__(
            input_dim=input_dim, 
            output_dim=output_dim, 
            alpha=alpha,
            learnable_alpha=learnable_alpha,
            alpha_init=alpha_init,
            bias=bias
        )
        
    def compute_gate_activation(self, x):
        # Implement your custom activation function
        return my_custom_activation(x)
        
    def forward(self, x):
        # Standard implementation, can be customized if needed
        x = self.linear(x)
        gates = self.compute_gate_activation(x)
        return x * gates
```

Then update `__init__.py`:

```python
from .paMyCustomU import paMyCustomU

__all__ = [
    # ... existing units
    'paMyCustomU',
]
```

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

**Commercial Use**: For commercial applications, please contact the authors for licensing arrangements.

## 📄 Research Paper

This framework is featured in our IEEE TNNLS submission:

**"paGating: A Parameterized Activation Gating Framework for Flexible and Efficient Neural Networks for GenAI"**

- **Authors**: Aaryan Guglani, Dr. Rajashree Shettar
- **Institution**: RV College of Engineering, Bengaluru
- **Status**: Under Review at IEEE Transactions on Neural Networks and Learning Systems
- **Reproducibility**: Complete reproduction guide available in [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md)

## 📚 Documentation

- **[Reproducibility Guide](docs/REPRODUCIBILITY.md)**: Step-by-step instructions to reproduce all paper results
- **[Contributing Guide](CONTRIBUTING.md)**: How to contribute to the project
- **[API Documentation](docs/)**: Detailed API reference and examples

## 🏆 Citation

If you use paGating in your research, please cite:

```bibtex
@article{guglani2025pagating,
  title={paGating: A Parameterized Activation Gating Framework for Flexible and Efficient Neural Networks for GenAI},
  author={Guglani, Aaryan and Shettar, Rajashree},
  journal={IEEE Transactions on Neural Networks and Learning Systems},
  year={2025},
  note={Under Review},
  url={https://github.com/guglxni/paGating}
}
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Interactive Dashboard

The project includes a Streamlit dashboard for visualizing experiment results:

```bash
# Install required packages if not already installed
pip install streamlit plotly pandas

# Run the dashboard with a specific results directory
streamlit run scripts/streamlit_dashboard.py -- --results_dir results/your_experiment_dir

# Or run the dashboard and select the results directory in the UI
streamlit run scripts/streamlit_dashboard.py
```

Dashboard features:
- Compare performance across different gating units
- Analyze the effect of different alpha values
- Explore the behavior of learnable alpha parameters
- View training curves and leaderboards
- Generate insights and recommendations

## Experiments

Run a hyperparameter sweep:

```bash
python scripts/utilities/run_experiment_pipeline.py
```

This will:
1. Run a sweep over different units and alpha values
2. Generate a leaderboard
3. Create visualizations
4. Run the analysis

## Research Paper

A detailed research paper describing the paGating framework, its implementation, and experimental results is available in the [docs/paper/](docs/paper/) directory.