"""
Survey type definitions for the Antonnia SDK.
"""

from typing import List, Optional, TypedDict
from datetime import datetime
from pydantic import BaseModel

class Survey(BaseModel):
    """
    Represents a survey that can be presented to contacts.
    
    Surveys are used to collect feedback and information from contacts during
    or after conversations. They contain a sequence of questions that can be
    linked together to create a survey flow.
    """
    
    id: str
    organization_id: str
    created_at: datetime
    title: str
    first_question_id: Optional[str] = None
    
    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SurveyUpdateFields(TypedDict, total=False):
    """
    Fields that can be updated in a survey.
    """
    title: Optional[str]
    first_question_id: Optional[str]
