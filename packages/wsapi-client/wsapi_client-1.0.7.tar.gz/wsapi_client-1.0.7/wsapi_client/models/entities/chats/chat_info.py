from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict


class ChatInfo(BaseModel):
    id: str = Field(alias="id")
    name: str = Field(alias="name")

    model_config = ConfigDict(populate_by_name=True)
