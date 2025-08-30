from __future__ import annotations

import warnings
from abc import abstractmethod
from enum import Enum
from typing import Any

from sapiopycommons.general.aliases import SapioRecord, AliasUtil
from sapiopycommons.general.exceptions import SapioException
from sapiopycommons.general.time_util import TimeUtil


class FileWriter:
    """
    This class helps with the creation of character separated value files (e.g. CSVs, TSVs). You can make use of
    FileUtil.csv_to_xlsx to convert these files to xlsx files.
    """
    headers: list[str]
    body: list[list[Any]]
    delimiter: str
    line_break: str
    column_definitions: dict[str, ColumnDef]

    def __init__(self, headers: list[str], delimiter: str = ",", line_break: str = "\r\n"):
        """
        :param headers: The headers to display at the top of the file in the order in which they should appear.
        :param delimiter: The delimiter character(s) to ues between cells in the file.
        :param line_break: The character(s) to use as a line break at the end of rows.
        """
        self.headers = headers
        self.delimiter = delimiter
        self.line_break = line_break
        self.body = []
        self.column_definitions = {}

    def add_row_list(self, row: list[Any]) -> None:
        """
        Add a row of values to the file from a list. The length of the given list should be equal to the number of
        headers defined for this FileWriter.

        To be used when you just want to put together a simple file and don't want to deal with ColumnDefinitions and
        RowBundles.

        :param row: A row of values to add to the end of the file.
        """
        row_count: int = len(row)
        header_count: int = len(self.headers)
        if row_count != header_count:
            raise SapioException(f"The given list has {row_count} elements but this FileWriter has {header_count} "
                                 f"headers. The number of row elements must equal the number of headers.")
        self.body.append(row)

    def add_row_dict(self, row: dict[str, Any]) -> None:
        """
        Add a row of values to the file from a dict. The dict is expected to contain keys that match the headers of
        the file. For any header that exists for the file that doesn't have a matching key in the given dict, an empty
        string is printed.

        To be used when you just want to put together a simple file and don't want to deal with ColumnDefinitions and
        RowBundles.

        :param row: A row of values to add to the end of the file.
        """
        new_row: list[Any] = []
        for header in self.headers:
            new_row.append(row.get(header, ""))
        self.body.append(new_row)

    def add_column_definition(self, header: str, column_def: ColumnDef) -> None:
        """
        Add a new column definition to this FileWriter for a specific header.

        ColumnDefs are only used if the build_file function is provided with a list of RowBundles. Every header must
        have a column definition if this is the case.

        Custom column definitions can be created by defining a class that extends ColumnDef and implements the print
        method.

        :param column_def: A column definitions to be used to construct the file when build_file is
            called.
        :param header: The header that this column definition is for. If a header is provided that isn't in the headers
            list, the header is appended to the end of the list.
        """
        if header not in self.headers:
            self.headers.append(header)
        self.column_definitions[header] = column_def

    def add_column_definitions(self, column_defs: dict[str, ColumnDef]) -> None:
        """
        Add new column definitions to this FileWriter.

        ColumnDefs are only used if the build_file function is provided with a list of RowBundles. Every header must
        have a column definition if this is the case.

        Custom column definitions can be created by defining a class that extends ColumnDef and implements the print
        method.

        :param column_defs: A dictionary of header names to column definitions to be used to construct the file when
            build_file is called.
        """
        # For backwards compatibility purposes, if column definitions are provided as a list,
        # add them in order of appearance of the headers. This will only work if the headers are defined first, though.
        if isinstance(column_defs, list):
            warnings.warn("Adding column definitions is no longer expected as a list. Continuing to provide a list to "
                          "this function may result in undesirable behavior.", UserWarning)
            if not self.headers:
                raise SapioException("No headers provided to FileWriter before the column definitions were added.")
            for header, column_def in zip(self.headers, column_defs):
                self.column_definitions[header] = column_def
        for header, column_def in column_defs.items():
            self.add_column_definition(header, column_def)

    def build_file(self, rows: list[RowBundle] | None = None, sorter=None, reverse: bool = False) -> str:
        """
        Build the file according the information that has been given to this FileWriter. If any add_row calls were
        made, those will be listed first before any rows constructed using any given RowBundles (assuming you aren't
        sorting the rows). RowBundles can only be used if this FileWriter was also provided with ColumnDefs for mapping
        the bundles to the file.
        
        If ever a None value is countered, instead prints an empty string.

        :param rows: A list of information used to populate rows in the file. If this parameter is provided, then this
            FileWriter must have also been given column definitions to map the row information to the file with.
        :param sorter: Some function to sort the rows by before they are printed.
            See https://docs.python.org/3.10/howto/sorting.html#sortinghowto for details on the type of functions that
            can be provided.
        :param reverse: Whether the above sorter should be run in reverse.
        :return: A string of the created file. Call string.encode() to turn this into a byte array for client callbacks.
        """
        # If any column definitions have been provided, the number of column definitions and headers must be equal.
        if self.column_definitions:
            for header in self.headers:
                if header not in self.column_definitions:
                    raise SapioException(f"FileWriter has no column definition for the header {header}. If any column "
                                         f"definitions are provided, then all headers must have a column definition.")
        # If any RowBundles have been provided, there must be column definitions for mapping them to the file.
        elif rows:
            raise SapioException(f"FileWriter was given RowBundles but contains no column definitions for mapping "
                                 f"them to file contents. Either add ColumnDefs to map the RowBundles with, or use the "
                                 f"simple add_row functions.")

        file: str = self.delimiter.join(self.headers) + self.line_break
        self.__build_rows(rows)
        if sorter is not None:
            sorted(self.body, key=sorter, reverse=reverse)
        for row in self.body:
            file += self.delimiter.join([self.__str(x) for x in row]) + self.line_break
        return file

    def __build_rows(self, rows: list[RowBundle] | None = None) -> None:
        """
        Populate the FileWriter's body using the RowBundles and ColumnDefs.

        :param rows: A list of RowBundles to populate the file body with.
        """
        if not rows:
            return
        rows.sort(key=lambda x: x.index)
        for row in rows:
            new_row: list[Any] = []
            for header in self.headers:
                column = self.column_definitions[header]
                if column.may_skip and row.may_skip:
                    new_row.append("")
                else:
                    new_row.append(column.print(row))
            self.body.append(new_row)

    def __str(self, value: Any) -> str:
        """
        :param value: Some value to convert to a string.
        :return: The input value as a string. If the string of the input value contains the delimiter character, then
            the returned value is surrounded by quotation marks.
        """
        if value is None:
            return ""
        ret: str = str(value)
        if self.delimiter in ret:
            ret = "\"" + ret + "\""
        return ret


