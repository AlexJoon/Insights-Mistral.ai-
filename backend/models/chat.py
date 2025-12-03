"""
Data models for chat functionality.
Clean separation of data structures from business logic.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Literal
from datetime import datetime
import uuid


MessageRole = Literal["user", "assistant", "system"]


@dataclass
class Message:
    """Represents a single message in a conversation."""
    role: MessageRole
    content: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self):
        """Convert message to dictionary format."""
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }

    def to_api_format(self):
        """Convert to format expected by Mistral API."""
        return {
            "role": self.role,
            "content": self.content
        }


@dataclass
class Conversation:
    """Represents a conversation with multiple messages."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = "New Conversation"
    messages: List[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def add_message(self, role: MessageRole, content: str) -> Message:
        """Add a new message to the conversation."""
        message = Message(role=role, content=content)
        self.messages.append(message)
        self.updated_at = datetime.utcnow()
        return message

    def get_messages_for_api(self) -> List[dict]:
        """Get messages in format for Mistral API."""
        return [msg.to_api_format() for msg in self.messages]

    def to_dict(self):
        """Convert conversation to dictionary format."""
        return {
            "id": self.id,
            "title": self.title,
            "messages": [msg.to_dict() for msg in self.messages],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


@dataclass
class ChatRequest:
    """Request model for chat endpoint."""
    conversation_id: Optional[str] = None
    message: str = ""
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None

    @classmethod
    def from_dict(cls, data: dict) -> "ChatRequest":
        """Create ChatRequest from dictionary."""
        return cls(
            conversation_id=data.get("conversation_id"),
            message=data.get("message", ""),
            model=data.get("model"),
            temperature=data.get("temperature"),
            max_tokens=data.get("max_tokens")
        )


@dataclass
class StreamChunk:
    """Represents a chunk of streamed response."""
    content: str
    is_final: bool = False
    conversation_id: Optional[str] = None
    message_id: Optional[str] = None

    def to_sse_format(self) -> str:
        """Convert to SSE format."""
        import json
        data = {
            "content": self.content,
            "is_final": self.is_final,
            "conversation_id": self.conversation_id,
            "message_id": self.message_id
        }
        return f"data: {json.dumps(data)}\n\n"
