#!/usr/bin/env python3
"""
Worker to generate masks for given domain(s) and attack percentage(s).
This imports the existing `process_domain` from `main.py` and runs it for the configured domains
and hole percentages. Useful to parallelize mask creation by domain.

Usage:
  python run_masks_worker.py --domains blocksworld --attacks 10 20 30 [--tmp-dir ./tmp1]

The script respects the same directory structure as `main.py` (DATA_DIR etc.).
Each worker should use a unique temp directory to avoid conflicts.
"""
import argparse
import sys
import os
from typing import List

# Ensure package imports use repository path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from adversarial_gen.code import main as ag_main


def run_worker(attack_percentages: List[int], tmp_dir: str = None, domains: List[str] = None, hole_percentages: List[int] = None):
    # Use defaults from the original main if not provided
    if domains is None:
        domains = ag_main.DOMAINS
    if hole_percentages is None:
        hole_percentages = ag_main.HOLE_PERCENTAGES
    
    # Set unique temp directory for this worker
    if tmp_dir:
        original_tmp = ag_main.TMP_DIR
        ag_main.TMP_DIR = tmp_dir
        os.makedirs(tmp_dir, exist_ok=True)
        print(f"Worker temp directory: {tmp_dir}")
    
    print(f"Worker started: attacks={attack_percentages} | domains={domains} | holes={hole_percentages}")

    for domain in domains:
        try:
            print(f"\n{'='*60}")
            print(f"Processing domain {domain.upper()}")
            print(f"Attack percentages: {attack_percentages}")
            print(f"{'='*60}")
            ag_main.process_domain(domain, hole_percentages, attack_percentages)
            print(f"\n✓ Completed domain {domain}\n")
        except Exception as e:
            print(f"\n✗ Error processing domain {domain}: {e}")
            import traceback
            traceback.print_exc()
    
    # Restore original TMP_DIR if changed
    if tmp_dir:
        ag_main.TMP_DIR = original_tmp


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run mask generation for specified domain(s) and attack percentage(s)')
    parser.add_argument('--attacks', '-a', type=int, nargs='+', required=True, 
                        help='Attack percentages to apply (e.g. 10 20 30)')
    parser.add_argument('--tmp-dir', '-t', type=str, default=None,
                        help='Unique temp directory for this worker (e.g. ./tmp1, ./tmp2)')
    parser.add_argument('--domains', '-d', type=str, nargs='*', default=None,
                        help='Optional list of domains to process (default: all in main.py)')
    parser.add_argument('--holes', '-H', type=int, nargs='*', default=None,
                        help='Optional list of hole percentages to process (default: all in main.py)')
    args = parser.parse_args()

    run_worker(args.attacks, tmp_dir=args.tmp_dir, domains=args.domains, hole_percentages=args.holes)
