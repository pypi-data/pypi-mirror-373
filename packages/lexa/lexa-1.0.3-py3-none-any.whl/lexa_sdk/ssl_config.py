"""
SSL Configuration utilities for Lexa SDK.

This module provides secure SSL configuration options and utilities
for handling SSL certificate issues in a secure manner.
"""

import os
import warnings
from typing import Optional, Union
import ssl


def get_secure_ssl_config(
    verify_ssl: Optional[bool] = None,
    enhanced_ssl: Optional[bool] = None,
    development_mode: bool = False
) -> dict:
    """
    Get secure SSL configuration with appropriate warnings.
    
    Args:
        verify_ssl: Whether to verify SSL certificates
        enhanced_ssl: Whether to use enhanced SSL with additional certificates
        development_mode: Whether running in development mode
        
    Returns:
        Dictionary with SSL configuration
    """
    # Default to secure settings
    if verify_ssl is None:
        verify_ssl = True
        
    if enhanced_ssl is None:
        enhanced_ssl = True
    
    # Check environment variables for development mode
    if not development_mode:
        development_mode = (
            os.getenv('LEXA_DEV_MODE', '').lower() in ('true', '1', 'yes') or
            os.getenv('NODE_ENV', '').lower() == 'development' or
            os.getenv('ENVIRONMENT', '').lower() in ('dev', 'development')
        )
    
    # Warn if SSL verification is disabled
    if not verify_ssl:
        if development_mode:
            warnings.warn(
                "SSL verification is disabled in development mode. "
                "This should NEVER be used in production!",
                UserWarning,
                stacklevel=3
            )
        else:
            warnings.warn(
                "SSL verification is disabled! This creates security risks. "
                "Consider using enhanced_ssl=True instead, or update your certificates.",
                SecurityWarning,
                stacklevel=3
            )
    
    return {
        'verify_ssl': verify_ssl,
        'enhanced_ssl': enhanced_ssl,
        'development_mode': development_mode
    }


def suggest_ssl_fixes() -> str:
    """
    Provide suggestions for fixing SSL certificate issues.
    
    Returns:
        String with SSL fix suggestions
    """
    return """
SSL Certificate Issue Solutions:

1. Enhanced SSL (Recommended):
   client = Lexa(api_key='key', enhanced_ssl=True)

2. Update system certificates:
   - macOS: brew install ca-certificates
   - Linux: sudo apt-get install ca-certificates
   - Python: pip install --upgrade certifi

3. Check system time:
   Ensure your system clock is accurate

4. Corporate network:
   Contact IT if behind corporate proxy/firewall

5. Development only (NOT for production):
   Set LEXA_DEV_MODE=true environment variable
"""


class SecureSSLMixin:
    """
    Mixin class to add secure SSL configuration to SDK classes.
    """
    
    def _configure_ssl_safely(
        self, 
        verify_ssl: bool = True, 
        enhanced_ssl: bool = True,
        development_mode: bool = False
    ) -> dict:
        """Configure SSL settings with security considerations."""
        config = get_secure_ssl_config(verify_ssl, enhanced_ssl, development_mode)
        
        # If SSL verification is disabled and we're not in dev mode, provide help
        if not config['verify_ssl'] and not config['development_mode']:
            print("\n" + "="*60)
            print("⚠️  SSL VERIFICATION DISABLED - SECURITY RISK!")
            print("="*60)
            print(suggest_ssl_fixes())
            print("="*60)
        
        return config


# Custom warning category for SSL security issues
class SecurityWarning(UserWarning):
    """Warning category for security-related issues."""
    pass


# Register the custom warning category
warnings.simplefilter('always', SecurityWarning)
