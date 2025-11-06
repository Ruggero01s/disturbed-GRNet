#!/usr/bin/env python3
"""Test the full pipeline with zenotravel to see the actual error."""

import sys
sys.path.insert(0, '/home/ruggero.signoroni/disturbed-GRNet/adversarial_gen/code')

from up_utils import *
from unified_planning.shortcuts import *
import os

# Test file
test_zip = '/home/ruggero.signoroni/disturbed-GRNet/data/zenotravel/10/zenotravel_p000001_hyp=hyp-8_10.zip'
tmp_dir = '/tmp/test_zeno_full'
grounder_name = "fast-downward-reachability-grounder"

# Clean and create tmp dir
os.system(f'rm -rf {tmp_dir}')
os.system(f'mkdir -p {tmp_dir}')

print("Testing full zenotravel pipeline...")
print("=" * 60)

try:
    # Step 1: Open compressed file
    print("\n1. Opening compressed file...")
    open_compressed_file(test_zip, tmp_dir)
    print("   ✓ File extracted")
    
    # Step 2: Get observations
    print("\n2. Getting observations...")
    observations = get_observations(tmp_dir)
    print(f"   ✓ Found {len(observations)} observations")
    print(f"   Observations: {observations}")
    
    # Step 3: Get goals
    print("\n3. Getting goals...")
    is_pereira = test_zip.endswith('.tar.bz2')
    goals = get_goals(tmp_dir, is_pereira)
    print(f"   ✓ Found {len(goals)} goal hypotheses")
    
    # Step 4: Get real goal
    print("\n4. Getting real goal...")
    real_goal = get_real_goal(tmp_dir, is_pereira)
    print(f"   ✓ Real goal has {len(real_goal)} predicates")
    
    # Step 5: Get init state
    print("\n5. Getting init state...")
    from main import get_init_state_safe
    init_state = get_init_state_safe(tmp_dir)
    print(f"   ✓ Init state has {len(init_state)} predicates")
    if init_state:
        print(f"   First 3: {init_state[:3]}")
    
    # Step 6: Get grounded actions (this is where it might fail)
    print("\n6. Getting grounded actions...")
    grounder = Compiler(name=grounder_name)
    valid_actions = get_grounded_actions(tmp_dir, grounder, is_pereira)
    print(f"   ✓ Found {len(valid_actions)} valid actions")
    print(f"   First 3 actions: {valid_actions[:3]}")
    
    print("\n" + "=" * 60)
    print("✓ All steps passed!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Cleanup
os.system(f'rm -rf {tmp_dir}')
