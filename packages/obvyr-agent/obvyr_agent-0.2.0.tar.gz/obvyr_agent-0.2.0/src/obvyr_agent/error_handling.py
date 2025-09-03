"""
Centralised error handling for customer-facing messages.

This module provides consistent, user-friendly error messages and logging
for common failure scenarios in the Obvyr agent.
"""

import logging
from typing import Optional, Union

import httpx

logger = logging.getLogger(__name__)


class ObvyrError(Exception):
    """Base exception class for Obvyr agent errors."""

    def __init__(
        self, message: str, user_message: Optional[str] = None
    ) -> None:
        """Initialize with technical and user-friendly messages."""
        super().__init__(message)
        self.user_message = user_message or message


def handle_api_error(error: httpx.HTTPStatusError) -> Optional[dict]:
    """
    Handle API HTTP errors with customer-friendly messages.

    Args:
        error: HTTPStatusError from httpx

    Returns:
        None for client errors (4xx), re-raises server errors (5xx)

    Raises:
        HTTPStatusError: For 5xx server errors that should be retried
    """
    status_code = error.response.status_code

    # Handle client errors (4xx) with friendly messages
    if 400 <= status_code < 500:
        if status_code == 401:
            log_customer_friendly_error(
                f"Authentication failed: {error.response.text}",
                "Authentication failed. Please check your API token configuration.",
            )
        elif status_code == 403:
            log_customer_friendly_error(
                f"Permission denied: {error.response.text}",
                "Permission denied. Your API token may not have access to this project.",
            )
        elif status_code == 422:
            log_customer_friendly_error(
                f"Data validation failed: {error.response.text}",
                "Data validation failed. The command data may be malformed.",
            )
        else:
            log_customer_friendly_error(
                f"Client error {status_code}: {error.response.text}",
                f"Request failed with error {status_code}. Please check your configuration.",
            )
        return None

    # Re-raise server errors (5xx) for retry logic
    raise error


def handle_network_error(
    error: Union[httpx.RequestError, httpx.TimeoutException],
) -> None:
    """
    Handle network connection errors with customer-friendly messages.

    Args:
        error: Network-related error from httpx

    Raises:
        The original error after logging friendly message
    """
    error_message = str(error).lower()

    if isinstance(error, httpx.TimeoutException) or "timeout" in error_message:
        log_customer_friendly_error(
            f"Request timed out: {error}",
            "Request timed out. The API server may be slow or unreachable. "
            "Try again or increase the timeout setting.",
        )
    elif "ssl" in error_message or "certificate" in error_message:
        log_customer_friendly_error(
            f"SSL verification failed: {error}",
            "Connection failed due to SSL certificate issues. "
            "Check your SSL configuration or try with --verify-ssl=false.",
        )
    elif "connection" in error_message:
        log_customer_friendly_error(
            f"Connection failed: {error}",
            "Failed to connect to the API server. "
            "Check your network connection and API URL configuration.",
        )
    else:
        log_customer_friendly_error(
            f"Network error: {error}",
            "Network error occurred. Check your connection and try again.",
        )

    raise error


def handle_archive_error(error: OSError) -> None:
    """
    Handle archive creation errors with customer-friendly messages.

    Args:
        error: OSError from archive operations
    """
    error_message = str(error).lower()

    if (
        "permission denied" in error_message
        or "access is denied" in error_message
    ):
        log_customer_friendly_error(
            f"Permission denied creating archive: {error}",
            "Failed to create archive due to permission issues. "
            "Check file permissions in the temporary directory.",
        )
    elif "no space left" in error_message or "disk full" in error_message:
        log_customer_friendly_error(
            f"Disk space error: {error}",
            "Failed to create archive due to insufficient disk space. "
            "Free up space in the temporary directory.",
        )
    elif "file not found" in error_message:
        log_customer_friendly_error(
            f"File not found: {error}",
            "Failed to create archive because a required file was not found. "
            "This may be a temporary issue - try running the command again.",
        )
    else:
        log_customer_friendly_error(
            f"Archive creation failed: {error}",
            "Failed to create archive. This may be a temporary issue - try again.",
        )


def log_customer_friendly_error(
    technical_message: str, user_message: str, level: int = logging.ERROR
) -> None:
    """
    Log error with customer-friendly message and optional technical details.

    Args:
        technical_message: Technical error details for debugging
        user_message: User-friendly error message
        level: Logging level (default: ERROR)
    """
    # Always log the user-friendly message
    logger.log(level, user_message)

    # In debug mode, also log technical details
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(f"Technical details: {technical_message}")
