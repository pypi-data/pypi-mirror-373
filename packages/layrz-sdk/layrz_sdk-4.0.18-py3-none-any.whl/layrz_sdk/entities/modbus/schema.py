from enum import StrEnum


class ModbusSchema(StrEnum):
  """Modbus schema enumeration"""

  SINGLE = 'SINGLE'
  """ Defines a single Modbus request. """
  MULTIPLE = 'MULTIPLE'
  """ Defines multiple Modbus requests. """
