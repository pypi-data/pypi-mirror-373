from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from ...entities.users.sender import Sender


class MessageStarEvent(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    chat_id: str = Field(alias="chatId")
    sender: Sender
    time: datetime
    is_starred: bool = Field(alias="isStarred")
