#!/usr/bin/env python3
"""
Script to generate comprehensive plots from goal recognition experiment results.
Reads CSV files from the results directory and creates visualization plots.

Usage:
    python plot_results.py --results-dir ./disturbed_results_last_actions
"""

import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np
from datetime import datetime

# Set style for better-looking plots
sns.set_style("whitegrid")
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10


def load_results(results_dir: str) -> dict:
    """
    Load all summary_by_perc CSV files from the results directory.
    
    Returns:
        Dictionary mapping domain names to their DataFrames
    """
    results = {}
    results_path = Path(results_dir)
    
    if not results_path.exists():
        print(f"Error: Results directory {results_dir} does not exist")
        return results
    
    # Find all summary_by_perc CSV files
    csv_files = list(results_path.glob("*_summary_by_perc_*.csv"))
    
    if not csv_files:
        print(f"Warning: No summary_by_perc CSV files found in {results_dir}")
        return results
    
    for csv_file in csv_files:
        # Extract domain name from filename
        # Format: results_<domain>_summary_by_perc_<timestamp>.csv
        filename = csv_file.stem
        parts = filename.split('_')
        if len(parts) >= 2:
            domain = parts[1]
            
            # Load the CSV
            df = pd.read_csv(csv_file)
            results[domain] = df
            print(f"Loaded {domain}: {len(df)} rows")
    
    return results


def plot_accuracy_vs_noise(results: dict, output_dir: str):
    """
    Plot accuracy vs noise level for each observation percentage.
    Creates one plot per domain.
    """
    for domain, df in results.items():
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Get unique observation percentages
        obs_percentages = sorted(df['observation_percentage'].unique())
        
        for obs_perc in obs_percentages:
            data = df[df['observation_percentage'] == obs_perc].sort_values('noise_level')
            ax.plot(data['noise_level'], data['accuracy'], 
                   marker='o', linewidth=2, markersize=8,
                   label=f'{obs_perc}% observations')
        
        ax.set_xlabel('Noise Level (%)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Accuracy (%)', fontsize=12, fontweight='bold')
        ax.set_title(f'{domain.capitalize()} - Accuracy vs Noise Level', 
                    fontsize=14, fontweight='bold')
        ax.legend(loc='best', framealpha=0.9)
        ax.grid(True, alpha=0.3)
        ax.set_ylim([0, 105])
        
        # Save plot
        output_file = os.path.join(output_dir, f'{domain}_accuracy_vs_noise.png')
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_file}")
        plt.close()


def plot_accuracy_vs_observations(results: dict, output_dir: str):
    """
    Plot accuracy vs observation percentage for each noise level.
    Creates one plot per domain.
    """
    for domain, df in results.items():
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Get unique noise levels
        noise_levels = sorted(df['noise_level'].unique())
        
        for noise in noise_levels:
            data = df[df['noise_level'] == noise].sort_values('observation_percentage')
            label = 'Clean' if noise == 0 else f'{noise}% noise'
            ax.plot(data['observation_percentage'], data['accuracy'], 
                   marker='o', linewidth=2, markersize=8,
                   label=label)
        
        ax.set_xlabel('Observation Percentage (%)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Accuracy (%)', fontsize=12, fontweight='bold')
        ax.set_title(f'{domain.capitalize()} - Accuracy vs Observation Percentage', 
                    fontsize=14, fontweight='bold')
        ax.legend(loc='best', framealpha=0.9)
        ax.grid(True, alpha=0.3)
        ax.set_ylim([0, 105])
        
        # Save plot
        output_file = os.path.join(output_dir, f'{domain}_accuracy_vs_observations.png')
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_file}")
        plt.close()


