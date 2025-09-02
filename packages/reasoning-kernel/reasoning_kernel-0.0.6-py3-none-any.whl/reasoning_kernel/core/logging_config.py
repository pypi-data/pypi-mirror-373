"""
Standardized logging configuration for the MSA Reasoning Engine.

This module provides structured logging with consistent context and formatting
across all components of the reasoning engine. It extends the existing logging
infrastructure with enhanced error mapping and standardized conventions.
"""

import logging
import os
import sys
import time
import uuid
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

try:
    import structlog

    STRUCTLOG_AVAILABLE = True
except Exception:  # pragma: no cover
    structlog = None  # type: ignore
    STRUCTLOG_AVAILABLE = False


def get_settings():  # pragma: no cover - replaced by tests via patch
    """Return unified settings if available. Tests patch this symbol directly."""
    try:
        from reasoning_kernel.core.unified_settings import get_settings as _real

        return _real()
    except Exception:
        return None


DEFAULT_FORMAT = "[%(asctime)s - %(name)s:%(lineno)d - %(levelname)s] %(message)s"

# Global request context storage
_request_context: Dict[str, Any] = {}


def get_request_id() -> str:
    """Get current request ID from context, or generate a new one."""
    return _request_context.get("request_id", str(uuid.uuid4()))


def get_request_context() -> Dict[str, Any]:
    """Get current request context."""
    return _request_context.copy()


@contextmanager
def request_context(request_id: str, **context):
    """Context manager for setting request-specific logging context."""
    global _request_context
    old_context = _request_context.copy()
    _request_context.update({"request_id": request_id, **context})
    try:
        yield
    finally:
        _request_context = old_context


def add_request_context(logger, method_name, event_dict):
    """Add request context to log events."""
    event_dict.update(_request_context)
    return event_dict


def add_service_context(logger, method_name, event_dict):
    """Add service-level context to log events."""
    event_dict.update(
        {
            "service": "reasoning-kernel",
            "version": "0.0.2",
            "environment": os.getenv("ENVIRONMENT", "development"),
        }
    )
    return event_dict


def configure_logging(
    level: str | None = None,
    json_logs: bool | None = None,
    enable_colors: bool = True,
    format_type: str | None = None,
    enable_structlog: bool = True,
    log_file: str | None = None,
):
    """Configure structured logging for the application.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        json_logs: Whether to output logs in JSON format
        enable_colors: Whether to enable colored output (for CLI)
    """
    # Read defaults from settings if not provided (tests patch get_settings)
    if level is None or json_logs is None or log_file is None:
        try:
            from reasoning_kernel.core.unified_settings import get_settings as _get_settings  # type: ignore
        except Exception:
            _get_settings = None  # type: ignore
        try:
            # allow tests to patch this symbol
            from . import settings as _unused  # noqa: F401
        except Exception:
            pass
        # Provide a module-level symbol that tests can patch
        try:
            from reasoning_kernel.core.unified_settings import get_settings as _real_get_settings  # type: ignore
        except Exception:
            _real_get_settings = None  # type: ignore
        global get_settings  # type: ignore
        if "get_settings" not in globals():  # type: ignore

            def get_settings():  # type: ignore
                return _real_get_settings() if _real_get_settings else None

        settings = None
        try:
            settings = get_settings()  # type: ignore
        except Exception:
            settings = None
        if level is None and settings is not None:
            lvl = getattr(
                getattr(settings, "log_level", None), "value", None
            ) or getattr(settings, "log_level", None)
            level = str(lvl or "INFO")
        if json_logs is None and settings is not None:
            json_logs = bool(getattr(settings, "json_logs", False))
        if log_file is None and settings is not None:
            log_file = getattr(settings, "log_file", None)

    if level is None:
        level = "INFO"
    if json_logs is None:
        json_logs = False
    if format_type is None:
        format_type = "structured"

    # Convert string level to logging constant
    log_level = getattr(logging, level.upper(), logging.INFO)

    # Configure structlog if available and enabled
    if STRUCTLOG_AVAILABLE and enable_structlog:
        processors = [
            structlog.stdlib.filter_by_level,
            add_request_context,
            add_service_context,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.StackInfoRenderer(),
        ]

        if json_logs:
            processors.extend(
                [
                    structlog.processors.format_exc_info,
                    structlog.processors.JSONRenderer(),
                ]
            )
        else:
            processors.extend(
                [
                    structlog.dev.set_exc_info,
                    (
                        structlog.dev.ConsoleRenderer(colors=enable_colors)
                        if enable_colors
                        else structlog.processors.JSONRenderer()
                    ),
                ]
            )

        structlog.configure(
            processors=processors,
            wrapper_class=structlog.stdlib.BoundLogger,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

    # Configure standard logging
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(level=log_level, handlers=handlers)

    # Apply structured formatter to standard logging if requested
    if format_type == "structured":
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(DEFAULT_FORMAT)

    for h in logging.getLogger().handlers:
        try:
            h.setFormatter(formatter)
        except Exception:
            pass

    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("azure").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)

    if STRUCTLOG_AVAILABLE and enable_structlog:
        return structlog.get_logger()
    else:  # Return stdlib logger
        return logging.getLogger("reasoning-kernel")


