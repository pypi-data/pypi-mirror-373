from __future__ import annotations
from typing import Optional
from pydantic import Field, ConfigDict

from .message_request_base import MessageRequestBase


class MessageSendLocationRequest(MessageRequestBase):
    latitude: float = Field(alias="latitude")
    longitude: float = Field(alias="longitude")
    address: Optional[str] = Field(default=None, alias="address")
    name: Optional[str] = Field(default=None, alias="name")
    url: Optional[str] = Field(default=None, alias="url")

    model_config = ConfigDict(populate_by_name=True)
