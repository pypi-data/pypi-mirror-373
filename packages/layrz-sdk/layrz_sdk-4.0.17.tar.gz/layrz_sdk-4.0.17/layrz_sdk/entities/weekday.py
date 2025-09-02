from enum import StrEnum
from typing import Self


class Weekday(StrEnum):
  """
  Weekday definition
  """

  MONDAY = 'MON'
  TUESDAY = 'TUE'
  WEDNESDAY = 'WED'
  THURSDAY = 'THU'
  FRIDAY = 'FRI'
  SATURDAY = 'SAT'
  SUNDAY = 'SUN'

  def __str__(self: Self) -> str:
    """Readable property"""
    return self.name

  def __repr__(self: Self) -> str:
    """Readable property"""
    return f'Weekday.{self.name}'
