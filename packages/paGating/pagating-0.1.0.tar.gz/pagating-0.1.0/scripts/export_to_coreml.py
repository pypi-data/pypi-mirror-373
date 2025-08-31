#!/usr/bin/env python3.12
"""
Export a trained paGating model to CoreML for Neural Engine inference.
"""
import argparse
import os
import torch
import coremltools as ct
from transformers import GPT2LMHeadModel
import sys

sys.path.insert(0, os.path.abspath('.'))
from models.gpt2_pagating_patch import patch_gpt2_with_pagating

def main():
    parser = argparse.ArgumentParser(description="Export paGating model to CoreML.")
    parser.add_argument("--model_path", type=str, required=True, help="Path to the trained PyTorch model directory.")
    parser.add_argument("--output_dir", type=str, default="coreml_models", help="Directory to save the CoreML model.")
    parser.add_argument("--alpha_mode", type=str, required=True, help="The alpha mode used during training (e.g., 'learnable').")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    print(f"Loading model from: {args.model_path}")
    model = GPT2LMHeadModel.from_pretrained(args.model_path)
    patch_gpt2_with_pagating(model, args.alpha_mode)
    model.eval()

    class Gpt2Wrapper(torch.nn.Module):
        def __init__(self, model):
            super().__init__()
            self.model = model

        def forward(self, input_ids):
            return self.model(input_ids).logits

    # Trace the model with a dummy input
    # Note: CoreML export requires a fixed input size.
    dummy_input = torch.randint(0, model.config.vocab_size, (1, 128))
    wrapped_model = Gpt2Wrapper(model)
    traced_model = torch.jit.trace(wrapped_model, dummy_input)

    # Convert to CoreML
    print("Converting model to CoreML...")
    mlmodel = ct.convert(
        traced_model,
        inputs=[ct.TensorType(name="input_ids", shape=dummy_input.shape)],
        outputs=[ct.TensorType(name="logits")],
        convert_to="mlprogram",
        compute_units=ct.ComputeUnit.ALL,
    )

    # Save the CoreML model
    output_path = os.path.join(args.output_dir, f"pagating_{args.alpha_mode}.mlpackage")
    print(f"Saving CoreML model to: {output_path}")
    mlmodel.save(output_path)

    print("CoreML export complete.")
    print(f"Model saved at: {output_path}")

if __name__ == "__main__":
    main()