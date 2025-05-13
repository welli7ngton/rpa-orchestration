from pydantic import BaseModel, Field
from typing import Optional, Dict, Literal
from uuid import UUID, uuid4
from datetime import datetime
import pytz


class TaskRequest(BaseModel):
    task_id: UUID = Field(default_factory=uuid4)
    type: Literal["python", "robotframework"] = Field(..., example="python")
    path: str = Field(..., example="/home/user/scripts/test.py")
    variables: Optional[Dict[str, str]] = Field(default_factory=dict)
    queued_time: datetime = Field(default_factory=lambda: datetime.now(pytz.UTC))

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "x3x1x8f4x-55x2-41x3-x9x7-924x3097xxb0",
                "type": "python",
                "path": "/scripts/test.py",
                "variables": {
                    "user": "admin"
                },
                "queued_time": "2025-05-12T12:34:56.789Z"
            }
        }


class TaskResponse(BaseModel):
    task_id: UUID
    status: Literal["queued", "running", "success", "failed", "aborted"] = Field(..., example="queued")
    queued_time: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "x3x1x8f4x-55x2-41x3-x9x7-924x3097xxb0",
                "status": "success",
                "queued_time": "2025-05-12T12:34:56.789Z",
            }
        }
