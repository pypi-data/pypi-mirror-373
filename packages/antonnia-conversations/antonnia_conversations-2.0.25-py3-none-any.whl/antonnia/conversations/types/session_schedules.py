"""
Session schedule type definitions for the Antonnia SDK.
"""

from datetime import datetime
from typing import Literal, Optional, TypedDict, Union
from pydantic import BaseModel, Field

from .messages import MessageContent

# Session status literal type
SessionScheduleStatus = Literal["scheduled", "completed", "failed"]

class ScheduledMessageConfig(BaseModel):
    type: Literal["message"] = "message"
    message: MessageContent = Field(..., description="Message content")

class ScheduledNodeConfig(BaseModel):
    type: Literal["node"] = "node"
    node_id: str = Field(..., description="Node reference within agent")

class SessionSchedule(BaseModel):
    """
    Represents a scheduled message or node execution for a session.
    """
    id: str
    session_id: str
    organization_id: str
    scheduled_for: datetime = Field(..., description="When to send (UTC)")
    config: Union[ScheduledMessageConfig, ScheduledNodeConfig] = Field(..., discriminator='type')
    status: SessionScheduleStatus
    created_at: datetime

    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class SessionScheduleUpdateFields(TypedDict, total=False):
    """
    Fields that can be updated in a session schedule.
    """
    status: Optional[Literal["scheduled", "completed", "failed"]]
