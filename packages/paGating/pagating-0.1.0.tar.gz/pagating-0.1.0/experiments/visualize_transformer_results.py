#!/usr/bin/env python3
"""
Visualize transformer test results from all units.
This script creates a combined visualization of the transformer
test results for easy comparison.
"""

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import os
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Visualize transformer test results')
    parser.add_argument('--alpha', type=float, default=0.5, 
                        help='Alpha value used in test (default: 0.5)')
    parser.add_argument('--output', type=str, default='combined_transformer_results.png',
                        help='Output filename (default: combined_transformer_results.png)')
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Units to include in the visualization
    units = ['paMishU', 'paGLU', 'paGTU', 'paSwishU', 'paReGLU', 'paGELU', 'paSiLU']
    
    # Setup the plot
    fig = plt.figure(figsize=(16, 12))
    fig.suptitle(f'Transformer Test Results (α={args.alpha})', fontsize=16)
    
    # Create subplots for each unit
    for i, unit in enumerate(units):
        ax = fig.add_subplot(3, 3, i + 1)
        filename = f"{unit}_transformer_alpha{args.alpha:.2f}.png"
        
        if os.path.exists(filename):
            # Load and display the image
            img = mpimg.imread(filename)
            ax.imshow(img)
            ax.set_title(unit)
            ax.axis('off')
        else:
            ax.text(0.5, 0.5, f"Missing: {filename}", 
                    horizontalalignment='center',
                    verticalalignment='center')
            ax.axis('off')
    
    # Add a plot with summary info
    ax = fig.add_subplot(3, 3, 8)
    ax.axis('off')
    ax.text(0.5, 0.9, "Comparison Summary:", 
            horizontalalignment='center',
            verticalalignment='center',
            fontsize=12,
            fontweight='bold')
    
    # You could extract test metrics from the image files or from logs
    # For now, we'll just add placeholder text
    ax.text(0.5, 0.6, 
            "These plots show the performance of different\n"
            "paGating units in transformer models with α=0.5.\n\n"
            "All units were tested on a synthetic sequence\n"
            "classification task where the model needs to\n"
            "determine if the sum of the sequence is positive.",
            horizontalalignment='center',
            verticalalignment='center',
            fontsize=10)
    
    # Save the combined figure
    plt.tight_layout(rect=[0, 0, 1, 0.97])  # Adjust for the suptitle
    plt.savefig(args.output, dpi=150)
    print(f"Combined visualization saved to {args.output}")

if __name__ == "__main__":
    main() 