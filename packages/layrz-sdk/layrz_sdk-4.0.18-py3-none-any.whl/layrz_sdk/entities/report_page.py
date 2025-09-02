"""Report page"""

from pydantic import BaseModel, Field

from .report_header import ReportHeader
from .report_row import ReportRow


class ReportPage(BaseModel):
  """Report page definition"""

  name: str = Field(description='Name of the page. Length should be less than 60 characters')
  headers: list[ReportHeader] = Field(description='List of report headers', default_factory=list)
  rows: list[ReportRow] = Field(description='List of report rows', default_factory=list)
  freeze_header: bool = Field(description='Freeze header', default=False)
