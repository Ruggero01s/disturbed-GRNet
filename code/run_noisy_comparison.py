#!/usr/bin/env python3
"""
Script to run goal recognition experiments with different noise levels.
Compares performance across clean and noisy observations (10%, 20%, 30% noise).
"""

import numpy as np
from tensorflow.keras.models import load_model
from os.path import join
import pickle
import time
import os
import argparse
import pandas as pd
from datetime import datetime
import tensorflow as tf
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

# Configure TensorFlow to limit memory growth
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
    except RuntimeError as e:
        print(f"GPU memory growth setting error: {e}")
import json
from typing import Union
import gc
from keras import backend as K
import psutil

# Import all required functions from the notebook
from GRNet_approach_functions import (
    C, AttentionWeights, ContextVector,
    parse_domain, get_model, get_domain_related,
    unzip_file, unpack_bz2,
    load_file, parse_file,
    get_observations_array, get_predictions,
    get_scores, get_max, get_result, get_correct_goal_idx,
    load_mask_file, apply_mask, get_mask_path
)


def run_experiment(obs_file: str, 
            goals_dict_file: Union[str, None],
            actions_dict_file: Union[str, None],
            possible_goals_file: str, 
            correct_goal_file: str, 
            domain: Union[str, int], 
            verbose: int = 0,
            mask_data: Union[dict, None] = None,
            problem_file: Union[str, None] = None) -> list:
    """Run a single goal recognition experiment."""
    
    domain = parse_domain(domain)
    if goals_dict_file is None:
        goals_dict_file = join(get_domain_related(domain, C.DICTIONARIES_DICT), 'dizionario_goal')
    goals_dict = load_file(goals_dict_file, binary=True, use_pickle=True)
    if actions_dict_file is None:
        actions_dict_file = join(get_domain_related(domain, C.DICTIONARIES_DICT), 'dizionario')
    actions_dict = load_file(actions_dict_file, binary=True, use_pickle=True)
    observations = parse_file(obs_file, C.OBSERVATIONS, actions_dict)
    
    # Apply mask if provided
    if mask_data is not None and problem_file is not None:
        observations = apply_mask(observations, problem_file, mask_data)
        if verbose > 1:
            print(f'Applied noisy mask for {problem_file}')
    
    if verbose > 1:
        print('Observed actions:\n')
        for o in observations:
            print(o)
    possible_goals = parse_file(possible_goals_file, C.POSSIBLE_GOALS, goals_dict)
    
    max_plan_length = get_domain_related(domain, C.MAX_PLAN_LENGTH)
    predictions = get_predictions(observations, max_plan_length, domain)
    scores = get_scores(predictions, possible_goals)
    
    correct_goal = parse_file(correct_goal_file, C.CORRECT_GOAL, goals_dict) 
    correct_goal_idx = get_correct_goal_idx(correct_goal, possible_goals)
    result = get_result(scores, correct_goal_idx)
    
    return [result, correct_goal_idx, get_max(scores)[0]]


def get_memory_usage() -> str:
    """Get current memory usage as a formatted string."""
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    mem_mb = mem_info.rss / 1024 / 1024
    return f"{mem_mb:.1f} MB"


def load_single_model(domain: int, model_type: int, percentage: float) -> None:
    """Load only the model for a specific domain."""
    model_file = get_domain_related(domain, C.MODEL_FILE, model_type=model_type, percentage=percentage)
    model = load_model(join(C.MODELS_DIR, model_file), custom_objects=C.CUSTOM_OBJECTS)
    
    # Set the appropriate model in C constants
    if domain == C.LOGISTICS:
        C.MODEL_LOGISTICS = model
    elif domain == C.SATELLITE:
        C.MODEL_SATELLITE = model
    elif domain == C.ZENOTRAVEL:
        C.MODEL_ZENOTRAVEL = model
    elif domain == C.DEPOTS:
        C.MODEL_DEPOTS = model
    elif domain == C.DRIVERLOG:
        C.MODEL_DRIVERLOG = model
    elif domain == C.BLOCKSWORLD:
        C.MODEL_BLOCKSWORLS = model
    
    print(f'✓ Loaded model for domain {get_domain_related(domain, C.MODEL_FILE).split("_")[0]} (Memory: {get_memory_usage()})')


