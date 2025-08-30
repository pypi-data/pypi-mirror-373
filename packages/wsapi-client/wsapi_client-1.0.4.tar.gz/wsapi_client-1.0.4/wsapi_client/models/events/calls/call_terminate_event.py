from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class CallTerminateEvent(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    caller: str
    time: datetime
    reason: str
