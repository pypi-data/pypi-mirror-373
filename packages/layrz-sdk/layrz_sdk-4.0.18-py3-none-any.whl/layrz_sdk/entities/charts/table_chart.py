"""Number chart"""

from typing import Any, Self

from pydantic import BaseModel, Field

from .chart_render_technology import ChartRenderTechnology
from .table_header import TableHeader
from .table_row import TableRow


class TableChart(BaseModel):
  """Table chart configuration"""

  columns: list[TableHeader] = Field(description='List of columns', default_factory=list)
  rows: list[TableRow] = Field(description='List of rows', default_factory=list)

  def render(self: Self, technology: ChartRenderTechnology = ChartRenderTechnology.FLUTTER) -> dict[str, Any]:
    """
    Render chart to a graphic Library.

    :param technology: The technology to use to render the chart.
    :type technology: ChartRenderTechnology

    :return: The configuration of the chart.
    :rtype: dict[str, Any]
    """
    if technology == ChartRenderTechnology.FLUTTER:
      return {
        'library': 'FLUTTER',
        'chart': 'TABLE',
        'configuration': self._render_flutter(),
      }

    return {
      'library': 'FLUTTER',
      'chart': 'TEXT',
      'configuration': [f'Unsupported {technology}'],
    }

  def _render_flutter(self: Self) -> dict[str, Any]:
    """
    Converts the configuration of the chart to a Flutter native components.
    """
    return {
      'columns': [{'key': column.key, 'label': column.label} for column in self.columns],
      'rows': [{'data': row.data} for row in self.rows],
    }
