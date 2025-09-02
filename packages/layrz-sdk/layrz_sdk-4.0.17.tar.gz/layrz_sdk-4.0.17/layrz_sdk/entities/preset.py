"""Preset entity"""

from datetime import datetime

from pydantic import BaseModel, Field


class Preset(BaseModel):
  """Preset entity"""

  model_config = {
    'json_encoders': {
      datetime: lambda v: v.timestamp(),
    },
  }

  pk: int = Field(description='Defines the primary key of the preset', alias='id')
  name: str = Field(description='Defines the name of the preset')
  valid_before: datetime = Field(
    ...,
    description='Defines the date and time before which the preset is valid',
  )
  comment: str = Field(
    default='',
    description='Defines the comment of the preset',
  )
  owner_id: int = Field(
    ...,
    description='Defines the ID of the owner of the preset',
  )
