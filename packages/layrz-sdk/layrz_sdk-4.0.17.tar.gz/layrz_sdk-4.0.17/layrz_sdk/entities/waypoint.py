"""Waypoint entity"""

from datetime import datetime, timedelta
from enum import StrEnum

from pydantic import BaseModel, Field

from .geofence import Geofence


class WaypointKind(StrEnum):
  PATHWAY = 'PATHWAY'
  """ This is the identification of the time between one waypoint and other """

  POINT = 'POINT'
  """ This refer the time inside of a geofence """

  DOWNLOADING = 'DOWNLOADING'
  """ Downloading phase of Tenvio """

  WASHING = 'WASHING'
  """ Washing phase of Tenvio """


class Waypoint(BaseModel):
  """Waypoint entity definition"""

  model_config = {
    'json_encoders': {
      datetime: lambda v: v.timestamp(),
    },
  }

  pk: int = Field(description='Waypoint ID', alias='id')
  geofence: Geofence | None = Field(default=None, description='Geofence object')
  geofence_id: int | None = Field(default=None, description='Geofence ID')
  start_at: datetime | None = Field(default=None, description='Waypoint start date')
  end_at: datetime | None = Field(default=None, description='Waypoint end date')
  sequence_real: int = Field(..., description='Real sequence number')
  sequence_ideal: int = Field(..., description='Ideal sequence number')


class WaypointRef(BaseModel):
  """Waypoint reference entity definition"""

  model_config = {
    'json_encoders': {
      timedelta: lambda v: v.total_seconds(),
      datetime: lambda v: v.timestamp(),
    },
  }

  pk: int = Field(description='Waypoint ID', alias='id')
  geofence_id: int = Field(description='Geofence ID')
  time: timedelta = Field(
    default_factory=lambda: timedelta(seconds=0),
    description='Time offset from the start of the checkpoint',
  )
  kind: WaypointKind = Field(
    ...,
    description='Defines the kind of waypoint',
  )