def get_logger(name: str):
    """Get a structured logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Structured logger instance
    """
    # Ensure structlog is configured if not already
    if not logging.getLogger().handlers:
        configure_logging(level="INFO", json_logs=False, enable_colors=True)

    try:
        if STRUCTLOG_AVAILABLE:
            return structlog.get_logger(name)
        # Fallback to stdlib logger
        return logging.getLogger(name)
    except Exception:
        configure_logging(level="INFO", json_logs=False, enable_colors=True)
        return logging.getLogger(name)


# Backward-compatibility alias used throughout the codebase/tests
def get_structured_logger(name: str):
    """Alias for get_logger to maintain compatibility with older imports."""
    return get_logger(name)


class StructuredFormatter(logging.Formatter):
    """Simple JSON formatter for standard logging records."""

    def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        import json

        payload: Dict[str, Any] = {
            "level": getattr(record, "levelname", "INFO"),
            "logger": getattr(record, "name", "root"),
            "message": record.getMessage()
            if hasattr(record, "getMessage")
            else str(getattr(record, "msg", "")),
            "timestamp": getattr(record, "created", time.time()),
        }
        ctx = getattr(record, "context", None)
        if isinstance(ctx, dict):
            payload["context"] = ctx
        if record.exc_info:
            try:
                import traceback

                payload["exception"] = "".join(
                    traceback.format_exception(*record.exc_info)
                )
            except Exception:
                payload["exception"] = "exception"
        try:
            return json.dumps(payload)
        except Exception:
            return str(payload)


# Re-export get_error_context so tests can patch it on this module
try:
    from reasoning_kernel.core.exceptions import get_error_context as get_error_context  # type: ignore
except Exception:  # pragma: no cover

    def get_error_context(e: Exception) -> Dict[str, Any]:  # type: ignore
        return {"error_type": type(e).__name__, "error_message": str(e)}


def safe_log(logger, level: str, message: str, **kwargs):
    """Safely log a message with fallback to basic logging if structured logging fails."""
    try:
        if level == "info":
            logger.info(message, **kwargs)
        elif level == "error":
            logger.error(message, **kwargs)
        elif level == "warning":
            logger.warning(message, **kwargs)
        elif level == "debug":
            logger.debug(message, **kwargs)
        else:
            logger.info(message, **kwargs)
    except Exception:
        # Fallback to basic logging
        fallback_message = f"{message}"
        if kwargs:
            fallback_message += f" - {kwargs}"
        if level == "info":
            logger.info(fallback_message)
        elif level == "error":
            logger.error(fallback_message)
        elif level == "warning":
            logger.warning(fallback_message)
        elif level == "debug":
            logger.debug(fallback_message)
        else:
            logger.info(fallback_message)


@contextmanager
def performance_context(operation: str, logger: Optional[Any] = None):
    """Context manager for performance logging with duration tracking."""
    if logger is None:
        logger = get_logger("performance")

    start_time = time.time()
    safe_log(
        logger, "info", "Operation started", operation=operation, start_time=start_time
    )

    try:
        yield logger
        duration = time.time() - start_time
        safe_log(
            logger,
            "info",
            "Operation completed",
            operation=operation,
            duration=duration,
            status="success",
        )
    except Exception as e:
        duration = time.time() - start_time
        safe_log(
            logger,
            "error",
            "Operation failed",
            operation=operation,
            duration=duration,
            status="error",
            error=str(e),
        )
        raise


@contextmanager
def error_context(logger: Any, operation: str, **context):
    """Enhanced error context manager for detailed error logging."""
    import traceback

    try:
        from reasoning_kernel.core.tracing import get_correlation_id
    except ImportError:

        def get_correlation_id():
            return None

    try:
        yield logger
    except Exception as e:
        # Capture detailed error information
        error_info = {
            "operation": operation,
            "error_type": type(e).__name__,
            "error_message": str(e),
            "correlation_id": get_correlation_id(),
            "traceback": traceback.format_exc(),
            **context,
        }

        # Add system context
        import sys

        error_info.update(
            {
                "python_version": sys.version,
                "request_context": get_request_context(),
            }
        )

        # Log with enhanced context
        logger.error("Error in error_context", **error_info)
        raise


def log_stage_error(
    logger,
    stage_name: str,
    error: Exception,
    context: Dict[str, Any],
    **additional_context,
) -> Dict[str, Any]:
    """Enhanced error logging for MSA pipeline stages."""
    import traceback

    try:
        from reasoning_kernel.core.tracing import get_correlation_id
    except ImportError:

        def get_correlation_id():
            return None

    error_details = {
        "stage": stage_name,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "correlation_id": get_correlation_id(),
        "session_id": context.get("session_id"),
        "scenario_preview": context.get("scenario", "")[:100]
        if context.get("scenario")
        else "",
        "stage_context": context,
        "traceback": traceback.format_exc(),
        **additional_context,
    }

    logger.error("Stage error occurred", **error_details)
    return error_details


