"""Broadcast result Status"""

from enum import StrEnum
from typing import Self


class BroadcastStatus(StrEnum):
  """Broadcast result status"""

  OK = 'OK'
  BAD_REQUEST = 'BADREQUEST'
  INTERNAL_ERROR = 'INTERNALERROR'
  UNAUTHORIZED = 'UNAUTHORIZED'
  UNPROCESSABLE = 'UNPROCESSABLE'
  DISCONNECTED = 'DISCONNECTED'

  def __str__(self: Self) -> str:
    """Readable property"""
    return self.name

  def __repr__(self: Self) -> str:
    """Readable property"""
    return f'BroadcastStatus.{self.name}'