def unload_models() -> None:
    """Unload all models and clear memory."""
    mem_before = get_memory_usage()
    
    # Clear model references
    C.MODEL_LOGISTICS = None
    C.MODEL_SATELLITE = None
    C.MODEL_ZENOTRAVEL = None
    C.MODEL_DEPOTS = None
    C.MODEL_DRIVERLOG = None
    C.MODEL_BLOCKSWORLS = None
    
    # Clear Keras/TensorFlow session
    K.clear_session()
    
    # Force garbage collection
    gc.collect()
    
    mem_after = get_memory_usage()
    print(f'✓ Models unloaded and memory cleared (Before: {mem_before} → After: {mem_after})')


def run_comparison(domain: int, domain_dir: str, source_dir: str, 
                   noise_levels: list, observation_percentages: list,
                   output_dir: str = '.'):
    """
    Run comprehensive comparison across different noise levels and observation percentages.
    
    Args:
        domain: Domain constant (e.g., C.BLOCKSWORLD)
        domain_dir: Path to domain data directory
        source_dir: Temporary directory for unpacking files
        noise_levels: List of noise levels to test (e.g., [0, 10, 20, 30])
        observation_percentages: List of observation percentages (e.g., [0.1, 0.3, 0.5, 0.7, 1.0])
        output_dir: Directory to save output CSV files
    """
    
    comparison_results = {}
    detailed_results = []
    
    for noise in noise_levels:
        print(f'\n{"="*60}')
        print(f'Testing with {noise}% noise')
        print(f'{"="*60}\n')
        
        use_noisy_masks = (noise > 0)
        noise_level = noise if noise > 0 else 10
        
        for perc in observation_percentages:
            plans_dir = f'{join(domain_dir, str(int(perc*100)))}'
            
            if not os.path.exists(plans_dir):
                print(f'Warning: Directory {plans_dir} does not exist, skipping...')
                continue
                
            files = os.listdir(plans_dir)
            
            print(f'\nProcessing {len(files)} files at {int(perc*100)}% observations...')
            
            # Load mask data if using noisy masks
            mask_data = None
            skip_problems = False
            if use_noisy_masks:
                try:
                    mask_file_path = get_mask_path(domain, str(int(perc*100)), noise_level)
                    mask_data = load_mask_file(mask_file_path)
                    print(f'Loaded mask file: {mask_file_path}')
                except FileNotFoundError:
                    print(f'⚠ Warning: Mask file not found. Skipping this noise level for {int(perc*100)}% observations.')
                    skip_problems = True
            
            # Skip this percentage if masks are needed but not found
            if skip_problems:
                continue
            
            correct = 0
            total = 0
            skipped = 0
            
            for idx, f in enumerate(files):
                if (idx + 1) % 100 == 0:
                    print(f'  Processed {idx + 1}/{len(files)} files...')
                    # Periodic garbage collection to prevent memory buildup
                    gc.collect()
                    
                if f.endswith('.zip'):
                    unzip_file(join(plans_dir, f), source_dir)
                elif f.endswith('.bz2'):
                    unpack_bz2(join(plans_dir, f), source_dir)
                else:
                    continue
                
                start_time = time.time()
                
                try:
                    result = run_experiment(
                        obs_file=join(source_dir, 'obs.dat'),
                        goals_dict_file=None,
                        actions_dict_file=None,
                        possible_goals_file=join(source_dir, 'hyps.dat'),
                        correct_goal_file=join(source_dir, 'real_hyp.dat'),
                        domain=domain,
                        verbose=0,
                        mask_data=mask_data,
                        problem_file=f
                    )
                    
                    exec_time = time.time() - start_time
                    
                    # Store detailed results
                    detailed_results.append({
                        'noise_level': noise,
                        'observation_percentage': int(perc*100),
                        'problem_file': f,
                        'correct_prediction': result[0],
                        'correct_goal_idx': result[1],
                        'predicted_goal_idx': result[2],
                        'execution_time': exec_time
                    })
                    
                    if result[0]:
                        correct += 1
                    total += 1
                    
                except KeyError:
                    # Problem not found in mask file - skip it
                    skipped += 1
                    if (idx + 1) % 100 == 0:
                        print(f'  (Skipped {skipped} problems not in mask file)')
                    continue
                except Exception as e:
                    print(f'  Error processing {f}: {e}')
                    continue
            
            accuracy = (correct / total) * 100 if total > 0 else 0
            comparison_results[f'{noise}% noise - {int(perc*100)}% obs'] = accuracy
            
            if skipped > 0:
                print(f'  ✓ Accuracy at {int(perc*100)}% observations: {accuracy:.2f}% ({correct}/{total}) [skipped {skipped} problems]')
            else:
                print(f'  ✓ Accuracy at {int(perc*100)}% observations: {accuracy:.2f}% ({correct}/{total})')
        
        overall_accuracy = (sum([r['correct_prediction'] for r in detailed_results if r['noise_level'] == noise]) / 
                           len([r for r in detailed_results if r['noise_level'] == noise])) * 100
        print(f'\n  Overall accuracy with {noise}% noise: {overall_accuracy:.2f}%')
        
        # Force garbage collection after each noise level
        gc.collect()
    
    # Save results
    save_results(detailed_results, noise_levels, domain, output_dir)
    
    return detailed_results


