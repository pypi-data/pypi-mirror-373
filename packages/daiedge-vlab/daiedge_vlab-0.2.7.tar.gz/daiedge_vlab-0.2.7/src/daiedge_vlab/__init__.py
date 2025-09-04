"""
daiedge-vlab - Python client for the dAIEdge benchmarking API.
"""

from .api import dAIEdgeVLabAPI          # public surface
from .config import OnDeviceTrainingConfig

__all__ = ["dAIEdgeVLabAPI", "OnDeviceTrainingConfig"]
__version__ = "0.1.0"
