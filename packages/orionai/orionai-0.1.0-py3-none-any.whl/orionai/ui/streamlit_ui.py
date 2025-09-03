"""
OrionAI Python Streamlit UI
Interactive interface for testing all OrionAI Python features
"""

import streamlit as st
import sys
import os
import traceback
from typing import Optional, Dict, Any
import json
import time

# Add the parent directory to the path so we can import orionai
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from orionai.python.aipython import AIPython, SimplePythonChat, InteractiveCodeChat
except ImportError as e:
    st.error(f"Failed to import OrionAI modules: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="OrionAI Python - Interactive UI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'ai_instance' not in st.session_state:
    st.session_state.ai_instance = None
if 'chat_instance' not in st.session_state:
    st.session_state.chat_instance = None
if 'code_chat_instance' not in st.session_state:
    st.session_state.code_chat_instance = None
if 'execution_history' not in st.session_state:
    st.session_state.execution_history = []

def configure_llm_sidebar():
    """Configure LLM settings in sidebar"""
    st.sidebar.title("🔧 LLM Configuration")
    
    # Provider selection
    provider = st.sidebar.selectbox(
        "Select LLM Provider",
        ["google", "openai", "anthropic"],
        index=0,
        help="Choose your preferred LLM provider"
    )
    
    # Model selection based on provider
    model_options = {
        "google": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"],
        "openai": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
        "anthropic": ["claude-3-sonnet-20240229", "claude-3-opus-20240229", "claude-3-haiku-20240307"]
    }
    
    model = st.sidebar.selectbox(
        "Select Model",
        model_options[provider],
        help=f"Choose a model for {provider}"
    )
    
    # API Key input
    api_key = st.sidebar.text_input(
        "API Key (optional)",
        type="password",
        help="Enter API key or use environment variable"
    )
    
    # Advanced settings
    st.sidebar.subheader("⚙️ Advanced Settings")
    
    verbose = st.sidebar.checkbox("Verbose Output", value=True)
    auto_install = st.sidebar.checkbox("Auto Install Packages", value=True)
    ask_permission = st.sidebar.checkbox("Ask Permission", value=False)
    max_retries = st.sidebar.slider("Max Retries", 1, 5, 3)
    
    # Workspace settings
    workspace_dir = st.sidebar.text_input(
        "Workspace Directory",
        value="./ui_outputs",
        help="Directory for saving outputs"
    )
    
    return {
        "provider": provider,
        "model": model,
        "api_key": api_key if api_key else None,
        "verbose": verbose,
        "auto_install": auto_install,
        "ask_permission": ask_permission,
        "max_retries": max_retries,
        "workspace_dir": workspace_dir
    }

def initialize_ai_instance(config: Dict[str, Any]) -> Optional[AIPython]:
    """Initialize AI instance with given configuration"""
    try:
        ai = AIPython(**config)
        st.sidebar.success(f"✅ Connected to {config['provider']}:{config['model']}")
        return ai
    except Exception as e:
        st.sidebar.error(f"❌ Failed to initialize: {str(e)}")
        return None

def display_execution_result(result: Any, execution_time: float):
    """Display execution result with proper formatting"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("📊 Result")
        
        # Try to display result in the best format
        if isinstance(result, str):
            st.text(result)
        elif hasattr(result, 'to_string'):  # pandas DataFrame/Series
            st.dataframe(result)
        elif isinstance(result, (list, dict)):
            st.json(result)
        else:
            st.write(result)
    
    with col2:
        st.metric("⏱️ Execution Time", f"{execution_time:.2f}s")

def main_interface():
    """Main interface for OrionAI Python UI"""
    
    # Header
    st.title("🚀 OrionAI Python - Interactive UI")
    st.markdown("Test all OrionAI Python features with an interactive interface")
    
    # Configure LLM in sidebar
    config = configure_llm_sidebar()
    
    # Initialize AI instance button
    if st.sidebar.button("🔄 Initialize/Update AI Instance"):
        with st.sidebar:
            with st.spinner("Initializing AI instance..."):
                st.session_state.ai_instance = initialize_ai_instance(config)
    
    # Check if AI instance is available
    if st.session_state.ai_instance is None:
        st.warning("⚠️ Please configure and initialize the AI instance in the sidebar first.")
        st.info("💡 Set your API key and click 'Initialize/Update AI Instance'")
        return
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🤖 AI Assistant", 
        "🐍 Python Chat", 
        "💬 Interactive Code", 
        "📊 Feature Tests", 
        "📈 Examples", 
        "📚 Documentation"
    ])
    
    with tab1:
        ai_assistant_tab()
    
    with tab2:
        python_chat_tab(config)
    
    with tab3:
        interactive_code_tab(config)
    
    with tab4:
        feature_tests_tab()
    
    with tab5:
        examples_tab()
    
    with tab6:
        documentation_tab()

def ai_assistant_tab():
    """AI Assistant tab for general Python tasks"""
    st.header("🤖 AI Python Assistant")
    st.markdown("Ask the AI to perform any Python task using natural language")
    
    # Task input
    task = st.text_area(
        "Describe your Python task:",
        height=100,
        placeholder="e.g., Create a pandas DataFrame with sample data and plot it"
    )
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        execute_button = st.button("🚀 Execute Task", type="primary")
    
    with col2:
        if st.button("🗑️ Clear History"):
            st.session_state.execution_history = []
            st.rerun()
    
    if execute_button and task:
        with st.spinner("Executing task..."):
            start_time = time.time()
            try:
                result = st.session_state.ai_instance.ask(task)
                execution_time = time.time() - start_time
                
                # Display result
                display_execution_result(result, execution_time)
                
                # Add to history
                st.session_state.execution_history.append({
                    "task": task,
                    "result": str(result)[:500] + "..." if len(str(result)) > 500 else str(result),
                    "execution_time": execution_time,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                })
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.code(traceback.format_exc())
    
    # Execution history
    if st.session_state.execution_history:
        st.subheader("📜 Execution History")
        for i, entry in enumerate(reversed(st.session_state.execution_history[-5:])):
            with st.expander(f"Task {len(st.session_state.execution_history)-i}: {entry['task'][:50]}..."):
                st.write(f"**Time:** {entry['timestamp']}")
                st.write(f"**Execution Time:** {entry['execution_time']:.2f}s")
                st.write(f"**Result:**")
                st.text(entry['result'])

def python_chat_tab(config: Dict[str, Any]):
    """Python learning chat tab"""
    st.header("🐍 Python Learning Chat")
    st.markdown("Interactive Python learning assistant for explanations and examples")
    
    # Initialize chat instance
    if st.session_state.chat_instance is None:
        with st.spinner("Initializing Python Chat..."):
            try:
                st.session_state.chat_instance = SimplePythonChat(
                    provider=config["provider"],
                    model=config["model"],
                    api_key=config["api_key"],
                    verbose=False
                )
                st.success("✅ Python Chat initialized")
            except Exception as e:
                st.error(f"❌ Failed to initialize Python Chat: {e}")
                return
    
    # Chat interface
    question = st.text_input(
        "Ask a Python question:",
        placeholder="e.g., How do list comprehensions work?"
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💬 Ask Question"):
            if question:
                with st.spinner("Getting answer..."):
                    try:
                        response = st.session_state.chat_instance.ask(question)
                        st.subheader("📝 Response")
                        st.markdown(response)
                    except Exception as e:
                        st.error(f"Error: {e}")
    
    with col2:
        if st.button("🔍 Explain Code"):
            code = st.text_area("Enter Python code to explain:", height=100)
            if code:
                with st.spinner("Explaining code..."):
                    try:
                        explanation = st.session_state.chat_instance.explain_code(code)
                        st.subheader("📖 Code Explanation")
                        st.markdown(explanation)
                    except Exception as e:
                        st.error(f"Error: {e}")
    
    with col3:
        topic = st.text_input("Topic for examples:", placeholder="e.g., decorators")
        if st.button("📚 Get Examples") and topic:
            with st.spinner("Generating examples..."):
                try:
                    examples = st.session_state.chat_instance.get_examples(topic)
                    st.subheader(f"🎯 Examples: {topic}")
                    st.markdown(examples)
                except Exception as e:
                    st.error(f"Error: {e}")

def interactive_code_tab(config: Dict[str, Any]):
    """Interactive code chat tab"""
    st.header("💬 Interactive Code Chat")
    st.markdown("Conversational interface with code execution and session memory")
    
    # Initialize code chat instance
    if st.session_state.code_chat_instance is None:
        session_name = st.text_input("Session Name:", value="streamlit_session")
        if st.button("🚀 Start Code Chat Session"):
            with st.spinner("Initializing Interactive Code Chat..."):
                try:
                    st.session_state.code_chat_instance = InteractiveCodeChat(
                        provider=config["provider"],
                        model=config["model"],
                        api_key=config["api_key"],
                        verbose=False,
                        session_name=session_name
                    )
                    st.success("✅ Interactive Code Chat initialized")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to initialize: {e}")
                    return
    
    if st.session_state.code_chat_instance:
        # Chat interface
        message = st.text_area(
            "Chat message:",
            height=100,
            placeholder="e.g., Create a visualization of random data"
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💬 Chat (No Code)") and message:
                with st.spinner("Processing..."):
                    try:
                        response = st.session_state.code_chat_instance.chat(message)
                        st.subheader("💭 Chat Response")
                        st.write(response)
                    except Exception as e:
                        st.error(f"Error: {e}")
        
        with col2:
            if st.button("💻 Chat with Code") and message:
                with st.spinner("Executing code..."):
                    try:
                        result = st.session_state.code_chat_instance.chat_with_code(message)
                        st.subheader("🔄 Code Execution Result")
                        st.json(result)
                    except Exception as e:
                        st.error(f"Error: {e}")
        
        with col3:
            if st.button("📊 Session Info"):
                try:
                    info = st.session_state.code_chat_instance.get_session_info()
                    st.subheader("📈 Session Information")
                    st.json(info)
                except Exception as e:
                    st.error(f"Error: {e}")

def feature_tests_tab():
    """Feature testing tab"""
    st.header("📊 Feature Tests")
    st.markdown("Test specific OrionAI Python features")
    
    # Feature categories
    feature_categories = {
        "Data Science": [
            "Create a pandas DataFrame with sample data",
            "Perform basic statistical analysis on data",
            "Create correlation matrix and heatmap"
        ],
        "Machine Learning": [
            "Train a simple classification model",
            "Perform clustering analysis", 
            "Create feature importance plot"
        ],
        "Visualization": [
            "Create multiple chart types",
            "Generate interactive plots",
            "Create a dashboard with subplots"
        ],
        "Web Operations": [
            "Fetch data from a public API",
            "Parse JSON data and analyze",
            "Create simple web scraping example"
        ],
        "Database": [
            "Create SQLite database and tables",
            "Insert and query data",
            "Generate database report"
        ]
    }
    
    selected_category = st.selectbox("Select Feature Category", list(feature_categories.keys()))
    
    if selected_category:
        st.subheader(f"🎯 {selected_category} Tests")
        
        for i, test in enumerate(feature_categories[selected_category]):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**{i+1}.** {test}")
            
            with col2:
                if st.button(f"Run Test {i+1}", key=f"test_{selected_category}_{i}"):
                    with st.spinner(f"Running {test}..."):
                        try:
                            result = st.session_state.ai_instance.ask(test)
                            st.success(f"✅ Test {i+1} completed")
                            with st.expander(f"View Result - Test {i+1}"):
                                st.write(result)
                        except Exception as e:
                            st.error(f"❌ Test {i+1} failed: {e}")

def examples_tab():
    """Examples and quick starts tab"""
    st.header("📈 Examples & Quick Starts")
    
    examples = {
        "Data Analysis Pipeline": """
# Complete data analysis example
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Create sample data
data = pd.DataFrame({
    'category': ['A', 'B', 'C'] * 10,
    'value': range(30),
    'score': [x*2 + 5 for x in range(30)]
})

# Analyze and visualize
summary = data.describe()
correlation = data.corr()

plt.figure(figsize=(12, 4))
plt.subplot(1, 3, 1)
sns.boxplot(data=data, x='category', y='value')
plt.subplot(1, 3, 2) 
sns.scatterplot(data=data, x='value', y='score')
plt.subplot(1, 3, 3)
sns.heatmap(correlation, annot=True)
plt.tight_layout()
plt.show()
        """,
        
        "Machine Learning Example": """
# Simple ML classification example
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

# Load data
iris = load_iris()
X, y = iris.data, iris.target

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
predictions = model.predict(X_test)
report = classification_report(y_test, predictions)
print(report)
        """,
        
        "Web Data Fetching": """
# Fetch and analyze web data
import requests
import pandas as pd

# Fetch data from API
response = requests.get('https://jsonplaceholder.typicode.com/posts')
data = response.json()

# Convert to DataFrame
df = pd.DataFrame(data)

# Analyze
print(f"Total posts: {len(df)}")
print(f"Unique users: {df['userId'].nunique()}")
print("\\nAverage title length by user:")
print(df.groupby('userId')['title'].apply(lambda x: x.str.len().mean()).head())
        """
    }
    
    selected_example = st.selectbox("Select Example", list(examples.keys()))
    
    if selected_example:
        st.subheader(f"📋 {selected_example}")
        st.code(examples[selected_example], language="python")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(f"🚀 Run {selected_example}"):
                with st.spinner(f"Executing {selected_example}..."):
                    try:
                        result = st.session_state.ai_instance.ask(f"Execute this code and show results: {examples[selected_example]}")
                        st.success("✅ Example executed successfully")
                        st.subheader("📊 Results")
                        st.write(result)
                    except Exception as e:
                        st.error(f"❌ Error executing example: {e}")
        
        with col2:
            if st.button(f"📖 Explain {selected_example}"):
                with st.spinner("Generating explanation..."):
                    try:
                        if st.session_state.chat_instance:
                            explanation = st.session_state.chat_instance.explain_code(examples[selected_example])
                            st.subheader("📝 Code Explanation")
                            st.markdown(explanation)
                        else:
                            st.warning("Initialize Python Chat first to get explanations")
                    except Exception as e:
                        st.error(f"Error: {e}")

def documentation_tab():
    """Documentation tab"""
    st.header("📚 Documentation")
    
    doc_sections = {
        "Quick Start": "docs/quickstart.md",
        "Features Overview": "docs/features.md", 
        "API Reference": "docs/api.md"
    }
    
    selected_doc = st.selectbox("Select Documentation", list(doc_sections.keys()))
    
    if selected_doc:
        try:
            doc_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), doc_sections[selected_doc])
            if os.path.exists(doc_path):
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                st.markdown(content)
            else:
                st.error(f"Documentation file not found: {doc_path}")
        except Exception as e:
            st.error(f"Error loading documentation: {e}")

if __name__ == "__main__":
    main_interface()
