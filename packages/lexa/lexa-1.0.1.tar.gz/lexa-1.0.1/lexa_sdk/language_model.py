"""
Lexa Language Model Implementation

This module contains the LexaLanguageModel class that handles
API communication with the Lexa backend for text generation.
"""

import json
import time
from typing import Dict, List, Optional, Iterator, AsyncIterator, Any, Union
import httpx
import requests

try:
    from .ssl_enhancer import get_ssl_enhancer
    SSL_ENHANCER_AVAILABLE = True
except ImportError:
    SSL_ENHANCER_AVAILABLE = False

try:
    from .ssl_config import SecureSSLMixin
    SSL_CONFIG_AVAILABLE = True
except ImportError:
    SSL_CONFIG_AVAILABLE = False

from .models import (
    LexaMessage, 
    LexaResponse, 
    LexaStreamChunk, 
    ChatCompletionRequest,
    LEXA_MODELS
)
from .exceptions import (
    LexaAPIError,
    LexaAuthenticationError,
    LexaRateLimitError,
    LexaValidationError,
    LexaServerError,
    LexaTimeoutError,
    LexaConnectionError,
)


class LexaLanguageModel(SecureSSLMixin if SSL_CONFIG_AVAILABLE else object):
    """
    Language model implementation for Lexa API.
    
    Handles both streaming and non-streaming text generation,
    with support for synchronous and asynchronous operations.
    """
    
    def __init__(
        self,
        model_id: str,
        api_key: str,
        base_url: str = "https://www.lexa.chat",
        timeout: float = 30.0,
        verify_ssl: Optional[bool] = None,
        enhanced_ssl: Optional[bool] = None
    ):
        """
        Initialize the language model.

        Args:
            model_id: The model identifier (e.g., 'lexa-mml')
            api_key: The API key for authentication
            base_url: The base URL for the API
            timeout: Request timeout in seconds
            verify_ssl: SSL verification setting (auto-detected if None)
            enhanced_ssl: Enhanced SSL setting (auto-detected if None)
        """
        self.model_id = model_id
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        
        # Auto-configure SSL for simplicity and compatibility
        if verify_ssl is None and enhanced_ssl is None:
            # Default to disabled SSL verification for maximum compatibility
            self.verify_ssl = False
            self.enhanced_ssl = False
        else:
            self.verify_ssl = verify_ssl if verify_ssl is not None else False
            self.enhanced_ssl = enhanced_ssl if enhanced_ssl is not None else False
        
        # Setup SSL verification
        self._setup_ssl_verification()
        
        # Validate model
        if model_id not in LEXA_MODELS:
            available_models = list(LEXA_MODELS.keys())
            raise ValueError(f"Unknown model '{model_id}'. Available models: {available_models}")
        
        # Setup headers
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "lexa-python-sdk/1.0.0",
        }
        
        # API endpoint
        self.endpoint = f"{self.base_url}/openai/chat/completions"
    
    def _handle_response_error(self, response: requests.Response) -> None:
        """Handle HTTP error responses and raise appropriate exceptions."""
        try:
            error_data = response.json()
        except json.JSONDecodeError:
            error_data = {"error": {"message": response.text}}
        
        error_message = error_data.get("error", {}).get("message", f"HTTP {response.status_code}")
        
        if response.status_code == 401:
            raise LexaAuthenticationError(error_message)
        elif response.status_code == 400:
            raise LexaValidationError(error_message, error_data.get("error", {}))
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            retry_after_int = int(retry_after) if retry_after and retry_after.isdigit() else None
            raise LexaRateLimitError(error_message, retry_after_int)
        elif response.status_code >= 500:
            raise LexaServerError(error_message, response.status_code)
        else:
            raise LexaAPIError(error_message, response.status_code, error_data)
    
    def _prepare_request_payload(self, messages: List[LexaMessage], **kwargs) -> Dict[str, Any]:
        """Prepare the request payload for the API."""
        payload = {
            "model": self.model_id,
            "messages": messages,
        }
        
        # Add optional parameters
        for key, value in kwargs.items():
            if value is not None:
                payload[key] = value
        
        return payload
    
    def generate(
        self, 
        messages: List[LexaMessage], 
        **kwargs
    ) -> LexaResponse:
        """
        Generate a non-streaming response.
        
        Args:
            messages: List of messages in the conversation
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            LexaResponse with the generated completion
        """
        payload = self._prepare_request_payload(messages, **kwargs)
        payload["stream"] = False
        
        try:
            if self.requests_session:
                # Use enhanced SSL session
                response = self.requests_session.post(
                    self.endpoint,
                    headers=self.headers,
                    json=payload,
                    timeout=self.timeout
                )
            else:
                # Use standard requests
                response = requests.post(
                    self.endpoint,
                    headers=self.headers,
                    json=payload,
                    timeout=self.timeout,
                    verify=self.verify_ssl
                )
            
            if not response.ok:
                self._handle_response_error(response)
            
            return response.json()
            
        except requests.exceptions.Timeout:
            raise LexaTimeoutError()
        except requests.exceptions.ConnectionError:
            raise LexaConnectionError()
        except requests.exceptions.RequestException as e:
            raise LexaAPIError(f"Request failed: {str(e)}")
    
    def stream(
        self, 
        messages: List[LexaMessage], 
        **kwargs
    ) -> Iterator[LexaStreamChunk]:
        """
        Generate a streaming response.
        
        Args:
            messages: List of messages in the conversation
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Yields:
            LexaStreamChunk objects with incremental completions
        """
        payload = self._prepare_request_payload(messages, **kwargs)
        payload["stream"] = True
        
        try:
            if self.requests_session:
                # Use enhanced SSL session
                response_ctx = self.requests_session.post(
                    self.endpoint,
                    headers=self.headers,
                    json=payload,
                    timeout=self.timeout,
                    stream=True
                )
            else:
                # Use standard requests
                response_ctx = requests.post(
                    self.endpoint,
                    headers=self.headers,
                    json=payload,
                    timeout=self.timeout,
                    stream=True,
                    verify=self.verify_ssl
                )
            
            with response_ctx as response:
                
                if not response.ok:
                    self._handle_response_error(response)
                
                for line in response.iter_lines(decode_unicode=True):
                    if line.startswith("data: "):
                        data = line[6:]  # Remove "data: " prefix
                        
                        if data == "[DONE]":
                            break
                        
                        try:
                            chunk = json.loads(data)
                            yield chunk
                        except json.JSONDecodeError:
                            continue
                            
        except requests.exceptions.Timeout:
            raise LexaTimeoutError()
        except requests.exceptions.ConnectionError:
            raise LexaConnectionError()
        except requests.exceptions.RequestException as e:
            raise LexaAPIError(f"Request failed: {str(e)}")
    
    async def agenerate(
        self, 
        messages: List[LexaMessage], 
        **kwargs
    ) -> LexaResponse:
        """
        Async generate a non-streaming response.
        
        Args:
            messages: List of messages in the conversation
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            LexaResponse with the generated completion
        """
        payload = self._prepare_request_payload(messages, **kwargs)
        payload["stream"] = False
        
        # Setup SSL verification for async client
        if self.verify_ssl and self.enhanced_ssl and self.ssl_enhancer:
            try:
                ssl_context = self.ssl_enhancer.create_enhanced_ssl_context()
                verify = ssl_context
            except Exception:
                verify = self.verify_ssl
        else:
            verify = self.verify_ssl
            
        async with httpx.AsyncClient(verify=verify) as client:
            try:
                response = await client.post(
                    self.endpoint,
                    headers=self.headers,
                    json=payload,
                    timeout=self.timeout
                )
                
                if not response.is_success:
                    # Convert httpx response to requests-like for error handling
                    mock_response = type('MockResponse', (), {
                        'status_code': response.status_code,
                        'headers': response.headers,
                        'json': lambda: response.json(),
                        'text': response.text,
                        'ok': response.is_success
                    })()
                    self._handle_response_error(mock_response)
                
                return response.json()
                
            except httpx.TimeoutException:
                raise LexaTimeoutError()
            except httpx.ConnectError:
                raise LexaConnectionError()
            except httpx.RequestError as e:
                raise LexaAPIError(f"Request failed: {str(e)}")
    
    async def astream(
        self, 
        messages: List[LexaMessage], 
        **kwargs
    ) -> AsyncIterator[LexaStreamChunk]:
        """
        Async generate a streaming response.
        
        Args:
            messages: List of messages in the conversation
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Yields:
            LexaStreamChunk objects with incremental completions
        """
        payload = self._prepare_request_payload(messages, **kwargs)
        payload["stream"] = True
        
        # Setup SSL verification for async client
        if self.verify_ssl and self.enhanced_ssl and self.ssl_enhancer:
            try:
                ssl_context = self.ssl_enhancer.create_enhanced_ssl_context()
                verify = ssl_context
            except Exception:
                verify = self.verify_ssl
        else:
            verify = self.verify_ssl
            
        async with httpx.AsyncClient(verify=verify) as client:
            try:
                async with client.stream(
                    "POST",
                    self.endpoint,
                    headers=self.headers,
                    json=payload,
                    timeout=self.timeout
                ) as response:
                    
                    if not response.is_success:
                        # Convert httpx response to requests-like for error handling
                        mock_response = type('MockResponse', (), {
                            'status_code': response.status_code,
                            'headers': response.headers,
                            'json': lambda: response.json() if response.content else {},
                            'text': response.text,
                            'ok': response.is_success
                        })()
                        self._handle_response_error(mock_response)
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]  # Remove "data: " prefix
                            
                            if data == "[DONE]":
                                break
                            
                            try:
                                chunk = json.loads(data)
                                yield chunk
                            except json.JSONDecodeError:
                                continue
                                
            except httpx.TimeoutException:
                raise LexaTimeoutError()
            except httpx.ConnectError:
                raise LexaConnectionError()
            except httpx.RequestError as e:
                raise LexaAPIError(f"Request failed: {str(e)}")

    def _auto_configure_ssl(self, verify_ssl: Optional[bool], enhanced_ssl: Optional[bool]) -> tuple[bool, bool]:
        """
        Automatically configure SSL settings for optimal security and compatibility.

        Returns:
            Tuple of (verify_ssl, enhanced_ssl) settings
        """
        # If user explicitly set values, respect them
        if verify_ssl is not None and enhanced_ssl is not None:
            return verify_ssl, enhanced_ssl

        # Auto-detection logic for maximum simplicity
        if verify_ssl is None and enhanced_ssl is None:
            # Default to enhanced SSL (secure and handles certificate issues)
            return True, True

        # If only one is set, intelligently set the other
        if verify_ssl is None:
            # If enhanced_ssl is True, enable SSL verification
            # If enhanced_ssl is False, disable SSL verification
            return enhanced_ssl, enhanced_ssl

        if enhanced_ssl is None:
            # If verify_ssl is True, try enhanced SSL
            # If verify_ssl is False, don't use enhanced SSL
            return verify_ssl, verify_ssl

        return verify_ssl, enhanced_ssl

    def _setup_ssl_verification(self):
        """Setup SSL verification based on auto-configured settings."""
        if self.verify_ssl and self.enhanced_ssl:
            try:
                self.ssl_enhancer = get_ssl_enhancer()
                self.requests_session = self.ssl_enhancer.get_requests_session()
            except Exception:
                # Fall back to standard verification
                self.ssl_enhancer = None
                self.requests_session = None
        else:
            self.ssl_enhancer = None
            self.requests_session = None

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        model_info = LEXA_MODELS.get(self.model_id)
        if not model_info:
            return {"id": self.model_id, "name": "Unknown"}
        
        return {
            "id": model_info.id,
            "name": model_info.name,
            "description": model_info.description,
            "context_window": model_info.context_window,
            "max_tokens": model_info.max_tokens,
        }
