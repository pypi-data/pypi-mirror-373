#!/usr/bin/env python
"""
Multi-Seed Experimental Framework for paGLU Research

This script runs comprehensive experiments with multiple seeds, baselines, and datasets
to ensure statistical significance, generalizability, and robustness claims.
"""

import os
import sys
import json
import time
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
import numpy as np
import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Multi-seed paGLU experiments")
    
    # Experiment configuration
    parser.add_argument("--seeds", type=int, nargs="+", default=[42, 123, 456, 789, 999],
                        help="Random seeds for experiments")
    parser.add_argument("--max_workers", type=int, default=2,
                        help="Maximum parallel workers")
    
    # NLP experiments
    parser.add_argument("--run_nlp", action="store_true", default=True,
                        help="Run NLP experiments")
    parser.add_argument("--nlp_steps", type=int, default=10000,
                        help="Training steps for NLP experiments")
    parser.add_argument("--nlp_batch_size", type=int, default=4,
                        help="Batch size for NLP experiments")
    
    # Vision experiments  
    parser.add_argument("--run_vision", action="store_true", default=True,
                        help="Run vision experiments")
    parser.add_argument("--vision_epochs", type=int, default=50,
                        help="Training epochs for vision experiments")
    parser.add_argument("--vision_batch_size", type=int, default=64,
                        help="Batch size for vision experiments")
    
    # Output
    parser.add_argument("--output_dir", type=str, default="experiments/multi_seed_validation",
                        help="Output directory for results")
    parser.add_argument("--dry_run", action="store_true",
                        help="Print commands without executing")
    
    return parser.parse_args()


