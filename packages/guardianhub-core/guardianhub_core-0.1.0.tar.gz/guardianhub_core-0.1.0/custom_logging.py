# guardianhub-core/custom_logging.py
"""
A standardized logging configuration to ensure all services use
the same format and level.
"""

import logging
import sys
from typing import Optional

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.

    Args:
        name: The name of the logger (usually __name__)

    Returns:
        A configured logger instance
    """
    return logging.getLogger(name)

def setup_logging(service_name: str, level=logging.INFO):
    """
    Configures a standardized logging setup.

    Args:
        service_name: The name of the service for log identification.
        level: The minimum log level to capture.
    """
    log_format = (
        f"%(asctime)s | {service_name} | %(levelname)s | "
        "%(name)s | %(funcName)s | %(lineno)d | %(message)s"
    )

    logging.basicConfig(
        stream=sys.stdout,
        level=level,
        format=log_format,
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    logging.info(f"Logging for '{service_name}' configured at level {logging.getLevelName(level)}")