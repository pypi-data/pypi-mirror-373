"""Report class"""

import logging
import os
import time
import warnings
from pathlib import Path
from typing import Any, Optional, Self

import xlsxwriter
from pydantic import BaseModel, Field, field_validator

from layrz_sdk.entities.custom_report_page import CustomReportPage
from layrz_sdk.entities.report_data_type import ReportDataType
from layrz_sdk.entities.report_format import ReportFormat
from layrz_sdk.entities.report_page import ReportPage
from layrz_sdk.helpers.color import use_black

log = logging.getLogger(__name__)


class Report(BaseModel):
  """Report definition"""

  name: str = Field(description='Name of the report. Length should be less than 60 characters')
  pages: list[ReportPage | CustomReportPage] = Field(
    description='List of report pages',
    default_factory=list,
  )
  export_format: Optional[ReportFormat] = Field(description='Export format of the report', default=None)

  @field_validator('export_format', mode='before')
  def _validate_export_format(cls: 'Report', value: Any) -> Any:
    if value is not None:
      warnings.warn(
        'export_format is deprecated, use the export method instead',
        DeprecationWarning,
        stacklevel=2,
      )

    return value

  @property
  def filename(self: Self) -> str:
    """Report filename"""
    return f'{self.name}_{int(time.time() * 1000)}.xlsx'

  def export(
    self: Self,
    path: str | Path,
    export_format: Optional[ReportFormat] = None,
    password: Optional[str] = None,
    msoffice_crypt_path: str = '/opt/msoffice/bin/msoffice-crypt.exe',
  ) -> Path | dict[str, Any]:
    """
    Export report to file

    :param path: Path to save the report
    :type path: str | Path
    :param export_format: Format to export the report
    :type export_format: ReportFormat
    :param password: Password to protect the file (Only works with Microsoft Excel format)
    :type password: str
    :param msoffice_crypt_path: Path to the msoffice-crypt.exe executable, used to encrypt the file
    :type msoffice_crypt_path: str
    :return: Full path of the exported file or JSON representation of the report
    :rtype: Path | dict
    :raises AttributeError: If the export format is not supported
    """
    if export_format:
      if export_format == ReportFormat.MICROSOFT_EXCEL:
        return self._export_xlsx(path=path, password=password, msoffice_crypt_path=msoffice_crypt_path)
      elif export_format == ReportFormat.JSON:
        if password:
          return {'name': self.name, 'is_protected': True, 'pages': []}
        return self._export_json()
      else:
        raise AttributeError(f'Unsupported export format: {export_format}')

    if self.export_format == ReportFormat.MICROSOFT_EXCEL:
      return self._export_xlsx(path=path, password=password, msoffice_crypt_path=msoffice_crypt_path)
    elif self.export_format == ReportFormat.JSON:
      if password:
        return {'name': self.name, 'is_protected': True, 'pages': []}
      return self._export_json()
    else:
      raise AttributeError(f'Unsupported export format: {self.export_format}')

  @warnings.deprecated('export_as_json is deprecated, use export with export_format=ReportFormat.JSON instead')
  def export_as_json(self: Self) -> dict[str, Any]:
    """Returns the report as a JSON dict"""
    return self._export_json()

  def _export_json(self: Self) -> dict[str, Any]:
    """Returns a JSON dict of the report"""
    json_pages = []
    for page in self.pages:
      if isinstance(page, CustomReportPage):
        continue

      headers: list[dict[str, Any]] = []
      for header in page.headers:
        headers.append(
          {
            'content': header.content,
            'text_color': '#000000' if use_black(header.color) else '#ffffff',
            'color': header.color,
          }
        )
      rows = []
      for row in page.rows:
        cells = []
        for cell in row.content:
          cells.append(
            {
              'content': cell.content,
              'text_color': '#000000' if use_black(cell.color) else '#ffffff',
              'color': cell.color,
              'data_type': cell.data_type.value,
            }
          )
        rows.append(
          {
            'content': cells,
            'compact': row.compact,
          }
        )
      json_pages.append(
        {
          'name': page.name,
          'headers': headers,
          'rows': rows,
        }
      )

    return {
      'name': self.name,
      'pages': json_pages,
    }

  def _export_xlsx(
    self: Self,
    path: str | Path,
    password: Optional[str] = None,
    msoffice_crypt_path: Optional[str] = None,
  ) -> Path:
    """
    Export to Microsoft Excel (.xslx)

    :param path: Path to save the report
    :type path: str | Path
    :param password: Password to protect the file
    :type password: str
    :param msoffice_crypt_path: Path to the msoffice-crypt.exe executable, used to encrypt the file
    :type msoffice_crypt_path: str

    :return: Full path of the exported file
    :rtype: Path

    :raises AttributeError: If the export format is not supported
    """

    if isinstance(path, str):
      path = Path(path).resolve()

    full_path = path / self.filename
    if full_path.exists():
      log.warning(f'File {full_path} already exists, overwriting it')
      os.remove(full_path)

    book = xlsxwriter.Workbook(full_path)

    pages_name: list[str] = []

    for page in self.pages:
      sheet_name = page.name[0:20]

      if sheet_name in pages_name:
        sheet_name = f'{sheet_name} ({pages_name.count(sheet_name) + 1})'

      # Allow only numbers, letters, spaces and _ or - characters
      # Other characters will be removed
      sheet_name = ''.join(e for e in sheet_name if e.isalnum() or e in [' ', '_', '-'])
      sheet = book.add_worksheet(sheet_name)

      if isinstance(page, CustomReportPage):
        if page.extended_builder:
          page.extended_builder(sheet=sheet, workbook=book)
        elif page.builder:
          page.builder(sheet)
        else:
          raise AttributeError('Custom report page must have a builder or extended_builder function')

        sheet.autofit()
        continue

      if page.freeze_header:
        sheet.freeze_panes(1, 0)

      for i, header in enumerate(page.headers):
        style = book.add_format(
          {
            'align': header.align.value,
            'font_color': '#000000' if use_black(header.color) else '#ffffff',
            'bg_color': header.color,
            'bold': header.bold,
            'valign': 'vcenter',
            'font_size': 11,
            'top': 1,
            'left': 1,
            'right': 1,
            'bottom': 1,
            'font_name': 'Aptos Narrow',
          }
        )
        sheet.write(0, i, header.content, style)

      should_protect = False
      for i, row in enumerate(page.rows):
        for j, cell in enumerate(row.content):
          style = {
            'align': cell.align.value,
            'font_color': '#000000' if use_black(cell.color) else '#ffffff',
            'bg_color': cell.color,
            'bold': cell.bold,
            'valign': 'vcenter',
            'font_size': 11,
            'top': 1,
            'left': 1,
            'right': 1,
            'bottom': 1,
            'font_name': 'Aptos Narrow',
          }

          format_ = book.add_format(style)

          if cell.lock:
            if not should_protect:
              should_protect = True
            format_.set_locked(True)

          value: Any = None

          match cell.data_type:
            case ReportDataType.BOOL:
              value = 'Yes' if cell.content else 'No'

            case ReportDataType.DATETIME:
              value = cell.content.strftime(cell.datetime_format)

            case ReportDataType.INT:
              try:
                value = int(cell.content)
              except ValueError:
                value = cell.content
                log.warning(f'Invalid int value: {cell.content} in cell {i + 1}, {j}')

            case ReportDataType.FLOAT:
              try:
                value = float(cell.content)
                format_.set_num_format('0.00')

              except ValueError:
                value = cell.content
                log.warning(f'Invalid float value: {cell.content} in cell {i + 1}, {j}')

            case ReportDataType.CURRENCY:
              value = float(cell.content)
              format_.set_num_format(f'"{cell.currency_symbol}" * #,##0.00;[Red]"{cell.currency_symbol}" * #,##0.00')

            case _:
              value = str(cell.content)

          sheet.write(i + 1, j, value, format_)

          if row.compact:
            sheet.set_row(i + 1, None, None, {'level': 1, 'hidden': True})
          else:
            sheet.set_row(i + 1, None, None, {'collapsed': True})

      sheet.autofit()

      if should_protect:
        sheet.protect()
    book.close()

    if password and msoffice_crypt_path:
      new_path = os.path.join(path, f'encrypted_{self.filename}')
      log.debug(f'Executing `{msoffice_crypt_path} -e -p "{password}" "{full_path}" "{new_path}"`')
      os.system(f'{msoffice_crypt_path} -e -p "{password}" "{full_path}" "{new_path}"')
      os.remove(full_path)

      with open(new_path, 'rb') as f:
        with open(full_path, 'wb') as f2:
          f2.write(f.read())

      os.remove(new_path)

    return full_path
