"""Local environment settings."""

from typing import List, Optional, Dict, Any

from pydantic import Field

from coding_agent.config.settings.base import AppSettings


class LocalSettings(AppSettings):
    """Settings for local development environment."""
    
    DEBUG: bool = True
    
    # Override default values for local development
    TEMPERATURE: float = Field(default=0.3)  # More creative in local development
    
    class Config:
        """Pydantic configuration for local settings."""
        env_file = ".env.local"
        env_file_encoding = "utf-8"
