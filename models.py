from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict, Any, List
from enum import Enum

class ActionType(str, Enum):
    CATEGORIZE = "categorize"
    DRAFT_RESPONSE = "draft_response"
    ESCALATE = "escalate"
    MARK_SPAM = "mark_spam"
    REQUEST_INFO = "request_info"

class EmailData(BaseModel):
    email_id: str
    sender: str
    subject: str
    body: str
    urgency: Literal["low", "medium", "high"]
    category: Optional[str] = None
    requires_response: bool = True

class Observation(BaseModel):
    """Current observation of the environment"""
    current_email: EmailData
    email_queue: int = Field(description="Number of emails remaining in queue")
    inbox_size: int = Field(description="Total emails in inbox")
    time_step: int = Field(description="Current step number")
    previous_actions: List[str] = Field(default_factory=list)
    performance_metrics: Dict[str, float] = Field(default_factory=dict)

class Action(BaseModel):
    """Action the agent can take"""
    action_type: ActionType
    parameters: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True

class Reward(BaseModel):
    """Reward signal for the action"""
    score: float = Field(ge=0.0, le=1.0, description="Reward score between 0 and 1")
    breakdown: Dict[str, float] = Field(default_factory=dict)
    is_terminal: bool = False