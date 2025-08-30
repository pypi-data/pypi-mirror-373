from __future__ import annotations
from pydantic import BaseModel, Field


class GroupUpdateDescriptionRequest(BaseModel):
    description: str = Field(alias="description")

    class Config:
        populate_by_name = True