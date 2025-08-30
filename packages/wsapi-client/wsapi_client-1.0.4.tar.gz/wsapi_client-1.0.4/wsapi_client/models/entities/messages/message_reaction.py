from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict


class MessageReaction(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    message_id: str = Field(alias="messageId")
    emoji: str
