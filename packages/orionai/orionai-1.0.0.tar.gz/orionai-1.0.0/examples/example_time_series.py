"""
AIPython Time Series Example
============================
This example demonstrates time series and date operations including:
- Time series data generation
- Moving averages calculation
- Date format parsing
- Business day calculations
- Calendar visualizations
- Time zone conversions
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

# Test time series and date operations
response = chat.ask("Generate a time series dataset with daily frequency for one year")

response = chat.ask("Calculate moving averages for a time series")

response = chat.ask("Parse different date formats and convert to standard format")

response = chat.ask("Find business days between two dates excluding weekends")

response = chat.ask("Create a calendar heatmap showing activity over time")

response = chat.ask("Perform time zone conversions between different regions")
