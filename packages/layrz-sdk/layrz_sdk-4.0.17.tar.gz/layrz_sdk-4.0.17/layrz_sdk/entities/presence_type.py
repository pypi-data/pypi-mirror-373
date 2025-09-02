from enum import StrEnum
from typing import Self


class PresenceType(StrEnum):
  """Presence type enum"""

  ENTRANCE = 'ENTRANCE'
  EXIT = 'EXIT'

  def __str__(self: Self) -> str:
    """Readable property"""
    return self.name

  def __repr__(self: Self) -> str:
    """Readable property"""
    return f'PresenceType.{self.name}'
