# GRNet - UV Package Manager Setup

This project has been converted to use [UV](https://github.com/astral-sh/uv) package manager for faster and more reliable Python dependency management.

## Prerequisites

1. Install UV (if not already installed):
   ```powershell
   # Windows (PowerShell)
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. Ensure Python 3.8 is available on your system

## Quick Start

### 1. Create and activate virtual environment

```powershell
# Create a virtual environment with Python 3.8
uv venv --python 3.8

# Activate the virtual environment
.venv\Scripts\activate
```

### 2. Install dependencies

```powershell
# Sync all dependencies from pyproject.toml
uv sync
```

### 3. Run Jupyter Lab

```powershell
# Start Jupyter Lab
uv run jupyter lab
```

## Project Structure

- `code/` - Main code directory with Jupyter notebooks
- `models/` - Pre-trained models for each domain
- `testsets/` - Test sets for experiments
- `adversarial_gen/` - Adversarial plan generation code

## Working with the Project

### Running the Main Notebook

```powershell
cd code
uv run jupyter lab GRNet_approach.ipynb
```

### Running Python Scripts

```powershell
# Run any Python script with UV
uv run python script_name.py
```

### Adding New Dependencies

```powershell
# Add a new package
uv add package-name

# Add a development dependency
uv add --dev package-name
```

### Updating Dependencies

```powershell
# Update all packages to latest compatible versions
uv lock --upgrade
uv sync
```

## Key Differences from Conda

| Conda | UV |
|-------|-----|
| `conda env create -f goal_rec.yml` | `uv sync` |
| `conda activate goal_rec` | `.venv\Scripts\activate` |
| `conda install package` | `uv add package` |
| `conda list` | `uv pip list` |

## Benefits of UV

- **⚡ Faster**: 10-100x faster than pip/conda
- **🔒 Reliable**: Deterministic dependency resolution
- **💾 Efficient**: Shared package cache across projects
- **🎯 Simple**: Single tool for all Python needs
- **🔄 Compatible**: Works with PyPI packages

## Troubleshooting

### Issue: TensorFlow not installing properly
UV will use the pip-compatible TensorFlow package. If you encounter issues:
```powershell
uv pip install tensorflow==2.4.0 --force-reinstall
```

### Issue: CUDA/GPU support
For GPU support with TensorFlow:
```powershell
uv pip install tensorflow-gpu==2.4.0
```

### Issue: Missing system libraries
Some packages (like TensorFlow) may require system libraries. On Windows, ensure you have:
- Microsoft Visual C++ Redistributable
- CUDA Toolkit (for GPU support)

## Development

### Running Tests

```powershell
uv run pytest
```

### Code Formatting

```powershell
uv run black .
uv run ruff check .
```

## Migration Notes

This project was originally using Conda with Python 3.8. The main dependencies have been converted to their PyPI equivalents in `pyproject.toml`. The original conda environment file (`code/goal_rec.yml`) is preserved for reference.

Key changes:
- Python 3.8 environment (pinned)
- TensorFlow 2.4.0 (CPU version by default)
- All scientific computing libraries maintained at similar versions
- Added modern development tools (pytest, black, ruff)

## Additional Resources

- [UV Documentation](https://docs.astral.sh/uv/)
- [Original GRNet Paper](https://icaps23.icaps-conference.org/)
- [PyProject.toml Reference](https://peps.python.org/pep-0621/)
