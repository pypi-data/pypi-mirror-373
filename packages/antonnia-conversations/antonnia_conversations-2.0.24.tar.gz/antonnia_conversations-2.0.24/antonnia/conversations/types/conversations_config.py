from typing import Literal, Union, Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel

ConfigKeys = Literal["session.autoclose.after_inactivity", "session.recovery.after_inactivity", "organization.working_hours"]

class SessionAutoCloseAfterInactivityConfig(BaseModel):
    type: Literal["session.autoclose.after_inactivity"]
    expires_in_minutes: int

class WorkingHoursConfig(BaseModel):
    type: Optional[Literal["organization.working_hours"]] = "organization.working_hours"
    timezone: str
    weekly_hours: Dict[str, List[Dict[str, str]]]  # {"mon": [{"start": "09:00", "end": "17:00"}]}
    overrides: Optional[List[Dict[str, Any]]] = []

Config = Union[
    SessionAutoCloseAfterInactivityConfig,
    WorkingHoursConfig
]

class ConversationsConfig(BaseModel):
  key: ConfigKeys
  organization_id: str
  config: Config
  created_at: datetime
  updated_at: datetime
    
    
    