def save_results(detailed_results: list, noise_levels: list, domain: int, output_dir: str):
    """Save results to CSV files."""
    
    # Create DataFrame
    df_detailed = pd.DataFrame(detailed_results)
    
    # Create summary by noise level
    summary_data = []
    for noise in noise_levels:
        noise_results = [r for r in detailed_results if r['noise_level'] == noise]
        if noise_results:
            summary_data.append({
                'noise_level': noise,
                'total_problems': len(noise_results),
                'correct_predictions': sum([r['correct_prediction'] for r in noise_results]),
                'accuracy': (sum([r['correct_prediction'] for r in noise_results]) / len(noise_results)) * 100,
                'avg_execution_time': np.mean([r['execution_time'] for r in noise_results])
            })
    
    df_summary = pd.DataFrame(summary_data)
    
    # Create summary by noise level AND observation percentage
    summary_by_perc_data = []
    for noise in noise_levels:
        for perc in [10, 30, 50, 70, 100]:
            perc_results = [r for r in detailed_results if r['noise_level'] == noise and r['observation_percentage'] == perc]
            if perc_results:
                summary_by_perc_data.append({
                    'noise_level': noise,
                    'observation_percentage': perc,
                    'total_problems': len(perc_results),
                    'correct_predictions': sum([r['correct_prediction'] for r in perc_results]),
                    'accuracy': (sum([r['correct_prediction'] for r in perc_results]) / len(perc_results)) * 100,
                    'avg_execution_time': np.mean([r['execution_time'] for r in perc_results])
                })
    
    df_summary_by_perc = pd.DataFrame(summary_by_perc_data)
    
    # Generate filenames
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    domain_name = get_domain_related(domain, C.MODEL_FILE).split('_')[0]
    
    detailed_filename = join(output_dir, f'results_{domain_name}_detailed_{timestamp}.csv')
    summary_filename = join(output_dir, f'results_{domain_name}_summary_{timestamp}.csv')
    summary_by_perc_filename = join(output_dir, f'results_{domain_name}_summary_by_perc_{timestamp}.csv')
    
    # Save files
    df_detailed.to_csv(detailed_filename, index=False)
    df_summary.to_csv(summary_filename, index=False)
    df_summary_by_perc.to_csv(summary_by_perc_filename, index=False)
    
    print(f'\n{"="*60}')
    print(f'RESULTS SAVED')
    print(f'{"="*60}')
    print(f'✓ Detailed results: {detailed_filename}')
    print(f'✓ Summary by noise level: {summary_filename}')
    print(f'✓ Summary by noise & obs %: {summary_by_perc_filename}')
    
    # Display summary
    print(f'\n{"="*60}')
    print('SUMMARY BY NOISE LEVEL')
    print(f'{"="*60}')
    print(df_summary.to_string(index=False))
    
    print(f'\n{"="*60}')
    print('SUMMARY BY NOISE LEVEL AND OBSERVATION PERCENTAGE')
    print(f'{"="*60}')
    print(df_summary_by_perc.to_string(index=False))


