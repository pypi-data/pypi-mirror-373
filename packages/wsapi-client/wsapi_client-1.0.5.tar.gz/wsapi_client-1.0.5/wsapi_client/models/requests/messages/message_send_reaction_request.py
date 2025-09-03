from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class MessageSendReactionRequest(BaseModel):
    to: str = Field(alias="to")
    sender_id: Optional[str] = Field(default=None, alias="senderId")
    reaction: str = Field(alias="reaction")

    model_config = ConfigDict(populate_by_name=True)
