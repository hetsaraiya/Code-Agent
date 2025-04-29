"""Development environment settings."""

from typing import List, Optional, Dict, Any

from pydantic import Field

from coding_agent.config.settings.base import AppSettings


class DevelopmentSettings(AppSettings):
    """Settings for the development environment."""
    
    DEBUG: bool = True
    
    # Override default values for development if needed
    TEMPERATURE: float = Field(default=0.2)  # Slightly more creative in development
    
    class Config:
        """Pydantic configuration for development settings."""
        env_file = ".env.dev"
        env_file_encoding = "utf-8"
