"""
Logging configuration for the txttoqti package.

Provides centralized logging configuration with different levels
and formatters for development and production use.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    format_type: str = "standard"
) -> logging.Logger:
    """
    Set up logging configuration for the txttoqti package.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        format_type: Format type ('standard', 'detailed', 'simple')
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("txttoqti")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers to avoid duplication
    logger.handlers.clear()
    
    # Define formatters
    formatters = {
        "simple": logging.Formatter("%(levelname)s: %(message)s"),
        "standard": logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        ),
        "detailed": logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
        )
    }
    
    formatter = formatters.get(format_type, formatters["standard"])
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatters["detailed"])
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f"txttoqti.{name}")