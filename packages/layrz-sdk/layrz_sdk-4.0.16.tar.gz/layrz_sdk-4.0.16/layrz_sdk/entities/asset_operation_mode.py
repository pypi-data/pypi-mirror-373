"""Asset Operation Mode"""

from enum import StrEnum
from typing import Self


class AssetOperationMode(StrEnum):
  """
  Asset Operation mode definition
  It's an enum of the operation mode of the asset.
  """

  SINGLE = 'SINGLE'
  MULTIPLE = 'MULTIPLE'
  ASSETMULTIPLE = 'ASSETMULTIPLE'
  DISCONNECTED = 'DISCONNECTED'
  STATIC = 'STATIC'
  ZONE = 'ZONE'

  def __str__(self: Self) -> str:
    """Readable property"""
    return self.name

  def __repr__(self: Self) -> str:
    """Readable property"""
    return f'AssetOperationMode.{self.name}'
