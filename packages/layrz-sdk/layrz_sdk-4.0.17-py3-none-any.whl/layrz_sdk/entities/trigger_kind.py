"""Asset Operation Mode"""

from enum import StrEnum
from typing import Self


class TriggerKind(StrEnum):
  """
  Trigger Kind definition
  """

  PRESENCE_IN_GEOFENCE = 'PRESENCEINGEOFENCE'
  EXACT_TIME = 'EXACTTIME'
  FORMULA = 'FORMULA'
  AUTHENTICATION = 'AUTHENTICATION'
  PYTHON_SCRIPT = 'PYTHONSCRIPT'
  CASES_CHANGES = 'CASES_CHANGES'
  BHS_SPEEDING = 'BHS_SPEEDING'
  BHS_PRESENCE = 'BHS_PRESENCE'
  MANUAL_ACTION = 'MANUAL_ACTION'
  NESTED = 'NESTED_TRIGGERS'

  def __str__(self: Self) -> str:
    """Readable property"""
    return self.name

  def __repr__(self: Self) -> str:
    """Readable property"""
    return f'TriggerKind.{self.name}'


class TriggerGeofenceKind(StrEnum):
  """
  Geofence Kind definition
  """

  ENTRANCE = 'ENTRANCE'
  EXIT = 'EXIT'
  BOTH = 'BOTH'

  def __str__(self: Self) -> str:
    """Readable property"""
    return self.name

  def __repr__(self: Self) -> str:
    """Readable property"""
    return f'GeofenceKind.{self.name}'


class TriggerCaseKind(StrEnum):
  """
  Case Kind definition
  """

  ON_FOLLOW = 'ON_FOLLOW'
  ON_CLOSE = 'ON_CLOSE'
  ON_DISMISS = 'ON_DISMISS'
  ON_COMMENT_PATTERN = 'ON_COMMENT_PATTERN'

  def __str__(self: Self) -> str:
    """Readable property"""
    return self.name

  def __repr__(self: Self) -> str:
    """Readable property"""
    return f'TriggerCaseKind.{self.name}'


class TriggerCommentPattern(StrEnum):
  """
  Comment Pattern definition
  """

  STARTS_WITH = 'STARTS_WITH'
  ENDS_WITH = 'ENDS_WITH'
  CONTAINS = 'CONTAINS'

  def __str__(self: Self) -> str:
    """Readable property"""
    return self.name

  def __repr__(self: Self) -> str:
    """Readable property"""
    return f'TriggerCommentPattern.{self.name}'
