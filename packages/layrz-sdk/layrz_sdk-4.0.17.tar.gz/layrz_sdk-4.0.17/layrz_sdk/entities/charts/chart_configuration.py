"""Charts entities"""

from pydantic import BaseModel, Field


class ChartConfiguration(BaseModel):
  """Chart configuration"""

  name: str = Field(description='Name of the chart')
  description: str = Field(description='Description of the chart')
