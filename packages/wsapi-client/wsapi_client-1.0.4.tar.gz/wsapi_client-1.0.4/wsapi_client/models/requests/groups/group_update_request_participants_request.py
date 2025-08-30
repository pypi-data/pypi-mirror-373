from __future__ import annotations
from typing import List
from pydantic import BaseModel, Field


class GroupUpdateRequestParticipantsRequest(BaseModel):
    participants: List[str] = Field(alias="participants", default_factory=list)
    action: str = Field(alias="action")

    class Config:
        populate_by_name = True