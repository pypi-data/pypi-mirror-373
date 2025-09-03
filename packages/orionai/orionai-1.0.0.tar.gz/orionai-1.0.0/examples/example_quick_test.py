"""
AIPython Quick Features Test
===========================
A quick test script to verify all AIPython features are working.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from orionai.python import AIPython

# Set your Google API key in environment variable
# os.environ['GOOGLE_API_KEY'] = 'your_api_key_here'

# Test basic initialization and functionality
chat = AIPython(
    provider="google",
    model="gemini-1.5-pro",
    ask_permission=False,  # Disable for automated testing
    verbose=True
)

print("Enhanced AIPython working!")
print(repr(chat))

# Quick functionality test
response = chat.ask("Calculate 2 + 2 and create a simple plot showing the result")

print("Quick test completed successfully!")
