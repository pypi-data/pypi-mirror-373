#!/usr/bin/env python3.12
import itertools, subprocess, yaml, pathlib, sys
CFG = pathlib.Path("configs/gpt2_pagating_alpha_sweep.yaml")
cfg = yaml.safe_load(CFG.read_text())

grid_keys = list(cfg["grid"].keys())
grid_vals = list(cfg["grid"].values())
combos = list(itertools.product(*grid_vals))
print(f"Launching {len(combos)} runs …")

dry_run = "--dry-run" in sys.argv

for combo in combos:
    params = dict(zip(grid_keys, combo))
    cmd = [
        "python3.12", "scripts/train_pagating.py",
        "--alpha_mode",   params["alpha_mode"],
        "--learning_rate", str(params["learning_rate"]),
        "--batch_size",    str(params["batch_size"]),
        "--max_steps",     str(cfg.get("max_steps",20000)),
        "--output_dir",    cfg.get("output_root","logs/phase2_sweeps"),
    ]
    print(">>>", " ".join(cmd))
    if not dry_run:
        subprocess.run(cmd, check=True) 