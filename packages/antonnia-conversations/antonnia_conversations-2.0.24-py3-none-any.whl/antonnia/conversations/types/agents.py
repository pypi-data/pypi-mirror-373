"""
Agent type definitions for the Antonnia SDK.
"""

from typing import Annotated, Any, Dict, Literal, Union, Optional
from pydantic import BaseModel, Discriminator, Tag
from datetime import datetime


class HumanAgent(BaseModel):
    """Represents a human agent in the conversation system."""
    
    id: str
    organization_id: str
    name: str
    type: Literal["human"]
    profile_id: str
    created_at: datetime


class AIAgent(BaseModel):
    """Represents an AI agent in the conversation system."""
    
    id: str
    organization_id: str
    name: str
    type: Literal["ai"]
    assistant_id: str
    created_at: datetime


def _get_agent_type(v: Union[Dict[str, Any], "Agent"]) -> str:
    """Discriminator function to determine agent type."""
    if isinstance(v, dict):
        agent_type = v.get('type')
    else:
        agent_type = getattr(v, 'type', None)
        
    if not agent_type:
        raise ValueError(f"Agent type not found in {v}")
    return str(agent_type)


Agent = Annotated[
    Union[
        Annotated[HumanAgent, Tag('human')],
        Annotated[AIAgent, Tag('ai')]
    ],
    Discriminator(_get_agent_type),
]


class AgentUpdateFields(BaseModel):
    """Fields that can be updated for an agent."""
    
    name: Optional[str] = None
    assistant_id: Optional[str] = None
    profile_id: Optional[str] = None
