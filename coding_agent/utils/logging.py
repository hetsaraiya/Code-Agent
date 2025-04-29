"""
Logging module for the Coding Agent.
This module provides a centralized logging configuration using Loguru.
"""

import os
import sys
from datetime import datetime
from loguru import logger

def setup_logger():
    """
    Configure and set up the logger with appropriate settings.
    
    This function configures console and file logging with custom formatting.
    Console logs show INFO and above, while file logs are separated by log level:
    - debug.log: All DEBUG and above logs
    - info.log: All INFO and above logs
    - error.log: All ERROR and above logs
    
    Returns:
        logger: The configured logger instance
    """
    # Base log directory
    base_log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs')
    
    # Create date folder
    today = datetime.now().strftime('%Y-%m-%d')
    log_dir = os.path.join(base_log_dir, today)
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
        colorize=True
    )

    # Configure file logging for different levels
    # Debug file (DEBUG and above)
    logger.add(
        os.path.join(log_dir, "debug.log"),
        level="DEBUG",
        format=log_format,
        enqueue=True,
        backtrace=True,
        diagnose=True
    )
    
    # Info file (INFO and above)
    logger.add(
        os.path.join(log_dir, "info.log"),
        level="INFO",
        format=log_format,
        enqueue=True,
        backtrace=True,
        diagnose=True
    )
    
    # Error file (ERROR and above)
    logger.add(
        os.path.join(log_dir, "error.log"),
        level="ERROR",
        format=log_format,
        enqueue=True,
        backtrace=True,
        diagnose=True
    )

    return logger

# Create a global logger instance that can be imported throughout the application
logger = setup_logger()
