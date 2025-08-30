from __future__ import annotations
from pydantic import BaseModel, Field


class ChatUpdateEphemeralExpirationRequest(BaseModel):
    expiration: str = Field(alias="expiration")

    class Config:
        populate_by_name = True