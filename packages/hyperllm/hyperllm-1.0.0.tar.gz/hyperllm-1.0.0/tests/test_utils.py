import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch

from hyperllm.utils.cache import CacheManager
from hyperllm.utils.interactive import InteractiveMode


class TestCacheManager(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.cache_manager = CacheManager(self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_cache_initialization(self):
        """Test cache manager initialization"""
        self.assertTrue(Path(self.temp_dir).exists())
        index_file = Path(self.temp_dir) / 'cache_index.json'
        self.assertTrue(index_file.exists())
    
    def test_save_and_load(self):
        """Test saving and loading from cache"""
        prompt = "Test prompt"
        response = "Test response"
        
        self.cache_manager.save(prompt, response)
        loaded = self.cache_manager.load(prompt)
        
        self.assertEqual(loaded, response)
    
    def test_cache_miss(self):
        """Test cache miss returns None"""
        result = self.cache_manager.load("Non-existent")
        self.assertIsNone(result)
    
    def test_get_stats(self):
        """Test cache statistics"""
        # Initially empty
        stats = self.cache_manager.get_stats()
        self.assertEqual(stats['total_entries'], 0)
        
        # Add entries
        self.cache_manager.save("test1", "response1")
        self.cache_manager.save("test2", "response2")
        
        stats = self.cache_manager.get_stats()
        self.assertEqual(stats['total_entries'], 2)


class TestInteractiveMode(unittest.TestCase):
    
    def test_interactive_mode_detection(self):
        """Test interactive mode detection"""
        import os
        
        # Default should be False
        interactive = InteractiveMode()
        self.assertFalse(interactive.is_interactive_mode())
        
        # Set environment variable
        with patch.dict(os.environ, {'LLM_INTERACTIVE_MODE': 'true'}):
            interactive = InteractiveMode()
            self.assertTrue(interactive.is_interactive_mode())


if __name__ == '__main__':
    unittest.main()
