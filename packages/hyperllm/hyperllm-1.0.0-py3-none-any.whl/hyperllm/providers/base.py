"""
Base provider class for all LLM providers
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, **kwargs):
        """
        Initialize the provider with configuration
        
        Args:
            **kwargs: Provider-specific configuration options
        """
        self.config = kwargs
        self._validate_and_setup()
    
    def _validate_and_setup(self):
        """Internal method to validate config and setup provider"""
        self.validate_config()
        self._setup_client()
    
    @abstractmethod
    def validate_config(self) -> bool:
        """
        Validate the configuration for this provider
        
        Returns:
            bool: True if configuration is valid
            
        Raises:
            ValueError: If configuration is invalid
            ImportError: If required dependencies are missing
        """
        pass
    
    @abstractmethod
    def _setup_client(self):
        """Setup the client/connection for this provider"""
        pass
    
    @abstractmethod
    def generate_response(self, prompt: str, **kwargs) -> str:
        """
        Generate response from the LLM provider
        
        Args:
            prompt: The input prompt
            **kwargs: Additional provider-specific parameters
            
        Returns:
            str: Generated response
            
        Raises:
            RuntimeError: If API call fails
        """
        pass
    
    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get information about this provider instance
        
        Returns:
            dict: Provider information
        """
        return {
            'provider_type': self.__class__.__name__,
            'config_keys': list(self.config.keys()),
            'is_configured': self._is_properly_configured()
        }
    
    def _is_properly_configured(self) -> bool:
        """Check if provider is properly configured"""
        try:
            self.validate_config()
            return True
        except (ValueError, ImportError):
            return False
    
    def supports_streaming(self) -> bool:
        """
        Check if provider supports streaming responses
        
        Returns:
            bool: True if streaming is supported
        """
        return hasattr(self, 'generate_response_stream')
    
    def get_model_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the current model
        
        Returns:
            dict or None: Model information if available
        """
        model = self.config.get('model')
        if model:
            return {
                'model_name': model,
                'provider': self.__class__.__name__
            }
        return None


class ProviderError(Exception):
    """Base exception for provider errors"""
    pass


class ConfigurationError(ProviderError):
    """Raised when provider configuration is invalid"""
    pass


class APIError(ProviderError):
    """Raised when API call fails"""
    pass


class AuthenticationError(APIError):
    """Raised when authentication fails"""
    pass


class RateLimitError(APIError):
    """Raised when rate limit is exceeded"""
    pass