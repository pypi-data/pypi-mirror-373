from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Dict
from enum import Enum
import pytz

from botrun_ask_folder.models.drive_file import DriveFileStatus


class DriveFolderStatus(str, Enum):
    """
    Enumeration of possible collection statuses.
    """

    INTIATED = "INTIATED"
    PROCESSING = "PROCESSING"
    DONE = "DONE"
    FAILED = "FAILED"


class DriveFolder(BaseModel):
    """
    Represents the status of a collection.也就是 Google Drive 的一個 folder

    Attributes:
        id (str): Unique identifier for the collection.
        status (FolderStatusEnum): Current status of the collection.
        items (List[str]): List of DriveFile ids in the collection.
        updated_at (str): Last updated time in "YYYY-MM-DD HH:MM:SS" format.
    """

    id: str = Field(..., description="Unique identifier for the collection")
    status: DriveFolderStatus = Field(
        ..., description="Current status of the collection"
    )
    items: List[str] = Field(
        default_factory=list, description="List of DriveFile ids in the collection"
    )
    # file_statuses: Dict[str, DriveFileStatus] = Field(
    #     default_factory=dict,
    #     description="Dictionary mapping DriveFile ids to their statuses",
    # )
    last_update_items_timestamp: str = Field(
        default="", description="最後一次 update items 的時間戳"
    )
    last_update_items: List[str] = Field(
        default_factory=list, description="最後一次 update 的 items"
    )
    last_update_failed_items: List[str] = Field(
        default_factory=list, description="最後一次 update 時有出錯的 items"
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now(pytz.timezone("Asia/Taipei")).strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        description="Last updated time in Asia/Taipei timezone",
    )

    @classmethod
    def model_validate_json(cls, json_data: str) -> "DriveFolder":
        """
        Create a DriveFolder instance from a JSON string.

        Args:
            json_data (str): JSON string representing a DriveFolder.

        Returns:
            DriveFolder: An instance of DriveFolder.
        """
        return super().model_validate_json(json_data)

    def model_dump_json(self, **kwargs) -> str:
        """
        Convert the DriveFolder instance to a JSON string.

        Returns:
            str: JSON representation of the DriveFolder.
        """
        return super().model_dump_json(**kwargs)

    def refresh_timestamp(self):
        """
        Update the updated_at timestamp to the current time in Asia/Taipei timezone.
        """
        self.updated_at = datetime.now(pytz.timezone("Asia/Taipei")).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
