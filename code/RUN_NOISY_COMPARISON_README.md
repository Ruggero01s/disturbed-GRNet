# Noisy Goal Recognition Comparison Script

This script runs comprehensive goal recognition experiments comparing clean observations with noisy observations at different noise levels (10%, 20%, 30%).

## Files

- **`run_noisy_comparison.py`**: Main script to run experiments
- **`GRNet_approach_functions.py`**: Helper module with all core functions
- **`GRNet_approach.ipynb`**: Original notebook (still available for interactive use)

## Quick Start

### Basic Usage

Run experiments on the blocksworld domain with default settings:

```bash
python run_noisy_comparison.py --domains blocksworld
```

### Common Examples

**Test a single domain:**
```bash
python run_noisy_comparison.py --domains logistics
```

**Test multiple domains at once:**
```bash
python run_noisy_comparison.py --domains blocksworld logistics satellite
```

**Test ALL domains:**
```bash
python run_noisy_comparison.py --domains all
```

**Custom noise levels (test only 10% and 20% noise):**
```bash
python run_noisy_comparison.py --domains blocksworld --noise-levels 0 10 20
```

**Multiple domains with specific observation percentages:**
```bash
python run_noisy_comparison.py --domains blocksworld depots --obs-percentages 10 50 100
```

**Custom data and output directories:**
```bash
python run_noisy_comparison.py \
    --domains blocksworld logistics \
    --data-dir /path/to/data \
    --output-dir ./results
```

**Run all domains with minimal testing (fast):**
```bash
python run_noisy_comparison.py \
    --domains all \
    --noise-levels 0 10 \
    --obs-percentages 10 100
```

## Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--domains` | Domain(s) to test (required). Use `all` for all domains | - |
| `--data-dir` | Path to **base** data directory | `../data` |
| `--output-dir` | Directory for output CSV files | `.` (current dir) |
| `--noise-levels` | Noise levels to test (%) | `0 10 20 30` |
| `--obs-percentages` | Observation percentages to test | `10 30 50 70 100` |
| `--source-dir` | Temporary directory for unpacking | `./tmp` |
| `--model-type` | Model type (`small` or `complete`) | `small` |

## Output Files

The script generates three CSV files:

1. **`results_<domain>_detailed_<timestamp>.csv`**
   - One row per problem
   - Columns: noise_level, observation_percentage, problem_file, correct_prediction, correct_goal_idx, predicted_goal_idx, execution_time

2. **`results_<domain>_summary_<timestamp>.csv`**
   - Summary by noise level
   - Columns: noise_level, total_problems, correct_predictions, accuracy, avg_execution_time

3. **`results_<domain>_summary_by_perc_<timestamp>.csv`**
   - Summary by noise level AND observation percentage
   - Columns: noise_level, observation_percentage, total_problems, correct_predictions, accuracy, avg_execution_time

## Example Output

```
============================================================
Testing with 0% noise
============================================================

Processing 1000 files at 10% observations...
Loaded mask file: ../data/validator_testset/noisy_masks/blocksworld/10/10_mask.json
  Processed 100/1000 files...
  Processed 200/1000 files...
  ...
  ✓ Accuracy at 10% observations: 85.40% (854/1000)

Processing 1000 files at 30% observations...
  ✓ Accuracy at 30% observations: 92.30% (923/1000)

  Overall accuracy with 0% noise: 88.85%

============================================================
SUMMARY BY NOISE LEVEL
============================================================
 noise_level  total_problems  correct_predictions  accuracy  avg_execution_time
           0            5000                 4440     88.80                0.15
          10            5000                 4320     86.40                0.16
          20            5000                 4050     81.00                0.16
          30            5000                 3800     76.00                0.16
```

## Requirements

- Python 3.7+
- TensorFlow
- Keras
- NumPy
- Pandas
- All dependencies from `GRNet_approach.ipynb`

## Directory Structure

```
code/
├── run_noisy_comparison.py          # Main script
├── GRNet_approach_functions.py      # Helper functions
├── GRNet_approach.ipynb             # Original notebook
└── tmp/                             # Temporary files (auto-created)

data/
└── <domain>/
    ├── 10/                          # 10% observation files
    ├── 30/                          # 30% observation files
    ├── 50/                          # 50% observation files
    ├── 70/                          # 70% observation files
    └── 100/                         # 100% observation files

data/validator_testset/noisy_masks/
└── <domain>/
    ├── 10/
    │   ├── 10_mask.json
    │   ├── 20_mask.json
    │   └── 30_mask.json
    ├── 30/
    ├── 50/
    ├── 70/
    └── 100/

models/
├── blocksworld_small.h5
├── logistics_small.h5
└── ...
```

## Troubleshooting

**Error: Data directory does not exist**
- Check that the path to your data directory is correct
- Use `--data-dir` to specify a custom path

**Error: Mask file not found**
- The script will continue with clean observations if masks are not found
- Ensure mask files exist at `../data/validator_testset/noisy_masks/<domain>/`

**Model loading errors**
- Ensure model files exist in `../models/`
- Check that model names match the domain

## Performance Tips

- The script shows progress every 100 files
- Use fewer observation percentages for faster testing
- Test with a subset of noise levels first (e.g., `--noise-levels 0 10`)

## Help

For full help and all options:
```bash
python run_noisy_comparison.py --help
```

# ex 1
/home/ruggero.signoroni/disturbed-GRNet/.venv/bin/python run_noisy_comparison.py \
    --domains zenotravel \
    --noise-levels 0 10 20 30 \
    --obs-percentages 10 30 50 70 100 \
    --output-dir ./disturbed_results

# ex2
python run_noisy_comparison.py \
    --domains blocksworld depots driverlog \
    --noise-levels 0 10 20 30 \
    --obs-percentages 10 30 50 70 100 \
    --output-dir ./full_results