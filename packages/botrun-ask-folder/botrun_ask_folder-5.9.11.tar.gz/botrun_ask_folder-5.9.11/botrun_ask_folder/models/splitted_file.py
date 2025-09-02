from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime
import pytz


class SplittedFileStatus(str, Enum):
    CREATED = "created"
    EMBEDDED = "embedded"


class SplittedFile(BaseModel):
    """
    Represents a split item from a collection item.

    Attributes:
        id (str): Unique identifier for the split item
        name (str): Name of the split item
        gen_page_imgs (bool): Whether page images have been generated for this item
        ori_file_name (str): Original file name this item was split from
        modified_time (str): Modified time of this split item
        page_number (Optional[int]): Page number of this split item
        sheet_name (Optional[str]): Sheet name of this split item
        file_id (str): ID of the DriveFile this split file belongs to
        save_path (str): storage 儲存路徑，如果是空的表示目前沒有儲存
        status (SplittedFileStatus): Current status of the split file
        updated_at (str): Last updated time in "YYYY-MM-DD HH:MM:SS" format.
    """

    id: str
    name: str
    gen_page_imgs: bool = False
    ori_file_name: str
    modified_time: str
    page_number: Optional[int] = None
    sheet_name: Optional[str] = None
    file_id: str
    save_path: str = ""
    status: SplittedFileStatus = SplittedFileStatus.CREATED
    updated_at: str = Field(
        default_factory=lambda: datetime.now(pytz.timezone("Asia/Taipei")).strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        description="Last updated time in Asia/Taipei timezone",
    )

    @classmethod
    def from_json(cls, json_str: str) -> "SplittedFile":
        return cls.model_validate_json(json_str)

    def to_json(self) -> str:
        return self.model_dump_json(exclude_none=True)

    def refresh_timestamp(self):
        """
        Update the updated_at timestamp to the current time in Asia/Taipei timezone.
        """
        self.updated_at = datetime.now(pytz.timezone("Asia/Taipei")).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
