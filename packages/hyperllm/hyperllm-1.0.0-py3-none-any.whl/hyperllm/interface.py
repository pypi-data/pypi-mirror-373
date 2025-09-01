import os
from pathlib import Path
from typing import Optional

from .providers import get_provider_class
from .providers.base import BaseLLMProvider
from .utils.cache import CacheManager
from .utils.interactive import InteractiveMode
from .utils.exceptions import HyperLLMError


class HyperLLM:
    """Main interface for interacting with various LLM providers"""
    
    def __init__(self, cache_dir: Optional[str] = None):
        # Initialize cache manager
        self.cache_manager = CacheManager(cache_dir)
        
        # Initialize interactive mode handler
        self.interactive_mode = InteractiveMode()
        
        # LLM provider
        self.provider: Optional[BaseLLMProvider] = None
    
    @property
    def cache_dir(self):
        """For backward compatibility"""
        return self.cache_manager.cache_dir
    
    def set_llm(self, provider_type: str, **kwargs):
        """
        Set the LLM provider with configuration
        
        Args:
            provider_type: Type of LLM provider
            **kwargs: Provider-specific configuration options
        """
        provider_class = get_provider_class(provider_type)
        self.provider = provider_class(**kwargs)
        
        print(f"✅ LLM provider set to: {provider_type}")
    
    def get_cache_path(self, prompt: str) -> Path:
        """Get cache path for a prompt (backward compatibility)"""
        return self.cache_manager._get_cache_path(prompt)
    
    def save_to_cache(self, prompt: str, response: str, metadata: Optional[dict] = None):
        """Save response to cache"""
        self.cache_manager.save(prompt, response, metadata)
    
    def load_from_cache(self, prompt: str) -> Optional[str]:
        """Load response from cache"""
        return self.cache_manager.load(prompt)
    
    def handle_interactive_input(self, prompt: str) -> str:
        """Handle interactive mode input"""
        return self.interactive_mode.handle_interactive_request(prompt)
    
    def fetch_from_connected_llm(self, prompt: str, **kwargs) -> str:
        """Fetch response from the connected LLM provider"""
        if not self.provider:
            raise HyperLLMError("No LLM provider configured. Use set_llm() first.")
        
        return self.provider.generate_response(prompt, **kwargs)
    
    def get_response(self, prompt: str, use_cache: bool = True, **kwargs) -> str:
        """
        Get response from LLM with caching and interactive mode support
        
        Args:
            prompt: The input prompt
            use_cache: Whether to use caching
            **kwargs: Additional parameters passed to the provider
            
        Returns:
            The LLM response
        """
        # Check cache first if enabled
        if use_cache:
            cached_response = self.load_from_cache(prompt)
            if cached_response:
                print("💾 Cache HIT - Loading cached response")
                return cached_response
            
            print("🔍 Cache MISS - Generating new response")
        
        # Get response based on mode
        if self.interactive_mode.is_interactive_mode():
            response_text = self.handle_interactive_input(prompt)
        else:
            response_text = self.fetch_from_connected_llm(prompt, **kwargs)
        
        # Save to cache if enabled
        if use_cache:
            print("💾 Saving response to cache")
            self.save_to_cache(prompt, response_text, {'provider': self.provider.__class__.__name__ if self.provider else None})
        
        return response_text
    
    def clear_cache(self):
        """Clear all cached responses"""
        self.cache_manager.clear()
        print("🗑️  Cache cleared successfully")
    
    def get_cache_stats(self):
        """Get cache statistics"""
        return self.cache_manager.get_stats()
    
    def get_provider_info(self):
        """Get information about current provider"""
        if self.provider:
            return self.provider.get_provider_info()
        return None


def create_interface(provider_type: str, cache_dir: Optional[str] = None, **kwargs) -> HyperLLM:
    """
    Convenience function to create and configure HyperLLM
    
    Args:
        provider_type: LLM provider type
        cache_dir: Cache directory path
        **kwargs: Provider-specific configuration
    
    Returns:
        Configured HyperLLM instance
    """
    interface = HyperLLM(cache_dir=cache_dir)
    interface.set_llm(provider_type, **kwargs)
    return interface
