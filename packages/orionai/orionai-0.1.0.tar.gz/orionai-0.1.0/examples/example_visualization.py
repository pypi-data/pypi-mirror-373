"""
AIPython Visualization Example
==============================
This example demonstrates visualization capabilities including:
- Line plots and mathematical functions
- Scatter plots with trend lines
- Bar charts and frequency analysis
- Pie charts for distribution
- Heatmaps for correlation
- 3D surface plots
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

# Test visualization capabilities
response = chat.ask("Create a line plot showing y = sin(x) for x from 0 to 2π")

response = chat.ask("Generate a scatter plot with 100 random points and add a trend line")

response = chat.ask("Create a bar chart showing the frequency of letters in the word 'visualization'")

response = chat.ask("Make a pie chart showing the distribution of values [25, 30, 15, 20, 10]")

response = chat.ask("Create a heatmap from a 5x5 random matrix")

response = chat.ask("Generate a 3D surface plot of the function z = x^2 + y^2")
