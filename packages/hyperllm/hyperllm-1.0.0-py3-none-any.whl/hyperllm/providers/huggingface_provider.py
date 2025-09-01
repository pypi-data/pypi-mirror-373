# import os
# from .base import BaseLLMProvider, ConfigurationError, APIError

# try:
#     from transformers import pipeline
#     import torch
# except ImportError:
#     pipeline = None
#     torch = None


# class HuggingFaceProvider(BaseLLMProvider):
#     """HuggingFace Transformers provider for local models"""
    
#     def validate_config(self) -> bool:
#         if pipeline is None:
#             raise ImportError("Transformers library not installed. Run: pip install transformers torch")
        
#         self.model_name = self.config.get('model', 'microsoft/DialoGPT-medium')
#         self.device = self.config.get('device', 'auto')
#         self.max_length = self.config.get('max_length', 1000)
#         self.temperature = self.config.get('temperature', 0.7)
        
#         return True
    
#     def _setup_client(self):
#         """Setup HuggingFace pipeline"""
#         try:
#             device = -1 if self.device == 'cpu' else 0 if torch and torch.cuda.is_available() else -1
            
#             self.client = pipeline(
#                 'text-generation',
#                 model=self.model_name,
#                 device=device,
#                 return_full_text=False
#             )
#         except Exception as e:
#             raise ConfigurationError(f"Failed to load HuggingFace model: {e}")
    
#     def generate_response(self, prompt: str, **kwargs) -> str:
#         """Generate response from HuggingFace model"""
#         try:
#             # Override defaults with kwargs
#             max_length = kwargs.get('max_length', self.max_length)
#             temperature = kwargs.get('temperature', self.temperature)
            
#             response = self.client(
#                 prompt,
#                 max_length=max_length,
#                 temperature=temperature,
#                 do_sample=True,
#                 num_return_sequences=1
#             )
#             return response[0]['generated_text']
#         except Exception as e:
#             raise APIError(f"HuggingFace API error: {str(e)}")
