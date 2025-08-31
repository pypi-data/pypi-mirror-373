#!/usr/bin/env python3.12
from transformers import GPT2Tokenizer, GPT2LMHeadModel, DataCollatorForLanguageModeling, Trainer, TrainingArguments
from datasets import load_dataset

def main():
    # 1. Load WikiText-103
    dataset = load_dataset("wikitext", "wikitext-103-raw-v1")
    # 2. Initialize GPT-2 small
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    model = GPT2LMHeadModel.from_pretrained("gpt2")

    # Set pad_token if not already set (common for GPT-2)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # 3. Tokenize
    def tokenize_fn(examples):
        return tokenizer(examples["text"], return_special_tokens_mask=True, truncation=True, max_length=512)
    tokenized_dataset = dataset.map(tokenize_fn, batched=True, remove_columns=["text"])

    # Filter out empty sequences
    def filter_empty_sequences(examples):
        return [len(x) > 0 for x in examples["input_ids"]]

    filtered_tokenized_dataset = tokenized_dataset.filter(filter_empty_sequences, batched=True)

    # 4. Data collator
    data_collator = DataCollatorForLanguageModeling(tokenizer, mlm=False)
    # 5. Training arguments
    training_args = TrainingArguments(
        output_dir="logs/phase1_baseline",              # store metrics & checkpoints here
        per_device_train_batch_size=1,
        per_device_eval_batch_size=1,
        gradient_accumulation_steps=4,                   # accumulate gradients over 4 steps
        no_cuda=True,                                    # disable CUDA, should fallback to CPU
        num_train_epochs=2,                              # run for 2 epochs
        logging_dir="logs/phase1_baseline/tensorboard",  # TensorBoard logs
        logging_steps=100,
        save_steps=500,
        evaluation_strategy="steps",
    )
    # 6. Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=filtered_tokenized_dataset["train"],
        eval_dataset=filtered_tokenized_dataset["validation"],
        data_collator=data_collator,
    )
    # 7. Run
    trainer.train()
    trainer.save_model("outputs/baseline_gpt2_final")

if __name__ == "__main__":
    main() 