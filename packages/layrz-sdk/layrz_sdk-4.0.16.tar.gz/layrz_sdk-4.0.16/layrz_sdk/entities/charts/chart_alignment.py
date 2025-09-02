"""Chart alignment"""

from enum import StrEnum
from typing import Self


class ChartAlignment(StrEnum):
  """
  Chart Alignment
  """

  CENTER = 'center'
  LEFT = 'left'
  RIGHT = 'right'

  def __str__(self: Self) -> str:
    """Readable property"""
    return self.name

  def __repr__(self: Self) -> str:
    """Readable property"""
    return f'ChartAlignment.{self.name}'
