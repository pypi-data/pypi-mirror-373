import json
import hashlib
import os
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime


class CacheManager:
    """Manages caching of LLM responses"""
    
    def __init__(self, cache_dir: Optional[str] = None):
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = Path.home() / '.hyperllm_cache'
        
        self.initialize_cache()
    
    def initialize_cache(self):
        """Initialize the cache directory and index"""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Create cache index file
        index_file = self.cache_dir / 'cache_index.json'
        if not index_file.exists():
            self._save_index({})
    
    def _get_cache_path(self, prompt: str) -> Path:
        """Generate cache file path from prompt hash"""
        prompt_hash = hashlib.sha256(prompt.encode('utf-8')).hexdigest()
        return self.cache_dir / f"{prompt_hash}.json"
    
    def _load_index(self) -> Dict[str, Any]:
        """Load cache index"""
        index_file = self.cache_dir / 'cache_index.json'
        try:
            return json.loads(index_file.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _save_index(self, index: Dict[str, Any]):
        """Save cache index"""
        index_file = self.cache_dir / 'cache_index.json'
        index_file.write_text(json.dumps(index, indent=2), encoding='utf-8')
    
    def save(self, prompt: str, response: str, metadata: Optional[Dict] = None):
        """Save response to cache"""
        cache_path = self._get_cache_path(prompt)
        
        cache_data = {
            'prompt': prompt,
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        cache_path.write_text(json.dumps(cache_data, indent=2), encoding='utf-8')
        
        # Update index
        index = self._load_index()
        prompt_hash = hashlib.sha256(prompt.encode('utf-8')).hexdigest()
        index[prompt_hash] = {
            'timestamp': cache_data['timestamp'],
            'file': cache_path.name
        }
        self._save_index(index)
    
    def load(self, prompt: str) -> Optional[str]:
        """Load response from cache"""
        cache_path = self._get_cache_path(prompt)
        
        if cache_path.exists():
            try:
                cache_data = json.loads(cache_path.read_text(encoding='utf-8'))
                return cache_data.get('response')
            except (json.JSONDecodeError, KeyError):
                # Invalid cache file, remove it
                cache_path.unlink(missing_ok=True)
        
        return None
    
    def clear(self):
        """Clear all cached responses"""
        import shutil
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            self.initialize_cache()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.cache_dir.exists():
            return {'total_entries': 0, 'cache_size': 0, 'cache_dir': str(self.cache_dir)}
        
        cache_files = list(self.cache_dir.glob('*.json'))
        cache_files = [f for f in cache_files if f.name != 'cache_index.json']
        
        total_size = sum(f.stat().st_size for f in cache_files)
        
        return {
            'total_entries': len(cache_files),
            'cache_size': total_size,
            'cache_dir': str(self.cache_dir)
        }