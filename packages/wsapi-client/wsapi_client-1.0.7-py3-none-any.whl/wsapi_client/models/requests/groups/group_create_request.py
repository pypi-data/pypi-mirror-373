from __future__ import annotations
from typing import List
from pydantic import BaseModel, Field


class GroupCreateRequest(BaseModel):
    name: str = Field(alias="name")
    participants: List[str] = Field(alias="participants", default_factory=list)

    class Config:
        populate_by_name = True