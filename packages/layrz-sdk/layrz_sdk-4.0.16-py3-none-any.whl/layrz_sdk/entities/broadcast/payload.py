"""Broadcast Payload data"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from layrz_sdk.constants import UTC
from layrz_sdk.entities.asset import Asset
from layrz_sdk.entities.device import Device
from layrz_sdk.entities.trigger import Trigger

from .service import BroadcastService


class BroadcastPayload(BaseModel):
  """Broadcast payload data, structure that is sent to the Outbound MQTT and other services"""

  model_config = {
    'loc_by_alias': True,
    'json_encoders': {
      datetime: lambda v: v.timestamp(),
    },
  }

  asset: Asset = Field(..., description='Asset object')
  primary_device: Device | None = Field(default=None, description='Primary device object')
  trigger: Trigger | None = Field(default=None, description='Trigger object, if available')
  message_id: int | str = Field(..., description='Message ID')
  service: BroadcastService | None = Field(default=None, description='Broadcast service object')
  position: dict[str, Any] = Field(default_factory=dict, description='Position data, if available')
  sensors: dict[str, Any] = Field(default_factory=dict, description='Sensors data, if available')
  payload: dict[str, Any] = Field(default_factory=dict, description='Payload data, if available')
  received_at: datetime = Field(
    default_factory=lambda: datetime.now(UTC),
    description='Broadcast payload received date',
  )
