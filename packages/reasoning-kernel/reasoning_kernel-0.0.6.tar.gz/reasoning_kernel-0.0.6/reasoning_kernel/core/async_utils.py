"""
Async Utilities
===============

Utilities for async operations in the Reasoning Kernel.
"""

import asyncio
import logging
import time
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class TimeoutErrorWithContext(asyncio.TimeoutError):
    """Timeout error that carries contextual information."""

    def __init__(self, message: str, timeout_seconds: Optional[float] = None):
        super().__init__(message)
        self.timeout_seconds = timeout_seconds


async def with_timeout(coro, timeout_seconds: float):
    """Compatibility wrapper: run a coroutine with a timeout and raise contextual error.

    Special-case timeout<=0: allow immediate coroutines to complete.
    """
    try:
        if timeout_seconds is not None and timeout_seconds <= 0:
            # Try to await directly to allow immediate completion
            return await coro
        return await asyncio.wait_for(coro, timeout=timeout_seconds)
    except asyncio.TimeoutError as e:
        raise TimeoutErrorWithContext(
            f"Operation timed out after {timeout_seconds} seconds", timeout_seconds
        ) from e


async def with_retry(
    func: Callable,
    *,
    retries: int = 3,
    backoff_base: float = 1.0,
    backoff_multiplier: float = 2.0,
    retry_on: tuple = (Exception,),
) -> Any:
    """Compatibility wrapper: retry an async callable according to policy."""

    async def _call():
        return await func()

    # Use existing retry manager for behavior
    retry_manager = AsyncRetryManager(
        max_retries=retries,
        base_delay=backoff_base,
        backoff_factor=backoff_multiplier,
        retry_exceptions=retry_on,
    )
    return await retry_manager.retry(_call)


class AsyncExecutor:
    """Simple async executor with bounded concurrency and optional per-task timeout."""

    def __init__(self, max_concurrency: int = 5):
        self._semaphore = asyncio.Semaphore(max_concurrency)

    async def run(
        self, func: Callable, *, timeout_seconds: Optional[float] = None
    ) -> Any:
        async with self._semaphore:
            coro = func() if callable(func) and not asyncio.iscoroutine(func) else func
            if timeout_seconds is not None:
                try:
                    return await asyncio.wait_for(coro, timeout=timeout_seconds)
                except asyncio.TimeoutError as e:
                    # Propagate as contextual timeout for compatibility
                    raise TimeoutErrorWithContext(
                        f"Operation timed out after {timeout_seconds} seconds",
                        timeout_seconds,
                    ) from e
            return await coro

    async def map(
        self,
        tasks: List[Callable[[], Any]],
        *,
        timeout_seconds: Optional[float] = None,
    ) -> List[Any]:
        if not tasks:
            return []

        async def _run_task(factory: Callable[[], Any]):
            async with self._semaphore:
                coro = factory()
                if timeout_seconds is not None:
                    return await asyncio.wait_for(coro, timeout=timeout_seconds)
                return await coro

        return await asyncio.gather(*[_run_task(t) for t in tasks])


async def run_with_timeout(
    coro, timeout_seconds: float, default_value: Any = None
) -> Any:
    """
    Run a coroutine with a timeout

    Args:
        coro: The coroutine to run
        timeout_seconds: Timeout in seconds
        default_value: Value to return if timeout occurs

    Returns:
        Result of the coroutine or default_value if timeout
    """
    try:
        return await asyncio.wait_for(coro, timeout=timeout_seconds)
    except asyncio.TimeoutError:
        logger.warning(f"Operation timed out after {timeout_seconds} seconds")
        return default_value


async def run_with_retries(
    coro_func: Callable,
    max_retries: int = 3,
    delay_seconds: float = 1.0,
    backoff_multiplier: float = 2.0,
    *args,
    **kwargs,
) -> Any:
    """
    Run a coroutine function with retries

    Args:
        coro_func: Async function to call
        max_retries: Maximum number of retries
        delay_seconds: Initial delay between retries
        backoff_multiplier: Multiplier for delay on each retry
        *args, **kwargs: Arguments to pass to the function

    Returns:
        Result of the function call

    Raises:
        The last exception if all retries fail
    """
    last_exception = None
    current_delay = delay_seconds

    for attempt in range(max_retries + 1):
        try:
            return await coro_func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            if attempt < max_retries:
                logger.warning(
                    f"Attempt {attempt + 1} failed: {e}. "
                    f"Retrying in {current_delay} seconds..."
                )
                await asyncio.sleep(current_delay)
                current_delay *= backoff_multiplier
            else:
                logger.error(f"All {max_retries + 1} attempts failed")

    raise last_exception


