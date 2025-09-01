import os
from typing import Optional
from .base import BaseLLMProvider, ConfigurationError, APIError

# import openai
try:
    import openai
except ImportError:
    openai = None


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT provider"""
    
    def validate_config(self) -> bool:
        if openai is None:
            raise ImportError("OpenAI library not installed. Run: pip install openai")
        
        self.api_key = self.config.get('api_key') or os.environ.get('OPENAI_API_KEY')
        self.base_url = self.config.get('base_url')
        
        if not self.api_key and not self.base_url:
            raise ConfigurationError("OpenAI API key or custom base_url is required")
        
        self.model = self.config.get('model', 'gpt-3.5-turbo')
        self.temperature = self.config.get('temperature', 0.7)
        self.max_tokens = self.config.get('max_tokens', 1000)
        
        return True
    
    def _setup_client(self):
        """Setup OpenAI client"""
        client_kwargs = {}
        if self.api_key:
            client_kwargs['api_key'] = self.api_key
        if self.base_url:
            client_kwargs['base_url'] = self.base_url
            
        if openai:
            self.client = openai.OpenAI(**client_kwargs)
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response from OpenAI"""
        try:
            # Override defaults with kwargs
            temperature = kwargs.get('temperature', self.temperature)
            max_tokens = kwargs.get('max_tokens', self.max_tokens)
            model = kwargs.get('model', self.model)
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            if response and response.choices and response.choices[0].message and response.choices[0].message.content:
                return response.choices[0].message.content
            return response.choices[0].to_json()
        except Exception as e:
            raise APIError(f"OpenAI API error: {str(e)}")
