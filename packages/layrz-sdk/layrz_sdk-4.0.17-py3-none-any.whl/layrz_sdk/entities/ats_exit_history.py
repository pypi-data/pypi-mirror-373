"""Exit Execution History"""

from datetime import datetime
from typing import Literal

from pydantic import (
  BaseModel,
  ConfigDict,
  Field,
)


class AtsExitExecutionHistory(BaseModel):
  model_config = {
    'json_encoders': {
      datetime: lambda v: v.timestamp(),
    }
  }
  pk: int = Field(description='Primary key of the Exit Execution History', alias='id')

  from_asset_id: int = Field(
    description='ID of the asset from which the exit is initiated',
  )
  to_asset_id: int = Field(
    description='ID of the asset to which the exit is directed',
  )

  status: Literal['PENDING', 'FAILED', 'SUCCESS'] = Field(default='PENDING')

  from_app: Literal['ATSWEB', 'ATSMOBILE', 'NFC'] | None = Field(
    default=None,
    description='Application from which the exit was initiated',
  )

  error_response: str | None = Field(default=None, description='Error response received during the exit process')
  generated_by_id: int = Field(description='ID of the user or system that initiated the exit')
  queue_id: int | None = Field(default=None, description='ID of the queue associated with the exit')
  to_asset_mileage: float | None = Field(default=None, description='Mileage of the asset to which the exit is directed')

  created_at: datetime = Field(description='Timestamp when the exit was created')
  updated_at: datetime = Field(description='Timestamp when the exit was last updated')
  model_config = ConfigDict(from_attributes=True)
