"""Ats Reception entity"""

from datetime import datetime

from pydantic import BaseModel, Field

from layrz_sdk.constants import UTC


class AtsReception(BaseModel):
  """AtsReception entity"""

  pk: int = Field(description='Defines the primary key of the AtsReception', alias='id')
  volume_bought: float = Field(
    description='Volume bought in liters',
    default=0.0,
  )
  real_volume: float | None = Field(
    description='Real volume in liters',
    default=None,
  )

  received_at: datetime = Field(
    description='Date and time when the reception was made',
    default_factory=lambda: datetime.now(UTC),
  )
  fuel_type: str = Field(
    description='Type of fuel used in the reception',
    default='',
  )
  is_merged: bool = Field(
    description='Indicates if the reception is merged with another',
    default=False,
  )
  order_id: int | None = Field(
    description='Order ID associated with the reception',
    default=None,
  )
