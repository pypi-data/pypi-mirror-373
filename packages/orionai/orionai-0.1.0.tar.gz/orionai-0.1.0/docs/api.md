# 📚 OrionAI Python - API Reference

Complete API documentation for all OrionAI Python classes and functions.

## 🎯 Main Classes

### AIPython

The core AI Python assistant class.

```python
class AIPython:
    def __init__(self, 
                 provider: str = "google",
                 model: str = "gemini-1.5-pro", 
                 api_key: Optional[str] = None,
                 verbose: bool = True,
                 auto_install: bool = True,
                 ask_permission: bool = True,
                 max_retries: int = 3,
                 workspace_dir: str = "./aipython_outputs")
```

#### Parameters
- **provider** (str): LLM provider ("google", "openai", "anthropic")
- **model** (str): Model name (e.g., "gemini-1.5-pro", "gpt-4", "claude-3-sonnet")
- **api_key** (str, optional): API key (uses environment variable if None)
- **verbose** (bool): Show detailed output and progress
- **auto_install** (bool): Automatically install missing packages
- **ask_permission** (bool): Ask before executing potentially dangerous operations
- **max_retries** (int): Number of retry attempts on failures
- **workspace_dir** (str): Directory for saving outputs and files

#### Methods

##### ask(question: str) → str
Execute any Python task using natural language.

```python
ai = AIPython()
result = ai.ask("Create a pandas DataFrame and visualize it")
```

**Parameters:**
- **question** (str): Natural language description of the task

**Returns:**
- **str**: Result of the executed task

##### configure_provider(provider: str, model: str, api_key: str) → None
Change LLM provider settings.

```python
ai.configure_provider("openai", "gpt-4", "your-api-key")
```

##### get_workspace_info() → dict
Get information about the current workspace.

```python
info = ai.get_workspace_info()
# Returns: {"workspace_dir": "path", "files_created": [...], ...}
```

##### clear_workspace() → None
Clear the workspace directory.

```python
ai.clear_workspace()
```

---

### SimplePythonChat

Interactive Python learning assistant.

```python
class SimplePythonChat:
    def __init__(self,
                 provider: str = "google",
                 model: str = "gemini-1.5-pro",
                 api_key: Optional[str] = None,
                 verbose: bool = True)
```

#### Methods

##### ask(question: str) → str
Ask a Python-related question.

```python
chat = SimplePythonChat()
response = chat.ask("How do decorators work in Python?")
```

##### explain_code(code: str) → str
Get explanation of Python code.

```python
explanation = chat.explain_code("""
def fibonacci(n):
    return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)
""")
```

##### get_examples(topic: str) → str
Get practical examples for a Python topic.

```python
examples = chat.get_examples("list comprehensions")
```

##### debug_help(code: str, error: str = None) → str
Get debugging help for problematic code.

```python
help_text = chat.debug_help("my_code", "AttributeError: ...")
```

##### best_practices(topic: str) → str
Get Python best practices for a topic.

```python
practices = chat.best_practices("error handling")
```

---

### InteractiveCodeChat

Conversational code execution with session memory.

```python
class InteractiveCodeChat:
    def __init__(self,
                 provider: str = "google",
                 model: str = "gemini-1.5-pro",
                 api_key: Optional[str] = None,
                 verbose: bool = True,
                 auto_install: bool = True,
                 session_name: str = "default")
```

#### Methods

##### chat(message: str) → str
Simple conversational response without code execution.

```python
code_chat = InteractiveCodeChat()
response = code_chat.chat("What's the difference between lists and tuples?")
```

##### chat_with_code(message: str) → dict
Chat with code execution capabilities.

```python
result = code_chat.chat_with_code("Create a scatter plot with random data")
# Returns: {"response": "...", "result": "...", "execution_info": {...}}
```

##### get_session_info() → dict
Get information about the current session.

```python
info = code_chat.get_session_info()
```

##### clear_session() → None
Clear session history and context.

```python
code_chat.clear_session()
```

##### save_session(filename: str) → None
Save session to file.

```python
code_chat.save_session("my_session.json")
```

##### load_session(filename: str) → None
Load session from file.

```python
code_chat.load_session("my_session.json")
```

---

## 🚀 Quick Access Functions

### simple_python_chat(**kwargs) → SimplePythonChat
Create a SimplePythonChat instance with default settings.

```python
from orionai.python import simple_python_chat

chat = simple_python_chat(verbose=True)
```

