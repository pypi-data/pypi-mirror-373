"""
Error Handling Utilities
=======================

Centralized error handling utilities for the reasoning kernel.
"""

import logging
import traceback
from typing import Any, Optional, Dict
from functools import wraps


def simple_log_error(message: str, error: Optional[Exception] = None, logger_name: str = "reasoning_kernel") -> None:
    """Simple error logging utility"""
    logger = logging.getLogger(logger_name)
    
    if error:
        logger.error(f"{message}: {error}")
        logger.debug(f"Error traceback: {traceback.format_exc()}")
    else:
        logger.error(message)


def simple_log_warning(message: str, logger_name: str = "reasoning_kernel") -> None:
    """Simple warning logging utility"""
    logger = logging.getLogger(logger_name)
    logger.warning(message)


def simple_log_info(message: str, logger_name: str = "reasoning_kernel") -> None:
    """Simple info logging utility"""
    logger = logging.getLogger(logger_name)
    logger.info(message)


def handle_exception(func):
    """Decorator for handling exceptions in functions"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            simple_log_error(f"Exception in {func.__name__}", e)
            raise
    return wrapper


def handle_async_exception(func):
    """Decorator for handling exceptions in async functions"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            simple_log_error(f"Exception in {func.__name__}", e)
            raise
    return wrapper


class ErrorContext:
    """Context manager for error handling"""
    
    def __init__(self, operation_name: str, logger_name: str = "reasoning_kernel"):
        self.operation_name = operation_name
        self.logger_name = logger_name
        self.logger = logging.getLogger(logger_name)
    
    def __enter__(self):
        self.logger.debug(f"Starting operation: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            simple_log_error(f"Error in operation {self.operation_name}", exc_val, self.logger_name)
        else:
            self.logger.debug(f"Completed operation: {self.operation_name}")
        return False  # Don't suppress exceptions


def create_error_response(error: Exception, operation: str = "unknown") -> Dict[str, Any]:
    """Create standardized error response"""
    return {
        "success": False,
        "error": {
            "type": type(error).__name__,
            "message": str(error),
            "operation": operation
        }
    }
