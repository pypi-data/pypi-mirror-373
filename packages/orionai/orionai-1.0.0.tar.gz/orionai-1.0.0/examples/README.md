# AIPython Examples

This directory contains comprehensive examples demonstrating the capabilities of the AIPython system.

## Setup

Before running any examples, make sure to set your API key in the environment variable:

```bash
# For Google Gemini (primary provider)
export GOOGLE_API_KEY="your_google_api_key_here"

# Optional: For additional providers
export OPENAI_API_KEY="your_openai_api_key_here"
export ANTHROPIC_API_KEY="your_anthropic_api_key_here"
```

Or in Python:
```python
import os
os.environ['GOOGLE_API_KEY'] = 'your_api_key_here'
```

## Available Examples

### Core Functionality
- **`example_quick_test.py`** - Quick test to verify installation and basic functionality
- **`example_enhanced_features.py`** - Demonstrates all enhanced features including multi-provider support

### Domain-Specific Examples
- **`example_data_analysis.py`** - Data loading, statistical analysis, and data exploration
- **`example_math_operations.py`** - Mathematical computations, equations, and numerical methods
- **`example_visualization.py`** - Charts, plots, and data visualization
- **`example_machine_learning.py`** - ML models, training, and evaluation
- **`example_web_data.py`** - Web scraping, API calls, and data parsing
- **`example_file_operations.py`** - File handling and system operations
- **`example_time_series.py`** - Time-based data operations and analysis
- **`example_text_processing.py`** - Natural language processing and text analysis

## Features Demonstrated

### Enhanced AIPython Features
- ✅ **Multi-Provider Support**: Google Gemini, OpenAI GPT, Anthropic Claude
- ✅ **Permission System**: Ask user permission before installing packages
- ✅ **Rich UI**: Beautiful terminal output with progress indicators
- ✅ **Environment Detection**: Automatic detection of Jupyter vs VSCode
- ✅ **Smart Package Installation**: With real-time logs and timeout handling
- ✅ **Error Recovery**: Intelligent retry mechanisms and fallback strategies

### Capabilities
- ✅ **Data Analysis**: CSV loading, statistics, visualization
- ✅ **Mathematics**: Complex calculations, equation solving, matrix operations
- ✅ **Machine Learning**: Model training, evaluation, and prediction
- ✅ **Visualization**: 2D/3D plots, charts, heatmaps, interactive graphs
- ✅ **Web Operations**: API calls, web scraping, data extraction
- ✅ **File Operations**: Reading, writing, compression, backup
- ✅ **Text Processing**: NLP, sentiment analysis, keyword extraction
- ✅ **Time Series**: Date operations, forecasting, trend analysis

## Running Examples

```bash
# Run a quick test
python examples/example_quick_test.py

# Test specific functionality
python examples/example_data_analysis.py
python examples/example_visualization.py
python examples/example_machine_learning.py

# Test enhanced features
python examples/example_enhanced_features.py
```

## Interactive Usage

```python
from orionai.python import AIPython

# Initialize with enhanced features
chat = AIPython(
    provider="google",           # or "openai", "anthropic"
    model="gemini-1.5-pro",     # or "gpt-4", "claude-3-sonnet-20240229"
    ask_permission=True,         # Ask before installing packages
    verbose=True                 # Show detailed output
)

# Ask anything!
response = chat.ask("Create a machine learning model to predict house prices")
response = chat.ask("Make a beautiful visualization of the results")
response = chat.ask("Generate a report summarizing the findings")
```

## Sample Data

The `sample_data.csv` file contains example data for testing data analysis features.

## Notes

- Examples are designed to work independently
- Each example includes comprehensive documentation
- All outputs are saved to `../aipython_outputs/` directory
- Package installation requires user permission (configurable)
- Rich UI provides beautiful terminal output with progress indicators
