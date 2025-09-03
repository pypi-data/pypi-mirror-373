"""
Unified Settings for Reasoning Kernel
=====================================

Consolidated settings management supporting both minimal and full modes.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from pydantic import Field
from pydantic_settings import BaseSettings as PydanticBaseSettings


@dataclass
class MinimalSettings:
    """Minimal settings for testing and development."""

    # Core settings
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    use_minimal_mode: bool = True

    # Azure OpenAI settings (minimal)
    azure_openai_endpoint: str | None = None
    azure_openai_key: str | None = None
    azure_openai_model: str = "gpt-35-turbo"
    azure_openai_api_version: str = "2024-02-01"

    def __post_init__(self):
        """Load environment variables if not provided."""
        self.azure_openai_endpoint = self.azure_openai_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.azure_openai_key = self.azure_openai_key or os.getenv("AZURE_OPENAI_API_KEY")

    def is_development(self) -> bool:
        """Check if in development mode."""
        return self.environment.lower() in ("development", "dev", "local")

    def validate_required_settings(self) -> list[str]:
        """Validate required settings and return missing ones."""
        missing = []
        if not self.azure_openai_endpoint:
            missing.append("AZURE_OPENAI_ENDPOINT")
        if not self.azure_openai_key:
            missing.append("AZURE_OPENAI_API_KEY")
        return missing


class Settings(PydanticBaseSettings):
    """Full Pydantic settings with comprehensive validation."""

    # Core settings
    environment: str = Field(default="development", description="Application environment")
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    use_minimal_mode: bool = Field(default=False, description="Use minimal settings mode")

    # Azure OpenAI settings
    azure_openai_endpoint: str | None = Field(default=None, description="Azure OpenAI endpoint URL")
    azure_openai_api_key: str | None = Field(default=None, description="Azure OpenAI API key")
    azure_openai_model: str = Field(default="gpt-35-turbo", description="Azure OpenAI model name")
    azure_openai_api_version: str = Field(default="2024-02-01", description="Azure OpenAI API version")

    # Redis settings
    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_db: int = Field(default=0, description="Redis database number")
    redis_password: str | None = Field(default=None, description="Redis password")
    enable_caching: bool = Field(default=True, description="Enable Redis caching")

    # Performance settings
    max_workers: int = Field(default=4, description="Maximum worker threads")
    timeout_seconds: int = Field(default=30, description="Request timeout in seconds")

    # MSA settings
    enable_msa: bool = Field(default=True, description="Enable Multi-Step Analysis")
    msa_max_steps: int = Field(default=10, description="Maximum MSA steps")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def is_development(self) -> bool:
        """Check if in development mode."""
        return self.environment.lower() in ("development", "dev", "local")

    def validate_required_settings(self) -> list[str]:
        """Validate required settings and return missing ones."""
        missing = []
        if not self.azure_openai_endpoint:
            missing.append("AZURE_OPENAI_ENDPOINT")
        if not self.azure_openai_api_key:
            missing.append("AZURE_OPENAI_API_KEY")
        return missing


def create_settings(minimal: bool | None = None) -> MinimalSettings | Settings:
    """
    Factory function to create appropriate settings instance.

    Args:
        minimal: Force minimal mode if True, full mode if False,
                auto-detect if None (checks environment variables)

    Returns:
        Settings instance (MinimalSettings or Settings)
    """
    # Auto-detect if not specified
    if minimal is None:
        # Use minimal mode if no Azure config provided or explicitly requested
        has_azure_config = bool(os.getenv("AZURE_OPENAI_ENDPOINT"))
        use_minimal_env = os.getenv("USE_MINIMAL_MODE", "false").lower() in ("true", "1", "yes")
        minimal = not has_azure_config or use_minimal_env

    if minimal:
        return MinimalSettings()
    else:
        try:
            return Settings()
        except Exception:
            # Fallback to minimal if Pydantic validation fails
            return MinimalSettings()


# Convenience exports
__all__ = [
    "MinimalSettings",
    "Settings",
    "create_settings",
]
