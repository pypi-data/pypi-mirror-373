"""
OrionAI - AI-Powered Python Assistant
====================================

Complete AI-powered Python assistant with 50+ advanced features for any Python task.

Example Usage:
--------------
>>> from orionai.python import AIPython
>>> ai = AIPython()
>>> ai.ask("Create a machine learning model to predict house prices")
>>> ai.ask("Analyze this CSV file and create visualizations")
>>> ai.ask("Scrape website data and save to database")

>>> from orionai.python import SimplePythonChat
>>> chat = SimplePythonChat()
>>> chat.ask("How do decorators work in Python?")

>>> from orionai.python import ui
>>> ui()  # Launch Streamlit interface
"""

# Import main modules
from . import python
from . import ui

__version__ = "0.1.0"
__author__ = "AIMLDev726"
__email__ = "aistudentlearn4@gmail.com"
__url__ = "https://github.com/AIMLDev726/OrionAI"

__all__ = ["python", "ui"]
