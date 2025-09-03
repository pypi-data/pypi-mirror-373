"""
Main CLI Interface for OrionAI
==============================

Rich CLI interface with session management and LLM selection.
"""

import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.text import Text
from rich.align import Align
from rich.layout import Layout
from rich.live import Live
import rich.box

from .config import ConfigManager
from .session import SessionManager
from .chat import InteractiveChatSession


def create_header() -> Panel:
    """Create the header panel."""
    header_text = Text()
    header_text.append("🚀 ", style="bold yellow")
    header_text.append("OrionAI", style="bold blue")
    header_text.append(" - Interactive LLM Chat with Code Execution", style="bold white")
    
    return Panel(
        Align.center(header_text),
        box=rich.box.DOUBLE,
        style="blue"
    )


def show_llm_selection(config_manager: ConfigManager) -> bool:
    """Show LLM provider selection interface."""
    console = Console()
    
    # Create provider table
    table = Table(title="🤖 Available LLM Providers", box=rich.box.ROUNDED)
    table.add_column("Option", style="cyan", width=8)
    table.add_column("Provider", style="green", width=15)
    table.add_column("Description", style="white")
    table.add_column("Status", style="yellow", width=10)
    
    providers = [
        ("1", "OpenAI", "GPT-3.5, GPT-4 models", "✅ Available"),
        ("2", "Anthropic", "Claude models", "✅ Available"),
        ("3", "Google", "Gemini models", "✅ Available"),
    ]
    
    for option, provider, desc, status in providers:
        table.add_row(option, provider, desc, status)
    
    console.print(table)
    
    # Current configuration
    current = config_manager.config.llm
    if current.provider and current.model:
        console.print(f"\n📋 Current: {current.provider} ({current.model})")
    
    # Get user choice
    choice = Prompt.ask(
        "\nSelect provider or press Enter to use current",
        choices=["1", "2", "3", ""], 
        default=""
    )
    
    if choice:
        provider_map = {"1": "openai", "2": "anthropic", "3": "google"}
        provider = provider_map[choice]
        
        # Setup the provider
        return config_manager.setup_llm_provider(provider)
    
    # Check if current config is valid
    if not current.provider or not config_manager.get_api_key():
        console.print("❌ No valid LLM configuration found.", style="red")
        setup = Confirm.ask("Setup LLM provider now?")
        if setup:
            return config_manager.setup_llm_provider()
        return False
    
    return True


def show_session_selection(session_manager: SessionManager, console: Console) -> Optional[str]:
    """Show session selection interface."""
    sessions = session_manager.list_sessions()
    
    # Create sessions table
    table = Table(title="📝 Available Sessions", box=rich.box.ROUNDED)
    table.add_column("Option", style="cyan", width=8)
    table.add_column("Session ID", style="green", width=12)
    table.add_column("Title", style="white", width=30)
    table.add_column("Messages", style="yellow", width=10)
    table.add_column("Updated", style="blue")
    
    # Add new session option
    table.add_row("0", "NEW", "Create New Session", "-", "-")
    
    # Add existing sessions
    for i, session in enumerate(sessions[:9], 1):  # Limit to 9 sessions
        updated = session["updated_at"][:16].replace("T", " ")
        table.add_row(
            str(i),
            session["session_id"],
            session["title"][:30],
            str(session["total_messages"]),
            updated
        )
    
    console.print(table)
    
    if not sessions:
        console.print("ℹ️  No existing sessions found. Creating new session...", style="blue")
        return None
    
    # Get user choice
    max_choice = min(len(sessions), 9)
    choice = IntPrompt.ask(
        f"Select session (0 for new, 1-{max_choice})",
        default=0
    )
    
    if choice == 0:
        return None
    elif 1 <= choice <= len(sessions):
        return sessions[choice - 1]["session_id"]
    else:
        console.print("❌ Invalid choice", style="red")
        return show_session_selection(session_manager, console)


