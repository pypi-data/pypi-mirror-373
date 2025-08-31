# Reproducibility Guide for paGating Research

This document provides comprehensive instructions for reproducing all experimental results presented in the IEEE TNNLS paper "paGating: A Parameterized Activation Gating Framework for Flexible and Efficient Neural Networks for GenAI".

## 🎯 Overview

The paGating framework provides reproducible results across multiple domains:
- **Language Modeling**: GPT-2 Small on WikiText-103
- **Image Classification**: ResNet variants on CIFAR-10
- **Hardware Benchmarks**: Apple M4 performance analysis
- **Export Validation**: ONNX and CoreML compatibility

## 📋 System Requirements

### Minimum Requirements
- **Python**: 3.8+
- **PyTorch**: 1.9+
- **Memory**: 8GB RAM
- **Storage**: 5GB free space

### Recommended Setup
- **Python**: 3.10+
- **PyTorch**: 2.0+ with CUDA support
- **Memory**: 16GB+ RAM
- **GPU**: NVIDIA GPU with 8GB+ VRAM (optional but recommended)
- **Storage**: 20GB+ free space

### Hardware-Specific Testing
- **Apple M4 Benchmarks**: Requires Apple Silicon Mac
- **CUDA Benchmarks**: Requires NVIDIA GPU
- **CoreML Export**: Requires macOS

## 🚀 Quick Reproduction

### 1. Environment Setup
```bash
# Clone repository
git clone https://github.com/aaryanguglani/paGating.git
cd paGating

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

### 2. Verify Installation
```bash
# Run test suite
./run_tests.sh

# Quick benchmark
python scripts/benchmark/benchmark_gateflow.py --quick
```

### 3. Reproduce Key Results
```bash
# Language modeling results (Table II)
python experiments/reproduce_language_modeling.py

# Image classification results (Table III)
python experiments/reproduce_image_classification.py

# Hardware benchmarks (Table IV)
python experiments/reproduce_hardware_benchmarks.py
```

## 📊 Detailed Reproduction Instructions

### Language Modeling Experiments

#### GPT-2 Small on WikiText-103

**Objective**: Reproduce 1.9% improvement in evaluation loss

```bash
# Full reproduction (requires GPU, ~2-4 hours)
python experiments/train_gpt2_wikitex103.py \
    --model_size small \
    --dataset wikitext-103 \
    --units paGLU paGTU paSwishU identity \
    --alpha_values 0.0 0.2 0.5 0.8 1.0 \
    --epochs 10 \
    --batch_size 16 \
    --learning_rate 5e-4

# Quick validation (CPU compatible, ~30 minutes)
python experiments/train_gpt2_wikitex103.py \
    --quick \
    --units paGLU identity \
    --alpha_values 0.0 0.5 \
    --epochs 2
```

**Expected Results**:
- paGLU (α=0.5): ~3.85 evaluation loss
- Identity (α=0.0): ~3.92 evaluation loss
- Improvement: ~1.9%

#### Validation Steps
```bash
# Verify model convergence
python scripts/validate_convergence.py --experiment language_modeling

# Check statistical significance
python scripts/statistical_analysis.py --results language_modeling_results.json
```

### Image Classification Experiments

#### CIFAR-10 with ResNet Variants

**Objective**: Reproduce 59.1% accuracy with paGLU integration

```bash
# Full CIFAR-10 reproduction
python experiments/train_cifar10.py \
    --architecture resnet18 \
    --units paGLU paGTU paSwishU baseline \
    --alpha_values 0.0 0.2 0.5 0.8 1.0 \
    --epochs 100 \
    --batch_size 128

# Quick validation
python experiments/train_cifar10.py \
    --quick \
    --units paGLU baseline \
    --epochs 10
```

**Expected Results**:
- paGLU ResNet18: 59.1% ± 0.3% accuracy
- Baseline ResNet18: 57.2% ± 0.4% accuracy
- Improvement: +1.9 percentage points

### Hardware Performance Benchmarks

#### Apple M4 Optimization

**Objective**: Reproduce 3.11× speedup on Apple M4

```bash
# Requires Apple Silicon Mac
python experiments/benchmark_m4.py \
    --units paGLU paGTU paSwishU \
    --batch_sizes 1 8 16 32 \
    --sequence_lengths 128 512 1024 \
    --iterations 1000

# Alternative: CPU-only benchmarks
python experiments/benchmark_cpu.py \
    --units paGLU paGTU paSwishU \
    --profile_memory \
    --profile_compute
```

**Expected Results**:
- paGLU M4 optimized: 3.11× speedup vs baseline
- Memory efficiency: 15% reduction in peak usage
- Throughput: 2.8× improvement in tokens/second

### Export Compatibility Validation

#### ONNX Export Testing

```bash
# Test all units for ONNX compatibility
python scripts/test_onnx_export.py \
    --units paGLU paGTU paSwishU paGELU paMishU \
    --alpha_values 0.0 0.5 1.0 \
    --opset_version 17

# Validate exported models
python scripts/validate_onnx_models.py \
    --input_shapes "1,512" "8,512" "32,512"
```

#### CoreML Export Testing

```bash
# Requires macOS
python scripts/test_coreml_export.py \
    --units paGLU paGTU paSwishU \
    --alpha_values 0.0 0.5 1.0 \
    --target_ios 15.0

# Performance validation
python scripts/benchmark_coreml.py \
    --device_types cpu gpu ane
