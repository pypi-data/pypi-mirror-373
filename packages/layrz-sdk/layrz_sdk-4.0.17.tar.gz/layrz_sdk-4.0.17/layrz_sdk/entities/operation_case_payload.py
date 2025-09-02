"""Operation case payload entity"""

from datetime import datetime, timedelta
from typing import Any

from pydantic import BaseModel, Field, field_validator

from layrz_sdk.constants import UTC
from layrz_sdk.entities.trigger import Trigger


class OperationCaseCommentPayload(BaseModel):
  """Operation case comment payload entity"""

  pk: int = Field(..., description='Defines the primary key of the operation case comment', alias='id')
  user: str = Field(..., description='Defines the user who created the operation case comment')
  content: str = Field(..., description='Defines the content of the operation case comment')
  created_at: datetime = Field(
    default_factory=lambda: datetime.now(UTC),
    description='Defines the creation date of the operation case comment',
  )


class OperationCasePayload(BaseModel):
  """Operation case payload entity"""

  model_config = {
    'json_encoders': {
      timedelta: lambda v: v.total_seconds(),
      datetime: lambda v: v.timestamp(),
      Trigger: lambda v: v.model_dump(by_alias=True, exclude_none=True),
    },
  }

  pk: int = Field(description='Defines the primary key of the operation case payload', alias='id')
  created_at: datetime = Field(
    default_factory=lambda: datetime.now(UTC),
    description='Defines the creation date of the operation case payload',
  )
  updated_at: datetime = Field(
    default_factory=lambda: datetime.now(UTC),
    description='Defines the last update date of the operation case payload',
  )

  trigger: Trigger = Field(
    ...,
    description='Defines the trigger associated with the operation case payload',
  )

  @field_validator('trigger', mode='before')
  def serialize_trigger(cls, value: Any) -> Trigger:
    """Serialize trigger to a dictionary"""
    if isinstance(value, Trigger):
      return Trigger(
        id=value.pk,
        name=value.name,
        code=value.code,
      )
    if isinstance(value, dict):
      return Trigger.model_validate(value)

    raise ValueError('Trigger must be an instance of Trigger or a dictionary')

  file_id: int | None = Field(
    default=None,
    description='Defines the file ID associated with the operation case payload',
  )

  file_created_at: datetime | None = Field(
    default=None,
    description='Defines the creation date of the file associated with the operation case payload',
  )

  comment: OperationCaseCommentPayload | None = Field(
    default=None,
    description='Defines the comment associated with the operation case payload',
  )
