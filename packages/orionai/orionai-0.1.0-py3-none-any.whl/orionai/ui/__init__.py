"""
OrionAI Python UI Module
Provides easy access to the Streamlit UI interface
"""

import subprocess
import sys
import os
import webbrowser
import time
import threading
from typing import Optional

def ui(port: int = 8501, auto_open: bool = True) -> None:
    """
    Launch the OrionAI Python Streamlit UI.
    
    Args:
        port (int): Port number for the Streamlit app (default: 8501)
        auto_open (bool): Whether to automatically open the browser (default: True)
    """
    
    # Get the path to the streamlit_ui.py file
    ui_file = os.path.join(os.path.dirname(__file__), "streamlit_ui.py")
    
    if not os.path.exists(ui_file):
        raise FileNotFoundError(f"UI file not found: {ui_file}")
    
    print("🚀 Starting OrionAI Python UI...")
    print(f"   Port: {port}")
    print(f"   UI File: {ui_file}")
    print("   Press Ctrl+C to stop the server")
    
    # Build the streamlit command
    cmd = [
        sys.executable, "-m", "streamlit", "run", 
        ui_file,
        "--server.port", str(port),
        "--server.headless", "true" if not auto_open else "false",
        "--theme.primaryColor", "#ff6b6b",
        "--theme.backgroundColor", "#ffffff", 
        "--theme.secondaryBackgroundColor", "#f0f2f6",
        "--theme.textColor", "#262730"
    ]
    
    def open_browser():
        """Open browser after a delay to allow server to start"""
        time.sleep(3)  # Wait for server to start
        if auto_open:
            url = f"http://localhost:{port}"
            print(f"🌐 Opening browser: {url}")
            webbrowser.open(url)
    
    # Start browser opening in background if requested
    if auto_open:
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
    
    try:
        # Run the streamlit app
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting Streamlit: {e}")
        raise
    except KeyboardInterrupt:
        print("\\n🛑 Stopping OrionAI Python UI...")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        raise

def check_streamlit_installed() -> bool:
    """
    Check if Streamlit is installed.
    
    Returns:
        bool: True if Streamlit is available, False otherwise
    """
    try:
        import streamlit
        return True
    except ImportError:
        return False

def install_streamlit() -> bool:
    """
    Install Streamlit if not available.
    
    Returns:
        bool: True if installation successful, False otherwise
    """
    try:
        print("📦 Installing Streamlit...")
        subprocess.run([sys.executable, "-m", "pip", "install", "streamlit"], 
                      check=True, capture_output=True)
        print("✅ Streamlit installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Streamlit: {e}")
        return False

def ensure_streamlit() -> bool:
    """
    Ensure Streamlit is available, install if necessary.
    
    Returns:
        bool: True if Streamlit is available, False if installation failed
    """
    if check_streamlit_installed():
        return True
    
    print("⚠️  Streamlit not found. Installing...")
    return install_streamlit()

# Auto-install Streamlit when module is imported
if not check_streamlit_installed():
    print("🔄 OrionAI Python UI requires Streamlit. Installing...")
    if not install_streamlit():
        print("❌ Failed to install Streamlit. UI functionality may not work.")

__all__ = ['ui', 'check_streamlit_installed', 'install_streamlit', 'ensure_streamlit']
