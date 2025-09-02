"""Line chart"""

import logging
from typing import Any, Self

from pydantic import BaseModel, Field

from .axis_config import AxisConfig
from .chart_alignment import ChartAlignment
from .chart_data_serie import ChartDataSerie
from .chart_data_serie_type import ChartDataSerieType
from .chart_data_type import ChartDataType
from .chart_render_technology import ChartRenderTechnology

log = logging.getLogger(__name__)


class LineChart(BaseModel):
  """Line chart configuration"""

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

  def render(self: Self, technology: ChartRenderTechnology) -> dict[str, Any]:
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
        'chart': 'LINE',
        'configuration': self._render_graphic(),
      }

    if technology == ChartRenderTechnology.SYNCFUSION_FLUTTER_CHARTS:
      return {
        'library': 'SYNCFUSION_FLUTTER_CHARTS',
        'chart': 'LINE',
        'configuration': self._render_syncfusion_flutter_charts(),
      }

    if technology == ChartRenderTechnology.CANVAS_JS:
      return {
        'library': 'CANVASJS',
        'chart': 'LINE',
        'configuration': self._render_canvasjs(),
      }

    return {
      'library': 'FLUTTER',
      'chart': 'TEXT',
      'configuration': [f'Unsupported {technology}'],
    }

  def _render_syncfusion_flutter_charts(self: Self) -> dict[str, Any]:
    """
    Converts the configuration of the chart to a Flutter library syncfusion_flutter_charts.
    """
    series = []

    for serie in self.y_axis:
      if serie.serie_type not in [ChartDataSerieType.LINE, ChartDataSerieType.AREA]:
        log.warning('Serie type not supported: %s', serie.serie_type)
        continue

      points = []

      for i, value in enumerate(self.x_axis.data):
        x_value = value.timestamp() if self.x_axis.data_type == ChartDataType.DATETIME else value
        if not isinstance(x_value, (int, float)):
          continue

        y_value = serie.data[i]
        if isinstance(y_value, bool):
          if y_value:
            y_value = 1
          else:
            y_value = 0

        if not isinstance(y_value, (int, float)):
          log.debug("Value isn't a number: %s", y_value)
          continue

        points.append(
          {
            'xAxis': x_value,
            'yAxis': y_value,
          }
        )

      series.append(
        {
          'color': serie.color,
          'values': points,
          'label': serie.label,
          'type': 'AREA' if serie.serie_type == ChartDataSerieType.AREA else 'LINE',
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
    Converts the configuration of the chart to a Flutter library Graphic.
    """
    series = []

    for serie in self.y_axis:
      if serie.serie_type not in [ChartDataSerieType.LINE, ChartDataSerieType.AREA]:
        continue

      points = []

      for i, value in enumerate(self.x_axis.data):
        points.append(
          {
            'x_axis': {
              'value': value.timestamp() if self.x_axis.data_type == ChartDataType.DATETIME else value,
              'is_datetime': self.x_axis.data_type == ChartDataType.DATETIME,
            },
            'y_axis': serie.data[i],
          }
        )

      series.append(
        {
          'group': serie.label,
          'color': serie.color,
          'dashed': serie.serie_type == ChartDataSerieType.LINE and serie.dashed,
          'type': 'AREA' if serie.serie_type == ChartDataSerieType.AREA else 'LINE',
          'values': points,
        }
      )

    return series

  def _render_canvasjs(self: Self) -> dict[str, Any]:
    """
    Converts the configuration of the chart to Javascript library CanvasJS.
    """
    datasets = []

    for serie in self.y_axis:
      dataset = {
        'type': 'line',
        'name': serie.label,
        'connectNullData': True,
        'nullDataLineDashType': 'solid',
        'showInLegend': True,
        'color': serie.color,
        'markerSize': 3,
      }

      if serie.serie_type != ChartDataSerieType.NONE:
        dataset['type'] = serie.serie_type.value

      if serie.serie_type == ChartDataSerieType.AREA:
        dataset['fillOpacity'] = 0.3

      if self.x_axis.data_type == ChartDataType.DATETIME:
        dataset['xValueType'] = 'dateTime'
        dataset['xValueFormatString'] = 'YYYY-MM-DD HH:mm:ss TT'

      if serie.serie_type == ChartDataSerieType.LINE and serie.dashed:
        dataset['lineDashType'] = 'dash'
        dataset['markerSize'] = 0

      points = []

      if serie.serie_type == ChartDataSerieType.SCATTER:
        for point in serie.data:
          points.append({'x': point.x, 'y': point.y})
      else:
        for i, value in enumerate(self.x_axis.data):
          points.append(
            {
              'x': (value.timestamp() * 1000) if self.x_axis.data_type == ChartDataType.DATETIME else value,
              'y': serie.data[i],
            }
          )

      dataset['dataPoints'] = points
      datasets.append(dataset)

    return {
      'animationEnabled': False,
      'zoomEnabled': True,
      'title': {
        'text': self.title,
        'fontFamily': 'Fira Sans Condensed',
        'fontSize': 20,
        'horizontalAlign': self.align.value,
      },
      'data': datasets,
      'axisX': {
        'title': self.x_axis.label,
        'titleFontFamily': 'Fira Sans Condensed',
        'titleFontSize': 20,
      },
      'toolTip': {'animationEnabled': False, 'shared': True},
      'legend': {'cursor': 'pointer'},
    }


class AreaChart(LineChart):
  """
  Line chart
  Deprecation warning: This class will be removed in the next version. Use LineChart instead.
  """
