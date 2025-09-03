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

# Import lazy loading functions
from .lazy_imports import get_pandas, get_numpy, get_matplotlib, get_seaborn

# Import AIPython classes with error handling
try:
    from .aipython import AIPython, SimplePythonChat, InteractiveCodeChat, simple_python_chat, interactive_code_chat
except ImportError as e:
    print(f"Warning: Could not import AIPython classes: {e}")
    # Provide dummy classes to prevent complete failure
    class AIPython:
        def __init__(self, *args, **kwargs):
            raise ImportError(f"AIPython not available due to import issues: {e}")
    
    class SimplePythonChat:
        def __init__(self, *args, **kwargs):
            raise ImportError(f"SimplePythonChat not available due to import issues: {e}")
    
    class InteractiveCodeChat:
        def __init__(self, *args, **kwargs):
            raise ImportError(f"InteractiveCodeChat not available due to import issues: {e}")
    
    def simple_python_chat(*args, **kwargs):
        raise ImportError(f"simple_python_chat not available due to import issues: {e}")
    
    def interactive_code_chat(*args, **kwargs):
        raise ImportError(f"interactive_code_chat not available due to import issues: {e}")

from ..ui import ui

# Export available functions and classes
__all__ = ["AIPython", "SimplePythonChat", "InteractiveCodeChat", "simple_python_chat", "interactive_code_chat", "ui", "get_pandas", "get_numpy", "get_matplotlib", "get_seaborn"]
