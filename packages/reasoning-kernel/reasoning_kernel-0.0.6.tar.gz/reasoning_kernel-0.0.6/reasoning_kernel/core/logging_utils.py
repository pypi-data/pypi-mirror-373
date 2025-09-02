"""
Logging Utilities
================

Utility functions for logging across the reasoning kernel.
"""

import logging
from typing import Optional


def simple_log_error(
    message: str,
    error: Optional[Exception] = None,
    logger_name: str = "reasoning_kernel",
    **kwargs,
) -> None:
    """Simple error logging utility with support for additional context"""
    logger = logging.getLogger(logger_name)

    if error:
        if kwargs:
            # Include additional context in the log message
            context_str = ", ".join(f"{k}={v}" for k, v in kwargs.items())
            logger.error(f"{message}: {error} [{context_str}]")
        else:
            logger.error(f"{message}: {error}")
    else:
        if kwargs:
            context_str = ", ".join(f"{k}={v}" for k, v in kwargs.items())
            logger.error(f"{message} [{context_str}]")
        else:
            logger.error(message)


def simple_log_info(message: str, logger_name: str = "reasoning_kernel") -> None:
    """Simple info logging utility"""
    logger = logging.getLogger(logger_name)
    logger.info(message)


def simple_log_warning(message: str, logger_name: str = "reasoning_kernel") -> None:
    """Simple warning logging utility"""
    logger = logging.getLogger(logger_name)
    logger.warning(message)


def simple_log_debug(message: str, logger_name: str = "reasoning_kernel") -> None:
    """Simple debug logging utility"""
    logger = logging.getLogger(logger_name)
    logger.debug(message)
