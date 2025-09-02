from typing import Any

from pydantic import BaseModel, Field, field_validator

from .schema import ModbusSchema


class ModbusParameter(BaseModel):
  """Modbus parameter model"""

  schema_: ModbusSchema = Field(
    ...,
    description='Modbus schema',
    alias='schema',
  )

  split_each: int = Field(
    ...,
    description='Number of bytes to split each Modbus parameter',
  )

  @field_validator('split_each', mode='before')
  def validate_split_each(cls, value: Any) -> int:
    """Validate and convert split_each to integer."""
    if isinstance(value, int):
      return value

    if isinstance(value, str):
      try:
        return int(value)
      except ValueError as e:
        raise ValueError(f'Invalid Modbus split_each value: {value}') from e

    raise ValueError(f'Invalid Modbus split_each type: {type(value)}')

  data_length: int = Field(
    ...,
    description='Length of data for the Modbus parameter, from Hexadecimal representation',
  )

  @field_validator('data_length', mode='before')
  def validate_data_length(cls, value: Any) -> int:
    """Validate and convert data_length to integer."""
    if isinstance(value, int):
      return value

    if isinstance(value, str):
      try:
        return int(value, 16)  # Convert from hexadecimal string to integer
      except ValueError as e:
        raise ValueError(f'Invalid Modbus data_length value: {value}') from e

    raise ValueError(f'Invalid Modbus data_length type: {type(value)}')

  data_address: int = Field(
    ...,
    description='Address of the Modbus parameter, from Hexadecimal representation',
  )

  @field_validator('data_address', mode='before')
  def validate_data_address(cls, value: Any) -> int:
    """Validate and convert data_address to integer."""
    if isinstance(value, int):
      return value

    if isinstance(value, str):
      try:
        return int(value, 16)  # Convert from hexadecimal string to integer
      except ValueError as e:
        raise ValueError(f'Invalid Modbus data_address value: {value}') from e

    raise ValueError(f'Invalid Modbus data_address type: {type(value)}')

  function_code: int = Field(
    ...,
    description='Function code for the Modbus parameter',
  )

  @field_validator('function_code', mode='before')
  def validate_function_code(cls, value: Any) -> int:
    """Validate and convert function_code to integer."""
    if isinstance(value, int):
      return value

    if isinstance(value, str):
      try:
        return int(value, 16)  # Convert from hexadecimal string to integer
      except ValueError as e:
        raise ValueError(f'Invalid Modbus function_code value: {value}') from e

    raise ValueError(f'Invalid Modbus function_code type: {type(value)}')

  controller_address: int = Field(
    ...,
    description='Controller address for the Modbus parameter',
  )

  @field_validator('controller_address', mode='before')
  def validate_controller_address(cls, value: Any) -> int:
    """Validate and convert controller_address to integer."""
    if isinstance(value, int):
      return value

    if isinstance(value, str):
      try:
        return int(value, 16)  # Convert from hexadecimal string to integer
      except ValueError as e:
        raise ValueError(f'Invalid Modbus controller_address value: {value}') from e

    raise ValueError(f'Invalid Modbus controller_address type: {type(value)}')
