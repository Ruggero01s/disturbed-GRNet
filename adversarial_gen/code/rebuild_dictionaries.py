"""
Script to rebuild dictionaries for all domains.

This script scans all plan files in each domain and extracts:
- dizionario: all unique actions (observations)
- dizionario_goal: all unique goal predicates

The dictionaries are saved as pickle files in the dictionaries directory.
"""

import os
import pickle
import tempfile
from tqdm import tqdm
from up_utils import *
from unified_planning.shortcuts import *

# Constants
BASE_PATH = 'adversarial_gen'
DATA_DIR = f'{BASE_PATH}/data'
DICTIONARIES_DIR = f'{DATA_DIR}/dictionaries'
GROUNDER_NAME = "fast-downward-reachability-grounder"

DOMAINS = ['blocksworld', 'logistics', 'driverlog', 'satellite', 'depots', 'zenotravel']
HOLE_PERCENTAGES = [10, 30, 50, 70, 100]


def extract_all_actions_and_goals(domain: str):
    """
    Extract all unique actions and goal predicates from all plan files in a domain.
    
    Args:
        domain: Name of the domain (e.g., 'blocksworld')
    
    Returns:
        Tuple of (all_actions, all_goal_predicates)
    """
    all_actions = set()
    all_goal_predicates = set()
    
    # Initialize grounder
    grounder = Compiler(name=GROUNDER_NAME)
    
    # Create temporary directory for extraction
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Iterate through all hole percentages
        # for hole_perc in HOLE_PERCENTAGES:
        for hole_perc in [100]: # has all actions

            plans_path = f'{DATA_DIR}/{domain}/{hole_perc}'
            
            if not os.path.exists(plans_path):
                print(f'  Skipping {plans_path} (does not exist)')
                continue
            
            # Get all plan files
            plan_files = [f for f in os.listdir(plans_path) 
                         if f.endswith('.zip') or f.endswith('.tar.bz2')]
            
            print(f'  Processing {len(plan_files)} files from {hole_perc}% directory...')
            
            for plan_name in tqdm(plan_files, desc=f'  {hole_perc}%'):
                try:
                    # Determine if it's a Pereira dataset
                    is_pereira = plan_name.endswith('.tar.bz2')
                    
                    # Extract the problem
                    problem_dir = os.path.join(plans_path, plan_name)
                    open_compressed_file(problem_dir, tmp_dir)
                    
                    # Extract observations (actions) - with error handling
                    try:
                        observations = get_observations(tmp_dir)
                        for obs in observations:
                            # Skip empty observations
                            if obs and obs.strip():
                                all_actions.add(obs.strip().upper())
                    except Exception as e:
                        print(f'\n    Error getting observations from {plan_name}: {str(e)}')
                    
                    # Extract grounded actions - with error handling
                    # Note: This step is optional - observations alone are sufficient
                    try:
                        grounded_actions = get_grounded_actions(tmp_dir, grounder, is_pereira)
                        for action in grounded_actions:
                            # Skip empty actions
                            if action and action.strip():
                                all_actions.add(action.strip().upper())
                    except Exception as e:
                        # Grounded actions are optional, so we just skip on error
                        pass
                    
                    # Extract goal predicates from all goals - with error handling
                    try:
                        goals = get_goals(tmp_dir, is_pereira)
                        for goal in goals:
                            for predicate in goal:
                                # Skip empty predicates
                                if predicate and predicate.strip():
                                    all_goal_predicates.add(predicate.strip().upper())
                    except Exception as e:
                        print(f'\n    Error getting goals from {plan_name}: {str(e)}')
                    
                    # Extract real goal predicates - with error handling
                    try:
                        real_goal = get_real_goal(tmp_dir, is_pereira)
                        for predicate in real_goal:
                            # Skip empty predicates
                            if predicate and predicate.strip():
                                all_goal_predicates.add(predicate.strip().upper())
                    except Exception as e:
                        print(f'\n    Error getting real goal from {plan_name}: {str(e)}')
                    
                    # Skip init state extraction - not needed for dictionary building , gives error for different formats
                    # Relevant predicate appear in goals
                    # Only goal predicates and hypothesis predicates are needed
                        
                except Exception as e:
                    print(f'\n    Error processing {plan_name}: {str(e)}')
                    import traceback
                    traceback.print_exc()
                    continue
    
    return all_actions, all_goal_predicates


def build_dictionary(items: set) -> dict:
    """
    Build a dictionary mapping items to indices.
    
    Args:
        items: Set of unique items (actions or predicates)
    
    Returns:
        Dictionary mapping each item to a unique index
    """
    # Sort items for consistency
    sorted_items = sorted(items)
    
    # Create mapping
    dictionary = {item: idx for idx, item in enumerate(sorted_items)}
    
    return dictionary


def save_dictionary(dictionary: dict, filepath: str):
    """
    Save dictionary as a pickle file.
    
    Args:
        dictionary: Dictionary to save
        filepath: Path to save the pickle file
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'wb') as f:
        pickle.dump(dictionary, f)


def rebuild_domain_dictionaries(domain: str):
    """
    Rebuild dictionaries for a specific domain.
    
    Args:
        domain: Name of the domain
    """
    print(f'\n{"="*60}')
    print(f'Rebuilding dictionaries for: {domain.upper()}')
    print(f'{"="*60}')
    
    # Extract all actions and goal predicates
    all_actions, all_goal_predicates = extract_all_actions_and_goals(domain)
    
    print(f'\n  Found {len(all_actions)} unique actions')
    print(f'  Found {len(all_goal_predicates)} unique goal predicates')
    
    # Build dictionaries
    dizionario = build_dictionary(all_actions)
    dizionario_goal = build_dictionary(all_goal_predicates)
    
    # Save dictionaries
    dict_dir = f'{DICTIONARIES_DIR}/{domain}'
    
    dizionario_path = f'{dict_dir}/dizionario'
    save_dictionary(dizionario, dizionario_path)
    print(f'\n  Saved action dictionary to: {dizionario_path}')
    
    dizionario_goal_path = f'{dict_dir}/dizionario_goal'
    save_dictionary(dizionario_goal, dizionario_goal_path)
    print(f'  Saved goal dictionary to: {dizionario_goal_path}')
    
    # Print sample entries
    print(f'\n  Sample actions (first 5):')
    for action in sorted(all_actions)[:5]:
        print(f'    {action} -> {dizionario[action]}')
    
    print(f'\n  Sample goal predicates (first 5):')
    for predicate in sorted(all_goal_predicates)[:5]:
        print(f'    {predicate} -> {dizionario_goal[predicate]}')


def main():
    """
    Main function to rebuild dictionaries for all domains.
    """
    print('='*60)
    print('DICTIONARY REBUILDER')
    print('='*60)
    print(f'Domains: {", ".join(DOMAINS)}')
    print(f'Hole percentages: {HOLE_PERCENTAGES}')
    
    for domain in DOMAINS:
        try:
            rebuild_domain_dictionaries(domain)
        except Exception as e:
            print(f'\nERROR rebuilding {domain}: {repr(e)}')
            import traceback
            traceback.print_exc()
            continue
    
    print('\n' + '='*60)
    print('Dictionary rebuilding completed!')
    print('='*60)


if __name__ == '__main__':
    main()
