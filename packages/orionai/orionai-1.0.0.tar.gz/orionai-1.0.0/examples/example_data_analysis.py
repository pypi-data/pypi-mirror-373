"""
AIPython Data Analysis Example
==============================
This example demonstrates data analysis capabilities including:
- Loading CSV files
- Statistical calculations
- Data visualization
- Missing value analysis
- Correlation analysis
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

# Test data analysis capabilities
response = chat.ask("Load the CSV file from examples/sample_data.csv and show me the first 5 rows")

response = chat.ask("Calculate the mean and standard deviation for all numeric columns")

response = chat.ask("Create a histogram for the first numeric column")

response = chat.ask("Find any missing values in the dataset")

response = chat.ask("Create a correlation matrix between numeric columns")
