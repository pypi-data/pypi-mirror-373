"""Platform"""

from enum import StrEnum
from typing import Self


class Platform(StrEnum):
  """
  Platform definition
  """

  WEB = 'WEB'
  """ Web browser """

  ANDROID = 'ANDROID'
  """ Google Android """

  IOS = 'IOS'
  """ Apple iOS """

  WINDOWS = 'WINDOWS'
  """ Microsoft Windows """

  MACOS = 'MACOS'
  """ Apple MacOS """

  LINUX = 'LINUX'
  """ GNU/Linux """

  LAYRZ_OS = 'LAYRZ_OS'
  """ Layrz OS for embedding systems """

  def __str__(self: Self) -> str:
    """Readable property"""
    return self.name

  def __repr__(self: Self) -> str:
    """Readable property"""
    return f'Platform.{self.name}'
