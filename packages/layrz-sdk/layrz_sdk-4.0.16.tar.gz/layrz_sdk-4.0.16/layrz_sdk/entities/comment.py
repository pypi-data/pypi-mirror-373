"""Comment entity"""

from datetime import datetime

from pydantic import BaseModel, Field

from .user import User


class Comment(BaseModel):
  """Comment entity"""

  pk: int = Field(description='Comment ID', alias='id')
  content: str = Field(description='Comment content')
  user: User = Field(description='Operator/User what commented the case')
  submitted_at: datetime = Field(description='Date of comment submission')
