from __future__ import annotations
from pydantic import BaseModel, Field


class ChatUpdatePresenceRequest(BaseModel):
    state: str = Field(alias="state")

    class Config:
        populate_by_name = True