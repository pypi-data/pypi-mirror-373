"""Text alignment"""

from enum import StrEnum
from typing import Self


class TextAlignment(StrEnum):
  """Text alignment enum definition"""

  CENTER = 'center'
  LEFT = 'left'
  RIGHT = 'right'
  JUSTIFY = 'justify'

  def __str__(self: Self) -> str:
    """Readable property"""
    return self.name

  def __repr__(self: Self) -> str:
    """Readable property"""
    return f'TextAlignment.{self.value}'
