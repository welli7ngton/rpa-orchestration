from pydantic import BaseModel, Field
from typing import Optional, Dict, Literal


class TaskRequest(BaseModel):
    id: int = Field(..., example=1)
    type: Literal["python", "robotframework"] = Field(..., example="python")
    path: str = Field(..., example="/home/user/scripts/test.py")
    variables: Optional[Dict[str, str]] = Field(default_factory=dict)

    class Config:
        schema_extra = {
            "example": {
                "id": 123,
                "type": "python",
                "path": "/scripts/test.py",
                "variables": {
                    "user": "admin"
                }
            }
        }


class TaskResponse(BaseModel):
    id: int
    status: Literal["queued", "running", "success", "failed"]

    class Config:
        schema_extra = {
            "example": {
                "id": 123,
                "status": "queued"
            }
        }
