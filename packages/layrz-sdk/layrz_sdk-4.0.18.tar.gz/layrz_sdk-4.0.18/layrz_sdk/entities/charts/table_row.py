from typing import Any

from pydantic import BaseModel, Field


class TableRow(BaseModel):
  """Table row chart configuration"""

  data: Any = Field(description='Data of the row')
