from pydantic import BaseModel, Field
from datetime import datetime
import pytz
from typing import List, Dict


class LineBotUserSetting(BaseModel):
    user_id: str
    model_name: str = ""  # 默認模型
    chat_history: List[Dict[str, str]] = Field(default_factory=list)
    created_at: str = datetime.now(pytz.timezone("Asia/Taipei")).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    updated_at: str = datetime.now(pytz.timezone("Asia/Taipei")).strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    def refresh_timestamp(self):
        self.updated_at = datetime.now(pytz.timezone("Asia/Taipei")).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    def add_chat_entry(self, user_message: str, system_response: str):
        self.chat_history.append({"user": user_message, "assistant": system_response})
        if len(self.chat_history) > 10:
            self.chat_history.pop(0)
