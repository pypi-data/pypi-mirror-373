"""Device entitiy"""

from typing import Any

from pydantic import BaseModel, Field, field_validator

from .modbus import ModbusConfig


class Device(BaseModel):
  """Device entity"""

  pk: int = Field(description='Defines the primary key of the device', alias='id')
  name: str = Field(description='Defines the name of the device')
  ident: str = Field(description='Defines the identifier of the device')
  protocol_id: int | None = Field(
    description='Defines the protocol ID of the device',
    default=None,
  )
  protocol: str = Field(description='Defines the protocol of the device')
  is_primary: bool = Field(default=False, description='Defines if the device is the primary device')

  @field_validator('is_primary', mode='before')
  def validate_is_primary(cls, value: Any) -> bool:
    """Validate that is_primary is a boolean value."""
    if isinstance(value, str):
      return value.lower() in ('true', '1', 'yes')
    if isinstance(value, bool):
      return value
    return False

  modbus: ModbusConfig | None = Field(default=None, description='Modbus configuration')
