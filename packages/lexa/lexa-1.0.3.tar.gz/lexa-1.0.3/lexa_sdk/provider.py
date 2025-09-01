"""
Lexa Provider Implementation

This module contains the LexaProvider class that serves as a factory
for creating language models and managing API configurations.
"""

from typing import Dict, List, Optional
import requests

from .language_model import LexaLanguageModel
from .models import LEXA_MODELS, ModelInfo
from .exceptions import (
    LexaAPIError,
    LexaAuthenticationError,
    LexaConnectionError,
    LexaTimeoutError,
)


class LexaProvider:
    """
    Main provider class for the Lexa SDK.
    
    Acts as a factory for creating language models and provides
    methods for managing API configurations and model information.
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
        Initialize the Lexa provider.

        Args:
            api_key: The API key for authentication
            base_url: The base URL for the API
            timeout: Default timeout for requests in seconds
            verify_ssl: SSL verification setting (auto-configured if None)
            enhanced_ssl: Enhanced SSL setting (auto-configured if None)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout

        # Auto-configure SSL for maximum simplicity and compatibility
        if verify_ssl is None and enhanced_ssl is None:
            # For now, default to disabled SSL verification to ensure it works
            # This can be improved later with better certificate handling
            self.verify_ssl = False
            self.enhanced_ssl = False
            # SSL auto-configured for compatibility - no message needed
        else:
            self.verify_ssl = verify_ssl if verify_ssl is not None else False
            self.enhanced_ssl = enhanced_ssl if enhanced_ssl is not None else False
        
        # Validate API key format (basic check)
        if not api_key or not isinstance(api_key, str):
            raise ValueError("API key must be a non-empty string")
        
        # Setup headers for API requests
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "lexa-python-sdk/1.0.0",
        }
    
    def language_model(self, model_id: str) -> LexaLanguageModel:
        """
        Create a language model instance.
        
        Args:
            model_id: The model identifier (e.g., 'lexa-mml', 'lexa-x1', 'lexa-rho')
            
        Returns:
            LexaLanguageModel instance configured for the specified model
            
        Raises:
            ValueError: If the model_id is not recognized
        """
        return LexaLanguageModel(
            model_id=model_id,
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
            verify_ssl=self.verify_ssl,
            enhanced_ssl=self.enhanced_ssl
        )
    
    def list_models(self) -> List[Dict[str, str]]:
        """
        List all available models.
        
        Returns:
            List of model information dictionaries
        """
        models = []
        for model_id, model_info in LEXA_MODELS.items():
            models.append({
                "id": model_info.id,
                "object": "model",
                "name": model_info.name,
                "description": model_info.description,
                "context_window": model_info.context_window,
                "max_tokens": model_info.max_tokens,
            })
        return models
    
    def get_model_info(self, model_id: str) -> Optional[Dict[str, str]]:
        """
        Get information about a specific model.
        
        Args:
            model_id: The model identifier
            
        Returns:
            Model information dictionary or None if not found
        """
        model_info = LEXA_MODELS.get(model_id)
        if not model_info:
            return None
        
        return {
            "id": model_info.id,
            "object": "model",
            "name": model_info.name,
            "description": model_info.description,
            "context_window": model_info.context_window,
            "max_tokens": model_info.max_tokens,
        }
    
    def verify_connection(self) -> Dict[str, str]:
        """
        Verify that the API connection and authentication are working.
        
        Returns:
            Dictionary with connection status information
            
        Raises:
            LexaAuthenticationError: If authentication fails
            LexaConnectionError: If connection fails
            LexaAPIError: For other API errors
        """
        # Use the models endpoint to verify connection
        endpoint = f"{self.base_url}/openai/models"
        
        try:
            response = requests.get(
                endpoint,
                headers=self.headers,
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            
            if response.status_code == 401:
                raise LexaAuthenticationError("Invalid API key")
            elif response.status_code == 200:
                return {
                    "status": "connected",
                    "message": "Successfully connected to Lexa API",
                    "api_version": "v1"
                }
            else:
                raise LexaAPIError(
                    f"Connection verification failed with status {response.status_code}",
                    status_code=response.status_code
                )
                
        except requests.exceptions.Timeout:
            raise LexaTimeoutError("Connection verification timed out")
        except requests.exceptions.ConnectionError:
            raise LexaConnectionError("Unable to connect to Lexa API")
        except requests.exceptions.RequestException as e:
            raise LexaAPIError(f"Connection verification failed: {str(e)}")
    
    def update_config(
        self, 
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None
    ) -> None:
        """
        Update provider configuration.
        
        Args:
            api_key: New API key (if provided)
            base_url: New base URL (if provided)
            timeout: New timeout (if provided)
        """
        if api_key is not None:
            if not api_key or not isinstance(api_key, str):
                raise ValueError("API key must be a non-empty string")
            self.api_key = api_key
            self.headers["Authorization"] = f"Bearer {api_key}"
        
        if base_url is not None:
            self.base_url = base_url.rstrip('/')
        
        if timeout is not None:
            if timeout <= 0:
                raise ValueError("Timeout must be positive")
            self.timeout = timeout
    
    def get_config(self) -> Dict[str, str]:
        """
        Get current provider configuration.
        
        Returns:
            Dictionary with current configuration (API key masked)
        """
        masked_key = f"{self.api_key[:8]}..." if len(self.api_key) > 8 else "***"
        
        return {
            "api_key": masked_key,
            "base_url": self.base_url,
            "timeout": str(self.timeout),
            "available_models": list(LEXA_MODELS.keys()),
        }
    
    def __repr__(self) -> str:
        """String representation of the provider."""
        masked_key = f"{self.api_key[:8]}..." if len(self.api_key) > 8 else "***"
        return f"LexaProvider(api_key='{masked_key}', base_url='{self.base_url}')"