def create_new_session(session_manager: SessionManager, config_manager: ConfigManager, auto_start_chat: bool = False) -> bool:
    """Create a new session interactively."""
    console = Console()
    
    console.print(Panel.fit("📝 Create New Session", style="bold green"))
    
    # Get session title
    title = Prompt.ask("Session title", default=f"Session {session_manager.sessions_dir.name}")
    
    # Confirm LLM settings
    llm_config = config_manager.config.llm
    console.print(f"🤖 Using: {llm_config.provider} ({llm_config.model})")
    
    change_llm = Confirm.ask("Change LLM settings?", default=False)
    if change_llm:
        show_llm_selection(config_manager)
    
    # Create session
    session_id = session_manager.create_session(
        title=title,
        llm_provider=config_manager.config.llm.provider,
        llm_model=config_manager.config.llm.model
    )
    
    console.print(f"✅ Created session: {session_id}", style="green")
    
    # Ask if user wants to start chatting immediately
    if auto_start_chat or Confirm.ask("🚀 Start chatting now?", default=True):
        console.clear()
        chat_session = InteractiveChatSession(config_manager, session_manager)
        chat_session.run()
        return True
    
    return True


def show_main_menu(config_manager: ConfigManager, session_manager: SessionManager):
    """Show the main menu and handle user choices."""
    console = Console()
    
    while True:
        console.clear()
        console.print(create_header())
        
        # Show current status
        status_text = Text()
        
        # LLM Status
        llm_config = config_manager.config.llm
        if llm_config.provider and config_manager.get_api_key():
            status_text.append("🤖 LLM: ", style="bold")
            status_text.append(f"{llm_config.provider} ({llm_config.model})", style="green")
        else:
            status_text.append("🤖 LLM: ", style="bold")
            status_text.append("Not configured", style="red")
        
        status_text.append(" | ")
        
        # Session Status
        if session_manager.current_session:
            status_text.append("📝 Session: ", style="bold")
            status_text.append(session_manager.current_session.session_id, style="green")
        else:
            status_text.append("📝 Session: ", style="bold")
            status_text.append("None", style="yellow")
        
        console.print(Panel(Align.center(status_text), style="blue"))
        
        # Menu options
        menu_table = Table(box=rich.box.ROUNDED, show_header=False)
        menu_table.add_column("Option", style="cyan", width=8)
        menu_table.add_column("Description", style="white")
        
        menu_options = [
            ("1", "🚀 Start Interactive Chat"),
            ("2", "📝 Manage Sessions"),
            ("3", "🤖 Configure LLM Provider"),
            ("4", "⚙️  Settings"),
            ("5", "📊 Session Statistics"),
            ("0", "🚪 Exit"),
        ]
        
        for option, desc in menu_options:
            menu_table.add_row(option, desc)
        
        console.print(menu_table)
        
        choice = Prompt.ask("Select option", choices=["0", "1", "2", "3", "4", "5"], default="1")
        
        if choice == "0":
            console.print("👋 Goodbye!", style="yellow")
            sys.exit(0)
        
        elif choice == "1":
            # Start interactive chat
            if not config_manager.get_api_key():
                console.print("❌ No LLM configured. Please configure first.", style="red")
                input("Press Enter to continue...")
                continue
            
            if not session_manager.current_session:
                console.print("📝 No active session. Please select or create one.")
                session_id = show_session_selection(session_manager, console)
                
                if session_id:
                    if not session_manager.load_session(session_id):
                        console.print("❌ Failed to load session", style="red")
                        input("Press Enter to continue...")
                        continue
                else:
                    # Create new session with auto-start chat option
                    create_new_session(session_manager, config_manager, auto_start_chat=True)
                    # After creating and potentially chatting, continue to main menu
                    continue
            
            # Start chat
            console.clear()
            chat_session = InteractiveChatSession(config_manager, session_manager)
            chat_session.run()
        
        elif choice == "2":
            # Manage sessions
            handle_session_management(session_manager, config_manager, console)
        
        elif choice == "3":
            # Configure LLM
            show_llm_selection(config_manager)
            input("Press Enter to continue...")
        
        elif choice == "4":
            # Settings
            handle_settings(config_manager, console)
        
        elif choice == "5":
            # Statistics
            show_session_statistics(session_manager, console)


