from __future__ import annotations
from pydantic import BaseModel, Field


class AccountUpdatePictureResponse(BaseModel):
    picture_id: str = Field(alias="pictureId")

    class Config:
        populate_by_name = True