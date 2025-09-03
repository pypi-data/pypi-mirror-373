# OrionAI Interactive CLI

A rich command-line interface for interactive LLM sessions with real-time Python code execution.

## Features

### 🚀 Interactive LLM Chat
- **Rich UI**: Beautiful terminal interface with panels, tables, and syntax highlighting
- **Multiple LLM Providers**: Support for OpenAI, Anthropic (Claude), and Google (Gemini)
- **Real-time Code Execution**: Automatically executes Python code blocks in responses
- **Error Handling**: Automatically sends errors back to LLM for fixing
- **Scrollable Interface**: Fully scrollable chat history

### 📝 Session Management
- **Persistent Sessions**: All conversations saved in `~/.orionai/sessions/{session_id}/`
- **Session History**: Access to previous conversations and context
- **Multiple Sessions**: Create, load, delete, and export sessions
- **Auto-save**: Automatic session saving with configurable intervals

### 🔧 Code Execution Engine
- **Safe Execution**: Isolated execution environment
- **Output Capture**: Captures stdout, stderr, and execution time
- **File Management**: Automatic saving of plots and images
- **Package Installation**: Automatic package installation when needed
- **Error Recovery**: LLM-assisted error fixing and retry mechanism

### 💾 Storage & Organization
- **Structured Storage**: 
  ```
  ~/.orionai/
  ├── config.yaml              # Global configuration
  ├── sessions/
  │   └── {session_id}/
  │       ├── session.json     # Chat history
  │       ├── images/          # Generated plots and images
  │       ├── reports/         # Analysis reports
  │       └── execution_*.json # Code execution logs
  └── logs/                    # Application logs
  ```

### 🖼️ Image & Plot Handling
- **Automatic Plot Saving**: Matplotlib figures automatically saved to `images/` folder
- **Path Display**: Shows user the exact path to generated files
- **Multiple Formats**: Support for PNG, JPG, and other image formats
- **Organized Storage**: Images organized by session and timestamp

## Installation

### Quick Install
```bash
# Clone the repository
git clone https://github.com/AIMLDev726/OrionAI.git
cd OrionAI

# Install in development mode
pip install -e .

# Or run the installation script (Windows)
install_cli.bat
```

### Requirements
- Python 3.8+
- API key for at least one LLM provider:
  - OpenAI API key
  - Anthropic API key  
  - Google AI API key

## Usage

### Starting the CLI
```bash
orionai
```

### First Time Setup
1. Run `orionai` to start the CLI
2. Select your preferred LLM provider
3. Enter your API key
4. Create a new session
5. Start chatting!

### CLI Commands
Once in a chat session, you can use these commands:

- `help` - Show help information
- `info` - Show current session information  
- `clear` - Clear the screen
- `save` - Save current session
- `history` - Show conversation history
- `exit` or `quit` - Exit the session

### Example Interaction

```
🙋 You: Create a scatter plot showing the relationship between height and weight

🤖 OrionAI: I'll create a scatter plot for you showing the relationship between height and weight.

```python
import matplotlib.pyplot as plt
import numpy as np

# Generate sample data
np.random.seed(42)
heights = np.random.normal(170, 10, 100)  # Heights in cm
weights = 0.9 * heights + np.random.normal(0, 5, 100) - 80  # Weights in kg

# Create scatter plot
plt.figure(figsize=(10, 6))
plt.scatter(heights, weights, alpha=0.6, c='blue', s=50)
plt.xlabel('Height (cm)')
plt.ylabel('Weight (kg)')
plt.title('Relationship between Height and Weight')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
```

🔧 Executing Code...

📤 Output:
<plot displayed>

📁 Files Created:
C:\Users\{username}\.orionai\abc12345\images\plot_20250902_143022_1.png

⏱️ Execution time: 0.15s
```

### Configuration

The CLI stores configuration in `~/.orionai/config.yaml`:

```yaml
llm:
  provider: openai
  model: gpt-3.5-turbo
  api_key: null  # Stored separately for security
  temperature: 0.7
  max_tokens: 2000

session:
  auto_save: true
  save_interval: 300
  max_history: 100
  enable_code_execution: true
  image_folder: images
  reports_folder: reports
```

### Environment Variables

You can set API keys via environment variables:
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GOOGLE_API_KEY`

## Advanced Features

### Code Execution with Error Handling
```
🙋 You: Calculate the mean of a list but use wrong syntax

🤖 OrionAI: I'll calculate the mean for you.

```python
numbers = [1, 2, 3, 4, 5]
mean = numbers.mean()  # This will fail
print(f"Mean: {mean}")
```

🔧 Executing Code...

❌ Error:
AttributeError: 'list' object has no attribute 'mean'

🔄 Code execution failed. Asking LLM to fix it...

🛠️ LLM provided a fix:

```python
numbers = [1, 2, 3, 4, 5]
mean = sum(numbers) / len(numbers)  # Fixed version
print(f"Mean: {mean}")
```

🔧 Executing Code...

📤 Output:
Mean: 3.0

✅ Code fixed and executed successfully!
```

### Session Management
- **Create Sessions**: Organize conversations by topic or project
- **Load Previous Sessions**: Continue where you left off
- **Export Sessions**: Share or backup your conversations
- **Session Statistics**: Track usage and activity

### Multi-Modal Support
- **Text Analysis**: Process and analyze text data
- **Data Visualization**: Create charts, plots, and graphs
- **Image Processing**: Basic image operations and analysis
- **File Operations**: Read, write, and process various file formats

## API Keys Setup

### OpenAI
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Set environment variable: `set OPENAI_API_KEY=your_key_here`

### Anthropic
1. Go to https://console.anthropic.com/
2. Create an API key
3. Set environment variable: `set ANTHROPIC_API_KEY=your_key_here`

### Google AI
1. Go to https://makersuite.google.com/app/apikey
2. Create an API key
3. Set environment variable: `set GOOGLE_API_KEY=your_key_here`

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **API Key Not Found**: Set environment variables or configure through the CLI

3. **Permission Errors**: Ensure write permissions to `~/.orionai/` directory

4. **Code Execution Failures**: Check if required packages are installed

### Getting Help

- Use the `help` command within the CLI
- Check the session logs in `~/.orionai/logs/`
- Review execution logs for debugging
- Open an issue on GitHub for bugs or feature requests

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.
