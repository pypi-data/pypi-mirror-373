from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field


class GroupParticipantRequest(BaseModel):
    user_id: str = Field(alias="userId")
    requested_at: datetime = Field(alias="requestedAt")

    class Config:
        populate_by_name = True