#!/bin/bash
# Example script to run noisy comparison experiments

echo "============================================================"
echo "Running Noisy Goal Recognition Comparison"
echo "============================================================"
echo ""

# Example 1: Basic run on blocksworld
echo "Example 1: Running on blocksworld with default settings..."
python run_noisy_comparison.py --domains blocksworld

# Example 2: Run on multiple domains at once
# echo "Example 2: Running on multiple domains..."
# python run_noisy_comparison.py --domains blocksworld logistics satellite

# Example 3: Run ALL domains
# echo "Example 3: Running on ALL domains..."
# python run_noisy_comparison.py --domains all

# Example 4: Quick test with fewer percentages
# echo "Example 4: Quick test with only 10% and 100% observations..."
# python run_noisy_comparison.py \
#     --domains blocksworld depots \
#     --obs-percentages 10 100 \
#     --output-dir ./quick_test_results

# Example 5: Test only specific noise levels on all domains
# echo "Example 5: Testing only 0% (clean) and 10% noise on all domains..."
# python run_noisy_comparison.py \
#     --domains all \
#     --noise-levels 0 10 \
#     --output-dir ./partial_noise_results

echo ""
echo "============================================================"
echo "Experiments completed!"
echo "Check the generated CSV files for results."
echo "============================================================"
