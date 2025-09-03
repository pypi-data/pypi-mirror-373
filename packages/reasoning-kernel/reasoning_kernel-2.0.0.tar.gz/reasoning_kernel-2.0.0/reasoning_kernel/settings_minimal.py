"""
Minimal Settings for Testing
=============================

Simplified settings for testing SK-native architecture.
"""


class Settings:
    """Minimal settings for testing."""

    def __init__(self):
        """Initialize with simple defaults."""
        self.environment = "development"
        self.debug = False
        self.redis_url = "redis://localhost:6379"
        self.azure_openai_api_key = None
        self.azure_openai_endpoint = None
