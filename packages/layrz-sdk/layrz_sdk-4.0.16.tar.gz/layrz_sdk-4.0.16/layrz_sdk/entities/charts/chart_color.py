"""Chart alignment"""

from enum import StrEnum
from typing import Self


class ChartColor(StrEnum):
  """Chart color list, ideal to use to colorize the series"""

  RED = '#F44336'
  BLUE = '#2196F3'
  GREEN = '#4CAF50'
  PURPLE = '#9C27B0'
  ORANGE = '#FF9800'
  PINK = '#E91E63'
  TEAL = '#009688'
  AMBER = '#FFC107'
  CYAN = '#00BCD4'
  INDIGO = '#3F51B5'
  LIME = '#CDDC39'

  def __str__(self: Self) -> str:
    """Readable property"""
    return self.name

  def __repr__(self: Self) -> str:
    """Readable property"""
    return f'ChartColor.{self.name}'

  @staticmethod
  def get_colors() -> list[str]:
    """Get a color from the list"""
    return [color.value for color in ChartColor]


def get_color_list() -> list[str]:
  """Get all colors"""
  return ChartColor.get_colors()
