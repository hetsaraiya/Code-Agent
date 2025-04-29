"""
Utility functions for interacting with models during runtime.
"""

from typing import Optional, Dict, Any, List
import os

from coding_agent.core.model_service import model_service
from coding_agent.config.manager import config_manager


def switch_model(provider_name: str) -> bool:
    """
    Switch to a different AI model provider during runtime.
    
    Args:
        provider_name: Name of the provider to switch to ('openai', 'anthropic', 'google')
        
    Returns:
        bool: True if successful, False otherwise
    """
    return model_service.switch_provider(provider_name)


def get_current_model_info() -> Dict[str, Any]:
    """
    Get information about the current model configuration.
    
    Returns:
        Dict[str, Any]: Information about the current model
    """
    provider = model_service.get_current_provider()
    config = config_manager.get_model_config()
    
    model_name = ""
    if provider == "openai":
        model_name = config.get("openai_model_name", "gpt-4")
    elif provider == "anthropic":
        model_name = config.get("anthropic_model_name", "claude-3-opus-20240229")
    elif provider == "google":
        model_name = config.get("google_model_name", "gemini-1.5-pro")
    
    return {
        "provider": provider,
        "model_name": model_name,
        "temperature": config.get("temperature", 0),
        "max_tokens": config.get("max_tokens", 4096)
    }


def list_available_models() -> List[Dict[str, Any]]:
    """
    List all available AI models that can be used.
    
    Returns:
        List[Dict[str, Any]]: Information about available models
    """
    models = []
    
    # Check OpenAI
    if config_manager.settings.OPENAI_API_KEY:
        models.append({
            "provider": "openai",
            "model_name": config_manager.settings.MODEL_NAME,
            "available": True
        })
    
    # Check Anthropic
    if config_manager.settings.ANTHROPIC_API_KEY:
        models.append({
            "provider": "anthropic",
            "model_name": config_manager.settings.ANTHROPIC_MODEL,
            "available": True
        })
    else:
        models.append({
            "provider": "anthropic",
            "model_name": config_manager.settings.ANTHROPIC_MODEL,
            "available": False,
            "reason": "API key not configured"
        })
      # Check Google
    if config_manager.settings.GOOGLE_API_KEY:
        models.append({
            "provider": "google",
            "model_name": config_manager.settings.GOOGLE_MODEL,
            "available": True
        })
    else:
        models.append({
            "provider": "google",
            "model_name": config_manager.settings.GOOGLE_MODEL,
            "available": False,
            "reason": "API key not configured"
        })
    
    return models
