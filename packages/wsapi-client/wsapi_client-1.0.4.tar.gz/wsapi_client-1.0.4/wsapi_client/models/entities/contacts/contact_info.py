from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ContactInfo(BaseModel):
    id: str = Field(alias="id")
    full_name: str = Field(alias="fullName")
    business_name: str = Field(alias="businessName")
    push_name: str = Field(alias="pushName")
    status: str = Field(alias="status")
    picture_id: str = Field(alias="pictureId")
    in_phone_address_book: bool = Field(alias="inPhoneAddressBook")

    model_config = ConfigDict(populate_by_name=True)
