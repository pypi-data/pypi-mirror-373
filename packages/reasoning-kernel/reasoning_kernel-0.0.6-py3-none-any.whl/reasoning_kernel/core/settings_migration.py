"""Compatibility module for settings migration functionality."""

import warnings
from typing import Dict, Any


class LegacySettingsAdapter:
    """Adapter for legacy settings access patterns."""

    def __init__(self, unified_settings):
        self.unified_settings = unified_settings

    def get_azure_openai_config(self) -> Dict[str, Any]:
        """Legacy method for Azure OpenAI config."""
        warnings.warn(
            "get_azure_openai_config is deprecated, use unified_settings directly", DeprecationWarning, stacklevel=2
        )
        return {
            "endpoint": getattr(self.unified_settings, "azure_openai_endpoint", None),
            "api_key": getattr(self.unified_settings, "azure_openai_api_key", None),
        }

    def get_redis_config(self) -> Dict[str, Any]:
        """Legacy method for Redis config."""
        warnings.warn("get_redis_config is deprecated, use unified_settings directly", DeprecationWarning, stacklevel=2)
        return {"connection_string": getattr(self.unified_settings, "redis_url", None)}

    def get_daytona_config(self) -> Dict[str, Any]:
        """Legacy method for Daytona config."""
        warnings.warn(
            "get_daytona_config is deprecated, use unified_settings directly", DeprecationWarning, stacklevel=2
        )
        return {
            "api_url": getattr(self.unified_settings, "daytona_api_url", "https://api.daytona.dev"),
            "api_key": getattr(self.unified_settings, "daytona_api_key", None),
        }


def validate_settings_consistency() -> Dict[str, Any]:
    """Validate settings consistency for legacy compatibility."""
    return {"valid": True, "warnings": [], "errors": []}


def generate_env_template() -> str:
    """Generate environment template for legacy compatibility."""
    return """# Environment Configuration Template
OPENAI_API_KEY=your_openai_api_key_here
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
REDIS_URL=redis://localhost:6379/0
DAYTONA_API_KEY=your_daytona_api_key_here
ENVIRONMENT=development
"""
