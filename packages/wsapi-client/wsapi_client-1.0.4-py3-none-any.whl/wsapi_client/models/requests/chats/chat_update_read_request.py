from __future__ import annotations
from pydantic import BaseModel, Field


class ChatUpdateReadRequest(BaseModel):
    read: bool = Field(alias="read")

    class Config:
        populate_by_name = True