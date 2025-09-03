"""
Reasoning Kernel - SK-native Architecture
========================================

Simplified SK-native package with clean exports.
"""

from .__version__ import __version__

# Simple direct imports for now - lazy loading was causing issues
try:
    from .settings_minimal import Settings  # Use minimal settings for testing
    from .kernel import ReasoningKernel, create_kernel

    _imports_available = True
except ImportError as e:
    # Fallback for import issues
    Settings = None
    ReasoningKernel = None
    create_kernel = None
    _imports_available = False

__all__ = ["__version__", "Settings", "ReasoningKernel", "create_kernel"]
__title__ = "reasoning-kernel"
__description__ = "SK-native MSA Architecture for Advanced Reasoning"
__author__ = "Qredence Team"
__license__ = "MIT"
