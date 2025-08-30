from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict


class ContactEvent(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    full_name: str = Field(alias="fullName")
    in_phone_address_book: bool = Field(alias="inPhoneAddressBook")