def main():
    parser = argparse.ArgumentParser(
        description='Run goal recognition experiments with noisy observations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run on blocksworld with default settings
  python run_noisy_comparison.py --domains blocksworld
  
  # Run on multiple domains
  python run_noisy_comparison.py --domains blocksworld logistics satellite
  
  # Run on ALL domains
  python run_noisy_comparison.py --domains all
  
  # Run on logistics with custom noise levels
  python run_noisy_comparison.py --domains logistics --noise-levels 0 10 20
  
  # Run multiple domains with specific observation percentages
  python run_noisy_comparison.py --domains blocksworld depots --obs-percentages 10 30 50
  
  # Specify custom data directory and output location
  python run_noisy_comparison.py --domains depots --data-dir ../data --output-dir ./results
        """
    )
    
    parser.add_argument('--domains', type=str, nargs='+', required=True,
                        choices=['blocksworld', 'logistics', 'satellite', 'zenotravel', 'driverlog', 'depots', 'all'],
                        help='Domain(s) to test. Use "all" to test all domains')
    
    parser.add_argument('--data-dir', type=str, default=None,
                        help='Path to base data directory (default: ../data). Each domain will use ../data/<domain>')
    
    parser.add_argument('--output-dir', type=str, default='.',
                        help='Directory to save output CSV files (default: current directory)')
    
    parser.add_argument('--noise-levels', type=int, nargs='+', default=[0, 5, 10, 15, 20, 30],
                        help='Noise levels to test (default: 0 5 10 15 20 30)')
    
    parser.add_argument('--obs-percentages', type=int, nargs='+', default=[10, 30, 50, 70, 100],
                        help='Observation percentages to test (default: 10 30 50 70 100)')
    
    parser.add_argument('--source-dir', type=str, default='./tmp',
                        help='Temporary directory for unpacking files (default: ./tmp)')
    
    parser.add_argument('--model-type', type=str, default='small',
                        choices=['small', 'complete'],
                        help='Model type to use (default: small)')
    
    args = parser.parse_args()
    
    # Handle "all" domains
    if 'all' in args.domains:
        domains_to_test = ['blocksworld', 'logistics', 'satellite', 'zenotravel', 'driverlog', 'depots']
    else:
        domains_to_test = args.domains
    
    # Set base data directory
    if args.data_dir is None:
        base_data_dir = '../data'
    else:
        base_data_dir = args.data_dir
    
    # Create output directory if needed
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Create source directory if needed
    os.makedirs(args.source_dir, exist_ok=True)
    
    print(f'{"="*60}')
    print(f'NOISY GOAL RECOGNITION COMPARISON')
    print(f'{"="*60}')
    print(f'Domains: {", ".join(domains_to_test)}')
    print(f'Base data directory: {base_data_dir}')
    print(f'Output directory: {args.output_dir}')
    print(f'Noise levels: {args.noise_levels}')
    print(f'Observation percentages: {args.obs_percentages}%')
    print(f'Model type: {args.model_type}')
    
    # Determine model type
    model_type = C.SMALL if args.model_type == 'small' else C.COMPLETE
    
    # Convert percentages to decimals
    obs_percentages = [p / 100.0 for p in args.obs_percentages]
    
    # Run comparison for each domain (load models one at a time to save memory)
    overall_start_time = time.time()
    failed_domains = []
    
    for idx, domain_name in enumerate(domains_to_test):
        print(f'\n\n{"#"*60}')
        print(f'# DOMAIN {idx+1}/{len(domains_to_test)}: {domain_name.upper()}')
        print(f'{"#"*60}\n')
        
        try:
            # Parse domain
            domain = parse_domain(domain_name)
            
            # Set domain-specific data directory
            domain_dir = join(base_data_dir, domain_name)
            
            # Verify directory exists
            if not os.path.exists(domain_dir):
                print(f'⚠ Warning: Data directory {domain_dir} does not exist, skipping {domain_name}...')
                failed_domains.append(domain_name)
                continue
            
            # Load only the model for this domain
            print(f'\n{"="*60}')
            print(f'LOADING MODEL FOR {domain_name.upper()}')
            print(f'{"="*60}')
            load_single_model(domain=domain, model_type=model_type, percentage=0)
            
            # Run comparison
            start_time = time.time()
            run_comparison(
                domain=domain,
                domain_dir=domain_dir,
                source_dir=args.source_dir,
                noise_levels=args.noise_levels,
                observation_percentages=obs_percentages,
                output_dir=args.output_dir
            )
            
            elapsed_time = time.time() - start_time
            print(f'\n✓ {domain_name} completed in {elapsed_time:.2f} seconds (Memory: {get_memory_usage()})')
            
            # Unload model to free memory before next domain
            print(f'\nUnloading {domain_name} model to free memory...')
            unload_models()
            
        except Exception as e:
            print(f'\n✗ Error processing {domain_name}: {e}')
            import traceback
            traceback.print_exc()
            failed_domains.append(domain_name)
            # Still try to unload models even on error
            try:
                unload_models()
            except:
                pass
            continue
    
    # Final summary
    total_time = time.time() - overall_start_time
    print(f'\n\n{"="*60}')
    print(f'ALL EXPERIMENTS COMPLETED')
    print(f'{"="*60}')
    print(f'Total time: {total_time:.2f} seconds')
    print(f'Successful domains: {len(domains_to_test) - len(failed_domains)}/{len(domains_to_test)}')
    
    if failed_domains:
        print(f'Failed domains: {", ".join(failed_domains)}')
    
    print(f'\nResults saved to: {args.output_dir}')
    print(f'{"="*60}')
    
    return 0 if len(failed_domains) == 0 else 1


if __name__ == '__main__':
    exit(main())
