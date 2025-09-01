"""Provider comparison examples"""

import os
from hyperllm import HyperLLM


def compare_providers():
    """Compare responses from different providers"""
    print("=== Provider Comparison Example ===")
    
    interface = HyperLLM()
    test_prompt = "Explain the concept of recursion with a simple example."
    
    # Provider configurations
    providers = {
        'OpenAI GPT-3.5': ('openai', {
            'api_key': os.environ.get('OPENAI_API_KEY', 'demo-key'),
            'model': 'gpt-3.5-turbo',
            'temperature': 0.7
        }),
        'Anthropic Claude': ('anthropic', {
            'api_key': os.environ.get('ANTHROPIC_API_KEY', 'demo-key'),
            'model': 'claude-3-sonnet-20240229'
        }),
        'Ollama Llama2': ('ollama', {
            'model': 'llama2',
            'base_url': 'http://localhost:11434'
        }),
        'Custom API': ('custom', {
            'base_url': 'https://api.example.com',
            'api_key': 'demo-key',
            'model': 'custom-model'
        })
    }
    
    results = {}
    
    print(f"Testing prompt: {test_prompt}")
    print("=" * 80)
    
    for name, (provider_type, config) in providers.items():
        print(f"\n--- Testing {name} ---")
        
        try:
            interface.set_llm(provider_type, **config)
            
            # For demo purposes, simulate responses instead of real API calls
            simulated_responses = {
                'OpenAI GPT-3.5': "Recursion is when a function calls itself. Example: factorial(n) = n * factorial(n-1).",
                'Anthropic Claude': "Recursion occurs when a function invokes itself. Consider calculating factorial: factorial(5) calls factorial(4), which calls factorial(3), etc.",
                'Ollama Llama2': "Recursion is a programming technique where a function calls itself. A classic example is the Fibonacci sequence.",
                'Custom API': "Recursion: A function calling itself. Example: def countdown(n): print(n); countdown(n-1) if n > 0."
            }
            
            # In real usage: response = interface.get_response(test_prompt)
            response = simulated_responses.get(name, f"Simulated response from {name}")
            results[name] = response
            
            # Cache the simulated response
            interface.save_to_cache(f"{name}: {test_prompt}", response)
            
            print(f"✅ {name}: {len(response)} characters")
            print(f"Preview: {response[:100]}...")
            
        except Exception as e:
            print(f"❌ {name} failed: {e}")
            results[name] = f"Error: {e}"
    
    # Display comparison
    print("\n" + "=" * 80)
    print("FULL COMPARISON")
    print("=" * 80)
    
    for name, response in results.items():
        print(f"\n--- {name} ---")
        print(response)
        print("-" * 50)
    
    # Show cache stats
    stats = interface.get_cache_stats()
    print(f"\n📊 Cache Statistics:")
    print(f"- Total entries: {stats['total_entries']}")
    print(f"- Cache size: {stats['cache_size']} bytes")


if __name__ == "__main__":
    compare_providers()
