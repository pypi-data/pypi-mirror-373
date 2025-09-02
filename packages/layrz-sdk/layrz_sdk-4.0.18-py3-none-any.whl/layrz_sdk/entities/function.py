"""Geofence entity"""

from datetime import timedelta
from typing import Any

from pydantic import BaseModel, Field

from .asset import Asset


class Function(BaseModel):
  """Function entity"""

  pk: int = Field(description='Defines the primary key of the Function', alias='id')
  name: str = Field(description='Name of the function')

  maximum_time: timedelta | None = Field(
    default=None,
    description='Maximum time for the function to run',
  )
  minutes_delta: timedelta | None = Field(
    default=None,
    description='Time delta in minutes for the function to run',
  )

  external_identifiers: list[str] = Field(
    default_factory=list,
    description='List of external identifiers for the function',
  )

  credentials: dict[str, Any] = Field(
    default_factory=dict,
    description='Credentials for the function',
  )

  assets: list[Asset] = Field(
    default_factory=list,
    description='List of assets associated with the function',
  )

  # Foreign keys – normally expose only the FK id to keep the payload small.
  owner_id: int | None = Field(
    default=None,
    description='Owner ID of the function',
  )
  algorithm_id: int = Field(..., description='Algorithm ID of the function')
