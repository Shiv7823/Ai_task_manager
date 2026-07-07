from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.task import PriorityEnum, StatusEnum

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200, example="Implement user authentication module")
    description: Optional[str] = Field(None, example="Build JWT-based auth with refresh tokens")
    priority: Optional[PriorityEnum] = PriorityEnum.medium
    status: Optional[StatusEnum] = StatusEnum.todo
    deadline: Optional[datetime] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    priority: Optional[PriorityEnum] = None
    status: Optional[StatusEnum] = None
    deadline: Optional[datetime] = None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    priority: PriorityEnum
    status: StatusEnum
    deadline: Optional[datetime]
    ai_summary: Optional[str]
    ai_priority_reason: Optional[str]
    ai_enriched: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TaskListResponse(BaseModel):
    total: int
    tasks: list[TaskResponse]
