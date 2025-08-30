from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict


class UserInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    is_in_whats_app: bool = Field(alias="isInWhatsApp")
    status: str
    picture_id: str = Field(alias="pictureId")
    picture_url: str = Field(alias="pictureUrl")
    is_verified: bool = Field(alias="isVerified")
