"""
Unified Configuration for Reasoning Kernel
==========================================

Single source for kernel configuration and initialization.
Integrates with both legacy runtime config and new SK-native patterns.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

from .kernel import ReasoningKernel
from .settings import MinimalSettings, Settings, create_settings

logger = logging.getLogger(__name__)


@dataclass
class RuntimeConfig:
    """Runtime configuration with sensible defaults for backward compatibility."""

    environment: str = "development"
    log_level: str = "INFO"
    enable_tracing: bool = False
    extras: dict[str, Any] = field(default_factory=dict)


# Alias for tests that expect UnifiedConfig
UnifiedConfig = RuntimeConfig

_CONFIG: RuntimeConfig | None = None


def get_config() -> RuntimeConfig:
    """Return a global runtime config instance for backward compatibility."""
    global _CONFIG
    if _CONFIG is None:
        _CONFIG = RuntimeConfig()
    return _CONFIG


async def configure_kernel(settings: MinimalSettings | Settings | None = None) -> ReasoningKernel:
    """
    Configure and return a fully initialized Semantic Kernel.

    Args:
        settings: Configuration settings (auto-detected if None)

    Returns:
        Configured ReasoningKernel instance

    Raises:
        RuntimeError: If required configuration is missing
    """
    if settings is None:
        settings = create_settings()

    logger.info(f"Configuring kernel with {type(settings).__name__}")

    # Validate required settings
    missing = settings.validate_required_settings()
    if missing:
        logger.warning(f"Missing optional settings: {missing}")

    # Create reasoning kernel (which includes base kernel setup)
    reasoning_kernel = ReasoningKernel(settings)

    # Enhance with AI service if configured
    if hasattr(settings, "azure_openai_api_key") and settings.azure_openai_api_key:
        try:
            azure_config = settings.get_azure_openai_config()

            ai_service = AzureChatCompletion(
                service_id="azure_openai",
                deployment_name=azure_config["deployment"],
                endpoint=azure_config["endpoint"],
                api_key=azure_config["api_key"],
                api_version=azure_config.get("api_version", "2024-02-15-preview"),
            )

            reasoning_kernel.kernel.add_service(ai_service)
            logger.info("Enhanced kernel with Azure OpenAI chat completion service")

        except Exception as e:
            logger.error(f"Failed to configure Azure OpenAI: {e}")
            if not settings.is_development():
                raise RuntimeError(f"Azure OpenAI configuration failed: {e}")

    logger.info("Kernel configuration completed successfully")
    return reasoning_kernel


def configure_minimal_kernel() -> ReasoningKernel:
    """Configure a minimal kernel for testing without external dependencies."""
    settings = MinimalSettings()
    kernel = ReasoningKernel(settings)
    logger.info("Minimal kernel configured for testing")
    return kernel


def validate_kernel_configuration(settings: MinimalSettings | Settings) -> list[str]:
    """
    Validate kernel configuration and return list of issues.

    Args:
        settings: Settings to validate

    Returns:
        List of validation error messages (empty if valid)
    """
    issues = []

    # Check AI service configuration
    if not hasattr(settings, "azure_openai_api_key") or not settings.azure_openai_api_key:
        issues.append("Azure OpenAI API key not configured")

    if not hasattr(settings, "azure_openai_endpoint") or not settings.azure_openai_endpoint:
        issues.append("Azure OpenAI endpoint not configured")

    # Check environment settings
    if settings.environment not in ("development", "testing", "production"):
        issues.append(f"Invalid environment: {settings.environment}")

    if settings.log_level not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
        issues.append(f"Invalid log level: {settings.log_level}")

    return issues
