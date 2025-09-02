# liron-utils

A comprehensive collection of utility modules for data analysis, visualization, machine learning, and more.

## Installation

### From PyPI (recommended)
```bash
pip install liron-utils
```

### With optional dependencies
```bash
# Install with extra dependencies
pip install liron-utils[extra]

# Install with all dependencies
pip install liron-utils[all]
```

### Development installation
To install the package in editable mode for development:
```bash
pip install -e git+https://github.com/lironst1/liron-utils.git#egg=liron-utils
```

## Features

This package includes various utility modules:

- **graphics**: Visualization and plotting utilities
- **signal_processing**: Signal analysis and processing tools
- **machine_learning**: ML utilities and helpers
- **pure_python**: General Python utilities
- **symbolic_math**: Symbolic mathematics tools
- **time**: Time-related utilities
- **uncertainties_math**: Uncertainty propagation tools
- **files**: File handling utilities
- **web**: Web-related utilities
- **manim_animations**: Animation utilities using Manim

## Usage

```python
import liron_utils

# Check version
print(liron_utils.__version__)

# Use specific modules
from liron_utils import graphics
```

## Requirements

See `pyproject.toml` for full dependency list

## License

See LICENSE file for details.
