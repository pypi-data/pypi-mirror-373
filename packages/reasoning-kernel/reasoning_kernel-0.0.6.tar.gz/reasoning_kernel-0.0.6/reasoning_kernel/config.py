"""Minimal configuration utilities for the Reasoning Kernel.

This module provides a lightweight `get_config` accessor used by the CLI and
other entrypoints. It's intentionally small to avoid import-time failures when
optional integrations are not installed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class RuntimeConfig:
    """Runtime configuration with sensible defaults.

    This is a simplified placeholder to keep the CLI operational without
    requiring full environment setup.
    """

    environment: str = "development"
    log_level: str = "INFO"
    enable_tracing: bool = False
    extras: Dict[str, Any] = field(default_factory=dict)


# Alias for tests that expect UnifiedConfig
UnifiedConfig = RuntimeConfig


_CONFIG: Optional[RuntimeConfig] = None


def get_config() -> RuntimeConfig:
    """Return a global runtime config instance.

    In full builds this would read from environment variables or config files.
    For now we return a default config to unblock CLI usage.
    """

    global _CONFIG
    if _CONFIG is None:
        _CONFIG = RuntimeConfig()
    return _CONFIG
