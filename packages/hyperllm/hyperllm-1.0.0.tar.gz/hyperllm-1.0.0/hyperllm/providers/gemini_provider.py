import os
from .base import BaseLLMProvider, ConfigurationError, APIError

try:
    from google import genai
except ImportError:
    genai = None


class GeminiProvider(BaseLLMProvider):
    """Google Gemini provider"""
    
    def validate_config(self) -> bool:
        if genai is None:
            raise ImportError("Google GenerativeAI library not installed. Run: pip install google-genai")
        
        self.api_key = self.config.get('api_key') or os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
        
        if not self.api_key:
            raise ConfigurationError("Gemini API key is required")
        
        self.model = self.config.get('model', 'gemini-pro')
        self.temperature = self.config.get('temperature', 0.7)
        self.max_tokens = self.config.get('max_output_tokens', 1000)

        return True
    
    def _setup_client(self):
        """Setup Gemini client"""
        if genai:
            self.client = genai.Client(api_key=self.api_key)
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response from Google Gemini"""
        try:
            # Override defaults with kwargs
            temperature = kwargs.get('temperature', self.temperature)
            max_tokens = kwargs.get('max_output_tokens', self.max_tokens)
            thinking_budget = kwargs.get('thinking_budget', -1)
            include_thoughts = kwargs.get('include_thoughts', False)
            response_mime_type = kwargs.get('response_mime_type', None)
            contents = kwargs.get('contents', [])
            
            if genai is None:
                raise ImportError("Google GenerativeAI library not installed. Run: pip install google-genai")

            from google.genai import types

            _thinking_config=types.ThinkingConfig(
                thinking_budget=thinking_budget,
                include_thoughts=include_thoughts,
            )
            _config = types.GenerateContentConfig(
                thinking_config=_thinking_config,
                temperature=temperature,
                max_output_tokens=max_tokens,
                response_mime_type=response_mime_type,
            )

            prompt_content = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=prompt),
                    ]
                )
            ]

            contents = contents + prompt_content
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=_config,
            )
            if response and response.text:
                return response.text
            return response.model_dump_json()

        except Exception as e:
            raise APIError(f"Gemini API error: {str(e)}")
