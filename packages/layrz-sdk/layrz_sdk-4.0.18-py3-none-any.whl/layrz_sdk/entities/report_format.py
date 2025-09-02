"""Report formats"""

from enum import StrEnum
from typing import Self


class ReportFormat(StrEnum):
  """
  Report format definition.
  """

  MICROSOFT_EXCEL = 'MICROSOFT_EXCEL'
  JSON = 'JSON'
  PDF = 'PDF'

  def __str__(self: Self) -> str:
    """Readable property"""
    return self.name

  def __repr__(self: Self) -> str:
    """Readable property"""
    return f'ReportFormat.{self.value}'