async def gather_with_concurrency(
    coroutines: List[Any], max_concurrency: int = 10
) -> List[Any]:
    """
    Run coroutines with limited concurrency

    Args:
        coroutines: List of coroutines to run
        max_concurrency: Maximum number of concurrent operations

    Returns:
        List of results in the same order as input coroutines
    """
    semaphore = asyncio.Semaphore(max_concurrency)

    async def run_with_semaphore(coro):
        async with semaphore:
            return await coro

    tasks = [run_with_semaphore(coro) for coro in coroutines]
    return await asyncio.gather(*tasks)


def async_timer(func: Callable) -> Callable:
    """
    Decorator to time async function execution

    Args:
        func: Async function to time

    Returns:
        Wrapped function that logs execution time
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.debug(f"{func.__name__} completed in {execution_time:.3f} seconds")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                f"{func.__name__} failed after {execution_time:.3f} seconds: {e}"
            )
            raise

    return wrapper


async def safe_gather(*coroutines, return_exceptions: bool = True) -> List[Any]:
    """
    Safely gather coroutines, handling exceptions gracefully

    Args:
        *coroutines: Coroutines to gather
        return_exceptions: Whether to return exceptions as results

    Returns:
        List of results or exceptions
    """
    try:
        return await asyncio.gather(*coroutines, return_exceptions=return_exceptions)
    except Exception as e:
        logger.error(f"Error in safe_gather: {e}")
        return [e] * len(coroutines)


class AsyncTaskManager:
    """Manager for async tasks with lifecycle management"""

    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.completed_tasks: List[Dict[str, Any]] = []
        self.failed_tasks: List[Dict[str, Any]] = []
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def submit_task(
        self,
        task_id: str,
        coro_func: Callable,
        args: tuple = (),
        kwargs: Optional[dict] = None,
    ) -> str:
        """Submit an async task for execution"""
        if kwargs is None:
            kwargs = {}

        async def task_wrapper():
            try:
                if asyncio.iscoroutinefunction(coro_func):
                    result = await coro_func(*args, **kwargs)
                else:
                    # If it's not a coroutine function, assume it's already a coroutine
                    result = await coro_func(*args, **kwargs)
                self.completed_tasks.append(
                    {"task_id": task_id, "result": result, "completed_at": time.time()}
                )
                return result
            except Exception as e:
                self.failed_tasks.append(
                    {"task_id": task_id, "error": str(e), "failed_at": time.time()}
                )
                raise
            finally:
                if task_id in self.active_tasks:
                    del self.active_tasks[task_id]

        async with self.semaphore:
            task = asyncio.create_task(task_wrapper())
            self.active_tasks[task_id] = task
            return task_id

    async def wait_for_task(self, task_id: str) -> Any:
        """Wait for a specific task to complete"""
        if task_id not in self.active_tasks:
            # Check if it already completed
            for completed in self.completed_tasks:
                if completed["task_id"] == task_id:
                    return completed["result"]
            for failed in self.failed_tasks:
                if failed["task_id"] == task_id:
                    raise ValueError(failed["error"])
            raise ValueError(f"Task {task_id} not found")

        task = self.active_tasks[task_id]
        try:
            return await task
        except Exception:
            # Error should already be recorded in failed_tasks by task_wrapper
            raise

    async def wait_for_all_tasks(self) -> List[Any]:
        """Wait for all active tasks to complete"""
        if not self.active_tasks:
            return []

        tasks = list(self.active_tasks.values())
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task"""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                logger.debug(f"Task {task_id} was cancelled")
            del self.active_tasks[task_id]
            return True
        return False

    def get_active_tasks(self) -> List[str]:
        """Get list of active task IDs"""
        return list(self.active_tasks.keys())

    def get_task_status(self, task_id: str) -> Dict[str, str]:
        """Get the status of a task"""
        if task_id in self.active_tasks:
            return {"status": "running", "task_name": task_id}
        for completed in self.completed_tasks:
            if completed["task_id"] == task_id:
                return {"status": "completed", "task_name": task_id}
        for failed in self.failed_tasks:
            if failed["task_id"] == task_id:
                return {"status": "failed", "task_name": task_id}
        return {"status": "not_found", "task_name": task_id}


