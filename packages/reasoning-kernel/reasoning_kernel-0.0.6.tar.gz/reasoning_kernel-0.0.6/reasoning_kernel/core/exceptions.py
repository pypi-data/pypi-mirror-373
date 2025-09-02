"""
Central Exception Hierarchy for MSA Reasoning Kernel

This module provides a comprehensive, structured exception hierarchy for the MSA Reasoning Kernel,
replacing scattered custom exceptions with a centralized, consistent error handling system.

Features:
- Hierarchical exception structure for better error categorization
- Error context tracking with correlation IDs
- User-friendly error messages with developer details
- Integration with logging and monitoring systems
- Support for error recovery and graceful degradation
"""

import uuid
import time
from typing import Any, Dict, List, Optional, Union
from enum import Enum
import logging
from dataclasses import dataclass, field

from reasoning_kernel.core.error_handling import simple_log_error

# Import error codes from constants
from reasoning_kernel.core.constants import (
    ERROR_VALIDATION_FAILED,
    ERROR_AUTHENTICATION_FAILED,
    ERROR_AUTHORIZATION_FAILED,
    ERROR_RATE_LIMITED,
    ERROR_INTERNAL_SERVER,
    ERROR_SERVICE_UNAVAILABLE,
    ERROR_TIMEOUT,
    ERROR_INVALID_REQUEST,
    HTTP_BAD_REQUEST,
    HTTP_UNAUTHORIZED,
    HTTP_FORBIDDEN,
    HTTP_TOO_MANY_REQUESTS,
    HTTP_INTERNAL_SERVER_ERROR,
    HTTP_SERVICE_UNAVAILABLE,
)

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels for categorizing exceptions."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for classification and handling."""

    VALIDATION = "validation"
    SECURITY = "security"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    NETWORK = "network"
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    API = "api"
    MSA_PIPELINE = "msa_pipeline"
    DATABASE = "database"
    CACHE = "cache"
    CONFIGURATION = "configuration"
    SERVICE = "service"
    INTERNAL = "internal"


