from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict
from ...entities.users.sender import Sender


class ChatPresenceEvent(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    sender: Sender
    is_from_me: bool = Field(alias="isFromMe")
    state: str
