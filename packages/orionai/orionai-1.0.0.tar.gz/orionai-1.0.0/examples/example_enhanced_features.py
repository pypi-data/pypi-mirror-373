"""
AIPython Enhanced Features Example
==================================
This example demonstrates the enhanced AIPython features including:
- Multi-provider LLM support (Google, OpenAI, Anthropic)
- Permission system for package installation
- Rich UI for better terminal output
- Environment detection (Jupyter vs VSCode)
- Advanced logging and error handling
"""

import os
import sys
sys.path.append('..')
from orionai.python import AIPython

# Set your API keys in environment variables
# os.environ['GOOGLE_API_KEY'] = 'your_google_api_key_here'
# os.environ['OPENAI_API_KEY'] = 'your_openai_api_key_here'
# os.environ['ANTHROPIC_API_KEY'] = 'your_anthropic_api_key_here'

def test_google_provider():
    """Test Google Gemini provider."""
    chat = AIPython(
        provider="google",
        model="gemini-1.5-pro",
        ask_permission=True,  # Enable permission system
        verbose=True
    )
    
    # Test basic functionality
    response = chat.ask("Calculate the sum of squares from 1 to 10")
    
    # Test with package installation (will ask permission in interactive mode)
    response = chat.ask("Create a simple machine learning model with sklearn")
    
    return chat

def test_environment_detection():
    """Test environment detection and logging."""
    chat = AIPython(provider="google", ask_permission=False)
    
    # Environment detection should be automatic
    print(f"Detected environment: {chat.environment}")
    print(f"Using rich UI: {chat.use_rich}")
    print(f"Provider: {chat.provider_name}")
    print(f"Model: {chat.model_name}")
    
    return chat

def test_permission_system():
    """Test the permission system for package installation."""
    chat = AIPython(
        provider="google",
        ask_permission=True,  # Enable permission asking
        verbose=True
    )
    
    # This should ask for permission before installing packages
    response = chat.ask("Use scipy to solve a differential equation")
    
    return chat

def test_multi_provider_support():
    """Test multiple LLM providers (if API keys are available)."""
    providers_to_test = []
    
    # Test Google (if API key available)
    if os.environ.get('GOOGLE_API_KEY'):
        providers_to_test.append(('google', 'gemini-1.5-pro'))
    
    # Test OpenAI (if API key available)
    if os.environ.get('OPENAI_API_KEY'):
        providers_to_test.append(('openai', 'gpt-4'))
    
    # Test Anthropic (if API key available)
    if os.environ.get('ANTHROPIC_API_KEY'):
        providers_to_test.append(('anthropic', 'claude-3-sonnet-20240229'))
    
    results = {}
    for provider, model in providers_to_test:
        try:
            chat = AIPython(
                provider=provider,
                model=model,
                ask_permission=False,
                verbose=True
            )
            
            response = chat.ask("Calculate fibonacci numbers up to 50")
            results[f"{provider}:{model}"] = "SUCCESS"
            
        except Exception as e:
            results[f"{provider}:{model}"] = f"FAILED: {e}"
    
    return results

if __name__ == "__main__":
    print("=== Testing Enhanced AIPython Features ===\n")
    
    print("1. Testing Google Provider...")
    google_chat = test_google_provider()
    print(f"Google test result: {repr(google_chat)}\n")
    
    print("2. Testing Environment Detection...")
    env_chat = test_environment_detection()
    print()
    
    print("3. Testing Multi-Provider Support...")
    provider_results = test_multi_provider_support()
    for provider, result in provider_results.items():
        print(f"  {provider}: {result}")
    print()
    
    print("4. Testing Permission System (Interactive)...")
    print("   Note: This will ask for permission to install packages")
    # Uncomment to test interactively:
    # permission_chat = test_permission_system()
    
    print("=== All Tests Completed ===")
