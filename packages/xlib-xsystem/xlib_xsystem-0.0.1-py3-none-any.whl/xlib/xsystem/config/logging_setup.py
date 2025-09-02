"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: August 31, 2025

Logging configuration setup for xSystem.

Provides centralized logging setup functions and logger factory.
This module handles the implementation details of logging configuration.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

from .defaults import LOGGING_ENABLED, LOGGING_LEVEL


def setup_logging(
    log_file="logs/xsystem.log",
    level=logging.INFO,
    max_bytes=10 * 1024 * 1024,
    backup_count=5,
    fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
):
    """
    Centralized logging setup for production use.
    - Console and rotating file handlers
    - Structured formatting
    - Easy integration for all entry points
    """
    # Check if logging is disabled via environment variable - do this FIRST
    if os.getenv("XSYSTEM_LOGGING_DISABLE", "false").lower() == "true":
        logging.disable(logging.CRITICAL)
        return

    # Also check if logging is already disabled
    if logging.getLogger().disabled:
        return

    # Try to check xSystem config if available
    try:
        from .logging import logging_config

        if not logging_config.enabled:
            logging.disable(logging.CRITICAL)
            return
    except ImportError:
        # xSystem config not available, continue with normal setup
        pass

    logger = logging.getLogger()
    logger.setLevel(level)
    formatter = logging.Formatter(fmt)

    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Rotating file handler
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    fh = RotatingFileHandler(
        log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
    )
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Reduce noise from common external libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.WARNING)

    logger.info("✅ Logging system initialized (console + file)")


def get_logger(name=None) -> logging.Logger:
    """
    Get a logger instance with the specified name.

    Args:
        name: Logger name (defaults to __name__ if not provided)

    Returns:
        logging.Logger: Configured logger instance
    """
    # Check if logging is disabled
    if os.getenv("XSYSTEM_LOGGING_DISABLE", "false").lower() == "true":
        # Return a disabled logger
        logger = logging.getLogger(name)
        logger.disabled = True
        return logger

    return logging.getLogger(name)
