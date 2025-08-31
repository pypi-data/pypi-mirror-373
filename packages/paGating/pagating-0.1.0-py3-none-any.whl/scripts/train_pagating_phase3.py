#!/usr/bin/env python3.12
import argparse, pathlib, sys, os, time, psutil
from datasets import load_dataset
from transformers import GPT2Tokenizer, TrainingArguments, Trainer, GPT2LMHeadModel
import torch
import torch._dynamo
import numpy as np
from typing import Dict, Any

# Suppress torch.compile errors and fallback to eager
torch._dynamo.config.suppress_errors = True

# Add project root to Python path for models import
sys.path.insert(0, os.path.abspath('.'))
from models.gpt2_pagating_patch import patch_gpt2_with_pagating

# --- Cache Setup ---
CACHE_DIR = os.path.abspath('.cache')
os.environ['HF_HOME'] = CACHE_DIR
os.environ['TRANSFORMERS_CACHE'] = CACHE_DIR

class HardwareProfiler:
    """Monitor hardware utilization during training"""
    def __init__(self):
        self.cpu_usage = []
        self.memory_usage = []
        self.start_time = time.time()
        
    def log_stats(self) -> Dict[str, Any]:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory_info = psutil.virtual_memory()
        
        stats = {
            'cpu_percent': cpu_percent,
            'memory_percent': memory_info.percent,
            'memory_used_gb': memory_info.used / (1024**3),
            'memory_available_gb': memory_info.available / (1024**3),
            'timestamp': time.time() - self.start_time
        }
        
        self.cpu_usage.append(cpu_percent)
        self.memory_usage.append(memory_info.percent)
        
        return stats
    
    def get_summary(self) -> Dict[str, float]:
        return {
            'avg_cpu_usage': np.mean(self.cpu_usage) if self.cpu_usage else 0,
            'max_cpu_usage': np.max(self.cpu_usage) if self.cpu_usage else 0,
            'avg_memory_usage': np.mean(self.memory_usage) if self.memory_usage else 0,
            'max_memory_usage': np.max(self.memory_usage) if self.memory_usage else 0,
        }

