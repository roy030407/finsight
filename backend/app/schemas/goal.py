from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class GoalCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    target_amount: float = Field(..., gt=0)
    current_amount: Optional[float] = Field(0, ge=0)
    icon: Optional[str] = Field(None, max_length=10)
    deadline: Optional[datetime] = None

class GoalUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    target_amount: Optional[float] = Field(None, gt=0)
    current_amount: Optional[float] = Field(None, ge=0)
    icon: Optional[str] = None
    deadline: Optional[datetime] = None

class GoalOut(BaseModel):
    id: str
    user_id: int
    title: str
    target_amount: float
    current_amount: float
    icon: Optional[str] = None
    deadline: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}