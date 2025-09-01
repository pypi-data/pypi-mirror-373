"""Custom exceptions for Hyper LLM"""


class HyperLLMError(Exception):
    """Base exception for Hyper LLM"""
    pass


class ProviderError(HyperLLMError):
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


class CacheError(HyperLLMError):
    """Raised when cache operations fail"""
    pass


class InteractiveModeError(HyperLLMError):
    """Raised when interactive mode fails"""
    pass
