from pydantic import BaseModel, Field

from .parameter import ModbusParameter


class ModbusConfig(BaseModel):
  port_id: str = Field(
    ...,
    description='Port ID for Modbus communication',
  )
  is_enabled: bool = Field(
    default=False,
    description='Flag to enable or disable Modbus communication',
  )

  parameters: list[ModbusParameter] = Field(
    default_factory=list,
    description='List of Modbus parameters to be used in communication',
  )