def plot_heatmap(results: dict, output_dir: str):
    """
    Create heatmap of accuracy for each domain.
    Rows: observation percentages, Columns: noise levels
    """
    for domain, df in results.items():
        # Pivot data to create matrix
        pivot_data = df.pivot(index='observation_percentage', 
                             columns='noise_level', 
                             values='accuracy')
        
        # Create heatmap
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(pivot_data, annot=True, fmt='.1f', cmap='RdYlGn',
                   vmin=0, vmax=100, cbar_kws={'label': 'Accuracy (%)'},
                   linewidths=0.5, ax=ax)
        
        ax.set_xlabel('Noise Level (%)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Observation Percentage (%)', fontsize=12, fontweight='bold')
        ax.set_title(f'{domain.capitalize()} - Accuracy Heatmap', 
                    fontsize=14, fontweight='bold')
        
        # Save plot
        output_file = os.path.join(output_dir, f'{domain}_heatmap.png')
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_file}")
        plt.close()


def plot_all_domains_comparison(results: dict, output_dir: str, obs_perc: int = 100):
    """
    Compare all domains at a specific observation percentage.
    Shows how different domains handle noise.
    """
    fig, ax = plt.subplots(figsize=(14, 8))
    
    for domain, df in results.items():
        data = df[df['observation_percentage'] == obs_perc].sort_values('noise_level')
        if len(data) > 0:
            ax.plot(data['noise_level'], data['accuracy'], 
                   marker='o', linewidth=2, markersize=8,
                   label=domain.capitalize())
    
    ax.set_xlabel('Noise Level (%)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Accuracy (%)', fontsize=12, fontweight='bold')
    ax.set_title(f'All Domains Comparison - {obs_perc}% Observations', 
                fontsize=14, fontweight='bold')
    ax.legend(loc='best', framealpha=0.9, ncol=2)
    ax.grid(True, alpha=0.3)
    ax.set_ylim([0, 105])
    
    # Save plot
    output_file = os.path.join(output_dir, f'all_domains_comparison_{obs_perc}pct.png')
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()


def plot_degradation_analysis(results: dict, output_dir: str):
    """
    Plot accuracy degradation (difference from clean) vs noise level.
    Shows how much accuracy drops with noise.
    """
    for domain, df in results.items():
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Get unique observation percentages
        obs_percentages = sorted(df['observation_percentage'].unique())
        
        for obs_perc in obs_percentages:
            data = df[df['observation_percentage'] == obs_perc].sort_values('noise_level')
            
            if len(data) > 0 and 0 in data['noise_level'].values:
                # Get clean accuracy (noise_level = 0)
                clean_accuracy = data[data['noise_level'] == 0]['accuracy'].values[0]
                
                # Calculate degradation
                degradation = clean_accuracy - data['accuracy']
                
                ax.plot(data['noise_level'], degradation, 
                       marker='o', linewidth=2, markersize=8,
                       label=f'{obs_perc}% observations')
        
        ax.set_xlabel('Noise Level (%)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Accuracy Drop from Clean (%)', fontsize=12, fontweight='bold')
        ax.set_title(f'{domain.capitalize()} - Accuracy Degradation', 
                    fontsize=14, fontweight='bold')
        ax.legend(loc='best', framealpha=0.9)
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='black', linestyle='--', linewidth=1)
        
        # Save plot
        output_file = os.path.join(output_dir, f'{domain}_degradation.png')
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_file}")
        plt.close()


