#!/usr/bin/env python3.12
import argparse, pathlib, sys, os

# --- Cache Setup ---
# Set HF_HOME and TRANSFORMERS_CACHE to a local directory
CACHE_DIR = os.path.abspath('.cache')
os.environ['HF_HOME'] = CACHE_DIR
os.environ['TRANSFORMERS_CACHE'] = CACHE_DIR
os.makedirs(CACHE_DIR, exist_ok=True)

from datasets import load_dataset
from transformers import GPT2Tokenizer, TrainingArguments, Trainer, GPT2LMHeadModel
import torch
import torch._dynamo

# Suppress torch.compile errors and fallback to eager
torch._dynamo.config.suppress_errors = True

# Add project root to Python path for models import
sys.path.insert(0, os.path.abspath('.'))
from models.gpt2_pagating_patch import patch_gpt2_with_pagating

parser = argparse.ArgumentParser()
parser.add_argument("--alpha_mode", required=True)
parser.add_argument("--learning_rate", type=float, default=5e-4)
parser.add_argument("--batch_size",  type=int,   default=8)
parser.add_argument("--max_steps",   type=int,   default=20000)
parser.add_argument("--output_dir",  default="logs/phase2_runs")
parser.add_argument("--resume_from_checkpoint", type=str, default=None, help="Path to checkpoint to resume from")
args = parser.parse_args()

run_name = f"pagating_{args.alpha_mode}_lr{args.learning_rate}".replace(".","-")
run_dir  = pathlib.Path(args.output_dir) / run_name
run_dir.mkdir(parents=True, exist_ok=True)

print("Loading dataset …")
tok = GPT2Tokenizer.from_pretrained("gpt2", cache_dir=CACHE_DIR)
tok.pad_token = tok.eos_token  # Fix missing pad_token
ds  = load_dataset("wikitext", "wikitext-103-raw-v1", cache_dir=CACHE_DIR)
def tok_fn(ex): 
    result = tok(ex["text"], truncation=True, padding="max_length", max_length=128)
    # For language modeling, labels should be the same as input_ids
    result["labels"] = result["input_ids"].copy()
    # Filter out empty sequences
    if not result['input_ids'] or len(result['input_ids']) == 0:
        return None
    return result
train = ds["train"].select(range(50_000)).map(tok_fn, batched=True, remove_columns=["text"])
val   = ds["validation"].map(tok_fn, batched=True, remove_columns=["text"])
# Filter None results
train = train.filter(lambda x: x is not None)
val = val.filter(lambda x: x is not None)
train.set_format(type="torch", columns=["input_ids","attention_mask","labels"])
val.set_format(type="torch", columns=["input_ids","attention_mask","labels"])

print("Patching GPT-2 with paGating …")
model = GPT2LMHeadModel.from_pretrained("gpt2", cache_dir=CACHE_DIR)
patch_gpt2_with_pagating(model, args.alpha_mode)
# model.gradient_checkpointing_enable() # Disabled for performance

# if hasattr(torch, 'compile'):
#     print("Compiling model with torch.compile() ...")
#     model = torch.compile(model)

training_args = TrainingArguments(
    output_dir=str(run_dir),
    per_device_train_batch_size=args.batch_size,
    per_device_eval_batch_size=args.batch_size,
    learning_rate=args.learning_rate,
    max_steps=args.max_steps,
    logging_dir=str(run_dir/"tb"),
    logging_steps=200,
    eval_strategy="steps",
    eval_steps=1000,
    save_steps=5000,
    remove_unused_columns=False,
    bf16=False, # Disabled for performance
    use_cpu=not torch.backends.mps.is_available(),
)

trainer = Trainer(model=model, args=training_args, train_dataset=train, eval_dataset=val)

# Resume from checkpoint if specified
if args.resume_from_checkpoint:
    print(f"Resuming training from checkpoint: {args.resume_from_checkpoint}")
    trainer.train(resume_from_checkpoint=args.resume_from_checkpoint)
else:
    trainer.train()

trainer.save_model(run_dir/"final_model") 