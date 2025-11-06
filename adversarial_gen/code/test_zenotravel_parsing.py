#!/usr/bin/env python3
"""Quick test to verify zenotravel parsing works correctly."""

import sys
sys.path.insert(0, '/home/ruggero.signoroni/disturbed-GRNet/adversarial_gen/code')

from up_utils import get_goals, get_real_goal, get_observations
import os

# Extract a test file
test_zip = '/home/ruggero.signoroni/disturbed-GRNet/data/zenotravel/10/zenotravel_p000001_hyp=hyp-8_10.zip'
tmp_dir = '/tmp/test_zenotravel'

# Clean and create tmp dir
os.system(f'rm -rf {tmp_dir}')
os.system(f'mkdir -p {tmp_dir}')
os.system(f'unzip -q {test_zip} -d {tmp_dir}')

print("Testing zenotravel parsing...")
print("=" * 60)

try:
    # Test observations
    print("\n1. Testing get_observations()...")
    obs = get_observations(tmp_dir)
    print(f"   ✓ Found {len(obs)} observations")
    print(f"   First observation: {obs[0]}")
    
    # Test goals
    print("\n2. Testing get_goals()...")
    goals = get_goals(tmp_dir, pereira=False)
    print(f"   ✓ Found {len(goals)} goal hypotheses")
    print(f"   First goal has {len(goals[0])} predicates")
    print(f"   First 3 predicates: {goals[0][:3]}")
    
    # Test real goal
    print("\n3. Testing get_real_goal()...")
    real_goal = get_real_goal(tmp_dir, pereira=False)
    print(f"   ✓ Real goal has {len(real_goal)} predicates")
    print(f"   First 3 predicates: {real_goal[:3]}")
    
    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Cleanup
os.system(f'rm -rf {tmp_dir}')
