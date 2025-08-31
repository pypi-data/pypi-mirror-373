import torch
import torch.nn as nn
import torch.nn.functional as F
import math
from typing import Optional, Tuple

# Helper functions for parameterized activations within GRU
def PaSigmoid(x: torch.Tensor, alpha: torch.Tensor) -> torch.Tensor:
    """ Parameterized Sigmoid: sigmoid(alpha * x) """
    # Ensure alpha is broadcastable
    if isinstance(alpha, torch.Tensor) and alpha.numel() == 1:
        return torch.sigmoid(alpha.item() * x)
    elif isinstance(alpha, float):
         return torch.sigmoid(alpha * x)
    else: # Should not happen with current setup, but handles tensor alpha if needed
         return torch.sigmoid(alpha * x) 

def PaTanh(x: torch.Tensor, alpha: torch.Tensor) -> torch.Tensor:
    """ Parameterized Tanh: tanh(alpha * x) """
    if isinstance(alpha, torch.Tensor) and alpha.numel() == 1:
        return torch.tanh(alpha.item() * x)
    elif isinstance(alpha, float):
        return torch.tanh(alpha * x)
    else:
        return torch.tanh(alpha * x)

# Placeholder for the main class
class PaGRUCell(nn.Module):
    """An Parameterized Adaptive Gated Recurrent Unit (PaGRU) cell.

    Differs from standard GRUCell by using parameterized sigmoid and tanh functions
    for the reset gate, update gate, and new gate, controlled by learnable or static
    alpha parameters.

    PaSigmoid(x, alpha) = sigmoid(alpha * x)
    PaTanh(x, alpha) = tanh(alpha * x)

    r_t = PaSigmoid(W_{ir}x_t + b_{ir} + W_{hr}h_{t-1} + b_{hr}, alpha_r)
    z_t = PaSigmoid(W_{iz}x_t + b_{iz} + W_{hz}h_{t-1} + b_{hz}, alpha_z)
    n_t = PaTanh(W_{in}x_t + b_{in} + r_t * (W_{hn}h_{t-1} + b_{hn}), alpha_h)
    h_t = (1 - z_t) * n_t + z_t * h_{t-1}

    Args:
        input_size (int): The number of expected features in the input x
        hidden_size (int): The number of features in the hidden state h
        bias (bool): If ``False``, then the layer does not use bias weights. Default: ``True``
        alpha_mode (str | float): Controls the alpha parameters. 
            - If "learnable" (default), creates learnable `alpha_r`, `alpha_z`, `alpha_h` parameters initialized to 1.0.
            - If a float, uses this static value for all three alpha parameters.
        device: The device tensors will be moved to. Default: ``None``
        dtype: The data type for tensors. Default: ``None``
    """
    def __init__(self, input_size: int, hidden_size: int, bias: bool = True,
                 alpha_mode: str | float = "learnable", 
                 device=None, dtype=None) -> None:
        factory_kwargs = {'device': device, 'dtype': dtype}
        super().__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.bias = bias
        self.alpha_mode = alpha_mode

        # Weights and biases (combined similar to torch.nn.GRUCell)
        self.weight_ih = nn.Parameter(torch.empty((3 * hidden_size, input_size), **factory_kwargs))
        self.weight_hh = nn.Parameter(torch.empty((3 * hidden_size, hidden_size), **factory_kwargs))
        if bias:
            self.bias_ih = nn.Parameter(torch.empty(3 * hidden_size, **factory_kwargs))
            self.bias_hh = nn.Parameter(torch.empty(3 * hidden_size, **factory_kwargs))
        else:
            self.register_parameter('bias_ih', None)
            self.register_parameter('bias_hh', None)

        # Alpha parameters based on mode
        if self.alpha_mode == "learnable":
            self.alpha_r = nn.Parameter(torch.tensor(1.0, **factory_kwargs))
            self.alpha_z = nn.Parameter(torch.tensor(1.0, **factory_kwargs))
            self.alpha_h = nn.Parameter(torch.tensor(1.0, **factory_kwargs))
            self._alpha_r_static = None
            self._alpha_z_static = None
            self._alpha_h_static = None
        elif isinstance(self.alpha_mode, (float, int)):
            if not 0.0 <= self.alpha_mode <= 1.0:
                 print(f"Warning: Static alpha value {self.alpha_mode} is outside the typical [0, 1] range.")
            # Store static alpha, register None for parameters
            self._alpha_r_static = float(self.alpha_mode)
            self._alpha_z_static = float(self.alpha_mode)
            self._alpha_h_static = float(self.alpha_mode)
            self.register_parameter('alpha_r', None)
            self.register_parameter('alpha_z', None)
            self.register_parameter('alpha_h', None)
        else:
            raise ValueError(f"Invalid alpha_mode: {self.alpha_mode}. Must be 'learnable' or a float/int.")

        self.reset_parameters()

    def extra_repr(self) -> str:
        s = 'input_size={input_size}, hidden_size={hidden_size}, bias={bias}'.format(**self.__dict__)
        if self.alpha_mode == "learnable":
            s += ', alpha_mode=learnable'
        else:
            s += f', alpha_mode=static({self._alpha_r_static})'
        return s

    def reset_parameters(self) -> None:
        # Standard PyTorch GRU initialization for weights/biases
        stdv = 1.0 / math.sqrt(self.hidden_size) if self.hidden_size > 0 else 0
        for name, param in self.named_parameters():
            if param is None: # Skip None parameters (e.g., static alphas)
                 continue
            if 'weight' in name:
                nn.init.uniform_(param, -stdv, stdv)
            elif 'bias' in name:
                nn.init.uniform_(param, -stdv, stdv)
            elif 'alpha' in name: # Only reset learnable alphas
                 if self.alpha_mode == "learnable":
                      with torch.no_grad():
                           param.fill_(1.0)

    def forward(self, input: torch.Tensor, hx: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Performs a forward pass of the PaGRU cell.

        Args:
            input (torch.Tensor): Tensor of shape (batch, input_size).
            hx (Optional[torch.Tensor]): Tensor of shape (batch, hidden_size).

        Returns:
            torch.Tensor: Tensor of shape (batch, hidden_size).
        """
        if hx is None:
            hx = torch.zeros(input.size(0), self.hidden_size, dtype=input.dtype, device=input.device)

        # Linear transformations
        gi = F.linear(input, self.weight_ih, self.bias_ih)
        gh = F.linear(hx, self.weight_hh, self.bias_hh)
        i_r, i_z, i_n = gi.chunk(3, 1)
        h_r, h_z, h_n = gh.chunk(3, 1)

        # Determine which alpha values to use
        alpha_r = self.alpha_r if self.alpha_mode == "learnable" else self._alpha_r_static
        alpha_z = self.alpha_z if self.alpha_mode == "learnable" else self._alpha_z_static
        alpha_h = self.alpha_h if self.alpha_mode == "learnable" else self._alpha_h_static

        # Calculate gates using Parameterized Activations
        resetgate = PaSigmoid(i_r + h_r, alpha_r)
        updategate = PaSigmoid(i_z + h_z, alpha_z)
        newgate = PaTanh(i_n + resetgate * h_n, alpha_h)

        # Calculate next hidden state
        hy = newgate + updategate * (hx - newgate)

        return hy 