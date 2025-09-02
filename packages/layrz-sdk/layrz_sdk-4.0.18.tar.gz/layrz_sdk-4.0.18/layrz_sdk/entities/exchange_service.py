"""Exchange Service entity"""

from typing import Any

from pydantic import BaseModel, Field


class ExchangeService(BaseModel):
  """Exchange service definition"""

  pk: int = Field(..., description='Service ID', alias='id')
  name: str = Field(..., description='Service name')
  credentials: dict[str, Any] = Field(
    description='Service credentials',
    default_factory=dict,
  )
  protocol_id: int | None = Field(
    default=None,
    description='Protocol ID',
  )
  flespi_token: str | None = Field(
    default=None,
    description='Flespi token for the service',
  )

  owner_id: int | None = Field(
    default=None,
    description='Owner ID',
  )
