#!/usr/bin/env python
"""
24-Hour Expedited Experimental Plan for paGLU Research

This script runs the minimum critical experiments needed to achieve 8/10 publication readiness:
1. 3-seed validation for key NLP comparisons
2. Standard baseline comparisons for vision
3. Enhanced statistical analysis of existing + new results
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

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="24-hour expedited paGLU experiments")
    
    parser.add_argument("--seeds", type=int, nargs="+", default=[42, 123, 456],
                        help="Random seeds (3 minimum for expedited)")
    parser.add_argument("--max_workers", type=int, default=1,
                        help="Maximum parallel workers")
    parser.add_argument("--output_dir", type=str, default="experiments/expedited_24h",
                        help="Output directory for results")
    
    return parser.parse_args()


class ExpeditedExperimentRunner:
    """Manages expedited 24-hour experimental runs."""
    
    def __init__(self, args):
        self.args = args
        self.output_dir = Path(args.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # CRITICAL experiments only - focus on statistical significance
        self.critical_nlp_configs = [
            # Core comparison that we know works
            {"unit": "baseline", "alpha": 0.0, "lr": 5e-4, "description": "Baseline (no gating)"},
            {"unit": "paGLU", "alpha": 0.5, "lr": 5e-4, "description": "paGLU (moderate gating)"},
        ]
        
        self.critical_vision_configs = [
            # paGLU vs standard baselines (CRITICAL for generalizability)
            {"unit": "paGLU", "alpha": 0.5, "description": "paGLU"},
            {"unit": "ReLU", "alpha": None, "description": "ReLU baseline"},
            {"unit": "GELU", "alpha": None, "description": "GELU baseline"},
        ]
        
        self.results = {"nlp": [], "vision": []}
    
    def run_critical_nlp_experiments(self):
        """Run critical NLP experiments with 3 seeds."""
        print("🔤 Running CRITICAL NLP experiments...")
        
        for config in self.critical_nlp_configs:
            for seed in self.args.seeds:
                exp_name = f"{config['unit']}_alpha{config['alpha']}_lr{config['lr']}_seed{seed}"
                output_path = self.output_dir / "nlp" / exp_name
                
                cmd = [
                    "python", "scripts/train_pagating_optimized.py",
                    "--unit", "paGLU",  # Always use paGLU, vary alpha
                    "--alpha", str(config['alpha']),
                    "--learning_rate", str(config['lr']),
                    "--max_steps", "5000",  # Reduced for speed
                    "--batch_size", "4",
                    "--gradient_accumulation_steps", "4",
                    "--seed", str(seed),
                    "--output_dir", str(output_path),
                    "--eval_steps", "1000"
                ]
                
                result = self._run_experiment(cmd, exp_name, "nlp", config, seed)
                self.results["nlp"].append(result)
                self._save_results()
    
    def run_critical_vision_experiments(self):
        """Run critical vision experiments with 3 seeds."""
        print("🖼️ Running CRITICAL vision experiments...")
        
        for config in self.critical_vision_configs:
            for seed in self.args.seeds:
                exp_name = f"{config['unit']}_seed{seed}"
                output_path = self.output_dir / "vision" / exp_name
                
                if config['unit'] in ['ReLU', 'GELU']:
                    cmd = [
                        "python", "scripts/train_standard_baselines.py",
                        "--activation", config['unit'],
                        "--max_epochs", "25",  # Reduced for speed
                        "--batch_size", "64",
                        "--seed", str(seed),
                        "--output_dir", str(output_path)
                    ]
                else:
                    cmd = [
                        "python", "scripts/train_cifar_pagating.py",
                        "--unit", config['unit'],
                        "--alpha", str(config['alpha']),
                        "--max_epochs", "25",  # Reduced for speed
                        "--batch_size", "64",
                        "--seed", str(seed),
                        "--output_dir", str(output_path)
                    ]
                
                result = self._run_experiment(cmd, exp_name, "vision", config, seed)
                self.results["vision"].append(result)
                self._save_results()
    
    def _run_experiment(self, cmd, exp_name, domain, config, seed):
        """Execute a single experiment."""
        print(f"🚀 Starting {domain.upper()}: {exp_name}")
        start_time = time.time()
        
        try:
            env = os.environ.copy()
            env["KMP_DUPLICATE_LIB_OK"] = "TRUE"
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=3600,  # 1 hour timeout
                env=env
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                print(f"✅ Completed {exp_name} in {duration:.1f}s")
                
                # Parse results
                results = self._parse_experiment_results(result.stdout, domain)
                
                return {
                    "experiment": exp_name,
                    "domain": domain,
                    "config": config,
                    "seed": seed,
                    "status": "success",
                    "duration": duration,
                    "results": results,
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
                "duration": 3600,
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
        
        elif domain == "vision":
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
    
    def _save_results(self):
        """Save current results to file."""
        results_file = self.output_dir / "expedited_results.json"
        
        results_with_meta = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "seeds": self.args.seeds,
                "experiment_type": "expedited_24h",
                "total_experiments": len(self.results["nlp"]) + len(self.results["vision"])
            },
            "results": self.results
        }
        
        with open(results_file, 'w') as f:
            json.dump(results_with_meta, f, indent=2)
    
    def run_expedited_experiments(self):
        """Run all expedited experiments."""
        print("⚡ 24-HOUR EXPEDITED EXPERIMENTAL PLAN")
        print("=" * 50)
        print(f"📁 Output: {self.output_dir}")
        print(f"🎲 Seeds: {self.args.seeds}")
        print(f"🎯 Target: 8/10 publication readiness")
        print("=" * 50)
        
        # Run critical experiments
        self.run_critical_nlp_experiments()
        self.run_critical_vision_experiments()
        
        # Final save
        self._save_results()
        
        print("🏁 Expedited experiments complete!")
        return self.results


def main():
    """Main execution function."""
    args = parse_args()
    
    runner = ExpeditedExperimentRunner(args)
    results = runner.run_expedited_experiments()
    
    # Print summary
    print("\n📊 EXPEDITED EXPERIMENT SUMMARY")
    print("=" * 40)
    
    for domain in ["nlp", "vision"]:
        domain_results = results[domain]
        total = len(domain_results)
        successful = len([r for r in domain_results if r["status"] == "success"])
        
        print(f"{domain.upper()}: {successful}/{total} successful")
    
    print(f"\n✅ Results saved to: {args.output_dir}")
    print("🔬 Ready for enhanced statistical analysis!")


if __name__ == "__main__":
    main() 