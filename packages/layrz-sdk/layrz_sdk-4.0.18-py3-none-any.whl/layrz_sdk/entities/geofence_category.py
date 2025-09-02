"""Geofence category"""

from enum import StrEnum
from typing import Self


class GeofenceCategory(StrEnum):
  """
  Geofence category definition
  """

  NONE = 'NONE'
  """ Classic or uncategorized geofence """

  CUSTOM = 'CUSTOM'
  """ Geofence with non-standard category """

  ADMINISTRATIVE = 'ADMINISTRATIVE'
  """ Geofence as administrative area """

  CUSTOMER = 'CUSTOMER'
  """ Geofence as customer location """

  PROSPECT = 'PROSPECT'
  """ Similar to customer location but not yet a customer """

  OTHER = 'OTHER'
  """ Other geofence category """

  POLYGON = 'POLYGON'
  """ Geofence as search geozone """

  LEAD = 'LEAD'
  """ Geofence as lead location, not yet a prospect or customer """

  def __str__(self: Self) -> str:
    """Readable property"""
    return self.name

  def __repr__(self: Self) -> str:
    """Readable property"""
    return f'GeofenceCategory.{self.name}'
