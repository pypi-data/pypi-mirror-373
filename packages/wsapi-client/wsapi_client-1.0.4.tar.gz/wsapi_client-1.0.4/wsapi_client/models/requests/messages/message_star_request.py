from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict


class MessageStarRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    chat_id: str = Field(alias="chatId")
    sender_id: str = Field(alias="senderId")
    message_id: str = Field(alias="messageId")
    starred: bool
