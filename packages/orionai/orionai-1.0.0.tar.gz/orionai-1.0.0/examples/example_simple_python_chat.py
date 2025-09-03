"""
SimplePythonChat Example
========================
Demonstrates the Python learning assistant features.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from orionai.python import SimplePythonChat, simple_python_chat

# Set your Google API key in environment variable
# os.environ['GOOGLE_API_KEY'] = 'your_api_key_here'

def demo_simple_python_chat():
    """Demonstrate SimplePythonChat features."""
    print("=" * 60)
    print("🐍 SimplePythonChat Demo")
    print("=" * 60)
    
    # Create a Python tutor
    tutor = SimplePythonChat(verbose=True)
    
    print("\n1. Ask about Python concepts:")
    print("-" * 40)
    response = tutor.ask("What are list comprehensions and why are they useful?")
    
    print("\n2. Explain code:")
    print("-" * 40)
    code_to_explain = """
def factorial(n):
    return 1 if n <= 1 else n * factorial(n - 1)

numbers = [1, 2, 3, 4, 5]
factorials = [factorial(num) for num in numbers]
print(factorials)
"""
    response = tutor.explain_code(code_to_explain)
    
    print("\n3. Get examples:")
    print("-" * 40)
    response = tutor.get_examples("decorators")
    
    print("\n4. Debug help:")
    print("-" * 40)
    buggy_code = """
def divide_numbers(a, b):
    return a / b

result = divide_numbers(10, 0)
print(result)
"""
    error_msg = "ZeroDivisionError: division by zero"
    response = tutor.debug_help(buggy_code, error_msg)
    
    print("\n5. Best practices:")
    print("-" * 40)
    response = tutor.best_practices("error handling")
    
    print("\n6. Learning path:")
    print("-" * 40)
    response = tutor.learning_path("intermediate")
    
    print("\n" + "=" * 60)
    print(f"Demo completed! Conversation history: {len(tutor.get_history())} exchanges")
    print("=" * 60)

def demo_convenience_function():
    """Demonstrate the convenience function."""
    print("\n🚀 Using convenience function:")
    print("-" * 40)
    
    # Quick setup
    chat = simple_python_chat()
    response = chat.ask("Explain the difference between a list and a tuple in Python")
    
    print(f"\nChat instance: {chat}")

if __name__ == "__main__":
    # Check if API key is available
    if not os.getenv('GOOGLE_API_KEY'):
        print("⚠️  Please set GOOGLE_API_KEY environment variable to run this demo")
        print("Example: export GOOGLE_API_KEY='your_api_key_here'")
        exit(1)
    
    demo_simple_python_chat()
    demo_convenience_function()
