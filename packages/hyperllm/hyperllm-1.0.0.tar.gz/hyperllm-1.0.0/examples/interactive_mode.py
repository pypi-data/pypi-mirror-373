"""Interactive mode examples"""

import os
from hyperllm import HyperLLM

def basic_interactive_example():
    """Basic interactive mode example"""
    print("=== Interactive Mode Example ===")
    print("This example demonstrates interactive mode for cost-free development")
    print("Set LLM_INTERACTIVE_MODE=true to enable")
    print()
    
    # Enable interactive mode
    os.environ['LLM_INTERACTIVE_MODE'] = 'true'
    
    interface = HyperLLM()
    interface.set_llm('openai')  # Provider doesn't matter in interactive mode
    
    prompts = [
        "What is the difference between Python and Java?",
        "Explain REST API design principles",
        "How does database indexing work?"
    ]
    
    print("Interactive mode enabled. For each prompt:")
    print("1. Prompt will be copied to clipboard")
    print("2. Paste it into your favorite Hyper LLM")
    print("3. Copy the response and paste it back here")
    print("4. Response gets cached for future use")
    print()
    
    for i, prompt in enumerate(prompts[:1]):  # Just do one for demo
        print(f"--- Processing prompt {i+1} ---")
        print(f"Prompt: {prompt}")
        
        try:
            # In real usage, this would wait for user input
            # For demo, we'll simulate a response
            response = f"Simulated response for: {prompt}"
            interface.save_to_cache(prompt, response)
            print(f"✅ Response cached: {response[:50]}...")
            
        except KeyboardInterrupt:
            print("Demo interrupted")
            break
    
    print("\n✅ All responses are now cached and available for production!")


def file_based_interactive_example():
    """File-based interactive mode"""
    print("\n=== File-Based Interactive Mode ===")
    
    # Set up file-based interactive mode
    prompt_file = "/tmp/llm_prompt.txt"
    response_file = "/tmp/llm_response.txt"
    
    os.environ['LLM_INTERACTIVE_MODE'] = 'true'
    os.environ['PROMPT_OUTPUT_FILE'] = prompt_file
    os.environ['RESPONSE_INPUT_FILE'] = response_file
    
    # Create a demo response file
    with open(response_file, 'w') as f:
        f.write("This is a simulated response from file-based interactive mode.")
    
    interface = HyperLLM()
    interface.set_llm('openai')
    
    print(f"Prompt will be written to: {prompt_file}")
    print(f"Response will be read from: {response_file}")
    print()
    
    try:
        prompt = "What are the benefits of microservices?"
        
        # Simulate the file workflow
        with open(prompt_file, 'w') as f:
            f.write(prompt)
        print(f"✅ Prompt written to {prompt_file}")
        
        with open(response_file, 'r') as f:
            response = f.read().strip()
        print(f"✅ Response read from {response_file}")
        
        # Cache the response
        interface.save_to_cache(prompt, response)
        print("✅ Response cached for future use")
        
    except Exception as e:
        print(f"File-based example error: {e}")


if __name__ == "__main__":
    print("Interactive Mode Examples")
    print("=" * 50)
    basic_interactive_example()
    file_based_interactive_example()

