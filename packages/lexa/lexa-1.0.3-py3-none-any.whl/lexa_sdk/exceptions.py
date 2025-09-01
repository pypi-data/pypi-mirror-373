"""
Custom exceptions for Lexa SDK

This module defines all the custom exception classes used throughout
the SDK for handling different types of API errors and failures.
"""

from typing import Optional, Dict, Any


class LexaError(Exception):
    """Base exception class for all Lexa SDK errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class LexaAPIError(LexaError):
    """Exception raised for API-related errors."""
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)
        self.status_code = status_code
        self.response_data = response_data or {}


class LexaAuthenticationError(LexaAPIError):
    """Exception raised for authentication errors (401)."""
    
    def __init__(self, message: str = "Authentication failed. Please check your API key."):
        super().__init__(message, status_code=401)


class LexaRateLimitError(LexaAPIError):
    """Exception raised for rate limiting errors (429)."""
    
    def __init__(
        self, 
        message: str = "Rate limit exceeded.",
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, status_code=429, details=details)
        self.retry_after = retry_after


class LexaValidationError(LexaAPIError):
    """Exception raised for validation errors (400)."""
    
    def __init__(
        self, 
        message: str = "Invalid request parameters.",
        validation_errors: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, status_code=400)
        self.validation_errors = validation_errors or {}


class LexaServerError(LexaAPIError):
    """Exception raised for server errors (5xx)."""
    
    def __init__(self, message: str = "Internal server error.", status_code: int = 500):
        super().__init__(message, status_code=status_code)


class LexaTimeoutError(LexaError):
    """Exception raised when API request times out."""
    
    def __init__(self, message: str = "Request timed out."):
        super().__init__(message)


class LexaConnectionError(LexaError):
    """Exception raised when unable to connect to the API."""
    
    def __init__(self, message: str = "Failed to connect to Lexa API."):
        super().__init__(message)
