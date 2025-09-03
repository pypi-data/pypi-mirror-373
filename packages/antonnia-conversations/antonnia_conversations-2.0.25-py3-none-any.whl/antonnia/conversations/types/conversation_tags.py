"""
Conversation tag type definitions for the Antonnia SDK.
"""

from datetime import datetime
from pydantic import BaseModel


class ConversationTag(BaseModel):
    """
    Represents the association between a conversation and a tag.
    
    ConversationTags are used to categorize and organize conversations
    by linking them to specific tags. This allows for filtering and
    grouping conversations based on their tags.
    """
    
    conversation_id: str
    tag_id: str
    created_at: datetime
    
    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
