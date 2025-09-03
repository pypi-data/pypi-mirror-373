from __future__ import annotations
from pydantic import BaseModel, Field


class GroupCreated(BaseModel):
    id: str = Field(alias="id")

    class Config:
        populate_by_name = True