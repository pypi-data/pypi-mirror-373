"""
AIObject - AI-powered wrapper with multiple LLM support and auto-visualization
Enhanced with package installation, verification, and AI summary capabilities
"""

import pandas as pd
import numpy as np
import json
import os
import io
import base64
import subprocess
import sys
import time
from typing import Any, Optional, Dict, Union, Literal, List
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import display, Image, HTML, Markdown

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


class AIObject:
    """
    AI-powered wrapper for Python objects with multiple LLM support.
    
    Enhanced Features:
    - Multiple LLM providers (Google, OpenAI, etc.)
    - Automatic visualization generation
    - Smart code execution with output display
    - Dynamic package installation with user permission
    - Code verification and error recovery
    - AI-generated operation summaries
    - Image generation and display
    
    Usage:
        ai_df = AIObject(df, model="gemini-1.5-pro")
        ai_df.ask("Plot sales trend by month")
        ai_df.ask("Show correlation heatmap")
    """
    
    def __init__(self, obj: Any, model: str = "gemini-1.5-pro", api_key: Optional[str] = None, 
                 auto_install: bool = False, verbose: bool = True):
        """
        Initialize AIObject with any Python object.
        
        Args:
            obj: The object to wrap (DataFrame, Model, etc.)
            model: LLM model to use
            api_key: API key for the LLM provider
            auto_install: Whether to auto-install packages with user permission
            verbose: Whether to show detailed operations
        """
        self.obj = obj
        self.obj_type = self._detect_object_type(obj)
        self.model = model
        self.auto_install = auto_install
        self.verbose = verbose
        self.operation_history = []
        self.installed_packages = set()
        
        # Setup LLM - NO HARDCODED KEYS!
        self.api_key = api_key or self._get_api_key_from_env(model)
        self.llm_provider = self._setup_llm(model, self.api_key)
        self.ai_enabled = self.llm_provider is not None
        
        if self.verbose:
            print(f"🚀 AIObject initialized: {self.obj_type}")
            print(f"🤖 AI Model: {model} ({'✅ Ready' if self.ai_enabled else '❌ Not available'})")
            print(f"📦 Auto-install: {'✅ Enabled' if auto_install else '❌ Disabled'}")
            
    def _get_user_permission(self, action: str, details: str = "") -> bool:
        """Get user permission for potentially risky operations."""
        print(f"\n🔐 PERMISSION REQUEST")
        print(f"Action: {action}")
        if details:
            print(f"Details: {details}")
        
        response = input("Do you want to proceed? (y/n): ").lower().strip()
        return response in ['y', 'yes', 'ok', 'okay', '1', 'true']
    
    def _install_package(self, package: str) -> bool:
        """Install a Python package with user permission."""
        if package in self.installed_packages:
            return True
            
        if not self.auto_install:
            print(f"📦 Package '{package}' is required but auto-install is disabled.")
            print(f"💡 Please install manually: pip install {package}")
            return False
        
        # Ask for permission
        if not self._get_user_permission(
            f"Install package '{package}'", 
            f"This will run: pip install {package}"
        ):
            print(f"❌ Installation of '{package}' declined by user")
            return False
        
        try:
            print(f"📦 Installing {package}...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                self.installed_packages.add(package)
                print(f"✅ Successfully installed {package}")
                return True
            else:
                print(f"❌ Failed to install {package}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"❌ Installation of {package} timed out")
            return False
        except Exception as e:
            print(f"❌ Error installing {package}: {e}")
            return False
    
    def _check_and_install_requirements(self, code: str) -> bool:
        """Check code for package requirements and install if needed."""
        # Common package mappings
        package_mappings = {
            'plotly': 'plotly',
            'bokeh': 'bokeh',
            'altair': 'altair',
            'sklearn': 'scikit-learn',
            'cv2': 'opencv-python',
            'PIL': 'Pillow',
            'requests': 'requests',
            'bs4': 'beautifulsoup4',
            'dash': 'dash',
            'streamlit': 'streamlit'
        }
        
        # Extract imports from code
        imports = []
        for line in code.split('\n'):
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                # Extract package name
                if line.startswith('import '):
                    pkg = line.replace('import ', '').split()[0].split('.')[0]
                elif line.startswith('from '):
                    pkg = line.replace('from ', '').split()[0].split('.')[0]
                
                if pkg in package_mappings:
                    imports.append(package_mappings[pkg])
                elif pkg not in ['pandas', 'numpy', 'matplotlib', 'seaborn', 'os', 'sys', 'json']:
                    imports.append(pkg)
        
        # Install missing packages
        all_installed = True
        for package in set(imports):
            if package not in self.installed_packages:
                try:
                    __import__(package.replace('-', '_'))
                    self.installed_packages.add(package)
                except ImportError:
                    if not self._install_package(package):
                        all_installed = False
        
        return all_installed
    
    def _verify_execution(self, code: str, result: Any, question: str) -> Dict[str, Any]:
        """Verify if the execution was successful and provide feedback."""
        verification_prompt = f"""
You are OrionAI's verification system. Analyze this execution:

ORIGINAL QUESTION: "{question}"

GENERATED CODE:
```python
{code}
```

EXECUTION RESULT: {str(result)[:500]}

Provide a JSON response with:
{{
    "success": true/false,
    "explanation": "Brief explanation of what was accomplished",
    "issues": ["list of any issues found"],
    "suggestions": ["list of improvements if any"],
    "summary": "One-sentence summary of the operation"
}}

Return only valid JSON.
"""
        
        try:
            if self.ai_enabled:
                verification_response = self._get_ai_response(verification_prompt)
                verification_data = json.loads(verification_response)
            else:
                verification_data = {
                    "success": result is not None,
                    "explanation": "Code executed successfully" if result is not None else "Execution failed",
                    "issues": [],
                    "suggestions": [],
                    "summary": f"Processed query: {question[:50]}..."
                }
            
            return verification_data
            
        except Exception as e:
            return {
                "success": False,
                "explanation": f"Verification failed: {e}",
                "issues": ["Verification system error"],
                "suggestions": ["Manual review recommended"],
                "summary": "Execution completed with verification issues"
            }
    
    def _generate_ai_summary(self, operations: List[Dict]) -> str:
        """Generate an AI summary of all operations performed."""
        if not operations:
            return "No operations performed yet."
        
        summary_prompt = f"""
You are OrionAI's summary generator. Create a comprehensive summary of the operations performed:

OPERATIONS PERFORMED:
{json.dumps(operations, indent=2)}

Create a markdown summary that includes:
1. **Overview**: What was accomplished overall
2. **Key Operations**: List of main operations with brief descriptions
3. **Visualizations Created**: List any plots/charts generated
4. **Data Insights**: Key findings or patterns discovered
5. **Technical Details**: Packages used, any installations, etc.
6. **Recommendations**: Suggestions for further analysis

Make it professional, informative, and well-formatted in markdown.
"""
        
        try:
            if self.ai_enabled:
                summary_response = self._get_ai_response(summary_prompt)
                return summary_response
            else:
                # Fallback summary
                total_ops = len(operations)
                successful_ops = sum(1 for op in operations if op.get('verification', {}).get('success', False))
                
                return f"""
# OrionAI Operations Summary

## Overview
Performed {total_ops} operations with {successful_ops} successful executions.

## Operations
{chr(10).join([f"- {op.get('question', 'Unknown operation')}" for op in operations])}

## Status
- Success Rate: {successful_ops/total_ops*100:.1f}%
- AI Features: {'Enabled' if self.ai_enabled else 'Disabled'}
"""
                
        except Exception as e:
            return f"# Summary Generation Failed\nError: {e}"

    def _detect_object_type(self, obj: Any) -> str:
        """Detect the type of object we're working with."""
        if hasattr(obj, 'shape') and hasattr(obj, 'columns'):
            return 'DataFrame'
        elif hasattr(obj, 'parameters'):
            return 'Model'
        elif isinstance(obj, str) and obj.endswith('.pdf'):
            return 'PDF'
        elif isinstance(obj, str):
            return 'File'
        else:
            return 'Unknown'
    
    def _setup_llm(self, model: str, api_key: Optional[str] = None) -> Optional[Any]:
        """Setup LLM provider based on model name."""
        api_key = api_key or self._get_api_key_from_env(model)
        
        if model.startswith("gemini") or model.startswith("google"):
            return self._setup_google(model, api_key)
        elif model.startswith("gpt") or model.startswith("openai"):
            return self._setup_openai(model, api_key)
        elif model.startswith("claude") or model.startswith("anthropic"):
            return self._setup_anthropic(model, api_key)
        else:
            print(f"⚠️ Unknown model: {model}")
            print("🤖 Supported models:")
            print("   - Google: gemini-1.5-pro, gemini-1.5-flash")
            print("   - OpenAI: gpt-4, gpt-3.5-turbo")
            print("   - Anthropic: claude-3-opus, claude-3-sonnet")
            return None
    
    def _get_api_key_from_env(self, model: str) -> Optional[str]:
        """Get API key from environment based on model - NO HARDCODED KEYS!"""
        if model.startswith("gemini") or model.startswith("google"):
            key = os.environ.get('GOOGLE_API_KEY')
            if not key:
                print("❌ GOOGLE_API_KEY environment variable not set")
                print("💡 Get your key from: https://makersuite.google.com/app/apikey")
                print("💡 Set it with: export GOOGLE_API_KEY=your_key_here")
            return key
        elif model.startswith("gpt") or model.startswith("openai"):
            key = os.environ.get('OPENAI_API_KEY')
            if not key:
                print("❌ OPENAI_API_KEY environment variable not set")
                print("💡 Get your key from: https://platform.openai.com/api-keys")
                print("💡 Set it with: export OPENAI_API_KEY=your_key_here")
            return key
        elif model.startswith("claude") or model.startswith("anthropic"):
            key = os.environ.get('ANTHROPIC_API_KEY')
            if not key:
                print("❌ ANTHROPIC_API_KEY environment variable not set")
                print("💡 Get your key from: https://console.anthropic.com/")
                print("💡 Set it with: export ANTHROPIC_API_KEY=your_key_here")
            return key
        return None
    
    def _setup_google(self, model: str, api_key: str) -> Optional[Any]:
        """Setup Google Gemini."""
        if not GOOGLE_AVAILABLE:
            print("❌ Google AI not available. Install: pip install google-generativeai")
            return None
        
        if not api_key:
            print("❌ Google API key not found")
            return None
        
        try:
            genai.configure(api_key=api_key)
            return genai.GenerativeModel(model)
        except Exception as e:
            print(f"❌ Google setup failed: {e}")
            return None
    
    def _setup_openai(self, model: str, api_key: str) -> Optional[Any]:
        """Setup OpenAI."""
        if not OPENAI_AVAILABLE:
            print("❌ OpenAI not available. Install: pip install openai")
            return None
        
        if not api_key:
            print("❌ OpenAI API key not found")
            return None
        
        try:
            openai.api_key = api_key
            return {"model": model, "client": openai}
        except Exception as e:
            print(f"❌ OpenAI setup failed: {e}")
            return None
    
    def _setup_anthropic(self, model: str, api_key: str) -> Optional[Any]:
        """Setup Anthropic Claude."""
        if not ANTHROPIC_AVAILABLE:
            print("❌ Anthropic not available. Install: pip install anthropic")
            return None
        
        if not api_key:
            print("❌ Anthropic API key not found")
            return None
            
        try:
            client = anthropic.Anthropic(api_key=api_key)
            # Test the connection
            test_response = client.messages.create(
                model=model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hello"}]
            )
            print(f"✅ Anthropic Claude {model} initialized successfully")
            return client
        except Exception as e:
            print(f"❌ Anthropic setup failed: {e}")
            return None
    
    def _get_context(self) -> Dict[str, Any]:
        """Get context about the object for AI."""
        if self.obj_type == 'DataFrame':
            # Convert sample data to JSON-serializable format
            sample_data = self.obj.head(3).copy()
            # Convert datetime columns to strings
            for col in sample_data.columns:
                if pd.api.types.is_datetime64_any_dtype(sample_data[col]):
                    sample_data[col] = sample_data[col].dt.strftime('%Y-%m-%d')
            
            return {
                'type': 'DataFrame',
                'shape': self.obj.shape,
                'columns': list(self.obj.columns),
                'dtypes': {col: str(dtype) for col, dtype in self.obj.dtypes.items()},
                'sample_data': sample_data.to_dict('records'),
                'numeric_columns': list(self.obj.select_dtypes(include=[np.number]).columns),
                'categorical_columns': list(self.obj.select_dtypes(include=['object', 'category']).columns),
                'memory_usage': f"{self.obj.memory_usage(deep=True).sum() / 1024**2:.2f} MB"
            }
        else:
            return {'type': self.obj_type, 'object': str(type(self.obj))}
    
    def ask(self, question: str, show_code: bool = False, verify: bool = True) -> Any:
        """
        Ask a natural language question about the object with enhanced features.
        
        Args:
            question: Natural language question
            show_code: Whether to display the generated code
            verify: Whether to verify execution and provide feedback
            
        Returns:
            Result of the operation (DataFrame, plot, summary, etc.)
        """
        start_time = time.time()
        
        if not self.ai_enabled:
            return self._fallback_ask(question)
        
        try:
            # Detect if visualization is requested
            is_plot_request = self._is_plot_request(question)
            
            # Create enhanced prompt
            context = self._get_context()
            prompt = self._create_prompt(question, context, is_plot_request)
            
            # Get AI response
            code = self._get_ai_response(prompt)
            
            if show_code:
                print("🔍 Generated Code:")
                print("```python")
                print(code)
                print("```")
                print()
            
            # Check and install required packages
            if not self._check_and_install_requirements(code):
                print("⚠️ Some packages could not be installed. Code may fail.")
            
            # Execute the code and handle visualization
            result = self._execute_and_display(code, is_plot_request)
            
            # Verify execution if requested
            verification = None
            if verify:
                verification = self._verify_execution(code, result, question)
                if self.verbose:
                    print(f"\n🔍 Verification: {verification.get('summary', 'Complete')}")
                    if verification.get('issues'):
                        print(f"⚠️ Issues: {', '.join(verification['issues'])}")
            
            # Record operation
            operation_record = {
                'timestamp': time.time(),
                'question': question,
                'code': code,
                'is_plot': is_plot_request,
                'execution_time': time.time() - start_time,
                'verification': verification,
                'result_type': type(result).__name__
            }
            self.operation_history.append(operation_record)
            
            return result
            
        except Exception as e:
            error_msg = f"❌ Error processing query: {e}"
            print(error_msg)
            
            # Try to provide a fallback
            fallback_result = self._fallback_ask(question)
            if fallback_result != "❌ AI not available and no fallback for this question":
                print("🔄 Using fallback approach...")
                return fallback_result
            
            # Record failed operation
            operation_record = {
                'timestamp': time.time(),
                'question': question,
                'error': str(e),
                'execution_time': time.time() - start_time,
                'verification': {'success': False, 'explanation': 'Execution failed', 'summary': f'Failed: {str(e)[:50]}...'}
            }
            self.operation_history.append(operation_record)
            
            return error_msg
            return self._execute_and_display(code, is_plot_request)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return self._fallback_ask(question)
    
    def _is_plot_request(self, question: str) -> bool:
        """Detect if the question requests a plot/visualization."""
        plot_keywords = [
            'plot', 'chart', 'graph', 'visualize', 'show', 'display',
            'histogram', 'scatter', 'line', 'bar', 'pie', 'heatmap',
            'correlation', 'distribution', 'trend', 'comparison'
        ]
        return any(keyword in question.lower() for keyword in plot_keywords)
    
    def _create_prompt(self, question: str, context: Dict, is_plot: bool) -> str:
        """Create an enhanced prompt for the AI."""
        base_prompt = f"""
You are OrionAI, an expert data scientist and Python programmer.

CONTEXT:
{json.dumps(context, indent=2)}

USER QUESTION: "{question}"

INSTRUCTIONS:
1. Generate Python code that answers the question
2. Use 'obj' to refer to the DataFrame
3. Import required libraries (pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns)
4. Be concise and practical
5. Handle errors gracefully

"""
        
        if is_plot:
            base_prompt += """
6. CREATE VISUALIZATION:
   - Generate appropriate plots using matplotlib/seaborn
   - Use plt.figure(figsize=(10, 6)) for good sizing
   - Add proper titles, labels, and styling
   - Use plt.tight_layout() for better layout
   - End with plt.show() to display the plot
   - Save the plot result to 'result' variable

"""
        else:
            base_prompt += """
6. DATA ANALYSIS:
   - Return meaningful results as DataFrame, Series, or summary
   - Store final result in 'result' variable
   - Format numbers appropriately

"""
        
        base_prompt += """
Return ONLY executable Python code. No explanations or markdown.

CODE:
"""
        return base_prompt
    
    def _get_ai_response(self, prompt: str) -> str:
        """Get response from the configured AI provider."""
        try:
            if self.model.startswith("gemini"):
                response = self.llm_provider.generate_content(prompt)
                code = response.text.strip()
            elif self.model.startswith("gpt"):
                response = openai.ChatCompletion.create(
                    model=self.llm_provider["model"],
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1
                )
                code = response.choices[0].message.content.strip()
            else:
                raise Exception(f"Unknown model: {self.model}")
            
            # Clean the code
            if '```python' in code:
                code = code.split('```python')[1].split('```')[0].strip()
            elif '```' in code:
                code = code.split('```')[1].strip()
            
            return code
            
        except Exception as e:
            raise Exception(f"AI response failed: {e}")
    
    def _execute_and_display(self, code: str, is_plot: bool) -> Any:
        """Execute code and handle visualization display."""
        try:
            # Create execution environment
            namespace = {
                'obj': self.obj,
                'pd': pd,
                'np': np,
                'plt': plt,
                'sns': sns,
                'result': None
            }
            
            # Clear any existing plots
            plt.clf()
            
            # Execute the code
            exec(code, namespace)
            
            # Handle plot display
            if is_plot:
                # Display the plot
                plt.show()
                
                # Save plot as image for return
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
                buf.seek(0)
                
                # Also return the result if available
                if namespace.get('result') is not None:
                    return namespace['result']
                else:
                    return "📊 Visualization generated and displayed"
            
            # Return the result for non-plot queries
            if namespace.get('result') is not None:
                result = namespace['result']
                
                # Display DataFrames nicely
                if isinstance(result, pd.DataFrame):
                    display(result)
                elif isinstance(result, pd.Series):
                    display(result)
                else:
                    print(f"📊 Result: {result}")
                
                return result
            else:
                return "✅ Operation completed successfully"
                
        except Exception as e:
            raise Exception(f"Code execution failed: {e}")
    
    def _fallback_ask(self, question: str) -> Any:
        """Fallback when AI is not available."""
        question_lower = question.lower()
        
        if self.obj_type == 'DataFrame':
            if 'missing' in question_lower or 'null' in question_lower:
                result = self.obj.isnull().sum()
                display(result)
                return result
            elif 'shape' in question_lower or 'size' in question_lower:
                return f"Shape: {self.obj.shape}"
            elif 'head' in question_lower or 'first' in question_lower:
                result = self.obj.head()
                display(result)
                return result
            elif 'describe' in question_lower or 'summary' in question_lower:
                result = self.obj.describe()
                display(result)
                return result
            elif 'columns' in question_lower:
                return list(self.obj.columns)
        
        return "❌ AI not available and no fallback for this question"
    
    def switch_model(self, model: str, api_key: Optional[str] = None):
        """Switch to a different LLM model."""
        print(f"🔄 Switching from {self.model} to {model}...")
        self.model = model
        self.llm_provider = self._setup_llm(model, api_key)
        self.ai_enabled = self.llm_provider is not None
        print(f"✅ Now using {model} ({'enabled' if self.ai_enabled else 'disabled'})")
    
    def available_models(self) -> Dict[str, bool]:
        """Show available models and their status."""
        models = {
            "gemini-1.5-pro": GOOGLE_AVAILABLE and bool(self._get_api_key("gemini-1.5-pro")),
            "gemini-1.5-flash": GOOGLE_AVAILABLE and bool(self._get_api_key("gemini-1.5-flash")),
            "gpt-4": OPENAI_AVAILABLE and bool(self._get_api_key("gpt-4")),
            "gpt-3.5-turbo": OPENAI_AVAILABLE and bool(self._get_api_key("gpt-3.5-turbo")),
        }
        
        print("📋 Available Models:")
        for model, available in models.items():
            status = "✅ Ready" if available else "❌ Not available"
            current = " (Current)" if model == self.model else ""
            print(f"  {model}: {status}{current}")
        
        return models
    
    def optimize(self, target: str = "memory") -> Dict[str, Any]:
        """Optimize the object (memory, performance, etc.)."""
        if self.obj_type != 'DataFrame':
            return {"message": "Optimization only available for DataFrames"}
        
        if target == "memory":
            return self._optimize_memory()
        else:
            return {"message": f"Optimization for '{target}' not implemented"}
    
    def _optimize_memory(self) -> Dict[str, Any]:
        """Optimize DataFrame memory usage."""
        original_memory = self.obj.memory_usage(deep=True).sum()
        
        # Convert float64 to float32 where possible
        for col in self.obj.select_dtypes(include=['float64']).columns:
            self.obj[col] = pd.to_numeric(self.obj[col], downcast='float')
        
        # Convert int64 to smaller int types where possible
        for col in self.obj.select_dtypes(include=['int64']).columns:
            self.obj[col] = pd.to_numeric(self.obj[col], downcast='integer')
        
        # Convert object to category for repeated strings
        for col in self.obj.select_dtypes(include=['object']).columns:
            if self.obj[col].nunique() / len(self.obj) < 0.5:
                self.obj[col] = self.obj[col].astype('category')
        
        new_memory = self.obj.memory_usage(deep=True).sum()
        savings = original_memory - new_memory
        
        result = {
            "original_memory_mb": f"{original_memory / 1024**2:.2f}",
            "new_memory_mb": f"{new_memory / 1024**2:.2f}",
            "savings_mb": f"{savings / 1024**2:.2f}",
            "savings_percent": f"{(savings / original_memory) * 100:.1f}%"
        }
        
        print("🔧 Memory Optimization Results:")
        for key, value in result.items():
            print(f"  {key}: {value}")
        
        return result
    
    def info(self) -> Dict[str, Any]:
        """Get comprehensive information about the object."""
        context = self._get_context()
        info_data = {
            "object_type": self.obj_type,
            "model": self.model,
            "ai_enabled": self.ai_enabled,
            "operations_count": len(self.operation_history),
            "installed_packages": list(self.installed_packages),
            **context
        }
        
        print("📊 Object Information:")
        for key, value in info_data.items():
            if isinstance(value, dict) and len(str(value)) > 100:
                print(f"  {key}: {type(value).__name__} with {len(value)} items")
            elif isinstance(value, list) and len(value) > 5:
                print(f"  {key}: [{', '.join(map(str, value[:3]))}, ...] ({len(value)} items)")
            else:
                print(f"  {key}: {value}")
        
        return info_data
    
    def get_operation_history(self) -> List[Dict]:
        """Get the history of all operations performed."""
        return self.operation_history
    
    def clear_history(self):
        """Clear the operation history."""
        self.operation_history = []
        print("🗑️ Operation history cleared")
    
    def get_ai_summary(self, detailed: bool = True) -> str:
        """Get an AI-generated summary of all operations performed."""
        if not self.operation_history:
            return "No operations performed yet."
        
        print("🤖 Generating AI summary...")
        summary = self._generate_ai_summary(self.operation_history)
        
        if detailed:
            display(Markdown(summary))
        else:
            print(summary)
        
        return summary
    
    def visualize_capabilities(self):
        """Show all visualization capabilities with examples."""
        capabilities = {
            "Basic Plots": [
                "Plot revenue by month",
                "Show distribution of values",
                "Create bar chart of categories"
            ],
            "Advanced Plots": [
                "Create correlation heatmap", 
                "Show scatter plot with regression line",
                "Generate subplot with multiple charts"
            ],
            "Statistical Plots": [
                "Show box plot by category",
                "Create violin plot",
                "Display histogram with normal curve"
            ],
            "Time Series": [
                "Plot time series with trend",
                "Show seasonal decomposition",
                "Create moving average chart"
            ]
        }
        
        print("🎨 VISUALIZATION CAPABILITIES")
        print("=" * 50)
        
        for category, examples in capabilities.items():
            print(f"\n📊 {category}:")
            for example in examples:
                print(f"  • {example}")
        
        print(f"\n💡 Usage: ai_df.ask('Your visualization request here')")
        print(f"🔧 Tip: Add 'show_code=True' to see generated code")
    
    def __repr__(self) -> str:
        return f"AIObject({self.obj_type}, model={self.model}, ai_enabled={self.ai_enabled}, operations={len(self.operation_history)})"
    
    def __repr__(self) -> str:
        return f"AIObject({self.obj_type}, model={self.model}, ai_enabled={self.ai_enabled})"
