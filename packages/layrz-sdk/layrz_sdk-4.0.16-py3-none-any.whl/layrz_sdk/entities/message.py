"""Message entity"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator

from layrz_sdk.constants import UTC
from layrz_sdk.entities.geofence import Geofence
from layrz_sdk.entities.position import Position


class Message(BaseModel):
  """Message definition"""

  model_config = {
    'json_encoders': {
      datetime: lambda v: v.timestamp(),
    }
  }

  pk: int = Field(..., description='Message ID', alias='id')
  asset_id: int = Field(..., description='Asset ID')
  position: Position = Field(
    default_factory=lambda: Position(),
    description='Current position of the device',
  )
  payload: dict[str, Any] = Field(
    default_factory=dict,
    description='Payload data of the device message',
  )
  sensors: dict[str, Any] = Field(
    default_factory=dict,
    description='Sensor data of the device message',
  )
  received_at: datetime = Field(
    default_factory=lambda: datetime.now(UTC),
    description='Timestamp when the message was received',
  )

  geofences: list[Geofence] = Field(
    default_factory=list,
    description='List of geofences associated with the message',
  )

  @field_validator('geofences', mode='before')
  def _validate_geofences(cls, value: Any) -> list[Geofence]:
    """Validate geofences"""
    if value is None:
      return []

    if not isinstance(value, list):
      return []

    return value
