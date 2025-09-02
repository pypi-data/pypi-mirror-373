"""LastMessage entity"""

from pydantic import BaseModel, Field

from .asset import Asset
from .message import Message


class LastMessage(Message, BaseModel):
  """LastMessage definition"""

  asset: Asset = Field(description='Defines the asset of the last message')
