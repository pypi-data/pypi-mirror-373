"""Entry entity"""

from datetime import datetime

from pydantic import BaseModel, Field


class AtsPossibleEntry(BaseModel):
  """Entry entity"""

  initial_tank_level: float = Field(description='Initial tank level in liters', default=0.0)
  tank_accumulator: float = Field(description='Tank accumulator in liters', default=0.0)
  is_ready: bool = Field(description='Indicates if the entry is ready', default=False)
  is_validated: bool = Field(description='Indicates if the entry is validated', default=False)
  start_at: datetime = Field(description='Start time of the entry')
  end_at: datetime | None = Field(description='End time of the entry')
  accumulator_history: list[float] = Field(
    default_factory=list, description='History of the tank accumulator in liters'
  )
  is_recalculated: bool = Field(description='Indicates if the entry is recalculated', default=False)
  is_blackbox: bool = Field(description='Indicates if the entry is a black box', default=False)
  is_executed_by_command: bool | None = Field(
    description='Indicates if the entry is executed by command', default=False
  )
  is_ready_by_reception: bool | None = Field(description='Indicates if the entry is ready by reception', default=False)
  false_positive_count: int = Field(description='Count of false positives for the entry', default=0)
  reception_id: int | None = Field(description='Reception ID associated with the entry', default=None)
