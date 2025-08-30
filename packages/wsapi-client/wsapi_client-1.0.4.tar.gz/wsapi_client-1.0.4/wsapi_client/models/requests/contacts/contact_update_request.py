from __future__ import annotations
from pydantic import BaseModel, Field


class ContactUpdateRequest(BaseModel):
    full_name: str = Field(alias="fullName")
    first_name: str = Field(alias="firstName")

    class Config:
        populate_by_name = True