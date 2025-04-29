"""Base settings for the Coding Agent."""

import os
from enum import Enum
from typing import Any, Dict, List, Optional, Union, ClassVar, Set
from pydantic_settings import BaseSettings
from pydantic import validator, Field, field_validator, model_validator # Import model_validator
from decouple import config, Config, RepositoryEnv

# Define the path to the .env file
ENV_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env')
# Create a custom config object that uses the .env file
config = Config(RepositoryEnv(ENV_FILE_PATH))


class ModelProvider(str, Enum):
    """Supported AI model providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"


class AppSettings(BaseSettings):
    """
    Base settings class that loads environment variables based on the naming pattern.
    All environment specific settings classes should inherit from this class.
    """
    # Project info
    PROJECT_NAME: str = Field(default="Coding Agent")
    VERSION: str = Field(default="0.1.0")
    DESCRIPTION: str = Field(default="An intelligent coding assistant")
    
    # LangChain and LangGraph API Settings
    OPENAI_API_KEY: Optional[str] = Field(default=None)
    
    # Model Configuration
    ACTIVE_PROVIDER: ModelProvider = Field(default=ModelProvider.OPENAI)
    MODEL_NAME: str = Field(default="gpt-4.1")  # Default model for OpenAI
    ANTHROPIC_MODEL: str = Field(default="claude-3-opus-20240229")  # Default model for Anthropic
    GOOGLE_MODEL: str = Field(default="gemini-1.5-pro")  # Default model for Google
    
    # Agent Configuration
    TEMPERATURE: float = Field(default=0.0)
    MAX_TOKENS: int = Field(default=4096)
    
    # Optional: Alternative AI Provider Settings
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None)
    GOOGLE_API_KEY: Optional[str] = Field(default=None)
    
    # Optional: File Operation Limits
    MAX_FILE_SIZE_MB: int = Field(default=10)
    
    # Additional configuration
    DEBUG: bool = Field(default=False)
    
    # Hard-coded ALLOWED_EXTENSIONS - no environment loading attempted
    ALLOWED_EXTENSIONS: ClassVar[List[str]] = ["py", "js", "ts", "json", "md", "txt"]
    
    class Config:
        """Pydantic configuration for settings."""
        env_file_encoding = "utf-8"
        case_sensitive = True
        
        # Skip environment variable loading for ALLOWED_EXTENSIONS
        env_skip = {"ALLOWED_EXTENSIONS"}
