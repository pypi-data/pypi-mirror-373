from collections.abc import Callable
from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field
from xlsxwriter.worksheet import Worksheet


@runtime_checkable
class BuilderFunction(Protocol):
  """
  Protocol for the builder function.
  """

  def __call__(self, *, sheet: Worksheet, **kwargs: Any) -> None: ...


class CustomReportPage(BaseModel):
  """
  Custom report page
  Basically it's a wrapper of the `xlswriter` worksheet that uses a function to construct the page
  """

  model_config = ConfigDict(
    from_attributes=True,
    arbitrary_types_allowed=True,
  )

  name: str = Field(description='Name of the page. Length should be less than 60 characters')
  builder: Callable[[Worksheet], None] | None = Field(
    description=('Function to build the page. The only argument is the worksheet object'),
    default=None,
  )
  extended_builder: BuilderFunction | None = Field(
    description=(
      'Function to build the page. The first argument is the worksheet object, '
      'and the rest are the kwargs to give support for the builder function.'
      '\n Currently, the only supported kwarg is `workbook` which is the workbook object'
    ),
    default=None,
  )
