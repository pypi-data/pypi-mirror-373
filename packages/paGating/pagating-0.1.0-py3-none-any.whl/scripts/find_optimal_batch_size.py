import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel, TrainingArguments, Trainer
from datasets import load_dataset
import sys
import os
import gc
import torch._dynamo

# Suppress torch.compile errors and fallback to eager
torch._dynamo.config.suppress_errors = True

# Set HF_HOME environment variable at the beginning
os.environ['HF_HOME'] = os.path.abspath('.cache')
CACHE_DIR = os.environ['HF_HOME']

# Add project root to Python path
sys.path.insert(0, os.path.abspath('.'))
from models.gpt2_pagating_patch import patch_gpt2_with_pagating

def run_test(batch_size, device):
    """Function to run a short training test with a given batch size."""
    print(f"--- Testing Batch Size: {batch_size} ---")
    
    # Clear cache and collect garbage
    torch.mps.empty_cache()
    gc.collect()

    try:
        # 1. Model and Tokenizer
        model = GPT2LMHeadModel.from_pretrained("gpt2", cache_dir=CACHE_DIR)
        patch_gpt2_with_pagating(model, "learnable")
        # if hasattr(torch, 'compile'):
        #     model = torch.compile(model)
        model.to(device)

        tokenizer = GPT2Tokenizer.from_pretrained("gpt2", cache_dir=CACHE_DIR)
        tokenizer.pad_token = tokenizer.eos_token

        # 2. Dataset
        ds = load_dataset("wikitext", "wikitext-103-raw-v1", split='train[:1%]', cache_dir=CACHE_DIR) # Use a small subset
        def tok_fn(ex):
            result = tokenizer(ex["text"], truncation=True, padding="max_length", max_length=128)
            result["labels"] = result["input_ids"].copy()
            return result
        
        tokenized_ds = ds.map(tok_fn, batched=True, remove_columns=["text"])
        tokenized_ds.set_format(type="torch", columns=["input_ids", "attention_mask", "labels"])
        
        # 3. Training Arguments
        training_args = TrainingArguments(
            output_dir=f"./logs/batch_size_test_{batch_size}",
            per_device_train_batch_size=batch_size,
            max_steps=5,  # Only run a few steps to check for memory errors
            logging_steps=1,
            report_to="none", # Disable reporting for this test
            remove_unused_columns=False,
        )

        # 4. Trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=tokenized_ds,
        )

        # 5. Run Training
        trainer.train()
        
        print(f"✅ Batch size {batch_size} SUCCEEDED.")
        return True

    except RuntimeError as e:
        if "out of memory" in str(e):
            print(f"❌ Batch size {batch_size} FAILED: MPS out of memory.")
        else:
            print(f"❌ Batch size {batch_size} FAILED with a runtime error: {e}")
        return False
    except Exception as e:
        print(f"❌ Batch size {batch_size} FAILED with an unexpected error: {e}")
        return False
    finally:
        # Clean up to free memory for the next run
        try:
            del model
            del tokenizer
            del ds
            del tokenized_ds
            del trainer
        except UnboundLocalError:
            pass # A variable was not assigned due to an error
        torch.mps.empty_cache()
        gc.collect()


if __name__ == "__main__":
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    print(f"Using device: {device}")

    if device.type != "mps":
        print("This script is intended for MPS devices. Exiting.")
        sys.exit()

    test_batch_sizes = [4, 8, 12, 16, 24, 32, 48, 64]
    successful_sizes = []

    for bs in test_batch_sizes:
        success = run_test(bs, device)
        if success:
            successful_sizes.append(bs)
        else:
            # If a batch size fails, larger ones are likely to fail too
            print("Stopping test as a batch size failed due to memory.")
            break
            
    if successful_sizes:
        print(f"\n--- Optimal Batch Size ---")
        print(f"The largest successful batch size was: {max(successful_sizes)}")
        print("You can use this value for the --batch_size argument in the main training script.")
    else:
        print("\nCould not find a suitable batch size. Please check your setup.") 