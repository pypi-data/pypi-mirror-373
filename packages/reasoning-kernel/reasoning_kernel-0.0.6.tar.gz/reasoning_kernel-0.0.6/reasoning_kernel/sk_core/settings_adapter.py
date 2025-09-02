"""
Settings Adapter for Semantic Kernel Integration
================================================

Adapts the existing unified settings to work seamlessly with Semantic Kernel configuration.
Maps existing .env variables to SK service configurations.
"""

import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

from ..core.unified_settings import get_settings


@dataclass
class SKServiceConfig:
    """Configuration for SK services"""

    service_id: str
    api_key: str
    endpoint: Optional[str] = None
    model: Optional[str] = None
    api_version: Optional[str] = None
    deployment_name: Optional[str] = None
    reasoning_config: Optional[Dict[str, Any]] = None


class SKSettingsAdapter:
    """Adapter to map unified settings to Semantic Kernel configurations"""

    def __init__(self):
        self.settings = get_settings()

    def get_azure_openai_config(self) -> SKServiceConfig:
        """Get Azure OpenAI configuration for SK"""
        return SKServiceConfig(
            service_id="azure_openai_chat",
            api_key=os.getenv("AZURE_OPENAI_API_KEY", ""),
            endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
            model=os.getenv("AZURE_OPENAI_MODEL", "gpt-4"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4"),
            reasoning_config={
                "effort": os.getenv("AZURE_OPENAI_REASONING_EFFORT", "high"),
                "summary": os.getenv("AZURE_OPENAI_REASONING_SUMMARY", "") or None,
            },
        )

    def get_openai_config(self) -> Optional[SKServiceConfig]:
        """Get OpenAI configuration for SK"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None

        return SKServiceConfig(service_id="openai_chat", api_key=api_key, model="gpt-4")

    def get_google_config(self) -> Optional[SKServiceConfig]:
        """Get Google AI configuration for SK"""
        api_key = os.getenv("GOOGLE_AI_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            return None

        return SKServiceConfig(
            service_id="google_ai_chat", api_key=api_key, model="gemini-pro"
        )

    def get_redis_config(self) -> Dict[str, Any]:
        """Get Redis configuration for SK memory"""
        return {
            "connection_string": os.getenv("REDIS_URL", ""),
            "host": os.getenv("REDIS_HOST", "localhost"),
            "port": int(os.getenv("REDIS_PORT", "6379")),
            "password": os.getenv("REDIS_PASSWORD", ""),
            "db": int(
                os.getenv("REDIS_DB", "0")
                if os.getenv("REDIS_DB", "0").isdigit()
                else 0
            ),
            "ssl": os.getenv("REDIS_SSL", "false").lower() == "true",
            "vector_size": int(os.getenv("REDIS_VECTOR_SIZE", "1536")),
            "collection_name": os.getenv("REDIS_COLLECTION_NAME", "msa_knowledge"),
            "max_connections": int(os.getenv("REDIS_MAX_CONNECTIONS", "50")),
            "socket_timeout": float(os.getenv("REDIS_SOCKET_TIMEOUT", "5")),
        }

    def get_embedding_config(self) -> Dict[str, Any]:
        """Get embedding model configuration"""
        return {
            "model": os.getenv("AZURE_EMBEDDING_MODEL", "text-embedding-3-small"),
            "api_key": os.getenv("AZURE_OPENAI_API_KEY", ""),
            "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT", ""),
            "api_version": os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
        }

    def get_msa_config(self) -> Dict[str, Any]:
        """Get MSA engine configuration"""
        return {
            "max_reasoning_steps": int(os.getenv("MAX_REASONING_STEPS", "10")),
            "max_iterations": int(os.getenv("MAX_ITERATIONS", "5")),
            "confidence_threshold": float(os.getenv("CONFIDENCE_THRESHOLD", "0.7")),
            "uncertainty_threshold": float(os.getenv("UNCERTAINTY_THRESHOLD", "0.8")),
            "probabilistic_samples": int(os.getenv("PROBABILISTIC_SAMPLES", "1000")),
            "reasoning_timeout": int(os.getenv("REASONING_TIMEOUT", "300")),
            "knowledge_extraction_timeout": int(
                os.getenv("KNOWLEDGE_EXTRACTION_TIMEOUT", "120")
            ),
            "probabilistic_synthesis_timeout": int(
                os.getenv("PROBABILISTIC_SYNTHESIS_TIMEOUT", "180")
            ),
        }

    def get_feature_flags(self) -> Dict[str, bool]:
        """Get feature flags configuration"""
        return {
            "enable_memory": os.getenv("ENABLE_MEMORY", "true").lower() == "true",
            "enable_plugins": os.getenv("ENABLE_PLUGINS", "true").lower() == "true",
            "enable_caching": os.getenv("ENABLE_CACHING", "true").lower() == "true",
            "enable_tracing": os.getenv("ENABLE_TRACING", "false").lower() == "true",
            "enable_metrics": os.getenv("ENABLE_METRICS", "false").lower() == "true",
            "structured_logging": os.getenv("STRUCTURED_LOGGING", "true").lower()
            == "true",
        }

    def get_daytona_config(self) -> Optional[Dict[str, Any]]:
        """Get Daytona sandbox configuration"""
        api_key = os.getenv("DAYTONA_API_KEY")
        if not api_key:
            return None

        return {
            "api_key": api_key,
            "api_url": os.getenv("DAYTONA_API_URL", "https://app.daytona.io/api"),
            "target": os.getenv("DAYTONA_TARGET", "us"),
            "workspace_id": os.getenv("DAYTONA_WORKSPACE_ID", ""),
            "cpu_limit": int(os.getenv("DAYTONA_CPU_LIMIT", "2")),
            "memory_limit_mb": int(os.getenv("DAYTONA_MEMORY_LIMIT_MB", "512")),
            "execution_timeout": int(os.getenv("DAYTONA_EXECUTION_TIMEOUT", "30")),
            "python_version": os.getenv("DAYTONA_PYTHON_VERSION", "3.12"),
            "enable_networking": os.getenv("DAYTONA_ENABLE_NETWORKING", "false").lower()
            == "true",
        }
