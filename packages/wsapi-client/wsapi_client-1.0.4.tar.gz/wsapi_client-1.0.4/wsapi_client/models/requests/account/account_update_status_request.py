from __future__ import annotations
from pydantic import BaseModel, Field


class AccountUpdateStatusRequest(BaseModel):
    status: str = Field(alias="status")

    class Config:
        populate_by_name = True