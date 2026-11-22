from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import TaskStatus


class TaskCreate(BaseModel):
    github_issue_id: int = Field(gt=0)
    title: str = Field(min_length=1, max_length=500)


class TaskUpdate(BaseModel):
    status: TaskStatus | None = None
    result: str | None = None


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    github_issue_id: int
    title: str
    status: TaskStatus
    result: str | None
    created_at: datetime
    updated_at: datetime
