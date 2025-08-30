from __future__ import annotations
from typing import Optional
from pydantic import Field, ConfigDict

from .message_request_base import MessageRequestBase


class MessageSendLinkRequest(MessageRequestBase):
    text: str = Field(alias="text")
    url: str = Field(alias="url")
    title: Optional[str] = Field(default=None, alias="title")
    description: Optional[str] = Field(default=None, alias="description")
    jpeg_thumbnail: Optional[str] = Field(default=None, alias="jpegThumbnail")

    model_config = ConfigDict(populate_by_name=True)
