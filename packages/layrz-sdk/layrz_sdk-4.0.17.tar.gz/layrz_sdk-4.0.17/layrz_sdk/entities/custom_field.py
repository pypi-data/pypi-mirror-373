"""Custom Field entitiy"""

from pydantic import BaseModel, Field


class CustomField(BaseModel):
  """Custom field definition"""

  pk: int | None = Field(default=None, description='Primary key of the custom field', alias='id')
  name: str = Field(description='Defines the name of the custom field')
  value: str = Field(description='Defines the value of the custom field')
  is_fixed: bool = Field(default=False, description='Defines if the custom field is fixed or not')