def handle_session_management(session_manager: SessionManager, config_manager: ConfigManager, console: Console):
    """Handle session management operations."""
    while True:
        console.clear()
        console.print(Panel.fit("📝 Session Management", style="bold blue"))
        
        # Show current session
        if session_manager.current_session:
            current_info = f"Current: {session_manager.current_session.session_id} - {session_manager.current_session.title}"
            console.print(Panel(current_info, style="green"))
        
        # Menu
        session_menu = Table(box=rich.box.ROUNDED, show_header=False)
        session_menu.add_column("Option", style="cyan", width=8)
        session_menu.add_column("Description", style="white")
        
        options = [
            ("1", "📝 Create New Session"),
            ("2", "📂 Load Existing Session"),
            ("3", "� Start Chat with Current Session") if session_manager.current_session else None,
            ("4", "�🗑️  Delete Session"),
            ("5", "📤 Export Session"),
            ("6", "📋 List All Sessions"),
            ("0", "🔙 Back to Main Menu"),
        ]
        
        # Filter out None options
        options = [(opt, desc) for opt, desc in options if desc is not None]
        
        for option, desc in options:
            session_menu.add_row(option, desc)
        
        console.print(session_menu)
        
        # Build valid choices based on available options
        valid_choices = [opt for opt, _ in options]
        choice = Prompt.ask("Select option", choices=valid_choices, default="0")
        
        if choice == "0":
            break
        elif choice == "1":
            create_new_session(session_manager, config_manager)
        elif choice == "2":
            session_id = show_session_selection(session_manager, console)
            if session_id and session_manager.load_session(session_id):
                console.print(f"✅ Loaded session: {session_id}", style="green")
                
                # Ask if user wants to start chatting immediately
                if Confirm.ask("🚀 Start chatting now?", default=True):
                    console.clear()
                    chat_session = InteractiveChatSession(config_manager, session_manager)
                    chat_session.run()
                    # After chat ends, break out of session management to main menu
                    break
            elif session_id:
                console.print("❌ Failed to load session", style="red")
        elif choice == "3" and session_manager.current_session:
            # Start chat with current session
            console.clear()
            chat_session = InteractiveChatSession(config_manager, session_manager)
            chat_session.run()
            break
        elif choice == "4":
            # Delete session
            sessions = session_manager.list_sessions()
            if not sessions:
                console.print("ℹ️  No sessions to delete", style="blue")
            else:
                console.print("🗑️  Select session to delete:")
                session_id = show_session_selection(session_manager, console)
                if session_id:
                    confirm = Confirm.ask(f"Delete session {session_id}? This cannot be undone!")
                    if confirm and session_manager.delete_session(session_id):
                        console.print("✅ Session deleted", style="green")
                        if session_manager.current_session and session_manager.current_session.session_id == session_id:
                            session_manager.current_session = None
        elif choice == "5":
            # Export session
            sessions = session_manager.list_sessions()
            if not sessions:
                console.print("ℹ️  No sessions to export", style="blue")
            else:
                session_id = show_session_selection(session_manager, console)
                if session_id:
                    export_path = Path(Prompt.ask("Export path", default=f"session_{session_id}.json"))
                    if session_manager.export_session(session_id, export_path):
                        console.print(f"✅ Session exported to {export_path}", style="green")
        elif choice == "6":
            # List sessions
            sessions = session_manager.list_sessions()
            if sessions:
                show_session_selection(session_manager, console)
            else:
                console.print("ℹ️  No sessions found", style="blue")
        
        if choice != "0":
            input("Press Enter to continue...")


