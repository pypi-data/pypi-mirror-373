"""Report header"""

import warnings
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator

from .text_alignment import TextAlignment


class ReportHeader(BaseModel):
  """Report header entity"""

  content: Any = Field(description='Header content')
  color: str = Field(description='Header color', default='#ffffff')
  text_color: Optional[str] = Field(description='Header text color', default=None)
  align: TextAlignment = Field(description='Header text alignment', default=TextAlignment.CENTER)
  bold: bool = Field(description='Bold text', default=False)
  width: Optional[float] = Field(description='Header width', default=None)

  @field_validator('text_color', mode='before')
  def _validate_text_color(cls, value: Any) -> Any:
    """Validate text color"""
    if value is not None:
      warnings.warn(
        'text_color is deprecated, the algorithm will calculate the rigth text color instead',
        DeprecationWarning,
        stacklevel=2,
      )

    return value

  @field_validator('width', mode='before')
  def _validate_width(cls, value: Any) -> Any:
    """Validate width"""
    if value is not None:
      warnings.warn(
        'width is deprecated, the algorithm will calculate the rigth width instead',
        DeprecationWarning,
        stacklevel=2,
      )

    return value
