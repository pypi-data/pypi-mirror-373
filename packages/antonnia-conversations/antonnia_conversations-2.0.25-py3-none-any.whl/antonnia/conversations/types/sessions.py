"""
Session type definitions for the Antonnia SDK.
"""

from datetime import datetime
from typing import Any, Dict, Literal, Optional, TypedDict
from pydantic import BaseModel

from .agents import Agent

# Session status literal type
SessionStatus = Literal["open", "closed"]


class Session(BaseModel):
    """
    Represents a conversation session between a contact and an agent.
    
    A session contains messages and tracks the state of an ongoing conversation.
    Sessions can be transferred between different agents and have associated metadata.
    """
    
    id: str
    contact_id: str
    organization_id: str
    thread_id: Optional[str] = None
    conversation_id: str
    status: SessionStatus
    agent: Optional[Agent] = None
    ending_survey_submission_id: Optional[str] = None
    metadata: Dict[str, Any] = {}
    created_at: datetime
    
    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 


class SessionUpdateFields(TypedDict, total=False):
    """
    Fields that can be updated in a session.
    """
    thread_id: Optional[str]
    status: Optional[SessionStatus]
    agent_id: Optional[str]
    ending_survey_submission_id: Optional[str]
    metadata: Optional[Dict[str, Any]]
    organization_id: Optional[str]
