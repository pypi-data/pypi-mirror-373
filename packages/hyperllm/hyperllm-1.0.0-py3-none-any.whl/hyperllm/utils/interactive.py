import os
import sys
from pathlib import Path

try:
    import pyperclip
except ImportError:
    pyperclip = None


class InteractiveMode:
    """Handles interactive mode functionality"""
    
    def __init__(self):
        self.prompt_output_file = os.environ.get("PROMPT_OUTPUT_FILE", None)
        self.response_input_file = os.environ.get("RESPONSE_INPUT_FILE", None)
        self.is_enabled = os.environ.get('LLM_INTERACTIVE_MODE', 'false').lower() in ('true', '1')
    
    def is_interactive_mode(self) -> bool:
        """Check if interactive mode is enabled"""
        return self.is_enabled
    
    def handle_prompt_output(self, prompt: str):
        """Handle prompt output (clipboard and/or file)"""
        print("\n--- INTERACTIVE MODE: Awaiting Manual Input ---")
        
        # Copy to clipboard if available
        if pyperclip:
            try:
                pyperclip.copy(prompt)
                print("✅ Prompt copied to clipboard")
            except Exception as e:
                print(f"⚠️  Clipboard copy failed: {e}", file=sys.stderr)
        else:
            print("⚠️  Clipboard unavailable. Install with: pip install pyperclip")
        
        # Write to file if specified
        if self.prompt_output_file:
            prompt_file = Path(self.prompt_output_file)
            prompt_file.write_text(prompt, encoding='utf-8')
            print(f"📝 Prompt written to: {prompt_file.resolve()}")
        else:
            print("\n--- PROMPT ---")
            print(prompt)
            print("--- END PROMPT ---\n")
    
    def get_user_response(self) -> str:
        """Get response from user (file or stdin)"""
        if self.response_input_file:
            response_file = Path(self.response_input_file)
            try:
                print(f"📖 Reading response from: {response_file.resolve()}")
                return response_file.read_text(encoding='utf-8').strip()
            except FileNotFoundError:
                print(f"❌ Response file not found: {response_file.resolve()}", file=sys.stderr)
                sys.exit(1)
        elif sys.stdout.isatty():
            print("💬 Paste the LLM response below (Ctrl+D/Ctrl+Z when done):")
            try:
                return sys.stdin.read().strip()
            except KeyboardInterrupt:
                print("\n❌ Interrupted by user")
                sys.exit(1)
        else:
            print("❌ Non-interactive terminal. Set RESPONSE_INPUT_FILE env var.", file=sys.stderr)
            sys.exit(1)
    
    def handle_interactive_request(self, prompt: str) -> str:
        """Handle complete interactive request workflow"""
        self.handle_prompt_output(prompt)
        response = self.get_user_response()
        print("✅ Response received and will be cached")
        return response

