"""
Conversation type definitions for the Antonnia SDK.
"""

from typing import Optional, TypedDict
from pydantic import BaseModel
from datetime import datetime


class Conversation(BaseModel):
    """
    Represents a conversation between a contact and the channel_id.
    
    A conversation is a container for sessions and tracks the overall interaction
    between a contact and the organization across different channels. Each conversation
    has associated metadata and tracks the most recent activity.
    """
    
    id: str
    organization_id: str
    channel_id: str
    channel_user_id: str
    channel_type: str
    contact_id: str
    current_session_id: Optional[str] = None
    last_message_id: Optional[str] = None
    last_message_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ConversationUpdateFields(TypedDict, total=False):
    """
    Fields that can be updated in a conversation.
    """
    current_session_id: Optional[str]
    last_message_id: Optional[str]
    last_message_at: Optional[str]