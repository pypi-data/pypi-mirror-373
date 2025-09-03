"""
AIPython - Universal Python AI Assistant
========================================

Can perform any Python task with automatic package installation,
code execution, error handling, and intelligent feedback.
"""

import os
import sys
import subprocess
import importlib
import traceback
import json
import time
import warnings
from typing import Any, Dict, List, Optional, Union, Tuple
from io import StringIO, BytesIO
import contextlib
import datetime
import tempfile
import base64
from pathlib import Path
import threading
import queue

# Core imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Rich for better terminal UI
try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
    from rich.prompt import Confirm
    from rich.panel import Panel
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# LLM Providers
try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

warnings.filterwarnings('ignore')


def detect_environment():
    """Detect if running in Jupyter or VSCode."""
    try:
        # Check for Jupyter
        if 'ipykernel' in sys.modules:
            return 'jupyter'
        # Check for IPython
        if 'IPython' in sys.modules:
            from IPython import get_ipython
            if get_ipython() is not None:
                return 'jupyter'
        # Check for VSCode
        if 'VSCODE_PID' in os.environ:
            return 'vscode'
    except:
        pass
    return 'terminal'


def setup_console():
    """Setup console based on environment."""
    env = detect_environment()
    if RICH_AVAILABLE and env != 'jupyter':
        return Console(), True
    else:
        return None, False


class LLMProvider:
    """Base class for LLM providers."""
    
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
    
    def generate(self, prompt: str) -> str:
        raise NotImplementedError


