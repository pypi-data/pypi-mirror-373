from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class MediaDownloadRequest(BaseModel):
    media_type: str = Field(alias="mediaType")
    url: str = Field(alias="url")
    direct_path: Optional[str] = Field(default=None, alias="directPath")
    media_key: Optional[str] = Field(default=None, alias="mediaKey")
    mime_type: Optional[str] = Field(default=None, alias="mimeType")
    file_length: int = Field(alias="fileLength")
    file_sha256: Optional[str] = Field(default=None, alias="fileSHA256")
    file_enc_sha256: Optional[str] = Field(default=None, alias="fileEncSHA256")
    file_name: Optional[str] = Field(default=None, alias="fileName")

    model_config = ConfigDict(populate_by_name=True)
