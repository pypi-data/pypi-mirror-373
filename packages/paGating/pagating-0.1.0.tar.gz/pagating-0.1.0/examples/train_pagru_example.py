import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader

# Add project root to path for correct imports
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from paGating.paGRU import PaGRUCell

# --- Configuration ---
INPUT_SIZE = 10
HIDDEN_SIZE = 20
NUM_LAYERS = 1 # PaGRUCell is a single cell, for multi-layer use nn.GRU or manual stacking
OUTPUT_SIZE = 1 # Binary classification
SEQUENCE_LENGTH = 15
BATCH_SIZE = 32
NUM_EPOCHS = 5
LEARNING_RATE = 0.001
NUM_SAMPLES = 1000
ALPHA_MODE = "learnable" # Options: "learnable", float (e.g., 0.5)

# --- Simple RNN Model using PaGRUCell ---
class SimpleRNN(nn.Module):
    def __init__(self, input_size, hidden_size, output_size, alpha_mode):
        super().__init__()
        self.hidden_size = hidden_size
        # Note: PaGRUCell itself is not inherently multi-layer like nn.GRU
        # For multi-layer, you'd stack these manually or wrap them.
        self.pagru_cell = PaGRUCell(input_size, hidden_size, alpha_mode=alpha_mode)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x, hx=None):
        # x shape: (batch_size, seq_len, input_size)
        batch_size = x.size(0)

        if hx is None:
            hx = torch.zeros(batch_size, self.hidden_size).to(x.device)

        # Process sequence step-by-step
        outputs = []
        for t in range(x.size(1)):
            hx = self.pagru_cell(x[:, t, :], hx)
            outputs.append(hx)

        # Use the last hidden state for classification
        last_hidden_state = outputs[-1]
        out = self.fc(last_hidden_state)
        return torch.sigmoid(out) # Sigmoid for binary classification output

# --- Synthetic Dataset ---
class SequenceDataset(Dataset):
    def __init__(self, num_samples, seq_length, input_size):
        self.num_samples = num_samples
        self.seq_length = seq_length
        self.input_size = input_size
        self.data, self.labels = self._generate_data()

    def _generate_data(self):
        # Generate random sequences
        data = torch.randn(self.num_samples, self.seq_length, self.input_size)
        # Label based on whether the sum of the first feature across the sequence is positive
        labels = (torch.sum(data[:, :, 0], dim=1) > 0).float().unsqueeze(1)
        return data, labels

    def __len__(self):
        return self.num_samples

    def __getitem__(self, idx):
        return self.data[idx], self.labels[idx]

# --- Training Loop ---
def train_model():
    print(f"--- Training PaGRU Example ---")
    print(f"Config: Input={INPUT_SIZE}, Hidden={HIDDEN_SIZE}, SeqLen={SEQUENCE_LENGTH}, Alpha='{ALPHA_MODE}'")

    device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
    print(f"Using device: {device}")

    # Data
    train_dataset = SequenceDataset(NUM_SAMPLES, SEQUENCE_LENGTH, INPUT_SIZE)
    test_dataset = SequenceDataset(NUM_SAMPLES // 5, SEQUENCE_LENGTH, INPUT_SIZE) # Smaller test set
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE)

    # Model, Loss, Optimizer
    model = SimpleRNN(INPUT_SIZE, HIDDEN_SIZE, OUTPUT_SIZE, alpha_mode=ALPHA_MODE).to(device)
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

    print(f"Model Parameters:")
    for name, param in model.named_parameters():
        print(f"  {name}: {param.shape}, Requires Grad: {param.requires_grad}")
        if "alpha" in name and ALPHA_MODE == "learnable":
             print(f"    Initial Alpha Value: {param.data.item():.4f}")


    # Training
    for epoch in range(NUM_EPOCHS):
        model.train()
        total_loss = 0
        correct_train = 0
        total_train = 0
        for sequences, labels in train_loader:
            sequences, labels = sequences.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(sequences)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            predicted = (outputs > 0.5).float()
            correct_train += (predicted == labels).sum().item()
            total_train += labels.size(0)

        avg_loss = total_loss / len(train_loader)
        train_acc = 100 * correct_train / total_train
        print(f"Epoch [{epoch+1}/{NUM_EPOCHS}], Loss: {avg_loss:.4f}, Train Acc: {train_acc:.2f}%")
        # Print learnable alphas if applicable
        if ALPHA_MODE == "learnable":
            alpha_r = model.pagru_cell.alpha_r.item()
            alpha_z = model.pagru_cell.alpha_z.item()
            alpha_h = model.pagru_cell.alpha_h.item()
            print(f"  Learned Alphas: r={alpha_r:.4f}, z={alpha_z:.4f}, h={alpha_h:.4f}")


    # Testing
    model.eval()
    correct_test = 0
    total_test = 0
    with torch.no_grad():
        for sequences, labels in test_loader:
            sequences, labels = sequences.to(device), labels.to(device)
            outputs = model(sequences)
            predicted = (outputs > 0.5).float()
            correct_test += (predicted == labels).sum().item()
            total_test += labels.size(0)

    test_acc = 100 * correct_test / total_test
    print(f"--- Results ---")
    print(f"Final Train Accuracy: {train_acc:.2f}%")
    print(f"Final Test Accuracy: {test_acc:.2f}%")

if __name__ == "__main__":
    train_model() 