class AsyncBatchProcessor:
    """Process items in batches asynchronously"""

    def __init__(
        self,
        batch_size: int = 10,
        max_concurrency: int = 5,
        auto_flush: bool = False,
        batch_callback: Optional[Callable] = None,
    ):
        self.batch_size = batch_size
        self.max_concurrency = max_concurrency
        self.pending_items: List[Any] = []
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.auto_flush = auto_flush
        self.batch_callback = batch_callback

    async def process_batch(
        self, items: List[Any], processor_func: Callable, ignore_failures: bool = False
    ) -> List[Any]:
        """Process items in batches"""
        results = []
        for i in range(0, len(items), self.batch_size):
            batch = items[i : i + self.batch_size]
            async with self.semaphore:
                if ignore_failures:
                    batch_results = await asyncio.gather(
                        *[processor_func(item) for item in batch],
                        return_exceptions=True,
                    )
                    # Filter out exceptions if ignore_failures is True
                    batch_results = [
                        r for r in batch_results if not isinstance(r, Exception)
                    ]
                else:
                    batch_results = await asyncio.gather(
                        *[processor_func(item) for item in batch]
                    )
                results.extend(batch_results)
        return results

    async def add_item(self, item) -> None:
        """Add an item to the pending batch"""
        self.pending_items.append(item)
        if self.auto_flush and len(self.pending_items) >= self.batch_size:
            await self.flush_batch()

    async def flush_batch(self) -> None:
        """Process all pending items"""
        if not self.pending_items:
            return

        items_to_process = self.pending_items.copy()
        self.pending_items.clear()

        # This would need a processor function to be set, but for now we'll assume it's handled externally
        if self.batch_callback:
            await self.batch_callback(items_to_process)

    async def process_pending(self, processor_func: Callable) -> List[Any]:
        """Process all pending items with the given processor function"""
        if not self.pending_items:
            return []

        items_to_process = self.pending_items.copy()
        self.pending_items.clear()

        return await self.process_batch(items_to_process, processor_func)


class AsyncRetryManager:
    """Manager for retrying async operations"""

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        backoff_factor: float = 2.0,
        retry_exceptions: Optional[tuple] = None,
        retry_callback: Optional[Callable] = None,
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.backoff_factor = backoff_factor
        self.retry_exceptions = retry_exceptions or (Exception,)
        self.retry_callback = retry_callback

    async def retry(self, coro_func: Callable, *args, **kwargs) -> Any:
        """Execute a coroutine with retry logic"""
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                return await coro_func(*args, **kwargs)
            except self.retry_exceptions as e:
                last_exception = e
                if attempt < self.max_retries:
                    delay = self.base_delay * (self.backoff_factor**attempt)
                    if self.retry_callback:
                        await self.retry_callback(attempt + 1, e)
                    await asyncio.sleep(delay)

        # If we get here, all retries failed
        if last_exception:
            raise last_exception
        else:
            raise RuntimeError("Retry failed with unknown error")

    async def execute_with_retry(self, coro_func: Callable, *args, **kwargs) -> Any:
        """Execute a coroutine with retry logic (deprecated, use retry instead)"""
        return await self.retry(coro_func, *args, **kwargs)


class AsyncTimeoutManager:
    """Manager for async operations with timeouts"""

    def __init__(
        self, default_timeout: float = 30.0, timeout_callback: Optional[Callable] = None
    ):
        self.default_timeout = default_timeout
        self.timeout_callback = timeout_callback

    async def with_timeout(
        self, coro, timeout: Optional[float] = None, operation_name: str = "operation"
    ) -> Any:
        """Execute coroutine with timeout"""
        timeout_value = timeout or self.default_timeout

        # If coro is a function, call it to get the coroutine
        if callable(coro) and not asyncio.iscoroutine(coro):
            coro = coro()

        # Ensure we have a coroutine or future
        if not asyncio.iscoroutine(coro) and not asyncio.isfuture(coro):
            raise TypeError("Expected a coroutine or future")

        try:
            return await asyncio.wait_for(coro, timeout=timeout_value)
        except asyncio.TimeoutError:
            if self.timeout_callback:
                await self.timeout_callback(operation_name, timeout_value)
            raise

    async def execute_with_timeout(self, coro, timeout: Optional[float] = None) -> Any:
        """Execute coroutine with timeout (deprecated, use with_timeout instead)"""
        return await self.with_timeout(coro, timeout)


class ConcurrencyLimiter:
    """Limit concurrent execution of async operations"""

    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self._current_count = 0

    @property
    def current_count(self) -> int:
        """Get current number of active operations"""
        return self._current_count

    async def execute(self, coro) -> Any:
        """Execute coroutine with concurrency limit"""
        async with self:
            return await coro

    async def __aenter__(self):
        """Enter async context manager"""
        await self.semaphore.__aenter__()
        self._current_count += 1
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context manager"""
        self._current_count -= 1
        await self.semaphore.__aexit__(exc_type, exc_val, exc_tb)


class AsyncContextManager:
    """Async context manager utility"""

    def __init__(
        self,
        enter_func: Optional[Callable] = None,
        exit_func: Optional[Callable] = None,
    ):
        self.enter_func = enter_func
        self.exit_func = exit_func

    async def __aenter__(self):
        if self.enter_func:
            return await self.enter_func()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.exit_func:
            await self.exit_func(exc_type, exc_val, exc_tb)
