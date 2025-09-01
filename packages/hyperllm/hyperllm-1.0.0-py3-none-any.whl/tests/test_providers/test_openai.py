import unittest
from unittest.mock import patch, MagicMock
import os

from hyperllm.providers.openai_provider import OpenAIProvider
from hyperllm.providers.base import ConfigurationError, APIError


class TestOpenAIProvider(unittest.TestCase):
    
    @patch('hyperllm.providers.openai_provider.openai')
    def test_valid_configuration(self, mock_openai):
        """Test valid OpenAI configuration"""
        provider = OpenAIProvider(api_key='test-key', model='gpt-3.5-turbo')
        self.assertTrue(provider.validate_config())
        self.assertEqual(provider.model, 'gpt-3.5-turbo')
    
    @patch('hyperllm.providers.openai_provider.openai', None)
    def test_missing_openai_library(self):
        """Test error when OpenAI library is missing"""
        with self.assertRaises(ImportError):
            OpenAIProvider(api_key='test-key')
    
    @patch('hyperllm.providers.openai_provider.openai')
    def test_missing_api_key(self, mock_openai):
        """Test error when API key is missing"""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ConfigurationError):
                provider = OpenAIProvider()
                provider.validate_config()
    
    @patch('hyperllm.providers.openai_provider.openai')
    def test_generate_response(self, mock_openai):
        """Test response generation"""
        # Mock the client and response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_response
        
        mock_openai.OpenAI.return_value = mock_client
        
        provider = OpenAIProvider(api_key='test-key')
        response = provider.generate_response("Test prompt")
        
        self.assertEqual(response, "Test response")
        mock_client.chat.completions.create.assert_called_once()
    
    @patch('hyperllm.providers.openai_provider.openai')
    def test_api_error_handling(self, mock_openai):
        """Test API error handling"""
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.OpenAI.return_value = mock_client
        
        provider = OpenAIProvider(api_key='test-key')
        
        with self.assertRaises(APIError):
            provider.generate_response("Test prompt")
