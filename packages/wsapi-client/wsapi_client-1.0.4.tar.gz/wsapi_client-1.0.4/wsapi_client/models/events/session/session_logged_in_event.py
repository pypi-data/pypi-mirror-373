from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict


class SessionLoggedInEvent(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    device_id: str = Field(alias="deviceId")
