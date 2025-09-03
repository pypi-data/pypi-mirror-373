"""
Survey answer type definitions for the Antonnia SDK.
"""

from datetime import datetime
from typing import Optional, TypedDict
from pydantic import BaseModel
from .survey_questions import QuestionType

# Define valid answer types that mirror question types
AnswerType = QuestionType


class SurveyAnswer(BaseModel):
    """
    Represents an answer to a survey question.
    
    Answers are submitted as part of a survey submission and contain
    the user's response to a specific question. The answer format
    depends on the question type.
    """
    
    id: str
    submission_id: str
    question_id: str
    type: AnswerType
    answer: str  # Contains the answer as a string, structured based on type
    submitted_at: datetime
    
    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SurveyAnswerUpdateFields(TypedDict, total=False):
    """
    Fields that can be updated in a survey answer.
    """
    answer: Optional[str]