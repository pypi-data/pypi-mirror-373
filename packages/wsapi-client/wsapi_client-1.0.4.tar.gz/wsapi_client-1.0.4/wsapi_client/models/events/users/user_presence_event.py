from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class UserPresenceEvent(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    status: str
    last_seen: datetime = Field(alias="lastSeen")
