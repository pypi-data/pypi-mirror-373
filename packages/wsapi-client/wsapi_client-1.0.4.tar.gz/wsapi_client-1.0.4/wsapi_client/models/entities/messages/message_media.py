from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict


class MessageMedia(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    media_type: str = Field(alias="mediaType")
    url: str
    mimetype: str | None = Field(alias="mimeType", default=None)
    file_length: int = Field(alias="fileLength")
    file_sha256: str | None = Field(alias="fileSHA256", default=None)
    file_enc_sha256: str | None = Field(alias="fileEncSHA256", default=None)
    media_key: str | None = Field(alias="mediaKey", default=None)
    caption: str | None = None
    height: int = 0
    width: int = 0
    jpeg_thumbnail: str | None = Field(alias="jpegThumbnail", default=None)
    direct_path: str | None = Field(alias="directPath", default=None)
    duration: int = 0
    page_count: int = Field(alias="pageCount", default=0)
    title: str | None = None
