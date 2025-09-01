import unittest
import tempfile
import os
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

from hyperllm import HyperLLM, create_interface
from hyperllm.providers.base import BaseLLMProvider
from hyperllm.providers import register_provider


class MockProvider(BaseLLMProvider):
    """Mock provider for testing"""
    
    def validate_config(self):
        return True
    
    def _setup_client(self):
        pass
    
    def generate_response(self, prompt, **kwargs):
        return f"Mock response: {prompt}"


class TestHyperLLM(unittest.TestCase):
    
    def setUp(self):
        register_provider('mock', MockProvider)
        self.temp_dir = tempfile.mkdtemp()
        self.interface = HyperLLM(cache_dir=self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_cache_initialization(self):
        """Test cache directory creation"""
        self.assertTrue(self.interface.cache_dir.exists())
        index_file = self.interface.cache_dir / 'cache_index.json'
        self.assertTrue(index_file.exists())
    
    def test_cache_operations(self):
        """Test cache save and load"""
        prompt = "Test prompt"
        response = "Test response"
        
        # Save and load
        self.interface.save_to_cache(prompt, response)
        cached = self.interface.load_from_cache(prompt)
        
        self.assertEqual(cached, response)
    
    def test_cache_miss(self):
        """Test cache miss returns None"""
        result = self.interface.load_from_cache("Non-existent prompt")
        self.assertIsNone(result)
    
    def test_set_llm_mock_provider(self):
        """Test setting a mock provider"""
        with patch('hyperllm.providers.get_provider_class', return_value=MockProvider):
            self.interface.set_llm('mock')
            self.assertIsInstance(self.interface.provider, MockProvider)
    
    def test_get_response_with_cache(self):
        """Test get_response with caching"""
        with patch('hyperllm.providers.get_provider_class', return_value=MockProvider):
            self.interface.set_llm('mock')
            
            prompt = "Test prompt"
            
            # First call
            response1 = self.interface.get_response(prompt)
            self.assertIn("Mock response", response1)
            
            # Second call should use cache
            response2 = self.interface.get_response(prompt)
            self.assertEqual(response1, response2)
    
    def test_get_response_no_cache(self):
        """Test get_response without caching"""
        with patch('hyperllm.providers.get_provider_class', return_value=MockProvider):
            self.interface.set_llm('mock')
            
            response = self.interface.get_response("Test", use_cache=False)
            self.assertIn("Mock response", response)
    
    def test_clear_cache(self):
        """Test cache clearing"""
        # Add something to cache
        self.interface.save_to_cache("test", "response")
        self.assertIsNotNone(self.interface.load_from_cache("test"))
        
        # Clear cache
        self.interface.clear_cache()
        
        # Should be gone
        self.assertIsNone(self.interface.load_from_cache("test"))
    
    def test_cache_stats(self):
        """Test cache statistics"""
        # Initially empty
        stats = self.interface.get_cache_stats()
        self.assertEqual(stats['total_entries'], 0)
        
        # Add entries
        self.interface.save_to_cache("test1", "response1")
        self.interface.save_to_cache("test2", "response2")
        
        stats = self.interface.get_cache_stats()
        self.assertEqual(stats['total_entries'], 2)
        self.assertGreater(stats['cache_size'], 0)
    
    @patch.dict(os.environ, {'LLM_INTERACTIVE_MODE': 'true'})
    def test_interactive_mode(self):
        """Test interactive mode detection"""
        interface = HyperLLM(cache_dir=self.temp_dir)
        self.assertTrue(interface.interactive_mode.is_interactive_mode())
    
    def test_create_interface_convenience_function(self):
        """Test convenience function"""
        with patch('hyperllm.providers.get_provider_class', return_value=MockProvider):
            interface = create_interface('mock', cache_dir=self.temp_dir)
            self.assertIsInstance(interface, HyperLLM)
            self.assertIsInstance(interface.provider, MockProvider)
