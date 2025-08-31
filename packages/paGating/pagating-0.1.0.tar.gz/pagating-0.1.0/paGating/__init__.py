"""paGating: Fast Gating Function for Transformer Architectures.

The paGating module contains all activation gate units as defined in
the paper. This package enables easy import of the units and export
to CoreML for mobile applications.
"""

from paGating.activation_fns import gelu, mish, swish
from paGating.paGELU import paGELU
from paGating.paGLU import paGLU
from paGating.paGTU import paGTU
from paGating.paMishU import paMishU
from paGating.paReGLU import paReGLU
from paGating.paSwishU import paSwishU
from paGating.paUnit import paUnit
# from .paSiLUU import paSiLUU # Commented out - File not found
from .paSiLU import paSiLU
from .paGRU import PaGRUCell
from .alpha_schedulers import (
    CosineAlphaScheduler,
    LinearRampScheduler,
    EntropyBasedAlpha,
    ConfidenceBasedAlpha
)
from .norms import (
    GateNorm,
    PrePostNormWrapper
)
from .cnn_adapters import (
    paGating2D,
    create_paGating2D
)

__version__ = "0.1.0"

# Create activation map for easy unit access by name
activation_map = {
    'paGLU': paGLU,
    'paGTU': paGTU,
    'paSwishU': paSwishU,
    'paReGLU': paReGLU,
    'paGELU': paGELU,
    'paMishU': paMishU,
    'paSiLU': paSiLU,
}

__all__ = [
    'paGLU',
    'paGTU',
    'paSwishU',
    'paReGLU',
    'paGELU',
    'paMishU',
    'paSiLU',
    # 'paSiLUU', # Also comment out from __all__ if it was there
    'CosineAlphaScheduler',
    'LinearRampScheduler',
    'EntropyBasedAlpha',
    'ConfidenceBasedAlpha',
    'GateNorm',
    'PrePostNormWrapper',
    'activation_map',
    'paGating2D',
    'create_paGating2D',
    'PaGRUCell',
]