@dataclass
class ErrorContext:
    """Context information for errors including tracking and debugging details."""

    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    operation: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    component: Optional[str] = None
    additional_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert error context to dictionary for logging and serialization."""
        return {
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp,
            "operation": self.operation,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "request_id": self.request_id,
            "component": self.component,
            "additional_data": self.additional_data,
        }


class MSAError(Exception):
    """
    Base exception class for all MSA Reasoning Kernel errors.

    Provides structured error information including:
    - Error codes and categories
    - User-friendly and developer messages
    - Context tracking with correlation IDs
    - Severity levels for error handling
    - HTTP status code mapping for API responses
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        error_category: ErrorCategory = ErrorCategory.INTERNAL,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        user_message: Optional[str] = None,
        http_status: int = HTTP_INTERNAL_SERVER_ERROR,
        context: Optional[ErrorContext] = None,
        cause: Optional[Exception] = None,
        recoverable: bool = False,
        retry_after: Optional[int] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or ERROR_INTERNAL_SERVER
        self.error_category = error_category
        self.severity = severity
        self.user_message = user_message or "An error occurred. Please try again later."
        self.http_status = http_status
        self.context = context or ErrorContext()
        self.cause = cause
        self.recoverable = recoverable
        self.retry_after = retry_after

        # Log error creation for monitoring
        self._log_error()

    def _log_error(self):
        """Log error creation with structured data."""
        log_data = {
            "error_class": self.__class__.__name__,
            "error_code": self.error_code,
            "error_category": self.error_category.value,
            "severity": self.severity.value,
            "message": self.message,
            "user_message": self.user_message,
            "http_status": self.http_status,
            "recoverable": self.recoverable,
            "context": self.context.to_dict(),
        }

        if self.cause:
            log_data["cause"] = str(self.cause)

        simple_log_error(logger, "msa_error", Exception(self.message), **log_data)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses and logging."""
        return {
            "error": {
                "code": self.error_code,
                "category": self.error_category.value,
                "severity": self.severity.value,
                "message": self.user_message,
                "developer_message": self.message,
                "correlation_id": self.context.correlation_id,
                "timestamp": self.context.timestamp,
                "recoverable": self.recoverable,
                "retry_after": self.retry_after,
            }
        }

    def __str__(self) -> str:
        return f"[{self.error_code}] {self.message} (correlation_id: {self.context.correlation_id})"


# Back-compat alias referenced by logging_config
ReasoningEngineError = MSAError


def get_error_context(error: Exception) -> Dict[str, Any]:
    """Extract minimal error context for logging tests."""
    return {"error_type": type(error).__name__, "error_message": str(error)}


# Validation Errors
class ValidationError(MSAError):
    """Raised when input validation fails."""

    def __init__(self, message: str, field_errors: Optional[Dict[str, List[str]]] = None, **kwargs):
        super().__init__(
            message,
            error_code=kwargs.get("error_code", ERROR_VALIDATION_FAILED),
            error_category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.LOW,
            http_status=kwargs.get("http_status", HTTP_BAD_REQUEST),
            user_message=kwargs.get("user_message", "Please check your input and try again."),
            **{k: v for k, v in kwargs.items() if k not in ["error_code", "http_status", "user_message"]},
        )
        self.field_errors = field_errors or {}


class SecurityError(MSAError):
    """Raised when security violations occur."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            error_code=kwargs.get("error_code", ERROR_AUTHORIZATION_FAILED),
            error_category=ErrorCategory.SECURITY,
            severity=ErrorSeverity.HIGH,
            http_status=kwargs.get("http_status", HTTP_FORBIDDEN),
            user_message=kwargs.get("user_message", "Access denied. Please check your permissions."),
            **{k: v for k, v in kwargs.items() if k not in ["error_code", "http_status", "user_message"]},
        )


class AuthenticationError(MSAError):
    """Raised when authentication fails."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            error_code=kwargs.get("error_code", ERROR_AUTHENTICATION_FAILED),
            error_category=ErrorCategory.AUTHENTICATION,
            severity=ErrorSeverity.HIGH,
            http_status=kwargs.get("http_status", HTTP_UNAUTHORIZED),
            user_message=kwargs.get("user_message", "Authentication failed. Please log in again."),
            **{k: v for k, v in kwargs.items() if k not in ["error_code", "http_status", "user_message"]},
        )


class AuthorizationError(MSAError):
    """Raised when authorization fails."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            error_code=kwargs.get("error_code", ERROR_AUTHORIZATION_FAILED),
            error_category=ErrorCategory.AUTHORIZATION,
            severity=ErrorSeverity.HIGH,
            http_status=kwargs.get("http_status", HTTP_FORBIDDEN),
            user_message=kwargs.get("user_message", "You don't have permission to access this resource."),
            **{k: v for k, v in kwargs.items() if k not in ["error_code", "http_status", "user_message"]},
        )


class TimeoutError(MSAError):
    """Raised when operations timeout."""

    def __init__(self, message: str, timeout_duration: Optional[float] = None, **kwargs):
        super().__init__(
            message,
            error_code=kwargs.get("error_code", ERROR_TIMEOUT),
            error_category=ErrorCategory.TIMEOUT,
            severity=ErrorSeverity.MEDIUM,
            http_status=kwargs.get("http_status", HTTP_INTERNAL_SERVER_ERROR),
            user_message=kwargs.get("user_message", "The operation took too long. Please try again."),
            recoverable=True,
            **{k: v for k, v in kwargs.items() if k not in ["error_code", "http_status", "user_message"]},
        )
        self.timeout_duration = timeout_duration


