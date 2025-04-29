"""
Configuration manager for the application.
Provides centralized access to application settings and configuration.
"""

import logging
from typing import Any, Dict, Optional, Type

from coding_agent.config.settings import AppSettings, get_app_settings
from coding_agent.config.settings.base import ModelProvider
# Import the logger
from coding_agent.utils.logging import logger

class ConfigurationManager:
    """
    Configuration manager for the Coding Agent.
    Provides centralized access to application settings and configuration.
    """
    
    def __init__(self):
        """Initialize the configuration manager with application settings."""
        self._settings = get_app_settings()
        logger.info(f"Initialized ConfigurationManager with {self._settings.__class__.__name__}")
    
    @property
    def settings(self) -> AppSettings:
        """
        Get the current application settings.
        
        Returns:
            AppSettings: The current application settings.
        """
        return self._settings
    
    def get_model_config(self) -> Dict[str, Any]:
        """
        Get configuration for the active AI model.
        
        Returns:
            Dict[str, Any]: Configuration dictionary for the model.
        """
        provider = self._settings.ACTIVE_PROVIDER
        logger.debug(f"Getting model config for provider: {provider.value}")
        
        # Base config that applies to all models
        config = {
            "temperature": self._settings.TEMPERATURE,
            "max_tokens": self._settings.MAX_TOKENS,
        }
        
        # Add provider-specific model names
        if provider == ModelProvider.OPENAI:
            config["openai_model_name"] = self._settings.MODEL_NAME
        elif provider == ModelProvider.ANTHROPIC:
            config["anthropic_model_name"] = self._settings.ANTHROPIC_MODEL
        elif provider == ModelProvider.GOOGLE:
            config["google_model_name"] = self._settings.GOOGLE_MODEL
            
        return config
    
    def set_model_provider(self, provider: str) -> None:
        """
        Switch the AI model provider.
        
        Args:
            provider: The provider to switch to ('openai', 'anthropic', or 'google')
        """
        try:
            # Convert string to ModelProvider enum
            provider_enum = ModelProvider(provider.lower())
            
            # Check if we have the necessary API key for this provider
            if provider_enum == ModelProvider.ANTHROPIC and not self._settings.ANTHROPIC_API_KEY:
                logger.warning("ANTHROPIC_API_KEY not set, cannot switch to Anthropic")
                return
            elif provider_enum == ModelProvider.GOOGLE and not self._settings.GOOGLE_API_KEY:
                logger.warning("GOOGLE_API_KEY not set, cannot switch to Google")
                return
            
            # Update the active provider
            self._settings.ACTIVE_PROVIDER = provider_enum
            logger.info(f"Switched model provider to {provider_enum.value}")
            
        except (ValueError, KeyError) as e:
            logger.error(f"Failed to switch provider to {provider}: {str(e)}")
    
    def get_file_limits(self) -> Dict[str, Any]:
        """
        Get file operation limits.
        
        Returns:
            Dict[str, Any]: File operation limits.
        """
        return {
            "max_file_size_mb": self._settings.MAX_FILE_SIZE_MB,
            "allowed_extensions": self._settings.ALLOWED_EXTENSIONS,
        }
    
    def get_active_provider(self) -> str:
        """
        Get the name of the currently active AI provider.
        
        Returns:
            str: The name of the active provider
        """
        return self._settings.ACTIVE_PROVIDER.value


# Singleton instance
config_manager = ConfigurationManager()
