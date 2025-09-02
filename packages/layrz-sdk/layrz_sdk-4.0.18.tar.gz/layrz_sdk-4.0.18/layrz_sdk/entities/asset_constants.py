"""Asset constants"""

from datetime import timedelta

from pydantic import BaseModel, Field


class AssetConstants(BaseModel):
  """Asset constants"""

  model_config = {
    'json_encoders': {
      timedelta: lambda v: v.total_seconds(),
    },
  }

  distance_traveled: float = Field(default=0.0, description='Total distance traveled by the asset in meters')
  primary_device: str = Field(default='N/A', description='Primary device associated with the asset')
  elapsed_time: timedelta = Field(
    default=timedelta(seconds=0),
    description='Total elapsed time for the asset in seconds',
  )
