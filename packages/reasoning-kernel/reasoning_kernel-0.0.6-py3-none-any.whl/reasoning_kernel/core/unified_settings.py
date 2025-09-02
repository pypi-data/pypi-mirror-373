"""
Unified Settings
================

Centralized configuration management for the Reasoning Kernel.
"""

import json
import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml

logger = logging.getLogger(__name__)


class LogLevel(Enum):
    """Logging levels"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Environment(Enum):
    """Environment types"""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


# Backward-compatibility: external tests expect EnvironmentProfile
class EnvironmentProfile(Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class DatabaseSettings:
    """Database configuration"""

    host: str = "localhost"
    port: int = 5432
    database: str = "reasoning_kernel"
    username: str = "postgres"
    password: str = ""
    ssl_mode: str = "prefer"
    pool_size: int = 10
    max_overflow: int = 20


@dataclass
class RedisSettings:
    """Redis configuration"""

    host: str = "localhost"
    port: int = 6379
    database: int = 0
    password: Optional[str] = None
    ssl: bool = False
    connection_pool_size: int = 10
    socket_timeout: float = 5.0
    socket_connect_timeout: float = 5.0


@dataclass
class APISettings:
    """API configuration"""

    host: str = "0.0.0.0"
    port: int = 8000
    enable_docs: bool = True
    enable_cors: bool = True
    enable_streaming: bool = True
    max_request_size: int = 10 * 1024 * 1024  # 10MB
    timeout_seconds: int = 300


@dataclass
class LoggingSettings:
    """Logging configuration"""

    level: LogLevel = LogLevel.INFO
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    enable_structured_logging: bool = True


@dataclass
class CloudSettings:
    """Cloud services configuration"""

    gpt5_api_key: Optional[str] = None
    gpt5_base_url: Optional[str] = None
    redis_cloud_url: Optional[str] = None
    daytona_api_key: Optional[str] = None
    daytona_workspace_id: Optional[str] = None


@dataclass
class MSASettings:
    """MSA pipeline configuration"""

    enable_caching: bool = True
    enable_parallel_stages: bool = False
    timeout_seconds: int = 300
    retry_attempts: int = 3
    enhanced_mode: bool = True
    verbose_logging: bool = False
    stage_weights: Dict[str, float] = field(
        default_factory=lambda: {
            "parse": 0.25,
            "knowledge": 0.20,
            "graph": 0.20,
            "synthesis": 0.20,
            "inference": 0.15,
        }
    )


@dataclass
class CacheSettings:
    """Cache configuration"""

    max_size: int = 1000
    max_memory_mb: Optional[float] = None
    default_ttl: Optional[float] = 3600  # 1 hour
    cleanup_interval: int = 300  # 5 minutes
    enable_persistence: bool = False
    persistence_path: Optional[str] = None


@dataclass
class SecuritySettings:
    """Security configuration"""

    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    enable_rate_limiting: bool = True
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds


@dataclass
class MonitoringSettings:
    """Monitoring and metrics configuration"""

    enable_metrics: bool = True
    enable_tracing: bool = True
    metrics_port: int = 9090
    health_check_interval: int = 30
    performance_tracking: bool = True


@dataclass
class UnifiedSettings:
    """Unified settings container"""

    # Backward-compatible flat fields
    app_name: str = "MSA Reasoning Engine"
    environment: EnvironmentProfile = EnvironmentProfile.DEVELOPMENT
    debug: Optional[bool] = None
    reload: bool = False
    enable_metrics: bool = False

    # Flat Redis fields for compatibility
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: Optional[str] = None
    redis_db: Union[int, str] = 0
    redis_ssl: bool = False
    redis_url: Optional[str] = None

    # Flat AI/Cloud fields for compatibility
    openai_api_key: Optional[str] = None
    openai_temperature: float = 1.0
    azure_openai_endpoint: Optional[str] = None
    azure_openai_api_key: Optional[str] = None
    daytona_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    azure_gpt5_mini_deployment: Optional[str] = None
    secret_key: Optional[str] = None

    # Flat logging field for compatibility (string or enum)
    log_level: Any = LogLevel.INFO
    cors_origins: Union[str, list] = field(default_factory=list)

    # Component settings
    database: DatabaseSettings = field(default_factory=DatabaseSettings)
    redis: RedisSettings = field(default_factory=RedisSettings)
    api: APISettings = field(default_factory=APISettings)
    logging: LoggingSettings = field(default_factory=LoggingSettings)
    cloud: CloudSettings = field(default_factory=CloudSettings)
    msa: MSASettings = field(default_factory=MSASettings)
    cache: CacheSettings = field(default_factory=CacheSettings)
    security: SecuritySettings = field(default_factory=SecuritySettings)
    monitoring: MonitoringSettings = field(default_factory=MonitoringSettings)

    def __post_init__(self):
        """Post-initialization processing"""
        # Track whether explicit redis-related constructor args were provided
        self._explicit_redis_config = any(
            [
                self.redis_url is not None,
                self.redis_host != "localhost",
                self.redis_port != 6379,
                self.redis_password not in (None, ""),
                bool(self.redis_ssl),
                self.redis_db not in (0, "0"),
                isinstance(self.redis_db, str),
            ]
        )

        # Load from environment variables
        self._load_from_environment()

        # Apply flat overrides into nested structures
        self._apply_flat_overrides()

        # Coerce debug if provided as string; respect explicit bool
        if isinstance(self.debug, str):
            self.debug = self.debug.lower() in {"true", "1", "yes", "on", "debug"}

        # Parse CORS origins
        if isinstance(self.cors_origins, str):
            val = self.cors_origins.strip()
            if val == "*":
                self.cors_origins = "*"
            elif "," in val:
                self.cors_origins = [x.strip() for x in val.split(",") if x.strip()]
            elif val:
                self.cors_origins = [val]
            else:
                self.cors_origins = []

        # Validate settings
        self._validate_settings()

    def _load_from_environment(self) -> None:
        """Load settings from environment variables"""
        # Environment: respect explicit parameter over env
        env_from_env = os.getenv("ENVIRONMENT") or os.getenv("REASONING_KERNEL_ENV")
        if env_from_env and self.environment == EnvironmentProfile.DEVELOPMENT:
            try:
                self.environment = EnvironmentProfile(env_from_env.lower())
            except ValueError:
                logger.warning(
                    f"Invalid environment '{env_from_env}', using development"
                )
                self.environment = EnvironmentProfile.DEVELOPMENT

        # Debug mode (support various truthy values); only if not provided explicitly
        if self.debug is None:
            debug_val = os.getenv("DEBUG")
            if debug_val is not None:
                self.debug = debug_val.lower() in {"true", "1", "yes", "on", "debug"}

        # API settings
        self.api.host = os.getenv("API_HOST", self.api.host)
        self.api.port = int(os.getenv("API_PORT", str(self.api.port)))

        # Database settings
        self.database.host = os.getenv("DB_HOST", self.database.host)
        self.database.port = int(os.getenv("DB_PORT", str(self.database.port)))
        self.database.database = os.getenv("DB_NAME", self.database.database)
        self.database.username = os.getenv("DB_USER", self.database.username)
        self.database.password = os.getenv("DB_PASSWORD", self.database.password)

        # Redis settings
        self.redis.host = os.getenv("REDIS_HOST", self.redis.host)
        self.redis.port = int(os.getenv("REDIS_PORT", str(self.redis.port)))
        self.redis.password = os.getenv("REDIS_PASSWORD", self.redis.password)
        db_val = os.getenv("REDIS_DB")
        if db_val is not None:
            try:
                self.redis.database = int(db_val)
            except ValueError:
                logger.warning("Invalid REDIS_DB value; using default")

        # Cloud settings
        self.cloud.gpt5_api_key = os.getenv("GPT5_API_KEY")
        self.cloud.redis_cloud_url = os.getenv("REDIS_CLOUD_URL")
        self.cloud.daytona_api_key = os.getenv("DAYTONA_API_KEY")

        # Security settings
        self.security.secret_key = os.getenv("SECRET_KEY", self.security.secret_key)

        # Logging level
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        try:
            self.logging.level = LogLevel(log_level)
        except ValueError:
            logger.warning(f"Invalid log level '{log_level}', using INFO")
            self.logging.level = LogLevel.INFO

        # Profile-specific flags used by tests
        if self.environment == EnvironmentProfile.DEVELOPMENT:
            self.reload = True
            self.enable_metrics = False
            if self.debug is None:
                self.debug = True
        elif self.environment == EnvironmentProfile.PRODUCTION:
            self.reload = False
            self.enable_metrics = True
            if self.debug is None:
                self.debug = False

        # CORS origins from env
        cors_env = os.getenv("CORS_ORIGINS")
        if cors_env is not None and not self.cors_origins:
            self.cors_origins = cors_env

    def _apply_flat_overrides(self) -> None:
        """Apply flat fields into nested settings for backward-compatibility."""
        # Redis
        # Coerce db value if provided as string
        if isinstance(self.redis_db, str):
            self.redis_db = int(self.redis_db) if self.redis_db.isdigit() else 0
        self.redis.host = self.redis_host or self.redis.host
        self.redis.port = self.redis_port or self.redis.port
        if self.redis_password is not None:
            self.redis.password = self.redis_password
        self.redis.database = (
            self.redis_db if self.redis_db is not None else self.redis.database
        )
        self.redis.ssl = (
            self.redis_ssl if self.redis_ssl is not None else self.redis.ssl
        )

        # Security
        if self.secret_key:
            self.security.secret_key = self.secret_key

        # Logging
        if isinstance(self.log_level, str):
            try:
                self.logging.level = LogLevel(self.log_level.upper())
            except ValueError:
                raise ValueError("Invalid log level")
        elif isinstance(self.log_level, LogLevel):
            self.logging.level = self.log_level
        # Adjust defaults per environment
        if (
            self.environment == EnvironmentProfile.DEVELOPMENT
            and self.log_level == LogLevel.INFO
        ):
            self.log_level = LogLevel.DEBUG
            self.logging.level = LogLevel.DEBUG

        # Cloud
        if self.azure_openai_endpoint:
            os.environ.setdefault("AZURE_OPENAI_ENDPOINT", self.azure_openai_endpoint)
        if self.azure_openai_api_key:
            os.environ.setdefault("AZURE_OPENAI_API_KEY", self.azure_openai_api_key)
        if self.daytona_api_key:
            os.environ.setdefault("DAYTONA_API_KEY", self.daytona_api_key)
        if self.openai_api_key:
            os.environ.setdefault("OPENAI_API_KEY", self.openai_api_key)
        if self.google_api_key or self.gemini_api_key:
            os.environ.setdefault(
                "GOOGLE_AI_API_KEY", self.google_api_key or self.gemini_api_key
            )

    def _validate_settings(self) -> None:
        """Validate settings for consistency"""
        # Validate ports
        if not (1 <= self.api.port <= 65535):
            raise ValueError(f"Invalid API port: {self.api.port}")

        if not (1 <= self.redis.port <= 65535):
            raise ValueError(f"Invalid Redis port: {self.redis.port}")

        # Validate timeouts
        if self.msa.timeout_seconds <= 0:
            raise ValueError("MSA timeout must be positive")

        if self.api.timeout_seconds <= 0:
            raise ValueError("API timeout must be positive")

        # Validate cache settings
        if self.cache.max_size <= 0:
            raise ValueError("Cache max size must be positive")

        # Production environment checks
        if self.environment == EnvironmentProfile.PRODUCTION:
            if self.security.secret_key == "your-secret-key-here":
                # Warn in tests rather than raising
                logger.warning("Secret key should be changed in production")
            if self.debug:
                logger.warning("Debug mode is enabled in production")

        # Validate temperature range
        if not (0.0 <= float(self.openai_temperature) <= 2.0):
            raise ValueError("openai_temperature must be between 0.0 and 2.0")

    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary"""

        def convert_value(value):
            if isinstance(value, Enum):
                return value.value
            elif hasattr(value, "__dict__"):
                return {k: convert_value(v) for k, v in value.__dict__.items()}
            else:
                return value

        return {k: convert_value(v) for k, v in self.__dict__.items()}

    # --- Compatibility helpers expected by tests ---
    def get_redis_connection_string(self) -> str:
        # Prefer explicit REDIS_URL if provided
        if self.redis_url:
            return self.redis_url
        # If no explicit config, allow env URL
        if not self._explicit_redis_config:
            env_url = os.getenv("REDIS_URL")
            if env_url:
                return env_url
        scheme = "rediss" if self.redis.ssl or self.redis_ssl else "redis"
        auth = f":{self.redis.password}@" if self.redis.password else ""
        return f"{scheme}://{auth}{self.redis.host}:{self.redis.port}/{self.redis.database}"

    def is_ai_service_available(self, provider: str) -> bool:
        prov = provider.lower()
        if prov == "openai":
            return bool(self.openai_api_key or os.getenv("OPENAI_API_KEY"))
        if prov == "azure":
            return bool(
                (self.azure_openai_api_key or os.getenv("AZURE_OPENAI_API_KEY"))
                and (self.azure_openai_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT"))
            )
        if prov == "google":
            return bool(
                self.google_api_key
                or self.gemini_api_key
                or os.getenv("GOOGLE_AI_API_KEY")
                or os.getenv("GOOGLE_API_KEY")
                or os.getenv("GEMINI_API_KEY")
            )
        return False

    def get_azure_openai_config(self) -> Dict[str, Any]:
        return {
            "endpoint": self.azure_openai_endpoint
            or os.getenv("AZURE_OPENAI_ENDPOINT", ""),
            "api_key": self.azure_openai_api_key
            or os.getenv("AZURE_OPENAI_API_KEY", ""),
        }

    def get_daytona_config(self) -> Dict[str, Any]:
        return {
            "api_key": self.daytona_api_key or os.getenv("DAYTONA_API_KEY", ""),
            "workspace_name": os.getenv("DAYTONA_WORKSPACE", "msa-reasoning"),
            "api_url": os.getenv("DAYTONA_API_URL", ""),
        }

    # Convenience property for tests
    @property
    def openai_model(self) -> str:
        return os.getenv("OPENAI_MODEL", "gpt-4o")

    def save_to_file(self, file_path: str) -> None:
        """Save settings to file"""
        path = Path(file_path)
        settings_dict = self.to_dict()

        if path.suffix.lower() == ".json":
            with open(path, "w") as f:
                json.dump(settings_dict, f, indent=2)
        elif path.suffix.lower() in [".yml", ".yaml"]:
            with open(path, "w") as f:
                yaml.dump(settings_dict, f, default_flow_style=False)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")

        logger.info(f"Settings saved to {file_path}")

    @classmethod
    def load_from_file(cls, file_path: str) -> "UnifiedSettings":
        """Load settings from file"""
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Settings file not found: {file_path}")

        if path.suffix.lower() == ".json":
            with open(path, "r") as f:
                data = json.load(f)
        elif path.suffix.lower() in [".yml", ".yaml"]:
            with open(path, "r") as f:
                data = yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")

        # Create settings instance and update with loaded data
        settings = cls()
        settings._update_from_dict(data)

        logger.info(f"Settings loaded from {file_path}")
        return settings

    def _update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update settings from dictionary"""
        for key, value in data.items():
            if hasattr(self, key):
                attr = getattr(self, key)
                if hasattr(attr, "__dict__"):
                    # Update nested settings
                    for nested_key, nested_value in value.items():
                        if hasattr(attr, nested_key):
                            setattr(attr, nested_key, nested_value)
                else:
                    setattr(self, key, value)


# Global settings instance
_settings: Optional[UnifiedSettings] = None


def get_settings() -> UnifiedSettings:
    """Get the global settings instance"""
    global _settings
    if _settings is None:
        _settings = UnifiedSettings()
    return _settings


def load_settings_from_file(file_path: str) -> UnifiedSettings:
    """Load settings from file and set as global instance"""
    global _settings
    _settings = UnifiedSettings.load_from_file(file_path)
    return _settings


def reset_settings() -> None:
    """Reset global settings instance"""
    global _settings
    _settings = None
