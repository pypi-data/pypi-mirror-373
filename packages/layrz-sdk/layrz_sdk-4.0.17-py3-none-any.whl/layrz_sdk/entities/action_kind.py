"""Action kind"""

from enum import StrEnum
from typing import Self


class ActionKind(StrEnum):
  """
  Action kind definition
  """

  LINK = 'LINK'
  """ Links or unkinks an asset or device to the parent asset """

  PERFORM_OPERATION = 'PERFORMOPERATION'
  """ Performs an operation over the activation """

  SEND_TO_OUTBOUND = 'SENDTOOMEGA'
  """ Send to Outbound services """

  PERFORM_COMMAND = 'PERFORMCOMMAND'
  """ Performs a command over the activation """

  TO_MONITOR_CENTER = 'TOMONITORCENTER'
  """ Sends the activation to the monitor center """

  TO_CHECKPOINT_ROUTE = 'TOCHECKPOINTROUTE'
  """ Sends the activation to the checkpoint route """

  CORE_PROCESS = 'COREPROCESS'
  """ Core process of the action """

  CREATE_GEOFENCE = 'CREATE_GEOFENCE'
  """ Creates a geofence for the action """

  PURCHASE_ORDER_STATUS = 'PURCHASEORDERSTATUS'
  """ Updates the purchase order status for the action """

  EXCHANGE = 'EXCHANGE'
  """ Sends the activation to the exchange service """

  def __str__(self: Self) -> str:
    """Readable property"""
    return self.name

  def __repr__(self: Self) -> str:
    """Readable property"""
    return f'ActionKind.{self.name}'
