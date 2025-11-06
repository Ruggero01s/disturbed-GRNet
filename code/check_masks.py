#!/usr/bin/env python3
"""
Script to verify that all problem files have corresponding masks for all noise levels.
Checks that for every problem in the data directories, there exists a mask entry
in the 10%, 20%, and 30% mask files.
"""

import os
import json
from os.path import join
from typing import Dict, List, Tuple

# Configuration
DOMAINS = ['blocksworld', 'logistics', 'satellite', 'zenotravel', 'driverlog', 'depots']
OBSERVATION_PERCENTAGES = [10, 30, 50, 70, 100]
NOISE_LEVELS = [10, 20, 30]
BASE_DATA_DIR = '../data'
MASK_BASE_DIR = '../data/validator_testset/noisy_masks'


def load_mask_file(mask_path: str) -> Dict:
    """Load a mask JSON file."""
    try:
        with open(mask_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as e:
        print(f"  ⚠ Error parsing {mask_path}: {e}")
        return None


def get_problem_files(domain_dir: str, obs_perc: int) -> List[str]:
    """Get list of problem files for a domain and observation percentage."""
    plans_dir = join(domain_dir, str(obs_perc))
    
    if not os.path.exists(plans_dir):
        return []
    
    files = os.listdir(plans_dir)
    return [f for f in files if f.endswith('.zip') or f.endswith('.tar.bz2')]


def check_domain(domain: str) -> Tuple[bool, Dict]:
    """
    Check if all problems have masks for all noise levels.
    
    Returns:
        Tuple of (all_ok, report) where report contains detailed information
    """
    print(f"\n{'='*60}")
    print(f"Checking domain: {domain.upper()}")
    print(f"{'='*60}")
    
    domain_dir = join(BASE_DATA_DIR, domain)
    mask_domain_dir = join(MASK_BASE_DIR, domain)
    
    all_ok = True
    report = {
        'domain': domain,
        'observation_percentages': {}
    }
    
    for obs_perc in OBSERVATION_PERCENTAGES:
        print(f"\n--- {obs_perc}% observations ---")
        
        # Get all problem files
        problem_files = get_problem_files(domain_dir, obs_perc)
        
        if not problem_files:
            print(f"  ⚠ No problem files found in {join(domain_dir, str(obs_perc))}")
            report['observation_percentages'][obs_perc] = {
                'status': 'no_problems',
                'problem_count': 0
            }
            continue
        
        print(f"  Found {len(problem_files)} problem files")
        
        obs_report = {
            'problem_count': len(problem_files),
            'noise_levels': {}
        }
        
        # Check each noise level
        for noise in NOISE_LEVELS:
            mask_file = join(mask_domain_dir, str(obs_perc), f'{noise}_mask.json')
            
            # Load mask file
            mask_data = load_mask_file(mask_file)
            
            if mask_data is None:
                print(f"  ✗ {noise}% mask file NOT FOUND: {mask_file}")
                obs_report['noise_levels'][noise] = {
                    'status': 'missing_file',
                    'missing_problems': problem_files
                }
                all_ok = False
                continue
            
            # Check which problems are missing from mask
            missing_problems = []
            for problem_file in problem_files:
                if problem_file not in mask_data:
                    missing_problems.append(problem_file)
            
            if missing_problems:
                print(f"  ✗ {noise}% mask: {len(missing_problems)} problems missing")
                print(f"    First 5 missing: {missing_problems[:5]}")
                obs_report['noise_levels'][noise] = {
                    'status': 'incomplete',
                    'problems_in_mask': len(mask_data),
                    'missing_count': len(missing_problems),
                    'missing_problems': missing_problems
                }
                all_ok = False
            else:
                print(f"  ✓ {noise}% mask: All {len(problem_files)} problems present")
                obs_report['noise_levels'][noise] = {
                    'status': 'complete',
                    'problems_in_mask': len(mask_data)
                }
        
        report['observation_percentages'][obs_perc] = obs_report
    
    return all_ok, report


def main():
    """Main function to check all domains."""
    print('='*60)
    print('MASK VERIFICATION TOOL')
    print('='*60)
    print(f'Domains: {", ".join(DOMAINS)}')
    print(f'Observation percentages: {OBSERVATION_PERCENTAGES}')
    print(f'Noise levels: {NOISE_LEVELS}')
    print(f'Data directory: {BASE_DATA_DIR}')
    print(f'Mask directory: {MASK_BASE_DIR}')
    
    all_reports = {}
    domains_ok = []
    domains_issues = []
    
    # Check each domain
    for domain in DOMAINS:
        try:
            ok, report = check_domain(domain)
            all_reports[domain] = report
            
            if ok:
                domains_ok.append(domain)
            else:
                domains_issues.append(domain)
                
        except Exception as e:
            print(f"\n✗ Error checking {domain}: {e}")
            domains_issues.append(domain)
            continue
    
    # Final summary
    print(f"\n\n{'='*60}")
    print('FINAL SUMMARY')
    print(f"{'='*60}")
    print(f"✓ Domains OK: {len(domains_ok)}/{len(DOMAINS)}")
    if domains_ok:
        print(f"  {', '.join(domains_ok)}")
    
    print(f"\n✗ Domains with issues: {len(domains_issues)}/{len(DOMAINS)}")
    if domains_issues:
        print(f"  {', '.join(domains_issues)}")
    
    # Save detailed report
    report_file = 'mask_verification_report.json'
    with open(report_file, 'w') as f:
        json.dump(all_reports, f, indent=2)
    print(f"\n📄 Detailed report saved to: {report_file}")
    
    # Exit with appropriate code
    if domains_issues:
        print(f"\n⚠ Verification FAILED - some masks are missing or incomplete")
        return 1
    else:
        print(f"\n✓ Verification PASSED - all masks are present and complete")
        return 0


if __name__ == '__main__':
    exit(main())
