"""
Lightweight KernelManager stub used by the CLI and tests.

This implementation keeps dependencies minimal and avoids importing the
heavy Semantic Kernel stack at import time. It provides a small async
API surface compatible with how the rest of the codebase references
KernelManager (initialize/get_kernel/close).

If you enable the Semantic Kernel path later, this module can be
extended to construct a real kernel via reasoning_kernel.sk_core.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class KernelManagerConfig:
    """Configuration for KernelManager.

    Attributes are intentionally minimal; extend as needed.
    """

    enable_semantic_kernel: bool = False
    profile: Optional[str] = None


class _MinimalKernel:
    """Very small facade exposing an async invoke_function method.

    This mimics the interface used by higher layers during tests and
    prevents runtime errors when Semantic Kernel is not wired yet.
    """

    async def invoke_function(self, plugin: str, function: str, **kwargs) -> dict:
        return {
            "result": f"Invoked {plugin}.{function}",
            "input": kwargs.get("input") or kwargs.get("text") or "",
            "confidence": 0.5,
        }


class KernelManager:
    """Minimal async KernelManager.

    Methods:
    - initialize(): prepare resources
    - get_kernel(): return a kernel facade providing invoke_function()
    - close(): cleanup
    """

    def __init__(self, config: Optional[KernelManagerConfig] = None):
        self.config = config or KernelManagerConfig()
        self._initialized = False
        self._kernel: Optional[_MinimalKernel] = None

    async def initialize(self) -> bool:
        """Initialize manager resources."""
        try:
            # For now, always create a minimal kernel facade.
            self._kernel = _MinimalKernel()
            self._initialized = True
            logger.debug("KernelManager initialized")
            return True
        except Exception as e:  # pragma: no cover - defensive
            logger.error(f"KernelManager initialization failed: {e}")
            self._initialized = False
            return False

    def get_kernel(self) -> _MinimalKernel:
        """Return an initialized kernel facade.

        Lazily creates a minimal kernel if initialize() was not called
        to make the CLI resilient in fallback scenarios.
        """
        if not self._kernel:
            self._kernel = _MinimalKernel()
        return self._kernel

    async def close(self) -> None:
        """Cleanup resources (noop for the stub)."""
        self._kernel = None
        self._initialized = False
        logger.debug("KernelManager closed")
