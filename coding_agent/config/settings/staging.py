"""Staging environment settings."""

from typing import List, Optional, Dict, Any

from coding_agent.config.settings.base import AppSettings


class StagingSettings(AppSettings):
    """Settings for the staging environment."""
    
    DEBUG: bool = False
    
    # Settings specific to staging environment
    # These settings are similar to production but may include
    # different endpoints or debugging features
    
    class Config:
        """Pydantic configuration for staging settings."""
        env_file = ".env.staging"
        env_file_encoding = "utf-8"
