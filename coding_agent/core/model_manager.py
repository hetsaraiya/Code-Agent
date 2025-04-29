"""
Model manager module for the Coding Agent.
This module handles the initialization and switching of different AI model providers.
"""

from typing import Optional, Dict, Any, Union
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

# Import the logger
from coding_agent.utils.logging import logger
from coding_agent.utils.llm_logging import log_llm_call

# Import these conditionally to avoid errors if APIs aren't available
try:
    from langchain_anthropic import ChatAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("Anthropic package not available. Anthropic models will not be accessible.")

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    logger.warning("Google Generative AI package not available. Google models will not be accessible.")

from coding_agent.config.settings.base import ModelProvider


class ModelManager:
    """
    Manager for AI model providers that handles initialization and switching between models.
    """
    
    def __init__(self, provider: ModelProvider = ModelProvider.OPENAI, 
                 model_configs: Dict[str, Any] = None):
        """
        Initialize the model manager with the specified provider.
        
        Args:
            provider: The AI model provider to use
            model_configs: Configuration parameters for the models
        """
        self._provider = provider
        self._model_configs = model_configs or {}
        self._current_model = None
        logger.info(f"Initializing ModelManager with provider: {provider.value}")
        self._initialize_model()
        
    def _initialize_model(self) -> None:
        """Initialize the model based on the current provider."""
        logger.debug(f"Initializing model for provider: {self._provider.value}")
        if self._provider == ModelProvider.OPENAI:
            self._current_model = self._create_openai_model()
        elif self._provider == ModelProvider.ANTHROPIC and ANTHROPIC_AVAILABLE:
            self._current_model = self._create_anthropic_model()
        elif self._provider == ModelProvider.GOOGLE and GOOGLE_AVAILABLE:
            self._current_model = self._create_google_model()
        else:
            # Fall back to OpenAI if requested provider is not available
            logger.warning(f"Provider {self._provider} is not available. Falling back to OpenAI.")
            self._provider = ModelProvider.OPENAI
            self._current_model = self._create_openai_model()
          # Add logging for LLM calls
        # Instead of modifying the invoke method directly, we'll wrap the model object
        # This approach works with newer LangChain versions where invoke might be a property or descriptor
        self._current_model = log_llm_call(self._current_model)
        logger.debug("Added LLM logging wrapper to model")
      
    def _create_openai_model(self) -> ChatOpenAI:
        """
        Create an OpenAI model instance.
        
        Returns:
            ChatOpenAI: An instance of the OpenAI chat model
        """
        from coding_agent.config.manager import config_manager

        api_key = config_manager.settings.OPENAI_API_KEY
        logger.debug("Creating OpenAI model instance")
        
        return ChatOpenAI(model="gpt-4o", temperature=0.9, openai_api_key=api_key)
    
    def _create_anthropic_model(self) -> Union[BaseChatModel, ChatOpenAI]:
        """
        Create an Anthropic model instance.
        
        Returns:
            BaseChatModel: An instance of the Anthropic chat model or fallback to OpenAI
        """
        if not ANTHROPIC_AVAILABLE:
            logger.warning("Anthropic package not installed. Falling back to OpenAI.")
            return self._create_openai_model()
            
        model_name = self._model_configs.get("anthropic_model_name", "claude-3-opus-20240229")
        temperature = self._model_configs.get("temperature", 0)
        logger.debug(f"Creating Anthropic model instance with model: {model_name}")
        return ChatAnthropic(model=model_name, temperature=temperature)
    
    def _create_google_model(self) -> Union[BaseChatModel, ChatOpenAI]:
        """
        Create a Google Generative AI model instance.
        
        Returns:
            BaseChatModel: An instance of the Google chat model or fallback to OpenAI
        """
        if not GOOGLE_AVAILABLE:
            logger.warning("Google Generative AI package not installed. Falling back to OpenAI.")
            return self._create_openai_model()
            
        model_name = self._model_configs.get("google_model_name", "gemini-1.5-pro")
        temperature = self._model_configs.get("temperature", 0)
        logger.debug(f"Creating Google model instance with model: {model_name}")
        return ChatGoogleGenerativeAI(model=model_name, temperature=temperature)
    
    @property
    def provider(self) -> ModelProvider:
        """Get the current model provider."""
        return self._provider
    
    @provider.setter
    def provider(self, value: ModelProvider) -> None:
        """
        Set the model provider and initialize the corresponding model.
        
        Args:
            value: The model provider to switch to
        """
        if self._provider != value:
            logger.info(f"Switching provider from {self._provider.value} to {value.value}")
            self._provider = value
            self._initialize_model()
    
    @property
    def model(self) -> BaseChatModel:
        """Get the current model instance."""
        return self._current_model
    
    def update_config(self, config: Dict[str, Any]) -> None:
        """
        Update model configuration and reinitialize the model.
        
        Args:
            config: New configuration parameters
        """
        logger.debug(f"Updating model configuration: {config}")
        self._model_configs.update(config)
        self._initialize_model()


# Global model manager instance
model_manager = ModelManager()
