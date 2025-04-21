"""
Logging module for the Coding Agent.
This module provides a centralized logging configuration using Loguru.
"""

import os
import sys
from loguru import logger

def setup_logger():
    """
    Configure and set up the logger with appropriate settings.
    
    This function configures console and file logging with custom formatting.
    Console logs show INFO and above, while file logs capture DEBUG and above.
    
    Returns:
        logger: The configured logger instance
    """
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    logger.remove()  # Remove default handler

    # Define a more detailed format
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )

    # Configure console logging
    logger.add(
        sys.stdout,
        level="INFO",
        format=log_format,
        colorize=True  # Enable colorization for console
    )

    # Configure file logging
    logger.add(
        os.path.join(log_dir, "{time:YYYY-MM-DD}.log"),
        rotation="50 MB",  # Reduced rotation size for more frequent rotation if needed
        retention="10 days",  # Keep logs for 10 days
        level="DEBUG",
        format=log_format,
        enqueue=True,  # Make logging asynchronous for performance
        backtrace=True,  # Include traceback in logs
        diagnose=True  # Add exception diagnosis information
    )

    return logger

# Create a global logger instance that can be imported throughout the application
app_logger = setup_logger()
