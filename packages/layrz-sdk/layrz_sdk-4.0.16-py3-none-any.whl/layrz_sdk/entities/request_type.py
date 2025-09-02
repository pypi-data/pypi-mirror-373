"""Http Operation Type"""

from enum import StrEnum
from typing import Self


class HttpRequestType(StrEnum):
  """
  Http Operation Type definition
  """

  GET = 'GET'
  POST = 'POST'
  PUT = 'PUT'
  PATCH = 'PATCH'

  def __str__(self: Self) -> str:
    """Readable property"""
    return self.name

  def __repr__(self: Self) -> str:
    """Readable property"""
    return f'HttpRequestType.{self.name}'
