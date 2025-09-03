"""
AIPython Web Data Example
=========================
This example demonstrates web and data handling capabilities including:
- HTTP requests and API calls
- Web scraping
- JSON data handling
- Text file processing
- REST API clients
- XML parsing
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

# Test web scraping and API tasks
response = chat.ask("Make a GET request to httpbin.org/json and parse the response")

response = chat.ask("Create a simple web scraper that extracts titles from a webpage")

response = chat.ask("Generate sample JSON data and save it to a file")

response = chat.ask("Read a text file and count word frequencies")

response = chat.ask("Create a simple REST API client that handles authentication")

response = chat.ask("Parse XML data and extract specific elements")