class GoogleProvider(LLMProvider):
    """Google Gemini provider."""
    
    def __init__(self, api_key: str, model: str = "gemini-1.5-pro"):
        super().__init__(api_key, model)
        if not GOOGLE_AVAILABLE:
            raise ImportError("google-generativeai not installed")
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(model)
    
    def generate(self, prompt: str) -> str:
        try:
            response = self.client.generate_content(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Google API error: {e}")


class OpenAIProvider(LLMProvider):
    """OpenAI provider."""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        super().__init__(api_key, model)
        if not OPENAI_AVAILABLE:
            raise ImportError("openai not installed")
        self.client = openai.OpenAI(api_key=api_key)
    
    def generate(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API error: {e}")


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider."""
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        super().__init__(api_key, model)
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic not installed")
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def generate(self, prompt: str) -> str:
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            raise Exception(f"Anthropic API error: {e}")


class AIPython:
    """
    Universal Python AI Assistant that can perform any Python task.
    
    Features:
    - Automatic package installation with user permission
    - Intelligent code generation
    - Safe code execution with error recovery
    - Visual output capture (plots, charts)
    - Comprehensive logging and feedback
    - Multiple LLM support (Google, OpenAI, Anthropic)
    - Rich terminal UI with progress bars
    - Environment detection (Jupyter vs VSCode)
    
    Usage:
        chat = AIPython(provider="google", model="gemini-1.5-pro")
        chat = AIPython(provider="openai", model="gpt-4")
        chat = AIPython(provider="anthropic", model="claude-3-sonnet-20240229")
        chat.ask("Create a machine learning model")
        chat.ask("Generate interactive dashboard")
        chat.ask("Scrape and analyze website data")
    """
    
    def __init__(self, 
                 provider: str = "google",
                 model: Optional[str] = None,
                 api_key: Optional[str] = None,
                 auto_install: bool = True,
                 ask_permission: bool = True,
                 verbose: bool = True,
                 max_retries: int = 3,
                 workspace_dir: Optional[str] = None,
                 save_outputs: bool = True):
        """
        Initialize AIPython assistant.
        
        Args:
            provider: LLM provider ("google", "openai", "anthropic")
            model: LLM model to use (provider-specific defaults if None)
            api_key: API key for the provider
            auto_install: Automatically install missing packages
            ask_permission: Ask user permission before installing packages
            verbose: Show detailed output
            max_retries: Maximum retry attempts for failed operations
            workspace_dir: Directory to save outputs and files
            save_outputs: Whether to save generated plots and files
        """
        self.provider_name = provider.lower()
        self.auto_install = auto_install
        self.ask_permission = ask_permission
        self.verbose = verbose
        self.max_retries = max_retries
        self.save_outputs = save_outputs
        
        # Setup environment detection and console
        self.environment = detect_environment()
        self.console, self.use_rich = setup_console()
        
        # Setup workspace directory
        if workspace_dir:
            self.workspace_dir = Path(workspace_dir)
        else:
            self.workspace_dir = Path.cwd() / "aipython_outputs"
        
        self.workspace_dir.mkdir(exist_ok=True)
        
        # Initialize LLM provider
        self._setup_llm_provider(provider, model, api_key)
        
        # Execution history
        self.execution_history = []
        self.installed_packages = set()
        self.global_namespace = {}
        self.saved_files = []
        
        # Initialize execution environment
        self._setup_environment()
        
        if self.verbose:
            self._log_info(f"🚀 AIPython initialized with {self.provider_name}:{self.model_name}")
            self._log_info(f"   Environment: {self.environment}")
            self._log_info(f"   Auto-install: {self.auto_install}")
            self._log_info(f"   Ask permission: {self.ask_permission}")
            self._log_info(f"   Max retries: {self.max_retries}")
            self._log_info(f"   Workspace: {self.workspace_dir}")
            self._log_info(f"   Save outputs: {self.save_outputs}")
    
    def _log_info(self, message: str):
        """Log information with environment-appropriate formatting."""
        if self.environment == 'jupyter':
            print(message)
        elif self.use_rich and self.console:
            self.console.print(message)
        else:
            print(message)
    
    def _log_success(self, message: str):
        """Log success message."""
        if self.use_rich and self.console:
            self.console.print(f"✅ {message}", style="green")
        else:
            print(f"✅ {message}")
    
    def _log_error(self, message: str):
        """Log error message."""
        if self.use_rich and self.console:
            self.console.print(f"❌ {message}", style="red")
        else:
            print(f"❌ {message}")
    
    def _log_warning(self, message: str):
        """Log warning message."""
        if self.use_rich and self.console:
            self.console.print(f"⚠️ {message}", style="yellow")
        else:
            print(f"⚠️ {message}")
    
    def _setup_llm_provider(self, provider: str, model: Optional[str], api_key: Optional[str]):
        """Setup LLM provider."""
        provider = provider.lower()
        
        # Get API key from environment if not provided
        if not api_key:
            if provider == "google":
                api_key = os.environ.get('GOOGLE_API_KEY')
            elif provider == "openai":
                api_key = os.environ.get('OPENAI_API_KEY')
            elif provider == "anthropic":
                api_key = os.environ.get('ANTHROPIC_API_KEY')
        
        if not api_key:
            raise ValueError(f"API key required for {provider}. Set {provider.upper()}_API_KEY environment variable.")
        
        # Set default models
        if not model:
            if provider == "google":
                model = "gemini-1.5-pro"
            elif provider == "openai":
                model = "gpt-4"
            elif provider == "anthropic":
                model = "claude-3-sonnet-20240229"
            else:
                raise ValueError(f"Unsupported provider: {provider}")
        
        self.model_name = model
        
        # Initialize provider
        try:
            if provider == "google":
                self.llm_provider = GoogleProvider(api_key, model)
            elif provider == "openai":
                self.llm_provider = OpenAIProvider(api_key, model)
            elif provider == "anthropic":
                self.llm_provider = AnthropicProvider(api_key, model)
            else:
                raise ValueError(f"Unsupported provider: {provider}")
        except ImportError as e:
            raise ImportError(f"Required library not installed for {provider}: {e}")
        except Exception as e:
            raise Exception(f"Failed to initialize {provider} provider: {e}")
    
    def _setup_environment(self):
        """Setup Python execution environment."""
        self.global_namespace = {
            'pd': pd,
            'np': np,
            'plt': plt,
            'sns': sns,
            'os': os,
            'sys': sys,
            'json': json,
            'time': time,
            'datetime': datetime,
            'Path': Path,
            'workspace_dir': self.workspace_dir,
            '_aipython': self,  # Reference to self for advanced operations
            # Add more common imports
        }
        
        # Set matplotlib backend for non-interactive use
        plt.switch_backend('Agg')
        
        # Configure seaborn style
        sns.set_style("whitegrid")
        
        # Add custom helper functions
        self._add_helper_functions()
    
    def _add_helper_functions(self):
        """Add custom helper functions to the execution environment."""
        
        def save_plot(filename: str = None, dpi: int = 300, transparent: bool = False):
            """Save the current matplotlib plot."""
            if filename is None:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"plot_{timestamp}.png"
            
            filepath = self.workspace_dir / filename
            plt.savefig(filepath, dpi=dpi, bbox_inches='tight', transparent=transparent)
            if self.verbose:
                print(f"📊 Plot saved: {filepath}")
            self.saved_files.append(str(filepath))
            return str(filepath)
        
        def save_dataframe(df, filename: str = None, format: str = 'csv'):
            """Save DataFrame in various formats."""
            if filename is None:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"dataframe_{timestamp}.{format}"
            
            filepath = self.workspace_dir / filename
            
            if format.lower() == 'csv':
                df.to_csv(filepath, index=False)
            elif format.lower() in ['xlsx', 'excel']:
                df.to_excel(filepath, index=False)
            elif format.lower() == 'json':
                df.to_json(filepath, orient='records', indent=2)
            elif format.lower() == 'parquet':
                df.to_parquet(filepath)
            else:
                df.to_csv(filepath, index=False)  # Default to CSV
            
            if self.verbose:
                print(f"💾 DataFrame saved: {filepath}")
            self.saved_files.append(str(filepath))
            return str(filepath)
        
        def load_data(filepath: str, **kwargs):
            """Smart data loader that detects file format."""
            filepath = Path(filepath)
            
            if not filepath.exists():
                # Try in workspace directory
                filepath = self.workspace_dir / filepath
            
            if not filepath.exists():
                raise FileNotFoundError(f"File not found: {filepath}")
            
            extension = filepath.suffix.lower()
            
            if extension == '.csv':
                return pd.read_csv(filepath, **kwargs)
            elif extension in ['.xlsx', '.xls']:
                return pd.read_excel(filepath, **kwargs)
            elif extension == '.json':
                return pd.read_json(filepath, **kwargs)
            elif extension == '.parquet':
                return pd.read_parquet(filepath, **kwargs)
            else:
                # Try CSV as default
                return pd.read_csv(filepath, **kwargs)
        
        def display_results(*args, max_rows: int = 20, max_cols: int = 10):
            """Enhanced display function for results."""
            for arg in args:
                if isinstance(arg, pd.DataFrame):
                    print(f"📊 DataFrame Shape: {arg.shape}")
                    with pd.option_context('display.max_rows', max_rows, 'display.max_columns', max_cols):
                        print(arg)
                elif isinstance(arg, (list, dict, tuple)):
                    print(f"📋 {type(arg).__name__}: {arg}")
                else:
                    print(f"📄 Result: {arg}")
                print("-" * 50)
        
        def create_report(title: str, sections: Dict[str, Any]):
            """Create a formatted report."""
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            report_lines = [
                f"# {title}",
                f"Generated on: {timestamp}",
                f"Generated by: AIPython",
                "=" * 50,
                ""
            ]
            
            for section_title, content in sections.items():
                report_lines.append(f"## {section_title}")
                report_lines.append("")
                
                if isinstance(content, str):
                    report_lines.append(content)
                elif isinstance(content, (list, tuple)):
                    for item in content:
                        report_lines.append(f"- {item}")
                elif isinstance(content, dict):
                    for key, value in content.items():
                        report_lines.append(f"- {key}: {value}")
                else:
                    report_lines.append(str(content))
                
                report_lines.append("")
            
            # Save report
            timestamp_file = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"report_{timestamp_file}.md"
            filepath = self.workspace_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(report_lines))
            
            if self.verbose:
                print(f"📋 Report saved: {filepath}")
            self.saved_files.append(str(filepath))
            return str(filepath)
        
        def safe_profiler(func, *args, **kwargs):
            """Safe profiler that handles conflicts."""
            import cProfile
            import pstats
            import io
            import sys
            
            # Check if profiler is already active
            if hasattr(sys, '_getframe'):
                frame = sys._getframe()
                while frame:
                    if 'profile' in str(frame.f_code.co_filename).lower():
                        print("Warning: Profiler already active. Skipping profiling.")
                        return func(*args, **kwargs)
                    frame = frame.f_back
            
            try:
                pr = cProfile.Profile()
                pr.enable()
                result = func(*args, **kwargs)
                pr.disable()
                
                s = io.StringIO()
                ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
                ps.print_stats(10)  # Only show top 10
                print("Profiling Results:")
                print(s.getvalue())
                return result
            except Exception as e:
                print(f"Profiling failed: {e}")
                return func(*args, **kwargs)
        
        def ensure_nltk_data():
            """Ensure NLTK data is downloaded."""
            import nltk
            
            required_datasets = ['punkt', 'punkt_tab', 'stopwords', 'vader_lexicon', 'wordnet']
            
            for dataset in required_datasets:
                try:
                    nltk.data.find(f'tokenizers/{dataset}' if 'punkt' in dataset else f'corpora/{dataset}' if dataset in ['stopwords', 'wordnet'] else f'vader_lexicon/{dataset}')
                except LookupError:
                    try:
                        print(f"Downloading NLTK {dataset}...")
                        nltk.download(dataset, quiet=True)
                    except Exception as e:
                        print(f"Warning: Could not download {dataset}: {e}")
        
        def safe_color_conversion(image, target_mode):
            """Safe color space conversion that handles unsupported conversions."""
            from PIL import Image
            import numpy as np
            
            # Supported conversions in PIL
            supported_modes = ['RGB', 'RGBA', 'L', 'P', 'CMYK', 'YCbCr', 'LAB', 'HSV']
            
            if target_mode not in supported_modes:
                print(f"Warning: {target_mode} not supported. Converting to RGB instead.")
                target_mode = 'RGB'
            
            try:
                return image.convert(target_mode)
            except ValueError as e:
                print(f"Error converting to {target_mode}: {e}")
                print("Falling back to RGB conversion.")
                return image.convert('RGB')
        
        # Add functions to namespace
        self.global_namespace.update({
            'save_plot': save_plot,
            'save_dataframe': save_dataframe,
            'load_data': load_data,
            'display_results': display_results,
            'create_report': create_report,
            'safe_profiler': safe_profiler,
            'ensure_nltk_data': ensure_nltk_data,
            'safe_color_conversion': safe_color_conversion,
        })
    
    def ask(self, 
            question: str, 
            show_code: bool = True,
            execute: bool = True,
            install_missing: bool = None) -> Any:
        """
        Ask AIPython to perform any Python task.
        
        Args:
            question: Natural language description of the task
            show_code: Whether to display generated code
            execute: Whether to execute the code automatically
            install_missing: Override auto_install setting
            
        Returns:
            Result of the execution or generated code
        """
        if install_missing is None:
            install_missing = self.auto_install
            
        if self.verbose:
            print(f"🤖 AIPython processing: {question}")
        
        start_time = time.time()
        operation = {
            'question': question,
            'timestamp': time.time(),
            'attempts': 0,
            'success': False,
            'code': None,
            'result': None,
            'errors': [],
            'packages_installed': []
        }
        
        try:
            # Generate code
            code = self._generate_code(question)
            operation['code'] = code
            
            if show_code:
                print(f"\n💻 Generated Code:")
                print("```python")
                print(code)
                print("```")
            
            if execute:
                # Execute with retry logic
                result = self._execute_with_retry(code, operation, install_missing)
                operation['result'] = result
                operation['success'] = True
                
                execution_time = time.time() - start_time
                operation['execution_time'] = execution_time
                
                if self.verbose:
                    print(f"✅ Execution completed in {execution_time:.2f}s")
                
                self.execution_history.append(operation)
                return result
            else:
                self.execution_history.append(operation)
                return code
                
        except Exception as e:
            operation['errors'].append(str(e))
            operation['execution_time'] = time.time() - start_time
            self.execution_history.append(operation)
            
            if self.verbose:
                print(f"❌ Error: {e}")
            
            raise e
    
    def _generate_code(self, question: str) -> str:
        """Generate Python code for the given question."""
        # Create context about available packages and environment
        available_packages = list(self.installed_packages) + [
            'pandas', 'numpy', 'matplotlib', 'seaborn', 'requests', 'sklearn', 
            'plotly', 'scipy', 'statsmodels', 'beautifulsoup4'
        ]
        
        # Get recent execution context
        recent_operations = []
        if self.execution_history:
            recent_operations = [op['question'] for op in self.execution_history[-3:]]
        
        helper_functions = [
            "save_plot(filename=None) - Save matplotlib plots",
            "save_dataframe(df, filename=None, format='csv') - Save DataFrames", 
            "load_data(filepath) - Smart data loader for CSV/Excel/JSON/Parquet",
            "display_results(*args) - Enhanced display for results",
            "create_report(title, sections) - Generate formatted reports",
            "workspace_dir - Current workspace directory path"
        ]
        
        prompt = f"""
You are AIPython, an expert Python assistant that generates complete, executable Python code.

USER REQUEST: "{question}"

CONTEXT:
- Available packages: {', '.join(available_packages)}
- Recent operations: {', '.join(recent_operations) if recent_operations else 'None'}
- Execution environment: Jupyter-like with global namespace
- Workspace directory: Available as 'workspace_dir' variable
- Helper functions available:
  {chr(10).join(['  ' + func for func in helper_functions])}

INSTRUCTIONS:
1. Generate complete, executable Python code
2. Import all required packages at the top
3. Include error handling where appropriate
4. For plots: use plt.figure(), create clear visualizations, and use save_plot() if permanent storage needed
5. For data analysis: return results or use display_results() for enhanced output
6. Make code self-contained and robust
7. Add comments for complex operations
8. Handle edge cases and potential errors
9. Use helper functions when appropriate (save_dataframe, load_data, create_report)
10. For file operations: use workspace_dir for saving files

IMPORTANT RULES:
- Return ONLY Python code, no explanations
- Use 'result = ' for final output to be returned
- For visualizations: create clear, labeled plots with titles and legends
- For data operations: ensure proper formatting and meaningful variable names
- For web scraping: include proper headers and error handling
- For ML: include basic evaluation and interpretation
- For complex analyses: use display_results() to show intermediate steps
- For reports: use create_report() to generate formatted output

COMMON PATTERNS:
- Data loading: df = load_data('filename.csv')
- Plotting: plt.figure(figsize=(10,6)); ...; save_plot('chart.png')
- Saving results: save_dataframe(results_df, 'analysis_results.csv')
- Reports: create_report('Analysis Title', {{'Summary': summary, 'Results': results}})

CODE:
```python
"""

        try:
            response = self.llm_provider.generate(prompt)
            code = response.strip()
            
            # Clean the code
            if '```python' in code:
                code = code.split('```python')[1].split('```')[0].strip()
            elif '```' in code:
                code = code.split('```')[1].strip()
            
            return code
            
        except Exception as e:
            raise Exception(f"Code generation failed: {e}")
    
    def _execute_with_retry(self, code: str, operation: Dict, install_missing: bool) -> Any:
        """Execute code with retry logic for package installation."""
        last_error = None
        
        for attempt in range(self.max_retries):
            operation['attempts'] = attempt + 1
            
            try:
                if self.verbose and attempt > 0:
                    print(f"🔄 Retry attempt {attempt + 1}/{self.max_retries}")
                
                return self._execute_code(code)
                
            except ImportError as e:
                if install_missing and attempt < self.max_retries - 1:
                    package_name = self._extract_package_name(str(e))
                    if package_name and package_name not in self.installed_packages:
                        if self._install_package(package_name):
                            operation['packages_installed'].append(package_name)
                            continue
                
                last_error = e
                operation['errors'].append(f"Attempt {attempt + 1}: {str(e)}")
                
            except Exception as e:
                last_error = e
                operation['errors'].append(f"Attempt {attempt + 1}: {str(e)}")
                
                # Try to fix common issues automatically
                if attempt < self.max_retries - 1:
                    fixed_code = self._auto_fix_code(code, str(e))
                    if fixed_code != code:
                        if self.verbose:
                            print(f"🔧 Auto-fixing code error...")
                        code = fixed_code
                        continue
        
        # If all retries failed, raise the last error
        raise last_error
    
    def _execute_code(self, code: str) -> Any:
        """Execute Python code safely."""
        # Capture stdout and stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        
        stdout_capture = StringIO()
        stderr_capture = StringIO()
        
        try:
            # Redirect output
            sys.stdout = stdout_capture
            sys.stderr = stderr_capture
            
            # Execute code
            exec(code, self.global_namespace)
            
            # Get output
            stdout_output = stdout_capture.getvalue()
            stderr_output = stderr_capture.getvalue()
            
            # Restore stdout/stderr
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            
            # Display outputs with better formatting
            if stdout_output.strip():
                if self.use_rich:
                    self.console.print(stdout_output.strip())
                else:
                    print(stdout_output.strip())
            
            if stderr_output.strip():
                warning_text = f"⚠️ Warnings:\n{stderr_output.strip()}"
                if self.use_rich:
                    self.console.print(warning_text, style="yellow")
                else:
                    print(warning_text)
            
            # Return result if available
            if 'result' in self.global_namespace:
                result = self.global_namespace['result']
                # Clear result for next execution
                del self.global_namespace['result']
                
                # Show the result if it's not already displayed
                if result is not None and str(result) not in stdout_output:
                    if self.use_rich:
                        self.console.print(f"📊 Result: {result}", style="green")
                    else:
                        print(f"📊 Result: {result}")
                
                return result
            
            return "✅ Code executed successfully"
            
        except Exception as e:
            # Restore stdout/stderr
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            
            # Show any captured output before the error
            stdout_output = stdout_capture.getvalue()
            stderr_output = stderr_capture.getvalue()
            
            if stdout_output:
                print(stdout_output)
            if stderr_output:
                print(f"⚠️ Warnings: {stderr_output}")
            
            raise e
        
        finally:
            stdout_capture.close()
            stderr_capture.close()
    
    def _extract_package_name(self, error_msg: str) -> Optional[str]:
        """Extract package name from ImportError message."""
        import re
        
        # Common patterns for import errors
        patterns = [
            r"No module named '([^']+)'",
            r"cannot import name '([^']+)'",
            r"ModuleNotFoundError: No module named '([^']+)'"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, error_msg)
            if match:
                module_name = match.group(1)
                # Handle submodules (e.g., 'sklearn.datasets' -> 'scikit-learn')
                package_map = {
                    'sklearn': 'scikit-learn',
                    'cv2': 'opencv-python',
                    'PIL': 'Pillow',
                    'bs4': 'beautifulsoup4',
                    'requests_html': 'requests-html',
                    'plotly': 'plotly',
                    'dash': 'dash',
                    'streamlit': 'streamlit',
                    'fastapi': 'fastapi',
                    'flask': 'flask',
                    'django': 'django',
                    'sqlalchemy': 'sqlalchemy',
                    'psycopg2': 'psycopg2-binary',
                    'pymongo': 'pymongo',
                    'redis': 'redis',
                    'celery': 'celery',
                    'pytest': 'pytest',
                    'black': 'black',
                    'flake8': 'flake8',
                    'mypy': 'mypy',
                    'jupyter': 'jupyter',
                    'notebook': 'notebook',
                    'ipywidgets': 'ipywidgets',
                    'folium': 'folium',
                    'wordcloud': 'wordcloud',
                    'textblob': 'textblob',
                    'spacy': 'spacy',
                    'nltk': 'nltk',
                    'transformers': 'transformers',
                    'torch': 'torch',
                    'tensorflow': 'tensorflow',
                    'keras': 'keras',
                    'xgboost': 'xgboost',
                    'lightgbm': 'lightgbm',
                    'catboost': 'catboost',
                    'optuna': 'optuna',
                    'mlflow': 'mlflow',
                    'wandb': 'wandb',
                    'streamlit': 'streamlit',
                    'gradio': 'gradio',
                    'voila': 'voila',
                    'bokeh': 'bokeh',
                    'altair': 'altair',
                    'pygments': 'pygments',
                    'markdown': 'markdown',
                    'jinja2': 'jinja2',
                    'click': 'click',
                    'typer': 'typer',
                    'pydantic': 'pydantic',
                    'httpx': 'httpx',
                    'aiohttp': 'aiohttp',
                    'asyncio': 'asyncio',  # Built-in, but listed for completeness
                }
                
                base_module = module_name.split('.')[0]
                return package_map.get(base_module, base_module)
        
        return None
    
    def _install_package(self, package_name: str) -> bool:
        """Install a Python package with user permission and progress tracking."""
        
        # Ask for permission if enabled
        if self.ask_permission:
            if self.environment == 'jupyter':
                response = input(f"📦 Install package '{package_name}'? (y/n): ").lower().strip()
                permission = response in ['y', 'yes']
            elif self.use_rich and self.console:
                permission = Confirm.ask(f"📦 Install package '{package_name}'?", console=self.console)
            else:
                response = input(f"📦 Install package '{package_name}'? (y/n): ").lower().strip()
                permission = response in ['y', 'yes']
            
            if not permission:
                if self.verbose:
                    self._log_warning(f"Package installation declined for {package_name}. Trying alternative approach.")
                return False
        
        # Installation with progress tracking
        def install_with_progress():
            try:
                # For large packages, use longer timeout
                timeout = 300 if package_name in ['tensorflow', 'torch', 'transformers'] else 120
                
                result = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', package_name
                ], capture_output=True, text=True, timeout=timeout)
                
                return result.returncode == 0, result.stderr if result.returncode != 0 else ""
                
            except subprocess.TimeoutExpired:
                return False, f"Installation timeout after {timeout}s"
            except Exception as e:
                return False, str(e)
        
        # Show progress based on environment
        if self.use_rich and self.console and self.environment != 'jupyter':
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TimeRemainingColumn(),
                console=self.console
            ) as progress:
                task = progress.add_task(f"Installing {package_name}...", total=None)
                
                success, error_msg = install_with_progress()
                
                if success:
                    progress.update(task, description=f"✅ Installed {package_name}")
                    self.installed_packages.add(package_name)
                    
                    # Try to import the package to update global namespace
                    try:
                        module = importlib.import_module(package_name)
                        self.global_namespace[package_name] = module
                    except:
                        pass  # Some packages can't be imported directly
                    
                    return True
                else:
                    progress.update(task, description=f"❌ Failed to install {package_name}")
                    if self.verbose:
                        self._log_error(f"Failed to install {package_name}: {error_msg}")
                    return False
        else:
            # Simple installation for Jupyter or when rich is not available
            if self.verbose:
                self._log_info(f"📦 Installing package: {package_name}...")
            
            success, error_msg = install_with_progress()
            
            if success:
                self.installed_packages.add(package_name)
                if self.verbose:
                    self._log_success(f"Successfully installed {package_name}")
                
                # Try to import the package to update global namespace
                try:
                    module = importlib.import_module(package_name)
                    self.global_namespace[package_name] = module
                except:
                    pass  # Some packages can't be imported directly
                
                return True
            else:
                if self.verbose:
                    self._log_error(f"Failed to install {package_name}: {error_msg}")
                return False
    
    def _auto_fix_code(self, code: str, error_msg: str) -> str:
        """Attempt to automatically fix common code issues."""
        fixed_code = code
        
        # Fix matplotlib display issues
        if "figure" in error_msg.lower() or "plot" in error_msg.lower():
            if "plt.show()" not in fixed_code:
                fixed_code = fixed_code.replace("plt.plot", "plt.figure()\nplt.plot")
                fixed_code += "\nplt.show()"
        
        # Fix pandas display issues
        if "dataframe" in error_msg.lower():
            if "display(" not in fixed_code and "print(" not in fixed_code:
                fixed_code += "\nprint(result)"
        
        return fixed_code
    
    def get_execution_history(self) -> List[Dict]:
        """Get the execution history."""
        return self.execution_history
    
    def get_summary(self) -> str:
        """Get a summary of all executed operations."""
        if not self.execution_history:
            return "No operations executed yet."
        
        total_ops = len(self.execution_history)
        successful_ops = sum(1 for op in self.execution_history if op['success'])
        packages_installed = set()
        
        for op in self.execution_history:
            packages_installed.update(op.get('packages_installed', []))
        
        total_time = sum(op.get('execution_time', 0) for op in self.execution_history)
        
        summary = f"""
🤖 AIPython Session Summary
==========================
📊 Total Operations: {total_ops}
✅ Successful: {successful_ops}/{total_ops} ({successful_ops/total_ops*100:.1f}%)
📦 Packages Installed: {len(packages_installed)} ({', '.join(packages_installed) if packages_installed else 'None'})
⏱️ Total Execution Time: {total_time:.2f}s
🔧 Model Used: {self.model_name}

Recent Operations:
"""
        
        # Show last 3 operations
        for op in self.execution_history[-3:]:
            status = "✅" if op['success'] else "❌"
            summary += f"  {status} {op['question'][:50]}...\n"
        
        return summary
    
    def clear_history(self):
        """Clear execution history."""
        self.execution_history = []
        if self.verbose:
            print("🗑️ Execution history cleared")
    
    def reset_environment(self):
        """Reset the execution environment."""
        self.global_namespace.clear()
        self._setup_environment()
        if self.verbose:
            print("🔄 Execution environment reset")
    
    def install_package(self, package_name: str) -> bool:
        """Manually install a package."""
        return self._install_package(package_name)
    
    def create_dashboard(self, data_description: str, chart_types: List[str] = None) -> Any:
        """Create an interactive dashboard with multiple visualizations."""
        if chart_types is None:
            chart_types = ["bar", "line", "scatter", "histogram"]
        
        dashboard_request = f"""
Create an interactive dashboard for: {data_description}

Include the following chart types: {', '.join(chart_types)}
Use Plotly for interactivity with:
- Hover information
- Zoom and pan capabilities
- Professional styling
- Clear titles and labels
- Color coding where appropriate

Return the dashboard as a Plotly figure that can be displayed.
"""
        
        return self.ask(dashboard_request, show_code=True, execute=True)
    
    def analyze_data(self, data_source: str, analysis_type: str = "comprehensive") -> Any:
        """Perform automated data analysis."""
        analysis_request = f"""
Perform {analysis_type} data analysis on: {data_source}

Include:
1. Data overview (shape, types, missing values)
2. Descriptive statistics
3. Data quality assessment
4. Correlation analysis
5. Distribution analysis
6. Outlier detection
7. Key insights and recommendations
8. Visualizations for each analysis step

Generate a comprehensive report with findings.
"""
        
        return self.ask(analysis_request, show_code=True, execute=True)
    
    def build_ml_model(self, task_description: str, model_type: str = "auto") -> Any:
        """Build and evaluate a machine learning model."""
        ml_request = f"""
Build a machine learning model for: {task_description}

Model type: {model_type}

Include complete ML workflow:
1. Data preprocessing and feature engineering
2. Train/validation/test split
3. Model selection and training
4. Hyperparameter tuning (if appropriate)
5. Model evaluation with metrics
6. Feature importance analysis
7. Predictions on test set
8. Model interpretation and insights
9. Visualizations of results

Provide recommendations for model improvement.
"""
        
        return self.ask(ml_request, show_code=True, execute=True)
    
    def scrape_web_data(self, url_or_description: str, data_format: str = "dataframe") -> Any:
        """Scrape and process web data."""
        scraping_request = f"""
Scrape web data from: {url_or_description}

Requirements:
1. Use appropriate libraries (requests, beautifulsoup4, selenium if needed)
2. Include proper error handling and rate limiting
3. Respect robots.txt and add appropriate delays
4. Clean and structure the data
5. Convert to {data_format} format
6. Handle different data types appropriately
7. Validate data quality
8. Save results for future use

Include data preview and summary statistics.
"""
        
        return self.ask(scraping_request, show_code=True, execute=True)
    
    def generate_report(self, topic: str, data_sources: List[str] = None, format: str = "markdown") -> str:
        """Generate a comprehensive analytical report."""
        if data_sources is None:
            data_sources = ["analysis results from current session"]
        
        report_request = f"""
Generate a comprehensive {format} report on: {topic}

Data sources: {', '.join(data_sources)}

Report structure:
1. Executive Summary
2. Methodology
3. Key Findings
4. Detailed Analysis
5. Visualizations and Charts
6. Insights and Recommendations
7. Conclusion
8. Appendices (if needed)

Make it professional and well-formatted.
Save the report using create_report() function.
"""
        
        result = self.ask(report_request, show_code=True, execute=True)
        return result
    
    def optimize_performance(self, code_or_data: str) -> Any:
        """Analyze and optimize Python code or data operations."""
        optimization_request = f"""
Analyze and optimize: {code_or_data}

Performance optimization areas:
1. Code efficiency and algorithmic improvements
2. Memory usage optimization
3. Pandas operations optimization
4. Vectorization opportunities
5. Parallel processing possibilities
6. Data structure improvements
7. I/O operation optimization
8. Caching strategies

Provide before/after comparisons and performance metrics.
"""
        
        return self.ask(optimization_request, show_code=True, execute=True)
    
    def export_session(self, filename: str = None) -> str:
        """Export the entire session including history, results, and files."""
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"aipython_session_{timestamp}.json"
        
        session_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "model": self.model_name,
            "execution_history": self.execution_history,
            "installed_packages": list(self.installed_packages),
            "saved_files": self.saved_files,
            "workspace_dir": str(self.workspace_dir)
        }
        
        filepath = self.workspace_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, default=str)
        
        if self.verbose:
            print(f"💾 Session exported: {filepath}")
        
        return str(filepath)
    
    def load_session(self, filename: str) -> bool:
        """Load a previously exported session."""
        try:
            filepath = Path(filename)
            if not filepath.exists():
                filepath = self.workspace_dir / filename
            
            with open(filepath, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            # Restore session data
            self.execution_history = session_data.get("execution_history", [])
            self.installed_packages = set(session_data.get("installed_packages", []))
            self.saved_files = session_data.get("saved_files", [])
            
            if self.verbose:
                print(f"✅ Session loaded from: {filepath}")
                print(f"   Operations: {len(self.execution_history)}")
                print(f"   Packages: {len(self.installed_packages)}")
                print(f"   Files: {len(self.saved_files)}")
            
            return True
            
        except Exception as e:
            if self.verbose:
                print(f"❌ Failed to load session: {e}")
            return False
    
    def get_saved_files(self) -> List[str]:
        """Get list of all saved files in this session."""
        return self.saved_files.copy()
    
    def get_workspace_info(self) -> Dict[str, Any]:
        """Get information about the current workspace."""
        workspace_files = list(self.workspace_dir.glob("*"))
        
        return {
            "workspace_dir": str(self.workspace_dir),
            "total_files": len(workspace_files),
            "saved_files": len(self.saved_files),
            "execution_history": len(self.execution_history),
            "installed_packages": len(self.installed_packages),
            "file_types": {
                ext: len([f for f in workspace_files if f.suffix == ext])
                for ext in set(f.suffix for f in workspace_files if f.suffix)
            }
        }
    
    def __repr__(self) -> str:
        return f"AIPython(provider={self.provider_name}, model={self.model_name}, environment={self.environment}, operations={len(self.execution_history)}, workspace={self.workspace_dir.name})"

    # =============================================
    # ADVANCED FEATURES AND UTILITIES
    # =============================================
    
    def create_ml_pipeline(self, problem_type: str, data_description: str, 
                          target_variable: str = None, validation_split: float = 0.2) -> Any:
        """Create a complete machine learning pipeline."""
        pipeline_request = f"""
Create a complete machine learning pipeline for {problem_type} problem:

Data: {data_description}
Target Variable: {target_variable if target_variable else "auto-detect"}
Validation Split: {validation_split}

Include:
1. Data loading and preprocessing
2. Feature engineering and selection
3. Model selection and training
4. Hyperparameter tuning
5. Cross-validation
6. Model evaluation with metrics
7. Feature importance analysis
8. Model interpretation (SHAP if applicable)
9. Performance visualization
10. Model persistence (save/load)

Use appropriate algorithms for {problem_type} and provide detailed analysis.
"""
        return self.ask(pipeline_request, show_code=True, execute=True)
    
    def create_api_client(self, api_type: str, endpoint: str, auth_method: str = "none") -> Any:
        """Create a robust API client with error handling and retry logic."""
        api_request = f"""
Create a robust API client for {api_type}:

Endpoint: {endpoint}
Authentication: {auth_method}

Include:
1. Request/response handling
2. Authentication management
3. Rate limiting and retry logic
4. Error handling and logging
5. Data validation
6. Caching mechanisms
7. Async support if beneficial
8. Response parsing
9. Timeout handling
10. Usage examples

Make it production-ready with proper error messages and documentation.
"""
        return self.ask(api_request, show_code=True, execute=True)
    
    def create_data_pipeline(self, source_type: str, destination_type: str, 
                           transformation_rules: str = "standard cleaning") -> Any:
        """Create an ETL data pipeline."""
        pipeline_request = f"""
Create a robust ETL data pipeline:

Source: {source_type}
Destination: {destination_type}
Transformations: {transformation_rules}

Include:
1. Data extraction with validation
2. Data cleaning and preprocessing
3. Data transformation and enrichment
4. Data quality checks
5. Error handling and logging
6. Performance monitoring
7. Data lineage tracking
8. Incremental loading
9. Rollback mechanisms
10. Automated testing

Make it scalable and maintainable.
"""
        return self.ask(pipeline_request, show_code=True, execute=True)
    
    def generate_report(self, report_type: str, data_analysis: str, 
                       format_type: str = "markdown") -> Any:
        """Generate comprehensive reports with visualizations."""
        report_request = f"""
Generate a comprehensive {report_type} report:

Analysis: {data_analysis}
Format: {format_type}

Include:
1. Executive summary
2. Key findings and insights
3. Statistical analysis
4. Data visualizations
5. Recommendations
6. Technical appendix
7. Methodology section
8. Risk assessment
9. Future considerations
10. Interactive elements if applicable

Make it professional and presentation-ready.
"""
        return self.ask(report_request, show_code=True, execute=True)
    
    def create_web_scraper(self, target_site: str, data_to_extract: str, 
                          respect_robots: bool = True) -> Any:
        """Create an intelligent web scraper with best practices."""
        scraper_request = f"""
Create an intelligent web scraper:

Target Site: {target_site}
Data to Extract: {data_to_extract}
Respect robots.txt: {respect_robots}

Include:
1. Robots.txt compliance
2. Rate limiting and delays
3. User agent rotation
4. Session management
5. Error handling and retries
6. Data validation and cleaning
7. Progress tracking
8. Output formatting
9. Concurrent processing (if appropriate)
10. Legal compliance checks

Use appropriate libraries and follow ethical scraping practices.
"""
        return self.ask(scraper_request, show_code=True, execute=True)
    
    def create_recommendation_system(self, system_type: str, data_description: str, 
                                   algorithm: str = "collaborative_filtering") -> Any:
        """Create a recommendation system."""
        rec_request = f"""
Create a {system_type} recommendation system:

Data: {data_description}
Algorithm: {algorithm}

Include:
1. Data preprocessing and feature engineering
2. Model training and validation
3. Similarity calculations
4. Cold start handling
5. Evaluation metrics (precision, recall, MAP)
6. Real-time recommendation serving
7. A/B testing framework
8. Performance optimization
9. Bias detection and mitigation
10. Explainable recommendations

Provide complete implementation with examples.
"""
        return self.ask(rec_request, show_code=True, execute=True)
    
    def create_time_series_forecaster(self, data_description: str, 
                                    forecast_horizon: int = 30, 
                                    model_type: str = "auto") -> Any:
        """Create a time series forecasting system."""
        forecast_request = f"""
Create a comprehensive time series forecasting system:

Data: {data_description}
Forecast Horizon: {forecast_horizon} periods
Model Type: {model_type}

Include:
1. Time series analysis and decomposition
2. Stationarity testing and transformation
3. Feature engineering (lags, rolling stats, seasonality)
4. Multiple model evaluation (ARIMA, Prophet, LSTM, etc.)
5. Hyperparameter optimization
6. Cross-validation for time series
7. Forecast uncertainty quantification
8. Model interpretation and diagnostics
9. Automated model selection
10. Production deployment code

Provide accuracy metrics and confidence intervals.
"""
        return self.ask(forecast_request, show_code=True, execute=True)
    
    def create_nlp_processor(self, task_type: str, language: str = "english", 
                           domain: str = "general") -> Any:
        """Create an NLP processing system."""
        nlp_request = f"""
Create a comprehensive NLP processing system for {task_type}:

Language: {language}
Domain: {domain}

Include:
1. Text preprocessing and cleaning
2. Tokenization and normalization
3. Feature extraction (TF-IDF, embeddings)
4. Model training and evaluation
5. Named entity recognition
6. Sentiment analysis
7. Topic modeling
8. Text classification
9. Language detection
10. Performance benchmarking

Use state-of-the-art models and provide evaluation metrics.
"""
        return self.ask(nlp_request, show_code=True, execute=True)
    
    def create_computer_vision_system(self, task_type: str, 
                                    input_type: str = "images") -> Any:
        """Create a computer vision system."""
        cv_request = f"""
Create a computer vision system for {task_type}:

Input Type: {input_type}

Include:
1. Image preprocessing and augmentation
2. Model architecture design
3. Training and validation pipeline
4. Transfer learning implementation
5. Performance evaluation
6. Inference optimization
7. Real-time processing capabilities
8. Error analysis and visualization
9. Model interpretation techniques
10. Deployment preparation

Use modern deep learning frameworks and best practices.
"""
        return self.ask(cv_request, show_code=True, execute=True)
    
    def create_database_manager(self, db_type: str, operations: List[str]) -> Any:
        """Create a database management system."""
        db_request = f"""
Create a comprehensive database manager for {db_type}:

Operations: {', '.join(operations)}

Include:
1. Connection management and pooling
2. Query building and optimization
3. Transaction handling
4. Migration management
5. Backup and recovery
6. Performance monitoring
7. Security and access control
8. Data validation
9. Logging and auditing
10. Error handling and recovery

Provide ORM integration and raw SQL capabilities.
"""
        return self.ask(db_request, show_code=True, execute=True)
    
    def create_testing_suite(self, code_type: str, coverage_target: float = 0.9) -> Any:
        """Create a comprehensive testing suite."""
        test_request = f"""
Create a comprehensive testing suite for {code_type}:

Coverage Target: {coverage_target * 100}%

Include:
1. Unit tests with high coverage
2. Integration tests
3. Performance tests
4. Security tests
5. API tests
6. End-to-end tests
7. Mock and fixture setup
8. Test data generation
9. Continuous testing pipeline
10. Test reporting and analytics

Use appropriate testing frameworks and best practices.
"""
        return self.ask(test_request, show_code=True, execute=True)
    
    def create_monitoring_system(self, system_type: str, metrics: List[str]) -> Any:
        """Create a monitoring and alerting system."""
        monitor_request = f"""
Create a monitoring system for {system_type}:

Metrics to Track: {', '.join(metrics)}

Include:
1. Metrics collection and aggregation
2. Real-time dashboards
3. Alerting and notifications
4. Log analysis and correlation
5. Performance trending
6. Anomaly detection
7. Health checks and probes
8. Incident response automation
9. Historical data analysis
10. Cost and resource optimization

Provide visualization and reporting capabilities.
"""
        return self.ask(monitor_request, show_code=True, execute=True)
    
    def create_security_scanner(self, scan_type: str, target_description: str) -> Any:
        """Create a security scanning system."""
        security_request = f"""
Create a security scanning system for {scan_type}:

Target: {target_description}

Include:
1. Vulnerability assessment
2. Penetration testing automation
3. Code security analysis
4. Dependency vulnerability scanning
5. Configuration security checks
6. Compliance validation
7. Threat modeling
8. Risk assessment
9. Security reporting
10. Remediation recommendations

Follow security best practices and standards.
"""
        return self.ask(security_request, show_code=True, execute=True)
    
    def create_deployment_pipeline(self, app_type: str, platform: str = "cloud") -> Any:
        """Create a CI/CD deployment pipeline."""
        deploy_request = f"""
Create a CI/CD deployment pipeline for {app_type} on {platform}:

Include:
1. Source code management integration
2. Automated building and testing
3. Quality gates and code analysis
4. Security scanning
5. Environment management
6. Blue-green deployment
7. Rollback mechanisms
8. Performance testing
9. Monitoring and alerting
10. Documentation generation

Use modern DevOps practices and tools.
"""
        return self.ask(deploy_request, show_code=True, execute=True)
    
    def optimize_performance(self, code_description: str, 
                           optimization_type: str = "speed") -> Any:
        """Optimize code for performance."""
        optimize_request = f"""
Optimize performance for: {code_description}

Optimization Focus: {optimization_type}

Include:
1. Performance profiling and analysis
2. Algorithm optimization
3. Memory usage optimization
4. CPU utilization improvements
5. I/O optimization
6. Caching strategies
7. Parallel processing
8. Code refactoring
9. Benchmarking and testing
10. Performance monitoring

Provide before/after comparisons and metrics.
"""
        return self.ask(optimize_request, show_code=True, execute=True)
    
    def create_microservice(self, service_name: str, functionality: str, 
                          api_type: str = "REST") -> Any:
        """Create a microservice with full implementation."""
        microservice_request = f"""
Create a {service_name} microservice:

Functionality: {functionality}
API Type: {api_type}

Include:
1. Service architecture design
2. API endpoint implementation
3. Data persistence layer
4. Authentication and authorization
5. Input validation and error handling
6. Logging and monitoring
7. Health checks and metrics
8. Documentation (OpenAPI/Swagger)
9. Testing suite
10. Containerization (Docker)

Follow microservice best practices and patterns.
"""
        return self.ask(microservice_request, show_code=True, execute=True)
    
    def create_blockchain_application(self, app_type: str, blockchain: str = "ethereum") -> Any:
        """Create a blockchain application."""
        blockchain_request = f"""
Create a blockchain application for {app_type} on {blockchain}:

Include:
1. Smart contract development
2. Web3 integration
3. Wallet connectivity
4. Transaction handling
5. Event monitoring
6. Gas optimization
7. Security best practices
8. Testing framework
9. Frontend integration
10. Deployment scripts

Use current blockchain development standards.
"""
        return self.ask(blockchain_request, show_code=True, execute=True)
    
    def create_game_engine(self, game_type: str, platform: str = "desktop") -> Any:
        """Create a game engine or game."""
        game_request = f"""
Create a {game_type} game for {platform}:

Include:
1. Game architecture and design patterns
2. Rendering system
3. Physics engine integration
4. Input handling
5. Audio system
6. Game state management
7. Asset management
8. AI and game logic
9. Multiplayer capabilities (if applicable)
10. Performance optimization

Use appropriate game development frameworks.
"""
        return self.ask(game_request, show_code=True, execute=True)
    
    def create_iot_system(self, device_type: str, data_processing: str) -> Any:
        """Create an IoT system."""
        iot_request = f"""
Create an IoT system for {device_type}:

Data Processing: {data_processing}

Include:
1. Device communication protocols
2. Data collection and transmission
3. Real-time data processing
4. Cloud integration
5. Device management
6. Security and encryption
7. Analytics and visualization
8. Alert and notification system
9. Remote monitoring
10. Scalability considerations

Use appropriate IoT frameworks and platforms.
"""
        return self.ask(iot_request, show_code=True, execute=True)
    
    def create_chatbot(self, bot_type: str, domain: str, platform: str = "web") -> Any:
        """Create an intelligent chatbot."""
        chatbot_request = f"""
Create a {bot_type} chatbot for {domain} on {platform}:

Include:
1. Natural language understanding
2. Intent recognition and classification
3. Entity extraction
4. Dialogue management
5. Response generation
6. Context awareness
7. Multi-turn conversations
8. Integration with external APIs
9. Analytics and improvement
10. Deployment and scaling

Use modern NLP and conversational AI techniques.
"""
        return self.ask(chatbot_request, show_code=True, execute=True)
    
    def create_automation_script(self, task_description: str, 
                               schedule: str = "on-demand") -> Any:
        """Create an automation script."""
        automation_request = f"""
Create an automation script for: {task_description}

Schedule: {schedule}

Include:
1. Task orchestration and workflow
2. Error handling and recovery
3. Logging and monitoring
4. Configuration management
5. Notification system
6. Progress tracking
7. Resource management
8. Security considerations
9. Testing and validation
10. Documentation and maintenance

Make it robust and production-ready.
"""
        return self.ask(automation_request, show_code=True, execute=True)
    
    def create_data_visualizer(self, data_type: str, chart_types: List[str], 
                             interactive: bool = True) -> Any:
        """Create an advanced data visualization system."""
        viz_request = f"""
Create an advanced data visualization system:

Data Type: {data_type}
Chart Types: {', '.join(chart_types)}
Interactive: {interactive}

Include:
1. Dynamic data binding
2. Interactive controls and filters
3. Real-time updates
4. Multiple visualization libraries
5. Custom chart components
6. Export capabilities
7. Responsive design
8. Performance optimization
9. Accessibility features
10. Theme and styling options

Create both static and interactive visualizations.
"""
        return self.ask(viz_request, show_code=True, execute=True)
    
    def benchmark_system(self, system_description: str, 
                        metrics: List[str] = None) -> Any:
        """Create a comprehensive benchmarking system."""
        if metrics is None:
            metrics = ["speed", "memory", "accuracy", "throughput"]
            
        benchmark_request = f"""
Create a benchmarking system for: {system_description}

Metrics: {', '.join(metrics)}

Include:
1. Performance baseline establishment
2. Load testing and stress testing
3. Memory profiling
4. CPU utilization analysis
5. I/O performance testing
6. Scalability testing
7. Comparative analysis
8. Report generation
9. Trend analysis
10. Optimization recommendations

Provide detailed performance insights and recommendations.
"""
        return self.ask(benchmark_request, show_code=True, execute=True)
    
    def create_neural_network(self, problem_type: str, architecture: str = "auto", 
                            framework: str = "tensorflow") -> Any:
        """Create a custom neural network."""
        nn_request = f"""
Create a neural network for {problem_type}:

Architecture: {architecture}
Framework: {framework}

Include:
1. Network architecture design
2. Layer configuration and optimization
3. Loss function selection
4. Optimizer configuration
5. Regularization techniques
6. Training pipeline
7. Validation and evaluation
8. Hyperparameter tuning
9. Model interpretation
10. Transfer learning capabilities

Use best practices for deep learning development.
"""
        return self.ask(nn_request, show_code=True, execute=True)
    
    def create_edge_computing_solution(self, use_case: str, 
                                     constraints: Dict[str, Any] = None) -> Any:
        """Create an edge computing solution."""
        if constraints is None:
            constraints = {"power": "low", "latency": "minimal", "bandwidth": "limited"}
            
        edge_request = f"""
Create an edge computing solution for: {use_case}

Constraints: {constraints}

Include:
1. Edge device optimization
2. Local data processing
3. Offline capability
4. Synchronization mechanisms
5. Resource management
6. Security at the edge
7. Model compression
8. Real-time processing
9. Network resilience
10. Cloud integration

Optimize for edge deployment constraints.
"""
        return self.ask(edge_request, show_code=True, execute=True)
    
    # =============================================
    # SPECIALIZED UTILITY METHODS
    # =============================================
    
    def quick_analysis(self, data_path: str) -> Any:
        """Quick data analysis with automatic insights."""
        return self.ask(f"Perform quick exploratory data analysis on {data_path} with key insights and visualizations")
    
    def quick_model(self, data_path: str, target: str, problem_type: str = "auto") -> Any:
        """Quick machine learning model creation."""
        return self.ask(f"Create and evaluate a {problem_type} model for {data_path} predicting {target}")
    
    def quick_viz(self, data_path: str, chart_type: str = "auto") -> Any:
        """Quick data visualization."""
        return self.ask(f"Create {chart_type} visualization for {data_path} with best practices")
    
    def quick_scrape(self, url: str, target_data: str) -> Any:
        """Quick web scraping."""
        return self.ask(f"Scrape {target_data} from {url} following ethical practices")
    
    def quick_api(self, api_url: str, operation: str = "get_data") -> Any:
        """Quick API interaction."""
        return self.ask(f"Create API client to {operation} from {api_url} with error handling")
    
    def quick_clean(self, data_path: str) -> Any:
        """Quick data cleaning."""
        return self.ask(f"Clean and preprocess data from {data_path} with quality report")
    
    def quick_report(self, analysis_topic: str) -> Any:
        """Quick report generation."""
        return self.ask(f"Generate comprehensive report on {analysis_topic} with visualizations")
    
    def code_review(self, code_description: str) -> Any:
        """Perform code review and provide improvements."""
        review_request = f"""
Perform comprehensive code review for: {code_description}

Include:
1. Code quality analysis
2. Performance optimization suggestions
3. Security vulnerability assessment
4. Best practices recommendations
5. Refactoring opportunities
6. Documentation improvements
7. Testing coverage analysis
8. Design pattern suggestions
9. Maintainability assessment
10. Compliance checking

Provide detailed feedback and improved code examples.
"""
        return self.ask(review_request, show_code=True, execute=True)
    
    def debug_assistant(self, error_description: str, code_context: str = "") -> Any:
        """Intelligent debugging assistance."""
        debug_request = f"""
Debug the following issue: {error_description}

Code Context: {code_context}

Provide:
1. Root cause analysis
2. Step-by-step debugging approach
3. Multiple solution approaches
4. Prevention strategies
5. Testing recommendations
6. Code examples with fixes
7. Performance considerations
8. Best practices to avoid similar issues
9. Monitoring and logging suggestions
10. Documentation updates

Include working code examples.
"""
        return self.ask(debug_request, show_code=True, execute=True)
    
    def architecture_advisor(self, system_requirements: str, 
                           constraints: str = "") -> Any:
        """Provide system architecture recommendations."""
        arch_request = f"""
Design system architecture for: {system_requirements}

Constraints: {constraints}

Include:
1. High-level architecture design
2. Component interaction diagrams
3. Technology stack recommendations
4. Scalability considerations
5. Security architecture
6. Performance optimization
7. Deployment strategies
8. Monitoring and observability
9. Cost optimization
10. Risk assessment and mitigation

Provide detailed architectural documentation.
"""
        return self.ask(arch_request, show_code=True, execute=True)
    
    def security_audit(self, system_description: str) -> Any:
        """Perform comprehensive security audit."""
        security_request = f"""
Perform security audit for: {system_description}

Include:
1. Vulnerability assessment
2. Threat modeling
3. Security controls evaluation
4. Compliance checking
5. Risk analysis
6. Penetration testing approach
7. Security monitoring setup
8. Incident response planning
9. Security training recommendations
10. Remediation roadmap

Provide actionable security improvements.
"""
        return self.ask(security_request, show_code=True, execute=True)
    
    def performance_optimizer(self, system_description: str, 
                            bottleneck_areas: List[str] = None) -> Any:
        """Optimize system performance."""
        if bottleneck_areas is None:
            bottleneck_areas = ["cpu", "memory", "io", "network"]
            
        perf_request = f"""
Optimize performance for: {system_description}

Focus Areas: {', '.join(bottleneck_areas)}

Include:
1. Performance profiling setup
2. Bottleneck identification
3. Optimization strategies
4. Code improvements
5. Infrastructure optimizations
6. Caching implementations
7. Database optimizations
8. Network optimizations
9. Monitoring and alerting
10. Performance testing

Provide measurable improvements with benchmarks.
"""
        return self.ask(perf_request, show_code=True, execute=True)
    
    def data_scientist_assistant(self, research_question: str, 
                               data_sources: List[str] = None) -> Any:
        """Complete data science project assistant."""
        ds_request = f"""
Complete data science project for research question: {research_question}

Data Sources: {data_sources if data_sources else 'To be determined'}

Include:
1. Problem formulation and hypothesis
2. Data collection and exploration
3. Feature engineering and selection
4. Model development and evaluation
5. Statistical analysis and validation
6. Insights and recommendations
7. Visualization and reporting
8. Reproducible research setup
9. Model deployment considerations
10. Future research directions

Provide scientific rigor and business value.
"""
        return self.ask(ds_request, show_code=True, execute=True)
    
    def cloud_architect(self, application_type: str, cloud_provider: str = "aws") -> Any:
        """Design cloud architecture."""
        cloud_request = f"""
Design cloud architecture for {application_type} on {cloud_provider}:

Include:
1. Infrastructure as Code templates
2. Serverless vs container strategy
3. Auto-scaling configuration
4. Load balancing and traffic management
5. Data storage and backup strategies
6. Security and compliance setup
7. Cost optimization strategies
8. Monitoring and logging
9. Disaster recovery planning
10. Multi-region deployment

Provide implementation guides and best practices.
"""
        return self.ask(cloud_request, show_code=True, execute=True)
    
    def devops_engineer(self, project_type: str, team_size: str = "small") -> Any:
        """Complete DevOps pipeline setup."""
        devops_request = f"""
Setup complete DevOps pipeline for {project_type} (team size: {team_size}):

Include:
1. CI/CD pipeline configuration
2. Infrastructure automation
3. Environment management
4. Configuration management
5. Monitoring and alerting
6. Log aggregation and analysis
7. Security scanning integration
8. Performance testing automation
9. Deployment strategies
10. Team collaboration tools

Provide practical implementation with tools.
"""
        return self.ask(devops_request, show_code=True, execute=True)
    
    def product_manager_assistant(self, product_idea: str, 
                                market_context: str = "") -> Any:
        """Product management and analysis assistant."""
        pm_request = f"""
Product management analysis for: {product_idea}

Market Context: {market_context}

Include:
1. Market research and analysis
2. Competitive analysis
3. Feature prioritization framework
4. User story development
5. Technical feasibility assessment
6. Go-to-market strategy
7. Success metrics and KPIs
8. Risk assessment
9. Resource planning
10. Roadmap development

Provide strategic insights and actionable plans.
"""
        return self.ask(pm_request, show_code=True, execute=True)
    
    def business_analyst(self, business_problem: str, 
                        stakeholders: List[str] = None) -> Any:
        """Business analysis and requirements gathering."""
        ba_request = f"""
Business analysis for: {business_problem}

Stakeholders: {stakeholders if stakeholders else 'To be identified'}

Include:
1. Requirements gathering and analysis
2. Stakeholder mapping and communication
3. Process modeling and optimization
4. Gap analysis
5. Solution recommendations
6. Cost-benefit analysis
7. Risk assessment
8. Implementation planning
9. Change management strategy
10. Success measurement framework

Provide comprehensive business insights.
"""
        return self.ask(ba_request, show_code=True, execute=True)
    
    def research_assistant(self, research_topic: str, 
                         research_type: str = "comprehensive") -> Any:
        """Comprehensive research assistant."""
        research_request = f"""
Conduct {research_type} research on: {research_topic}

Include:
1. Literature review and analysis
2. Current trends and developments
3. Key findings and insights
4. Methodology recommendations
5. Data collection strategies
6. Analysis frameworks
7. Reporting and visualization
8. Future research directions
9. Practical applications
10. Citation and references

Provide scholarly and practical insights.
"""
        return self.ask(research_request, show_code=True, execute=True)
    
    def innovation_lab(self, challenge_description: str, 
                      innovation_type: str = "technological") -> Any:
        """Innovation and creative solution development."""
        innovation_request = f"""
Develop innovative solutions for: {challenge_description}

Innovation Type: {innovation_type}

Include:
1. Problem reframing and analysis
2. Creative ideation techniques
3. Technology trend analysis
4. Feasibility assessment
5. Prototype development
6. Market validation approaches
7. Implementation roadmap
8. Risk and opportunity analysis
9. Scaling strategies
10. Impact measurement

Provide creative and practical innovation paths.
"""
        return self.ask(innovation_request, show_code=True, execute=True)
    
    def startup_advisor(self, startup_idea: str, stage: str = "ideation") -> Any:
        """Comprehensive startup advisory."""
        startup_request = f"""
Startup advisory for: {startup_idea} (Stage: {stage})

Include:
1. Business model validation
2. Market opportunity analysis
3. Technical architecture planning
4. Team and resource planning
5. Funding strategy development
6. Go-to-market planning
7. Risk assessment and mitigation
8. Competitive positioning
9. Growth strategy development
10. Exit strategy considerations

Provide actionable startup guidance.
"""
        return self.ask(startup_request, show_code=True, execute=True)
    
    def ethical_ai_advisor(self, ai_application: str) -> Any:
        """Ethical AI development guidance."""
        ethics_request = f"""
Ethical AI analysis for: {ai_application}

Include:
1. Bias detection and mitigation
2. Fairness assessment frameworks
3. Transparency and explainability
4. Privacy protection measures
5. Accountability mechanisms
6. Stakeholder impact analysis
7. Regulatory compliance
8. Ethical decision frameworks
9. Continuous monitoring setup
10. Responsible AI practices

Provide ethical AI implementation guidelines.
"""
        return self.ask(ethics_request, show_code=True, execute=True)
    
    def sustainability_consultant(self, project_description: str) -> Any:
        """Sustainability and environmental impact analysis."""
        sustainability_request = f"""
Sustainability analysis for: {project_description}

Include:
1. Environmental impact assessment
2. Carbon footprint calculation
3. Resource optimization strategies
4. Sustainable technology recommendations
5. Lifecycle analysis
6. Green computing practices
7. Waste reduction strategies
8. Energy efficiency improvements
9. Sustainability metrics and KPIs
10. Reporting and compliance

Provide sustainable development recommendations.
"""
        return self.ask(sustainability_request, show_code=True, execute=True)
    
    # =============================================
    # INTEGRATION AND WORKFLOW METHODS
    # =============================================
    
    def create_workflow(self, workflow_description: str, 
                       steps: List[str] = None) -> Any:
        """Create automated workflows."""
        workflow_request = f"""
Create automated workflow for: {workflow_description}

Steps: {steps if steps else 'Auto-generate based on description'}

Include:
1. Workflow design and orchestration
2. Step-by-step automation
3. Error handling and recovery
4. Progress tracking and logging
5. Notification and alerting
6. Resource management
7. Parallel processing where applicable
8. Validation and testing
9. Monitoring and optimization
10. Documentation and maintenance

Provide complete workflow implementation.
"""
        return self.ask(workflow_request, show_code=True, execute=True)
    
    def integrate_systems(self, system1: str, system2: str, 
                         integration_type: str = "api") -> Any:
        """Create system integrations."""
        integration_request = f"""
Create integration between {system1} and {system2}:

Integration Type: {integration_type}

Include:
1. Integration architecture design
2. Data mapping and transformation
3. Authentication and security
4. Error handling and retry logic
5. Performance optimization
6. Monitoring and logging
7. Testing and validation
8. Documentation
9. Maintenance procedures
10. Scaling considerations

Provide robust integration solution.
"""
        return self.ask(integration_request, show_code=True, execute=True)
    
    def multi_model_ensemble(self, problem_description: str, 
                           model_types: List[str] = None) -> Any:
        """Create ensemble of multiple models."""
        if model_types is None:
            model_types = ["tree-based", "linear", "neural", "ensemble"]
            
        ensemble_request = f"""
Create multi-model ensemble for: {problem_description}

Model Types: {', '.join(model_types)}

Include:
1. Individual model development
2. Model selection and validation
3. Ensemble strategies (voting, stacking, blending)
4. Feature engineering for each model
5. Hyperparameter optimization
6. Cross-validation framework
7. Performance comparison
8. Model interpretation
9. Production deployment
10. Monitoring and retraining

Provide comprehensive ensemble solution.
"""
        return self.ask(ensemble_request, show_code=True, execute=True)
    
    def real_time_system(self, system_description: str, 
                        latency_requirement: str = "low") -> Any:
        """Create real-time processing system."""
        realtime_request = f"""
Create real-time system for: {system_description}

Latency Requirement: {latency_requirement}

Include:
1. Real-time architecture design
2. Stream processing implementation
3. Low-latency optimizations
4. Event-driven processing
5. Scalability and fault tolerance
6. Monitoring and alerting
7. Performance benchmarking
8. Resource management
9. Data consistency handling
10. Deployment and operations

Provide high-performance real-time solution.
"""
        return self.ask(realtime_request, show_code=True, execute=True)
    
    def experiment_platform(self, experiment_type: str, 
                          variables: List[str] = None) -> Any:
        """Create experimentation platform."""
        experiment_request = f"""
Create experimentation platform for: {experiment_type}

Variables: {variables if variables else 'To be determined'}

Include:
1. Experiment design framework
2. A/B testing infrastructure
3. Statistical analysis tools
4. Data collection and tracking
5. Result visualization
6. Hypothesis testing
7. Sample size calculations
8. Bias detection and mitigation
9. Reporting and insights
10. Continuous experimentation

Provide scientific experimentation capabilities.
"""
        return self.ask(experiment_request, show_code=True, execute=True)

    # ====================
    # 50+ ADVANCED FEATURES
    # ====================
    
    # === DATA SCIENCE & ANALYTICS (10 Features) ===
    
    def advanced_statistical_analysis(self, data_query: str) -> Any:
        """Perform advanced statistical analysis with multiple tests."""
        self._log_operation("advanced_statistical_analysis")
        prompt = f"""
        Perform comprehensive statistical analysis: {data_query}
        
        Include:
        - Descriptive statistics
        - Distribution tests (Shapiro-Wilk, Kolmogorov-Smirnov)
        - Correlation analysis with significance tests
        - Outlier detection (IQR, Z-score, Isolation Forest)
        - Time series decomposition if applicable
        - Statistical significance tests
        - Effect size calculations
        - Confidence intervals
        - Bootstrap sampling
        - Hypothesis testing recommendations
        
        Use scipy.stats, statsmodels, and scikit-learn.
        """
        return self._generate_and_execute(prompt)
    
    def automated_feature_engineering(self, dataset_query: str) -> Any:
        """Automatically generate and select features from data."""
        self._log_operation("automated_feature_engineering")
        prompt = f"""
        Perform automated feature engineering: {dataset_query}
        
        Generate features using:
        - Polynomial features
        - Interaction terms
        - Binning/discretization
        - Log/sqrt transformations
        - Date/time features (if applicable)
        - Text features (TF-IDF, n-grams if text data)
        - Principal components
        - Feature selection (SelectKBest, RFE, LASSO)
        - Feature importance ranking
        - Feature clustering
        
        Use scikit-learn, feature-engine, and pandas.
        """
        return self._generate_and_execute(prompt)
    
    def time_series_forecasting(self, data_query: str) -> Any:
        """Advanced time series analysis and forecasting."""
        self._log_operation("time_series_forecasting")
        prompt = f"""
        Perform comprehensive time series analysis: {data_query}
        
        Include:
        - Trend and seasonality decomposition
        - Stationarity tests (ADF, KPSS)
        - ACF/PACF analysis
        - ARIMA model fitting
        - Seasonal ARIMA (SARIMA)
        - Prophet forecasting
        - Exponential smoothing
        - LSTM neural networks
        - Forecast accuracy metrics
        - Residual analysis
        - Confidence intervals
        
        Use statsmodels, prophet, tensorflow/keras.
        """
        return self._generate_and_execute(prompt)
    
    def clustering_analysis(self, data_query: str) -> Any:
        """Advanced clustering with multiple algorithms."""
        self._log_operation("clustering_analysis")
        prompt = f"""
        Perform comprehensive clustering analysis: {data_query}
        
        Apply multiple algorithms:
        - K-means with elbow method
        - Hierarchical clustering
        - DBSCAN
        - Gaussian Mixture Models
        - Spectral clustering
        - OPTICS
        - Mean Shift
        - Cluster validation metrics (silhouette, calinski-harabasz)
        - Dimensionality reduction for visualization
        - Cluster profiling and interpretation
        
        Use scikit-learn and create visualizations.
        """
        return self._generate_and_execute(prompt)
    
    def anomaly_detection(self, data_query: str) -> Any:
        """Multiple anomaly detection algorithms."""
        self._log_operation("anomaly_detection")
        prompt = f"""
        Perform comprehensive anomaly detection: {data_query}
        
        Apply multiple methods:
        - Isolation Forest
        - One-Class SVM
        - Local Outlier Factor
        - Elliptic Envelope
        - Statistical methods (Z-score, IQR)
        - Autoencoders for anomaly detection
        - Time series anomaly detection
        - Multivariate anomaly detection
        - Anomaly scoring and ranking
        - Visualization of anomalies
        
        Use scikit-learn, tensorflow, and pyod.
        """
        return self._generate_and_execute(prompt)
    
    def survival_analysis(self, data_query: str) -> Any:
        """Survival analysis and reliability modeling."""
        self._log_operation("survival_analysis")
        prompt = f"""
        Perform survival analysis: {data_query}
        
        Include:
        - Kaplan-Meier survival curves
        - Cox proportional hazards model
        - Log-rank tests
        - Hazard ratios
        - Time-dependent covariates
        - Competing risks analysis
        - Parametric survival models
        - Survival prediction
        - Risk stratification
        - Visualization of survival curves
        
        Use lifelines and scikit-survival.
        """
        return self._generate_and_execute(prompt)
    
    def causal_inference(self, data_query: str) -> Any:
        """Causal inference and treatment effect analysis."""
        self._log_operation("causal_inference")
        prompt = f"""
        Perform causal inference analysis: {data_query}
        
        Methods:
        - Propensity score matching
        - Instrumental variables
        - Difference-in-differences
        - Regression discontinuity
        - Causal graphs and DAGs
        - Treatment effect estimation
        - Sensitivity analysis
        - Confounding adjustment
        - Mediation analysis
        - Causal discovery algorithms
        
        Use econml, dowhy, and causal-learn.
        """
        return self._generate_and_execute(prompt)
    
    def bayesian_analysis(self, data_query: str) -> Any:
        """Bayesian statistical analysis and modeling."""
        self._log_operation("bayesian_analysis")
        prompt = f"""
        Perform Bayesian analysis: {data_query}
        
        Include:
        - Bayesian regression models
        - MCMC sampling
        - Prior specification
        - Posterior distributions
        - Credible intervals
        - Model comparison (WAIC, LOO)
        - Hierarchical models
        - Bayesian A/B testing
        - Uncertainty quantification
        - Model diagnostics
        
        Use pymc, stan (pystan), and arviz.
        """
        return self._generate_and_execute(prompt)
    
    def network_analysis(self, data_query: str) -> Any:
        """Social network and graph analysis."""
        self._log_operation("network_analysis")
        prompt = f"""
        Perform network analysis: {data_query}
        
        Compute:
        - Centrality measures (degree, betweenness, closeness, eigenvector)
        - Community detection algorithms
        - Network clustering
        - Path analysis
        - Network density and connectivity
        - Small-world properties
        - Scale-free network tests
        - Network visualization
        - Temporal network analysis
        - Link prediction
        
        Use networkx, igraph, and graph-tool.
        """
        return self._generate_and_execute(prompt)
    
    def text_analytics_advanced(self, text_query: str) -> Any:
        """Advanced text analytics and NLP."""
        self._log_operation("text_analytics_advanced")
        prompt = f"""
        Perform advanced text analytics: {text_query}
        
        Include:
        - Topic modeling (LDA, NMF, BERTopic)
        - Sentiment analysis with transformers
        - Named entity recognition
        - Text classification
        - Text summarization
        - Language detection
        - Text similarity and clustering
        - Keyword extraction
        - Text generation
        - Document embeddings
        
        Use spacy, transformers, gensim, and nltk.
        """
        return self._generate_and_execute(prompt)
    
    # === MACHINE LEARNING & AI (10 Features) ===
    
    def automl_pipeline(self, ml_query: str) -> Any:
        """Automated machine learning pipeline."""
        self._log_operation("automl_pipeline")
        prompt = f"""
        Create automated ML pipeline: {ml_query}
        
        Include:
        - Automated data preprocessing
        - Feature selection and engineering
        - Algorithm selection and tuning
        - Hyperparameter optimization
        - Cross-validation strategies
        - Model ensemble methods
        - Performance evaluation
        - Model interpretation
        - Automated reporting
        - Pipeline deployment preparation
        
        Use auto-sklearn, tpot, or h2o.
        """
        return self._generate_and_execute(prompt)
    
    def deep_learning_models(self, dl_query: str) -> Any:
        """Advanced deep learning model creation."""
        self._log_operation("deep_learning_models")
        prompt = f"""
        Create deep learning models: {dl_query}
        
        Implement:
        - CNN for image/spatial data
        - RNN/LSTM for sequential data
        - Transformer models
        - Autoencoders
        - GANs (Generative Adversarial Networks)
        - Transfer learning
        - Model optimization techniques
        - Regularization methods
        - Learning rate scheduling
        - Model visualization
        
        Use tensorflow/keras or pytorch.
        """
        return self._generate_and_execute(prompt)
    
    def reinforcement_learning(self, rl_query: str) -> Any:
        """Reinforcement learning algorithms."""
        self._log_operation("reinforcement_learning")
        prompt = f"""
        Implement reinforcement learning: {rl_query}
        
        Algorithms:
        - Q-learning
        - Deep Q-Networks (DQN)
        - Policy gradient methods
        - Actor-Critic methods
        - Multi-armed bandits
        - Environment simulation
        - Reward function design
        - Training and evaluation
        - Hyperparameter tuning
        - Performance visualization
        
        Use stable-baselines3, gym, or ray[rllib].
        """
        return self._generate_and_execute(prompt)
    
    def model_explainability(self, model_query: str) -> Any:
        """Model interpretation and explainability."""
        self._log_operation("model_explainability")
        prompt = f"""
        Perform model explainability analysis: {model_query}
        
        Methods:
        - SHAP values
        - LIME explanations
        - Permutation importance
        - Partial dependence plots
        - Feature interaction effects
        - Model-agnostic methods
        - Local vs global explanations
        - Counterfactual explanations
        - Anchors explanations
        - Visualization of explanations
        
        Use shap, lime, eli5, and interpret.
        """
        return self._generate_and_execute(prompt)
    
    def computer_vision(self, cv_query: str) -> Any:
        """Computer vision and image processing."""
        self._log_operation("computer_vision")
        prompt = f"""
        Perform computer vision tasks: {cv_query}
        
        Capabilities:
        - Image classification
        - Object detection
        - Image segmentation
        - Face recognition
        - Optical character recognition (OCR)
        - Image preprocessing
        - Feature extraction
        - Image augmentation
        - Style transfer
        - Image generation
        
        Use opencv, PIL, tensorflow, pytorch, and transformers.
        """
        return self._generate_and_execute(prompt)
    
    def recommender_systems(self, rec_query: str) -> Any:
        """Recommendation system algorithms."""
        self._log_operation("recommender_systems")
        prompt = f"""
        Build recommendation system: {rec_query}
        
        Approaches:
        - Collaborative filtering
        - Content-based filtering
        - Matrix factorization
        - Deep learning recommendations
        - Hybrid approaches
        - Cold start handling
        - Evaluation metrics
        - Real-time recommendations
        - Diversity and novelty
        - Bias detection and mitigation
        
        Use surprise, implicit, and lightfm.
        """
        return self._generate_and_execute(prompt)
    
    def optimization_algorithms(self, opt_query: str) -> Any:
        """Advanced optimization algorithms."""
        self._log_operation("optimization_algorithms")
        prompt = f"""
        Solve optimization problem: {opt_query}
        
        Methods:
        - Linear programming
        - Integer programming
        - Genetic algorithms
        - Particle swarm optimization
        - Simulated annealing
        - Gradient-based optimization
        - Constrained optimization
        - Multi-objective optimization
        - Bayesian optimization
        - Metaheuristic algorithms
        
        Use scipy.optimize, cvxpy, deap, and optuna.
        """
        return self._generate_and_execute(prompt)
    
    def federated_learning(self, fl_query: str) -> Any:
        """Federated learning implementation."""
        self._log_operation("federated_learning")
        prompt = f"""
        Implement federated learning: {fl_query}
        
        Components:
        - Client-server architecture
        - Model aggregation strategies
        - Differential privacy
        - Secure aggregation
        - Non-IID data handling
        - Communication efficiency
        - Personalization techniques
        - Evaluation metrics
        - Simulation framework
        - Privacy analysis
        
        Use flower, tensorflow-federated, or pysyft.
        """
        return self._generate_and_execute(prompt)
    
    def graph_neural_networks(self, gnn_query: str) -> Any:
        """Graph neural network models."""
        self._log_operation("graph_neural_networks")
        prompt = f"""
        Create graph neural networks: {gnn_query}
        
        Architectures:
        - Graph Convolutional Networks (GCN)
        - GraphSAGE
        - Graph Attention Networks
        - Graph Transformer
        - Node classification
        - Link prediction
        - Graph classification
        - Graph generation
        - Temporal graphs
        - Heterogeneous graphs
        
        Use pytorch-geometric, dgl, or spektral.
        """
        return self._generate_and_execute(prompt)
    
    def quantum_ml(self, qml_query: str) -> Any:
        """Quantum machine learning algorithms."""
        self._log_operation("quantum_ml")
        prompt = f"""
        Implement quantum ML: {qml_query}
        
        Algorithms:
        - Quantum neural networks
        - Variational quantum eigensolver
        - Quantum approximate optimization
        - Quantum support vector machines
        - Quantum clustering
        - Quantum feature maps
        - Hybrid classical-quantum models
        - Quantum advantage analysis
        - Noise mitigation
        - Circuit optimization
        
        Use qiskit, pennylane, or cirq.
        """
        return self._generate_and_execute(prompt)
    
    # === WEB DEVELOPMENT & APIs (8 Features) ===
    
    def web_scraping_advanced(self, scraping_query: str) -> Any:
        """Advanced web scraping with anti-detection."""
        self._log_operation("web_scraping_advanced")
        prompt = f"""
        Perform advanced web scraping: {scraping_query}
        
        Features:
        - Selenium automation
        - Beautiful Soup parsing
        - Playwright browser control
        - Anti-detection measures
        - Proxy rotation
        - Session management
        - Rate limiting
        - Dynamic content handling
        - Form submission
        - Data extraction pipelines
        
        Use selenium, beautifulsoup4, playwright, and scrapy.
        """
        return self._generate_and_execute(prompt)
    
    def api_development(self, api_query: str) -> Any:
        """REST API development and testing."""
        self._log_operation("api_development")
        prompt = f"""
        Develop REST API: {api_query}
        
        Include:
        - FastAPI or Flask application
        - Authentication and authorization
        - Input validation
        - Error handling
        - Database integration
        - API documentation
        - Rate limiting
        - Caching strategies
        - Testing endpoints
        - Deployment configuration
        
        Use fastapi, flask, sqlalchemy, and pydantic.
        """
        return self._generate_and_execute(prompt)
    
    def webhook_systems(self, webhook_query: str) -> Any:
        """Webhook creation and management."""
        self._log_operation("webhook_systems")
        prompt = f"""
        Create webhook system: {webhook_query}
        
        Components:
        - Webhook receivers
        - Event processing
        - Signature verification
        - Retry mechanisms
        - Queue management
        - Event routing
        - Payload validation
        - Logging and monitoring
        - Error handling
        - Testing framework
        
        Use flask/fastapi, celery, and redis.
        """
        return self._generate_and_execute(prompt)
    
    def microservices_architecture(self, microservice_query: str) -> Any:
        """Microservices design and implementation."""
        self._log_operation("microservices_architecture")
        prompt = f"""
        Design microservices architecture: {microservice_query}
        
        Components:
        - Service decomposition
        - API gateway
        - Service discovery
        - Load balancing
        - Circuit breakers
        - Health checks
        - Configuration management
        - Distributed tracing
        - Event-driven communication
        - Container orchestration
        
        Use fastapi, docker, kubernetes concepts.
        """
        return self._generate_and_execute(prompt)
    
    def graphql_apis(self, graphql_query: str) -> Any:
        """GraphQL API development."""
        self._log_operation("graphql_apis")
        prompt = f"""
        Create GraphQL API: {graphql_query}
        
        Features:
        - Schema definition
        - Resolvers implementation
        - Query optimization
        - Mutations and subscriptions
        - Authentication integration
        - Caching strategies
        - Error handling
        - Real-time updates
        - Testing queries
        - Documentation generation
        
        Use graphene, strawberry, or ariadne.
        """
        return self._generate_and_execute(prompt)
    
    def websocket_systems(self, websocket_query: str) -> Any:
        """Real-time WebSocket applications."""
        self._log_operation("websocket_systems")
        prompt = f"""
        Create WebSocket application: {websocket_query}
        
        Features:
        - WebSocket server setup
        - Client connection management
        - Real-time messaging
        - Room/channel management
        - Authentication
        - Message broadcasting
        - Connection state handling
        - Error recovery
        - Scaling considerations
        - Performance optimization
        
        Use websockets, socketio, or fastapi websockets.
        """
        return self._generate_and_execute(prompt)
    
    def oauth_authentication(self, oauth_query: str) -> Any:
        """OAuth and authentication systems."""
        self._log_operation("oauth_authentication")
        prompt = f"""
        Implement OAuth authentication: {oauth_query}
        
        Components:
        - OAuth 2.0 flow implementation
        - JWT token handling
        - Social login integration
        - Session management
        - Role-based access control
        - Token refresh mechanisms
        - Security best practices
        - Multi-factor authentication
        - Password policies
        - Audit logging
        
        Use authlib, python-jose, and passlib.
        """
        return self._generate_and_execute(prompt)
    
    def api_testing_automation(self, test_query: str) -> Any:
        """Automated API testing frameworks."""
        self._log_operation("api_testing_automation")
        prompt = f"""
        Create API testing framework: {test_query}
        
        Features:
        - Test case generation
        - Response validation
        - Performance testing
        - Contract testing
        - Mock services
        - Test data management
        - Continuous testing
        - Report generation
        - Error analysis
        - CI/CD integration
        
        Use pytest, requests, locust, and tavern.
        """
        return self._generate_and_execute(prompt)
    
    # === DATABASE & STORAGE (6 Features) ===
    
    def database_optimization(self, db_query: str) -> Any:
        """Database query optimization and tuning."""
        self._log_operation("database_optimization")
        prompt = f"""
        Optimize database performance: {db_query}
        
        Techniques:
        - Query analysis and optimization
        - Index creation and management
        - Database schema design
        - Performance monitoring
        - Connection pooling
        - Caching strategies
        - Partitioning strategies
        - Backup and recovery
        - Migration scripts
        - Performance benchmarking
        
        Use sqlalchemy, psycopg2, and database-specific tools.
        """
        return self._generate_and_execute(prompt)
    
    def data_warehousing(self, warehouse_query: str) -> Any:
        """Data warehouse design and ETL processes."""
        self._log_operation("data_warehousing")
        prompt = f"""
        Design data warehouse solution: {warehouse_query}
        
        Components:
        - Dimensional modeling
        - ETL pipeline design
        - Data quality checks
        - Incremental loading
        - Change data capture
        - Data lineage tracking
        - Performance optimization
        - Monitoring and alerting
        - Documentation generation
        - Testing frameworks
        
        Use apache-airflow, pandas, and sqlalchemy.
        """
        return self._generate_and_execute(prompt)
    
    def nosql_databases(self, nosql_query: str) -> Any:
        """NoSQL database operations and design."""
        self._log_operation("nosql_databases")
        prompt = f"""
        Work with NoSQL databases: {nosql_query}
        
        Operations:
        - Document database operations (MongoDB)
        - Key-value store operations (Redis)
        - Graph database operations (Neo4j)
        - Column-family operations (Cassandra)
        - Schema design patterns
        - Query optimization
        - Indexing strategies
        - Replication and sharding
        - Backup and recovery
        - Performance tuning
        
        Use pymongo, redis, neo4j, and cassandra-driver.
        """
        return self._generate_and_execute(prompt)
    
    def big_data_processing(self, bigdata_query: str) -> Any:
        """Big data processing with distributed systems."""
        self._log_operation("big_data_processing")
        prompt = f"""
        Process big data: {bigdata_query}
        
        Tools and techniques:
        - Apache Spark operations
        - Distributed computing
        - Data partitioning strategies
        - Memory optimization
        - Lazy evaluation
        - Streaming data processing
        - Batch processing pipelines
        - Data format optimization
        - Cluster management
        - Performance monitoring
        
        Use pyspark, dask, and ray.
        """
        return self._generate_and_execute(prompt)
    
    def data_lake_management(self, datalake_query: str) -> Any:
        """Data lake architecture and management."""
        self._log_operation("data_lake_management")
        prompt = f"""
        Manage data lake: {datalake_query}
        
        Features:
        - Data ingestion pipelines
        - Metadata management
        - Data cataloging
        - Schema evolution
        - Data governance
        - Access control
        - Data quality monitoring
        - Lifecycle management
        - Cost optimization
        - Integration patterns
        
        Use delta-lake, apache-iceberg concepts with pandas/pyarrow.
        """
        return self._generate_and_execute(prompt)
    
    def blockchain_storage(self, blockchain_query: str) -> Any:
        """Blockchain and distributed ledger operations."""
        self._log_operation("blockchain_storage")
        prompt = f"""
        Implement blockchain operations: {blockchain_query}
        
        Components:
        - Smart contract interaction
        - Transaction processing
        - Wallet management
        - Cryptocurrency operations
        - NFT operations
        - DeFi protocol integration
        - Blockchain data analysis
        - Security best practices
        - Gas optimization
        - Event monitoring
        
        Use web3, eth-account, and requests for API calls.
        """
        return self._generate_and_execute(prompt)
    
    # === IMAGE & MEDIA PROCESSING (6 Features) ===
    
    def image_processing_advanced(self, image_query: str) -> Any:
        """Advanced image processing and manipulation."""
        self._log_operation("image_processing_advanced")
        prompt = f"""
        Perform advanced image processing: {image_query}
        
        Operations:
        - Image enhancement and filtering
        - Morphological operations
        - Edge detection algorithms
        - Image segmentation
        - Feature extraction
        - Image registration
        - Panorama stitching
        - HDR processing
        - Noise reduction
        - Color space conversions
        
        Use opencv, PIL, scikit-image, and numpy.
        """
        return self._generate_and_execute(prompt)
    
    def video_processing(self, video_query: str) -> Any:
        """Video processing and analysis."""
        self._log_operation("video_processing")
        prompt = f"""
        Process video content: {video_query}
        
        Capabilities:
        - Video frame extraction
        - Video editing and manipulation
        - Motion detection
        - Object tracking
        - Video stabilization
        - Format conversion
        - Compression optimization
        - Subtitle processing
        - Video analytics
        - Live stream processing
        
        Use opencv, moviepy, and ffmpeg-python.
        """
        return self._generate_and_execute(prompt)
    
    def audio_processing(self, audio_query: str) -> Any:
        """Audio processing and analysis."""
        self._log_operation("audio_processing")
        prompt = f"""
        Process audio content: {audio_query}
        
        Features:
        - Audio file manipulation
        - Spectral analysis
        - Noise reduction
        - Audio effects
        - Speech recognition
        - Music information retrieval
        - Audio classification
        - Beat detection
        - Pitch analysis
        - Audio synthesis
        
        Use librosa, pydub, speechrecognition, and numpy.
        """
        return self._generate_and_execute(prompt)
    
    def pdf_processing(self, pdf_query: str) -> Any:
        """PDF processing and document analysis."""
        self._log_operation("pdf_processing")
        prompt = f"""
        Process PDF documents: {pdf_query}
        
        Operations:
        - Text extraction
        - Image extraction
        - PDF manipulation
        - Document parsing
        - Table extraction
        - Form processing
        - Metadata handling
        - PDF generation
        - Annotation processing
        - OCR integration
        
        Use PyPDF2, pdfplumber, reportlab, and pytesseract.
        """
        return self._generate_and_execute(prompt)
    
    def geospatial_analysis(self, geo_query: str) -> Any:
        """Geospatial data analysis and mapping."""
        self._log_operation("geospatial_analysis")
        prompt = f"""
        Perform geospatial analysis: {geo_query}
        
        Capabilities:
        - Geographic data processing
        - Spatial joins and queries
        - Distance calculations
        - Route optimization
        - Geocoding and reverse geocoding
        - Spatial clustering
        - Heat map generation
        - Coordinate transformations
        - Satellite imagery analysis
        - Interactive mapping
        
        Use geopandas, folium, shapely, and geopy.
        """
        return self._generate_and_execute(prompt)
    
    def media_metadata(self, metadata_query: str) -> Any:
        """Media file metadata extraction and manipulation."""
        self._log_operation("media_metadata")
        prompt = f"""
        Process media metadata: {metadata_query}
        
        Operations:
        - EXIF data extraction
        - Media file organization
        - Duplicate detection
        - Batch metadata editing
        - Thumbnail generation
        - File format conversion
        - Quality assessment
        - Content-based indexing
        - Automated tagging
        - Archive management
        
        Use exifread, pillow, and python-magic.
        """
        return self._generate_and_execute(prompt)
    
    # === SECURITY & ENCRYPTION (5 Features) ===
    
    def cryptography_operations(self, crypto_query: str) -> Any:
        """Cryptographic operations and security."""
        self._log_operation("cryptography_operations")
        prompt = f"""
        Perform cryptographic operations: {crypto_query}
        
        Operations:
        - Symmetric encryption/decryption
        - Asymmetric encryption/decryption
        - Digital signatures
        - Hash functions
        - Key generation and management
        - Certificate handling
        - Secure random generation
        - Password hashing
        - Message authentication
        - Cryptographic protocols
        
        Use cryptography, pycryptodome, and hashlib.
        """
        return self._generate_and_execute(prompt)
    
    def security_scanning(self, security_query: str) -> Any:
        """Security vulnerability scanning and analysis."""
        self._log_operation("security_scanning")
        prompt = f"""
        Perform security analysis: {security_query}
        
        Checks:
        - Dependency vulnerability scanning
        - Code security analysis
        - Network security testing
        - SQL injection detection
        - XSS vulnerability detection
        - Authentication bypass testing
        - Input validation testing
        - Configuration security
        - API security testing
        - Penetration testing basics
        
        Use bandit, safety, and requests for security testing.
        """
        return self._generate_and_execute(prompt)
    
    def privacy_protection(self, privacy_query: str) -> Any:
        """Data privacy and anonymization techniques."""
        self._log_operation("privacy_protection")
        prompt = f"""
        Implement privacy protection: {privacy_query}
        
        Techniques:
        - Data anonymization
        - Differential privacy
        - K-anonymity
        - L-diversity
        - T-closeness
        - Data masking
        - PII detection and removal
        - Synthetic data generation
        - Privacy impact assessment
        - GDPR compliance tools
        
        Use faker, presidio, and custom anonymization.
        """
        return self._generate_and_execute(prompt)
    
    def secure_communication(self, comm_query: str) -> Any:
        """Secure communication protocols and implementation."""
        self._log_operation("secure_communication")
        prompt = f"""
        Implement secure communication: {comm_query}
        
        Features:
        - TLS/SSL implementation
        - End-to-end encryption
        - Secure messaging protocols
        - Key exchange mechanisms
        - Certificate management
        - Secure file transfer
        - VPN tunnel creation
        - Secure email protocols
        - Zero-knowledge protocols
        - Quantum-safe cryptography
        
        Use cryptography, paramiko, and requests with SSL.
        """
        return self._generate_and_execute(prompt)
    
    def forensics_analysis(self, forensics_query: str) -> Any:
        """Digital forensics and incident response."""
        self._log_operation("forensics_analysis")
        prompt = f"""
        Perform digital forensics: {forensics_query}
        
        Analysis:
        - File system analysis
        - Network traffic analysis
        - Log file analysis
        - Memory dump analysis
        - Deleted file recovery
        - Timeline reconstruction
        - Hash verification
        - Steganography detection
        - Malware analysis basics
        - Evidence preservation
        
        Use hashlib, python-magic, and file analysis tools.
        """
        return self._generate_and_execute(prompt)
    
    # === SYSTEM & PERFORMANCE (5 Features) ===
    
    def system_monitoring(self, monitor_query: str) -> Any:
        """System performance monitoring and analysis."""
        self._log_operation("system_monitoring")
        prompt = f"""
        Implement system monitoring: {monitor_query}
        
        Metrics:
        - CPU and memory usage
        - Disk I/O monitoring
        - Network traffic analysis
        - Process monitoring
        - Service health checks
        - Log analysis
        - Alert generation
        - Performance baselines
        - Anomaly detection
        - Dashboard creation
        
        Use psutil, matplotlib, and logging.
        """
        return self._generate_and_execute(prompt)
    
    def parallel_processing(self, parallel_query: str) -> Any:
        """Parallel and concurrent processing optimization."""
        self._log_operation("parallel_processing")
        prompt = f"""
        Implement parallel processing: {parallel_query}
        
        Techniques:
        - Multiprocessing implementation
        - Threading optimization
        - Asyncio programming
        - Distributed computing
        - GPU acceleration
        - Task queue management
        - Load balancing
        - Resource management
        - Performance profiling
        - Bottleneck identification
        
        Use multiprocessing, asyncio, concurrent.futures, and ray.
        """
        return self._generate_and_execute(prompt)
    
    def cloud_integration(self, cloud_query: str) -> Any:
        """Cloud services integration and deployment."""
        self._log_operation("cloud_integration")
        prompt = f"""
        Integrate with cloud services: {cloud_query}
        
        Services:
        - AWS services integration
        - Azure services integration
        - Google Cloud Platform
        - Storage services (S3, Blob, Cloud Storage)
        - Serverless functions
        - Container orchestration
        - CI/CD pipeline integration
        - Infrastructure as code
        - Monitoring and logging
        - Cost optimization
        
        Use boto3, azure-sdk, google-cloud, and requests.
        """
        return self._generate_and_execute(prompt)
    
    def containerization(self, container_query: str) -> Any:
        """Docker containerization and orchestration."""
        self._log_operation("containerization")
        prompt = f"""
        Implement containerization: {container_query}
        
        Components:
        - Dockerfile creation
        - Multi-stage builds
        - Container optimization
        - Docker Compose setup
        - Kubernetes manifests
        - Health checks
        - Volume management
        - Network configuration
        - Security scanning
        - Registry management
        
        Generate Docker and Kubernetes configurations.
        """
        return self._generate_and_execute(prompt)
    
    def performance_profiling(self, profile_query: str) -> Any:
        """Advanced performance profiling and optimization."""
        self._log_operation("performance_profiling")
        prompt = f"""
        Perform performance profiling: {profile_query}
        
        Analysis:
        - Code profiling and optimization
        - Memory usage analysis
        - CPU bottleneck identification
        - I/O performance analysis
        - Database query optimization
        - Caching strategies
        - Algorithm complexity analysis
        - Resource utilization
        - Performance benchmarking
        - Optimization recommendations
        
        Use cProfile, memory_profiler, and line_profiler.
        """
        return self._generate_and_execute(prompt)


class SimplePythonChat:
    """
    Simple Python learning assistant focused on teaching and explaining Python concepts.
    
    This is a lightweight LLM-based chat system specifically designed to help users
    learn Python programming through explanations, examples, and guidance.
    
    Features:
    - Python concept explanations
    - Code examples and tutorials
    - Debugging help
    - Best practices guidance
    - Learning path recommendations
    - Interactive Python Q&A
    
    Usage:
        from orionai.python import SimplePythonChat
        
        chat = SimplePythonChat()
        response = chat.ask("How do list comprehensions work in Python?")
        chat.explain_code("def fibonacci(n): return [0,1] + [fibonacci(n-1) + fibonacci(n-2) for i in range(2,n)]")
    """
    
    def __init__(self, 
                 provider: str = "google",
                 model: str = "gemini-1.5-pro",
                 api_key: Optional[str] = None,
                 verbose: bool = True):
        """
        Initialize Simple Python Chat.
        
        Args:
            provider: LLM provider ("google", "openai", "anthropic")
            model: Model name
            api_key: API key (optional, can use environment variable)
            verbose: Show detailed responses
        """
        self.provider_name = provider.lower()
        self.model_name = model
        self.verbose = verbose
        
        # Initialize using AIPython engine for consistency
        self.ai_engine = AIPython(
            provider=provider,
            model=model,
            api_key=api_key,
            verbose=False,  # Keep SimplePythonChat output clean
            ask_permission=False
        )
        
        # Conversation history for context
        self.conversation_history = []
        
        if self.verbose:
            print(f"🐍 SimplePythonChat initialized with {provider}:{model}")
            print("Ready to help you learn Python! Ask me anything about Python programming.")
    

    
    def ask(self, question: str) -> str:
        """
        Ask a Python-related question.
        
        Args:
            question: Your Python question or concept you want to learn about
            
        Returns:
            Detailed explanation and examples
        """
        if self.verbose:
            print(f"🤔 Question: {question}")
        
        # Build context from conversation history
        context = ""
        if self.conversation_history:
            recent_context = self.conversation_history[-3:]  # Last 3 exchanges
            context = "\n".join([f"Q: {q}\nA: {a[:200]}..." for q, a in recent_context])
        
        prompt = f"""
You are a Python programming tutor and expert. Your goal is to help users learn Python through clear explanations, practical examples, and guidance.

CONVERSATION CONTEXT:
{context}

USER QUESTION: "{question}"

INSTRUCTIONS:
1. Provide clear, educational explanations
2. Include practical Python code examples
3. Explain concepts step-by-step
4. Highlight best practices and common pitfalls
5. Suggest related topics to explore
6. Use beginner-friendly language when appropriate
7. Include multiple examples for complex concepts
8. Focus ONLY on Python programming topics
9. Encourage learning and exploration

RESPONSE FORMAT:
- Start with a clear explanation
- Provide code examples with comments
- Include output examples when relevant
- End with tips or related concepts to explore

Remember: You are a Python tutor, not a code executor. Focus on teaching and explaining Python concepts clearly.
"""

        try:
            response = self.ai_engine._generate_code(prompt)
            
            # Store in conversation history
            self.conversation_history.append((question, response))
            
            if self.verbose:
                print(f"🐍 Python Tutor Response:")
                print("-" * 50)
                print(response)
                print("-" * 50)
            
            return response
            
        except Exception as e:
            error_msg = f"Error getting response: {e}"
            if self.verbose:
                print(f"❌ {error_msg}")
            return error_msg
    
    def explain_code(self, code: str) -> str:
        """
        Explain what a piece of Python code does.
        
        Args:
            code: Python code to explain
            
        Returns:
            Detailed explanation of the code
        """
        if self.verbose:
            print(f"🔍 Explaining code:")
            print("```python")
            print(code)
            print("```")
        
        question = f"Please explain this Python code step by step:\n\n```python\n{code}\n```\n\nBreak down what each part does and how it works."
        
        return self.ask(question)
    
    def get_examples(self, topic: str) -> str:
        """
        Get practical examples for a Python topic.
        
        Args:
            topic: Python topic (e.g., "list comprehensions", "decorators", "classes")
            
        Returns:
            Multiple examples with explanations
        """
        question = f"Show me 3-5 practical examples of {topic} in Python with explanations for each example. Include different use cases and complexity levels."
        
        return self.ask(question)
    
    def debug_help(self, code: str, error: str = None) -> str:
        """
        Get help debugging Python code.
        
        Args:
            code: The problematic Python code
            error: Error message (if any)
            
        Returns:
            Debugging suggestions and fixes
        """
        if self.verbose:
            print(f"🐛 Debug Help Request:")
            print("Code:", code)
            if error:
                print("Error:", error)
        
        question = f"Help me debug this Python code:\n\n```python\n{code}\n```"
        if error:
            question += f"\n\nError message: {error}"
        question += "\n\nPlease explain what's wrong and how to fix it."
        
        return self.ask(question)
    
    def best_practices(self, topic: str) -> str:
        """
        Get Python best practices for a specific topic.
        
        Args:
            topic: Python topic or concept
            
        Returns:
            Best practices and recommendations
        """
        question = f"What are the best practices for {topic} in Python? Include do's and don'ts with examples."
        
        return self.ask(question)
    
    def learning_path(self, current_level: str = "beginner") -> str:
        """
        Get a learning path recommendation for Python.
        
        Args:
            current_level: Current skill level ("beginner", "intermediate", "advanced")
            
        Returns:
            Structured learning path
        """
        question = f"Suggest a learning path for a {current_level} Python programmer. What topics should they focus on next and in what order?"
        
        return self.ask(question)
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
        if self.verbose:
            print("🧹 Conversation history cleared.")
    
    def get_history(self) -> List[Tuple[str, str]]:
        """Get conversation history."""
        return self.conversation_history.copy()
    
    def __repr__(self):
        """String representation."""
        return f"SimplePythonChat(provider={self.provider_name}, model={self.model_name}, conversations={len(self.conversation_history)})"


# Convenience function for quick access
def simple_python_chat(provider: str = "google", model: str = "gemini-1.5-pro", **kwargs) -> SimplePythonChat:
    """
    Create a SimplePythonChat instance quickly.
    
    Args:
        provider: LLM provider ("google", "openai", "anthropic")
        model: Model name
        **kwargs: Additional arguments for SimplePythonChat
        
    Returns:
        SimplePythonChat instance
    """
    return SimplePythonChat(provider=provider, model=model, **kwargs)


class InteractiveCodeChat:
    """
    Interactive conversational Python code chat with session memory and code execution.
    
    Features:
    - Conversational interface with memory
    - Code execution capabilities
    - Session management
    - Interactive learning
    - Code explanation and debugging
    """
    
    def __init__(self, 
                 provider: str = "google",
                 model: str = "gemini-1.5-pro",
                 api_key: Optional[str] = None,
                 verbose: bool = True,
                 auto_install: bool = True,
                 session_name: str = "default"):
        """
        Initialize Interactive Code Chat.
        
        Args:
            provider: LLM provider ("google", "openai", "anthropic")
            model: Model name
            api_key: API key (uses environment variable if not provided)
            verbose: Show detailed output
            auto_install: Automatically install missing packages
            session_name: Name for this chat session
        """
        self.provider_name = provider
        self.model_name = model
        self.verbose = verbose
        self.auto_install = auto_install
        self.session_name = session_name
        
        # Initialize the core AIPython engine
        self.ai_engine = AIPython(
            provider=provider,
            model=model,
            api_key=api_key,
            verbose=verbose,
            auto_install=auto_install,
            ask_permission=False  # For smooth conversation flow
        )
        
        # Session management
        self.conversation_history = []
        self.code_execution_history = []
        self.session_context = {}
        
        if self.verbose:
            print(f"🤖 Interactive Code Chat initialized")
            print(f"   Provider: {self.provider_name}")
            print(f"   Model: {self.model_name}")
            print(f"   Session: {self.session_name}")
            print(f"   Features: Conversation + Code Execution")
    
    def chat(self, message: str) -> str:
        """
        Simple conversational response without code execution.
        
        Args:
            message: User's message/question
            
        Returns:
            AI response as text
        """
        # Add context from conversation history
        context_prompt = self._build_context_prompt()
        
        full_prompt = f"""
        {context_prompt}
        
        User: {message}
        
        Provide a helpful, conversational response. Focus on Python programming assistance, 
        explanations, and guidance. Do not generate code unless specifically requested.
        Keep the tone friendly and educational.
        """
        
        try:
            # Get response from the AI engine
            response = self.ai_engine._generate_code(full_prompt)
            
            # Store in conversation history
            self.conversation_history.append({
                "type": "chat",
                "user_message": message,
                "ai_response": response,
                "timestamp": datetime.datetime.now().isoformat()
            })
            
            if self.verbose:
                print(f"💬 Chat Response:")
                print(f"   {response}")
            
            return response
            
        except Exception as e:
            error_msg = f"Error in chat: {str(e)}"
            if self.verbose:
                print(f"❌ {error_msg}")
            return error_msg
    
    def chat_with_code(self, message: str) -> Dict[str, Any]:
        """
        Conversational response with code execution when code is present.
        
        Args:
            message: User's message/question
            
        Returns:
            Dictionary containing response, code (if any), and execution results
        """
        # Add context from conversation and code history
        context_prompt = self._build_full_context_prompt()
        
        full_prompt = f"""
        {context_prompt}
        
        User: {message}
        
        Provide a helpful response. If the user is asking for code, examples, or wants to 
        execute something, generate appropriate Python code. Otherwise, provide conversational assistance.
        
        Focus on:
        - Python programming help
        - Code explanations and examples
        - Problem-solving assistance
        - Learning guidance
        - Debugging help
        
        If generating code, make it clear, well-commented, and executable.
        """
        
        try:
            # Use the full AIPython engine for code generation and execution
            result = self.ai_engine.ask(message + f"\n\nContext: {context_prompt}")
            
            # Extract information about the execution
            execution_info = {
                "user_message": message,
                "ai_response": "Code executed successfully",
                "code_generated": True,
                "execution_successful": True,
                "timestamp": datetime.datetime.now().isoformat(),
                "result": result
            }
            
            # Store in both conversation and code execution history
            self.conversation_history.append(execution_info)
            self.code_execution_history.append(execution_info)
            
            if self.verbose:
                print(f"💻 Code Chat Response:")
                print(f"   Executed successfully with result")
            
            return {
                "response": "Code executed successfully",
                "result": result,
                "execution_info": execution_info
            }
            
        except Exception as e:
            error_info = {
                "user_message": message,
                "ai_response": f"Error: {str(e)}",
                "code_generated": False,
                "execution_successful": False,
                "timestamp": datetime.datetime.now().isoformat(),
                "error": str(e)
            }
            
            self.conversation_history.append(error_info)
            
            if self.verbose:
                print(f"❌ Error in code chat: {str(e)}")
            
            return {
                "response": f"Error: {str(e)}",
                "result": None,
                "execution_info": error_info
            }
    
    def _build_context_prompt(self) -> str:
        """Build context from recent conversation history."""
        if not self.conversation_history:
            return "This is the start of a new Python programming conversation."
        
        # Get last 5 exchanges for context
        recent_history = self.conversation_history[-5:]
        context_lines = ["Previous conversation context:"]
        
        for entry in recent_history:
            context_lines.append(f"User: {entry['user_message']}")
            context_lines.append(f"AI: {entry['ai_response']}")
        
        return "\n".join(context_lines)
    
    def _build_full_context_prompt(self) -> str:
        """Build full context including code execution history."""
        context_parts = []
        
        if self.conversation_history:
            context_parts.append("Conversation History:")
            recent_conv = self.conversation_history[-3:]
            for entry in recent_conv:
                context_parts.append(f"User: {entry['user_message']}")
                context_parts.append(f"AI: {entry['ai_response']}")
        
        if self.code_execution_history:
            context_parts.append("\nRecent Code Executions:")
            recent_code = self.code_execution_history[-2:]
            for entry in recent_code:
                if entry.get('execution_successful'):
                    context_parts.append(f"Successfully executed code for: {entry['user_message']}")
        
        if self.session_context:
            context_parts.append(f"\nSession Context: {self.session_context}")
        
        return "\n".join(context_parts) if context_parts else "New conversation session."
    
    def set_session_context(self, key: str, value: Any):
        """Set context variable for this session."""
        self.session_context[key] = value
        if self.verbose:
            print(f"📝 Session context updated: {key} = {value}")
    
    def get_session_context(self, key: str = None):
        """Get session context."""
        if key:
            return self.session_context.get(key)
        return self.session_context.copy()
    
    def clear_history(self):
        """Clear conversation and code execution history."""
        self.conversation_history = []
        self.code_execution_history = []
        if self.verbose:
            print("🧹 Chat history cleared.")
    
    def save_session(self, filepath: str = None):
        """Save current session to file."""
        if not filepath:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"chat_session_{self.session_name}_{timestamp}.json"
        
        session_data = {
            "session_name": self.session_name,
            "provider": self.provider_name,
            "model": self.model_name,
            "conversation_history": self.conversation_history,
            "code_execution_history": self.code_execution_history,
            "session_context": self.session_context,
            "created": datetime.datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        if self.verbose:
            print(f"💾 Session saved to: {filepath}")
        return filepath
    
    def load_session(self, filepath: str):
        """Load session from file."""
        try:
            with open(filepath, 'r') as f:
                session_data = json.load(f)
            
            self.conversation_history = session_data.get('conversation_history', [])
            self.code_execution_history = session_data.get('code_execution_history', [])
            self.session_context = session_data.get('session_context', {})
            
            if self.verbose:
                print(f"📂 Session loaded from: {filepath}")
                print(f"   Conversations: {len(self.conversation_history)}")
                print(f"   Code executions: {len(self.code_execution_history)}")
            
            return True
            
        except Exception as e:
            if self.verbose:
                print(f"❌ Error loading session: {str(e)}")
            return False
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of current conversation."""
        return {
            "session_name": self.session_name,
            "total_exchanges": len(self.conversation_history),
            "code_executions": len(self.code_execution_history),
            "session_context_keys": list(self.session_context.keys()),
            "provider": self.provider_name,
            "model": self.model_name
        }
    
    def __repr__(self):
        """String representation."""
        return f"InteractiveCodeChat(session={self.session_name}, provider={self.provider_name}, model={self.model_name}, exchanges={len(self.conversation_history)})"


# Convenience function for quick access
def interactive_code_chat(provider: str = "google", 
                         model: str = "gemini-1.5-pro", 
                         session_name: str = "default",
                         **kwargs) -> InteractiveCodeChat:
    """
    Create an InteractiveCodeChat instance quickly.
    
    Args:
        provider: LLM provider ("google", "openai", "anthropic")
        model: Model name
        session_name: Name for the chat session
        **kwargs: Additional arguments for InteractiveCodeChat
        
    Returns:
        InteractiveCodeChat instance
    """
    return InteractiveCodeChat(provider=provider, model=model, session_name=session_name, **kwargs)
