#!/usr/bin/env python3
"""
Test script for integrating paGating units into transformer models.
This script builds a simple transformer model with a paGating unit and
tests it on a basic sequence classification task.
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
import matplotlib.pyplot as plt
import argparse
import sys
import os
import random

# Add the parent directory to the path to import paGating
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from paGating import paMishU, paGLU, paGTU, paSwishU, paReGLU, paGELU, paSiLU

# Parse command line arguments
parser = argparse.ArgumentParser(description='Test paGating units in a transformer model')
parser.add_argument('--unit', type=str, default='paMishU', choices=['paMishU', 'paGLU', 'paGTU', 'paSwishU', 'paReGLU', 'paGELU', 'paSiLU'],
                    help='Gating unit to use (default: paMishU)')
parser.add_argument('--alpha', type=float, default=0.5, help='Alpha value for gating unit (default: 0.5)')
parser.add_argument('--batch_size', type=int, default=32, help='Batch size (default: 32)')
parser.add_argument('--epochs', type=int, default=5, help='Number of epochs (default: 5)')
parser.add_argument('--seq_len', type=int, default=16, help='Sequence length (default: 16)')
parser.add_argument('--d_model', type=int, default=64, help='Model dimension (default: 64)')
parser.add_argument('--n_head', type=int, default=4, help='Number of attention heads (default: 4)')
parser.add_argument('--seed', type=int, default=42, help='Random seed (default: 42)')
args = parser.parse_args()

# Set seed for reproducibility
torch.manual_seed(args.seed)
np.random.seed(args.seed)

# Define a simple transformer layer with paGating unit in the feed-forward network
class TransformerLayerWithPaGating(nn.Module):
    def __init__(self, d_model, nhead, unit_name, alpha=0.5):
        super().__init__()
        self.self_attn = nn.MultiheadAttention(d_model, nhead, batch_first=True)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        
        # Create the appropriate paGating unit
        unit_map = {
            'paMishU': paMishU,
            'paGLU': paGLU,
            'paGTU': paGTU,
            'paSwishU': paSwishU, 
            'paReGLU': paReGLU,
            'paGELU': paGELU,
            'paSiLU': paSiLU
        }
        
        self.unit = unit_map[unit_name](d_model, d_model, alpha=alpha)
        
    def forward(self, x, mask=None):
        # Self-attention block
        attn_output, _ = self.self_attn(x, x, x, attn_mask=mask)
        x = self.norm1(x + attn_output)
        
        # Feed-forward block with paGating
        ff_output = self.unit(x)
        x = self.norm2(x + ff_output)
        
        return x

# Simple transformer model for sequence classification
class SimpleTransformer(nn.Module):
    def __init__(self, d_model, nhead, num_layers, num_classes, unit_name, alpha=0.5):
        super().__init__()
        self.embedding = nn.Linear(1, d_model)  # Simple embedding for 1D sequences
        
        self.layers = nn.ModuleList([
            TransformerLayerWithPaGating(d_model, nhead, unit_name, alpha)
            for _ in range(num_layers)
        ])
        
        self.classifier = nn.Linear(d_model, num_classes)
        
    def forward(self, x):
        # x shape: [batch_size, seq_len, 1]
        x = self.embedding(x)
        
        for layer in self.layers:
            x = layer(x)
        
        # Global average pooling
        x = x.mean(dim=1)
        
        # Classification head
        return self.classifier(x)

# Generate a simple synthetic dataset
def generate_synthetic_data(num_samples, seq_len):
    # Generate sequences where the task is to determine if the sum is positive or negative
    data = []
    labels = []
    
    for _ in range(num_samples):
        # Generate a random sequence
        seq = np.random.normal(0, 1, (seq_len, 1)).astype(np.float32)
        
        # The label is 1 if the sum is positive, otherwise 0
        label = 1 if np.sum(seq) > 0 else 0
        
        data.append(seq)
        labels.append(label)
    
    # Convert to PyTorch tensors
    data = torch.tensor(np.array(data))
    labels = torch.tensor(np.array(labels), dtype=torch.long)
    
    return data, labels

def main():
    print(f"Testing {args.unit} with alpha={args.alpha} in a transformer model")
    
    # Generate synthetic data
    train_data, train_labels = generate_synthetic_data(1000, args.seq_len)
    test_data, test_labels = generate_synthetic_data(200, args.seq_len)
    
    # Create data loaders
    train_dataset = TensorDataset(train_data, train_labels)
    test_dataset = TensorDataset(test_data, test_labels)
    
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=args.batch_size)
    
    # Create model
    model = SimpleTransformer(
        d_model=args.d_model,
        nhead=args.n_head,
        num_layers=2,
        num_classes=2,
        unit_name=args.unit,
        alpha=args.alpha
    )
    
    device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
    print(f"Using device: {device}")
    model = model.to(device)
    
    # Define loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    # Training loop
    train_losses = []
    train_accs = []
    
    for epoch in range(args.epochs):
        model.train()
        epoch_loss = 0
        correct = 0
        total = 0
        
        for inputs, targets in train_loader:
            inputs, targets = inputs.to(device), targets.to(device)
            
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item()
            
            _, predicted = outputs.max(1)
            total += targets.size(0)
            correct += predicted.eq(targets).sum().item()
        
        avg_loss = epoch_loss / len(train_loader)
        accuracy = 100.0 * correct / total
        
        train_losses.append(avg_loss)
        train_accs.append(accuracy)
        
        print(f"Epoch {epoch+1}/{args.epochs}, Loss: {avg_loss:.4f}, Accuracy: {accuracy:.2f}%")
    
    # Evaluate on test set
    model.eval()
    test_loss = 0
    correct = 0
    total = 0
    
    with torch.no_grad():
        for inputs, targets in test_loader:
            inputs, targets = inputs.to(device), targets.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            
            test_loss += loss.item()
            
            _, predicted = outputs.max(1)
            total += targets.size(0)
            correct += predicted.eq(targets).sum().item()
    
    avg_test_loss = test_loss / len(test_loader)
    test_accuracy = 100.0 * correct / total
    
    print(f"Test Loss: {avg_test_loss:.4f}, Test Accuracy: {test_accuracy:.2f}%")
    
    # Plot training progress
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    plt.plot(train_losses)
    plt.title(f'Training Loss ({args.unit}, α={args.alpha})')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    
    plt.subplot(1, 2, 2)
    plt.plot(train_accs)
    plt.title(f'Training Accuracy ({args.unit}, α={args.alpha})')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy (%)')
    
    plt.tight_layout()
    # Create experiments directory if it doesn't exist
    os.makedirs('experiments', exist_ok=True)
    
    # Save the plot to the experiments directory
    plot_path = os.path.join('experiments', f"{args.unit}_transformer_alpha{args.alpha:.2f}.png")
    plt.savefig(plot_path)
    print(f"Plot saved to {plot_path}")

if __name__ == "__main__":
    main()
