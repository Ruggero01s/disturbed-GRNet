# Multi-Domain Support - Quick Reference

## New Feature: Run Multiple Domains at Once!

The script now supports running experiments on multiple domains in a single command.

## Quick Examples

### Run a single domain
```bash
python run_noisy_comparison.py --domains blocksworld
```

### Run multiple specific domains
```bash
python run_noisy_comparison.py --domains blocksworld logistics satellite
```

### Run ALL domains (blocksworld, logistics, satellite, zenotravel, driverlog, depots)
```bash
python run_noisy_comparison.py --domains all
```

## What Changed?

- **`--domain`** → **`--domains`** (now accepts multiple values)
- **`--data-dir`** now refers to the **base** data directory (e.g., `../data`)
  - Each domain will automatically use `<base_data_dir>/<domain_name>`
- New option: **`--domains all`** to run all 6 domains at once

## Output

When running multiple domains:
- Each domain gets its own set of 3 CSV files (detailed, summary, summary_by_perc)
- Progress is shown for each domain
- Final summary shows which domains succeeded/failed
- Total execution time across all domains

Example output structure:
```
results_blocksworld_detailed_20251105_143022.csv
results_blocksworld_summary_20251105_143022.csv
results_blocksworld_summary_by_perc_20251105_143022.csv
results_logistics_detailed_20251105_143025.csv
results_logistics_summary_20251105_143025.csv
results_logistics_summary_by_perc_20251105_143025.csv
...
```

## Performance Tips

For faster testing when running multiple domains:
- Use fewer observation percentages: `--obs-percentages 10 100`
- Use fewer noise levels: `--noise-levels 0 10`
- Test on a subset of domains first before running all

## Example Workflow

```bash
# 1. Quick sanity check on one domain
python run_noisy_comparison.py --domains blocksworld --obs-percentages 10 100 --noise-levels 0 10

# 2. If successful, run on all domains with full settings
python run_noisy_comparison.py --domains all --output-dir ./full_experiment_results

# 3. Or run specific domains you care about
python run_noisy_comparison.py --domains blocksworld logistics depots
```
