from __future__ import annotations
from pydantic import BaseModel, Field


class GroupPictureInfo(BaseModel):
    picture_id: str = Field(alias="pictureId")
    picture_url: str = Field(alias="pictureUrl")

    class Config:
        populate_by_name = True