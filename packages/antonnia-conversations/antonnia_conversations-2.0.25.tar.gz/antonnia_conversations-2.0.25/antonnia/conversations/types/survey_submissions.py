"""
Survey submission type definitions for the Antonnia SDK.
"""

from typing import Literal, Optional, TypedDict
from datetime import datetime
from pydantic import BaseModel
import pytz

# Survey submission status literal type
SurveySubmissionStatus = Literal["pending", "finished"]


class SurveySubmission(BaseModel):
    """
    Represents a submission of a survey by a contact.
    
    Survey submissions track the progress and completion of surveys.
    They have expiration times and can be associated with conversations
    and sessions for context.
    """
    
    id: str
    survey_id: str
    status: SurveySubmissionStatus
    created_at: datetime
    expires_at: datetime
    finished_at: Optional[datetime] = None
    organization_id: str
    session_id: str
    
    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    @property
    def is_active(self) -> bool:
        """
        Check if the survey submission is still active and can receive answers.
        
        Returns:
            bool: True if the submission is pending and not expired
        """
        return self.status == "pending" and self.expires_at > datetime.now(pytz.utc)


class SurveySubmissionUpdateFields(TypedDict, total=False):
    """
    Fields that can be updated in a survey submission.
    """
    status: Optional[SurveySubmissionStatus]
    finished_at: Optional[datetime]
