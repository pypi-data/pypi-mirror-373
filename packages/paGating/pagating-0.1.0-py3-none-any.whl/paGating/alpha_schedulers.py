"""
Alpha schedulers for the paGating framework.

This module provides various schedulers to dynamically control the alpha parameter
in paGating units. Alpha (α) determines the strength of gating, with α=0 representing
no gating and α=1 representing full gating.

Schedulers can be based on:
1. Fixed values
2. Learnable parameters
3. Training progress (steps/epochs)
4. Input characteristics (entropy, confidence)
"""

import math
from typing import Union, Callable, Optional, Dict, Any

import torch
import torch.nn as nn
import torch.nn.functional as F


class ConstantAlpha:
    """Simple scheduler that always returns a fixed alpha value.
    
    Formula: α = constant
    
    Args:
        alpha (float): Fixed alpha value to return, must be in range [0, 1]
    """
    
    def __init__(self, alpha: float = 0.5) -> None:
        if not 0 <= alpha <= 1:
            raise ValueError(f"Alpha must be between 0 and 1, got {alpha}")
        self.alpha = alpha
    
    def __call__(self, x: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Return the constant alpha value regardless of input.
        
        Args:
            x (Optional[torch.Tensor]): Ignored, included for API consistency
            
        Returns:
            torch.Tensor: Scalar tensor with constant alpha value
        """
        return torch.tensor(self.alpha, dtype=torch.float32)


class LearnableAlpha:
    """Scheduler based on a learnable parameter.
    
    Alpha is computed as: α = sigmoid(learnable_param)
    
    This ensures alpha stays in the range [0, 1] while allowing
    unconstrained optimization of the parameter.
    
    Args:
        initial_value (float, optional): Initial value for the parameter
            before sigmoid. Default: 0.0 (which maps to α=0.5)
    """
    
    def __init__(self, initial_value: float = 0.0) -> None:
        self.alpha_param = nn.Parameter(torch.tensor(initial_value, dtype=torch.float32))
    
    def __call__(self, x: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Return the current value of the learnable alpha parameter.
        
        Args:
            x (Optional[torch.Tensor]): Ignored, included for API consistency
            
        Returns:
            torch.Tensor: Scalar tensor with current alpha value
        """
        return torch.sigmoid(self.alpha_param)
    
    def parameters(self):
        """Return the learnable parameter for optimizer integration."""
        return [self.alpha_param]


class CosineAlphaScheduler:
    """Scheduler that follows a cosine decay curve based on training progress.
    
    Formula: α(t) = 0.5 * (1 + cos(π * t / T))
    
    Where:
    - t: Current step
    - T: Maximum number of steps
    
    This produces a smooth curve from 1 to 0 over the course of training.
    
    Args:
        max_steps (int): Total number of steps in the schedule
        min_alpha (float, optional): Minimum alpha value. Default: 0.0
        max_alpha (float, optional): Maximum alpha value. Default: 1.0
        reverse (bool, optional): If True, alpha starts at min_alpha and 
            increases to max_alpha. Default: False
    """
    
    def __init__(
        self, 
        max_steps: int,
        min_alpha: float = 0.0,
        max_alpha: float = 1.0,
        reverse: bool = False
    ) -> None:
        self.max_steps = max_steps
        self.min_alpha = min_alpha
        self.max_alpha = max_alpha
        self.reverse = reverse
        self.current_step = 0
    
    def step(self) -> None:
        """Increment the current step counter."""
        self.current_step = min(self.current_step + 1, self.max_steps)
    
    def __call__(self, x: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Calculate the current alpha value based on cosine schedule.
        
        Args:
            x (Optional[torch.Tensor]): Ignored, included for API consistency
            
        Returns:
            torch.Tensor: Scalar tensor with current alpha value
        """
        if self.max_steps <= 0:
            return torch.tensor(self.max_alpha if self.reverse else self.min_alpha)
        
        # Calculate raw cosine value (ranges from 1 at step 0 to -1 at max_steps)
        cosine = math.cos(math.pi * self.current_step / self.max_steps)
        
        # Convert to alpha range [0, 1]
        alpha = 0.5 * (1 + cosine)
        
        # Scale to [min_alpha, max_alpha]
        alpha = self.min_alpha + (self.max_alpha - self.min_alpha) * alpha
        
        # Reverse if needed
        if self.reverse:
            alpha = self.max_alpha - alpha + self.min_alpha
            
        return torch.tensor(alpha, dtype=torch.float32)
    
    def set_step(self, step: int) -> None:
        """Manually set the current step.
        
        Args:
            step (int): Step to set
        """
        self.current_step = min(max(0, step), self.max_steps)


class EntropyBasedAlpha:
    """Scheduler that computes alpha based on input entropy.
    
    Higher entropy in the input → higher alpha value.
    The intuition is that more uncertain/complex inputs benefit from stronger gating.
    
    Formula: α = min(1, max(0, scale * entropy(softmax(x)) / log(dim)))
    
    Where entropy is normalized by log(dim) to range [0, 1]
    
    Args:
        scale (float, optional): Scaling factor for the entropy. Default: 1.0
        temperature (float, optional): Temperature for softmax. Lower values 
            make the softmax more peaked. Default: 1.0
        min_alpha (float, optional): Minimum alpha value. Default: 0.0
        max_alpha (float, optional): Maximum alpha value. Default: 1.0
    """
    
    def __init__(
        self, 
        scale: float = 1.0,
        temperature: float = 1.0,
        min_alpha: float = 0.0,
        max_alpha: float = 1.0
    ) -> None:
        self.scale = scale
        self.temperature = temperature
        self.min_alpha = min_alpha
        self.max_alpha = max_alpha
    
    def __call__(self, x: torch.Tensor) -> torch.Tensor:
        """Calculate alpha based on the entropy of the input.
        
        Args:
            x (torch.Tensor): Input tensor
            
        Returns:
            torch.Tensor: Batch of alpha values corresponding to input entropy
        """
        # Apply softmax to get probability distribution
        probs = F.softmax(x / self.temperature, dim=-1)
        
        # Calculate entropy: -sum(p * log(p))
        # Adding small epsilon to avoid log(0)
        entropy = -torch.sum(probs * torch.log(probs + 1e-10), dim=-1)
        
        # Normalize by maximum possible entropy (log of dimension)
        log_dim = math.log(x.size(-1))
        normalized_entropy = entropy / log_dim
        
        # Scale and clip to [min_alpha, max_alpha]
        alpha = self.scale * normalized_entropy
        alpha = torch.clamp(alpha, min=self.min_alpha, max=self.max_alpha)
        
        return alpha


class ConfidenceBasedAlpha:
    """Scheduler that computes alpha based on prediction confidence.
    
    Lower confidence → higher alpha value.
    The intuition is that less confident predictions benefit from stronger gating.
    
    Formula: α = scale * (1 - max(softmax(x)))
    
    Args:
        scale (float, optional): Scaling factor for the confidence. Default: 1.0
        temperature (float, optional): Temperature for softmax. Default: 1.0
        min_alpha (float, optional): Minimum alpha value. Default: 0.0
        max_alpha (float, optional): Maximum alpha value. Default: 1.0
    """
    
    def __init__(
        self, 
        scale: float = 1.0,
        temperature: float = 1.0,
        min_alpha: float = 0.0,
        max_alpha: float = 1.0
    ) -> None:
        self.scale = scale
        self.temperature = temperature
        self.min_alpha = min_alpha
        self.max_alpha = max_alpha
    
    def __call__(self, x: torch.Tensor) -> torch.Tensor:
        """Calculate alpha based on the confidence of predictions.
        
        Args:
            x (torch.Tensor): Input tensor
            
        Returns:
            torch.Tensor: Batch of alpha values corresponding to prediction confidence
        """
        # Apply softmax to get probability distribution
        probs = F.softmax(x / self.temperature, dim=-1)
        
        # Get max probability as confidence measure
        confidence = torch.max(probs, dim=-1)[0]
        
        # Alpha is inversely related to confidence
        alpha = self.scale * (1 - confidence)
        
        # Clip to [min_alpha, max_alpha]
        alpha = torch.clamp(alpha, min=self.min_alpha, max=self.max_alpha)
        
        return alpha


class LinearRampScheduler:
    """Scheduler that linearly increases alpha from start to end over warmup steps.
    
    Formula: α(t) = min_alpha + (max_alpha - min_alpha) * min(t / warmup_steps, 1)
    
    Args:
        warmup_steps (int): Number of steps for the linear warmup
        min_alpha (float, optional): Starting alpha value. Default: 0.0
        max_alpha (float, optional): Final alpha value. Default: 1.0
        reverse (bool, optional): If True, alpha starts at max_alpha and 
            decreases to min_alpha. Default: False
    """
    
    def __init__(
        self, 
        warmup_steps: int,
        min_alpha: float = 0.0,
        max_alpha: float = 1.0,
        reverse: bool = False
    ) -> None:
        self.warmup_steps = warmup_steps
        self.min_alpha = min_alpha
        self.max_alpha = max_alpha
        self.reverse = reverse
        self.current_step = 0
    
    def step(self) -> None:
        """Increment the current step counter."""
        self.current_step += 1
    
    def __call__(self, x: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Calculate the current alpha value based on linear schedule.
        
        Args:
            x (Optional[torch.Tensor]): Ignored, included for API consistency
            
        Returns:
            torch.Tensor: Scalar tensor with current alpha value
        """
        if self.warmup_steps <= 0:
            return torch.tensor(self.max_alpha if self.reverse else self.min_alpha)
        
        # Calculate progress ratio (capped at 1.0)
        progress = min(self.current_step / self.warmup_steps, 1.0)
        
        # Calculate alpha based on progress
        if self.reverse:
            alpha = self.max_alpha - progress * (self.max_alpha - self.min_alpha)
        else:
            alpha = self.min_alpha + progress * (self.max_alpha - self.min_alpha)
            
        return torch.tensor(alpha, dtype=torch.float32)
    
    def set_step(self, step: int) -> None:
        """Manually set the current step.
        
        Args:
            step (int): Step to set
        """
        self.current_step = max(0, step)


def get_scheduler(name: str, **kwargs) -> Callable:
    """Factory method to retrieve an alpha scheduler by name.
    
    Args:
        name (str): Name of the scheduler to retrieve. Options:
            - 'constant': ConstantAlpha
            - 'learnable': LearnableAlpha
            - 'cosine': CosineAlphaScheduler
            - 'entropy': EntropyBasedAlpha
            - 'confidence': ConfidenceBasedAlpha
            - 'linear': LinearRampScheduler
        **kwargs: Arguments to pass to the scheduler constructor
        
    Returns:
        Callable: An initialized alpha scheduler object
        
    Raises:
        ValueError: If the scheduler name is not recognized
    """
    schedulers: Dict[str, Any] = {
        'constant': ConstantAlpha,
        'learnable': LearnableAlpha,
        'cosine': CosineAlphaScheduler,
        'entropy': EntropyBasedAlpha,
        'confidence': ConfidenceBasedAlpha,
        'linear': LinearRampScheduler,
    }
    
    if name not in schedulers:
        raise ValueError(
            f"Unknown scheduler '{name}'. Available options: {list(schedulers.keys())}"
        )
    
    return schedulers[name](**kwargs)