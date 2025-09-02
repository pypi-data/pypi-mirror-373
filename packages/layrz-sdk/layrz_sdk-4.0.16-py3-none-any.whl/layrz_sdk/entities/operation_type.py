"""Operation type"""

from enum import StrEnum
from typing import Self


class OperationType(StrEnum):
  """
  Operation type definition
  """

  WEBHOOKS = 'WEBHOOKS'
  """ All the operations by http request """

  SEND_EMAIL = 'SENDEMAIL'
  """ Send notifications emails """

  REGISTER_ON_ASSET = 'ACTIVATEASSET'
  """ Register an event for the asset """

  IN_APP_NOTIFICATION = 'INAPPNOTIFICATION'
  """ Send notifications inside the app """

  TWILIO = 'TWILIO'
  """ Send notifications using Twilio """

  MOBILE_POPUP_NOTIFICATION = 'MOBILE_POPUP_NOTIFICATION'
  """ Send notifications using Push Notification (Mobile) """

  BHS_PUSH = 'BHS_PUSH'
  """ Send notifications using Firebase Push Notifications of Brickhouse Tracking Platform """

  def __str__(self: Self) -> str:
    """Readable property"""
    return self.name

  def __repr__(self: Self) -> str:
    """Readable property"""
    return f'OperationType.{self.name}'