class RateLimitError(MSAError):
    """Raised when rate limits are exceeded."""

    def __init__(self, message: str, retry_after: Optional[int] = None, **kwargs):
        super().__init__(
            message,
            error_code=kwargs.get("error_code", ERROR_RATE_LIMITED),
            error_category=ErrorCategory.RATE_LIMIT,
            severity=ErrorSeverity.MEDIUM,
            http_status=kwargs.get("http_status", HTTP_TOO_MANY_REQUESTS),
            user_message=kwargs.get("user_message", "Rate limit exceeded. Please try again later."),
            recoverable=True,
            retry_after=retry_after,
            **{k: v for k, v in kwargs.items() if k not in ["error_code", "http_status", "user_message"]},
        )


class APIError(MSAError):
    """Raised when API operations fail."""

    def __init__(self, message: str, api_endpoint: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            error_code=kwargs.get("error_code", ERROR_INVALID_REQUEST),
            error_category=ErrorCategory.API,
            severity=ErrorSeverity.MEDIUM,
            http_status=kwargs.get("http_status", HTTP_BAD_REQUEST),
            user_message=kwargs.get("user_message", "API request failed. Please check your request."),
            **{k: v for k, v in kwargs.items() if k not in ["error_code", "http_status", "user_message"]},
        )
        self.api_endpoint = api_endpoint


class MSAPipelineError(MSAError):
    """Raised when MSA pipeline operations fail."""

    def __init__(
        self, message: str, stage: Optional[str] = None, stage_data: Optional[Dict[str, Any]] = None, **kwargs
    ):
        super().__init__(
            message,
            error_category=ErrorCategory.MSA_PIPELINE,
            severity=ErrorSeverity.HIGH,
            user_message=kwargs.get("user_message", "Reasoning pipeline error. Please try again."),
            recoverable=True,
            **kwargs,
        )
        self.stage = stage
        self.stage_data = stage_data or {}


class PipelineExecutionError(MSAPipelineError):
    """Specific error for failures during pipeline stage execution."""

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        stage = None
        stage_data = None
        if isinstance(context, dict):
            stage = context.get("stage")
            stage_data = context
        super().__init__(message, stage=stage, stage_data=stage_data, **kwargs)


class DatabaseError(MSAError):
    """Raised when database operations fail."""

    def __init__(self, message: str, query: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            error_category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.HIGH,
            http_status=kwargs.get("http_status", HTTP_INTERNAL_SERVER_ERROR),
            user_message=kwargs.get("user_message", "Database error occurred. Please try again."),
            recoverable=True,
            **{k: v for k, v in kwargs.items() if k not in ["http_status", "user_message"]},
        )
        self.query = query


class CacheError(MSAError):
    """Raised when cache operations fail."""

    def __init__(self, message: str, cache_key: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            error_category=ErrorCategory.CACHE,
            severity=ErrorSeverity.LOW,
            user_message=kwargs.get("user_message", "Cache error occurred. Operation will continue without cache."),
            recoverable=True,
            **kwargs,
        )
        self.cache_key = cache_key


class ConfigurationError(MSAError):
    """Raised when configuration errors occur."""

    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            error_category=ErrorCategory.CONFIGURATION,
            severity=ErrorSeverity.HIGH,
            user_message=kwargs.get("user_message", "Configuration error. Please contact support."),
            recoverable=False,
            **kwargs,
        )
        self.config_key = config_key


class ServiceError(MSAError):
    """Raised when external service operations fail."""

    def __init__(
        self, message: str, service_name: Optional[str] = None, service_endpoint: Optional[str] = None, **kwargs
    ):
        super().__init__(
            message,
            error_code=kwargs.get("error_code", ERROR_SERVICE_UNAVAILABLE),
            error_category=ErrorCategory.SERVICE,
            severity=ErrorSeverity.MEDIUM,
            http_status=kwargs.get("http_status", HTTP_SERVICE_UNAVAILABLE),
            user_message=kwargs.get("user_message", "External service unavailable. Please try again later."),
            recoverable=True,
            **{k: v for k, v in kwargs.items() if k not in ["error_code", "http_status", "user_message"]},
        )
        self.service_name = service_name
        self.service_endpoint = service_endpoint


