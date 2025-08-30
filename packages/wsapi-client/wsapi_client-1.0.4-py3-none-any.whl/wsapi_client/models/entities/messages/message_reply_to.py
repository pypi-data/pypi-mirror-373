from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict
from ..users.sender import Sender


class MessageReplyTo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    sender: Sender
    is_forwarded: bool = Field(alias="isForwarded")
