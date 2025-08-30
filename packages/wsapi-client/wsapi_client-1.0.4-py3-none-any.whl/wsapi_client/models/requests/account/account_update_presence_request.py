from __future__ import annotations
from pydantic import BaseModel, Field


class AccountUpdatePresenceRequest(BaseModel):
    status: str = Field(alias="status")

    class Config:
        populate_by_name = True