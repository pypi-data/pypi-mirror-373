#!/usr/bin/env python
"""
ONNX Export for paGating Units

This script converts paGating activation units to ONNX format for
cross-platform deployment and interoperability.

Usage:
    python onnx_export.py --unit paGELU --alpha 0.5 --input-dim 64 --output-dim 64
    python onnx_export.py --unit paSiLU --alpha 0.5 --opset 17 --verify

Requirements:
    - PyTorch 1.9+
    - onnx
    - onnxruntime (for verification)
    - paGating package

Note:
    - Only static alpha values are supported for ONNX export
    - Use --opset 17 for full mobile compatibility
"""

import os
import sys
import argparse
import torch
import torch.onnx
import numpy as np

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import paGating units
from paGating import (
    paGLU,
    paGTU,
    paSwishU,
    paReGLU,
    paGELU,
    paMishU,
    paSiLU,
    PaGRUCell
)


def get_device():
    """Get the best available device for tracing."""
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    elif torch.cuda.is_available():
        return torch.device("cuda")
    else:
        return torch.device("cpu")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert paGating units to ONNX format"
    )
    
    parser.add_argument(
        "--unit",
        type=str,
        required=True,
        choices=["paGLU", "paGTU", "paSwishU", "paReGLU", "paGELU", "paMishU", "paSiLU", "paGRU"],
        help="paGating unit to export"
    )
    
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.5,
        help="Alpha value for gating (0.0-1.0, default: 0.5). For paGRU, applies to all 3 gates."
    )
    
    parser.add_argument(
        "--input-dim",
        type=int,
        default=64,
        help="Input dimension (default: 64)"
    )
    
    parser.add_argument(
        "--hidden-dim",
        type=int,
        default=64,
        help="Hidden dimension (only used for paGRU) (default: 64)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output path for ONNX model (if not specified, auto-generated)"
    )
    
    parser.add_argument(
        "--opset",
        type=int,
        default=15,
        help="ONNX opset version (default: 15, use 17 for full mobile compatibility)"
    )
    
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify the exported model with ONNX Runtime"
    )
    
    parser.add_argument(
        "--use-gate-norm",
        action="store_true",
        help="Apply GateNorm to the gating pathway"
    )
    
    parser.add_argument(
        "--pre-norm",
        action="store_true",
        help="Apply LayerNorm before the gating unit"
    )
    
    parser.add_argument(
        "--post-norm",
        action="store_true",
        help="Apply LayerNorm after the gating unit"
    )
    
    parser.add_argument(
        "--norm-eps",
        type=float,
        default=1e-5,
        help="Epsilon value for normalization layers (default: 1e-5)"
    )
    
    return parser.parse_args()


def get_output_path(args):
    """Determine the output path for the ONNX model.
    
    Args:
        args: Command line arguments
        
    Returns:
        str: Output path
    """
    # If output path is explicitly specified, use it
    if args.output:
        return args.output
    
    # Create onnx_models directory if it doesn't exist
    os.makedirs("onnx_models", exist_ok=True)
    
    # Auto-generate output path based on unit name
    return f"onnx_models/{args.unit}_alpha{args.alpha:.2f}.onnx"


def export_to_onnx(
    model,
    input_dim,
    output_path,
    opset_version,
    device,
    is_pagru=False,
    hidden_dim=None
):
    """Export the model to ONNX format."""
    # Create example input for tracing
    # Shape (batch_size, input_dim)
    dummy_input = torch.randn(1, input_dim, device=device) 
    
    # Move model to device and set to evaluation mode
    model = model.to(device)
    model.eval()
    
    print(f"Tracing model on {device} for ONNX export...")
    
    # Define output names and dynamic axes
    output_names = ["output"]
    dynamic_axes = {
        "input": {0: "batch_size"},
        "output": {0: "batch_size"}
    }
    
    # Export the model to ONNX
    torch.onnx.export(
        model,                      # model being run
        dummy_input,                # model input (or a tuple for multiple inputs)
        output_path,                # where to save the model
        export_params=True,         # store the trained parameter weights inside the model file
        opset_version=opset_version,# the ONNX version to export the model to
        do_constant_folding=True,   # whether to execute constant folding for optimization
        input_names=["input"],      # the model's input names
        output_names=output_names,    # the model's output names
        dynamic_axes=dynamic_axes,
        verbose=False
    )
    print(f"ONNX model saved to {output_path}")


