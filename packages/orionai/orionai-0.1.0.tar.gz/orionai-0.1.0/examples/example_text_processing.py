"""
AIPython Text Processing Example
================================
This example demonstrates text processing and NLP capabilities including:
- Sentiment analysis
- Keyword extraction
- Word cloud generation
- Text similarity comparison
- Text classification
- Named entity recognition
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

# Test text processing and NLP
response = chat.ask("Analyze sentiment of a given text using natural language processing")

response = chat.ask("Extract keywords and key phrases from a paragraph")

response = chat.ask("Generate word clouds from text data")

response = chat.ask("Perform text similarity comparison between documents")

response = chat.ask("Create a simple text classifier for spam detection")

response = chat.ask("Extract named entities from text using spaCy")
