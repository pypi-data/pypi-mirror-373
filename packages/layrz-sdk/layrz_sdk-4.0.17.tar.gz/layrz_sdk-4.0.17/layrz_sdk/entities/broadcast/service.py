"""Broadcast Service object"""

from typing import Any

from pydantic import BaseModel, Field


class BroadcastService(BaseModel):
  """Broadcast Service object"""

  pk: int = Field(..., description='Service ID', alias='id')
  name: str = Field(..., description='Service name')
  credentials: dict[str, Any] = Field(default_factory=dict, description='Service credentials')
