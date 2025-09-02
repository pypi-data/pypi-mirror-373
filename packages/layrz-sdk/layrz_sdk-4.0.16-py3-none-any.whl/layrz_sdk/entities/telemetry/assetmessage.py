"""Asset message"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any, Self, cast

from geopy.distance import geodesic
from pydantic import BaseModel, Field, field_serializer
from shapely.geometry import MultiPoint

from layrz_sdk.constants import UTC
from layrz_sdk.entities.asset import Asset
from layrz_sdk.entities.asset_operation_mode import AssetOperationMode
from layrz_sdk.entities.message import Message
from layrz_sdk.entities.position import Position
from layrz_sdk.entities.telemetry.devicemessage import DeviceMessage


class AssetMessage(BaseModel):
  """Asset message model"""

  model_config = {
    'json_encoders': {
      datetime: lambda v: v.timestamp(),
      timedelta: lambda v: v.total_seconds(),
      Position: lambda v: json.loads(v.model_dump_json(exclude_none=True)),
    }
  }

  pk: int | None = Field(default=None, description='Message ID', alias='id')
  asset_id: int = Field(..., description='Asset ID')

  position: dict[str, float | int] = Field(
    default_factory=dict,
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

  geofences_ids: list[int] = Field(
    default_factory=list,
    description='List of geofence IDs associated with the message',
  )

  distance_traveled: float = Field(
    default=0.0,
    description='Distance traveled since the last message',
  )

  received_at: datetime = Field(
    default_factory=lambda: datetime.now(UTC),
    description='Timestamp when the message was received',
  )

  @field_serializer('received_at')
  def serialize_received_at(self: Self, value: datetime) -> float:
    """Serialize received_at to a timestamp."""
    return value.timestamp()

  elapsed_time: timedelta = Field(
    default_factory=lambda: timedelta(seconds=0),
    description='Elapsed time since the last message',
  )

  @field_serializer('elapsed_time')
  def serialize_elapsed_time(self: Self, value: timedelta) -> float:
    """Serialize elapsed_time to total seconds."""
    return value.total_seconds()

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
  def parse_from_devicemessage(cls, *, device_message: DeviceMessage, asset: Asset) -> AssetMessage:
    obj = cls(
      asset_id=asset.pk,
      position={},
      payload={},
      sensors={},
      received_at=device_message.received_at,
    )

    match asset.operation_mode:
      case AssetOperationMode.DISCONNECTED:
        obj.position = {}
      case AssetOperationMode.STATIC:
        obj.position = asset.static_position.model_dump(exclude_none=True) if asset.static_position else {}
      case AssetOperationMode.ZONE:
        points: MultiPoint = MultiPoint([(p.longitude, p.latitude) for p in asset.points])
        obj.position = {'latitude': points.centroid.y, 'longitude': points.centroid.x}
      case _:
        obj.position = device_message.position

    for key, value in device_message.payload.items():
      obj.payload[f'{device_message.ident}.{key}'] = value

    return obj

  def compute_distance_traveled(self: Self, *, previous_message: AssetMessage | None = None) -> float:
    """Compute the distance traveled since the last message."""
    if not self.has_point or not previous_message or not previous_message.has_point:
      return 0.0

    return cast(
      float,
      geodesic(
        (self.position['latitude'], self.position['longitude']),
        (previous_message.position['latitude'], previous_message.position['longitude']),
      ).meters,
    )

  def compute_elapsed_time(self: Self, *, previous_message: AssetMessage | None = None) -> timedelta:
    """Compute the elapsed time since the last message."""
    if not previous_message:
      return timedelta(seconds=0)

    if self.received_at < previous_message.received_at:
      return timedelta(seconds=0)

    return self.received_at - previous_message.received_at

  def to_message(self: Self) -> Message:
    """Convert the asset message to a Message object."""
    return Message(
      id=self.pk if self.pk is not None else 0,
      asset_id=self.asset_id,
      position=Position.model_validate(self.position),
      payload=self.payload,
      sensors=self.sensors,
      received_at=self.received_at,
    )
