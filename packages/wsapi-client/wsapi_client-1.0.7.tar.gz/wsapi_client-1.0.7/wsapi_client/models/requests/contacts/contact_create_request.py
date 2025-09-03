from __future__ import annotations
from pydantic import BaseModel, Field


class ContactCreateRequest(BaseModel):
    id: str = Field(alias="id")
    full_name: str = Field(alias="fullName")
    first_name: str = Field(alias="firstName")

    class Config:
        populate_by_name = True