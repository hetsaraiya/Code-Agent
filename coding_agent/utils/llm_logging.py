"""
LLM logging utilities for the Coding Agent.
This module provides functions to log LLM requests and responses.
"""

from typing import Any, Dict, List
import json
import time
import functools

from coding_agent.utils.logging import logger


def log_llm_request(messages: List[Dict[str, str]]) -> None:
    """
    Log an LLM request/prompt.
    
    Args:
        messages: List of messages being sent to the LLM
    """
    try:
        # Log the basic request info
        logger.info("LLM Request sent")
        
        # Format system and user messages for logging
        system_messages = [msg for msg in messages if msg.get("role") == "system"]
        user_messages = [msg for msg in messages if msg.get("role") == "user"]
        
        # Log system messages at debug level
        if system_messages:
            logger.debug(f"System prompt: {system_messages[0]['content'][:500]}...")
            
        # Log user messages at info level
        if user_messages:
            for i, msg in enumerate(user_messages):
                logger.info(f"User message {i+1}: {msg['content'][:500]}...")
                # Log full message at debug level
                logger.debug(f"Full user message {i+1}: {msg['content']}")
    except Exception as e:
        logger.error(f"Error logging LLM request: {str(e)}")


def log_llm_response(response: Any) -> None:
    """
    Log an LLM response.
    
    Args:
        response: Response from the LLM
    """
    try:
        logger.info("LLM Response received")
        
        # Extract content from the response based on its type
        if hasattr(response, "content"):
            content = response.content
        elif isinstance(response, dict) and "content" in response:
            content = response["content"]
        elif isinstance(response, str):
            content = response
        else:
            content = str(response)
            
        # Log a preview of the response at info level
        content_preview = content[:500] + ("..." if len(content) > 500 else "")
        logger.info(f"LLM response preview: {content_preview}")
        
        # Log the full response at debug level
        logger.debug(f"Full LLM response: {content}")
    except Exception as e:
        logger.error(f"Error logging LLM response: {str(e)}")


def log_llm_call(obj_or_func):
    """
    Adds logging to LLM calls. Can be used in two ways:
    1. As a decorator for functions that make LLM calls
    2. To wrap a model object and log its invoke method
    
    Args:
        obj_or_func: Either a function to wrap or a model object
        
    Returns:
        The wrapped function or a proxy for the model object
    """
    # If it's a function, use it as a decorator
    if callable(obj_or_func) and not hasattr(obj_or_func, 'invoke'):
        @functools.wraps(obj_or_func)
        def function_wrapper(*args, **kwargs):
            # Log the request if messages are present
            if "messages" in kwargs and isinstance(kwargs["messages"], list):
                log_llm_request(kwargs["messages"])
            elif len(args) >= 2 and isinstance(args[1], list):
                log_llm_request(args[1])
                
            # Measure response time
            start_time = time.time()
            response = obj_or_func(*args, **kwargs)
            elapsed_time = time.time() - start_time
            
            logger.info(f"LLM response time: {elapsed_time:.2f}s")
            log_llm_response(response)
            return response
        
        return function_wrapper
    
    # If it's a model object, create a proxy class
    else:
        class ModelLoggingProxy:
            def __init__(self, model):
                self.model = model
                logger.debug(f"Created logging proxy for {model.__class__.__name__}")
                
            def invoke(self, *args, **kwargs):
                # Log the request
                if args and isinstance(args[0], list):
                    log_llm_request(args[0])
                elif "messages" in kwargs:
                    log_llm_request(kwargs["messages"])
                    
                # Measure response time
                start_time = time.time()
                response = self.model.invoke(*args, **kwargs)
                elapsed_time = time.time() - start_time
                
                logger.info(f"LLM response time: {elapsed_time:.2f}s")
                log_llm_response(response)
                return response
            
            # Forward all other attributes to the underlying model
            def __getattr__(self, name):
                return getattr(self.model, name)
        
        return ModelLoggingProxy(obj_or_func)
