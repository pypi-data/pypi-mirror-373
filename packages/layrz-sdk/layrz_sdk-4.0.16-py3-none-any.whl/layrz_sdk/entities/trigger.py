"""Trigger entity"""

from datetime import time, timedelta
from typing import Any

from pydantic import BaseModel, Field, field_validator

from .trigger_kind import TriggerCaseKind, TriggerCommentPattern, TriggerGeofenceKind, TriggerKind
from .weekday import Weekday


class Trigger(BaseModel):
  """Trigger entity"""

  model_config = {
    'json_encoders': {
      timedelta: lambda v: v.total_seconds(),
      TriggerCaseKind: lambda v: v.value,
      TriggerGeofenceKind: lambda v: v.value,
      TriggerKind: lambda v: v.value,
      TriggerCommentPattern: lambda v: v.value,
      Weekday: lambda v: v.value,
    },
  }

  pk: int = Field(description='Defines the primary key of the trigger', alias='id')
  name: str = Field(description='Defines the name of the trigger')
  code: str = Field(description='Defines the code of the trigger')

  cooldown_time: timedelta = Field(
    default_factory=lambda: timedelta(seconds=0),
    description='Defines the cooldown time of the trigger',
  )

  type_: TriggerKind | None = Field(
    default=None,
    description='Defines the kind of the trigger',
    alias='type',
  )

  presence_type: TriggerGeofenceKind | None = Field(
    default=None,
    description='Defines the geofence kind of the trigger',
  )

  case_type: TriggerCaseKind | None = Field(
    default=None,
    description='Defines the case kind of the trigger',
  )

  case_comment_pattern: TriggerCommentPattern | None = Field(
    default=None,
    description='Defines the comment pattern of the trigger',
  )

  case_comment_value: str | None = Field(
    default=None,
    description='Defines the comment pattern value of the trigger',
  )

  exact_hour: time | None = Field(
    default=None,
    description='Defines the exact hour of the trigger',
  )
  crontab_format: str | None = Field(
    default=None,
    description='Defines the crontab format of the trigger',
  )

  weekdays: list[Weekday] = Field(
    default_factory=list,
    description='Defines the weekdays of the trigger',
  )

  is_plain_crontab: bool = Field(
    default=False,
    description='Defines if the trigger is a plain crontab',
  )

  timezone_id: int | None = Field(
    default=None,
    description='Defines the timezone ID of the trigger',
  )

  parameters: list[str] = Field(
    default_factory=list,
    description='Defines the parameters of the trigger',
  )

  manual_action_fields: list[dict[str, Any]] = Field(
    default_factory=list,
    description='Defines the fields for manual action in the trigger',
  )

  @field_validator('manual_action_fields', mode='before')
  def validate_manual_action_fields(cls, value: Any) -> list[dict[str, Any]]:
    """Ensure manual_action_fields is a list of dictionaries."""
    if isinstance(value, list):
      return value
    return []

  formula: str | None = Field(
    default=None,
    description='Defines the formula of the trigger, this formula is only LCL (Layrz Computation Language) compatible',
  )

  script: str | None = Field(
    default=None,
    description='Defines the script of the trigger, depending of the trigger kidn, this script can be in Python, '
    + 'Javascript, Lua, Dart or Golang. (Or any other language supported by the SDK)',
  )

  is_legacy: bool = Field(
    default=False,
    description='Defines if the trigger is legacy, normally when a version of the trigger is not compatible '
    + 'with the current version of the SDK',
  )

  priority: int = Field(
    default=0,
    description='Defines the priority of the trigger',
  )

  @field_validator('priority', mode='before')
  def validate_priority(cls, value: Any) -> int:
    """Ensure priority is an integer."""
    if isinstance(value, int):
      return value
    try:
      return int(value)
    except (ValueError, TypeError):
      return 0

  color: str | None = Field(
    default='#2196F3',
    description='Defines the color of the trigger',
  )

  sequence: int = Field(
    default=0,
    description='Defines the sequence of the trigger',
  )

  care_protocol_id: int | None = Field(
    default=None,
    description='Defines the care protocol ID of the trigger',
  )

  owner_id: int | None = Field(
    default=None,
    description='Owner ID',
  )

  search_time_delta: timedelta | None = Field(
    default=None,
    description='Defines the search time delta of the trigger',
  )
