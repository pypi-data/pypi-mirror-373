import os
from typing import Optional
from .base import BaseLLMProvider, ConfigurationError, APIError

# import anthropic
try:
    import anthropic
except ImportError:
    anthropic = None


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude provider"""
    
    def validate_config(self) -> bool:
        if anthropic is None:
            raise ImportError("Anthropic library not installed. Run: pip install anthropic")
        
        self.api_key = self.config.get('api_key') or os.environ.get('ANTHROPIC_API_KEY')
        
        if not self.api_key:
            raise ConfigurationError("Anthropic API key is required")
        
        self.model = self.config.get('model', 'claude-3-sonnet-20240229')
        self.max_tokens = self.config.get('max_tokens', 1000)
        
        return True
    
    def _setup_client(self):
        """Setup Anthropic client"""
        if anthropic:
            self.client = anthropic.Anthropic(api_key=self.api_key)
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response from Anthropic Claude"""
        try:
            # Override defaults with kwargs
            max_tokens = kwargs.get('max_tokens', self.max_tokens)
            model = kwargs.get('model', self.model)
            
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            if response and response.content and response.content[0].type == 'text':
                return response.content[0].text
            print("Sending full response as fallback", response.content)
            return response.content[0].to_json()
        except Exception as e:
            raise APIError(f"Anthropic API error: {str(e)}")
