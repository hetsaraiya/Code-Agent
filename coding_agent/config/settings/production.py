"""Production environment settings."""

from typing import List, Optional, Dict, Any

from coding_agent.config.settings.base import AppSettings


class ProductionSettings(AppSettings):
    """Settings for the production environment."""
    
    DEBUG: bool = False
    
    # Stricter file operation limits for production
    MAX_FILE_SIZE_MB: int = 5
    
    class Config:
        """Pydantic configuration for production settings."""
        env_file = ".env.prod"
        env_file_encoding = "utf-8"
