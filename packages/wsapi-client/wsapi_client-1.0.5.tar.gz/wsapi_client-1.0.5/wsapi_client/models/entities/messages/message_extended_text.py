from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict


class MessageExtendedText(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    matched_text: str | None = Field(alias="matchedText", default=None)
    description: str | None = None
    title: str | None = None
    jpeg_thumbnail: str | None = Field(alias="jpegThumbnail", default=None)
