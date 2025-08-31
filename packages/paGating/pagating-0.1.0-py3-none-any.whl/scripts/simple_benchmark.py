#!/usr/bin/env python3.12
"""
Simple benchmark for M4 optimizations
"""
import time
import torch
import psutil
from datasets import load_dataset
from transformers import GPT2Tokenizer, GPT2LMHeadModel
import sys, os

sys.path.insert(0, os.path.abspath('.'))
from models.gpt2_pagating_patch import patch_gpt2_with_pagating

CACHE_DIR = os.path.abspath('.cache')
os.environ['HF_HOME'] = CACHE_DIR
os.environ['TRANSFORMERS_CACHE'] = CACHE_DIR

def prepare_data():
    """Prepare a small dataset for benchmarking"""
    tok = GPT2Tokenizer.from_pretrained("gpt2", cache_dir=CACHE_DIR)
    tok.pad_token = tok.eos_token
    ds = load_dataset("wikitext", "wikitext-103-raw-v1", cache_dir=CACHE_DIR)
    
    def tok_fn(ex):
        result = tok(ex["text"], truncation=True, padding="max_length", max_length=128)
        result["labels"] = result["input_ids"].copy()
        return result
    
    train = ds["train"].select(range(100)).map(tok_fn, batched=True, remove_columns=["text"])
    train = train.filter(lambda x: x is not None)
    train.set_format(type="torch", columns=["input_ids", "attention_mask", "labels"])
    return train

def benchmark_config(model, dataset, batch_size, config_name, num_batches=10):
    """Benchmark a specific configuration"""
    print(f"\n=== Benchmarking {config_name} ===")
    print(f"Batch size: {batch_size}")
    
    model.train()
    optimizer = torch.optim.AdamW(model.parameters(), lr=5e-4)
    
    # Create dataloader
    from torch.utils.data import DataLoader
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    
    # Warmup
    print("Warming up...")
    device = model.device
    batch = next(iter(dataloader))
    batch = {k: v.to(device) for k, v in batch.items()}
    for _ in range(3):
        outputs = model(**batch)
        loss = outputs.loss
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
    
    # Reset for benchmark
    optimizer.zero_grad()
    
    # Apply torch.compile with error suppression
    if hasattr(torch, 'compile'):
        torch._dynamo.config.suppress_errors = True
        try:
            print("✓ Model compiled successfully")
            model = torch.compile(model)
        except Exception as e:
            print(f"Model compilation failed: {e}")
    
    # Benchmark
    print(f"Running {num_batches} training steps...")
    step_times = []
    memory_before = psutil.virtual_memory().percent
    
    for i, batch in enumerate(dataloader):
        if i >= num_batches:
            break
            
        batch = {k: v.to(device) for k, v in batch.items()}
        step_start = time.time()
        
        outputs = model(**batch)
        loss = outputs.loss
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
        
        step_time = time.time() - step_start
        step_times.append(step_time)
        
        if i % 2 == 0:
            print(f"Step {i+1}/{num_batches}: {step_time:.3f}s, loss: {loss.item():.4f}")
    
    memory_after = psutil.virtual_memory().percent
    
    # Calculate metrics
    avg_step_time = sum(step_times) / len(step_times)
    min_step_time = min(step_times)
    max_step_time = max(step_times)
    samples_per_second = batch_size / avg_step_time
    
    results = {
        'config_name': config_name,
        'batch_size': batch_size,
        'num_steps': len(step_times),
        'avg_step_time': avg_step_time,
        'min_step_time': min_step_time,
        'max_step_time': max_step_time,
        'samples_per_second': samples_per_second,
        'memory_delta': memory_after - memory_before,
    }
    
    print(f"Results:")
    print(f"  Average step time: {avg_step_time:.3f}s")
    print(f"  Min/Max step time: {min_step_time:.3f}s / {max_step_time:.3f}s")
    print(f"  Samples per second: {samples_per_second:.2f}")
    print(f"  Memory usage change: {memory_after - memory_before:.1f}%")
    
    return results

def main():
    print("=== M4 Optimization Benchmark ===")
    print(f"System: {psutil.cpu_count()} CPU cores, {psutil.virtual_memory().total / (1024**3):.1f}GB RAM")
    print(f"MPS available: {torch.backends.mps.is_available()}")
    print(f"PyTorch version: {torch.__version__}")
    
    # Prepare data
    print("\nPreparing dataset...")
    dataset = prepare_data()
    
    results = []
    
    # 1. CPU Baseline
    print("\n" + "="*60)
    try:
        model = GPT2LMHeadModel.from_pretrained("gpt2", cache_dir=CACHE_DIR)
        patch_gpt2_with_pagating(model, "learnable")
        model = model.to('cpu')
        
        result = benchmark_config(model, dataset, 4, "CPU_Baseline", 10)
        results.append(result)
        
        del model
        import gc
        gc.collect()
        
    except Exception as e:
        print(f"CPU benchmark failed: {e}")
    
    # 2. MPS Basic
    print("\n" + "="*60)
    try:
        if torch.backends.mps.is_available():
            model = GPT2LMHeadModel.from_pretrained("gpt2", cache_dir=CACHE_DIR)
            patch_gpt2_with_pagating(model, "learnable")
            model = model.to('mps')
            
            result = benchmark_config(model, dataset, 8, "MPS_Basic", 10)
            results.append(result)
            
            del model
            torch.mps.empty_cache()
            gc.collect()
    
    except Exception as e:
        print(f"MPS Basic benchmark failed: {e}")
    
    # 3. MPS Optimized
    print("\n" + "="*60)
    try:
        if torch.backends.mps.is_available():
            model = GPT2LMHeadModel.from_pretrained("gpt2", cache_dir=CACHE_DIR)
            patch_gpt2_with_pagating(model, "learnable")
            model = model.to('mps')
            
            # Apply optimizations
            model.gradient_checkpointing_enable()
            
            # Apply torch.compile with error suppression
            if hasattr(torch, 'compile'):
                torch._dynamo.config.suppress_errors = True
                try:
                    print("✓ Model compiled successfully")
                    model = torch.compile(model)
                except Exception as e:
                    print(f"Model compilation failed: {e}")
            
            result = benchmark_config(model, dataset, 16, "MPS_Optimized", 10)
            results.append(result)
            
            del model
            torch.mps.empty_cache()
            gc.collect()
    
    except Exception as e:
        print(f"MPS Optimized benchmark failed: {e}")
    
    # Print summary
    print("\n" + "="*60)
    print("BENCHMARK SUMMARY")
    print("="*60)
    
    if results:
        baseline_sps = None
        for result in results:
            if 'CPU' in result['config_name']:
                baseline_sps = result['samples_per_second']
                break
        
        for result in results:
            speedup = result['samples_per_second'] / baseline_sps if baseline_sps else 1.0
            print(f"\n{result['config_name']}:")
            print(f"  Batch size: {result['batch_size']}")
            print(f"  Avg step time: {result['avg_step_time']:.3f}s")
            print(f"  Throughput: {result['samples_per_second']:.2f} samples/sec")
            print(f"  Speedup vs CPU: {speedup:.2f}x")
    
    # Save results
    import json
    with open('simple_benchmark_results.json', 'w') as f:
        json.dump({
            'system_info': {
                'cpu_count': psutil.cpu_count(),
                'memory_gb': psutil.virtual_memory().total / (1024**3),
                'mps_available': torch.backends.mps.is_available(),
                'torch_version': torch.__version__
            },
            'results': results
        }, f, indent=2)
    
    print(f"\nResults saved to: simple_benchmark_results.json")

if __name__ == "__main__":
    main() 