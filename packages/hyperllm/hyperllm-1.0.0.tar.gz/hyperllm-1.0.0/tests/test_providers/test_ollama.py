import unittest
from unittest.mock import patch, MagicMock
import requests

from hyperllm.providers.ollama_provider import OllamaProvider
from hyperllm.providers.base import ConfigurationError, APIError


class TestOllamaProvider(unittest.TestCase):
    
    @patch('requests.get')
    def test_valid_configuration(self, mock_get):
        """Test valid Ollama configuration"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        provider = OllamaProvider()
        self.assertTrue(provider.validate_config())
    
    @patch('requests.get')
    def test_connection_error(self, mock_get):
        """Test connection error handling"""
        mock_get.side_effect = requests.RequestException("Connection failed")
        
        with self.assertRaises(ConfigurationError):
            provider = OllamaProvider()
            provider.validate_config()

    @patch('requests.get')
    def get_provider_ollama(self, mock_get) -> OllamaProvider:
        """Test default configuration values"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        provider = OllamaProvider()
        return provider
 
    
    @patch('requests.post')
    def test_generate_response(self, mock_post):
        """Test response generation"""
        mock_response = MagicMock()
        mock_response.json.return_value = {'response': 'Test response'}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Skip validation for this test
        provider = self.get_provider_ollama()
        with patch.object(provider, 'validate_config', return_value=True):
            provider._validate_and_setup()
            response = provider.generate_response("Test prompt")
        
        self.assertEqual(response, "Test response")
