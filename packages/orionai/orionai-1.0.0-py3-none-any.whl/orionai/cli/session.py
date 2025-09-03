"""
Session Manager for OrionAI CLI
===============================

Handles session creation, storage, and history management.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import pickle


@dataclass
class ChatMessage:
    """Represents a chat message."""
    timestamp: str
    role: str  # user, assistant, system
    content: str
    message_type: str = "text"  # text, code, error, image
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatMessage':
        return cls(**data)


@dataclass
class CodeExecution:
    """Represents a code execution result."""
    code: str
    output: str
    error: Optional[str] = None
    execution_time: float = 0.0
    files_created: List[str] = None
    
    def __post_init__(self):
        if self.files_created is None:
            self.files_created = []
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CodeExecution':
        return cls(**data)


@dataclass
class SessionData:
    """Session data structure."""
    session_id: str
    created_at: str
    updated_at: str
    title: str
    messages: List[ChatMessage]
    llm_provider: str
    llm_model: str
    total_messages: int = 0
    total_code_executions: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "title": self.title,
            "messages": [msg.to_dict() for msg in self.messages],
            "llm_provider": self.llm_provider,
            "llm_model": self.llm_model,
            "total_messages": self.total_messages,
            "total_code_executions": self.total_code_executions
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionData':
        messages = [ChatMessage.from_dict(msg) for msg in data.get("messages", [])]
        return cls(
            session_id=data["session_id"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            title=data["title"],
            messages=messages,
            llm_provider=data["llm_provider"],
            llm_model=data["llm_model"],
            total_messages=data.get("total_messages", len(messages)),
            total_code_executions=data.get("total_code_executions", 0)
        )


class SessionManager:
    """Manages chat sessions and history."""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.sessions_dir = config_manager.config_dir / "sessions"
        self.sessions_dir.mkdir(exist_ok=True)
        self.current_session: Optional[SessionData] = None
    
    def create_session(self, title: str = None, llm_provider: str = None, llm_model: str = None) -> str:
        """Create a new session."""
        session_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().isoformat()
        
        if not title:
            title = f"Session {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        if not llm_provider:
            llm_provider = self.config_manager.config.llm.provider
        
        if not llm_model:
            llm_model = self.config_manager.config.llm.model
        
        self.current_session = SessionData(
            session_id=session_id,
            created_at=timestamp,
            updated_at=timestamp,
            title=title,
            messages=[],
            llm_provider=llm_provider,
            llm_model=llm_model
        )
        
        self.save_session()
        return session_id
    
    def load_session(self, session_id: str) -> bool:
        """Load an existing session."""
        session_file = self.sessions_dir / session_id / "session.json"
        
        if not session_file.exists():
            return False
        
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.current_session = SessionData.from_dict(data)
            return True
        except Exception as e:
            print(f"Error loading session: {e}")
            return False
    
    def save_session(self):
        """Save current session to disk."""
        if not self.current_session:
            return
        
        session_dir = self.sessions_dir / self.current_session.session_id
        session_dir.mkdir(exist_ok=True)
        
        session_file = session_dir / "session.json"
        
        # Update timestamp
        self.current_session.updated_at = datetime.now().isoformat()
        
        try:
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_session.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving session: {e}")
    
    def add_message(self, role: str, content: str, message_type: str = "text", metadata: Dict[str, Any] = None):
        """Add a message to the current session."""
        if not self.current_session:
            return
        
        message = ChatMessage(
            timestamp=datetime.now().isoformat(),
            role=role,
            content=content,
            message_type=message_type,
            metadata=metadata or {}
        )
        
        self.current_session.messages.append(message)
        self.current_session.total_messages += 1
        
        # Auto-save if enabled
        if self.config_manager.config.session.auto_save:
            self.save_session()
    
    def add_code_execution(self, execution: CodeExecution):
        """Add code execution result to session."""
        if not self.current_session:
            return
        
        self.current_session.total_code_executions += 1
        
        # Store detailed execution data
        execution_file = (
            self.sessions_dir / 
            self.current_session.session_id / 
            f"execution_{self.current_session.total_code_executions}.json"
        )
        
        try:
            with open(execution_file, 'w', encoding='utf-8') as f:
                json.dump(execution.to_dict(), f, indent=2)
        except Exception as e:
            print(f"Error saving execution: {e}")
    
    def get_conversation_history(self, limit: int = None) -> List[ChatMessage]:
        """Get conversation history."""
        if not self.current_session:
            return []
        
        messages = self.current_session.messages
        if limit:
            messages = messages[-limit:]
        
        return messages
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all available sessions."""
        sessions = []
        
        for session_dir in self.sessions_dir.iterdir():
            if session_dir.is_dir():
                session_file = session_dir / "session.json"
                if session_file.exists():
                    try:
                        with open(session_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        sessions.append({
                            "session_id": data["session_id"],
                            "title": data["title"],
                            "created_at": data["created_at"],
                            "updated_at": data["updated_at"],
                            "total_messages": data.get("total_messages", 0),
                            "llm_provider": data["llm_provider"],
                            "llm_model": data["llm_model"]
                        })
                    except Exception:
                        continue
        
        # Sort by updated_at (most recent first)
        sessions.sort(key=lambda x: x["updated_at"], reverse=True)
        return sessions
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        import shutil
        
        session_dir = self.sessions_dir / session_id
        if session_dir.exists():
            try:
                shutil.rmtree(session_dir)
                return True
            except Exception as e:
                print(f"Error deleting session: {e}")
        
        return False
    
    def export_session(self, session_id: str, export_path: Path) -> bool:
        """Export session to a file."""
        session_file = self.sessions_dir / session_id / "session.json"
        
        if not session_file.exists():
            return False
        
        try:
            import shutil
            shutil.copy2(session_file, export_path)
            return True
        except Exception as e:
            print(f"Error exporting session: {e}")
            return False
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get current session statistics."""
        if not self.current_session:
            return {}
        
        return {
            "session_id": self.current_session.session_id,
            "title": self.current_session.title,
            "created_at": self.current_session.created_at,
            "total_messages": self.current_session.total_messages,
            "total_code_executions": self.current_session.total_code_executions,
            "llm_provider": self.current_session.llm_provider,
            "llm_model": self.current_session.llm_model
        }