class RowBundle:
    """
    A RowBundle represents a collection of information which may be used to print a row in a file.
    """
    index: int
    record: SapioRecord
    records: dict[str, SapioRecord]
    fields: dict[str, Any]
    may_skip: bool

    def __init__(self, index: int | None = None,
                 record: SapioRecord | None = None,
                 records: dict[str, SapioRecord] | None = None,
                 fields: dict[str, Any] | None = None,
                 may_skip: bool | None = None):
        """
        :param index: An index for this RowBundle. RowBundles are sorted by index before they are printed by the
            FileWriter. The FileWriter.build_file's sorter parameter is run after this sorting.
        :param record: A singular record for column definitions to pull information from.
        :param records: A dictionary of records for column definitions to pull information from. Each record is keyed by
            some name that column definitions can use to determine which record to get certain information from.
        :param fields: A list of "fields" specific to this bundle which aren't tied to a record.
        :param may_skip: If true, this RowBundle will return an empty string for ColumnDefs where may_skip is true.
        """
        self.index = index if index is not None else 0
        self.record = record
        self.records = records if records is not None else {}
        self.fields = fields if fields is not None else {}
        self.may_skip = may_skip if may_skip is not None else bool(records)


class ColumnDef:
    """
    The base class for all column definitions. Each column definition may cause a RowBundle to print a value in a
    different manner.
    """
    may_skip: bool
    """If true, this ColumnDef will return an empty string for RowBundles where may_skip is true."""

    @abstractmethod
    def print(self, row: RowBundle) -> Any:
        """
        :param row: The RowBundle to print some information for.
        :return: The printed value for the given RowBundle.
        """
        pass


class StaticColumn(ColumnDef):
    """
    A static column will always print the same value regardless of the input RowBundle.
    """
    value: Any

    def __init__(self, value: Any, may_skip: bool = False):
        """
        :param value: The value to print for this column.
        :param may_skip: If true, this ColumnDef will return an empty string for RowBundles where may_skip is true.
        """
        self.value = value
        self.may_skip = may_skip

    def print(self, row: RowBundle) -> Any:
        return self.value


class EmptyColumn(StaticColumn):
    """
    An empty column is a static column that always prints an empty string.
    """
    def __init__(self):
        super().__init__("")


class FieldSearchOrder(Enum):
    """
    An enum that specifies the order in which fields should be searched for in the RowBundle for FieldColumns.
    """
    RECORD_FIRST = 0
    """First search the fields on the record, then search the fields in the bundle."""
    BUNDLE_FIRST = 1
    """First search the fields in the bundle, then search the fields on the record."""
    RECORD_ONLY = 2
    """Only search the fields on the record."""
    BUNDLE_ONLY = 3
    """Only search the fields in the bundle."""


