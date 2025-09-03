from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from ...entities.users.sender import Sender


class MessageReadEvent(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    chat_id: str = Field(alias="chatId")
    sender: Sender
    time: datetime
    is_group: bool = Field(alias="isGroup")
    is_from_me: bool = Field(alias="isFromMe")
    message_sender: Sender = Field(alias="messageSender")
    receipt_type: str = Field(alias="receiptType")
    message_ids: list[str] = Field(alias="messageIds")
