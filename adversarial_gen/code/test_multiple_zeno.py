#!/usr/bin/env python3
"""Test multiple zenotravel files to ensure robustness."""

import sys
sys.path.insert(0, '/home/ruggero.signoroni/disturbed-GRNet/adversarial_gen/code')

from up_utils import *
from unified_planning.shortcuts import *
import os

test_files = [
    '/home/ruggero.signoroni/disturbed-GRNet/data/zenotravel/10/zenotravel_p000001_hyp=hyp-8_10.zip',
    '/home/ruggero.signoroni/disturbed-GRNet/data/zenotravel/30/zenotravel_p000001_hyp=hyp-8_30.zip',
    '/home/ruggero.signoroni/disturbed-GRNet/data/zenotravel/50/zenotravel_p000001_hyp=hyp-8_50.zip',
]

tmp_dir = '/tmp/test_zeno_multi'
grounder_name = "fast-downward-reachability-grounder"
grounder = Compiler(name=grounder_name)

print("Testing multiple zenotravel files...")
print("=" * 60)

passed = 0
failed = 0

for test_file in test_files:
    file_name = os.path.basename(test_file)
    print(f"\nTesting: {file_name}")
    
    # Clean tmp dir
    os.system(f'rm -rf {tmp_dir}')
    os.system(f'mkdir -p {tmp_dir}')
    
    try:
        # Extract
        open_compressed_file(test_file, tmp_dir)
        
        # Get data
        observations = get_observations(tmp_dir)
        goals = get_goals(tmp_dir, False)
        real_goal = get_real_goal(tmp_dir, False)
        from main import get_init_state_safe
        init_state = get_init_state_safe(tmp_dir)
        
        # Get grounded actions (the critical step)
        valid_actions = get_grounded_actions(tmp_dir, grounder, False)
        
        print(f"  ✓ Success: {len(observations)} obs, {len(goals)} goals, {len(valid_actions)} actions")
        passed += 1
        
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        failed += 1

# Cleanup
os.system(f'rm -rf {tmp_dir}')

print("\n" + "=" * 60)
print(f"Results: {passed} passed, {failed} failed")
print("=" * 60)

sys.exit(0 if failed == 0 else 1)