class ExperimentRunner:
    """Manages multi-seed experimental runs."""
    
    def __init__(self, args):
        self.args = args
        self.output_dir = Path(args.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Experiment configurations
        self.nlp_configs = [
            # Baseline comparisons
            {"unit": "baseline", "alpha": 0.0, "lr": 5e-4, "description": "Baseline (no gating)"},
            {"unit": "paGLU", "alpha": 0.5, "lr": 5e-4, "description": "paGLU (moderate gating)"},
            {"unit": "paGLU", "alpha": 1.0, "lr": 5e-4, "description": "paGLU (full gating = GLU)"},
            
            # Learning rate sensitivity
            {"unit": "baseline", "alpha": 0.0, "lr": 1e-4, "description": "Baseline (low LR)"},
            {"unit": "paGLU", "alpha": 0.5, "lr": 1e-4, "description": "paGLU (low LR)"},
        ]
        
        self.vision_configs = [
            # paGating variants
            {"unit": "paGLU", "alpha": 0.5, "description": "paGLU"},
            {"unit": "paGTU", "alpha": 0.5, "description": "paGTU"}, 
            {"unit": "paSwishU", "alpha": 0.5, "description": "paSwishU"},
            {"unit": "paReGLU", "alpha": 0.5, "description": "paReGLU"},
            {"unit": "paGELU", "alpha": 0.5, "description": "paGELU"},
            
            # Standard baselines
            {"unit": "ReLU", "alpha": None, "description": "ReLU baseline"},
            {"unit": "GELU", "alpha": None, "description": "GELU baseline"},
            {"unit": "SiLU", "alpha": None, "description": "SiLU/Swish baseline"},
        ]
        
        self.results = {"nlp": [], "vision": []}
    
    def run_single_nlp_experiment(self, config, seed):
        """Run a single NLP experiment."""
        exp_name = f"{config['unit']}_alpha{config['alpha']}_lr{config['lr']}_seed{seed}"
        output_path = self.output_dir / "nlp" / exp_name
        
        if config['unit'] == 'baseline':
            # Use paGLU with alpha=0.0 for baseline
            cmd = [
                "python", "scripts/train_pagating_optimized.py",
                "--unit", "paGLU",
                "--alpha", str(config['alpha']),
                "--learning_rate", str(config['lr']),
                "--max_steps", str(self.args.nlp_steps),
                "--batch_size", str(self.args.nlp_batch_size),
                "--gradient_accumulation_steps", "4",
                "--seed", str(seed),
                "--output_dir", str(output_path),
                "--save_final_model",
                "--eval_steps", "500"
            ]
        else:
            cmd = [
                "python", "scripts/train_pagating_optimized.py", 
                "--unit", config['unit'],
                "--alpha", str(config['alpha']),
                "--learning_rate", str(config['lr']),
                "--max_steps", str(self.args.nlp_steps),
                "--batch_size", str(self.args.nlp_batch_size),
                "--gradient_accumulation_steps", "4", 
                "--seed", str(seed),
                "--output_dir", str(output_path),
                "--save_final_model",
                "--eval_steps", "500"
            ]
        
        return self._run_experiment(cmd, exp_name, "nlp", config, seed)
    
    def run_single_vision_experiment(self, config, seed):
        """Run a single vision experiment."""
        exp_name = f"{config['unit']}_seed{seed}"
        output_path = self.output_dir / "vision" / exp_name
        
        if config['unit'] in ['ReLU', 'GELU', 'SiLU']:
            # Standard activation baselines
            cmd = [
                "python", "scripts/train_standard_baselines.py",
                "--activation", config['unit'],
                "--max_epochs", str(self.args.vision_epochs),
                "--batch_size", str(self.args.vision_batch_size),
                "--seed", str(seed),
                "--output_dir", str(output_path)
            ]
        else:
            # paGating variants
            cmd = [
                "python", "scripts/train_cifar_pagating.py",
                "--unit", config['unit'],
                "--alpha", str(config['alpha']),
                "--max_epochs", str(self.args.vision_epochs),
                "--batch_size", str(self.args.vision_batch_size),
                "--seed", str(seed),
                "--output_dir", str(output_path)
            ]
        
        return self._run_experiment(cmd, exp_name, "vision", config, seed)
    
    def _run_experiment(self, cmd, exp_name, domain, config, seed):
        """Execute a single experiment."""
        if self.args.dry_run:
            print(f"[DRY RUN] {domain.upper()}: {' '.join(cmd)}")
            return {
                "experiment": exp_name,
                "domain": domain,
                "config": config,
                "seed": seed,
                "status": "dry_run",
                "results": {}
            }
        
        print(f"🚀 Starting {domain.upper()} experiment: {exp_name}")
        start_time = time.time()
        
        try:
            # Set environment variable to handle OpenMP issues
            env = os.environ.copy()
            env["KMP_DUPLICATE_LIB_OK"] = "TRUE"
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=7200,  # 2 hour timeout
                env=env
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                print(f"✅ Completed {exp_name} in {duration:.1f}s")
                
                # Parse results from output
                results = self._parse_experiment_results(result.stdout, domain)
                
                return {
                    "experiment": exp_name,
                    "domain": domain,
                    "config": config,
                    "seed": seed,
                    "status": "success",
                    "duration": duration,
                    "results": results,
                    "stdout": result.stdout[-1000:],  # Last 1000 chars
                }
            else:
                print(f"❌ Failed {exp_name}: {result.stderr}")
                return {
                    "experiment": exp_name,
                    "domain": domain,
                    "config": config,
                    "seed": seed,
                    "status": "failed",
                    "duration": duration,
                    "error": result.stderr,
                    "results": {}
                }
                
        except subprocess.TimeoutExpired:
            print(f"⏰ Timeout {exp_name}")
            return {
                "experiment": exp_name,
                "domain": domain,
                "config": config,
                "seed": seed,
                "status": "timeout",
                "duration": 7200,
                "results": {}
            }
        except Exception as e:
            print(f"💥 Error {exp_name}: {e}")
            return {
                "experiment": exp_name,
                "domain": domain,
                "config": config,
                "seed": seed,
                "status": "error",
                "error": str(e),
                "results": {}
            }
    
    def _parse_experiment_results(self, stdout, domain):
        """Parse experimental results from stdout."""
        results = {}
        
        if domain == "nlp":
            # Look for final losses in GPT-2 output
            lines = stdout.split('\n')
            for line in lines:
                if "Final training loss:" in line:
                    try:
                        results["train_loss"] = float(line.split(":")[-1].strip())
                    except:
                        pass
                elif "Final evaluation loss:" in line:
                    try:
                        results["eval_loss"] = float(line.split(":")[-1].strip())
                    except:
                        pass
                elif "Final perplexity:" in line:
                    try:
                        results["perplexity"] = float(line.split(":")[-1].strip())
                    except:
                        pass
        
        elif domain == "vision":
            # Look for final accuracies in CIFAR-10 output
            lines = stdout.split('\n')
            for line in lines:
                if "Final validation accuracy:" in line:
                    try:
                        results["val_acc"] = float(line.split(":")[-1].strip())
                    except:
                        pass
                elif "Final test accuracy:" in line:
                    try:
                        results["test_acc"] = float(line.split(":")[-1].strip())
                    except:
                        pass
        
        return results
    
    def run_all_experiments(self):
        """Run all experiments with multiple seeds."""
        all_experiments = []
        
        # Generate all experiment combinations
        if self.args.run_nlp:
            for config in self.nlp_configs:
                for seed in self.args.seeds:
                    all_experiments.append(("nlp", config, seed))
        
        if self.args.run_vision:
            for config in self.vision_configs:
                for seed in self.args.seeds:
                    all_experiments.append(("vision", config, seed))
        
        print(f"🎯 Running {len(all_experiments)} total experiments")
        print(f"📊 Seeds: {self.args.seeds}")
        print(f"⚡ Max workers: {self.args.max_workers}")
        
        # Run experiments in parallel
        with ProcessPoolExecutor(max_workers=self.args.max_workers) as executor:
            # Submit all experiments
            future_to_exp = {}
            for domain, config, seed in all_experiments:
                if domain == "nlp":
                    future = executor.submit(self.run_single_nlp_experiment, config, seed)
                else:
                    future = executor.submit(self.run_single_vision_experiment, config, seed)
                future_to_exp[future] = (domain, config, seed)
            
            # Collect results as they complete
            for future in as_completed(future_to_exp):
                domain, config, seed = future_to_exp[future]
                try:
                    result = future.result()
                    self.results[domain].append(result)
                    
                    # Save intermediate results
                    self._save_results()
                    
                except Exception as e:
                    print(f"💥 Exception in {domain} experiment: {e}")
        
        print(f"🏁 Completed all experiments!")
        return self.results
    
    def _save_results(self):
        """Save current results to file."""
        results_file = self.output_dir / "experimental_results.json"
        
        # Add metadata
        results_with_meta = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "seeds": self.args.seeds,
                "nlp_steps": self.args.nlp_steps,
                "vision_epochs": self.args.vision_epochs,
                "total_experiments": len(self.results["nlp"]) + len(self.results["vision"])
            },
            "results": self.results
        }
        
        with open(results_file, 'w') as f:
            json.dump(results_with_meta, f, indent=2)
        
        print(f"💾 Saved results to {results_file}")


