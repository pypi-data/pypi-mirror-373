# Contributing to paGating

Thank you for your interest in contributing to paGating! This document provides guidelines for contributing to the project.

## 🚀 Quick Start for Contributors

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/paGating.git
   cd paGating
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -e .  # Install in development mode
   ```

4. **Run Tests**
   ```bash
   ./run_tests.sh
   ```

## 📋 Contribution Guidelines

### Types of Contributions

1. **New Activation Units** - Implement new parameterized activation functions
2. **Performance Optimizations** - Improve computational efficiency
3. **Documentation** - Enhance docs, examples, and tutorials
4. **Bug Fixes** - Fix issues and improve stability
5. **Testing** - Add test coverage and validation

### Code Standards

- **PEP 8 Compliance**: Follow Python style guidelines
- **Type Hints**: Use type annotations for all functions
- **Docstrings**: Document all classes and methods
- **Testing**: Maintain >90% test coverage

### Naming Conventions

- **paUnits**: Follow `pa<ActivationName>U` pattern (e.g., `paGELU`, `paMishU`)
- **Files**: Use snake_case for filenames
- **Classes**: Use PascalCase for class names
- **Functions**: Use snake_case for function names

## 🧪 Testing Requirements

### Running Tests
```bash
# Run all tests
./run_tests.sh

# Run specific test file
python -m pytest tests/test_pa_units.py -v

# Run with coverage
python -m pytest --cov=paGating tests/
```

### Test Categories

1. **Unit Tests** - Test individual components
2. **Integration Tests** - Test component interactions
3. **Performance Tests** - Benchmark performance
4. **Export Tests** - Validate ONNX/CoreML exports

### Adding New Tests

When adding a new paUnit, include:
- Basic functionality tests
- Parameter validation tests
- Gradient computation tests
- Export compatibility tests

## 📝 Documentation Standards

### Code Documentation
- Use Google-style docstrings
- Include parameter types and descriptions
- Provide usage examples
- Document mathematical formulations

### Example Docstring
```python
def compute_gate_activation(self, x: torch.Tensor) -> torch.Tensor:
    """Compute the gate activation for the input tensor.
    
    Args:
        x: Input tensor of shape (batch_size, input_dim)
        
    Returns:
        Gate activation tensor of same shape as input
        
    Example:
        >>> unit = paGLU(512, 512, alpha=0.5)
        >>> x = torch.randn(32, 512)
        >>> gates = unit.compute_gate_activation(x)
        >>> assert gates.shape == x.shape
    """
```

## 🔧 Adding New paUnits

### Step-by-Step Guide

1. **Create Unit File**
   ```bash
   touch paGating/pa<YourUnit>U.py
   ```

2. **Implement Base Class**
   ```python
   from .base import paGatingBase
   import torch
   import torch.nn.functional as F
   
   class pa<YourUnit>U(paGatingBase):
       def compute_gate_activation(self, x):
           # Implement your activation logic
           return your_activation_function(x)
   ```

3. **Add to Package**
   Update `paGating/__init__.py`:
   ```python
   from .pa<YourUnit>U import pa<YourUnit>U
   
   __all__ = [
       # ... existing units
       'pa<YourUnit>U',
   ]
   ```

4. **Create Tests**
   ```python
   # tests/test_pa<yourunit>u.py
   import pytest
   import torch
   from paGating import pa<YourUnit>U
   
   def test_pa<yourunit>u_basic():
       unit = pa<YourUnit>U(512, 512, alpha=0.5)
       x = torch.randn(32, 512)
       output = unit(x)
       assert output.shape == x.shape
   ```

5. **Add to Benchmarks**
   Update benchmark scripts to include your unit

6. **Update Documentation**
   Add your unit to README.md and create usage examples

## 🚀 Performance Guidelines

### Optimization Principles
- Minimize memory allocations
- Use in-place operations where possible
- Leverage PyTorch's built-in functions
- Profile before optimizing

### Benchmarking
```bash
python scripts/benchmark/benchmark_gateflow.py --units pa<YourUnit>U
```

## 📊 Export Compatibility

### ONNX Export
Ensure your unit works with ONNX export:
```python
# Test ONNX export
python scripts/export_to_onnx.py --unit pa<YourUnit>U --alpha 0.5
```

### CoreML Export
Test CoreML compatibility:
```python
# Test CoreML export
python scripts/coreml_export.py --unit pa<YourUnit>U --alpha 0.5
```

## 🔄 Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/add-pa<yourunit>u
   ```

2. **Make Changes**
   - Implement your feature
   - Add comprehensive tests
   - Update documentation

3. **Test Everything**
   ```bash
   ./run_tests.sh
   python scripts/benchmark/benchmark_gateflow.py
   ```

4. **Submit PR**
   - Clear description of changes
   - Reference any related issues
   - Include test results

### PR Checklist
- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Export compatibility verified

## 🐛 Bug Reports

### Issue Template
```markdown
**Bug Description**
Clear description of the bug

**Reproduction Steps**
1. Step 1
2. Step 2
3. Step 3

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- Python version:
- PyTorch version:
- OS:
- Hardware:
```

## 💡 Feature Requests

### Request Template
```markdown
**Feature Description**
Clear description of the proposed feature

**Use Case**
Why is this feature needed?

**Proposed Implementation**
How should this be implemented?

**Alternatives Considered**
Other approaches considered
```

## 📚 Resources

- [PyTorch Documentation](https://pytorch.org/docs/)
- [PEP 8 Style Guide](https://pep8.org/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Semantic Versioning](https://semver.org/)

## 🏆 Recognition

Contributors will be acknowledged in:
- CONTRIBUTORS.md file
- Release notes
- Academic publications (where appropriate)

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and general discussion
- **Email**: For private inquiries

Thank you for contributing to paGating! 🎉 