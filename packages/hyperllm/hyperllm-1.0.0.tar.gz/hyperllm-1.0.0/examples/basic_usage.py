"""Basic usage examples for Hyper LLM"""

import os
from hyperllm import HyperLLM, create_interface, get_available_providers


def show_available_providers():
    """Show which providers are available"""
    print("=== Available Providers ===")
    providers = get_available_providers()
    
    for name, info in providers.items():
        status = "✅ Available" if info['available'] else "❌ Missing dependencies"
        print(f"{name}: {status}")
        if not info['available'] and 'missing_dependencies' in info:
            deps = ', '.join(info['missing_dependencies'])
            print(f"   Install with: pip install {deps}")
    print()


def basic_openai_example():
    """Basic OpenAI usage example"""
    print("=== OpenAI Example ===")
    
    interface = HyperLLM()
    
    try:
        interface.set_llm('openai',
                          api_key=os.environ.get('OPENAI_API_KEY', 'your-api-key'),
                          model='gpt-3.5-turbo')
        
        prompt = "What is Python programming language?"
        print(f"Prompt: {prompt}")
        
        response = interface.get_response(prompt)
        print(f"Response: {response[:200]}...")
        
        # Second call uses cache
        response2 = interface.get_response(prompt)
        print("Second call used cache!")
        
    except Exception as e:
        print(f"OpenAI example failed: {e}")
    print()


def ollama_example():
    """Local Ollama example"""
    print("=== Ollama Example ===")
    
    try:
        interface = create_interface('ollama',
                                   model='llama2',
                                   temperature=0.5)
        
        response = interface.get_response("Explain machine learning in one sentence")
        print(f"Ollama Response: {response}")
        
    except Exception as e:
        print(f"Ollama example failed: {e}")
    print()


def cache_management_example():
    """Cache management example"""
    print("=== Cache Management ===")
    
    interface = HyperLLM()
    
    # Check initial stats
    stats = interface.get_cache_stats()
    print(f"Initial cache entries: {stats['total_entries']}")
    
    # Add some cached responses (simulate by saving directly to cache)
    interface.save_to_cache("What is AI?", "AI is artificial intelligence.")
    interface.save_to_cache("What is ML?", "ML is machine learning.")
    
    # Check updated stats
    stats = interface.get_cache_stats()
    print(f"After adding entries: {stats['total_entries']} entries, {stats['cache_size']} bytes")
    
    # Clear cache
    interface.clear_cache()
    stats = interface.get_cache_stats()
    print(f"After clearing: {stats['total_entries']} entries")
    print()


if __name__ == "__main__":
    show_available_providers()
    basic_openai_example()
    ollama_example()
    cache_management_example()

