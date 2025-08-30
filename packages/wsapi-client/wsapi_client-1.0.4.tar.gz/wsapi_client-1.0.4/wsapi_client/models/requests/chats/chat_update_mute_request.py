from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class ChatUpdateMuteRequest(BaseModel):
    duration: Optional[str] = Field(alias="duration", default=None)

    class Config:
        populate_by_name = True