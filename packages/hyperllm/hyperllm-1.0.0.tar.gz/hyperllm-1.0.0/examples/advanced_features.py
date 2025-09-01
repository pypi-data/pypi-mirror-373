"""Advanced features and usage patterns"""

import os
from hyperllm import HyperLLM
from hyperllm.providers import register_provider, BaseLLMProvider


class MockProvider(BaseLLMProvider):
    """Mock provider for testing"""
    
    def validate_config(self):
        return True
    
    def _setup_client(self):
        pass
    
    def generate_response(self, prompt, **kwargs):
        return f"Mock response for: {prompt[:50]}..."


def custom_provider_example():
    """Example of registering a custom provider"""
    print("=== Custom Provider Registration ===")
    
    # Register the mock provider
    register_provider('mock', MockProvider)
    
    interface = HyperLLM()
    interface.set_llm('mock')
    
    response = interface.get_response("Test custom provider")
    print(f"Custom provider response: {response}")
    print()


def advanced_caching_example():
    """Advanced caching patterns"""
    print("=== Advanced Caching ===")
    
    interface = HyperLLM(cache_dir="/tmp/custom_llm_cache")
    
    # Different cache strategies
    prompts = [
        "What is Python?",
        "What is machine learning?",  
        "Explain neural networks"
    ]
    
    # First pass - populate cache
    for prompt in prompts:
        # Simulate responses
        response = f"Cached response for: {prompt}"
        interface.save_to_cache(prompt, response, {'strategy': 'batch_load'})
    
    print(f"Populated cache with {len(prompts)} entries")
    
    # Second pass - use cache
    for prompt in prompts:
        response = interface.load_from_cache(prompt)
        print(f"From cache: {response}")
    
    stats = interface.get_cache_stats()
    print(f"\nCache stats: {stats['total_entries']} entries, {stats['cache_size']} bytes")
    print()


def production_patterns_example():
    """Production usage patterns"""
    print("=== Production Patterns ===")
    
    # Pattern 1: Fallback providers
    def try_providers(interface, prompt, providers):
        for provider_name, config in providers:
            try:
                interface.set_llm(provider_name, **config)
                return interface.get_response(prompt)
            except Exception as e:
                print(f"Provider {provider_name} failed: {e}")
                continue
        raise Exception("All providers failed")
    
    interface = HyperLLM()
    fallback_providers = [
        ('openai', {'api_key': 'primary-key', 'model': 'gpt-4'}),
        ('anthropic', {'api_key': 'backup-key', 'model': 'claude-3-sonnet-20240229'}),
        ('ollama', {'model': 'llama2'})  # Local fallback
    ]
    
    try:
        # Simulate fallback (will fail on first two, succeed on mock)
        register_provider('working_mock', MockProvider)
        working_providers = [('working_mock', {})]
        
        response = try_providers(interface, "Production test prompt", working_providers)
        print(f"Fallback successful: {response}")
        
    except Exception as e:
        print(f"All providers failed: {e}")
    
    print()


def batch_processing_example():
    """Batch processing with caching"""
    print("=== Batch Processing ===")
    
    interface = HyperLLM()
    interface.set_llm('mock', provider_class=MockProvider)
    
    # Simulate batch job
    batch_prompts = [
        "Analyze sentiment: 'Great product!'",
        "Analyze sentiment: 'Poor quality'", 
        "Analyze sentiment: 'Average experience'",
        "Summarize: 'Long article text here...'",
        "Translate to Spanish: 'Hello world'"
    ]
    
    print(f"Processing {len(batch_prompts)} prompts...")
    
    results = []
    for i, prompt in enumerate(batch_prompts):
        # Check cache first
        cached = interface.load_from_cache(prompt)
        if cached:
            print(f"  {i+1}. Cache hit: {prompt[:30]}...")
            results.append(cached)
        else:
            print(f"  {i+1}. Processing: {prompt[:30]}...")
            response = interface.get_response(prompt, use_cache=True)
            results.append(response)
    
    print(f"\nBatch processing complete: {len(results)} results")
    stats = interface.get_cache_stats()
    print(f"Cache now has {stats['total_entries']} entries")


if __name__ == "__main__":
    custom_provider_example()
    advanced_caching_example() 
    production_patterns_example()
    batch_processing_example()
