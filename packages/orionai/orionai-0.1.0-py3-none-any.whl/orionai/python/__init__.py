"""
OrionAI Python Module
=====================

AIPython - Universal Python AI Assistant that can perform any Python task.
SimplePythonChat - Python learning assistant focused on teaching Python concepts.
InteractiveCodeChat - Interactive conversational chat with code execution and session memory.
ui - Launch Streamlit interface for interactive testing of all features.

Usage:
    from orionai.python import AIPython, SimplePythonChat, InteractiveCodeChat, ui
    
    # For code execution and complex tasks
    ai = AIPython(model="gemini-1.5-pro")
    ai.ask("Create a machine learning model to predict house prices")
    ai.ask("Scrape website data and analyze it") 
    ai.ask("Generate a dashboard with plotly")
    
    # For Python learning and explanations
    tutor = SimplePythonChat()
    tutor.ask("How do decorators work in Python?")
    tutor.explain_code("@property\ndef name(self): return self._name")
    tutor.get_examples("list comprehensions")
    
    # For interactive conversational coding with memory
    interactive = InteractiveCodeChat(session_name="my_session")
    interactive.chat("How do I work with pandas DataFrames?")
    interactive.chat_with_code("Create a simple DataFrame and show basic operations")
    
    # Launch Streamlit UI for testing all features
    ui()  # Opens interactive interface in browser
"""

from .aipython import AIPython, SimplePythonChat, InteractiveCodeChat, simple_python_chat, interactive_code_chat
from ..ui import ui

__all__ = ["AIPython", "SimplePythonChat", "InteractiveCodeChat", "simple_python_chat", "interactive_code_chat", "ui"]
