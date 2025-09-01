"""
LLM Providers module

This module contains all the LLM provider implementations and manages
provider registration and discovery.
"""

from .base import BaseLLMProvider
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .ollama_provider import OllamaProvider
from .custom_provider import CustomAPIProvider

# Provider registry - maps provider names to their classes
PROVIDER_REGISTRY = {
    'openai': OpenAIProvider,
    'anthropic': AnthropicProvider,
    'claude': AnthropicProvider,  # Alias for anthropic
    'ollama': OllamaProvider,
    'custom': CustomAPIProvider,
}

# Optional providers that require additional dependencies
OPTIONAL_PROVIDERS = {}

# Try to import optional providers
try:
    from .gemini_provider import GeminiProvider
    OPTIONAL_PROVIDERS['gemini'] = GeminiProvider
    OPTIONAL_PROVIDERS['google'] = GeminiProvider  # Alias
except ImportError:
    pass

# try:
#     from .cohere_provider import CohereProvider
#     OPTIONAL_PROVIDERS['cohere'] = CohereProvider
# except ImportError:
#     pass

# try:
#     from .huggingface_provider import HuggingFaceProvider
#     OPTIONAL_PROVIDERS['huggingface'] = HuggingFaceProvider
#     OPTIONAL_PROVIDERS['hf'] = HuggingFaceProvider  # Alias
# except ImportError:
#     pass

# Merge optional providers into main registry
PROVIDER_REGISTRY.update(OPTIONAL_PROVIDERS)


def get_provider_class(provider_type: str):
    """
    Get provider class by name
    
    Args:
        provider_type: Name of the provider (case-insensitive)
        
    Returns:
        Provider class
        
    Raises:
        ValueError: If provider is not found
    """
    provider_type = provider_type.lower()
    
    if provider_type not in PROVIDER_REGISTRY:
        available = list(PROVIDER_REGISTRY.keys())
        raise ValueError(f"Unsupported provider type: {provider_type}. "
                        f"Available providers: {available}")
    
    return PROVIDER_REGISTRY[provider_type]


def get_available_providers():
    """
    Get list of available providers
    
    Returns:
        dict: Dictionary with provider info including availability
    """
    providers_info = {}
    
    for name, provider_class in PROVIDER_REGISTRY.items():
        try:
            # Try to instantiate with dummy config to check if dependencies are available
            is_available = True
            missing_deps = []
            
            # Check specific dependencies for each provider
            if name in ['openai']:
                try:
                    import openai
                except ImportError:
                    is_available = False
                    missing_deps.append('openai')
            
            elif name in ['anthropic', 'claude']:
                try:
                    import anthropic
                except ImportError:
                    is_available = False
                    missing_deps.append('anthropic')
            
            elif name in ['gemini', 'google']:
                try:
                    import google.genai
                except ImportError:
                    is_available = False
                    missing_deps.append('google-generativeai')
            
            # elif name in ['cohere']:
            #     try:
            #         import cohere
            #     except ImportError:
            #         is_available = False
            #         missing_deps.append('cohere')
            
            # elif name in ['huggingface', 'hf']:
            #     try:
            #         import transformers
            #     except ImportError:
            #         is_available = False
            #         missing_deps.append('transformers')
            
            providers_info[name] = {
                'class': provider_class.__name__,
                'available': is_available,
                'missing_dependencies': missing_deps,
                'module': provider_class.__module__
            }
            
        except Exception as e:
            providers_info[name] = {
                'class': provider_class.__name__,
                'available': False,
                'error': str(e),
                'module': provider_class.__module__
            }
    
    return providers_info


def register_provider(name: str, provider_class):
    """
    Register a custom provider
    
    Args:
        name: Provider name
        provider_class: Provider class (must inherit from BaseLLMProvider)
    """
    if not issubclass(provider_class, BaseLLMProvider):
        raise ValueError("Provider class must inherit from BaseLLMProvider")
    
    PROVIDER_REGISTRY[name.lower()] = provider_class


__all__ = [
    'BaseLLMProvider',
    'OpenAIProvider', 
    'AnthropicProvider',
    'OllamaProvider',
    'CustomAPIProvider',
    'PROVIDER_REGISTRY',
    'get_provider_class',
    'get_available_providers',
    'register_provider'
]