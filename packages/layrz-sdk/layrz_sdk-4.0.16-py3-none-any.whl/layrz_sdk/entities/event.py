"""Event entity"""

from datetime import datetime

from pydantic import BaseModel, Field

from .geofence import Geofence
from .message import Message
from .presence_type import PresenceType
from .trigger import Trigger


class Event(BaseModel):
  """Event entity definition"""

  pk: int = Field(description='Event ID', alias='id')
  trigger: Trigger = Field(description='Event trigger')
  asset_id: int = Field(description='Asset ID')
  message: Message = Field(description='Message')
  activated_at: datetime = Field(description='Event activation date')
  geofence: Geofence | None = Field(default=None, description='Geofence object')
  presence_type: PresenceType | None = Field(default=None, description='Presence type object')