def handle_settings(config_manager: ConfigManager, console: Console):
    """Handle settings configuration."""
    console.clear()
    console.print(Panel.fit("⚙️  Settings", style="bold blue"))
    
    # Show current settings
    config = config_manager.config
    
    settings_table = Table(title="Current Settings", box=rich.box.ROUNDED)
    settings_table.add_column("Setting", style="cyan")
    settings_table.add_column("Value", style="white")
    
    settings_table.add_row("LLM Provider", config.llm.provider)
    settings_table.add_row("LLM Model", config.llm.model)
    settings_table.add_row("Temperature", str(config.llm.temperature))
    settings_table.add_row("Max Tokens", str(config.llm.max_tokens))
    settings_table.add_row("Auto Save", str(config.session.auto_save))
    settings_table.add_row("Code Execution", str(config.session.enable_code_execution))
    settings_table.add_row("Max History", str(config.session.max_history))
    
    console.print(settings_table)
    
    # Settings menu
    if Confirm.ask("Modify settings?"):
        # Temperature
        new_temp = Prompt.ask(f"Temperature (current: {config.llm.temperature})", default=str(config.llm.temperature))
        try:
            config.llm.temperature = float(new_temp)
        except ValueError:
            pass
        
        # Max tokens
        new_tokens = Prompt.ask(f"Max tokens (current: {config.llm.max_tokens})", default=str(config.llm.max_tokens))
        try:
            config.llm.max_tokens = int(new_tokens)
        except ValueError:
            pass
        
        # Auto save
        config.session.auto_save = Confirm.ask(f"Auto save (current: {config.session.auto_save})", default=config.session.auto_save)
        
        # Code execution
        config.session.enable_code_execution = Confirm.ask(f"Enable code execution (current: {config.session.enable_code_execution})", default=config.session.enable_code_execution)
        
        config_manager.save_config()
        console.print("✅ Settings saved!", style="green")
    
    input("Press Enter to continue...")


def show_session_statistics(session_manager: SessionManager, console: Console):
    """Show session statistics."""
    console.clear()
    console.print(Panel.fit("📊 Session Statistics", style="bold blue"))
    
    sessions = session_manager.list_sessions()
    
    if not sessions:
        console.print("ℹ️  No sessions found", style="blue")
        input("Press Enter to continue...")
        return
    
    # Overall statistics
    total_sessions = len(sessions)
    total_messages = sum(s["total_messages"] for s in sessions)
    
    providers = {}
    for session in sessions:
        provider = session["llm_provider"]
        providers[provider] = providers.get(provider, 0) + 1
    
    # Statistics table
    stats_table = Table(title="Overall Statistics", box=rich.box.ROUNDED)
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Value", style="white")
    
    stats_table.add_row("Total Sessions", str(total_sessions))
    stats_table.add_row("Total Messages", str(total_messages))
    stats_table.add_row("Avg Messages/Session", f"{total_messages/total_sessions:.1f}" if total_sessions > 0 else "0")
    
    for provider, count in providers.items():
        stats_table.add_row(f"Sessions ({provider})", str(count))
    
    console.print(stats_table)
    
    # Recent sessions
    recent_table = Table(title="Recent Sessions", box=rich.box.ROUNDED)
    recent_table.add_column("ID", style="green")
    recent_table.add_column("Title", style="white")
    recent_table.add_column("Messages", style="yellow")
    recent_table.add_column("Provider", style="cyan")
    recent_table.add_column("Updated", style="blue")
    
    for session in sessions[:5]:  # Show last 5 sessions
        updated = session["updated_at"][:16].replace("T", " ")
        recent_table.add_row(
            session["session_id"],
            session["title"][:30],
            str(session["total_messages"]),
            session["llm_provider"],
            updated
        )
    
    console.print(recent_table)
    input("Press Enter to continue...")


def main_cli():
    """Main CLI entry point."""
    try:
        console = Console()
        
        # Initialize managers
        config_manager = ConfigManager()
        session_manager = SessionManager(config_manager)
        
        # Check if this is first run
        if not config_manager.config_file.exists():
            console.print(Panel.fit(
                "🎉 Welcome to OrionAI!\n"
                "This appears to be your first time running OrionAI.\n"
                "Let's set up your LLM provider.",
                style="bold green"
            ))
            
            if not show_llm_selection(config_manager):
                console.print("❌ Setup cancelled. Exiting.", style="red")
                return
        
        # Show main menu
        show_main_menu(config_manager, session_manager)
        
    except KeyboardInterrupt:
        console.print("\n👋 Goodbye!", style="yellow")
    except Exception as e:
        console.print(f"❌ Unexpected error: {e}", style="red")
        console.print_exception()


if __name__ == "__main__":
    main_cli()
