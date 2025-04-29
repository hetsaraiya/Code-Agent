"""
Model service module for the Coding Agent.
This module connects the configuration manager with the model manager,
providing an interface for switching between AI providers.
"""

from typing import Any, Dict, Optional

from coding_agent.config.manager import config_manager
from coding_agent.core.model_manager import model_manager, ModelProvider
# Import the logger
from coding_agent.utils.logging import logger


class ModelService:
    """
    Service that coordinates between the configuration manager and model manager.
    Provides methods for switching between different AI providers and models.
    """
    
    def __init__(self):
        """Initialize the model service with current configuration."""
        # Get initial configuration
        logger.info("Initializing ModelService")
        self.refresh_from_config()
    
    def refresh_from_config(self) -> None:
        """Refresh the model manager with the current configuration."""
        # Get current model configuration
        model_config = config_manager.get_model_config()
        
        # Get active provider from config
        provider_str = config_manager.get_active_provider()
        provider = ModelProvider(provider_str)
        
        logger.debug(f"Refreshing model configuration with provider: {provider.value}")
        
        # Update the model manager
        model_manager.provider = provider
        model_manager.update_config(model_config)
    
    def switch_provider(self, provider_name: str) -> bool:
        """
        Switch to a different AI provider.
        
        Args:
            provider_name: Name of the provider to switch to ('openai', 'anthropic', 'google')
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"Switching to provider: {provider_name}")
            
            # Update config manager
            config_manager.set_model_provider(provider_name)
            
            # Refresh model manager from updated config
            self.refresh_from_config()
            
            return True
        except Exception as e:
            logger.error(f"Error switching provider to {provider_name}: {str(e)}")
            return False
    
    def get_current_provider(self) -> str:
        """
        Get the name of the current AI provider.
        
        Returns:
            str: The name of the current provider
        """
        return model_manager.provider.value


# Global model service instance
model_service = ModelService()
