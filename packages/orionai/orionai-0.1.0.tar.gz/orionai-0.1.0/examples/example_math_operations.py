"""
AIPython Math Operations Example
================================
This example demonstrates mathematical capabilities including:
- Factorial calculations
- Fibonacci sequences
- Equation solving
- Numerical integration
- Matrix operations
- Prime number generation
"""

import os
import sys
sys.path.append('..')
from orionai.python import AIPython

# Set your Google API key in environment variable
# os.environ['GOOGLE_API_KEY'] = 'your_api_key_here'

chat = AIPython(
    provider="google",
    model="gemini-1.5-pro",
    verbose=True
)

# Test mathematical computations
response = chat.ask("Calculate the factorial of 15")

response = chat.ask("Generate the first 20 fibonacci numbers")

response = chat.ask("Solve the quadratic equation x^2 - 5x + 6 = 0")

response = chat.ask("Calculate the area under the curve y = x^2 from 0 to 5 using numerical integration")

response = chat.ask("Generate a 3x3 matrix with random integers and calculate its determinant")

response = chat.ask("Find all prime numbers between 1 and 100")
