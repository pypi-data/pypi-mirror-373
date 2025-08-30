from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict


class Sender(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    user: str
    device: int
    is_me: bool = Field(alias="isMe")
