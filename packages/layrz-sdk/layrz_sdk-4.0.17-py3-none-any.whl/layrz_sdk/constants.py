"""Constants"""

from zoneinfo import ZoneInfo

UTC = ZoneInfo('UTC')
""" UTC timezone constant for use in datetime fields. """


REJECTED_KEYS = (
  'timestamp',
  'ident',
  'server.timestamp',
  'protocol.id',
  'channel.id',
  'device.name',
  'device.id',
  'device.type.id',
)
""" Defines the ignored raw keys from a telemetry object """
