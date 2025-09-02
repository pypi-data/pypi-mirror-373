from pydantic import BaseModel, Field


class StaticPosition(BaseModel):
  latitude: float = Field(
    ...,
    description='Latitude of the static position',
  )
  longitude: float = Field(
    ...,
    description='Longitude of the static position',
  )

  altitude: float | None = Field(
    default=None,
    description='Altitude of the static position',
  )
