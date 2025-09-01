"""
OpenAI-Compatible Client for Lexa SDK

This module provides a familiar OpenAI-style interface for the Lexa API,
making it easy to drop-in replace OpenAI usage with Lexa.
"""

from typing import Dict, List, Optional, Iterator, Union, Any
import json

from .provider import LexaProvider
from .language_model import LexaLanguageModel
from .models import LexaMessage, LexaResponse, LexaStreamChunk, LEXA_MODELS
from .exceptions import LexaError, LexaValidationError


class Lexa:
    """
    OpenAI-compatible client for Lexa API.
    
    Provides a familiar interface similar to the OpenAI Python SDK,
    making it easy to migrate existing code to use Lexa.
    
    Example:
        ```python
        from lexa_sdk import Lexa
        
        client = Lexa(api_key="your-api-key")
        
        response = client.chat.completions.create(
            model="lexa-mml",
            messages=[{"role": "user", "content": "Hello!"}]
        )
        ```
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://www.lexa.chat",
        timeout: float = 30.0,
        verify_ssl: Optional[bool] = None,
        enhanced_ssl: Optional[bool] = None
    ):
        """
        Initialize the Lexa client.

        Args:
            api_key: The API key for authentication
            base_url: The base URL for the API
            timeout: Request timeout in seconds
            verify_ssl: SSL verification setting (auto-configured if None)
            enhanced_ssl: Enhanced SSL setting (auto-configured if None)
        """
        self.provider = LexaProvider(api_key, base_url, timeout, verify_ssl, enhanced_ssl)
        
        # Create chat interface
        self.chat = ChatInterface(self.provider)
        
        # Create models interface
        self.models = ModelsInterface(self.provider)
    
    def list_models(self) -> Dict[str, Any]:
        """
        List all available models (OpenAI-compatible format).
        
        Returns:
            Dictionary with models list in OpenAI format
        """
        models_list = self.provider.list_models()
        return {
            "object": "list",
            "data": models_list
        }
    
    def __repr__(self) -> str:
        """String representation of the client."""
        return f"Lexa(provider={self.provider})"


class ChatInterface:
    """Interface for chat completions."""
    
    def __init__(self, provider: LexaProvider):
        self.provider = provider
        self.completions = ChatCompletions(provider)


class ChatCompletions:
    """Chat completions interface."""
    
    def __init__(self, provider: LexaProvider):
        self.provider = provider
    
    def create(
        self,
        model: str = "lexa-mml",
        messages: List[Dict[str, str]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[Union[str, List[str]]] = None,
        stream: bool = False,
        user: Optional[str] = None,
        **kwargs
    ) -> Union[LexaResponse, Iterator[LexaStreamChunk]]:
        """
        Create a chat completion.
        
        Args:
            model: Model to use for completion
            messages: List of messages in the conversation
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum number of tokens to generate
            top_p: Nucleus sampling parameter
            frequency_penalty: Frequency penalty (-2.0 to 2.0)
            presence_penalty: Presence penalty (-2.0 to 2.0)
            stop: Stop sequences
            stream: Whether to stream the response
            user: User identifier
            **kwargs: Additional parameters
            
        Returns:
            LexaResponse for non-streaming, Iterator[LexaStreamChunk] for streaming
        """
        if messages is None:
            raise LexaValidationError("messages parameter is required")
        
        # Validate model
        if model not in LEXA_MODELS:
            available_models = list(LEXA_MODELS.keys())
            raise LexaValidationError(f"Unknown model '{model}'. Available models: {available_models}")
        
        # Convert messages to proper format
        formatted_messages = self._format_messages(messages)
        
        # Create language model
        language_model = self.provider.language_model(model)
        
        # Prepare parameters
        params = {}
        if temperature is not None:
            params["temperature"] = temperature
        if max_tokens is not None:
            params["max_tokens"] = max_tokens
        if top_p is not None:
            params["top_p"] = top_p
        if frequency_penalty is not None:
            params["frequency_penalty"] = frequency_penalty
        if presence_penalty is not None:
            params["presence_penalty"] = presence_penalty
        if stop is not None:
            params["stop"] = stop
        if user is not None:
            params["user"] = user
        
        # Add any additional parameters
        params.update(kwargs)
        
        # Generate response
        if stream:
            return language_model.stream(formatted_messages, **params)
        else:
            return language_model.generate(formatted_messages, **params)
    
    def _format_messages(self, messages: List[Dict[str, str]]) -> List[LexaMessage]:
        """Convert OpenAI format messages to Lexa format."""
        formatted = []
        
        for message in messages:
            if not isinstance(message, dict):
                raise LexaValidationError("Each message must be a dictionary")
            
            if "role" not in message:
                raise LexaValidationError("Each message must have a 'role' field")
            
            if "content" not in message:
                raise LexaValidationError("Each message must have a 'content' field")
            
            role = message["role"]
            content = message["content"]
            
            # Validate role
            if role not in ["system", "user", "assistant"]:
                raise LexaValidationError(f"Invalid role '{role}'. Must be 'system', 'user', or 'assistant'")
            
            formatted.append({
                "role": role,
                "content": content
            })
        
        return formatted


class ModelsInterface:
    """Interface for model operations."""
    
    def __init__(self, provider: LexaProvider):
        self.provider = provider
    
    def list(self) -> Dict[str, Any]:
        """
        List available models.
        
        Returns:
            Dictionary with models list in OpenAI format
        """
        models_list = self.provider.list_models()
        return {
            "object": "list",
            "data": models_list
        }
    
    def retrieve(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve information about a specific model.
        
        Args:
            model_id: The model identifier
            
        Returns:
            Model information dictionary or None if not found
        """
        return self.provider.get_model_info(model_id)


# Legacy/alternative interface for backward compatibility
def create_client(api_key: str, **kwargs) -> Lexa:
    """
    Create a Lexa client instance.
    
    Args:
        api_key: The API key for authentication
        **kwargs: Additional arguments passed to Lexa constructor
        
    Returns:
        Lexa client instance
    """
    return Lexa(api_key=api_key, **kwargs)


# Convenience function for quick usage
def chat(
    messages: List[Dict[str, str]],
    model: str = "lexa-mml",
    api_key: Optional[str] = None,
    verify_ssl: Optional[bool] = None,
    **kwargs
) -> LexaResponse:
    """
    Quick chat completion function.

    Args:
        messages: List of messages in the conversation
        model: Model to use for completion
        api_key: API key (if not provided, expects LEXA_API_KEY env var)
        verify_ssl: SSL verification setting (auto-configured if None)
        **kwargs: Additional parameters

    Returns:
        LexaResponse with the completion
    """
    if api_key is None:
        import os
        api_key = os.getenv("LEXA_API_KEY")
        if not api_key:
            raise LexaError("API key not provided. Set LEXA_API_KEY environment variable or pass api_key parameter.")
    
    client = Lexa(api_key=api_key, verify_ssl=verify_ssl)
    return client.chat.completions.create(
        model=model,
        messages=messages,
        **kwargs
    )