def verify_onnx_model(model_path, input_dim, device, is_pagru, hidden_dim):
    """Verify the ONNX model using ONNX Runtime."""
    try:
        import onnxruntime as ort
    except ImportError:
        print("\nVerification skipped: onnxruntime is not installed.")
        print("Install it with: pip install onnxruntime")
        return

    print("\nVerifying ONNX model...")
    try:
        # Load the ONNX model
        sess_options = ort.SessionOptions()
        # Set graph optimization level (optional)
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_EXTENDED
        
        # Try to use specific providers if available
        providers = ort.get_available_providers()
        print(f"Available ONNXRuntime providers: {providers}")
        chosen_provider = 'CPUExecutionProvider' # Default fallback
        if 'CUDAExecutionProvider' in providers and device.type == 'cuda':
            chosen_provider = 'CUDAExecutionProvider'
        elif 'CoreMLExecutionProvider' in providers and device.type == 'mps': # MPS often uses CoreML backend
             # Note: CoreML EP might have different compatibility
             # chosen_provider = 'CoreMLExecutionProvider'
             pass # Stick to CPU for broader compatibility unless specifically requested
        
        print(f"Using ONNXRuntime provider: {chosen_provider}")
        session = ort.InferenceSession(model_path, sess_options, providers=[chosen_provider])

        # Get model input name
        input_name = session.get_inputs()[0].name
        output_name = session.get_outputs()[0].name
        print(f"Model Input Name: {input_name}")
        print(f"Model Output Name: {output_name}")

        # Create dummy input (NumPy array)
        dummy_input_np = np.random.randn(1, input_dim).astype(np.float32)

        # Run inference
        outputs = session.run([output_name], {input_name: dummy_input_np})
        
        # Check output shape
        expected_output_dim = hidden_dim if is_pagru else input_dim
        output_shape = outputs[0].shape
        expected_shape = (1, expected_output_dim)
        
        if output_shape == expected_shape:
            print(f"ONNX model output shape is correct: {output_shape}")
        else:
            print(f"Error: ONNX model output shape mismatch! Expected {expected_shape}, Got {output_shape}")
            return

        print("ONNX model verification successful (basic inference check).")

    except Exception as e:
        print(f"Error during ONNX model verification: {e}")
        import traceback
        traceback.print_exc()


# --- Wrapper model for PaGRUCell Export ---
class PaGRUCellWrapper(torch.nn.Module):
    """Wraps a single PaGRUCell step for export compatibility."""
    def __init__(self, input_dim, hidden_dim, alpha):
        super().__init__()
        self.hidden_dim = hidden_dim
        # Instantiate PaGRUCell with static alpha for all gates
        # The actual PaGRUCell expects alpha_mode, so we pass the float directly
        self.cell = PaGRUCell(input_dim, hidden_dim, alpha_mode=alpha, bias=True) 

    def forward(self, x):
        # x shape: (batch_size, input_dim)
        # Create a dummy hidden state inside for single-step execution.
        batch_size = x.shape[0]
        h_0 = torch.zeros(batch_size, self.hidden_dim, device=x.device)
        h_1 = self.cell(x, h_0)
        # Return only the output hidden state
        return h_1


def main():
    # Parse command line arguments
    args = parse_arguments()
    
    # Validate alpha value
    if not 0 <= args.alpha <= 1:
        print(f"Error: Alpha must be between 0 and 1, got {args.alpha}")
        sys.exit(1)
    
    # Get the paGating unit class
    unit_class_map = {
        "paGLU": paGLU,
        "paGTU": paGTU,
        "paSwishU": paSwishU,
        "paReGLU": paReGLU,
        "paGELU": paGELU,
        "paMishU": paMishU,
        "paSiLU": paSiLU,
        "paGRU": PaGRUCellWrapper # Use the locally defined wrapper here
    }
    
    unit_class = unit_class_map.get(args.unit)
    if unit_class is None:
        raise ValueError(f"Unsupported unit: {args.unit}")

    is_pagru = (args.unit == "paGRU")

    if is_pagru:
        # Use the wrapper for export, passing static alpha
        base_unit = unit_class(args.input_dim, args.hidden_dim, alpha=args.alpha)
    else:
        # Instantiate other units (assuming they take input_dim, alpha)
        # This might need adjustment if units have different signatures
        base_unit = unit_class(args.input_dim, args.alpha)
        # Add norm flags if units accept them: , use_gate_norm=args.use_gate_norm, norm_eps=args.norm_eps

    # Apply normalization if requested (only for non-GRU units for now)
    model_layers = []
    if not is_pagru:
        if args.pre_norm:
            model_layers.append(torch.nn.LayerNorm(args.input_dim, eps=args.norm_eps))
        
        model_layers.append(base_unit)
        
        if args.post_norm:
            # Assuming output dim is same as input dim for these activations
            model_layers.append(torch.nn.LayerNorm(args.input_dim, eps=args.norm_eps))
            
        if args.use_gate_norm:
             print("Warning: --use-gate-norm flag is present but this script doesn't explicitly add GateNorm. Ensure the unit handles it internally or use PrePostNormWrapper in a different setup.")
        
        model = torch.nn.Sequential(*model_layers)
    else:
        # For PaGRU, use the wrapper directly
        model = base_unit 

    # Get device for tracing
    device = get_device()
    
    # Determine output path
    output_path = get_output_path(args)
    
    print(f"Exporting {args.unit} with alpha={args.alpha} to ONNX format...")
    print(f"Using device: {device}")
    print(f"ONNX opset version: {args.opset}")
    if is_pagru:
        print(f"Using PaGRUWrapper for {args.unit}")
    if args.pre_norm:
        print(f"Using pre-normalization (LayerNorm)")
    if args.post_norm:
        print(f"Using post-normalization (LayerNorm)")
    
    # Export the model to ONNX
    export_to_onnx(
        model=model,
        input_dim=args.input_dim,
        output_path=output_path,
        opset_version=args.opset,
        device=device,
        is_pagru=is_pagru,
        hidden_dim=args.hidden_dim
    )
    
    # Verify the exported model if requested
    if args.verify:
        verify_onnx_model(output_path, args.input_dim, device, is_pagru, args.hidden_dim)
    
    print("\n✅ ONNX export completed successfully!")


if __name__ == "__main__":
    main() 