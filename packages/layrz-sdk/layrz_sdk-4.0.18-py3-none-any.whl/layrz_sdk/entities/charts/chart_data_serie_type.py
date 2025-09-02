"""Chart Serie type"""

from enum import StrEnum
from typing import Self


class ChartDataSerieType(StrEnum):
  """
  Chart data serie type
  """

  NONE = 'None'
  LINE = 'line'
  AREA = 'area'
  SCATTER = 'scatter'

  def __str__(self: Self) -> str:
    """Readable property"""
    return self.name

  def __repr__(self: Self) -> str:
    """Readable property"""
    return f'ChartDataSerieType.{self.name}'
