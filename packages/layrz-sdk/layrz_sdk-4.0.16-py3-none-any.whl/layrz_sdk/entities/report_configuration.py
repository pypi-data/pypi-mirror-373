from pydantic import BaseModel, Field


class ReportConfiguration(BaseModel):
  """Report configuration entity"""

  title: str = Field(description='Report title')
  pages_count: int = Field(description='Number of pages in the report')
