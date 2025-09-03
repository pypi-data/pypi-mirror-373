from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict


class UserPushNameEvent(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    push_name: str = Field(alias="pushName")
