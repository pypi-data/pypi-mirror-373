from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class BaseEvent(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    instance_id: str = Field(alias="instanceId")
    received_at: datetime = Field(alias="receivedAt")
    event_type: str = Field(alias="eventType")
