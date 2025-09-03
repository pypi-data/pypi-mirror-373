# 🚀 OrionAI Python - Quick Start Guide

OrionAI Python is a comprehensive AI-powered Python assistant that enables you to perform any Python task with LLM assistance, automatic code execution, and interactive learning features.

## 📦 Installation

```bash
pip install orionai
```

## 🔑 Setup

Before using OrionAI Python, you need to configure your LLM provider API key:

### Option 1: Environment Variable (Recommended)
```bash
# For Google Gemini (Default)
export GOOGLE_API_KEY="your-api-key-here"

# For OpenAI
export OPENAI_API_KEY="your-api-key-here"

# For Anthropic
export ANTHROPIC_API_KEY="your-api-key-here"
```

### Option 2: Direct API Key
```python
from orionai.python import AIPython

ai = AIPython(api_key="your-api-key-here")
```

## 🎯 Basic Usage

### 1. Simple AI Python Assistant

```python
from orionai.python import AIPython

# Initialize with default settings (Google Gemini)
ai = AIPython()

# Ask AI to do any Python task
result = ai.ask("Create a pandas DataFrame with sample data and plot it")
print(result)
```

### 2. Python Learning Assistant

```python
from orionai.python import simple_python_chat

# Start interactive Python learning
chat = simple_python_chat()

# Ask Python questions
response = chat.ask("How do list comprehensions work?")
print(response)

# Get code explanations
explanation = chat.explain_code("""
def fibonacci(n):
    return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)
""")
print(explanation)
```

### 3. Interactive Code Chat

```python
from orionai.python import interactive_code_chat

# Start conversational code execution
code_chat = interactive_code_chat(session_name="my_project")

# Chat without code execution
response = code_chat.chat("What's the best way to handle missing data in pandas?")

# Chat with code execution
result = code_chat.chat_with_code("Load iris dataset and show basic statistics")
```

### 4. Streamlit UI (Interactive Testing)

```python
from orionai.python import ui

# Launch Streamlit interface for testing all features
ui()
```

## 🔧 Configuration Options

```python
from orionai.python import AIPython

# Customize your AI assistant
ai = AIPython(
    provider="google",           # "google", "openai", "anthropic"
    model="gemini-1.5-pro",     # Model name
    verbose=True,               # Show detailed output
    auto_install=True,          # Auto-install missing packages
    ask_permission=False,       # Skip permission prompts
    max_retries=3,             # Retry attempts on errors
    workspace_dir="./outputs"   # Output directory
)
```

## 📋 Core Features

- **🤖 AI-Powered Code Generation**: Generate and execute Python code with natural language
- **📊 Data Science**: Pandas, NumPy, Matplotlib, Seaborn, Scikit-learn integration
- **🔬 Machine Learning**: Model training, evaluation, and prediction
- **🌐 Web Operations**: API calls, web scraping, data fetching
- **📈 Visualizations**: Automatic plot generation and saving
- **🗄️ Database Operations**: SQLite integration with automatic management
- **🔒 Security**: Encryption, hashing, secure random generation
- **⚡ Performance**: Memory monitoring, timing, optimization
- **📝 Text Processing**: NLP operations, file handling
- **🔄 Interactive Learning**: Conversational Python tutoring

## 🎯 Quick Examples

### Data Analysis
```python
ai = AIPython()
result = ai.ask("Load a CSV file, analyze missing values, and create visualizations")
```

### Machine Learning
```python
result = ai.ask("Create a simple classification model with the iris dataset")
```

### Web Data
```python
result = ai.ask("Fetch data from a REST API and save to database")
```

### Visualization
```python
result = ai.ask("Create a beautiful dashboard with multiple charts")
```

## 🚀 Next Steps

1. **Explore Features**: Check out `docs/features.md` for complete feature list
2. **API Reference**: See `docs/api.md` for detailed API documentation  
3. **Examples**: Browse `examples/` directory for comprehensive examples
4. **Interactive UI**: Launch `ui()` to test features interactively

## 🤝 Need Help?

- 📖 Full documentation: `docs/`
- 🐛 Issues: GitHub Issues
- 💬 Discussion: GitHub Discussions
- 📧 Support: Create an issue for support

Happy coding with OrionAI Python! 🎉
