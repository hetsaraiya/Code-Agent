"""Settings configuration for the Coding Agent."""

from functools import lru_cache

from coding_agent.config.settings.base import AppSettings
from coding_agent.config.settings.environment import Environment, get_environment

__all__ = ["AppSettings", "Environment", "get_app_settings"]


@lru_cache()
def get_app_settings() -> AppSettings:
    """
    Get cached application settings based on the current environment.
    
    Returns:
        AppSettings: The application settings object for the current environment.
    """
    environment = get_environment()
    
    if environment == Environment.DEVELOPMENT:
        from coding_agent.config.settings.development import DevelopmentSettings
        return DevelopmentSettings()
    elif environment == Environment.STAGING:
        from coding_agent.config.settings.staging import StagingSettings
        return StagingSettings()
    elif environment == Environment.PRODUCTION:
        from coding_agent.config.settings.production import ProductionSettings
        return ProductionSettings()
    else:  # Default to development
        from coding_agent.config.settings.development import DevelopmentSettings
        return DevelopmentSettings()
