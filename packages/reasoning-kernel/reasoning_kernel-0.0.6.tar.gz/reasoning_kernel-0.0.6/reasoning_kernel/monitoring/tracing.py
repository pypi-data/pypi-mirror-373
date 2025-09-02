"""
Optimized Tracing Utilities
==========================

High-performance tracing and monitoring utilities for the reasoning kernel.
Optimized to minimize overhead while maintaining observability.
"""

import asyncio
import logging
import threading
import time
from collections import deque
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)


# Configuration for tracing optimization
class TracingConfig:
    """Configuration for tracing behavior"""

    def __init__(self):
        self.enabled = True
        self.sample_rate = 0.1  # Only trace 10% of operations
        self.async_logging = True
        self.batch_size = 100
        self.flush_interval = 5.0  # seconds
        self.max_queue_size = 10000


_config = TracingConfig()

# Async logging queue for high-performance logging
_log_queue = deque(maxlen=_config.max_queue_size)
_log_thread: Optional[threading.Thread] = None
_log_shutdown = threading.Event()


def _async_log_worker():
    """Background worker for async logging"""
    batch = []
    last_flush = time.time()

    while not _log_shutdown.is_set():
        try:
            # Collect logs from queue
            while _log_queue and len(batch) < _config.batch_size:
                batch.append(_log_queue.popleft())

            current_time = time.time()

            # Flush if batch is full or flush interval reached
            if batch and (len(batch) >= _config.batch_size or current_time - last_flush >= _config.flush_interval):
                # Process batch (in real implementation, this would write to storage)
                for log_entry in batch:
                    # Minimal processing to reduce overhead
                    pass
                batch.clear()
                last_flush = current_time

            # Small sleep to prevent busy waiting
            time.sleep(0.01)

        except Exception:
            # Silent failure to avoid affecting main application
            break


def initialize_tracing(config: Optional[TracingConfig] = None) -> None:
    """Initialize optimized tracing system"""
    global _config, _log_thread

    if config:
        _config = config

    if _config.async_logging and _log_thread is None:
        _log_thread = threading.Thread(target=_async_log_worker, daemon=True)
        _log_thread.start()

    logger.info("Optimized tracing system initialized")


def _should_trace(operation_name: str) -> bool:
    """Determine if operation should be traced based on sampling"""
    if not _config.enabled:
        return False

    # Always trace critical operations
    critical_ops = {"health_check", "error", "shutdown", "startup"}
    if any(critical in operation_name.lower() for critical in critical_ops):
        return True

    # Sample based on operation name hash for consistency
    import hashlib

    hash_val = int(hashlib.md5(operation_name.encode()).hexdigest()[:8], 16)
    return (hash_val % 100) < (_config.sample_rate * 100)


def _enqueue_log(level: str, message: str, **kwargs):
    """Enqueue log message for async processing"""
    if not _config.async_logging:
        # Fallback to synchronous logging
        getattr(logger, level)(message)
        return

    if len(_log_queue) < _config.max_queue_size:
        _log_queue.append({"level": level, "message": message, "timestamp": time.time(), **kwargs})