def plot_bar_comparison(results: dict, output_dir: str, noise_level: int = 30):
    """
    Bar chart comparing all domains at a specific noise level.
    Groups by observation percentage.
    """
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Get all domains and observation percentages
    domains = sorted(results.keys())
    obs_percentages = sorted(results[domains[0]]['observation_percentage'].unique())
    
    x = np.arange(len(obs_percentages))
    width = 0.12
    
    for idx, domain in enumerate(domains):
        df = results[domain]
        data = df[df['noise_level'] == noise_level].sort_values('observation_percentage')
        
        if len(data) > 0:
            offset = width * (idx - len(domains)/2 + 0.5)
            ax.bar(x + offset, data['accuracy'], width, 
                  label=domain.capitalize())
    
    ax.set_xlabel('Observation Percentage (%)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Accuracy (%)', fontsize=12, fontweight='bold')
    ax.set_title(f'All Domains Comparison - {noise_level}% Noise', 
                fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([f'{int(p)}%' for p in obs_percentages])
    ax.legend(loc='best', framealpha=0.9, ncol=2)
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_ylim([0, 105])
    
    # Save plot
    output_file = os.path.join(output_dir, f'bar_comparison_{noise_level}pct_noise.png')
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()


def generate_summary_stats(results: dict, output_dir: str):
    """
    Generate and save summary statistics table.
    """
    summary_data = []
    
    for domain, df in results.items():
        # Overall statistics
        mean_accuracy = df['accuracy'].mean()
        std_accuracy = df['accuracy'].std()
        min_accuracy = df['accuracy'].min()
        max_accuracy = df['accuracy'].max()
        
        # Clean vs max noise
        clean_data = df[df['noise_level'] == 0]
        max_noise_data = df[df['noise_level'] == df['noise_level'].max()]
        
        clean_avg = clean_data['accuracy'].mean() if len(clean_data) > 0 else 0
        noisy_avg = max_noise_data['accuracy'].mean() if len(max_noise_data) > 0 else 0
        degradation = clean_avg - noisy_avg
        
        summary_data.append({
            'Domain': domain.capitalize(),
            'Mean Accuracy': f'{mean_accuracy:.2f}%',
            'Std Dev': f'{std_accuracy:.2f}%',
            'Min Accuracy': f'{min_accuracy:.2f}%',
            'Max Accuracy': f'{max_accuracy:.2f}%',
            'Clean Avg': f'{clean_avg:.2f}%',
            'Max Noise Avg': f'{noisy_avg:.2f}%',
            'Avg Degradation': f'{degradation:.2f}%'
        })
    
    summary_df = pd.DataFrame(summary_data)
    
    # Save to CSV
    output_file = os.path.join(output_dir, 'summary_statistics.csv')
    summary_df.to_csv(output_file, index=False)
    print(f"\nSaved summary statistics: {output_file}")
    
    # Print to console
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)
    print(summary_df.to_string(index=False))
    print("="*80)


def main():
    parser = argparse.ArgumentParser(
        description='Generate plots from goal recognition experiment results',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--results-dir', type=str, 
                       default='./disturbed_results_last_actions',
                       help='Directory containing result CSV files')
    
    parser.add_argument('--output-dir', type=str, 
                       default='./plots',
                       help='Directory to save generated plots')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    print("="*80)
    print("GOAL RECOGNITION RESULTS PLOTTER")
    print("="*80)
    print(f"Results directory: {args.results_dir}")
    print(f"Output directory: {args.output_dir}")
    print()
    
    # Load results
    print("Loading results...")
    results = load_results(args.results_dir)
    
    if not results:
        print("Error: No results loaded. Exiting.")
        return 1
    
    print(f"\nLoaded {len(results)} domains: {', '.join(results.keys())}")
    print()
    
    # Generate all plots
    print("Generating plots...")
    print("-"*80)
    
    #* call relevant plotting functions, change as needed
    plot_accuracy_vs_noise(results, args.output_dir)
    
    plot_accuracy_vs_observations(results, args.output_dir)
    
    plot_heatmap(results, args.output_dir)
    
    plot_all_domains_comparison(results, args.output_dir, obs_perc=100)
    
    plot_all_domains_comparison(results, args.output_dir, obs_perc=50)
    
    plot_degradation_analysis(results, args.output_dir)
    
    plot_bar_comparison(results, args.output_dir, noise_level=30)
    
    plot_bar_comparison(results, args.output_dir, noise_level=10)
    
    generate_summary_stats(results, args.output_dir)
    
    print("\n" + "="*80)
    print("✓ All plots generated successfully!")
    print(f"✓ Output saved to: {args.output_dir}")
    print("="*80)
    
    return 0


if __name__ == '__main__':
    exit(main())