### interactive_code_chat(**kwargs) → InteractiveCodeChat
Create an InteractiveCodeChat instance with default settings.

```python
from orionai.python import interactive_code_chat

code_chat = interactive_code_chat(session_name="my_project")
```

### ui() → None
Launch Streamlit UI for interactive testing.

```python
from orionai.python import ui

ui()  # Opens Streamlit interface in browser
```

---

## 🔧 Provider Classes

### GoogleProvider
Google Gemini API integration.

```python
class GoogleProvider:
    def __init__(self, model: str = "gemini-1.5-pro", api_key: Optional[str] = None)
    def generate(self, prompt: str) → str
```

### OpenAIProvider
OpenAI API integration.

```python
class OpenAIProvider:
    def __init__(self, model: str = "gpt-4", api_key: Optional[str] = None)
    def generate(self, prompt: str) → str
```

### AnthropicProvider
Anthropic Claude API integration.

```python
class AnthropicProvider:
    def __init__(self, model: str = "claude-3-sonnet-20240229", api_key: Optional[str] = None)
    def generate(self, prompt: str) → str
```

---

## 🛠️ Utility Functions

### Helper Functions Available in Code Execution

When using `ai.ask()`, these helper functions are available in the execution context:

```python
# File operations
save_file(content: str, filename: str) → str
load_file(filename: str) → str

# Plotting
save_plot(filename: str) → None
show_plot() → None

# Display
display_results(title: str, data: Any) → None

# Database
create_database(db_name: str) → str
execute_query(query: str, db_name: str) → Any

# Data processing
process_data(data: Any, operation: str) → Any

# Visualization
create_chart(data: Any, chart_type: str, **kwargs) → None

# Report generation
create_report(title: str, sections: dict, filename: str = None) → str
```

---

## 🔒 Environment Variables

Required environment variables for different providers:

```bash
# Google Gemini (Default)
GOOGLE_API_KEY="your-google-api-key"

# OpenAI
OPENAI_API_KEY="your-openai-api-key"

# Anthropic
ANTHROPIC_API_KEY="your-anthropic-api-key"
```

---

## 🚨 Error Handling

### Common Exceptions

```python
# Provider errors
class ProviderError(Exception):
    """Raised when LLM provider encounters an error"""

# Execution errors  
class ExecutionError(Exception):
    """Raised when code execution fails"""

# Configuration errors
class ConfigurationError(Exception):
    """Raised when configuration is invalid"""
```

### Error Handling Example

```python
from orionai.python import AIPython, ProviderError

try:
    ai = AIPython()
    result = ai.ask("Complex data analysis task")
except ProviderError as e:
    print(f"LLM Provider error: {e}")
except ExecutionError as e:
    print(f"Code execution error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## 📊 Return Types

### Standard Return Types

- **Simple Results**: `str` - Text responses and simple outputs
- **Complex Results**: `Any` - DataFrames, arrays, objects, etc.
- **Execution Info**: `dict` - Detailed execution information
- **Session Data**: `dict` - Session state and history

### Example Return Structures

```python
# Simple ask() result
result = "Data analysis completed successfully"

# chat_with_code() result
{
    "response": "Code executed successfully",
    "result": pandas.DataFrame(...),
    "execution_info": {
        "execution_time": 2.34,
        "packages_installed": ["pandas", "matplotlib"],
        "files_created": ["plot.png"],
        "success": True
    }
}

# Session info result
{
    "session_name": "my_project",
    "total_exchanges": 15,
    "code_executions": 8,
    "files_created": ["plot1.png", "data.csv"],
    "conversation_history": [...],
    "session_context": {...}
}
```

---

## 🎯 Best Practices

### Initialization
```python
# Recommended initialization
ai = AIPython(
    verbose=True,          # See what's happening
    auto_install=True,     # Auto-install packages
    ask_permission=False,  # For smooth automation
    max_retries=3         # Handle transient failures
)
```

### Error Handling
```python
# Always handle potential errors
try:
    result = ai.ask("Your task here")
except Exception as e:
    print(f"Error: {e}")
    # Handle gracefully
```

### Session Management
```python
# Use sessions for related work
code_chat = interactive_code_chat(session_name="data_analysis_project")
code_chat.save_session("project_state.json")  # Save progress
```

### Resource Management
```python
# Clear workspace when done
ai.clear_workspace()

# Clear sessions when appropriate
code_chat.clear_session()
```

This API reference covers all public methods and classes. For implementation details, see the source code in `orionai/python/`.
