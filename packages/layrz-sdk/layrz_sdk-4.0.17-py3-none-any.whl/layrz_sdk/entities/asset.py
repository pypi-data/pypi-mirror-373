"""Asset Entity"""

from typing import Any, Self

from pydantic import BaseModel, Field, field_validator, model_validator

from .asset_contact import AssetContact
from .asset_operation_mode import AssetOperationMode
from .custom_field import CustomField
from .device import Device
from .sensor import Sensor
from .static_position import StaticPosition


class Asset(BaseModel):
  """Asset entity definition"""

  model_config = {
    'json_encoders': {
      AssetOperationMode: lambda v: v.value,
    }
  }

  pk: int = Field(description='Defines the primary key of the asset', alias='id')
  name: str = Field(description='Defines the name of the asset')
  vin: str | None = Field(
    default=None,
    description='Defines the serial number of the asset, may be an VIN, or any other unique identifier',
  )
  plate: str | None = Field(default=None, description='Defines the plate number of the asset')
  kind_id: int | None = Field(description='Defines the type of the asset', default=None)
  operation_mode: AssetOperationMode = Field(description='Defines the operation mode of the asset')
  sensors: list[Sensor] = Field(default_factory=list, description='Defines the list of sensors of the asset')
  custom_fields: list[CustomField] = Field(
    default_factory=list, description='Defines the list of custom fields of the asset'
  )
  devices: list[Device] = Field(default_factory=list, description='Defines the list of devices of the asset')
  children: list[Self] = Field(default_factory=list, description='Defines the list of children of the asset')

  static_position: StaticPosition | None = Field(
    default=None,
    description='Static position of the asset',
  )

  @field_validator('static_position', mode='before')
  def _validate_static_position(cls: Self, value: Any) -> StaticPosition | None:
    """Validate static position"""
    if isinstance(value, dict):
      try:
        return StaticPosition.model_validate(value)
      except Exception:
        return None

    if isinstance(value, StaticPosition):
      return value

    return None

  points: list[StaticPosition] = Field(
    default_factory=list,
    description='List of static positions for the asset. The altitude of StaticPosition is not used in this case.',
  )

  primary_id: int | None = Field(
    default=None,
    description='Defines the primary device ID of the asset',
  )

  @model_validator(mode='before')
  def _validate_model(cls: Self, data: dict[str, Any]) -> dict[str, Any]:
    """Validate model"""
    operation_mode: str | None = data.get('operation_mode')
    if operation_mode == AssetOperationMode.ASSETMULTIPLE.name:
      data['devices'] = []

    else:
      data['children'] = []

    return data

  @property
  def primary(self: Self) -> Device | None:
    """Get primary device"""
    if self.operation_mode not in [AssetOperationMode.SINGLE, AssetOperationMode.MULTIPLE]:
      return None

    for device in self.devices:
      if device.is_primary:
        return device

    return None

  contacts: list[AssetContact] = Field(
    default_factory=list,
    description='Defines the list of contacts of the asset, used for notifications',
  )

  owner_id: int | None = Field(
    default=None,
    description='Owner ID',
  )

  @property
  def asset_type(self: Self) -> int | None:
    """Get asset type"""
    return self.kind_id

  partition_number: int | None = Field(
    default=None,
    description='Partition number assigned for this Asset, if is None, will be auto-assigned by the system',
  )