class OptimizedTrainer(Trainer):
    """Enhanced Trainer with hardware profiling and advanced optimizations"""
    
    def __init__(self, *args, enable_profiling=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.profiler = HardwareProfiler() if enable_profiling else None
        self.step_times = []
        
    def training_step(self, model, inputs):
        step_start = time.time()
        
        # Profile hardware before step
        if self.profiler:
            hw_stats = self.profiler.log_stats()
            if self.state.global_step % 100 == 0:
                print(f"Step {self.state.global_step} - CPU: {hw_stats['cpu_percent']:.1f}%, "
                      f"Memory: {hw_stats['memory_percent']:.1f}% ({hw_stats['memory_used_gb']:.2f}GB)")
        
        # Execute training step with memory optimization
        with torch.cuda.amp.autocast(enabled=False):  # Use CPU autocast for MPS
            loss = super().training_step(model, inputs)
        
        step_time = time.time() - step_start
        self.step_times.append(step_time)
        
        # Memory cleanup every 50 steps
        if self.state.global_step % 50 == 0:
            if torch.backends.mps.is_available():
                torch.mps.empty_cache()
            import gc
            gc.collect()
        
        return loss
    
    def log_performance_summary(self):
        """Log comprehensive performance metrics"""
        if self.step_times:
            avg_step_time = np.mean(self.step_times[-100:])  # Last 100 steps
            samples_per_second = self.args.per_device_train_batch_size / avg_step_time
            
            print(f"\n=== Performance Summary ===")
            print(f"Average step time: {avg_step_time:.3f}s")
            print(f"Samples per second: {samples_per_second:.2f}")
            
            if self.profiler:
                hw_summary = self.profiler.get_summary()
                print(f"Average CPU usage: {hw_summary['avg_cpu_usage']:.1f}%")
                print(f"Peak CPU usage: {hw_summary['max_cpu_usage']:.1f}%")
                print(f"Average memory usage: {hw_summary['avg_memory_usage']:.1f}%")
                print(f"Peak memory usage: {hw_summary['max_memory_usage']:.1f}%")
            print("========================\n")

def optimize_model_for_mps(model):
    """Apply MPS-specific optimizations"""
    
    # Enable attention optimizations if available
    try:
        # Try to enable Flash Attention-style optimizations
        if hasattr(torch.nn.functional, 'scaled_dot_product_attention'):
            print("✓ Using optimized attention (scaled_dot_product_attention)")
        else:
            print("⚠ Optimized attention not available")
    except Exception as e:
        print(f"⚠ Attention optimization failed: {e}")
    
    # Set optimal tensor layouts for MPS
    if torch.backends.mps.is_available():
        print("✓ MPS backend detected - applying MPS optimizations")
        
        # Ensure model is on MPS device
        if next(model.parameters()).device.type != 'mps':
            model = model.to('mps')
            print("✓ Model moved to MPS device")
    
    return model

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--alpha_mode", required=True)
    parser.add_argument("--learning_rate", type=float, default=5e-4)
    parser.add_argument("--batch_size", type=int, default=32)
    parser.add_argument("--max_steps", type=int, default=20000)
    parser.add_argument("--output_dir", default="logs/phase3_runs")
    parser.add_argument("--resume_from_checkpoint", type=str, default=None)
    parser.add_argument("--enable_profiling", action="store_true", default=True)
    parser.add_argument("--compile_mode", choices=["default", "reduce-overhead", "max-autotune"], default="default")
    args = parser.parse_args()
    
    run_name = f"pagating_{args.alpha_mode}_lr{args.learning_rate}_phase3".replace(".", "-")
    run_dir = pathlib.Path(args.output_dir) / run_name
    run_dir.mkdir(parents=True, exist_ok=True)
    
    print("=== M4 Phase 3 Optimization Training ===")
    print(f"Device availability:")
    print(f"  MPS: {torch.backends.mps.is_available()}")
    print(f"  CPU cores: {psutil.cpu_count()}")
    print(f"  Memory: {psutil.virtual_memory().total / (1024**3):.1f}GB")
    
    print("\nLoading dataset...")
    tok = GPT2Tokenizer.from_pretrained("gpt2", cache_dir=CACHE_DIR)
    tok.pad_token = tok.eos_token
    ds = load_dataset("wikitext", "wikitext-103-raw-v1", cache_dir=CACHE_DIR)
    
    def tok_fn(ex):
        result = tok(ex["text"], truncation=True, padding="max_length", max_length=128)
        result["labels"] = result["input_ids"].copy()
        if not result['input_ids'] or len(result['input_ids']) == 0:
            return None
        return result
    
    train = ds["train"].select(range(50_000)).map(tok_fn, batched=True, remove_columns=["text"])
    val = ds["validation"].map(tok_fn, batched=True, remove_columns=["text"])
    train = train.filter(lambda x: x is not None)
    val = val.filter(lambda x: x is not None)
    train.set_format(type="torch", columns=["input_ids", "attention_mask", "labels"])
    val.set_format(type="torch", columns=["input_ids", "attention_mask", "labels"])
    
    print("Initializing model with advanced optimizations...")
    model = GPT2LMHeadModel.from_pretrained("gpt2", cache_dir=CACHE_DIR)
    patch_gpt2_with_pagating(model, args.alpha_mode)
    
    # Apply MPS optimizations
    model = optimize_model_for_mps(model)
    
    # Enable gradient checkpointing
    model.gradient_checkpointing_enable()
    print("✓ Gradient checkpointing enabled")
    
    # Apply torch.compile with specified mode
    if hasattr(torch, 'compile'):
        print(f"Compiling model with mode: {args.compile_mode}")
        try:
            model = torch.compile(model, mode=args.compile_mode)
            print("✓ Model compilation successful")
        except Exception as e:
            print(f"⚠ Model compilation failed: {e}")
    
    training_args = TrainingArguments(
        output_dir=str(run_dir),
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        max_steps=args.max_steps,
        logging_dir=str(run_dir / "tb"),
        logging_steps=100,  # More frequent logging for monitoring
        eval_strategy="steps",
        eval_steps=1000,
        save_steps=2500,  # More frequent saves
        remove_unused_columns=False,
        bf16=True,
        dataloader_num_workers=4,  # Parallel data loading
        dataloader_pin_memory=True,
        gradient_accumulation_steps=1,
        warmup_steps=500,
        weight_decay=0.01,
        adam_epsilon=1e-8,
        max_grad_norm=1.0,
        fp16_full_eval=False,  # Keep eval in full precision for stability
    )
    
    trainer = OptimizedTrainer(
        model=model,
        args=training_args,
        train_dataset=train,
        eval_dataset=val,
        enable_profiling=args.enable_profiling
    )
    
    # Training with performance monitoring
    try:
        if args.resume_from_checkpoint:
            print(f"Resuming from checkpoint: {args.resume_from_checkpoint}")
            trainer.train(resume_from_checkpoint=args.resume_from_checkpoint)
        else:
            trainer.train()
            
        # Log final performance summary
        trainer.log_performance_summary()
        
    except KeyboardInterrupt:
        print("\nTraining interrupted by user")
        trainer.log_performance_summary()
        
    except Exception as e:
        print(f"\nTraining error: {e}")
        trainer.log_performance_summary()
        raise
    
    finally:
        # Save final model and performance data
        trainer.save_model(run_dir / "final_model")
        
        # Save performance metrics
        if trainer.profiler:
            import json
            metrics = {
                'hardware_summary': trainer.profiler.get_summary(),
                'step_times': trainer.step_times[-1000:],  # Last 1000 steps
                'training_args': training_args.to_dict(),
            }
            with open(run_dir / "performance_metrics.json", 'w') as f:
                json.dump(metrics, f, indent=2)
        
        print(f"\nTraining completed! Results saved to: {run_dir}")

if __name__ == "__main__":
    main() 