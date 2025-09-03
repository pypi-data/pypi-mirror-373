from __future__ import annotations
from pydantic import BaseModel, Field


class ChatUpdatePinRequest(BaseModel):
    pinned: bool = Field(alias="pinned")

    class Config:
        populate_by_name = True