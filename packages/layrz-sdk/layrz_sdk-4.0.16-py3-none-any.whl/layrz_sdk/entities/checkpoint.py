"""Checkpoints entitites"""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from .waypoint import Waypoint, WaypointRef


class CheckpointOperationMode(StrEnum):
  """Defines the operation mode of a checkpoint"""

  FLEX = 'FLEX'
  """ Defines a flexible operation mode for the checkpoint """

  STRICT = 'STRICT'
  """ Defines a strict operation mode for the checkpoint """


class Checkpoint(BaseModel):
  """Checkpoint entity definition"""

  model_config = {
    'json_encoders': {
      datetime: lambda v: v.timestamp(),
    },
  }

  pk: int = Field(description='Checkpoint ID')
  asset_id: int = Field(description='Asset ID')
  waypoints: list[Waypoint] = Field(description='List of waypoints', default_factory=list)
  start_at: datetime = Field(description='Checkpoint start date')
  end_at: datetime = Field(description='Checkpoint end date')


class CheckpointRef(BaseModel):
  """Checkpoint reference entity definition"""

  model_config = {
    'json_encoders': {
      CheckpointOperationMode: lambda v: v.value,
    },
  }

  pk: int = Field(description='Checkpoint ID', alias='id')
  name: str = Field(description='Checkpoint name')
  waypoints: list[WaypointRef] = Field(description='List of waypoints', default_factory=list)

  operation_mode: CheckpointOperationMode = Field(
    ...,
    description='Checkpoint operation mode',
  )
