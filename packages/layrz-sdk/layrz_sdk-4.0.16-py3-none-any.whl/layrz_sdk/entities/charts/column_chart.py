"""Column chart"""

from typing import Any, Self

from pydantic import BaseModel, Field

from layrz_sdk.helpers import convert_to_rgba

from .axis_config import AxisConfig
from .chart_alignment import ChartAlignment
from .chart_data_serie import ChartDataSerie
from .chart_data_serie_type import ChartDataSerieType
from .chart_render_technology import ChartRenderTechnology


class ColumnChart(BaseModel):
  """Column chart configuration"""

  x_axis: ChartDataSerie = Field(description='Defines the X Axis of the chart')
  y_axis: list[ChartDataSerie] = Field(description='Defines the Y Axis of the chart', default_factory=list)
  title: str = Field(default='Chart', description='Title of the chart')
  align: ChartAlignment = Field(default=ChartAlignment.CENTER, description='Alignment of the title')
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
  ) -> Any:
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
        'chart': 'COLUMN',
        'configuration': self._render_graphic(),
      }

    if technology == ChartRenderTechnology.SYNCFUSION_FLUTTER_CHARTS:
      return {
        'library': 'SYNCFUSION_FLUTTER_CHARTS',
        'chart': 'COLUMN',
        'configuration': self._render_syncfusion_flutter_charts(),
      }

    if technology == ChartRenderTechnology.APEX_CHARTS:
      return {
        'library': 'APEXCHARTS',
        'chart': 'COLUMN',
        'configuration': self._render_apexcharts(),
      }

    return {
      'library': 'FLUTTER',
      'chart': 'TEXT',
      'configuration': [f'Unsupported {technology}'],
    }

  def _render_syncfusion_flutter_charts(self: Self) -> dict[str, Any]:
    """
    Converts the configuration of the chart to Syncfusion Flutter Charts.
    """
    series = []

    for serie in self.y_axis:
      values = []
      for i, value in enumerate(serie.data):
        x_axis = self.x_axis.data[i]
        values.append({'xAxis': x_axis, 'yAxis': value})

      series.append(
        {
          'label': serie.label,
          'color': serie.color,
          'values': values,
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
    Converts the configuration of the chart to Flutter library graphic.
    """

    series = []

    for serie in self.y_axis:
      for i, value in enumerate(serie.data):
        x_axis = self.x_axis.data[i]
        series.append(
          {
            'label': serie.label,
            'color': serie.color,
            'category': x_axis,
            'value': value,
          }
        )

    return series

  def _render_apexcharts(self: Self) -> dict[str, Any]:
    """
    Converts the configuration of the chart to Javascript library ApexCharts.
    """

    series = []
    colors = []
    stroke: dict[str, Any] = {'width': [], 'dashArray': []}
    markers = []

    for serie in self.y_axis:
      modified_serie: dict[str, Any] = {
        'name': serie.label,
      }
      if serie.serie_type == ChartDataSerieType.SCATTER:
        modified_serie['data'] = [{'x': item.x, 'y': item.y} for item in serie.data]
        modified_serie['type'] = 'scatter'
        stroke['width'].append(0)
        markers.append(10)
      else:
        modified_serie['data'] = [{'x': self.x_axis.data[i], 'y': item} for i, item in enumerate(serie.data)]

        if serie.serie_type is not ChartDataSerieType.NONE:
          modified_serie['type'] = serie.serie_type.value
        else:
          modified_serie['type'] = 'column'

        if serie.dashed and serie.serie_type == ChartDataSerieType.LINE:
          stroke['dashArray'].append(5)
        else:
          stroke['dashArray'].append(0)

        stroke['width'].append(3)
        markers.append(0)

      series.append(modified_serie)

      if serie.serie_type == ChartDataSerieType.AREA:
        color = convert_to_rgba(serie.color)
        colors.append(f'rgba({color[0]}, {color[1]}, {color[2]}, 0.5)')
      else:
        colors.append(serie.color)

    config = {
      'series': series,
      'colors': colors,
      'xaxis': {
        'type': self.x_axis.data_type.value,
        'title': {
          'text': self.x_axis.label,
          'style': {'fontFamily': 'Fira Sans Condensed', 'fontSize': '20px', 'fontWeight': 'normal'},
        },
      },
      'dataLabels': {'enabled': False},
      'title': {
        'text': self.title,
        'align': self.align.value,
        'style': {'fontFamily': 'Fira Sans Condensed', 'fontSize': '20px', 'fontWeight': 'normal'},
      },
      'markers': {'size': markers},
      'fill': {'type': 'solid'},
      'stroke': stroke,
      'chart': {'animations': {'enabled': False}, 'toolbar': {'show': False}, 'zoom': {'enabled': False}},
    }

    return config
