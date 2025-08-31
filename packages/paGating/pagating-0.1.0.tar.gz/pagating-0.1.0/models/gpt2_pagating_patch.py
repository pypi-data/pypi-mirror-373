"""Patch a HuggingFace GPT-2 model so its MLP uses paGating units."""
import torch.nn as nn
import sys
import os

# Add the project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from transformers import GPT2LMHeadModel
from paGating import paGLU
from paGating import alpha_schedulers

def _parse_alpha_mode(alpha_mode: str):
    if alpha_mode.startswith("static_"):
        return float(alpha_mode.split("_")[1]), None
    if alpha_mode == "learnable":
        return "learnable", None
    if alpha_mode == "scheduler_cosine":
        return 0.0, "cosine"
    raise ValueError(f"Unsupported alpha_mode: {alpha_mode}")

def patch_gpt2_with_pagating(model: GPT2LMHeadModel, alpha_mode: str):
    alpha_init, scheduler_name = _parse_alpha_mode(alpha_mode)

    class PaGatingMLP(nn.Module):
        def __init__(self, d_model: int, d_ff: int):
            super().__init__()
            self.fc_in = nn.Linear(d_model, d_ff)
            if scheduler_name:
                # Use the scheduler as the alpha parameter
                alpha_scheduler = alpha_schedulers.CosineAlphaScheduler(max_steps=20000)
                self.act = paGLU(input_dim=d_ff, output_dim=d_ff, alpha=alpha_scheduler)
            else:
                # Use static or learnable alpha
                self.act = paGLU(input_dim=d_ff, output_dim=d_ff, alpha=alpha_init)
            self.fc_out = nn.Linear(d_ff, d_model)

        def forward(self, x):
            return self.fc_out(self.act(self.fc_in(x)))

    for blk in model.transformer.h:
        d_model = blk.mlp.c_fc.nx
        d_ff = blk.mlp.c_fc.nf
        blk.mlp = PaGatingMLP(d_model, d_ff)

    return model 