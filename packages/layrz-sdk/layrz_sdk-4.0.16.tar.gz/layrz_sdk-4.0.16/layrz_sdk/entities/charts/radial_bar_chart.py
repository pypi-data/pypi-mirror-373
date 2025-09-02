"""Radial Bar chart"""

from typing import Any, Self

from pydantic import BaseModel, Field

from .chart_alignment import ChartAlignment
from .chart_data_serie import ChartDataSerie
from .chart_render_technology import ChartRenderTechnology


class RadialBarChart(BaseModel):
  """Radial Bar chart configuration"""

  series: list[ChartDataSerie] = Field(description='List of series to be displayed in the chart', default_factory=list)
  title: str = Field(description='Title of the chart', default='Chart')
  align: ChartAlignment = Field(description='Alignment of the chart', default=ChartAlignment.CENTER)

  def render(
    self: Self,
    technology: ChartRenderTechnology = ChartRenderTechnology.SYNCFUSION_FLUTTER_CHARTS,
  ) -> dict[str, Any]:
    """
    Render chart to a graphic Library.

    :param technology: The technology to use to render the chart.
    :type technology: ChartRenderTechnology

    :return: The configuration of the chart.
    :rtype: dict[str, Any]
    """
    if technology == ChartRenderTechnology.GRAPHIC:
      return {
        'library': 'GRAPHIC',
        'chart': 'RADIALBAR',
        'configuration': self._render_graphic(),
      }

    if technology == ChartRenderTechnology.APEX_CHARTS:
      return {
        'library': 'APEXCHARTS',
        'chart': 'RADIALBAR',
        'configuration': self._render_apexcharts(),
      }

    if technology == ChartRenderTechnology.SYNCFUSION_FLUTTER_CHARTS:
      return {
        'library': 'SYNCFUSION_FLUTTER_CHARTS',
        'chart': 'RADIALBAR',
        'configuration': self._render_syncfusion_flutter_charts(),
      }

    return {
      'library': 'FLUTTER',
      'chart': 'TEXT',
      'configuration': [f'Unsupported {technology}'],
    }

  def _render_syncfusion_flutter_charts(self) -> Any:
    """
    Converts the configuration of the chart to Syncfusion Flutter Charts.
    """
    series = []

    for serie in self.series:
      series.append(
        {
          'label': serie.label,
          'color': serie.color,
          'value': serie.data[0],
        }
      )

    return {'series': series}

  def _render_graphic(self) -> Any:
    """
    Converts the configuration of the chart to a Flutter library Graphic.
    """
    series = []

    for serie in self.series:
      series.append(
        {
          'group': serie.label,
          'color': serie.color,
          'value': serie.data[0],
        }
      )

    return series

  def _render_apexcharts(self) -> Any:
    """
    Converts the configuration of the chart to Javascript library ApexCharts.
    """

    series = []
    colors = []
    labels = []

    for serie in self.series:
      series.append(serie.data[0])
      colors.append(serie.color)
      labels.append(serie.label)

    config = {
      'series': series,
      'colors': colors,
      'labels': labels,
      'title': {
        'text': self.title,
        'align': self.align.value,
        'style': {'fontFamily': 'Fira Sans Condensed', 'fontSize': '20px', 'fontWeight': 'normal'},
      },
      'chart': {
        'type': 'radialBar',
        'animations': {'enabled': False},
        'toolbar': {'show': False},
        'zoom': {'enabled': False},
      },
      'dataLabels': {'enabled': True},
    }

    return config
