import requests
from .base import BaseLLMProvider, ConfigurationError, APIError


class CustomAPIProvider(BaseLLMProvider):
    """Generic custom API provider for OpenAI-compatible APIs"""
    
    def validate_config(self) -> bool:
        self.base_url = self.config.get('base_url')
        if not self.base_url:
            raise ConfigurationError("base_url is required for CustomAPIProvider")
        
        self.api_key = self.config.get('api_key')
        self.model = self.config.get('model', 'gpt-3.5-turbo')
        self.headers = self.config.get('headers', {})
        self.temperature = self.config.get('temperature', 0.7)
        self.max_tokens = self.config.get('max_tokens', 1000)
        
        return True
    
    def _setup_client(self):
        """Setup is handled in validate_config for custom API"""
        pass
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response from custom API"""
        try:
            headers = {"Content-Type": "application/json"}
            headers.update(self.headers)
            
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            # Override defaults with kwargs
            temperature = kwargs.get('temperature', self.temperature)
            max_tokens = kwargs.get('max_tokens', self.max_tokens)
            model = kwargs.get('model', self.model)
            
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            if not self.base_url:
                raise ConfigurationError("base_url is not configured properly.")

            response = requests.post(
                f"{self.base_url.rstrip('/')}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            data = response.json()
            return data['choices'][0]['message']['content']
        except requests.RequestException as e:
            raise APIError(f"Custom API error: {str(e)}")