def create_error_breadcrumbs() -> List[Dict[str, Any]]:
    """Create error breadcrumbs for debugging context."""
    import inspect

    breadcrumbs = []

    # Get current stack frames
    current_frame = inspect.currentframe()
    try:
        frames = inspect.getouterframes(current_frame)
        for frame_info in frames[:10]:  # Limit to 10 frames
            breadcrumb = {
                "filename": frame_info.filename.split("/")[-1],  # Just filename
                "function": frame_info.function,
                "line_number": frame_info.lineno,
                "code_context": frame_info.code_context[0].strip()
                if frame_info.code_context
                else None,
            }
            breadcrumbs.append(breadcrumb)
    finally:
        del current_frame  # Prevent reference cycles

    return breadcrumbs


def log_with_breadcrumbs(logger, level: str, message: str, **kwargs):
    """Log with error breadcrumbs for enhanced debugging context."""
    try:
        from reasoning_kernel.core.tracing import get_correlation_id
    except ImportError:

        def get_correlation_id():
            return None

    enhanced_context = {
        "correlation_id": get_correlation_id(),
        "breadcrumbs": create_error_breadcrumbs(),
        **kwargs,
    }

    log_func = getattr(logger, level.lower(), logger.info)
    log_func(message, **enhanced_context)


class MSAStageLogger:
    """Specialized logger for MSA pipeline stages with enhanced context."""

    def __init__(self, stage_name: str):
        self.stage_name = stage_name
        self.logger = get_logger(f"msa.stage.{stage_name}")
        self._stage_context: Dict[str, Any] = {}

    def set_stage_context(self, **context):
        """Set stage-specific context."""
        self._stage_context.update(context)

    def log_stage_start(self, **context):
        """Log stage start with context."""
        log_context = {
            "stage": self.stage_name,
            "correlation_id": None,  # Simplified - no tracing
            "stage_event": "stage_start",
            **self._stage_context,
            **context,
        }
        self.logger.info("MSA stage started", **log_context)

    def log_stage_complete(self, duration: float, **context):
        """Log stage completion with performance metrics."""
        log_context = {
            "stage": self.stage_name,
            "correlation_id": None,  # Simplified - no tracing
            "stage_event": "stage_complete",
            "duration": duration,
            **self._stage_context,
            **context,
        }
        self.logger.info("MSA stage completed", **log_context)

    def log_stage_error(self, error: Exception, **context):
        """Log stage error with enhanced context."""
        return log_stage_error(
            self.logger, self.stage_name, error, {**self._stage_context, **context}
        )

    def debug(self, message: str, **kwargs):
        """Debug logging with stage context."""
        self.logger.debug(
            message, stage=self.stage_name, **self._stage_context, **kwargs
        )

    def info(self, message: str, **kwargs):
        """Info logging with stage context."""
        self.logger.info(
            message, stage=self.stage_name, **self._stage_context, **kwargs
        )

    def warning(self, message: str, **kwargs):
        """Warning logging with stage context."""
        self.logger.warning(
            message, stage=self.stage_name, **self._stage_context, **kwargs
        )

    def error(self, message: str, **kwargs):
        """Error logging with stage context."""
        self.logger.error(
            message,
            stage=self.stage_name,
            **self._stage_context,
            **kwargs,
        )


# === Enhanced Error Logging ===


def log_domain_error(
    logger: Any, error: Exception, operation: str, **context: Any
) -> None:
    """
    Log domain-specific errors with standardized context.

    Args:
        logger: Structured logger instance
        error: Exception to log
        operation: Operation that failed
        **context: Additional context
    """
    from reasoning_kernel.core.exceptions import ReasoningEngineError

    # Use module-level get_error_context so tests can patch it

    error_context = get_error_context(error)
    error_context.update(context)

    if isinstance(error, ReasoningEngineError):
        logger.bind(**error_context).error(
            f"Domain error in {operation}",
            operation=operation,
            error_code=error.error_code,
            domain_error=True,
        )
    else:
        logger.bind(**error_context).error(
            f"External error in {operation}", operation=operation, domain_error=False
        )


def log_service_call(
    logger: Any,
    service: str,
    operation: str,
    success: bool,
    duration_ms: Optional[float] = None,
    **context: Any,
) -> None:
    """Log external service calls with standardized format."""
    log_context = {
        "service": service,
        "operation": operation,
        "success": success,
        "external_call": True,
        **context,
    }

    if duration_ms is not None:
        log_context["duration_ms"] = duration_ms

    level = "info" if success else "warning"
    status = "succeeded" if success else "failed"

    getattr(logger.bind(**log_context), level)(
        f"Service call {status}", service_call=f"{service}.{operation}"
    )


def log_pipeline_step(
    logger: Any,
    step: str,
    status: str,
    duration_ms: Optional[float] = None,
    **context: Any,
) -> None:
    """Log MSA pipeline step execution."""
    log_context = {
        "pipeline_step": step,
        "step_status": status,
        "msa_pipeline": True,
        **context,
    }

    if duration_ms is not None:
        log_context["duration_ms"] = duration_ms

    level = "info" if status == "completed" else "error"

    getattr(logger.bind(**log_context), level)(f"Pipeline step {status}", step=step)
