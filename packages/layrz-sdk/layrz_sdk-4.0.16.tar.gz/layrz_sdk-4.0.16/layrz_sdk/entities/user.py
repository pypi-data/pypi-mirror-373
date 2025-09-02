"""User entity"""

from pydantic import BaseModel, Field


class User(BaseModel):
  """User entity"""

  pk: int = Field(description='Defines the primary key of the user', alias='id')
  name: str = Field(description='Defines the name of the user')
