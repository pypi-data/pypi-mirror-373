"""
AIPython File Operations Example
================================
This example demonstrates file and system operations including:
- Directory creation and management
- File reading and analysis
- Backup operations
- Pattern searching with regex
- File compression
- File system monitoring
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

# Test file operations and utilities
response = chat.ask("Create a directory structure with subdirectories and files")

response = chat.ask("Read all .py files in the current directory and count lines of code")

response = chat.ask("Create a backup of files with timestamp in filename")

response = chat.ask("Search for specific patterns in text files using regex")

response = chat.ask("Compress files into a zip archive")

response = chat.ask("Monitor file system changes in a directory")
