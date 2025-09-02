from typing import Optional

from pydantic import BaseModel, Field

from .chart_data_type import ChartDataType


class AxisConfig(BaseModel):
  """Axis configuration"""

  label: str = Field(default='', description='Label of the axis')
  measure_unit: str = Field(default='', description='Measure unit of the axis')
  min_value: Optional[float] = Field(default=None, description='Minimum value of the axis')
  max_value: Optional[float] = Field(default=None, description='Maximum value of the axis')
  data_type: ChartDataType = Field(default=ChartDataType.DATETIME, description='Data type of the axis')
