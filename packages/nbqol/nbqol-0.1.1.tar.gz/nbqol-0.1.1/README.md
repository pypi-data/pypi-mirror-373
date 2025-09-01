# NB-QOL

Cross-platform, modular, quality-of-life tool kit for working with Jupyter notebooks wherever you work with them.

## Features

- **CUDA Device Management**: Easily configure, monitor, and select CUDA devices for your notebook
- **Output Capture**: Capture stdout, stderr, and logging in a clean, organized way  
- **Path Operations**: Utilities for working with notebook paths and Git repositories
- **IPython Configuration**: Quickly configure IPython settings like autoreload
- **Notebook Styling**: Auto-detect environment and apply appropriate CSS styling (VS Code, Jupyter Lab, etc.)
- **Notebook Processing**: Convert, clean, analyze, and execute notebooks programmatically
- **Environment Detection**: Detect notebook execution environment (VS Code, Jupyter, etc.)

## Installation

From PyPI:
```bash
pip install nbqol
```

Latest development version:
```bash
pip install git+https://github.com/ColinConwell/NB-QOL.git
```

## Quick Start

Here are some examples of what you can do with NB-QOL:

```python
# Import the library
import nbqol

# Configure IPython
nbqol.set_autoreload('complete')  # Auto-reload modules
nbqol.hide_warnings()  # Hide warning messages

# Get environment settings
env_info = nbqol.get_main_env_settings()

# Manage CUDA devices
nbqol.count_cuda_devices()  # Count available CUDA devices
nbqol.cuda_device_report()  # Get detailed info about CUDA devices
nbqol.set_cuda_visibles(0)  # Make only device 0 visible

# Path operations
notebook_dir = nbqol.notebook_path()
git_root = nbqol.path_to_git_root()

# Capture output
with nbqol.capture_output() as captured:
    print("This will be captured")
    import logging
    logging.warning("This warning will be captured")
print(captured)

# Apply styling
nbqol.auto_style()  # Apply appropriate styling based on environment
```

## Command Line Interface

NB-QOL also provides a command-line interface for common tasks:

```bash
# Show version
nbqol --version

# Show help
nbqol --help

# Get CUDA device information
nbqol device-info

# Apply styling to current environment
nbqol style
```

## Documentation

For full documentation, visit [docs/build/html/index.html](docs/build/html/index.html) after building the documentation:

```bash
# Recommended approach (includes tests)
./scripts/build_docs.sh

# Alternative approaches
cd docs && hatch run docs:build
cd docs && make html
cd docs && sphinx-build -b html source build/html
```

The `build_docs.sh` script runs tests to verify the package installation and documentation build before generating the HTML docs.

## Development

```bash
# Clone the repository
git clone https://github.com/ColinConwell/NB-QOL.git
cd NB-QOL

# Install in development mode
pip install -e .

# Install development dependencies
pip install -e .[dev]

# Run tests
pytest tests/

# Install documentation dependencies
pip install -e .[docs]

# Build documentation
cd docs && sphinx-build -b html source build/html
```

## Other Resources

### Related Tools

- [nbdime](https://github.com/jupyter/nbdime) - A tool from the Jupyter team for comparing and diffing Jupyter notebooks.
- [nb-clean](https://github.com/srstevenson/nb-clean) - A tool for cleaning and compression Jupyter notebooks in GitHub and other version control systems.
- [nbstripout](https://github.com/kynan/nbstripout) - A tool for stripping output from Jupyter notebooks for compression or presentation purposes.

### Dependency Source Repos

- [notebook](https://github.com/jupyter/notebook)
- [nbformat](https://github.com/jupyter/nbformat)
- [nbconvert](https://github.com/jupyter/nbconvert)




## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
