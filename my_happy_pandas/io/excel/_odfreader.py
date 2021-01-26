from typing import List, cast

import numpy as np

from my_happy_pandas._typing import FilePathOrBuffer, Scalar
from my_happy_pandas.compat._optional import import_optional_dependency

import my_happy_pandas as pd

from my_happy_pandas.io.excel._base import _BaseExcelReader


class _ODFReader(_BaseExcelReader):
    """
    Read tables out of OpenDocument formatted files.

    Parameters
    ----------
    filepath_or_buffer: string, path to be parsed or
        an open readable stream.
    """

    def __init__(self, filepath_or_buffer: FilePathOrBuffer):
        import_optional_dependency("odf")
        super().__init__(filepath_or_buffer)

    @property
    def _workbook_class(self):
        from odf.opendocument import OpenDocument

        return OpenDocument

    def load_workbook(self, filepath_or_buffer: FilePathOrBuffer):
        from odf.opendocument import load

        return load(filepath_or_buffer)

    @property
    def empty_value(self) -> str:
        """Property for compat with other readers."""
        return ""

    @property
    def sheet_names(self) -> List[str]:
        """Return a list of sheet names present in the document"""
        from odf.table import Table

        tables = self.book.getElementsByType(Table)
        return [t.getAttribute("name") for t in tables]

    def get_sheet_by_index(self, index: int):
        from odf.table import Table

        tables = self.book.getElementsByType(Table)
        return tables[index]

    def get_sheet_by_name(self, name: str):
        from odf.table import Table

        tables = self.book.getElementsByType(Table)

        for table in tables:
            if table.getAttribute("name") == name:
                return table

        raise ValueError(f"sheet {name} not found")

    def get_sheet_data(self, sheet, convert_float: bool) -> List[List[Scalar]]:
        """
        Parse an ODF Table into a list of lists
        """
        from odf.table import CoveredTableCell, TableCell, TableRow

        covered_cell_name = CoveredTableCell().qname
        table_cell_name = TableCell().qname
        cell_names = {covered_cell_name, table_cell_name}

        sheet_rows = sheet.getElementsByType(TableRow)
        empty_rows = 0
        max_row_len = 0

        table: List[List[Scalar]] = []

        for i, sheet_row in enumerate(sheet_rows):
            sheet_cells = [x for x in sheet_row.childNodes if x.qname in cell_names]
            empty_cells = 0
            table_row: List[Scalar] = []

            for j, sheet_cell in enumerate(sheet_cells):
                if sheet_cell.qname == table_cell_name:
                    value = self._get_cell_value(sheet_cell, convert_float)
                else:
                    value = self.empty_value

                column_repeat = self._get_column_repeat(sheet_cell)

                # Queue up empty values, writing only if content succeeds them
                if value == self.empty_value:
                    empty_cells += column_repeat
                else:
                    table_row.extend([self.empty_value] * empty_cells)
                    empty_cells = 0
                    table_row.extend([value] * column_repeat)

            if max_row_len < len(table_row):
                max_row_len = len(table_row)

            row_repeat = self._get_row_repeat(sheet_row)
            if self._is_empty_row(sheet_row):
                empty_rows += row_repeat
            else:
                # add blank rows to our table
                table.extend([[self.empty_value]] * empty_rows)
                empty_rows = 0
                for _ in range(row_repeat):
                    table.append(table_row)

        # Make our table square
        for row in table:
            if len(row) < max_row_len:
                row.extend([self.empty_value] * (max_row_len - len(row)))

        return table

    def _get_row_repeat(self, row) -> int:
        """
        Return number of times this row was repeated
        Repeating an empty row appeared to be a common way
        of representing sparse rows in the table.
        """
        from odf.namespaces import TABLENS

        return int(row.attributes.get((TABLENS, "number-rows-repeated"), 1))

    def _get_column_repeat(self, cell) -> int:
        from odf.namespaces import TABLENS

        return int(cell.attributes.get((TABLENS, "number-columns-repeated"), 1))

    def _is_empty_row(self, row) -> bool:
        """
        Helper function to find empty rows
        """
        for column in row.childNodes:
            if len(column.childNodes) > 0:
                return False

        return True

    def _get_cell_value(self, cell, convert_float: bool) -> Scalar:
        from odf.namespaces import OFFICENS

        if str(cell) == "#N/A":
            return np.nan

        cell_type = cell.attributes.get((OFFICENS, "value-type"))
        if cell_type == "boolean":
            if str(cell) == "TRUE":
                return True
            return False
        if cell_type is None:
            return self.empty_value
        elif cell_type == "float":
            # GH5394
            cell_value = float(cell.attributes.get((OFFICENS, "value")))
            if convert_float:
                val = int(cell_value)
                if val == cell_value:
                    return val
            return cell_value
        elif cell_type == "percentage":
            cell_value = cell.attributes.get((OFFICENS, "value"))
            return float(cell_value)
        elif cell_type == "string":
            return self._get_cell_string_value(cell)
        elif cell_type == "currency":
            cell_value = cell.attributes.get((OFFICENS, "value"))
            return float(cell_value)
        elif cell_type == "date":
            cell_value = cell.attributes.get((OFFICENS, "date-value"))
            return pd.to_datetime(cell_value)
        elif cell_type == "time":
            result = pd.to_datetime(str(cell))
            result = cast(pd.Timestamp, result)
            return result.time()
        else:
            raise ValueError(f"Unrecognized type {cell_type}")

    def _get_cell_string_value(self, cell) -> str:
        """
        Find and decode OpenDocument text:s tags that represent
        a run length encoded sequence of space characters.
        """
        from odf.element import Element
        from odf.namespaces import TEXTNS
        from odf.text import S

        text_s = S().qname

        value = []

        for fragment in cell.childNodes:
            if isinstance(fragment, Element):
                if fragment.qname == text_s:
                    spaces = int(fragment.attributes.get((TEXTNS, "c"), 1))
                    value.append(" " * spaces)
                else:
                    # recursive impl needed in case of nested fragments
                    # with multiple spaces
                    # https://github.com/pandas-dev/pandas/pull/36175#discussion_r484639704
                    value.append(self._get_cell_string_value(fragment))
            else:
                value.append(str(fragment))
        return "".join(value)
