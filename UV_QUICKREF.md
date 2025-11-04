# GRNet UV Quick Reference Card

## 🚀 Initial Setup (One Time)

```powershell
# Run the automated setup script
uv run setup_uv.py

# OR do it manually:
uv venv --python 3.8        # Create virtual environment
.venv\Scripts\activate      # Activate it
uv sync                     # Install all dependencies
```

## 📊 Daily Usage

```powershell
# Activate environment
.venv\Scripts\activate

# Start Jupyter Lab
uv run jupyter lab

# Run a Python script
uv run python script.py

# Run adversarial generation
cd adversarial_gen\code
uv run python main.py
```

## 📦 Package Management

```powershell
# Add a package
uv add numpy

# Add a dev dependency
uv add --dev pytest

# Remove a package
uv remove package-name

# Update all packages
uv lock --upgrade
uv sync

# List installed packages
uv pip list

# Show package info
uv pip show package-name
```

## 🔧 Environment Management

```powershell
# Create new environment
uv venv --python 3.8

# Activate environment
.venv\Scripts\activate      # PowerShell
.venv\Scripts\activate.bat  # CMD

# Deactivate
deactivate

# Delete environment
Remove-Item -Recurse -Force .venv
```

## 🐛 Troubleshooting

```powershell
# Reinstall all dependencies
uv sync --reinstall

# Clear UV cache
uv cache clean

# Install specific TensorFlow version
uv pip install tensorflow==2.4.0

# Check Python version
uv run python --version
```

## 📁 Project Commands

```powershell
# Run main notebook
cd code
uv run jupyter lab GRNet_approach.ipynb

# Run adversarial generator
cd adversarial_gen\code
uv run python main.py

# Run with specific Python
uv run --python 3.8 python script.py
```

## 🔄 Migration from Conda

| Conda Command | UV Equivalent |
|---------------|---------------|
| `conda create -n env python=3.8` | `uv venv --python 3.8` |
| `conda activate env` | `.venv\Scripts\activate` |
| `conda install package` | `uv add package` |
| `conda list` | `uv pip list` |
| `conda env export` | `uv pip freeze` |
| `conda remove package` | `uv remove package` |
| `conda deactivate` | `deactivate` |

## 💡 Tips

- UV is 10-100x faster than pip/conda
- No need to specify channels, UV uses PyPI
- Lock file ensures reproducible builds
- Shared cache saves disk space
- Works great with existing pip packages

## 🆘 Common Issues

**Issue**: Module not found after installation
```powershell
# Solution: Make sure environment is activated
.venv\Scripts\activate
```

**Issue**: TensorFlow not working
```powershell
# Solution: Reinstall TensorFlow
uv pip install --force-reinstall tensorflow==2.4.0
```

**Issue**: Jupyter kernel not found
```powershell
# Solution: Install ipykernel
uv add ipykernel
uv run python -m ipykernel install --user --name=grnet
```

## 📖 More Help

- UV Docs: https://docs.astral.sh/uv/
- Project Setup: See `UV_SETUP.md`
- Original Setup: See `code/README.md`