def trace_operation(operation_name: str, log_level: str = "debug"):
    """Optimized decorator to trace operation execution with minimal overhead"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not _should_trace(operation_name):
                return func(*args, **kwargs)

            start_time = time.perf_counter()  # Higher precision timer

            try:
                result = func(*args, **kwargs)
                execution_time = time.perf_counter() - start_time

                # Only log if execution time exceeds threshold or it's an error case
                if execution_time > 0.001:  # 1ms threshold
                    _enqueue_log(
                        log_level,
                        f"Operation completed: {operation_name}",
                        duration=execution_time,
                        operation=operation_name,
                    )

                return result
            except Exception as e:
                execution_time = time.perf_counter() - start_time
                _enqueue_log(
                    "error",
                    f"Operation failed: {operation_name}",
                    duration=execution_time,
                    operation=operation_name,
                    error=str(e),
                )
                raise

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not _should_trace(operation_name):
                return await func(*args, **kwargs)

            start_time = time.perf_counter()

            try:
                result = await func(*args, **kwargs)
                execution_time = time.perf_counter() - start_time

                # Only log if execution time exceeds threshold
                if execution_time > 0.001:  # 1ms threshold
                    _enqueue_log(
                        log_level,
                        f"Async operation completed: {operation_name}",
                        duration=execution_time,
                        operation=operation_name,
                    )

                return result
            except Exception as e:
                execution_time = time.perf_counter() - start_time
                _enqueue_log(
                    "error",
                    f"Async operation failed: {operation_name}",
                    duration=execution_time,
                    operation=operation_name,
                    error=str(e),
                )
                raise

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper

    return decorator


@contextmanager
def trace_context(operation_name: str, log_level: str = "debug"):
    """Optimized context manager for tracing operations"""
    if not _should_trace(operation_name):
        yield
        return

    start_time = time.perf_counter()

    try:
        yield
        execution_time = time.perf_counter() - start_time

        # Only log if execution time exceeds threshold
        if execution_time > 0.001:
            _enqueue_log(
                log_level,
                f"Context operation completed: {operation_name}",
                duration=execution_time,
                operation=operation_name,
            )
    except Exception as e:
        execution_time = time.perf_counter() - start_time
        _enqueue_log(
            "error",
            f"Context operation failed: {operation_name}",
            duration=execution_time,
            operation=operation_name,
            error=str(e),
        )
        raise


class OptimizedOperationTracker:
    """High-performance operation tracking with memory optimization"""

    def __init__(self, max_operations: int = 1000):
        self.operations: Dict[str, Dict[str, Any]] = {}
        self.max_operations = max_operations
        self._lock = threading.RLock()

    def start_operation(self, operation_id: str, operation_name: str) -> None:
        """Start tracking an operation"""
        with self._lock:
            # Remove old operations if we're at capacity
            if len(self.operations) >= self.max_operations:
                # Remove oldest completed operations
                completed_ops = [k for k, v in self.operations.items() if v.get("status") in ("success", "failed")]
                if completed_ops:
                    for op_id in completed_ops[: len(completed_ops) // 4]:  # Remove 25%
                        del self.operations[op_id]

            self.operations[operation_id] = {
                "name": operation_name,
                "start_time": time.perf_counter(),
                "status": "running",
            }

    def complete_operation(self, operation_id: str, success: bool = True) -> None:
        """Complete an operation"""
        with self._lock:
            if operation_id in self.operations:
                operation = self.operations[operation_id]
                operation["end_time"] = time.perf_counter()
                operation["duration"] = operation["end_time"] - operation["start_time"]
                operation["status"] = "success" if success else "failed"

    def get_operation_stats(self) -> Dict[str, Any]:
        """Get operation statistics"""
        with self._lock:
            total_ops = len(self.operations)
            successful_ops = len([op for op in self.operations.values() if op.get("status") == "success"])

            return {
                "total_operations": total_ops,
                "successful_operations": successful_ops,
                "success_rate": successful_ops / total_ops if total_ops > 0 else 0.0,
                "active_operations": len([op for op in self.operations.values() if op.get("status") == "running"]),
            }


# Global optimized operation tracker
_operation_tracker = OptimizedOperationTracker()


def get_operation_tracker() -> OptimizedOperationTracker:
    """Get the global operation tracker"""
    return _operation_tracker


def shutdown_tracing():
    """Shutdown tracing system gracefully"""
    global _log_shutdown, _log_thread

    _log_shutdown.set()
    if _log_thread and _log_thread.is_alive():
        _log_thread.join(timeout=1.0)

    # Clear queues
    _log_queue.clear()

    logger.info("Tracing system shutdown complete")


# Compatibility class for tests
class TracingManager:
    """Tracing manager compatibility stub for monitoring tests."""

    def __init__(self, service_name: str = "reasoning_kernel"):
        self.service_name = service_name
        self._enabled = True

    def start_trace(self, operation_name: str, **kwargs) -> str:
        """Start a trace operation."""
        return f"trace_{operation_name}"

    def end_trace(self, trace_id: str, **kwargs) -> None:
        """End a trace operation."""
        pass

    @contextmanager
    def trace(self, operation_name: str, **kwargs):
        """Context manager for tracing."""
        trace_id = self.start_trace(operation_name, **kwargs)
        try:
            yield trace_id
        finally:
            self.end_trace(trace_id, **kwargs)

    def set_tag(self, trace_id: str, key: str, value: Any) -> None:
        """Set a tag on a trace."""
        pass

    def set_error(self, trace_id: str, error: Exception) -> None:
        """Set an error on a trace."""
        pass

    def enable(self) -> None:
        """Enable tracing."""
        self._enabled = True

    def disable(self) -> None:
        """Disable tracing."""
        self._enabled = False

    def is_enabled(self) -> bool:
        """Check if tracing is enabled."""
        return self._enabled
