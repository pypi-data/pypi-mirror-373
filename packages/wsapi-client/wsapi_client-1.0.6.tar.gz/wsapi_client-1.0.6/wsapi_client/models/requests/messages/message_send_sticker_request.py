from __future__ import annotations
from typing import Optional
from pydantic import Field, ConfigDict

from .message_request_base import MessageRequestBase


class MessageSendStickerRequest(MessageRequestBase):
    sticker_base64: Optional[str] = Field(default=None, alias="stickerBase64")
    sticker_url: Optional[str] = Field(default=None, alias="stickerUrl")
    is_animated: bool = Field(default=False, alias="isAnimated")

    model_config = ConfigDict(populate_by_name=True)
