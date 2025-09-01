"""
EigenpairFlow: Continuous and stable tracking of eigendecomposition for parameter-dependent matrices.
"""

from .tracking import eigenpairtrack
from .types import EigenTrackingResults
from importlib import metadata

__all__ = [
    "eigenpairtrack",
    "EigenTrackingResults",
]

try:
    __version__ = metadata.version(__name__)
except metadata.PackageNotFoundError:
    # package is not installed
    __version__ = "0.0.0-unknown"