def main():
    """Main execution function."""
    args = parse_args()
    
    print("🔬 Multi-Seed paGLU Experimental Framework")
    print("=" * 50)
    print(f"📁 Output directory: {args.output_dir}")
    print(f"🎲 Seeds: {args.seeds}")
    print(f"🔤 NLP experiments: {args.run_nlp}")
    print(f"🖼️  Vision experiments: {args.run_vision}")
    print(f"⚡ Max workers: {args.max_workers}")
    
    if args.dry_run:
        print("🏃 DRY RUN MODE - No experiments will be executed")
    
    print("=" * 50)
    
    # Create experiment runner
    runner = ExperimentRunner(args)
    
    # Run all experiments
    results = runner.run_all_experiments()
    
    # Print summary
    print("\n📊 EXPERIMENT SUMMARY")
    print("=" * 30)
    
    for domain in ["nlp", "vision"]:
        domain_results = results[domain]
        total = len(domain_results)
        successful = len([r for r in domain_results if r["status"] == "success"])
        failed = len([r for r in domain_results if r["status"] == "failed"])
        
        print(f"{domain.upper()}: {successful}/{total} successful ({failed} failed)")
    
    print(f"\n✅ All results saved to: {args.output_dir}")
    print("🔬 Ready for statistical analysis!")


if __name__ == "__main__":
    main() 