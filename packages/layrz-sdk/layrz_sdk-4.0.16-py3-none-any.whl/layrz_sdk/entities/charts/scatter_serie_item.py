from pydantic import BaseModel, Field


class ScatterSerieItem(BaseModel):
  """Chart Data Serie Item for Scatter Charts"""

  x: float = Field(description='X value of the item')
  y: float = Field(description='Y value of the item')
