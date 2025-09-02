"""
Reasoning Kernel - Unified MSA Architecture
==========================================

Lightweight package initializer. Heavy components are imported from their
respective modules to avoid side effects during import.
"""

from .__version__ import __version__  # re-export version

# Re-export constants for compatibility
from .core import constants

__all__ = [
    "__version__",
    "constants",
]

# Package metadata (kept minimal to avoid heavy imports)
__title__ = "reasoning-kernel"
__description__ = "Unified MSA Architecture for Advanced Reasoning"
__author__ = "Qredence Team"
__license__ = "MIT"