```

## 🔬 Advanced Reproduction

### Custom Experiments

#### Hyperparameter Sensitivity Analysis

```bash
# Alpha sensitivity sweep
python experiments/alpha_sensitivity.py \
    --alpha_range 0.0 1.0 \
    --alpha_steps 21 \
    --units paGLU paGTU \
    --tasks language_modeling image_classification

# Learning rate sensitivity
python experiments/lr_sensitivity.py \
    --lr_range 1e-5 1e-2 \
    --lr_steps 10 \
    --units paGLU
```

#### Ablation Studies

```bash
# Component ablation
python experiments/ablation_study.py \
    --components alpha_scheduling normalization bias \
    --units paGLU paGTU

# Architecture ablation
python experiments/architecture_ablation.py \
    --architectures transformer cnn rnn \
    --units paGLU paSwishU
```

### Statistical Validation

#### Significance Testing

```bash
# Run multiple seeds for statistical significance
python experiments/multi_seed_validation.py \
    --seeds 42 123 456 789 1337 \
    --experiments language_modeling image_classification \
    --units paGLU paGTU

# Statistical analysis
python scripts/statistical_analysis.py \
    --results multi_seed_results.json \
    --tests ttest wilcoxon bootstrap \
    --confidence_level 0.95
```

## 📈 Results Validation

### Expected Performance Metrics

#### Language Modeling (WikiText-103)
| Unit | α | Eval Loss | Perplexity | Improvement |
|------|---|-----------|------------|-------------|
| Identity | 0.0 | 3.92 | 50.4 | Baseline |
| paGLU | 0.5 | 3.85 | 47.0 | +1.9% |
| paGTU | 0.5 | 3.87 | 47.8 | +1.3% |
| paSwishU | 0.5 | 3.86 | 47.4 | +1.6% |

#### Image Classification (CIFAR-10)
| Unit | α | Accuracy | Top-5 Acc | Improvement |
|------|---|----------|-----------|-------------|
| Baseline | - | 57.2% | 95.1% | Baseline |
| paGLU | 0.5 | 59.1% | 96.2% | +1.9pp |
| paGTU | 0.5 | 58.7% | 95.9% | +1.5pp |
| paSwishU | 0.5 | 58.9% | 96.0% | +1.7pp |

#### Hardware Performance (Apple M4)
| Metric | Baseline | paGLU | Speedup |
|--------|----------|-------|---------|
| Inference (ms) | 12.4 | 4.0 | 3.11× |
| Memory (MB) | 245 | 208 | 1.18× |
| Throughput (tok/s) | 1250 | 3500 | 2.8× |

### Tolerance Ranges

Due to hardware variations and random initialization:
- **Language Modeling**: ±0.02 evaluation loss
- **Image Classification**: ±0.5% accuracy
- **Hardware Benchmarks**: ±10% timing variation

## 🐛 Troubleshooting

### Common Issues

#### CUDA Out of Memory
```bash
# Reduce batch size
export CUDA_BATCH_SIZE=8

# Enable gradient checkpointing
export ENABLE_CHECKPOINTING=1

# Use mixed precision
export USE_AMP=1
```

#### Slow Training
```bash
# Enable optimizations
export TORCH_COMPILE=1
export CUDA_LAUNCH_BLOCKING=0

# Use DataLoader optimizations
export NUM_WORKERS=4
export PIN_MEMORY=1
```

#### Export Failures
```bash
# Check PyTorch version compatibility
python -c "import torch; print(torch.__version__)"

# Validate model before export
python scripts/validate_model.py --unit paGLU --alpha 0.5

# Use static alpha for exports
export FORCE_STATIC_ALPHA=1
```

### Platform-Specific Issues

#### macOS
```bash
# Install MPS support
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# CoreML dependencies
pip install coremltools>=6.0
```

#### Windows
```bash
# CUDA setup
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# Path issues
set PYTHONPATH=%PYTHONPATH%;%CD%
```

#### Linux
```bash
# CUDA libraries
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH

# Shared memory
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
```

## 📞 Support

### Getting Help

1. **Check Documentation**: Review this guide and README.md
2. **Search Issues**: Look for similar problems in GitHub issues
3. **Run Diagnostics**: Use `python scripts/diagnose_environment.py`
4. **Create Issue**: Provide full error logs and system information

### Reporting Reproduction Issues

When reporting issues, include:
- **System Information**: OS, Python version, PyTorch version
- **Hardware Details**: CPU, GPU, memory specifications
- **Error Logs**: Complete error messages and stack traces
- **Reproduction Steps**: Exact commands used
- **Expected vs Actual**: What you expected vs what happened

### Contact Information

- **GitHub Issues**: Primary support channel
- **Email**: aaryanguglani.cs21@rvce.edu.in
- **Paper Authors**: Aaryan Guglani, Rajashree Shettar

## 📚 Additional Resources

- **Paper**: IEEE TNNLS submission (under review)
- **Documentation**: `/docs` directory
- **Examples**: `/examples` directory
- **Benchmarks**: `/benchmarks` directory
- **Tests**: `/tests` directory

## 🏆 Citation

If you use this reproduction guide or achieve similar results, please cite:

```bibtex
@article{guglani2025pagating,
  title={paGating: A Parameterized Activation Gating Framework for Flexible and Efficient Neural Networks for GenAI},
  author={Guglani, Aaryan and Shettar, Rajashree},
  journal={IEEE Transactions on Neural Networks and Learning Systems},
  year={2025},
  note={Under Review}
}
```

---

**Last Updated**: June 2025  
**Version**: 1.0  
**Compatibility**: paGating v1.0+ 