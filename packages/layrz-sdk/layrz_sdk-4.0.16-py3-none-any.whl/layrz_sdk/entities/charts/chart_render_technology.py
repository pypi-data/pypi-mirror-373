"""Chart rendering technology / library"""

from enum import StrEnum
from typing import Self


class ChartRenderTechnology(StrEnum):
  """
  Chart Alignment
  """

  CANVAS_JS = 'CANVAS_JS'
  GRAPHIC = 'GRAPHIC'
  SYNCFUSION_FLUTTER_CHARTS = 'SYNCFUSION_FLUTTER_CHARTS'
  FLUTTER_MAP = 'FLUTTER_MAP'
  APEX_CHARTS = 'APEX_CHARTS'
  FLUTTER = 'FLUTTER'

  def __str__(self: Self) -> str:
    """Readable property"""
    return self.name

  def __repr__(self: Self) -> str:
    """Readable property"""
    return f'ChartRenderTechnology.{self.value}'
