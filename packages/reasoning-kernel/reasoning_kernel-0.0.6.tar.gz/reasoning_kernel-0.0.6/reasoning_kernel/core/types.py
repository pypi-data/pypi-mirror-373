"""
Enhanced Type Definitions for MSA Reasoning Kernel
==================================================

Comprehensive type definitions using Protocols, TypedDicts, and dataclasses
for improved type safety and mypy compliance.
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    Protocol,
    TypedDict,
    TypeVar,
    Union,
    runtime_checkable,
)

from typing_extensions import NotRequired

# Generic type variables
T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


# Status and State Enums
class ServiceStatus(str, Enum):
    """Service status enumeration"""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class ExecutionStatus(str, Enum):
    """Execution status enumeration"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CacheStatus(str, Enum):
    """Cache status enumeration"""

    HIT = "hit"
    MISS = "miss"
    EXPIRED = "expired"
    ERROR = "error"


# Core Protocol Definitions
@runtime_checkable
class Healthable(Protocol):
    """Protocol for objects that can report health status"""

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check and return status"""
        ...


@runtime_checkable
class Cacheable(Protocol):
    """Protocol for cacheable objects"""

    def cache_key(self) -> str:
        """Generate cache key for this object"""
        ...

    def cache_ttl(self) -> int:
        """Get cache TTL in seconds"""
        ...


@runtime_checkable
class Serializable(Protocol):
    """Protocol for serializable objects"""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        ...

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Serializable":
        """Create from dictionary"""
        ...


@runtime_checkable
class AsyncExecutable(Protocol[T]):
    """Protocol for async executable objects"""

    async def execute(self, *args: Any, **kwargs: Any) -> T:
        """Execute the operation"""
        ...


@runtime_checkable
class Configurable(Protocol):
    """Protocol for configurable objects"""

    def configure(self, config: Dict[str, Any]) -> None:
        """Configure the object"""
        ...

    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        ...


# TypedDict Definitions for Structured Data
class HealthCheckResult(TypedDict):
    """Health check result structure"""

    status: ServiceStatus
    message: str
    timestamp: float
    details: NotRequired[Dict[str, Any]]
    metrics: NotRequired[Dict[str, Union[int, float, str]]]


class ExecutionResult(TypedDict):
    """Execution result structure"""

    status: ExecutionStatus
    result: NotRequired[Any]
    error: NotRequired[str]
    duration_ms: float
    timestamp: float
    metadata: NotRequired[Dict[str, Any]]


class CacheEntry(TypedDict):
    """Cache entry structure"""

    key: str
    value: Any
    created_at: float
    expires_at: float
    access_count: int
    last_accessed: float
    size_bytes: NotRequired[int]


class MetricsData(TypedDict):
    """Metrics data structure"""

    total_requests: int
    successful_requests: int
    failed_requests: int
    average_latency_ms: float
    last_request_time: float
    error_rate: float


class ConfigurationData(TypedDict):
    """Configuration data structure"""

    service_name: str
    version: str
    environment: str
    settings: Dict[str, Any]
    last_updated: float


class PipelineStageResult(TypedDict):
    """Pipeline stage result structure"""

    stage_name: str
    status: ExecutionStatus
    input_data: Dict[str, Any]
    output_data: NotRequired[Dict[str, Any]]
    error: NotRequired[str]
    duration_ms: float
    confidence: NotRequired[float]
    metadata: NotRequired[Dict[str, Any]]


class PluginMetadata(TypedDict):
    """Plugin metadata structure"""

    name: str
    version: str
    description: str
    author: NotRequired[str]
    dependencies: List[str]
    capabilities: List[str]
    configuration_schema: NotRequired[Dict[str, Any]]


class ServiceConfiguration(TypedDict):
    """Service configuration structure"""

    endpoint: str
    api_key: NotRequired[str]
    timeout_seconds: float
    max_retries: int
    enable_caching: bool
    cache_ttl_seconds: int
    health_check_interval: float


# Dataclass Definitions for Complex Objects
@dataclass
class AsyncOperationContext:
    """Context for async operations"""

    operation_id: str
    timeout_seconds: float = 30.0
    max_retries: int = 3
    retry_delay_seconds: float = 1.0
    enable_circuit_breaker: bool = True
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class CacheConfiguration:
    """Cache configuration"""

    max_size: int = 1000
    default_ttl_seconds: int = 3600
    enable_compression: bool = True
    enable_metrics: bool = True
    eviction_policy: Literal["lru", "lfu", "ttl"] = "lru"
    cleanup_interval_seconds: float = 300.0


@dataclass
class RetryConfiguration:
    """Retry configuration"""

    max_attempts: int = 3
    base_delay_seconds: float = 1.0
    max_delay_seconds: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    retry_on_exceptions: tuple = (Exception,)


@dataclass
class CircuitBreakerConfiguration:
    """Circuit breaker configuration"""

    failure_threshold: int = 5
    recovery_timeout_seconds: float = 60.0
    half_open_max_calls: int = 3
    expected_exception: type = Exception


@dataclass
class PerformanceMetrics:
    """Performance metrics"""

    operation_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    total_duration_ms: float = 0.0
    min_duration_ms: float = float("inf")
    max_duration_ms: float = 0.0
    last_operation_time: float = 0.0

    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.operation_count == 0:
            return 0.0
        return self.success_count / self.operation_count

    @property
    def average_duration_ms(self) -> float:
        """Calculate average duration"""
        if self.operation_count == 0:
            return 0.0
        return self.total_duration_ms / self.operation_count

    def record_operation(self, success: bool, duration_ms: float) -> None:
        """Record an operation"""
        self.operation_count += 1
        self.total_duration_ms += duration_ms
        self.last_operation_time = time.time()

        if success:
            self.success_count += 1
        else:
            self.failure_count += 1

        self.min_duration_ms = min(self.min_duration_ms, duration_ms)
        self.max_duration_ms = max(self.max_duration_ms, duration_ms)


@dataclass
class ResourceUsage:
    """Resource usage metrics"""

    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    disk_mb: float = 0.0
    network_kb_in: float = 0.0
    network_kb_out: float = 0.0
    open_connections: int = 0
    timestamp: float = field(default_factory=time.time)


# Function Type Aliases
AsyncCallable = Callable[..., Awaitable[Any]]
SyncCallable = Callable[..., Any]
ErrorHandler = Callable[[Exception], Any]
HealthChecker = Callable[[], Awaitable[HealthCheckResult]]
MetricsCollector = Callable[[], MetricsData]
ConfigValidator = Callable[[Dict[str, Any]], bool]


# Complex Type Aliases
JSONValue = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]
JSONDict = Dict[str, JSONValue]
JSONList = List[JSONValue]

CacheKey = str
CacheValue = Any
ConfigKey = str
ConfigValue = Union[str, int, float, bool, List[Any], Dict[str, Any]]

ServiceName = str
PluginName = str
StageName = str
OperationName = str

# Result Types
OperationResult = Union[ExecutionResult, Exception]
CacheResult = Union[CacheEntry, None]
HealthResult = HealthCheckResult
ValidationResult = Union[bool, List[str]]  # True or list of error messages


# Generic Protocol for Async Context Managers
@runtime_checkable
class AsyncContextManager(Protocol[T]):
    """Protocol for async context managers"""

    async def __aenter__(self) -> T:
        """Enter async context"""
        ...

    async def __aexit__(
        self, exc_type: Any, exc_val: Any, exc_tb: Any
    ) -> Optional[bool]:
        """Exit async context"""
        ...


# Factory Protocol
@runtime_checkable
class Factory(Protocol[T]):
    """Protocol for factory objects"""

    def create(self, *args: Any, **kwargs: Any) -> T:
        """Create an instance"""
        ...


@runtime_checkable
class AsyncFactory(Protocol[T]):
    """Protocol for async factory objects"""

    async def create(self, *args: Any, **kwargs: Any) -> T:
        """Create an instance asynchronously"""
        ...


# Observer Pattern
@runtime_checkable
class Observer(Protocol):
    """Protocol for observer pattern"""

    async def notify(self, event: str, data: Dict[str, Any]) -> None:
        """Handle notification"""
        ...


@runtime_checkable
class Observable(Protocol):
    """Protocol for observable objects"""

    def add_observer(self, observer: Observer) -> None:
        """Add an observer"""
        ...

    def remove_observer(self, observer: Observer) -> None:
        """Remove an observer"""
        ...

    async def notify_observers(self, event: str, data: Dict[str, Any]) -> None:
        """Notify all observers"""
        ...


# Validation Types
ValidationError = str
ValidationErrors = List[ValidationError]
ValidationRule = Callable[[Any], Union[bool, ValidationError]]
ValidationRules = List[ValidationRule]


# Event Types
EventType = str
EventData = Dict[str, Any]
EventHandler = Callable[[EventType, EventData], Awaitable[None]]
EventHandlers = Dict[EventType, List[EventHandler]]


# Pipeline Types
PipelineStage = Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]
PipelineStages = List[PipelineStage]
PipelineContext = Dict[str, Any]
PipelineResult = Dict[str, Any]


# Plugin Types
PluginFunction = Callable[..., Awaitable[Any]]
PluginFunctions = Dict[str, PluginFunction]
PluginConfig = Dict[str, Any]
PluginRegistry = Dict[str, Any]


# Service Types
ServiceConfig = Dict[str, Any]
ServiceMetrics = Dict[str, Union[int, float, str]]
ServiceHealth = HealthCheckResult
ServiceInstance = Any  # Placeholder for actual service instances
