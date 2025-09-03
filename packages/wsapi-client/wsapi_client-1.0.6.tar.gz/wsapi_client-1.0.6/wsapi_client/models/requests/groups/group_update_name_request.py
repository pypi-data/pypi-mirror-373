from __future__ import annotations
from pydantic import BaseModel, Field


class GroupUpdateNameRequest(BaseModel):
    name: str = Field(alias="name")

    class Config:
        populate_by_name = True