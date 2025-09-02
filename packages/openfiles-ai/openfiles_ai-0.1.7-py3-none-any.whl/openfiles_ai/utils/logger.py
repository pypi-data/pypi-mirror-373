"""
Logging utilities for OpenFiles SDK
"""

import logging
from typing import Optional


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance for the given name

    Args:
        name: Logger name (typically __name__)
        level: Optional log level override

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Set level if provided
    if level:
        logger.setLevel(getattr(logging, level.upper()))
    elif not logger.handlers:
        # Default to INFO if no handlers are set
        logger.setLevel(logging.INFO)

    # Add console handler if none exists
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
