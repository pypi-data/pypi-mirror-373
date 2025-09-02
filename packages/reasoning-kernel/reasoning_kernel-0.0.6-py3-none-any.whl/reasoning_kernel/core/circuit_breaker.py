"""
Circuit Breaker Pattern Implementation for MSA Reasoning Kernel

Provides fault tolerance for external service calls with:
- Circuit breaker state management (Closed/Open/Half-Open)
- Exponential backoff retry logic
- Health check endpoints
- Graceful degradation strategies
- Se            except self.config.retriable_exceptions as e:
                last_exception = e
                self._record_failure(e)

                if attempt < self.config.max_retries:
                    delay = self._calculate_delay(attempt)
                    logger.warning(
                        f"Attempt {attempt + 1} failed for {self.config.service_type.value}, "
                        f"retrying in {delay:.2f}s: {e}"
                    )
                    time.sleep(delay)
                else:
                    simple_log_error("execute_with_retry_sync", e, service_type=self.config.service_type.value)c failure thresholds
"""

import asyncio
import logging
import random
import time
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from typing import Any, Awaitable, Callable, Dict, Optional, TypeVar

from reasoning_kernel.core.logging_utils import simple_log_error

# from datetime import datetime

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CircuitBreakerState(Enum):
    """Circuit breaker states"""

    CLOSED = "CLOSED"  # Normal operation
    OPEN = "OPEN"  # Failing fast, not allowing requests
    HALF_OPEN = "HALF_OPEN"  # Testing if service has recovered


class ServiceType(Enum):
    """Types of external services"""

    DAYTONA = "DAYTONA"
    REDIS = "REDIS"
    WEB_SEARCH = "WEB_SEARCH"
    MODEL_API = "MODEL_API"
    VECTOR_DB = "VECTOR_DB"


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior"""

    # Failure thresholds
    failure_threshold: int = 5  # Failures before opening circuit
    success_threshold: int = 1  # Successes in half-open to close circuit
    # Some tests configure half_open_max_calls to control HALF_OPEN behavior; map it to success_threshold
    half_open_max_calls: Optional[int] = None
    timeout_duration: float = 60.0  # Time before transitioning to half-open
    recovery_timeout: Optional[
        float
    ] = 60.0  # Alias for timeout_duration for test compatibility

    # Retry configuration
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 30.0
    exponential_base: float = 2.0
    jitter_factor: float = 0.1

    # Service-specific settings
    service_type: ServiceType = ServiceType.DAYTONA
    health_check_interval: int = 30  # Seconds between health checks
    health_check_function: Optional[Callable[[], bool]] = None

    # Exception handling
    retriable_exceptions: tuple = (
        ConnectionError,
        TimeoutError,
        OSError,
    )
    expected_exception: Optional[type] = Exception  # For test compatibility
    degradation_strategy: Optional[Callable[[], Any]] = None

    # Back-compat alias expected by tests
    @property
    def retry_exceptions(self):  # pragma: no cover - simple alias used by tests
        return self.retriable_exceptions

    def __post_init__(self):
        # If half_open_max_calls is provided, align success_threshold with it
        if self.half_open_max_calls is not None:
            self.success_threshold = int(self.half_open_max_calls)


@dataclass
class CircuitBreakerMetrics:
    """Metrics for circuit breaker monitoring"""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    circuit_open_count: int = 0
    half_open_attempts: int = 0

    # Timing metrics
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None
    last_state_change: Optional[float] = None

    # Performance metrics
    avg_response_time: float = 0.0
    total_response_time: float = 0.0

    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 1.0
        return self.successful_requests / self.total_requests

    @property
    def failure_rate(self) -> float:
        return 1.0 - self.success_rate


class CircuitBreakerError(Exception):
    """Exception raised when circuit breaker is open"""

    pass


class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open (alias for CircuitBreakerError)"""

    pass


class GracefulDegradationError(Exception):
    """Exception for graceful degradation scenarios"""

    pass


