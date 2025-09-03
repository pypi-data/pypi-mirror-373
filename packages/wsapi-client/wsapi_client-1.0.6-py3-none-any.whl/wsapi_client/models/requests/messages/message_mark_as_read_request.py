from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict


class MessageMarkAsReadRequest(BaseModel):
    chat_id: str = Field(alias="chatId")
    sender_id: str = Field(alias="senderId")
    receipt_type: str = Field(alias="receiptType")

    model_config = ConfigDict(populate_by_name=True)
