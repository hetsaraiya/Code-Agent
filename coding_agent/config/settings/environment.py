"""Environment configuration for the Coding Agent."""

import os
from enum import Enum
from functools import lru_cache


class Environment(str, Enum):
    """Environments that the application can run in."""
    DEVELOPMENT = "development"
    STAGING = "staging"  
    PRODUCTION = "production"
    LOCAL = "local"


@lru_cache
def get_environment() -> Environment:
    """
    Determine the current environment based on the ENV environment variable.
    
    Returns:
        Environment: The current environment enum value.
    """
    env = os.getenv("ENV", "development").lower()
    
    if env == "production" or env == "prod":
        return Environment.PRODUCTION
    elif env == "staging" or env == "stage":
        return Environment.STAGING
    elif env == "local":
        return Environment.LOCAL
    else:  # Default to development
        return Environment.DEVELOPMENT
