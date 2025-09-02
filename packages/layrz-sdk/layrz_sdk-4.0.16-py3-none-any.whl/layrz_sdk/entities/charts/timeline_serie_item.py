from datetime import datetime

from pydantic import BaseModel, Field


class TimelineSerieItem(BaseModel):
  """Chart Data Serie Item for Timeline Charts"""

  name: str = Field(description='Name of the item')
  start_at: datetime = Field(description='Start date of the item')
  end_at: datetime = Field(description='End date of the item')
  color: str = Field(description='Color of the item')
