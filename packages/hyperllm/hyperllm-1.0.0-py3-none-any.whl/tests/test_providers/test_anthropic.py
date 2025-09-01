import unittest
from unittest.mock import patch, MagicMock
import os

from hyperllm.providers.anthropic_provider import AnthropicProvider
from hyperllm.providers.base import ConfigurationError, APIError


class TestAnthropicProvider(unittest.TestCase):
    
    @patch('hyperllm.providers.anthropic_provider.anthropic')
    def test_valid_configuration(self, mock_anthropic):
        """Test valid Anthropic configuration"""
        provider = AnthropicProvider(api_key='test-key')
        self.assertTrue(provider.validate_config())
    
    @patch('hyperllm.providers.anthropic_provider.anthropic', None)
    def test_missing_anthropic_library(self):
        """Test error when Anthropic library is missing"""
        with self.assertRaises(ImportError):
            AnthropicProvider(api_key='test-key')
    
    @patch('hyperllm.providers.anthropic_provider.anthropic')
    def test_generate_response(self, mock_anthropic):
        """Test response generation"""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content[0].type = "text"
        mock_response.content[0].text = "Test response"
        mock_client.messages.create.return_value = mock_response
        
        mock_anthropic.Anthropic.return_value = mock_client
        
        provider = AnthropicProvider(api_key='test-key')
        response = provider.generate_response("Test prompt")
        
        self.assertEqual(response, "Test response")