class CircuitBreaker:
    """
    Circuit breaker implementation for external service calls

    Provides fault tolerance with three states:
    - CLOSED: Normal operation
    - OPEN: Fast fail, service unavailable
    - HALF_OPEN: Testing service recovery
    """

    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.metrics = CircuitBreakerMetrics()

        # State management
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None

        # Health checking
        self._health_check_task: Optional[asyncio.Task] = None
        self._running = False
        logger.info(
            f"Circuit breaker initialized: {self.name} for {self.config.service_type.value}"
        )

    async def __aenter__(self):
        """Async context manager entry"""
        await self.start_health_checks()
        return self

    async def __aexit__(self, exc_type, exc_val, _):
        """Async context manager exit"""
        await self.stop_health_checks()

    def __call__(self, func: Callable) -> Callable:
        """Decorator for circuit breaker protection"""
        if asyncio.iscoroutinefunction(func):
            return self._async_wrapper(func)
        else:
            return self._sync_wrapper(func)

    def _async_wrapper(self, func: Callable) -> Callable:
        """Async function wrapper"""

        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await self.call_async(func, *args, **kwargs)

        return wrapper

    def _sync_wrapper(self, func: Callable) -> Callable:
        """Sync function wrapper"""

        @wraps(func)
        def wrapper(*args, **kwargs):
            return self.call_sync(func, *args, **kwargs)

        return wrapper

    async def call_async(self, func: Callable[..., Awaitable[T]], *args, **kwargs) -> T:
        """Execute async function with circuit breaker protection"""
        if not self._should_allow_request():
            self.metrics.total_requests += 1
            raise CircuitBreakerOpenError(
                f"Circuit breaker OPEN for {self.config.service_type.value}"
            )

        return await self._execute_with_retry_async(func, *args, **kwargs)

    def call_sync(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Execute sync function with circuit breaker protection"""
        if not self._should_allow_request():
            self.metrics.total_requests += 1
            raise CircuitBreakerOpenError(
                f"Circuit breaker OPEN for {self.config.service_type.value}"
            )

        return self._execute_with_retry_sync(func, *args, **kwargs)

    # Alias expected by tests
    def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        return self.call_sync(func, *args, **kwargs)

    async def _execute_with_retry_async(self, func: Callable, *args, **kwargs) -> Any:
        """Execute with exponential backoff retry logic"""
        last_exception = None

        for attempt in range(self.config.max_retries + 1):
            start_time = time.perf_counter()

            try:
                self.metrics.total_requests += 1
                result = await func(*args, **kwargs)

                # Record success
                response_time = time.perf_counter() - start_time
                self._record_success(response_time)

                return result

            except self.config.retriable_exceptions as e:
                last_exception = e
                # Don't record failure on each retry - only when all retries exhausted

                if attempt < self.config.max_retries:
                    delay = self._calculate_delay(attempt)
                    logger.warning(
                        f"Attempt {attempt + 1} failed for {self.config.service_type.value}, "
                        f"retrying in {delay:.2f}s: {e}"
                    )
                    await asyncio.sleep(delay)
                else:
                    # All retries exhausted - record circuit breaker failure
                    self._record_failure(e)
                    simple_log_error(
                        "execute_with_retry_sync",
                        e,
                        service_type=self.config.service_type.value,
                    )
                    break

            except Exception as e:
                # Non-retriable exception - record circuit breaker failure
                self._record_failure(e)
                simple_log_error(
                    "execute_with_retry_sync_non_retriable",
                    e,
                    service_type=self.config.service_type.value,
                )
                raise

        # All retries failed
        if last_exception:
            raise last_exception
        else:
            raise CircuitBreakerError("All retries exhausted")

    def _execute_with_retry_sync(self, func: Callable, *args, **kwargs) -> Any:
        """Execute with exponential backoff retry logic (sync version)"""
        last_exception = None

        for attempt in range(self.config.max_retries + 1):
            start_time = time.perf_counter()

            try:
                self.metrics.total_requests += 1
                result = func(*args, **kwargs)

                # Record success
                response_time = time.perf_counter() - start_time
                self._record_success(response_time)

                return result

            except self.config.retriable_exceptions as e:
                last_exception = e
                # Don't record failure on each retry - only when all retries exhausted

                if attempt < self.config.max_retries:
                    delay = self._calculate_delay(attempt)
                    logger.warning(
                        f"Attempt {attempt + 1} failed for {self.config.service_type.value}, "
                        f"retrying in {delay:.2f}s: {e}"
                    )
                    time.sleep(delay)
                else:
                    # All retries exhausted - record circuit breaker failure
                    self._record_failure(e)
                    simple_log_error(
                        "execute_with_retry_async",
                        e,
                        service_type=self.config.service_type.value,
                    )
                    break

            except Exception as e:
                # Non-retriable exception - record circuit breaker failure
                self._record_failure(e)
                simple_log_error(
                    "execute_with_retry_async_non_retriable",
                    e,
                    service_type=self.config.service_type.value,
                )
                raise

        # All retries failed
        if last_exception:
            raise last_exception
        else:
            raise CircuitBreakerError("All retries exhausted")

    def _should_allow_request(self) -> bool:
        """Determine if request should be allowed based on circuit state"""
        current_time = time.time()

        if self.state == CircuitBreakerState.CLOSED:
            return True

        elif self.state == CircuitBreakerState.OPEN:
            # Check if recovery timeout has elapsed
            recovery_timeout = (
                self.config.recovery_timeout or self.config.timeout_duration
            )
            if (
                self.last_failure_time
                and current_time - self.last_failure_time >= recovery_timeout
            ):
                self._transition_to_half_open()
                return True
            return False

        elif self.state == CircuitBreakerState.HALF_OPEN:
            # Allow limited requests in half-open state
            return self.success_count < self.config.success_threshold

        return False

    def _record_success(self, response_time: float):
        """Record a successful request"""
        self.metrics.successful_requests += 1
        self.metrics.last_success_time = time.time()

        # Update response time metrics
        self.metrics.total_response_time += response_time
        self.metrics.avg_response_time = (
            self.metrics.total_response_time / self.metrics.successful_requests
        )

        # State transition logic
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self._transition_to_closed()
        elif self.state == CircuitBreakerState.CLOSED:
            # Reset failure count on success
            self.failure_count = 0

    def _record_failure(self, exception: Optional[Exception] = None):
        """Record a failed request"""
        self.metrics.failed_requests += 1
        self.metrics.last_failure_time = time.time()
        self.last_failure_time = time.time()

        # Only count failures for expected exceptions
        if self.config.expected_exception and exception:
            if not isinstance(exception, self.config.expected_exception):
                # This is not an expected exception, don't count it as a circuit breaker failure
                return

        if self.state == CircuitBreakerState.CLOSED:
            self.failure_count += 1
            if self.failure_count >= self.config.failure_threshold:
                self._transition_to_open()
        elif self.state == CircuitBreakerState.HALF_OPEN:
            # Any failure in half-open returns to open and increments failure count
            self.failure_count += 1
            self._transition_to_open()

    def _transition_to_open(self):
        """Transition circuit breaker to OPEN state"""
        self.state = CircuitBreakerState.OPEN
        self.metrics.circuit_open_count += 1
        self.metrics.last_state_change = time.time()
        logger.warning(f"Circuit breaker OPENED for {self.config.service_type.value}")

    def _transition_to_half_open(self):
        """Transition circuit breaker to HALF_OPEN state"""
        self.state = CircuitBreakerState.HALF_OPEN
        self.success_count = 0
        self.metrics.half_open_attempts += 1
        self.metrics.last_state_change = time.time()
        logger.info(f"Circuit breaker HALF_OPEN for {self.config.service_type.value}")

    def _transition_to_closed(self):
        """Transition circuit breaker to CLOSED state"""
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.metrics.last_state_change = time.time()
        logger.info(f"Circuit breaker CLOSED for {self.config.service_type.value}")

    def _calculate_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay with jitter"""
        base_delay = self.config.base_delay * (self.config.exponential_base**attempt)
        jitter = base_delay * self.config.jitter_factor * (random.random() * 2 - 1)
        delay = min(base_delay + jitter, self.config.max_delay)
        return max(delay, 0.1)  # Minimum delay of 100ms

    # Health check functionality

    async def start_health_checks(self):
        """Start background health checks"""
        self._running = True
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        logger.info(f"Started health checks for {self.config.service_type.value}")

    async def stop_health_checks(self):
        """Stop background health checks"""
        self._running = False
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        logger.info(f"Stopped health checks for {self.config.service_type.value}")

    async def _health_check_loop(self):
        """Background health check loop"""
        while self._running:
            try:
                await asyncio.sleep(self.config.health_check_interval)

                if self.state == CircuitBreakerState.OPEN:
                    # Perform health check to see if service has recovered
                    await self._perform_health_check()

            except asyncio.CancelledError:
                break
            except Exception as e:
                simple_log_error(
                    "health_check_loop", e, service_type=self.config.service_type.value
                )

    async def _perform_health_check(self):
        """Perform a health check on the external service"""
        try:
            # This would be implemented per service type
            if self.config.service_type == ServiceType.DAYTONA:
                await self._health_check_daytona()
            elif self.config.service_type == ServiceType.REDIS:
                await self._health_check_redis()
            elif self.config.service_type == ServiceType.WEB_SEARCH:
                await self._health_check_web_search()
            else:
                logger.debug(
                    f"No health check implemented for {self.config.service_type.value}"
                )

        except Exception as e:
            logger.debug(
                f"Health check failed for {self.config.service_type.value}: {e}"
            )

    async def _health_check_daytona(self):
        """Health check for Daytona service"""
        # This would make a lightweight API call to Daytona
        logger.debug("Performing Daytona health check")

    async def _health_check_redis(self):
        """Health check for Redis service"""
        # This would ping Redis
        logger.debug("Performing Redis health check")

    async def _health_check_web_search(self):
        """Health check for web search service"""
        # This would make a test search query
        logger.debug("Performing web search health check")

    # Status and monitoring

    def health_check(self) -> bool:
        """Synchronous health check using provided function if any."""
        if callable(self.config.health_check_function):
            try:
                return bool(self.config.health_check_function())
            except Exception as e:  # pragma: no cover - safety
                logger.debug(f"Health check function errored for {self.name}: {e}")
                return False
        # Default to healthy when no function is provided
        return True

    def get_status(self) -> Dict[str, Any]:
        """Get current circuit breaker status"""
        return {
            "service": self.config.service_type.value,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time,
            "metrics": {
                "total_requests": self.metrics.total_requests,
                "successful_requests": self.metrics.successful_requests,
                "failed_requests": self.metrics.failed_requests,
                "success_rate": self.metrics.success_rate,
                "failure_rate": self.metrics.failure_rate,
                "avg_response_time": self.metrics.avg_response_time,
                "circuit_open_count": self.metrics.circuit_open_count,
                "half_open_attempts": self.metrics.half_open_attempts,
            },
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "timeout_duration": self.config.timeout_duration,
                "max_retries": self.config.max_retries,
            },
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Expose metrics snapshot (compat with tests)."""
        return {
            "total_calls": self.metrics.total_requests,
            "successes": self.metrics.successful_requests,
            "failures": self.metrics.failed_requests,
            "success_rate": self.metrics.success_rate,
            "avg_response_time": self.metrics.avg_response_time,
        }

    def force_open(self):
        """Manually force circuit breaker to OPEN state"""
        self._transition_to_open()
        logger.warning(
            f"Circuit breaker manually OPENED for {self.config.service_type.value}"
        )

    def force_closed(self):
        """Manually force circuit breaker to CLOSED state"""
        self._transition_to_closed()
        logger.info(
            f"Circuit breaker manually CLOSED for {self.config.service_type.value}"
        )

    def get_state_info(self) -> Dict[str, Any]:
        """Get detailed state information for the circuit breaker"""
        return {
            "name": self.name,
            "state": self.state.value,
            "service_type": self.config.service_type.value,
            "failure_threshold": self.config.failure_threshold,
            "timeout_duration": self.config.timeout_duration,
            "recovery_timeout": self.config.recovery_timeout,
            "expected_exception": self.config.expected_exception.__name__
            if self.config.expected_exception
            else None,
            "metrics": self.get_metrics(),
            "last_failure_time": self.last_failure_time,
            "failure_count": getattr(self, "failure_count", 0),
            "consecutive_failures": getattr(self, "consecutive_failures", 0),
        }

    async def async_call(self, func: Callable[..., Awaitable[T]], *args, **kwargs) -> T:
        """Async version of call method"""
        return await self.call_async(func, *args, **kwargs)
        """Call with graceful degradation if available when failures occur or circuit is open."""
        try:
            return self.call_sync(func, *args, **kwargs)
        except CircuitBreakerError:
            if callable(self.config.degradation_strategy):
                return self.config.degradation_strategy()
            raise
        except Exception:
            # Record failure already happened inside call path; degrade if strategy exists
            if callable(self.config.degradation_strategy):
                return self.config.degradation_strategy()
            raise


class CircuitBreakerRegistry:
    """Registry for managing multiple circuit breakers"""

    def __init__(self):
        self._breakers: Dict[str, CircuitBreaker] = {}
        self._running = False

    def register(self, name: str, circuit_breaker: CircuitBreaker):
        """Register a circuit breaker"""
        self._breakers[name] = circuit_breaker
        logger.info(f"Registered circuit breaker: {name}")

    def get(self, name: str) -> Optional[CircuitBreaker]:
        """Get a circuit breaker by name"""
        return self._breakers.get(name)

    def get_all_status(self) -> Dict[str, Any]:
        """Get status of all circuit breakers"""
        return {name: breaker.get_status() for name, breaker in self._breakers.items()}

    async def start_all(self):
        """Start all circuit breakers"""
        self._running = True
        for breaker in self._breakers.values():
            await breaker.start_health_checks()

    async def stop_all(self):
        """Stop all circuit breakers"""
        self._running = False
        for breaker in self._breakers.values():
            await breaker.stop_health_checks()


# Graceful degradation strategies


class GracefulDegradationStrategy:
    """Base class for graceful degradation strategies"""

    async def handle_service_failure(
        self, service_type: ServiceType, error: Exception
    ) -> Any:
        """Handle service failure with graceful degradation"""
        raise NotImplementedError


class CacheBasedDegradation(GracefulDegradationStrategy):
    """Graceful degradation using cached responses"""

    def __init__(self, cache):
        self.cache = cache

    async def handle_service_failure(
        self, service_type: ServiceType, error: Exception
    ) -> Any:
        """Return cached response if available"""
        if service_type == ServiceType.WEB_SEARCH:
            # Return cached search results
            return await self._get_cached_search_results()
        elif service_type == ServiceType.DAYTONA:
            # Return cached execution results
            return await self._get_cached_execution_results()
        else:
            raise GracefulDegradationError(
                f"No degradation strategy for {service_type.value}"
            )

    async def _get_cached_search_results(self):
        """Get cached web search results"""
        cached_results = await self.cache.get("web_search:fallback")
        if cached_results:
            logger.info("Using cached web search results for graceful degradation")
            return cached_results
        raise GracefulDegradationError("No cached web search results available")

    async def _get_cached_execution_results(self):
        """Get cached execution results"""
        cached_results = await self.cache.get("daytona:fallback")
        if cached_results:
            logger.info("Using cached execution results for graceful degradation")
            return cached_results
        raise GracefulDegradationError("No cached execution results available")


class FallbackServiceDegradation(GracefulDegradationStrategy):
    """Graceful degradation using fallback services"""

    async def handle_service_failure(
        self, service_type: ServiceType, error: Exception
    ) -> Any:
        """Use fallback service implementations"""
        if service_type == ServiceType.DAYTONA:
            # Use local execution instead of Daytona
            return await self._execute_locally()
        elif service_type == ServiceType.WEB_SEARCH:
            # Use alternative search provider
            return await self._use_alternative_search()
        else:
            raise GracefulDegradationError(
                f"No fallback service for {service_type.value}"
            )

    async def _execute_locally(self):
        """Execute code locally instead of in Daytona sandbox"""
        logger.warning("Using local execution as Daytona fallback")
        return {"status": "fallback", "output": "Local execution fallback"}

    async def _use_alternative_search(self):
        """Use alternative search provider"""
        logger.warning("Using alternative search provider as fallback")
        return {"results": [], "status": "fallback"}


# Factory functions for common configurations


def create_daytona_circuit_breaker() -> CircuitBreaker:
    """Create circuit breaker for Daytona service"""
    config = CircuitBreakerConfig(
        service_type=ServiceType.DAYTONA,
        failure_threshold=5,
        timeout_duration=60.0,
        # Let higher-level retry logic handle retries; circuit breaker should not retry
        max_retries=0,
        base_delay=2.0,
        # Tests expect retry_exceptions == (Exception,)
        retriable_exceptions=(Exception,),
    )
    breaker = CircuitBreaker("daytona", config)
    # Register in global registry for visibility in health/registry tests
    circuit_breaker_registry.register("daytona", breaker)
    return breaker


def create_redis_circuit_breaker() -> CircuitBreaker:
    """Create circuit breaker for Redis service"""
    config = CircuitBreakerConfig(
        service_type=ServiceType.REDIS,
        failure_threshold=3,
        timeout_duration=30.0,
        max_retries=3,
        base_delay=1.0,
        retriable_exceptions=(
            ConnectionError,
            TimeoutError,
            OSError,
        ),
    )
    breaker = CircuitBreaker("redis", config)
    circuit_breaker_registry.register("redis", breaker)
    return breaker


def create_web_search_circuit_breaker() -> CircuitBreaker:
    """Create circuit breaker for web search service"""
    config = CircuitBreakerConfig(
        service_type=ServiceType.WEB_SEARCH,
        failure_threshold=10,
        timeout_duration=120.0,
        max_retries=2,
        base_delay=1.5,
        retriable_exceptions=(
            ConnectionError,
            TimeoutError,
            OSError,
        ),
    )
    breaker = CircuitBreaker("websearch", config)
    circuit_breaker_registry.register("websearch", breaker)
    return breaker


# Backwards-compatibility alias (tests import this name)
def create_websearch_circuit_breaker() -> (
    CircuitBreaker
):  # pragma: no cover - thin alias
    """Alias for create_web_search_circuit_breaker.

    Some callers use the older name without the underscore between
    'web' and 'search'. Keep this shim to preserve compatibility.
    """
    return create_web_search_circuit_breaker()


# Global registry instance
circuit_breaker_registry = CircuitBreakerRegistry()


# Convenience decorators


def with_circuit_breaker(
    service_type: ServiceType, config: Optional[CircuitBreakerConfig] = None
):
    """Decorator to add circuit breaker protection to a function"""

    def decorator(func: Callable) -> Callable:
        if config is None:
            # Use default config based on service type
            if service_type == ServiceType.DAYTONA:
                breaker = create_daytona_circuit_breaker()
            elif service_type == ServiceType.REDIS:
                breaker = create_redis_circuit_breaker()
            elif service_type == ServiceType.WEB_SEARCH:
                breaker = create_web_search_circuit_breaker()
            else:
                breaker = CircuitBreaker(
                    service_type.value, CircuitBreakerConfig(service_type=service_type)
                )
        else:
            # When custom config is provided, honor it and name by service type
            breaker = CircuitBreaker(service_type.value, config)

        # Register in global registry
        circuit_breaker_registry.register(
            f"{service_type.value}_{func.__name__}", breaker
        )

        return breaker(func)

    return decorator
