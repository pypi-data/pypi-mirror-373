"""Command Series Ticket entity"""

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from layrz_sdk.constants import UTC
from layrz_sdk.entities.action import Action
from layrz_sdk.entities.asset import Asset
from layrz_sdk.entities.geofence import Geofence
from layrz_sdk.entities.trigger import Trigger


class CommandSeriesTicketStatus(StrEnum):
  PENDING = 'PND'
  IN_SERVICE = 'ISV'
  TO_JOB = 'TJB'
  AT_JOB = 'ATJ'
  POURING = 'POU'
  TO_PLANT = 'TPL'
  IN_YARD = 'IYD'
  OUT_OF_SERVICE = 'OSV'


class CommandSeriesTicket(BaseModel):
  """Command Series Ticket definition"""

  pk: int = Field(..., description='ID', alias='id')
  service_id: int = Field(..., description='Service ID')
  status: CommandSeriesTicketStatus = Field(
    default=CommandSeriesTicketStatus.IN_SERVICE,
    description='Ticket status',
  )

  ticket_id: str = Field(..., description='Ticket ID')
  ticket_code: str = Field(..., description='Ticket code')
  ticket_at: datetime = Field(..., description='Ticket creation date')

  source_id: int | None = Field(default=None, description='Source geofence ID')
  source: Geofence | None = Field(default=None, description='Source geofence')

  job_id: int | None = Field(default=None, description='Job geofence ID')
  job: Geofence | None = Field(default=None, description='Job geofence')

  destination_id: int | None = Field(default=None, description='Destination geofence ID')
  destination: Geofence | None = Field(default=None, description='Destination geofence')

  asset_id: int | None = Field(default=None, description='Asset ID')
  asset: Asset | None = Field(default=None, description='Asset')

  trigger_id: int | None = Field(default=None, description='Trigger ID')
  trigger: Trigger | None = Field(default=None, description='Trigger')

  action_id: int | None = Field(default=None, description='Action ID')
  action: Action | None = Field(default=None, description='Action')

  created_at: datetime = Field(
    default_factory=lambda: datetime.now(UTC),
    description='Creation date',
  )
  updated_at: datetime = Field(
    default_factory=lambda: datetime.now(UTC),
    description='Last update date',
  )