class FieldColumn(ColumnDef):
    """
    A field column prints the value of a given field from the input RowBundle. This field may come from a record in the
    RowBundle or from the RowBundle itself.
    """
    field_name: str
    record_key: str | None
    search_order: FieldSearchOrder
    skip_none_values: bool

    def __init__(self, field_name: str, record_key: str | None = None,
                 search_order: FieldSearchOrder = FieldSearchOrder.RECORD_FIRST,
                 skip_none_values: bool = False,
                 may_skip: bool = False):
        """
        :param field_name: The name of the field in the RowBundle to get the value of.
        :param record_key: If a record key is given, looks in the RowBundle's record dict for the record with they key.
            If no record key is given, look as the RowBundle's singular record.
        :param search_order: An enum that specifies the order in which fields should be searched for in the RowBundle.
        :param skip_none_values: If true and search_order is RECORD_FIRST or BUNDLE_FIRST, use the value of the second
            location's field if the first location's value is None.
        :param may_skip: If true, this ColumnDef will return an empty string for RowBundles where may_skip is true.
        """
        self.field_name = field_name
        self.record_key = record_key
        self.search_order = search_order
        self.skip_none_values = skip_none_values
        self.may_skip = may_skip

    def print(self, row: RowBundle) -> Any:
        return self._get_field(row)
    
    def _get_field(self, row: RowBundle) -> Any:
        record: SapioRecord = row.records.get(self.record_key) if self.record_key else row.record
        if self.search_order == FieldSearchOrder.RECORD_ONLY:
            return record.get_field_value(self.field_name) if record else None
        elif self.search_order == FieldSearchOrder.BUNDLE_ONLY:
            return row.fields.get(self.field_name)
        elif self.search_order == FieldSearchOrder.RECORD_FIRST:
            fields: dict[str, Any] = AliasUtil.to_field_map(record) if record else {}
            if self.field_name not in fields or (self.skip_none_values and fields.get(self.field_name) is None):
                return row.fields.get(self.field_name)
            return fields.get(self.field_name)
        elif self.search_order == FieldSearchOrder.BUNDLE_FIRST:
            if self.field_name not in row.fields or (self.skip_none_values and row.fields.get(self.field_name) is None):
                return record.get_field_value(self.field_name) if record else None
            return row.fields.get(self.field_name)


class DateColumn(FieldColumn):
    """
    A time column takes a field value which is an integer timestamp since the epoch and converts it to a human-readable
    date/time string.
    """
    time_format: str
    timezone: str | None = None

    def __init__(self, field_name: str, time_format: str, timezone: str | None = None, record_key: str | None = None,
                 search_order: FieldSearchOrder = FieldSearchOrder.RECORD_FIRST,
                 skip_none_values: bool = False, may_skip: bool = False):
        """
        :param field_name: The name of the field in the RowBundle to get the value of.
        :param time_format: The format to put the date in. See TimeUtil for more details on date formats.
        :param timezone: The timezone to convert the date to. If not specified, uses the default timezone of
            TimeUtil. See TimeUtil for more details on timezones.
        :param record_key: If a record key is given, looks in the RowBundle's record dict for the record with they key.
            If no record key is given, look as the RowBundle's singular record.
        :param search_order: An enum that specifies the order in which fields should be searched for in the RowBundle.
        :param skip_none_values: If true and search_order is RECORD_FIRST or BUNDLE_FIRST, use the value of the second
            location's field if the first location's value is None.
        :param may_skip: If true, this ColumnDef will return an empty string for RowBundles where may_skip is true.
        """
        super().__init__(field_name, record_key, search_order, skip_none_values, may_skip)
        self.time_format = time_format
        self.timezone = timezone

    def print(self, row: RowBundle) -> str:
        field: int = self._get_field(row)
        return TimeUtil.millis_to_format(field, self.time_format, self.timezone)


class ListColumn(ColumnDef):
    """
    A list column is like a static column, except it may print a different value for each row. If there are more rows
    than the length of this list, then all subsequent rows will print a blank value.
    
    Note that using the FileWriter.build_file's sorter parameter may result in these values not being in the expected
    order in the output file.
    """
    column_list: list[Any]
    list_size: int
    index: int = 0

    def __init__(self, column_list: list[Any]):
        """
        :param column_list: The list of values to print for this column.
        """
        self.column_list = column_list
        self.list_size = len(column_list)
        self.may_skip = False

    def print(self, row: RowBundle) -> Any:
        if self.index >= self.list_size:
            return ""
        val: Any = self.column_list[self.index]
        self.index += 1
        return val
