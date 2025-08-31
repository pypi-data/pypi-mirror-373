"""
pbar-io: Share progress bars online
"""

from .client import ProgressBar, SharedProgressBar, configure, get_config
from .integrations import register, track_tqdm, track_rich, track

# Import tqdm drop-in replacement
from .tqdm import tqdm, trange

__version__ = "0.1.0"
__all__ = [
    "ProgressBar",
    "SharedProgressBar",
    "configure",
    "get_config",
    "register",
    "track_tqdm",
    "track_rich",
    "track",
    "tqdm",
    "trange",
]