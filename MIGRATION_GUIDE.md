# Migrating from Conda to UV - Detailed Guide

## Why UV?

### Performance Comparison
| Operation | Conda | UV | Speed Improvement |
|-----------|-------|-----|-------------------|
| Create environment | ~30s | ~3s | 10x faster |
| Install packages | ~2-5 min | ~10-30s | 4-10x faster |
| Resolve dependencies | ~1-2 min | ~5-10s | 6-12x faster |

### Disk Space Comparison
- **Conda**: ~500MB per environment (duplicate packages)
- **UV**: ~50MB per environment (shared cache)
- **Savings**: Up to 90% disk space with multiple projects

## Side-by-Side Commands

### Environment Creation
```powershell
# Conda
conda create -n goal_rec python=3.8
conda activate goal_rec

# UV
uv venv --python 3.8
.venv\Scripts\activate
```

### Installing from Requirements
```powershell
# Conda
conda env create -f goal_rec.yml

# UV
uv sync  # Uses pyproject.toml
```

### Package Management
```powershell
# Conda: Install package
conda install numpy

# UV: Install package
uv add numpy

# Conda: Install specific version
conda install numpy=1.19.2

# UV: Install specific version
uv add "numpy>=1.19.2,<1.20"

# Conda: Remove package
conda remove numpy

# UV: Remove package
uv remove numpy
```

### List Packages
```powershell
# Conda
conda list

# UV
uv pip list
```

### Export Environment
```powershell
# Conda
conda env export > environment.yml

# UV
uv pip freeze > requirements.txt
# or just use pyproject.toml
```

### Update Packages
```powershell
# Conda
conda update --all

# UV
uv lock --upgrade
uv sync
```

### Clean Cache
```powershell
# Conda
conda clean --all

# UV
uv cache clean
```

## Key Differences

### 1. Environment Location
- **Conda**: Centralized in `anaconda3/envs/`
- **UV**: Project-local `.venv/` folder

### 2. Configuration Files
- **Conda**: `environment.yml`
- **UV**: `pyproject.toml` (modern Python standard)

### 3. Package Sources
- **Conda**: Conda channels (conda-forge, defaults)
- **UV**: PyPI (Python Package Index)

### 4. Lock Files
- **Conda**: No built-in lock file
- **UV**: `uv.lock` ensures reproducibility

## Converting Dependencies

### Example: TensorFlow

**Conda version:**
```yaml
- tensorflow=2.4.0=py38h578d9bd_0
- tensorflow-base=2.4.0=py38h01d9eeb_0
- tensorflow-estimator=2.4.0=pyh9656e83_0
```

**UV version:**
```toml
dependencies = [
    "tensorflow>=2.4.0,<2.5",
]
```

UV automatically handles the base packages and estimator!

### Example: Scientific Stack

**Conda version:**
```yaml
- numpy=1.19.2=py38hf89b668_1
- scipy=1.7.0=py38h7b17777_1
- pandas=1.3.0=py38h1abd341_0
- matplotlib=3.4.2=py38h578d9bd_0
```

**UV version:**
```toml
dependencies = [
    "numpy>=1.19.2,<1.20",
    "scipy>=1.7.0,<2.0",
    "pandas>=1.3.0,<2.0",
    "matplotlib>=3.4.2,<4.0",
]
```

## Common Pitfalls and Solutions

### Pitfall 1: Package Not Found
**Problem**: Some conda-specific packages don't exist on PyPI

**Solution**: Find PyPI equivalent or use `uv pip install`
```powershell
# If package not on PyPI, try:
uv pip install package-name
```

### Pitfall 2: Different Package Names
**Problem**: Package has different name on PyPI

**Examples**:
- Conda: `pytorch` → PyPI: `torch`
- Conda: `opencv` → PyPI: `opencv-python`

### Pitfall 3: System Dependencies
**Problem**: Some packages need system libraries (like CUDA for TensorFlow)

**Solution**: Install system dependencies separately:
- Windows: Microsoft Visual C++ Redistributable
- CUDA: NVIDIA CUDA Toolkit

### Pitfall 4: Import Name vs Package Name
**Problem**: Import name differs from package name

**Examples**:
```python
# Package: opencv-python
import cv2

# Package: pillow
import PIL

# Package: scikit-learn
import sklearn
```

## GRNet-Specific Conversions

### Original Conda Packages → UV Packages

| Conda Package | UV Package | Notes |
|--------------|------------|-------|
| `tensorflow=2.4.0` | `tensorflow>=2.4.0,<2.5` | Auto includes estimator |
| `keras=2.4.3` | `keras>=2.4.3,<2.5` | Included with TF |
| `scikit-learn=0.24.2` | `scikit-learn>=0.24.2,<0.25` | Direct mapping |
| `jupyterlab=3.3.0` | `jupyterlab>=3.3.0,<4.0` | Direct mapping |
| `xgboost=1.5.0` | `xgboost>=1.5.0,<2.0` | Direct mapping |

### Packages Not in Original but Added
```toml
"unified-planning>=1.0.0"  # For adversarial_gen
```

## Testing Your Migration

### 1. Verify Python Version
```powershell
uv run python --version
# Should show Python 3.8.x
```

### 2. Verify Key Packages
```powershell
uv run python -c "import tensorflow; print(tensorflow.__version__)"
uv run python -c "import numpy; print(numpy.__version__)"
uv run python -c "import keras; print(keras.__version__)"
```

### 3. Test Jupyter
```powershell
uv run jupyter lab --version
uv run jupyter lab  # Should open browser
```

### 4. Test Main Notebook
```powershell
cd code
uv run jupyter lab GRNet_approach.ipynb
# Run the first few cells
```

## Advantages of UV for GRNet

1. **Faster Setup**: 10x faster than conda env creation
2. **Smaller**: Saves 450MB+ per project
3. **Modern**: Uses standard `pyproject.toml`
4. **Reproducible**: Lock file ensures exact versions
5. **Portable**: Easier to share and deploy
6. **Compatible**: Works with all PyPI packages
7. **Simple**: Single tool, clear commands

## When to Use Conda Instead

Consider sticking with Conda if:
- You need packages only available on Conda channels
- You require compiled binaries not on PyPI
- You work with R or other non-Python languages
- Your team is heavily invested in Conda

For GRNet, UV is recommended! ✅

## Getting Help

- **UV Issues**: https://github.com/astral-sh/uv/issues
- **Package Not Found**: Search PyPI at https://pypi.org
- **Import Errors**: Check `UV_QUICKREF.md` troubleshooting section

## Rollback to Conda

If you need to go back:
```powershell
# Remove UV environment
Remove-Item -Recurse -Force .venv

# Use original Conda setup
cd code
conda env create -f goal_rec.yml
conda activate goal_rec
```

The original `goal_rec.yml` is preserved for this purpose!
