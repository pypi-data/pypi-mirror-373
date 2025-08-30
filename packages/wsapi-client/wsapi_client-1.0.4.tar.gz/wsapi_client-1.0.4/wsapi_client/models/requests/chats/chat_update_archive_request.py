from __future__ import annotations
from pydantic import BaseModel, Field


class ChatUpdateArchiveRequest(BaseModel):
    archived: bool = Field(alias="archived")

    class Config:
        populate_by_name = True