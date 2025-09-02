"""Chart Data Serie"""

from typing import Any

from pydantic import BaseModel, Field

from .chart_data_serie_type import ChartDataSerieType
from .chart_data_type import ChartDataType


class ChartDataSerie(BaseModel):
  """Chart Serie"""

  data: Any = Field(description='Data of the serie')
  color: str = Field(description='Color of the serie', default='#000000')
  label: str = Field(description='Label of the serie', default='')
  serie_type: ChartDataSerieType = Field(description='Type of the serie', default=ChartDataSerieType.LINE)
  data_type: ChartDataType = Field(description='Type of the data', default=ChartDataType.NUMBER)
  dashed: bool = Field(description='If the serie should be dashed', default=False)
