"""Report row"""

import warnings
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator

from .report_col import ReportCol


class ReportRow(BaseModel):
  """Report row definition"""

  content: list[ReportCol] = Field(description='List of report columns', default_factory=list)
  height: Optional[float] = Field(description='Row height', default=None)
  compact: bool = Field(description='Compact mode', default=False)

  @field_validator('height', mode='before')
  def _validate_height(cls, value: Any) -> Any:
    """Validate height"""
    if value is not None:
      warnings.warn(
        'height is deprecated, the algorithm will calculate the rigth text color instead',
        DeprecationWarning,
        stacklevel=2,
      )

    return value
