from pydantic import BaseModel, Field

from .chart_data_serie_type import ChartDataSerieType
from .scatter_serie_item import ScatterSerieItem


class ScatterSerie(BaseModel):
  """Chart Data Serie for Timeline charts"""

  data: list[ScatterSerieItem] = Field(description='List of data points', default_factory=list)
  color: str = Field(description='Color of the serie', default='')
  label: str = Field(description='Label of the serie', default='')
  serie_type: ChartDataSerieType = Field(description='Type of the serie', default=ChartDataSerieType.SCATTER)
