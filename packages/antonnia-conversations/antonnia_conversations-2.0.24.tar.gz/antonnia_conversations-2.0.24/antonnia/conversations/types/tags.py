"""
Tag type definitions for the Antonnia SDK.
"""

from datetime import datetime
from typing import Literal, Optional, TypedDict
from pydantic import BaseModel

# shadcn colors from their default theme - used for tag visualization
TagColor = Literal[
    "slate",    # Gray
    "red",      # Error/Destructive
    "orange",   # Warning
    "green",    # Success
    "blue",     # Primary
    "yellow",   # Warning alternative
    "purple",   # Secondary
    "pink",     # Accent
]


class Tag(BaseModel):
    """
    Represents a tag that can be applied to conversations or other entities.
    
    Tags are used for organizing and categorizing conversations within an organization.
    Each tag has a name, color, and belongs to a specific organization.
    """
    
    id: str
    organization_id: str
    name: str
    color: TagColor
    created_at: datetime
    
    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TagUpdateFields(TypedDict, total=False):
    """
    Fields that can be updated in a tag.
    """
    name: Optional[str]
    color: Optional[TagColor]
