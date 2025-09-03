"""
Configuration Manager for OrionAI CLI
=====================================

Handles API keys, preferences, and settings storage.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Optional, Any
from dataclasses import dataclass, asdict
import getpass


@dataclass
class LLMConfig:
    """Configuration for LLM providers."""
    provider: str = "openai"  # openai, anthropic, google
    model: str = "gpt-3.5-turbo"
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2000


@dataclass
class SessionConfig:
    """Session configuration."""
    auto_save: bool = True
    save_interval: int = 300  # seconds
    max_history: int = 100
    enable_code_execution: bool = True
    image_folder: str = "images"
    reports_folder: str = "reports"


@dataclass
class OrionAIConfig:
    """Main OrionAI configuration."""
    llm: LLMConfig
    session: SessionConfig
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OrionAIConfig':
        return cls(
            llm=LLMConfig(**data.get('llm', {})),
            session=SessionConfig(**data.get('session', {}))
        )


class ConfigManager:
    """Manages OrionAI configuration and settings."""
    
    def __init__(self):
        self.home_dir = Path.home()
        self.config_dir = self.home_dir / ".orionai"
        self.config_file = self.config_dir / "config.yaml"
        self.ensure_config_dir()
        self.config = self.load_config()
    
    def ensure_config_dir(self):
        """Ensure configuration directory exists."""
        self.config_dir.mkdir(exist_ok=True)
        (self.config_dir / "sessions").mkdir(exist_ok=True)
        (self.config_dir / "logs").mkdir(exist_ok=True)
    
    def load_config(self) -> OrionAIConfig:
        """Load configuration from file or create default."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    data = yaml.safe_load(f)
                return OrionAIConfig.from_dict(data)
            except Exception as e:
                print(f"Error loading config: {e}. Using defaults.")
        
        return OrionAIConfig(
            llm=LLMConfig(),
            session=SessionConfig()
        )
    
    def save_config(self):
        """Save current configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(self.config.to_dict(), f, default_flow_style=False)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def setup_llm_provider(self, provider: str = None) -> bool:
        """Interactive setup for LLM provider."""
        from rich.console import Console
        from rich.prompt import Prompt, Confirm
        from rich.panel import Panel
        
        console = Console()
        
        # Show available providers
        providers = {
            "1": ("openai", "OpenAI (GPT-3.5/GPT-4)"),
            "2": ("anthropic", "Anthropic (Claude)"),
            "3": ("google", "Google (Gemini)")
        }
        
        if not provider:
            console.print(Panel.fit("🤖 LLM Provider Setup", style="bold blue"))
            console.print("Available providers:")
            for key, (name, desc) in providers.items():
                console.print(f"  {key}. {desc}")
            
            choice = Prompt.ask("Select provider", choices=list(providers.keys()), default="1")
            provider = providers[choice][0]
        
        self.config.llm.provider = provider
        
        # Get API key
        console.print(f"\n🔑 Setting up {provider.upper()} API key")
        
        # Check environment variable first
        env_key = f"{provider.upper()}_API_KEY"
        if env_key in os.environ:
            use_env = Confirm.ask(f"Use {env_key} environment variable?", default=True)
            if use_env:
                self.config.llm.api_key = os.environ[env_key]
                console.print("✅ Using environment variable")
            else:
                api_key = Prompt.ask("Enter API key", password=True)
                self.config.llm.api_key = api_key
        else:
            api_key = Prompt.ask("Enter API key", password=True)
            self.config.llm.api_key = api_key
        
        # Set default model based on provider
        models = {
            "openai": "gpt-3.5-turbo",
            "anthropic": "claude-3-sonnet-20240229",
            "google": "gemini-1.5-pro"
        }
        
        self.config.llm.model = models.get(provider, "gpt-3.5-turbo")
        
        # Ask for custom model
        custom_model = Prompt.ask(
            f"Model name (default: {self.config.llm.model})", 
            default=self.config.llm.model
        )
        self.config.llm.model = custom_model
        
        self.save_config()
        console.print("✅ LLM provider configured successfully!")
        return True
    
    def get_api_key(self, provider: str = None) -> Optional[str]:
        """Get API key for specified provider."""
        if provider is None:
            provider = self.config.llm.provider
        
        # Try config first
        if self.config.llm.api_key:
            return self.config.llm.api_key
        
        # Try environment variable
        env_key = f"{provider.upper()}_API_KEY"
        return os.environ.get(env_key)
    
    def update_llm_settings(self, **kwargs):
        """Update LLM settings."""
        for key, value in kwargs.items():
            if hasattr(self.config.llm, key):
                setattr(self.config.llm, key, value)
        self.save_config()
    
    def get_session_dir(self, session_id: str) -> Path:
        """Get session directory path."""
        session_dir = self.config_dir / "sessions" / session_id
        session_dir.mkdir(exist_ok=True)
        return session_dir
    
    def get_image_dir(self, session_id: str) -> Path:
        """Get images directory for session."""
        image_dir = self.get_session_dir(session_id) / self.config.session.image_folder
        image_dir.mkdir(exist_ok=True)
        return image_dir
    
    def get_reports_dir(self, session_id: str) -> Path:
        """Get reports directory for session."""
        reports_dir = self.get_session_dir(session_id) / self.config.session.reports_folder
        reports_dir.mkdir(exist_ok=True)
        return reports_dir
