from __future__ import annotations
from pydantic import BaseModel, ConfigDict


class UserStatusEvent(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    status: str
