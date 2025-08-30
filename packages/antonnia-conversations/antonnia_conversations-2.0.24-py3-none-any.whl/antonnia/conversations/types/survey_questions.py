"""
Survey question type definitions for the Antonnia SDK.
"""

from typing import Annotated, List, Optional, Union, Literal, TypedDict
from pydantic import BaseModel, Discriminator, Tag, field_validator

# Define valid question types
QuestionType = Literal["boolean", "options", "open_ended"]


class QuestionOptionItem(BaseModel):
    """
    Represents an option in a multiple choice question.
    
    Each option has a label and can optionally navigate to a specific
    next question based on the user's selection.
    """
    
    label: str
    next_question_id: Optional[str] = None


class BooleanQuestionConfig(BaseModel):
    """
    Configuration for boolean (yes/no) questions.
    
    Defines what questions to navigate to based on true/false answers.
    """
    
    type: Literal["boolean"] = "boolean"
    true: str  # UUID of the next question if answered true
    false: str  # UUID of the next question if answered false


class OptionsQuestionConfig(BaseModel):
    """
    Configuration for multiple choice questions.
    
    Contains a list of options that the user can select from.
    """
    
    type: Literal["options"] = "options"
    options: List[QuestionOptionItem]


class OpenEndedQuestionConfig(BaseModel):
    """
    Configuration for open-ended text questions.
    
    Allows users to provide free-form text responses.
    """
    
    type: Literal["open_ended"] = "open_ended"
    next_question_id: Optional[str] = None


def get_question_type(v) -> str:
    """
    Discriminator function to determine question type from config.
    
    Args:
        v: The configuration object (dict or model instance)
        
    Returns:
        str: The question type
        
    Raises:
        ValueError: If question type cannot be determined
    """
    # Handle both dictionary inputs and model instances
    if isinstance(v, dict):
        question_type = v.get('type')
    else:
        # Handle model instance
        question_type = getattr(v, 'type', None)
        
    if not question_type:
        raise ValueError(f"Question type not found in {v}")
    return str(question_type)


# Union type for all question configurations
SurveyQuestionConfig = Annotated[
    (
        Annotated[BooleanQuestionConfig, Tag('boolean')] |
        Annotated[OptionsQuestionConfig, Tag('options')] |
        Annotated[OpenEndedQuestionConfig, Tag('open_ended')]
    ),
    Discriminator(get_question_type),
]


class SurveyQuestion(BaseModel):
    """
    Represents a question within a survey.
    
    Questions have different types (boolean, options, open-ended) and
    corresponding configurations that define their behavior and navigation.
    """
    
    id: str
    message: str
    type: QuestionType
    config: SurveyQuestionConfig
    
    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            # Custom encoders if needed
        }


class SurveyQuestionUpdateFields(TypedDict, total=False):
    """
    Fields that can be updated in a survey question.
    """
    message: Optional[str]
    config: Optional[SurveyQuestionConfig]
    