from pydantic import BaseModel, Field


class TableHeader(BaseModel):
  """Table header chart configuration"""

  label: str = Field(description='Label of the header')
  key: str = Field(description='Key of the header')