# Legacy exception compatibility aliases for migration
DaytonaServiceError = ServiceError
StageExecutionError = MSAPipelineError
StageValidationError = ValidationError
CircuitBreakerError = ServiceError
GracefulDegradationError = ServiceError


# Domain-specific error types used by tests and legacy code
class UnderstandingError(MSAPipelineError):
    pass


class SearchError(MSAPipelineError):
    pass


class SynthesisError(MSAPipelineError):
    pass


class DaytonaExecutionError(ServiceError):
    pass


# Error handling utilities
class ErrorHandler:
    """Utility class for standardized error handling patterns."""

    @staticmethod
    def create_context(
        operation: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        request_id: Optional[str] = None,
        component: Optional[str] = None,
        **additional_data,
    ) -> ErrorContext:
        """Create an error context with provided information."""
        return ErrorContext(
            operation=operation,
            user_id=user_id,
            session_id=session_id,
            request_id=request_id,
            component=component,
            additional_data=additional_data,
        )

    @staticmethod
    def handle_validation_error(
        errors: Union[str, Dict[str, List[str]]], context: Optional[ErrorContext] = None
    ) -> ValidationError:
        """Create a standardized validation error."""
        if isinstance(errors, str):
            message = errors
            field_errors = {}
        else:
            message = "Validation failed"
            field_errors = errors

        return ValidationError(message=message, field_errors=field_errors, context=context)

    @staticmethod
    def handle_timeout(operation: str, timeout_duration: float, context: Optional[ErrorContext] = None) -> TimeoutError:
        """Create a standardized timeout error."""
        return TimeoutError(
            message=f"Operation '{operation}' timed out after {timeout_duration}s",
            timeout_duration=timeout_duration,
            context=context,
        )

    @staticmethod
    def handle_service_error(
        service_name: str, operation: str, cause: Optional[Exception] = None, context: Optional[ErrorContext] = None
    ) -> ServiceError:
        """Create a standardized service error."""
        return ServiceError(
            message=f"Service '{service_name}' failed during '{operation}'",
            service_name=service_name,
            cause=cause,
            context=context,
        )

    @staticmethod
    def wrap_exception(
        exception: Exception, context: Optional[ErrorContext] = None, message_override: Optional[str] = None
    ) -> MSAError:
        """Wrap a generic exception in an MSAError."""
        message = message_override or str(exception)

        # Try to map common exception types
        if isinstance(exception, ValueError):
            return ValidationError(message=message, cause=exception, context=context)
        elif isinstance(exception, KeyError):
            return ConfigurationError(message=message, cause=exception, context=context)
        elif isinstance(exception, TimeoutError):
            return TimeoutError(message=message, cause=exception, context=context)
        else:
            return MSAError(message=message, cause=exception, context=context)


def wrap_external_error(exception: Exception, context: Optional[Dict[str, Any]] = None) -> ServiceError:
    """Helper to wrap arbitrary external exceptions into ServiceError with context."""
    return ServiceError(message=str(exception), context=ErrorHandler.create_context(**(context or {})))


# Exception handling decorators
def handle_exceptions(
    _: type = MSAError,
    context_component: Optional[str] = None,
    reraise: bool = True,
):
    """
    Decorator for standardized exception handling.

    Args:
        _: Exception type to use for wrapping unknown exceptions (unused)
        context_component: Component name to add to error context
        reraise: Whether to reraise the wrapped exception
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            context = ErrorHandler.create_context(operation=func.__name__, component=context_component)

            try:
                return func(*args, **kwargs)
            except MSAError:
                # Re-raise MSA errors as-is
                raise
            except Exception as e:
                wrapped_error = ErrorHandler.wrap_exception(e, context)
                if reraise:
                    raise wrapped_error
                return wrapped_error

        return wrapper

    return decorator
