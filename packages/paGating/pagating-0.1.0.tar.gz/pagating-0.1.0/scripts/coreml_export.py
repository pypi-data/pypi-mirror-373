#!/usr/bin/env python
"""
CoreML Export for paGating Units

This script converts paGating activation units to Apple CoreML format for
deployment on iOS, macOS, and other Apple platforms.

Usage:
    python coreml_export.py --unit paGELU --alpha 0.5 --input-dim 64 --output-dim 64 --output coreml_models/paGELU.mlpackage

Requirements:
    - PyTorch 1.9+
    - coremltools 6.x or higher
    - paGating package

Note:
    - Only static alpha values are supported for CoreML export
    - For coremltools 6.x and higher, models are saved as .mlpackage (ML Program format)
"""

import os
import sys
import argparse
import torch
import coremltools as ct
import traceback

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
        description="Convert paGating units to CoreML format"
    )
    
    parser.add_argument(
        "--unit",
        type=str,
        default="paGELU",
        choices=["paGLU", "paGTU", "paSwishU", "paReGLU", "paGELU", "paMishU", "paSiLU", "paGRU"],
        help="paGating unit to export (default: paGELU)"
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
        help="Hidden dimension (used as output dim for activations, hidden dim for paGRU) (default: 64)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output path for CoreML model (if not specified, auto-generated based on unit and format)"
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


def get_output_path(args, ct_version):
    """Determine the correct output path based on coremltools version.
    
    Args:
        args: Command line arguments
        ct_version: coremltools version number
        
    Returns:
        str: Output path with correct extension
    """
    # If output path is explicitly specified, use it
    if args.output:
        output_path = args.output
        # Check if the extension is correct for the coremltools version
        if ct_version >= 6:
            if not output_path.endswith('.mlpackage'):
                print(f"Warning: For coremltools {ct_version}, the recommended extension is .mlpackage")
                print(f"Changing extension to .mlpackage")
                output_path = os.path.splitext(output_path)[0] + '.mlpackage'
        return output_path
    
    # Auto-generate output path based on unit name and format
    if ct_version >= 6:
        return f"coreml_models/{args.unit}_alpha{args.alpha:.2f}.mlpackage"
    else:
        return f"coreml_models/{args.unit}_alpha{args.alpha:.2f}.mlmodel"


def export_to_coreml(
    model,
    input_dim,
    output_path,
    alpha,
    device,
    is_pagru=False,
    hidden_dim=None
):
    """Export the model to CoreML format."""
    
    # Create example input for tracing
    # For PaGRU, input shape is (batch, input_dim)
    # For others, it's effectively (batch, input_dim) which acts as feature dim
    example_input = torch.randn(1, input_dim, device=device)
    
    # Move model to device and set to evaluation mode
    model = model.to(device)
    model.eval()
    
    print(f"Tracing model on {device}...")
    
    # Trace the model with TorchScript
    traced_model = torch.jit.trace(model, example_input)
    
    # Move back to CPU for CoreML conversion
    traced_model = traced_model.cpu()
    example_input = example_input.cpu()
    
    print(f"Converting to CoreML format...")
    
    # Determine the format based on the output path extension
    compute_units = ct.ComputeUnit.ALL  # Use all available compute units
    
    # Convert to CoreML
    mlmodel = ct.convert(
        traced_model,
        inputs=[
            ct.TensorType(
                name="input",
                shape=example_input.shape
            )
        ],
        compute_precision=ct.precision.FLOAT16,  # Use FP16 for better performance
        minimum_deployment_target=ct.target.macOS13,  # Target macOS 13+ and iOS 16+
    )
    
    # Add model metadata
    mlmodel.author = "paGating"
    mlmodel.license = "MIT"
    mlmodel.version = "1.0"
    mlmodel.short_description = f"{model.__class__.__name__} with α={alpha}"
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save the model
    mlmodel.save(output_path)
    print(f"CoreML model saved to: {output_path}")
    
    # Print model summary
    print(f"\nModel Summary:")
    print(f"  Unit: {model.__class__.__name__}")
    print(f"  Alpha: {alpha}")
    print(f"  Input shape: (batch, {input_dim})")
    print(f"  Output shape: (batch, {hidden_dim if is_pagru else input_dim})")
    
    # For .mlpackage (directory), use du -sh to get size
    if output_path.endswith('.mlpackage'):
        import subprocess
        result = subprocess.run(['du', '-sh', output_path], stdout=subprocess.PIPE)
        size_str = result.stdout.decode('utf-8').split()[0]
        print(f"  Model size: {size_str}")
    else:
        # For .mlmodel (file), use os.path.getsize
        print(f"  Model size: {os.path.getsize(output_path) / (1024 * 1024):.2f} MB")


# --- Wrapper model for PaGRUCell Export ---
class PaGRUCellWrapper(torch.nn.Module):
    """Wraps a single PaGRUCell step for export compatibility."""
    def __init__(self, input_dim, hidden_dim, alpha_mode):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.cell = PaGRUCell(input_dim, hidden_dim, alpha_mode=alpha_mode, bias=True) # Assuming bias=True is standard

    def forward(self, x):
        # x shape: (batch_size, input_dim)
        # CoreML export often expects a single input tensor.
        # We create a dummy hidden state inside.
        batch_size = x.shape[0]
        # Ensure hidden state is created on the same device as input x
        h_0 = torch.zeros(batch_size, self.hidden_dim, device=x.device)
        h_1 = self.cell(x, h_0)
        # Return only the output hidden state to mimic activation function structure
        return h_1


def main():
    """Main function for CoreML export."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Get coremltools version
    try:
        ct_version = int(ct.__version__.split('.')[0])
    except Exception as e:
        print(f"Warning: Could not parse coremltools version. Assuming >= 6. Error: {e}")
        ct_version = 6
    
    # Map unit name to class
    unit_mapping = {
        "paGLU": paGLU,
        "paGTU": paGTU,
        "paSwishU": paSwishU,
        "paReGLU": paReGLU,
        "paGELU": paGELU,
        "paMishU": paMishU,
        "paSiLU": paSiLU,
        "paGRU": PaGRUCellWrapper
    }
    
    unit_class = unit_mapping.get(args.unit)
    if unit_class is None:
        print(f"Error: Unknown unit {args.unit}")
        sys.exit(1)
    
    # Validate alpha
    if not 0 <= args.alpha <= 1:
        print(f"Error: Alpha must be in range [0, 1], got {args.alpha}")
        sys.exit(1)
    
    # Create output directory
    os.makedirs("coreml_models", exist_ok=True)
    
    # Import PrePostNormWrapper if needed
    pre_norm = args.pre_norm
    post_norm = args.post_norm
    use_gate_norm = args.use_gate_norm
    
    if pre_norm or post_norm:
        from paGating import PrePostNormWrapper
    
    # Determine correct output path based on coremltools version
    output_path = get_output_path(args, ct_version)
    
    # Get device for tracing
    device = get_device()
    print(f"Using device: {device}")
    
    # Instantiate the model
    try:
        is_pagru = (args.unit == "paGRU")
        
        # Create base unit/wrapper
        if is_pagru:
            # PaGRUWrapper expects hidden_dim and alpha_mode
            base_unit = unit_class(
                input_dim=args.input_dim,
                hidden_dim=args.hidden_dim,
                alpha_mode=args.alpha # Pass static alpha value directly
            )
        else:
            # Other units expect different args (input_dim, alpha, potentially output_dim if different)
            # Assuming output_dim is same as input_dim for activation units here
            # This part might need adjustment based on how units like paGLU handle dims
            # Let's assume they only need input_dim and alpha for now based on previous code
            base_unit = unit_class(
                input_dim=args.input_dim,
                # output_dim=args.hidden_dim, # Remove output_dim unless needed
                alpha=args.alpha
                # Add use_gate_norm, norm_eps if those units accept them directly
                # Example: use_gate_norm=use_gate_norm, norm_eps=args.norm_eps 
            )

        # Check for dynamic/learnable alpha (only relevant for non-wrapper units)
        if not is_pagru:
             if hasattr(base_unit, "alpha_fn") and getattr(base_unit, 'alpha_fn', None) is not None:
                 print("Warning: Dynamic alpha functions are not supported in CoreML export.")
                 print("Using static alpha value instead.")
             
             if hasattr(base_unit, "alpha_param") and getattr(base_unit, 'alpha_param', None) is not None:
                 print("Warning: Learnable alpha is not supported in CoreML export.")
                 print("Using static alpha value instead.")

        # Wrap with pre/post normalization if requested (should not apply to PaGRUWrapper directly)
        if not is_pagru and (pre_norm or post_norm):
             from paGating import PrePostNormWrapper # Import here if needed
             model = PrePostNormWrapper(
                 module=base_unit,
                 input_dim=args.input_dim,
                 output_dim=args.hidden_dim, # Output dim for LN might need to be input_dim?
                 pre_norm=pre_norm,
                 post_norm=post_norm,
                 norm_eps=args.norm_eps
             )
        else:
             model = base_unit
        
        # Export the model
        print(f"Exporting {args.unit} with alpha={args.alpha}...")
        print(f"Input Dim: {args.input_dim}, Hidden/Output Dim: {args.hidden_dim}")
        print(f"Using device: {device}")
        print(f"CoreMLTools version: {ct.__version__}")
        print(f"Output path: {output_path}")
        
        export_to_coreml(
            model=model,
            input_dim=args.input_dim,
            output_path=output_path,
            alpha=args.alpha,
            device=device,
            is_pagru=args.unit == "paGRU",
            hidden_dim=args.hidden_dim
        )
        
        print("\n✅ CoreML export completed successfully!")
        print(f"\nTest in Xcode or with Apple ML tools using:")
        print(f"  {output_path}")
    
    except Exception as e:
        print(f"Error during export: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    # Print coremltools version for reference
    print(f"coremltools version: {ct.__version__}")
    
    if float('.'.join(ct.__version__.split('.')[:2])) >= 6.0:
        print("Note: Using coremltools 6.x+, which uses ML Program format (.mlpackage)")
    else:
        print("Note: Using coremltools <6.0, which uses Neural Network format (.mlmodel)")
    
    main() 