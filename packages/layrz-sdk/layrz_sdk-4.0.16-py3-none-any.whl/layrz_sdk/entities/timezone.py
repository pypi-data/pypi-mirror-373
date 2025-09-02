"""Timezone entity"""

from pydantic import BaseModel, Field


class Timezone(BaseModel):
  """Timezone entity"""

  pk: int = Field(..., description='Defines the primary key of the timezone', alias='id')
  name: str = Field(..., description='Defines the name of the timezone')
  offset: int = Field(..., description='Defines the offset of the timezone in seconds from UTC')
