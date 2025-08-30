from __future__ import annotations
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict


class ProblemDetails(BaseModel):
    type: Optional[str] = None
    title: Optional[str] = None
    status: Optional[int] = None
    detail: Optional[str] = None
    instance: Optional[str] = None

    model_config = ConfigDict(extra="allow")
