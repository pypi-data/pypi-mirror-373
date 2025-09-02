"""Scatter chart"""

from typing import Any, Self

from pydantic import BaseModel, Field

from .axis_config import AxisConfig
from .chart_alignment import ChartAlignment
from .chart_data_serie_type import ChartDataSerieType
from .chart_render_technology import ChartRenderTechnology
from .scatter_serie import ScatterSerie


class ScatterChart(BaseModel):
  """Scatter chart configuration"""

  series: list[ScatterSerie] = Field(description='List of series to be displayed in the chart', default_factory=list)
  title: str = Field(description='Title of the chart', default='Chart')
  align: ChartAlignment = Field(description='Alignment of the chart', default=ChartAlignment.CENTER)
  x_axis_config: AxisConfig = Field(
    default_factory=lambda: AxisConfig(),
    description='Configuration of the X Axis',
  )
  y_axis_config: AxisConfig = Field(
    default_factory=lambda: AxisConfig(),
    description='Configuration of the Y Axis',
  )

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
        'chart': 'SCATTER',
        'configuration': self._render_graphic(),
      }

    if technology == ChartRenderTechnology.SYNCFUSION_FLUTTER_CHARTS:
      return {
        'library': 'SYNCFUSION_FLUTTER_CHARTS',
        'chart': 'SCATTER',
        'configuration': self._render_syncfusion_flutter_charts(),
      }

    if technology == ChartRenderTechnology.APEX_CHARTS:
      return {
        'library': 'APEXCHARTS',
        'chart': 'SCATTER',
        'configuration': self._render_apexcharts(),
      }

    return {
      'library': 'FLUTTER',
      'chart': 'TEXT',
      'configuration': [f'Unsupported {technology}'],
    }

  def _render_syncfusion_flutter_charts(self: Self) -> dict[str, Any]:
    """
    Converts the configuration of the chart to Flutter library Graphic.
    """
    series = []
    for serie in self.series:
      data = []

      type_serie = 'SCATTER'
      if serie.serie_type == ChartDataSerieType.SCATTER:
        type_serie = 'SCATTER'
      elif serie.serie_type == ChartDataSerieType.LINE:
        type_serie = 'LINE'
      elif serie.serie_type == ChartDataSerieType.AREA:
        type_serie = 'AREA'
      else:
        continue

      for item in serie.data:
        if not isinstance(item.x, (int, float)):
          continue
        if not isinstance(item.y, (int, float)):
          continue

        data.append(
          {
            'xAxis': item.x,
            'yAxis': item.y,
          }
        )

      series.append(
        {
          'label': serie.label,
          'color': serie.color,
          'values': data,
          'type': type_serie,
        }
      )

    return {
      'series': series,
      'xAxis': {
        'label': self.x_axis_config.label,
        'measureUnit': self.x_axis_config.measure_unit,
        'dataType': self.x_axis_config.data_type.value,
        'minValue': self.x_axis_config.min_value,
        'maxValue': self.x_axis_config.max_value,
      },
      'yAxis': {
        'label': self.y_axis_config.label,
        'measureUnit': self.y_axis_config.measure_unit,
        'dataType': self.y_axis_config.data_type.value,
        'minValue': self.y_axis_config.min_value,
        'maxValue': self.y_axis_config.max_value,
      },
    }

  def _render_graphic(self: Self) -> list[dict[str, Any]]:
    """
    Converts the configuration of the chart to Flutter library Graphic.
    """
    series = []
    for serie in self.series:
      data = []

      type_serie = 'SCATTER'
      if serie.serie_type == ChartDataSerieType.SCATTER:
        type_serie = 'SCATTER'
      elif serie.serie_type == ChartDataSerieType.LINE:
        type_serie = 'LINE'
      elif serie.serie_type == ChartDataSerieType.AREA:
        type_serie = 'AREA'
      else:
        continue

      for item in serie.data:
        data.append(
          {
            'x_axis': item.x,
            'y_axis': item.y,
          }
        )

      series.append(
        {
          'group': serie.label,
          'color': serie.color,
          'values': data,
          'type': type_serie,
        }
      )

    return series

  def _render_apexcharts(self: Self) -> dict[str, Any]:
    """
    Converts the configuration of the chart to Javascript library ApexCharts.
    """

    series = []
    colors = []

    for serie in self.series:
      data = []

      for item in serie.data:
        data.append([item.x, item.y])

      series.append(
        {
          'name': serie.label,
          'data': data,
          'type': serie.serie_type.value,
        }
      )
      colors.append(serie.color)

    config = {
      'series': series,
      'colors': colors,
      'title': {
        'text': self.title,
        'align': self.align.value,
        'style': {'fontFamily': 'Fira Sans Condensed', 'fontSize': '20px', 'fontWeight': 'normal'},
      },
      'chart': {
        'type': 'scatter',
        'animations': {'enabled': False},
        'toolbar': {'show': False},
        'zoom': {'enabled': False},
      },
      'dataLabels': {'enabled': True},
    }

    return config
