import requests
from .base import BaseLLMProvider, ConfigurationError, APIError


class OllamaProvider(BaseLLMProvider):
    """Ollama local LLM provider"""
    
    def validate_config(self) -> bool:
        self.base_url = self.config.get('base_url', 'http://localhost:11434')
        self.model = self.config.get('model', 'llama2')
        self.temperature = self.config.get('temperature', 0.7)
        
        # Test connection to Ollama
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code != 200:
                raise ConfigurationError(f"Ollama server returned status {response.status_code}")
        except requests.RequestException as e:
            raise ConfigurationError(f"Cannot connect to Ollama at {self.base_url}: {e}")
        
        return True
    
    def _setup_client(self):
        """Setup is handled in validate_config for Ollama"""
        pass
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response from Ollama"""
        try:
            # Override defaults with kwargs
            temperature = kwargs.get('temperature', self.temperature)
            model = kwargs.get('model', self.model)
            
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            return response.json()['response']
        except requests.RequestException as e:
            raise APIError(f"Ollama API error: {str(e)}")

