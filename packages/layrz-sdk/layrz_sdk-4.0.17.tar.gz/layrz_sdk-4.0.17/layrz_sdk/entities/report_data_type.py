from enum import StrEnum
from typing import Self


class ReportDataType(StrEnum):
  """
  Report date type
  """

  STR = 'str'
  INT = 'int'
  FLOAT = 'float'
  DATETIME = 'datetime'
  BOOL = 'bool'
  CURRENCY = 'currency'

  def __str__(self: Self) -> str:
    """Readable property"""
    return self.name

  def __repr__(self: Self) -> str:
    """Readable property"""
    return f'ReportDataType.{self.value}'
