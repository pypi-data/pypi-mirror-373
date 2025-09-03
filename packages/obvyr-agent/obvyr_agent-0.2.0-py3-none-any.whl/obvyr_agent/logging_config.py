"""
Centralised logging configuration for the Obvyr agent.

This module provides consistent logging setup that respects the customer-facing
nature of the agent - silent by default, but verbose when debugging is needed.
"""

import logging
import os
import sys
from typing import Optional

# Customer-facing default: WARNING level (minimal noise)
DEFAULT_LOG_LEVEL = logging.WARNING

# Format for customer-facing logs (simple, clean)
CUSTOMER_FORMAT = "%(message)s"

# Format for debug logs (detailed technical information)
DEBUG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

_configured = False


def configure_logging(
    level: Optional[int] = None,
    verbose: bool = False,
    quiet: bool = False,
) -> None:
    """
    Configure logging for the Obvyr agent.

    Args:
        level: Explicit log level (overrides environment and flags)
        verbose: Enable debug-level logging with technical details
        quiet: Enable only error-level logging
    """
    global _configured

    # Determine log level priority:
    # 1. Explicit level parameter
    # 2. verbose/quiet flags
    # 3. OBVYR_LOG_LEVEL environment variable
    # 4. Default (WARNING for customer-facing)

    if level is not None:
        log_level = level
    elif verbose:
        log_level = logging.DEBUG
    elif quiet:
        log_level = logging.ERROR
    else:
        # Check environment variable
        env_level = os.getenv("OBVYR_LOG_LEVEL", "").upper()
        log_level = _parse_log_level(env_level, DEFAULT_LOG_LEVEL)

    # Get the root logger for obvyr_agent
    logger = logging.getLogger("obvyr_agent")
    logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicates
    if _configured:
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

    # Create console handler
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(log_level)

    # Use appropriate format based on log level
    if log_level <= logging.DEBUG:
        # Debug mode: include technical details
        formatter = logging.Formatter(DEBUG_FORMAT)
    else:
        # Customer mode: simple, clean messages
        formatter = logging.Formatter(CUSTOMER_FORMAT)

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Prevent propagation to root logger (avoid duplicate logs)
    logger.propagate = False

    _configured = True


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module.

    Args:
        name: Module name (will be prefixed with 'obvyr_agent.')

    Returns:
        Configured logger instance
    """
    # Ensure logging is configured
    if not _configured:
        configure_logging()

    # Return logger with obvyr_agent prefix
    return logging.getLogger(f"obvyr_agent.{name}")


def set_log_level(level: int) -> None:
    """
    Change log level at runtime.

    Args:
        level: New logging level
    """
    logger = logging.getLogger("obvyr_agent")
    logger.setLevel(level)

    # Update handler levels as well
    for handler in logger.handlers:
        handler.setLevel(level)

        # Update formatter if switching to/from debug
        if level <= logging.DEBUG:
            formatter = logging.Formatter(DEBUG_FORMAT)
        else:
            formatter = logging.Formatter(CUSTOMER_FORMAT)
        handler.setFormatter(formatter)


def _parse_log_level(level_str: str, default: int) -> int:
    """
    Parse log level string to logging constant.

    Args:
        level_str: String representation of log level
        default: Default level if parsing fails

    Returns:
        Logging level constant
    """
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "WARN": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    return level_map.get(level_str, default)
