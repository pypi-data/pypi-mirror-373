from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from ...entities.users.sender import Sender


class MessageDeleteEvent(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    chat_id: str = Field(alias="chatId")
    sender: Sender
    sender_name: str = Field(alias="senderName")
    time: datetime
    is_from_me: bool = Field(alias="isFromMe")
    is_deleted_for_me: bool = Field(alias="isDeletedForMe")
    is_deleted_for_all: bool = Field(alias="isDeletedForAll")
    is_status: bool = Field(alias="isStatus")
