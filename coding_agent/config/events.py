"""
Application event handlers for startup and shutdown events.
These functions run during application lifecycle events.
"""

from typing import Callable
import logging

from coding_agent.config.settings import get_app_settings
from coding_agent.utils.logging import logger

def create_start_app_handler() -> Callable:
    """
    Create a callable that will run when the application starts.
    
    Returns:
        Callable: A function that will be called on application startup.
    """
    async def start_app() -> None:
        """Initialize services, connections, and resources on app startup."""
        settings = get_app_settings()
        logger.info(f"Starting application in {settings.PROJECT_NAME} mode")
        # Initialize connections, services, etc. here
    
    return start_app


def create_stop_app_handler() -> Callable:
    """
    Create a callable that will run when the application stops.
    
    Returns:
        Callable: A function that will be called on application shutdown.
    """
    async def stop_app() -> None:
        """Close connections and free resources on app shutdown."""
        settings = get_app_settings()
        logger.info(f"Shutting down {settings.PROJECT_NAME}")
        # Close connections, cleanup resources, etc. here
    
    return stop_app
