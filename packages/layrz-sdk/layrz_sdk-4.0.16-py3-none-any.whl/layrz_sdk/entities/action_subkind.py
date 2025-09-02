"""Action sub kind"""

from enum import StrEnum
from typing import Self


class ActionSubKind(StrEnum):
  """
  Action sub kind definition
  """

  UNUSED = 'UNUSED'
  """ Unused action sub kind, not linked to any action kind """

  LINK = 'LINK'
  """ Link asset or user to the parent asset """

  UNLINK = 'UNLINK'
  """ Unlink asset or user from the parent asset """

  BOTH = 'BOTH'
  """ Link and unlink asset or user to the parent asset """

  def __str__(self: Self) -> str:
    """Readable property"""
    return self.name

  def __repr__(self: Self) -> str:
    """Readable property"""
    return f'ActionSubKind.{self.name}'
