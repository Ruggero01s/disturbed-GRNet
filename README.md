# GRNet
Deep Learning architecture for solving Goal Recognition tasks. 

## 🚀 Quick Start with UV Package Manager

This project now supports [UV](https://github.com/astral-sh/uv) - a fast Python package manager!

### Setup (Windows)
```powershell
# Option 1: Automated setup
setup_uv.bat

# Option 2: Manual setup
uv venv --python 3.8
.venv\Scripts\activate
uv sync
```

### Run
```powershell
uv run jupyter lab
```

📖 **See [UV_SETUP.md](UV_SETUP.md) for detailed instructions** or [UV_QUICKREF.md](UV_QUICKREF.md) for quick reference.

### Traditional Conda Setup (Legacy)
The original Conda environment is still available in `code/goal_rec.yml`.

## Folder structure:
The following is the folder structure of the repository:

- **code**: contains the code 
- **models**: contains a model for each domain
- **supplementary_material**: contains the supplementary material
- **testsets**: contains the test sets used in our experiments

## Citing our work
If you use this code, please cite the following paper:

[Goal Recognition as a Deep Learning Task: the GRNet Approach (ICAPS-23)]()

Bibtex 

```
@inproceedings{chiari2023,
  author    = {Mattia Chiari and
               Alfonso E. Gerevini and
               Francesco Percassi and
               Luca Putelli and
               Matteo Olivato and
               Ivan Serina},
  editor    = { 
              },
  title     = {Goal Recognition as a Deep Learning Task: the GRNet Approach},
  booktitle = {},
  pages     = {},
  publisher = {},
  year      = {},
  url       = {},
  timestamp = {},
  biburl    = {},
  bibsource = {}
}
```
