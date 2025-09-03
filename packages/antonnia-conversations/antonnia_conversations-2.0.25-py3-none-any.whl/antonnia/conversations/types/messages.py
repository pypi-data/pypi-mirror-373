"""
Message type definitions for the Antonnia SDK.
"""

from datetime import datetime
from pydantic import BaseModel
from typing import Literal, Optional, Union

# Message role types
MessageRole = Literal["user", "assistant"]


class MessageContentText(BaseModel):
    """Text message content."""
    type: Literal["text"]
    text: str
    is_template: Optional[bool] = False


class MessageContentImage(BaseModel):
    """Image message content."""
    type: Literal["image"]
    url: str


class MessageContentAudio(BaseModel):
    """Audio message content."""
    type: Literal["audio"]
    url: str
    transcript: Optional[str] = None


class MessageContentFile(BaseModel):
    """File message content."""
    type: Literal["file"]
    url: str
    mime_type: str
    name: str


class MessageContentFunctionCall(BaseModel):
    """Function call message content."""
    type: Literal["function_call"]
    id: str
    name: str
    input: str


class MessageContentFunctionResult(BaseModel):
    """Function result message content."""
    type: Literal["function_result"]
    id: str
    name: str
    output: str


class MessageContentThought(BaseModel):
    """Thought message content (internal AI reasoning)."""
    type: Literal["thought"]
    thought: str


# Union type for all message content types
MessageContent = Union[
    MessageContentText,
    MessageContentImage,
    MessageContentAudio,
    MessageContentFile,
    MessageContentFunctionCall,
    MessageContentFunctionResult,
    MessageContentThought,
]


class Message(BaseModel):
    """
    Represents a message within a conversation session.
    
    Messages can contain different types of content (text, images, audio, etc.)
    and are associated with a specific role (user or assistant).
    """
    
    id: str
    session_id: str
    conversation_id: str
    organization_id: str
    provider_message_id: Optional[str] = None
    replied_provider_message_id: Optional[str] = None
    role: MessageRole
    content: MessageContent
    created_at: datetime
    
    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 