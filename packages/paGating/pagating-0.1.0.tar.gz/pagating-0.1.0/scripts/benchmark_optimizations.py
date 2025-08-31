#!/usr/bin/env python3.12
"""
Comprehensive benchmarking suite for paGating M4 optimizations
"""
import os
import sys

# Force cache directory before importing huggingface
CACHE_DIR = os.path.abspath('.cache')
os.environ['HF_HOME'] = CACHE_DIR
os.environ['TRANSFORMERS_CACHE'] = CACHE_DIR
os.makedirs(CACHE_DIR, exist_ok=True)

import argparse
import pathlib
import time
import json
import psutil
import torch
import numpy as np
import platform
import logging
from typing import Dict, List, Any
from datasets import load_dataset
from transformers import GPT2Tokenizer, TrainingArguments, Trainer, GPT2LMHeadModel

# Add project root to Python path
sys.path.insert(0, os.path.abspath('.'))
from models.gpt2_pagating_patch import patch_gpt2_with_pagating

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PerformanceBenchmark:
    """Comprehensive performance benchmarking for paGating optimizations"""
    
    def __init__(self):
        self.results = {}
        self.system_info = self._get_system_info()
        
    def _get_system_info(self) -> Dict[str, Any]:
        """Collect system information"""
        info = {
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'cpu': platform.processor(),
            'cpu_cores': psutil.cpu_count(logical=False),
            'cpu_logical_cores': psutil.cpu_count(logical=True),
            'cpu_freq': self._get_cpu_freq(),
            'memory': psutil.virtual_memory()._asdict(),
            'torch_version': torch.__version__,
            'cuda_available': torch.cuda.is_available(),
            'mps_available': torch.backends.mps.is_available()
        }
        info.update(self._get_gpu_info())
        return info
    
    def _get_cpu_freq(self):
        try:
            freq = psutil.cpu_freq()
            return freq._asdict() if freq else None
        except (FileNotFoundError, NotImplementedError):
            logger.warning("Could not determine CPU frequency. This is common on some platforms (e.g., Apple Silicon).")
            return {
                'current': 'N/A',
                'min': 'N/A',
                'max': 'N/A'
            }
    
    def _get_gpu_info(self):
        if torch.cuda.is_available():
            return {
                'cuda_device_count': torch.cuda.device_count(),
                'cuda_device_name': torch.cuda.get_device_name(0),
                'cuda_memory': torch.cuda.get_device_properties(0).total_memory / (1024**3)
            }
        else:
            return {}
    
    def benchmark_training_step(self, 
                              model, 
                              train_dataset, 
                              batch_size: int = 4,
                              num_steps: int = 10,
                              config_name: str = "default") -> Dict[str, float]:
        """Benchmark training performance for a specific configuration"""
        
        print(f"\n--- Benchmarking {config_name} ---")
        
        # Setup training arguments for benchmarking
        training_args = TrainingArguments(
            output_dir=f"./benchmark_temp/{config_name}",
            per_device_train_batch_size=batch_size,
            max_steps=num_steps,
            logging_steps=1,
            save_steps=999999,  # Don't save during benchmark
            eval_steps=999999,  # Don't eval during benchmark
            remove_unused_columns=False,
            # Optimizations for MPS
            bf16=True if "Optimized" in config_name and torch.backends.mps.is_available() else False,
            gradient_checkpointing=True if "Optimized" in config_name else False,
            use_cpu="Baseline" in config_name,
        )
        
        # Create trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset
        )
        
        # Warmup
        print("Warming up...")
        for _ in range(3):
            try:
                next(iter(trainer.get_train_dataloader()))
            except:
                break
        
        # Benchmark
        self.step_times = []
        self.memory_usage = []
        self.cpu_usage = []
        
        print(f"Running {num_steps} training steps...")
        start_time = time.time()
        
        # Monitor during training
        from transformers import TrainerCallback
        
        class BenchmarkCallback(TrainerCallback):
            def __init__(self, parent):
                self.parent = parent
                self.step_start_time = None
                
            def on_step_begin(self, args, state, control, **kwargs):
                self.step_start_time = time.time()
                # Use a non-blocking way to get CPU percent
                psutil.cpu_percent(interval=None) 
                
            def on_step_end(self, args, state, control, **kwargs):
                if self.step_start_time:
                    step_time = time.time() - self.step_start_time
                    cpu_percent = psutil.cpu_percent(interval=None)
                    memory_info = psutil.virtual_memory()

                    self.parent.step_times.append(step_time)
                    self.parent.cpu_usage.append(cpu_percent)
                    self.parent.memory_usage.append(memory_info.percent)
        
        # Create callback with access to our lists
        callback = BenchmarkCallback(self)
        
        try:
            # Run training with monitoring
            trainer.add_callback(callback)
            trainer.train()
            
        except Exception as e:
            print(f"Training error: {e}")
            return {}
        
        total_time = time.time() - start_time
        
        # Calculate metrics
        if self.step_times:
            avg_step_time = np.mean(self.step_times)
            samples_per_second = batch_size / avg_step_time
            
            results = {
                'config_name': config_name,
                'batch_size': batch_size,
                'num_steps': len(self.step_times),
                'total_time_seconds': total_time,
                'avg_step_time_seconds': avg_step_time,
                'min_step_time_seconds': np.min(self.step_times),
                'max_step_time_seconds': np.max(self.step_times),
                'samples_per_second': samples_per_second,
                'avg_cpu_usage_percent': np.mean(self.cpu_usage) if self.cpu_usage else 0,
                'max_cpu_usage_percent': np.max(self.cpu_usage) if self.cpu_usage else 0,
                'avg_memory_usage_percent': np.mean(self.memory_usage) if self.memory_usage else 0,
                'max_memory_usage_percent': np.max(self.memory_usage) if self.memory_usage else 0,
            }
            
            print(f"Results for {config_name}:")
            print(f"  Average step time: {avg_step_time:.3f}s")
            print(f"  Samples/second: {samples_per_second:.2f}")
            print(f"  CPU usage: {np.mean(self.cpu_usage):.1f}% (avg), {np.max(self.cpu_usage):.1f}% (max)")
            print(f"  Memory usage: {np.mean(self.memory_usage):.1f}% (avg), {np.max(self.memory_usage):.1f}% (max)")
            
            return results
        else:
            print(f"No timing data collected for {config_name}")
            return {}
    
    def benchmark_cpu_baseline(self, alpha_mode: str = "learnable") -> Dict[str, float]:
        """Benchmark CPU-only training (original configuration)"""
        
        try:
            print("Loading dataset for CPU benchmark...")
            tok = GPT2Tokenizer.from_pretrained("gpt2", cache_dir=CACHE_DIR)
            tok.pad_token = tok.eos_token
            ds = load_dataset("wikitext", "wikitext-103-raw-v1", cache_dir=CACHE_DIR)
            
            def tok_fn(ex):
                # Ensure 'text' field exists and is not empty
                if not ex.get("text"):
                    return None
                try:
                    result = tok(ex["text"], truncation=True, padding="max_length", max_length=128)
                    result["labels"] = result["input_ids"].copy()
                    # We need input_ids to proceed
                    return result if 'input_ids' in result and result['input_ids'] else None
                except Exception as e:
                    logger.error(f"Tokenization failed for an example: {e}")
                    return None
            
            train = ds["train"].select(range(1000)).map(tok_fn, batched=True, remove_columns=["text"])
            train = train.filter(lambda x: x is not None and 'input_ids' in x and len(x['input_ids']) > 0)
            train.set_format(type="torch", columns=["input_ids", "attention_mask", "labels"])
            
            # Create CPU model
            model = GPT2LMHeadModel.from_pretrained("gpt2", cache_dir=CACHE_DIR)
            patch_gpt2_with_pagating(model, alpha_mode)
            
            # Force CPU usage
            model = model.to('cpu')
            
            return self.benchmark_training_step(
                model, train, batch_size=4, num_steps=10, config_name="CPU_Baseline"
            )
        except Exception as e:
            print(f"Benchmark CPU Baseline failed: {e}")
            return {}
    
    def benchmark_mps_basic(self, alpha_mode: str = "learnable") -> Dict[str, float]:
        """Benchmark basic MPS acceleration"""
        
        try:
            print("Loading dataset for MPS benchmark...")
            tok = GPT2Tokenizer.from_pretrained("gpt2", cache_dir=CACHE_DIR)
            tok.pad_token = tok.eos_token
            ds = load_dataset("wikitext", "wikitext-103-raw-v1", cache_dir=CACHE_DIR)
            
            def tok_fn(ex):
                if not ex.get("text"):
                    return None
                try:
                    result = tok(ex["text"], truncation=True, padding="max_length", max_length=128)
                    result["labels"] = result["input_ids"].copy()
                    return result if 'input_ids' in result and result['input_ids'] else None
                except Exception as e:
                    logger.error(f"Tokenization failed for an example: {e}")
                    return None

            train = ds["train"].select(range(1000)).map(tok_fn, batched=True, remove_columns=["text"])
            train = train.filter(lambda x: x is not None and 'input_ids' in x and len(x['input_ids']) > 0)
            train.set_format(type="torch", columns=["input_ids", "attention_mask", "labels"])
            
            # Create MPS model
            model = GPT2LMHeadModel.from_pretrained("gpt2", cache_dir=CACHE_DIR)
            patch_gpt2_with_pagating(model, alpha_mode)
            
            if torch.backends.mps.is_available():
                model = model.to('mps')
            else:
                model = model.to('cpu') # Fallback for non-MPS
            
            return self.benchmark_training_step(
                model, train, batch_size=8, num_steps=10, config_name="MPS_Basic"
            )
        except Exception as e:
            print(f"Benchmark MPS Basic failed: {e}")
            return {}
    
    def benchmark_mps_optimized(self, alpha_mode: str = "learnable") -> Dict[str, float]:
        """Benchmark fully optimized MPS training"""
        
        try:
            print("Loading dataset for optimized MPS benchmark...")
            tok = GPT2Tokenizer.from_pretrained("gpt2", cache_dir=CACHE_DIR)
            tok.pad_token = tok.eos_token
            ds = load_dataset("wikitext", "wikitext-103-raw-v1", cache_dir=CACHE_DIR)
            
            def tok_fn(ex):
                if not ex.get("text"):
                    return None
                try:
                    result = tok(ex["text"], truncation=True, padding="max_length", max_length=128)
                    result["labels"] = result["input_ids"].copy()
                    return result if 'input_ids' in result and result['input_ids'] else None
                except Exception as e:
                    logger.error(f"Tokenization failed for an example: {e}")
                    return None

            train = ds["train"].select(range(1000)).map(tok_fn, batched=True, remove_columns=["text"])
            train = train.filter(lambda x: x is not None and 'input_ids' in x and len(x['input_ids']) > 0)
            train.set_format(type="torch", columns=["input_ids", "attention_mask", "labels"])
            
            # Create and configure the optimized model
            model = GPT2LMHeadModel.from_pretrained("gpt2", cache_dir=CACHE_DIR)
            patch_gpt2_with_pagating(model, alpha_mode)
            
            if torch.backends.mps.is_available():
                model = model.to('mps')
            else:
                model = model.to('cpu') # Fallback for non-MPS
            
            # Apply optimizations
            # torch.compile is disabled for now due to instability on MPS
            # if hasattr(torch, 'compile'):
            #     model = torch.compile(model)
            
            return self.benchmark_training_step(
                model, train, batch_size=32, num_steps=10, config_name="MPS_Optimized"
            )
        except Exception as e:
            print(f"Benchmark MPS Optimized failed: {e}")
            return {}
    
    def run_full_benchmark(self, alpha_mode: str = "learnable") -> Dict[str, Any]:
        """Run complete benchmark suite"""
        
        print("=== Running M4 Optimization Benchmark Suite ===")
        print(f"System Info: {self.system_info}")
        
        results = {
            'system_info': self.system_info,
            'benchmark_timestamp': time.time(),
            'configurations': []
        }
        
        # Run all benchmarks
        benchmarks = [
            ('CPU Baseline', self.benchmark_cpu_baseline),
            ('MPS Basic', self.benchmark_mps_basic),
            ('MPS Optimized', self.benchmark_mps_optimized),
        ]
        
        for name, benchmark_func in benchmarks:
            try:
                print(f"\n{'='*50}")
                print(f"Running {name} benchmark...")
                result = benchmark_func(alpha_mode)
                if result:
                    results['configurations'].append(result)
                    
                # Cleanup between benchmarks
                if torch.backends.mps.is_available():
                    torch.mps.empty_cache()
                import gc
                gc.collect()
                time.sleep(2)  # Brief pause between benchmarks
                
            except Exception as e:
                print(f"Benchmark {name} failed: {e}")
                continue
        
        # Calculate speedups
        if len(results['configurations']) > 1:
            baseline = next((r for r in results['configurations'] if 'CPU' in r['config_name']), None)
            if baseline:
                baseline_sps = baseline['samples_per_second']
                for config in results['configurations']:
                    config['speedup_vs_cpu'] = config['samples_per_second'] / baseline_sps
        
        return results
    
    def save_results(self, results: Dict[str, Any], output_path: str):
        """Save benchmark results to file"""
        output_path = pathlib.Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nBenchmark results saved to: {output_path}")
    
    def print_summary(self, results: Dict[str, Any]):
        """Print benchmark summary"""
        
        print(f"\n{'='*60}")
        print("M4 OPTIMIZATION BENCHMARK SUMMARY")
        print(f"{'='*60}")
        
        if 'configurations' in results:
            for config in results['configurations']:
                name = config.get('config_name', 'Unknown')
                sps = config.get('samples_per_second', 0)
                step_time = config.get('avg_step_time_seconds', 0)
                batch_size = config.get('batch_size', 0)
                speedup = config.get('speedup_vs_cpu', 1.0)
                
                print(f"\n{name}:")
                print(f"  Batch size: {batch_size}")
                print(f"  Step time: {step_time:.3f}s")
                print(f"  Throughput: {sps:.2f} samples/sec")
                print(f"  Speedup vs CPU: {speedup:.2f}x")
        
        print(f"\n{'='*60}")

def main():
    parser = argparse.ArgumentParser(description="Benchmark M4 optimizations")
    parser.add_argument("--alpha_mode", default="learnable", help="Alpha mode for paGating")
    parser.add_argument("--output", default="benchmark_results.json", help="Output file for results")
    
    args = parser.parse_args()
    
    benchmark = PerformanceBenchmark()
    results = benchmark.run_full_benchmark(args.alpha_mode)
    
    benchmark.print_summary(results)
    benchmark.save_results(results, args.output)

if __name__ == "__main__":
    main() 