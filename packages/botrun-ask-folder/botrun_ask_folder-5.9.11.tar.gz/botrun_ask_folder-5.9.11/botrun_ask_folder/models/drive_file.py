from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum
from .splitted_file import SplittedFile
import pytz


class DriveFileStatus(str, Enum):
    INITIATED = "initiated"
    DOWNLOADED = "downloaded"
    SPLITTED = "splitted"
    EMBEDDED = "embedded"


class DriveFile(BaseModel):
    """
    Represents an item in a collection, typically a file or folder.

    Attributes:
        id (str): Google file id
        name (str): 檔案名字，如果是處理過後的檔案，會存split過後的檔名
        mimeType (str): MIME type of the item.
        modifiedTime (str): Last modification time of the item.
        size (str): Size of the item, typically in bytes.
        parent (str): 在 Google Drive 上的 parent
        path (str): 在 Google Drive 上的 parent Full path
        splitted_files (List[str]): List of SplittedFile ids
        folder_id (str): 在 Google Drive 上的 folder id
        save_path (str): storage 儲存路徑，如果是空的表示目前沒有儲存
        status (DriveFileStatus): Current status of the drive file
        updated_at (str): Last updated time in "YYYY-MM-DD HH:MM:SS" format.
    """

    id: str
    name: str
    mimeType: str
    modifiedTime: str
    size: str
    parent: str
    path: str
    folder_id: str
    save_path: str = ""
    splitted_files: List[str] = []
    status: DriveFileStatus = DriveFileStatus.INITIATED
    updated_at: str = Field(
        default_factory=lambda: datetime.now(pytz.timezone("Asia/Taipei")).strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        description="Last updated time in Asia/Taipei timezone",
    )

    @classmethod
    def from_json(cls, json_str: str) -> "DriveFile":
        return cls.model_validate_json(json_str)

    def to_json(self) -> str:
        return self.model_dump_json(exclude_none=True)

    @classmethod
    def from_list(cls, item_list: List[dict]) -> List["DriveFile"]:
        return [cls(**item) for item in item_list]

    @classmethod
    def to_list(cls, items: List["DriveFile"]) -> List[dict]:
        return [item.model_dump(exclude_none=True) for item in items]

    def refresh_timestamp(self):
        """
        Update the updated_at timestamp to the current time in Asia/Taipei timezone.
        """
        self.updated_at = datetime.now(pytz.timezone("Asia/Taipei")).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
