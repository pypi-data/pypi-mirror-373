"""Broadcast Result Response data"""

from typing import Any

from pydantic import BaseModel, Field


class BroadcastResponse(BaseModel):
  """Broadcast response data"""

  parsed: Any = Field(description='Parsed data')
  raw: str = Field(description='Raw data')
