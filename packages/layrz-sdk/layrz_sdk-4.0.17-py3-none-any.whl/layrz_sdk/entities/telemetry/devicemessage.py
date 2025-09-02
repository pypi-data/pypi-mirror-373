"""Device message"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Self

from pydantic import BaseModel, Field, field_serializer

from layrz_sdk.constants import REJECTED_KEYS, UTC
from layrz_sdk.entities.device import Device
from layrz_sdk.entities.message import Message
from layrz_sdk.entities.position import Position


class DeviceMessage(BaseModel):
  """Device message model"""

  pk: int | None = Field(default=None, description='Device message ID', alias='id')
  ident: str = Field(..., description='Device identifier')
  device_id: int = Field(..., description='Device ID')
  protocol_id: int = Field(..., description='Protocol ID')

  position: dict[str, float | int] = Field(
    default_factory=dict,
    description='Current position of the device',
  )

  payload: dict[str, Any] = Field(
    default_factory=dict,
    description='Payload data of the device message',
  )

  received_at: datetime = Field(
    default_factory=lambda: datetime.now(UTC),
    description='Timestamp when the message was received',
  )

  @field_serializer('received_at')
  def serialize_received_at(self: Self, value: datetime) -> float:
    """Serialize received_at to a timestamp."""
    return value.timestamp()

  @property
  def datum_gis(self: Self) -> int:
    """Get the GIS datum of the message."""
    return 4326

  @property
  def point_gis(self: Self) -> str | None:
    """Get the GIS point of the message on WKT (Well-Known Text) format for OGC (Open Geospatial Consortium)."""
    latitude = self.position.get('latitude')
    longitude = self.position.get('longitude')

    if latitude is not None and longitude is not None:
      return f'POINT({longitude} {latitude})'

    return None

  @property
  def has_point(self: Self) -> bool:
    """Check if the message has a point."""
    latitude = self.position.get('latitude')
    longitude = self.position.get('longitude')

    return latitude is not None and longitude is not None

  @classmethod
  def parse_from_dict(cls, *, raw_payload: dict[str, Any], device: Device) -> DeviceMessage:
    """Format a DeviceMessage from a dictionary."""
    received_at: datetime
    position: dict[str, float | int] = {}
    payload: dict[str, Any] = {}

    if 'timestamp' in raw_payload:
      received_at = datetime.fromtimestamp(raw_payload['timestamp'], tz=UTC)
    else:
      received_at = datetime.now(UTC)

    for key, value in raw_payload.items():
      if key.startswith('position.'):
        position[key[9:]] = value

      if key not in REJECTED_KEYS:
        payload[key] = value

    return cls(
      ident=device.ident,
      device_id=device.pk,
      protocol_id=device.protocol_id,  # type: ignore
      position=position,
      payload=payload,
      received_at=received_at,
    )

  def to_message(self: Self) -> Message:
    """Convert the asset message to a Message object."""
    return Message(
      id=self.pk if self.pk is not None else 0,
      asset_id=self.device_id if self.device_id is not None else 0,
      position=Position.model_validate(self.position),
      payload=self.payload,
      received_at=self.received_at,
    )
