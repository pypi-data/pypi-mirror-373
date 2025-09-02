from enum import StrEnum


class ModbusStatus(StrEnum):
  """Modbus schema enumeration"""

  PENDING = 'PENDING'
  """ Defines the pending state, indicating that the request is waiting to be processed. """
  WAITING_FOR_SEND = 'WAITING_FOR_SEND'
  """ Indicates that the request is ready to be sent but has not yet been dispatched. """
  SENT = 'SENT'
  """ Indicates that the request has been sent to the device. """
  ACK_RECEIVED = 'ACK_RECEIVED'
  """ Indicates that an acknowledgment has been received from the device. """
  CANCELLED = 'CANCELLED'
  """ Indicates that the request has been cancelled. """
