"""Map chart"""

from typing import Any, Optional, Self, Tuple

from pydantic import BaseModel, Field

from .chart_render_technology import ChartRenderTechnology
from .map_center_type import MapCenterType
from .map_point import MapPoint


class MapChart(BaseModel):
  """Map chart configuration"""

  points: list[MapPoint] = Field(description='Points of the chart', default_factory=list)
  title: str = Field(description='Title of the chart', default='Chart')
  center: MapCenterType = Field(description='Center of the chart', default=MapCenterType.CONTAIN)
  center_latlng: Optional[list[float]] = Field(description='Center of the chart in latlng format', default=None)

  def render(self: Self, technology: ChartRenderTechnology = ChartRenderTechnology.FLUTTER_MAP) -> dict[str, Any]:
    """
    Render chart to a graphic Library.

    :param technology: The technology to use to render the chart.
    :type technology: ChartRenderTechnology

    :return: The configuration of the chart.
    :rtype: dict[str, Any]
    """
    if technology == ChartRenderTechnology.FLUTTER_MAP:
      return {
        'library': 'FLUTTER_MAP',
        'chart': 'MAP',
        'configuration': self._render_flutter_map(),
      }

    return {
      'library': 'FLUTTER',
      'chart': 'TEXT',
      'configuration': [f'Unsupported {technology}'],
    }

  def _render_flutter_map(self: Self) -> dict[str, Any]:
    """
    Converts the configuration to the chart to Flutter Map engine.
    """
    points = []

    for point in self.points:
      points.append(
        {
          'label': point.label,
          'color': point.color,
          'latlng': (point.latitude, point.longitude),
        }
      )

    center = 'CONTAIN'

    if self.center == MapCenterType.FIXED:
      center = 'FIXED'

    config: dict[str, Any] = {
      'points': points,
      'center': center,
    }

    if self.center == MapCenterType.FIXED:
      if self.center_latlng is not None:
        config['centerLatLng'] = self.center_latlng
      else:
        config['center'] = 'CONTAIN'

    return config

  def _render_leaflet(self: Self) -> dict[str, Any]:
    """
    Converts the configuration of the chart to Leaflet map engine.
    """
    points = []

    for point in self.points:
      points.append({'label': point.label, 'color': point.color, 'latlng': (point.latitude, point.longitude)})

    center = 'CONTAIN'

    if self.center == MapCenterType.FIXED:
      center = 'FIXED'

    config: dict[str, Any] = {
      'points': points,
      'title': self.title,
      'center': center,
    }

    if self.center == MapCenterType.FIXED:
      if self.center_latlng is not None:
        config['centerLatLng'] = self.center_latlng
      else:
        config['center'] = 'CONTAIN'

    return config
