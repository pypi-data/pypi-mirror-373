from __future__ import annotations
from pydantic import BaseModel, Field


class AccountUpdatePictureRequest(BaseModel):
    picture_base64: str = Field(alias="pictureBase64")

    class Config:
        populate_by_name = True