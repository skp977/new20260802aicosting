"""
FILE NAME: excel_exporter.py

PURPOSE:
Export dictionaries / JSON records to XLSX using openpyxl.

INPUT:
data (dict or list of dicts), filename

OUTPUT:
XLSX file

DEPENDENCIES:
openpyxl

LAST UPDATED:
2026-08-02
"""

from openpyxl import Workbook
from openpyxl.styles import Font


class ExcelExporter:

    def export(self, filename, data):

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Record"

        if isinstance(data, list):

            if data and isinstance(data[0], dict):
                self._write_rows(
                    sheet,
                    data[0].keys(),
                    [row.values() for row in data]
                )
            else:
                self._write_single_column(sheet, data)

        elif isinstance(data, dict):

            headers = ["Field", "Value"]

            sheet.append(headers)
            self._style_header(sheet, 1)

            for key, value in data.items():
                sheet.append([key, value])

            self._autosize(sheet)

        else:
            sheet.append(["data"])
            sheet.append([str(data)])

        workbook.save(filename)

        return filename

    def _write_rows(self, sheet, headers, rows):

        sheet.append(list(headers))
        self._style_header(sheet, 1)

        for row in rows:
            sheet.append(list(row))

        self._autosize(sheet)

    def _write_single_column(self, sheet, values):

        sheet.append(["Value"])
        self._style_header(sheet, 1)

        for value in values:
            sheet.append([value])

        self._autosize(sheet)

    def _style_header(self, sheet, row):

        for cell in sheet[row]:
            cell.font = Font(bold=True)

    def _autosize(self, sheet):

        for column in sheet.columns:
            width = max(
                len(str(cell.value)) if cell.value is not None else 0
                for cell in column
            )
            sheet.column_dimensions[
                column[0].column_letter
            ].width = min(width + 2, 60)
