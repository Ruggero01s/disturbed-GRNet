#!/usr/bin/env python3
"""
Worker to generate masks for a given attack percentage.
This imports the existing `process_domain` from `main.py` and runs it for the configured domains
and hole percentages, but using a single attack percentage. Useful to parallelize mask creation.

Usage:
  python run_masks_worker.py --attack 10 [--domains blocksworld logistics] [--base-path ..]

The script respects the same directory structure as `main.py` (DATA_DIR etc.).
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


def run_worker(attack_percentage: int, domains: List[str] = None, hole_percentages: List[int] = None):
    # Use defaults from the original main if not provided
    if domains is None:
        domains = ag_main.DOMAINS
    if hole_percentages is None:
        hole_percentages = ag_main.HOLE_PERCENTAGES

    print(f"Worker started: attack={attack_percentage} | domains={domains} | holes={hole_percentages}")

    for domain in domains:
        try:
            print(f"\n--- Processing domain {domain} (attack {attack_percentage}%) ---")
            ag_main.process_domain(domain, hole_percentages, [attack_percentage])
            print(f"--- Done domain {domain} (attack {attack_percentage}%) ---\n")
        except Exception as e:
            print(f"Error processing domain {domain} with attack {attack_percentage}%: {e}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run mask generation for a single attack percentage')
    parser.add_argument('--attack', '-a', type=int, required=True, help='Attack percentage to apply (e.g. 10)')
    parser.add_argument('--domains', '-d', type=str, nargs='*', default=None,
                        help='Optional list of domains to process (default: all in main.py)')
    parser.add_argument('--holes', '-H', type=int, nargs='*', default=None,
                        help='Optional list of hole percentages to process (default: all in main.py)')
    args = parser.parse_args()

    run_worker(args.attack, domains=args.domains, hole_percentages=args.holes)
