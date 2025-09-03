from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict


class MessagePin(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    message_id: str = Field(alias="messageId")
    is_from_me: bool = Field(alias="isFromMe")
    pinned: bool
    expiration: str
