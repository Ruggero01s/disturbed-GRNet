# GRNet
Deep Learning architecture for solving Goal Recognition tasks. Experiments to work with noisy data, changing a percentage of actions with random ones. 

### Setup (Windows)
```powershell
# Option 1: Automated setup
setup_uv.bat

# Option 2: Manual setup
uv venv --python 3.9
.venv\Scripts\activate
uv sync
```

📖 **See [UV_SETUP.md](UV_SETUP.md) for detailed instructions** or [UV_QUICKREF.md](UV_QUICKREF.md) for quick reference.

### Traditional Conda Setup (Legacy)
The original Conda environment is still available in `code/goal_rec.yml`.

## Folder structure:
The following is the folder structure of the repository:

- **code**: contains the code 
- **models**: contains a model for each domain
- **data**: contains the problems for the various domains
- **adversarial_gen**: contains code to generate adversarial masks for the problems

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
