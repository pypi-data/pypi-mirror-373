from pydantic import BaseModel, Field
import uuid
from enum import Enum
from datetime import datetime
import pytz


class JobType(str, Enum):
    LIST_FILES = "list_files"
    HANDLE_FILES = "handle_files"


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    FAILED = "failed"


class JobEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_type: JobType
    data: str
    status: JobStatus = JobStatus.PENDING
    updated_at: str = Field(
        default_factory=lambda: datetime.now(pytz.timezone("Asia/Taipei")).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )
    error: str = ""

    class Config:
        json_schema_extra = {
            "example": {
                "job_type": "list_files",
                "data": '{"folder_id": "1234567890", "force": false}',
                "status": "pending",
                "updated_at": "2023-04-20 15:30:00",
            }
        }

    @classmethod
    def from_json(cls, json_str: str) -> "JobEvent":
        return cls.model_validate_json(json_str)

    def to_json(self) -> str:
        return self.model_dump_json(exclude_none=True)
