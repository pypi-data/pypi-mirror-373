# import os
# from .base import BaseLLMProvider, ConfigurationError, APIError

# try:
#     import cohere
# except ImportError:
#     cohere = None


# class CohereProvider(BaseLLMProvider):
#     """Cohere provider"""
    
#     def validate_config(self) -> bool:
#         if cohere is None:
#             raise ImportError("Cohere library not installed. Run: pip install cohere")
        
#         self.api_key = self.config.get('api_key') or os.environ.get('COHERE_API_KEY')
        
#         if not self.api_key:
#             raise ConfigurationError("Cohere API key is required")
        
#         self.model = self.config.get('model', 'command')
#         self.temperature = self.config.get('temperature', 0.7)
#         self.max_tokens = self.config.get('max_tokens', 1000)
        
#         return True
    
#     def _setup_client(self):
#         """Setup Cohere client"""
#         self.client = cohere.Client(self.api_key)
    
#     def generate_response(self, prompt: str, **kwargs) -> str:
#         """Generate response from Cohere"""
#         try:
#             # Override defaults with kwargs
#             temperature = kwargs.get('temperature', self.temperature)
#             max_tokens = kwargs.get('max_tokens', self.max_tokens)
#             model = kwargs.get('model', self.model)
            
#             response = self.client.generate(
#                 prompt=prompt,
#                 model=model,
#                 temperature=temperature,
#                 max_tokens=max_tokens
#             )
#             return response.generations[0].text
#         except Exception as e:
#             raise APIError(f"Cohere API error: {str(e)}")
