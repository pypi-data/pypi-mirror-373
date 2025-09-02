from pydantic import BaseModel, Field, field_validator


class MapPoint(BaseModel):
  """Map point configuration"""

  latitude: float = Field(description='Latitude of the point')
  longitude: float = Field(description='Longitude of the point')
  label: str = Field(description='Label of the point')
  color: str = Field(description='Color of the point')

  @field_validator('latitude', mode='before')
  def _validate_latitude(cls, value: float) -> float:
    if value < -90 or value > 90:
      raise ValueError('Latitude must be between -90 and 90 degrees')
    return value

  @field_validator('longitude', mode='before')
  def _validate_longitude(cls, value: float) -> float:
    if value < -180 or value > 180:
      raise ValueError('Longitude must be between -180 and 180 degrees')
    return value
