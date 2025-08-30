import re
from typing import Any, Callable, Iterable

from sapiopycommons.general.aliases import SapioRecord
from sapiopycommons.general.exceptions import SapioException
from sapiopycommons.general.time_util import TimeUtil
from sapiopycommons.recordmodel.record_handler import RecordHandler

FilterList = Iterable[int] | range | Callable[[int, dict[str, Any]], bool] | None
"""A FilterList is an object used to determine if a row in the file data should be skipped over. This can take the
form of am iterable (e.g. list, set) of its or a range where row indices in the list or range are skipped, or it can be
a callable function where rows are skipped if the function returns true. Callable function have two input parameters;
the first is the index of the row and the second is the dict for that row. If None, then the list isn't used as a
filter."""


class FileDataHandler:
    """
    A FileDataHandler takes in a list of dictionaries, presumably from a tokenized CSV or XLSX file, and allows for the
    filtering and modification of its contents. This can be used for simpler querying of values from a file, such as
    getting every value under a header in order to use it to query records in the system.

    Look into using this in combination with FileValidator to prepare files for the FileValidator and for use in
    data record fields.
    """
    file_data: list[dict[str, Any]]

    def __init__(self, file_data: list[dict[str, Any]]):
        """
        :param file_data: A list of dictionaries. Every dictionary in the list is expected to have the same keys.
            FileUtil.tokenize_csv and tokenize_xlsx can be used to convert a file into such a list.
            CustomReportUtil can also generate lists of dictionaries that match this criteria.
        """
        self.file_data = file_data

    def get_row(self, index: int) -> dict[str, Any]:
        """
        Get a particular row of data given its index.

        :param index: The index of the row to return.
        :return: The file data for the corresponding row.
        """
        return self.file_data[index]

    def get_rows(self, indices: list[int]) -> list[dict[str, Any]]:
        """
        Get a list of rows given their indices. Rows will be returned in the same order as the index list.

        :param indices: The indices of the rows to return.
        :return: The file data for the corresponding rows, in the same order as the input.
        """
        return [self.file_data[index] for index in indices]

    def has_headers(self, headers: list[str]) -> list[str]:
        """
        Determine if the file data for this handler has all the provided headers (dict keys). This assumes that every
        dict in the file data list has the same keys, so only the first row is used to verify the headers. The file data
        may have extra headers than just those in the provided list.

        :param headers: A list of headers/key names to check.
        :return: A list of all the headers that are in the provided headers list but not in the file data.
        """
        first_row: dict[str, Any] = self.get_row(0)
        missing_headers: list[str] = []
        for header in headers:
            if header not in first_row:
                missing_headers.append(header)
        return missing_headers

    def empty_cells(self, header: str,
                    *, whitelist: FilterList = None, blacklist: FilterList = None) -> list[int]:
        """
        Find the index of all rows under a particular header which are empty. A cell under a header is considered empty
        if either the value is None or the object type under the header has the __len__ special method and len(value)
        returns zero; this is used to return rows with empty strings and lists. (Not simply using bool(value) because we
        want explicit zero numerical values to be considered occupied.)

        :param header: The header of the column to check the contents of.
        :param whitelist: If a row doesn't match the whitelist, it will be skipped over. See the FilterList alias
            description for the forms that a whitelist can take.
        :param blacklist: If a row matches the blacklist, it will be skipped over. See the FilterList alias
            description for the forms that a blacklist can take.
        :return: The index of every row with an empty cell under the specified header.
        """
        indices: list[int] = []
        for i, row in enumerate(self.file_data):
            if self.skip_row(i, row, whitelist, blacklist):
                continue
            value: Any = row.get(header)
            if value is None or (hasattr(value, "__len__") and len(value) == 0):
                indices.append(i)
        return indices

    def occupied_cells(self, header: str,
                       *, whitelist: FilterList = None, blacklist: FilterList = None) -> list[int]:
        """
        Find the index of all rows under a particular header which are occupied. A cell under a header is considered
        occupied if the value is not None, or, should the object type under the header have the __len__ special method,
        len(value) returns zero; this is used to avoid returning rows with empty strings and lists. (Not simply using
        bool(value) because we want explicit zero numerical values to be considered occupied.)

        :param header: The header of the column to check the contents of.
        :param whitelist: If a row doesn't match the whitelist, it will be skipped over. See the FilterList alias
            description for the forms that a whitelist can take.
        :param blacklist: If a row matches the blacklist, it will be skipped over. See the FilterList alias
            description for the forms that a blacklist can take.
        :return: The index of every row with an occupied cell under the specified header.
        """
        indices: list[int] = []
        for i, row in enumerate(self.file_data):
            if self.skip_row(i, row, whitelist, blacklist):
                continue
            value: Any = row.get(header)
            if value is not None and (not hasattr(value, "__len__") or len(value) != 0):
                indices.append(i)
        return indices

    def find_values(self, header: str, values: Iterable[Any],
                    *, whitelist: FilterList = None, blacklist: FilterList = None) -> list[int]:
        """
        Get the index of the rows with a value under the header matching the input values.

        :param header: The header of the column to check the contents of.
        :param values: A collection of values that the cells in the column must be within.
        :param whitelist: If a row doesn't match the whitelist, it will be skipped over. See the FilterList alias
            description for the forms that a whitelist can take.
        :param blacklist: If a row matches the blacklist, it will be skipped over. See the FilterList alias
            description for the forms that a blacklist can take.
        :return: The index of every row with a value in the input collection under the specified header.
        """
        indices: list[int] = []
        for i, row in enumerate(self.file_data):
            if self.skip_row(i, row, whitelist, blacklist):
                continue
            if row.get(header) in values:
                indices.append(i)
        return indices

    def get_values_list(self, header: str,
                        *, whitelist: FilterList = None, blacklist: FilterList = None) -> list[Any]:
        """
        Get a list of every value under a specific header in order of appearance.

        :param header: The header of the column to check the contents of.
        :param whitelist: If a row doesn't match the whitelist, it will be skipped over. See the FilterList alias
            description for the forms that a whitelist can take.
        :param blacklist: If a row matches the blacklist, it will be skipped over. See the FilterList alias
            description for the forms that a blacklist can take.
        :return: A list of the values under the specified header.
        """
        values: list[Any] = []
        for i, row in enumerate(self.file_data):
            if self.skip_row(i, row, whitelist, blacklist):
                continue
            values.append(row.get(header))
        return values

    def get_values_set(self, header: str,
                       *, whitelist: FilterList = None, blacklist: FilterList = None) -> set[Any]:
        """
        Get a set of values under a specified header.

        :param header: The header of the column to check the contents of.
        :param whitelist: If a row doesn't match the whitelist, it will be skipped over. See the FilterList alias
            description for the forms that a whitelist can take.
        :param blacklist: If a row matches the blacklist, it will be skipped over. See the FilterList alias
            description for the forms that a blacklist can take.
        :return: A set of the values under the specified header.
        """
        values: set[Any] = set()
        for i, row in enumerate(self.file_data):
            if self.skip_row(i, row, whitelist, blacklist):
                continue
            values.add(row.get(header))
        return values

    def get_values_dict(self, header: str,
                        *, whitelist: FilterList = None, blacklist: FilterList = None) \
            -> dict[Any, list[int]]:
        """
        Get a dict of values under a specified header where each value is mapped to its row(s) of origin.

        :param header: The header of the column to check the contents of.
        :param whitelist: If a row doesn't match the whitelist, it will be skipped over. See the FilterList alias
            description for the forms that a whitelist can take.
        :param blacklist: If a row matches the blacklist, it will be skipped over. See the FilterList alias
            description for the forms that a blacklist can take.
        :return: A dict of the values under the specified header, mapping the cell values to the indices that they come
            from.
        """
        values: dict[Any, list[int]] = {}
        for i, row in enumerate(self.file_data):
            if self.skip_row(i, row, whitelist, blacklist):
                continue
            values.setdefault(row.get(header), []).append(i)
        return values

    def get_duplicates(self, header: str,
                       *, whitelist: FilterList = None, blacklist: FilterList = None) \
            -> dict[Any, list[int]]:
        """
        Get a dict of values under a specific header that appear more than once in that column where each value is
        mapped by its rows of origin.

        :param header: The header of the column to check the contents of.
        :param whitelist: If a row doesn't match the whitelist, it will be skipped over. See the FilterList alias
            description for the forms that a whitelist can take.
        :param blacklist: If a row matches the blacklist, it will be skipped over. See the FilterList alias
            description for the forms that a blacklist can take.
        :return: A dict of the values under the specified header, mapping the cell values to the indices that they come
            from.
        """
        values: dict[Any, list[int]] = self.get_values_dict(header, whitelist=whitelist, blacklist=blacklist)
        duplicates: dict[Any, list[int]] = {}
        for value, indices in values.items():
            if len(indices) > 1:
                duplicates.update({value: indices})
        return duplicates

    def get_by_function(self, func: Callable[[int, dict[str, Any]], bool],
                        *, whitelist: FilterList = None, blacklist: FilterList = None) -> list[int]:
        """
        Get the index of every row where some function returns true. This can be used for more complex validation than
        checking that a value is present or avoiding duplicates. Look at functions in this class like get_inside_range
        or get_in_List to see how this can be used. These example functions only check the contents of a single header,
        but you could create a function that checks across multiple headers as well.

        :param func: A callable function where the input is the data for a row and the output is a boolean.
        :param whitelist: If a row doesn't match the whitelist, it will be skipped over. See the FilterList alias
            description for the forms that a whitelist can take.
        :param blacklist: If a row matches the blacklist, it will be skipped over. See the FilterList alias
            description for the forms that a blacklist can take.
        :return: The index of every row where the provided function returns true.
        """
        indices: list[int] = []
        for i, row in enumerate(self.file_data):
            if self.skip_row(i, row, whitelist, blacklist):
                continue
            if func(i, row):
                indices.append(i)
        return indices

    def get_inside_range(self, header: str, min_val: float | int, max_val: float | int,
                         *, whitelist: FilterList = None, blacklist: FilterList = None) -> list[int]:
        """
        Get the index of every row with a value under the header inside a range defined by the min and max values.
        This range check is inclusive (i.e. min <= x <= max).

        :param header: The header of the column to check the contents of.
        :param min_val: The minimum allowed value of the cell.
        :param max_val: The maximum allowed value of the cell.
        :param whitelist: If a row doesn't match the whitelist, it will be skipped over. See the FilterList alias
            description for the forms that a whitelist can take.
        :param blacklist: If a row matches the blacklist, it will be skipped over. See the FilterList alias
            description for the forms that a blacklist can take.
        :return: The index of every row with a value under the specified header inside the range.
        """
        def func(index: int, row: dict[str, Any]) -> bool:
            nonlocal header, min_val, max_val
            return min_val <= row.get(header) <= max_val

        return self.get_by_function(func, whitelist=whitelist, blacklist=blacklist)

    def get_outside_range(self, header: str, min_val: float | int, max_val: float | int,
                          *, whitelist: FilterList = None, blacklist: FilterList = None) -> list[int]:
        """
        Get the index of every row with a value under the header inside a range defined by the min and max values.
        This range check is exclusive (i.e. x < min or max < x).

        :param header: The header of the column to check the contents of.
        :param min_val: The value that the cell may be lesser than.
        :param max_val: The value that the cell may be greater than.
        :param whitelist: If a row doesn't match the whitelist, it will be skipped over. See the FilterList alias
            description for the forms that a whitelist can take.
        :param blacklist: If a row matches the blacklist, it will be skipped over. See the FilterList alias
            description for the forms that a blacklist can take.
        :return: The index of every row with a value under the specified header outside the range.
        """
        def func(index: int, row: dict[str, Any]) -> bool:
            value = row.get(header)
            return value < min_val or value > max_val

        return self.get_by_function(func, whitelist=whitelist, blacklist=blacklist)

    def get_in_list(self, header: str, values: list[Any],
                    *, whitelist: FilterList = None, blacklist: FilterList = None) -> list[int]:
        """
        Get the index of every row with a value under the header that is within a given list.

        :param header: The header of the column to check the contents of.
        :param values: A list of values to check the header cells against.
        :param whitelist: If a row doesn't match the whitelist, it will be skipped over. See the FilterList alias
            description for the forms that a whitelist can take.
        :param blacklist: If a row matches the blacklist, it will be skipped over. See the FilterList alias
            description for the forms that a blacklist can take.
        :return: The index of every row with a value under the specified header inside the list.
        """
        return self.get_by_function(lambda i, row: row.get(header) in values, whitelist=whitelist, blacklist=blacklist)

    def get_not_in_list(self, header: str, values: list[Any],
                        *, whitelist: FilterList = None, blacklist: FilterList = None) -> list[int]:
        """
        Get the index of every row with a value under the header that is not within a given list.

        :param header: The header of the column to check the contents of.
        :param values: A list of values to check the header cells against.
        :param whitelist: If a row doesn't match the whitelist, it will be skipped over. See the FilterList alias
            description for the forms that a whitelist can take.
        :param blacklist: If a row matches the blacklist, it will be skipped over. See the FilterList alias
            description for the forms that a blacklist can take.
        :return: The index of every row with a value under the specified header not inside the range.
        """
        return self.get_by_function(lambda i, row: row.get(header) not in values, whitelist=whitelist, blacklist=blacklist)

    def get_matches(self, header: str, pattern: str | re.Pattern[str],
                    *, whitelist: FilterList = None, blacklist: FilterList = None) -> list[int]:
        """
        Get the index of every row with a value under the given header than matches a regex pattern. Unless you set up
        your regex pattern to require that the entire string must match, can return rows where only a substring of
        the cell matches.

        :param header: The header of the column to check the contents of.
        :param pattern: A regex pattern to run on the cells.
        :param whitelist: If a row doesn't match the whitelist, it will be skipped over. See the FilterList alias
            description for the forms that a whitelist can take.
        :param blacklist: If a row matches the blacklist, it will be skipped over. See the FilterList alias
            description for the forms that a blacklist can take.
        :return: The index of every row with a value under the specified header that matches the regex pattern.
        """
        def func(index: int, row: dict[str, Any]) -> bool:
            return len(re.findall(pattern, row.get(header))) > 0

        return self.get_by_function(func, whitelist=whitelist, blacklist=blacklist)

    def get_mismatches(self, header: str, pattern: str | re.Pattern[str],
                       *, whitelist: FilterList = None, blacklist: FilterList = None) -> list[int]:
        """
        Get the index of every row with a value under the given header than doesn't match a regex pattern.

        :param header: The header of the column to check the contents of.
        :param pattern: A regex pattern to run on the cells.
        :param whitelist: If a row doesn't match the whitelist, it will be skipped over. See the FilterList alias
            description for the forms that a whitelist can take.
        :param blacklist: If a row matches the blacklist, it will be skipped over. See the FilterList alias
            description for the forms that a blacklist can take.
        :return: The index of every row with a value under the specified header that doesn't match the regex pattern.
        """
        def func(index: int, row: dict[str, Any]) -> bool:
            return len(re.findall(pattern, row.get(header))) == 0

        return self.get_by_function(func, whitelist=whitelist, blacklist=blacklist)

    def set_defaults(self, header: str, value: Any,
                     *, whitelist: FilterList = None, blacklist: FilterList = None) -> None:
        """
        For all rows which are returned by the empty_cells function, set their value to some default. Useful for when
        a file may have "optional" headers and some default value is assumed if no value is given in the file.

        :param header: The header of the column to update the contents of.
        :param value: The value to set empty cells to.
        :param whitelist: If a row doesn't match the whitelist, it will be skipped over. See the FilterList alias
            description for the forms that a whitelist can take.
        :param blacklist: If a row matches the blacklist, it will be skipped over. See the FilterList alias
            description for the forms that a blacklist can take.
        """
        indices: list[int] = self.empty_cells(header, whitelist=whitelist, blacklist=blacklist)
        rows: list[dict[str, Any]] = self.get_rows(indices)
        for row in rows:
            row.update({header: value})

    def for_each(self, func: Callable[[int, dict[str, Any]], None],
                 *, whitelist: FilterList = None, blacklist: FilterList = None) -> None:
        """
        Run a function on rows in the file data. It is expected that the function updates values of the row, although
        this doesn't need to be the case. Look at functions in this class like update_timestamps or update_lists to see
        how this can be used.

        :param func: A callable function where the input is the index and data for a row. Has no output.
        :param whitelist: If a row doesn't match the whitelist, it will be skipped over. See the FilterList alias
            description for the forms that a whitelist can take.
        :param blacklist: If a row matches the blacklist, it will be skipped over. See the FilterList alias
            description for the forms that a blacklist can take.
        """
        for i, row in enumerate(self.file_data):
            if self.skip_row(i, row, whitelist, blacklist):
                continue
            func(i, row)

    def update_timestamps(self, header: str, time_format: str, timezone: str | int | None = None,
                          *, whitelist: FilterList = None, blacklist: FilterList = None) -> None:
        """
        Given a header whose contents contain integer timestamps since the epoch, convert them to human-readable
        date/time strings for a given format.

        :param header: The header of the column to update the contents of.
        :param time_format: The time format to convert the timestamp to. See TimeUtil for specifics.
        :param timezone: The timezone of the timestamp to convert from. If not specified, uses whatever timezone was
            set as the default by the TimeUtil class elsewhere in your project.
        :param whitelist: If a row doesn't match the whitelist, it will be skipped over. See the FilterList alias
            description for the forms that a whitelist can take.
        :param blacklist: If a row matches the blacklist, it will be skipped over. See the FilterList alias
            description for the forms that a blacklist can take.
        """
        def func(index: int, row: dict[str, Any]) -> None:
            row.update({header: TimeUtil.millis_to_format(row.get(header), time_format, timezone)})

        self.for_each(func, whitelist=whitelist, blacklist=blacklist)

    def update_dates(self, header: str, time_format: str, timezone: str | int | None = None,
                     *, whitelist: FilterList = None, blacklist: FilterList = None) -> None:
        """
        Given a header whose contents contain human-readable date/time strings for a given format, convert them to
        integer timestamps since the epoch.

        :param header: The header of the column to update the contents of.
        :param time_format: The time format to convert the timestamp from. See TimeUtil for specifics.
        :param timezone: The timezone of the time point to convert from. If not specified, uses whatever timezone was
            set as the default by the TimeUtil class elsewhere in your project.
        :param whitelist: If a row doesn't match the whitelist, it will be skipped over. See the FilterList alias
            description for the forms that a whitelist can take.
        :param blacklist: If a row matches the blacklist, it will be skipped over. See the FilterList alias
            description for the forms that a blacklist can take.
        """
        def func(index: int, row: dict[str, Any]) -> None:
            row.update({header: TimeUtil.format_to_millis(row.get(header), time_format, timezone)})

        self.for_each(func, whitelist=whitelist, blacklist=blacklist)

    def update_lists(self, header: str, separator: str = ",",
                     *, whitelist: FilterList = None, blacklist: FilterList = None) -> None:
        """
        Given a header whose contents contain strings representing a list of values, convert them to a list of strings
        by splitting the contents on a separator.

        :param header: The header of the column to update the contents of.
        :param separator: The separator to split the cell values on.
        :param whitelist: If a row doesn't match the whitelist, it will be skipped over. See the FilterList alias
            description for the forms that a whitelist can take.
        :param blacklist: If a row matches the blacklist, it will be skipped over. See the FilterList alias
            description for the forms that a blacklist can take.
        """
        def func(index: int, row: dict[str, Any]) -> None:
            row.update({header: row.get(header).split(separator)})

        self.for_each(func, whitelist=whitelist, blacklist=blacklist)

    def replace_values(self, header: str, replacements: dict[Any, Any],
                       *, whitelist: FilterList = None, blacklist: FilterList = None) -> None:
        """
        For every cell under a header, if the value in the cell is equivalent ot a key in the replacements set, then
        set that cell to the value for that key.

        :param header: The header of the column to update the contents of.
        :param replacements: A dictionary of values to replace to values to replace them with.
        :param whitelist: If a row doesn't match the whitelist, it will be skipped over. See the FilterList alias
            description for the forms that a whitelist can take.
        :param blacklist: If a row matches the blacklist, it will be skipped over. See the FilterList alias
            description for the forms that a blacklist can take.
        """
        def func(index: int, row: dict[str, Any]) -> None:
            value: Any = row.get(header)
            if value in replacements:
                row.update({header: replacements.get(value)})

        self.for_each(func, whitelist=whitelist, blacklist=blacklist)

    def expand_values(self, header: str, expansions: dict[str, str],
                      *, whitelist: FilterList = None, blacklist: FilterList = None) -> None:
        """
        Given a header whose contents contain strings, if the string contains any of the keys in the expansions dict,
        replace that substring of the cell with the value for that key. For example, a cell that contains "horse" with
        a dict {"r": "u"} would result in a cell being updated to read "house".

        Expansions are recursive; e.g. "horse" with the dict {"r": "u", "u": "r"} would replace the "r" with "u"
        would then replace that "u" with "r", resulting in no change.

        :param header: The header of the column to update the contents of.
        :param expansions: A dictionary of values to replace to values to replace them with.
        :param whitelist: If a row doesn't match the whitelist, it will be skipped over. See the FilterList alias
            description for the forms that a whitelist can take.
        :param blacklist: If a row matches the blacklist, it will be skipped over. See the FilterList alias
            description for the forms that a blacklist can take.
        """
        def func(index: int, row: dict[str, Any]) -> None:
            value: str = row.get(header)
            for key in expansions:
                if key in value:
                    value = value.replace(key, expansions.get(key))
                    row.update({header: value})

        self.for_each(func, whitelist=whitelist, blacklist=blacklist)

    def match_records(self, header: str, field: str, records: list[SapioRecord]) -> dict[SapioRecord, dict[str, Any]]:
        """
        Match a list of records to rows in the file given a header and field to match on.

        The expectation is that no two records have the same value for the given field and that no two rows in the file
        map to the same record. It is allowable that a record may have no matching row in the file.

        :param header: The header of the column to check against.
        :param field: The data field name on the records to check against.
        :param records: The records to map to the file rows.
        :return: A dict of record to the row where that record's field value matches the row's value under the header.
        """
        mapped_records: dict[Any, SapioRecord] = RecordHandler.map_by_unique_field(records, field)
        matches: dict[SapioRecord, dict[str, Any]] = {}
        for row in self.file_data:
            value: Any = row.get(header)
            record: SapioRecord = mapped_records.get(value)
            if record:
                if record in matches:
                    raise SapioException(f"The header {header} value {value} matches with multiple records in the "
                                         f"given list of records.")
                matches.update({record: row})
        return matches

    def update_records(self, match_header: str, match_field: str, records: list[SapioRecord],
                       header_to_fields: dict[str, str]) -> None:
        """
        Match a list of records to rows in the file given a header and field ot match on, then update the fields of
        those records using values from the column of the matching row.

        The expectation is that no two records have the same value for the given field and that no two rows in the file
        map to the same record. It is allowable that a record may have no matching row in the file.

        :param match_header: The header of the column to match against.
        :param match_field: The data field name on the records to match against.
        :param records: The records to update.
        :param header_to_fields: A dict of file header to record field name to.
        """
        records_to_row: dict[SapioRecord, dict[str, Any]] = self.match_records(match_header, match_field, records)
        for record, row in records_to_row.items():
            for header, field in header_to_fields.items():
                record.set_field_value(field, row.get(header))

    def find_missing_values(self, header: str, field: str, records: list[SapioRecord]) -> list[int]:
        """
        Given a header and a list of records with a field to check, return every value that is present in the file
        but is not present in the record fields.

        :param header: The header of the column to check against.
        :param field: The data field name on the records to check against.
        :param records: The records to check if their values exist in the file.
        :return: A list of row indices for rows that contain a value that isn't present in the given records.
        """
        missing: list[int] = []
        values: list[Any] = [x.get_field_value(field) for x in records]
        for i, row in enumerate(self.file_data):
            if row.get(header) not in values:
                missing.append(i)
        return missing

    def get_differences(self, diff_check: list[dict[str, Any]], headers: list[str]) -> dict[str, list[int]]:
        """
        Given a list of dictionaries and a list of headers to check, return an index of every row where the values
        in the file and the values in the given list differ. The given list should be the same size as the file. Rows
        in the file are compared against the matching index in the diff check list.

        :param diff_check: A list of dictionaries similar to the list used to initialize this FileDataHandler. The
            number of elements in this list should be equivalent to the number of elements in hte initializing list.
            This list's dicts do not necessarily need to have all the same headers as the initializing dicts, but both
            should have the headers that are in the headers parameter.
        :param headers: A list of the specific headers that should be difference checked.
        :return: A dictionary of headers to a list of indices for the rows that differed between the file and input.
        """
        differences: dict[str, list[int]] = {}
        for i, (row, other_row) in enumerate(zip(self.file_data, diff_check, strict=True)):
            for header in headers:
                if row.get(header) != other_row.get(header):
                    differences.setdefault(header, []).append(i)
        return differences

    def get_differences_for_index(self, index: int, diff_check: dict[str, Any], headers: list[str]) -> list[str]:
        """
        Given a row index, a dictionary , and a list of headers to check, return the headers where the values
        in the row at the given index and the values in the given dict differ.

        :param index: The index of the row to check against the given dict.
        :param diff_check: A dictionary similar to the dictionaries in the list used to initialize this FileDataHandler.
            This dict does not necessarily need to have all the same headers as the initializing dicts, but both
            should have the headers that are in the headers parameter.
        :param headers: A list of the specific headers that should be difference checked.
        :return: A list of headers that differed between the file and input.
        """
        differences: list[str] = []
        row: dict[str, Any] = self.get_row(index)
        for header in headers:
            if row.get(header) != diff_check.get(header):
                differences.append(header)
        return differences

    def get_differences_for_record(self, row: dict[str, Any] | int, record: SapioRecord,
                                   field_mappings: dict[str, str]) -> list[str]:
        """
        Given a row, a record, and a dictionary mapping headers in the row to fields on the record, return a list of
        all file headers where the value in the file differs from the value in the record.

        :param row: A row from the file, either as a dictionary or an integer for the row's index.
        :param record: A record to compare against.
        :param field_mappings: A dictionary that maps header names in the file to field names on the record.
        :return: A list of file headers where the file and record have different values.
        """
        if isinstance(row, int):
            row: dict[str, Any] = self.get_row(row)

        differences: list[str] = []
        for header, field in field_mappings.items():
            if row.get(header) != record.get_field_value(field):
                differences.append(header)
        return differences

    @staticmethod
    def skip_row(i: int, row: dict[str, Any], whitelist: FilterList, blacklist: FilterList) -> bool:
        """
        Determine whether a row should be skipped given whitelist and blacklist filters.

        :param i: The index of the row.
        :param row: The file data of the row.
        :param whitelist: If a row doesn't match the whitelist, it will be skipped over. See the FilterList alias
            description for the forms that a whitelist can take.
        :param blacklist: If a row matches the blacklist, it will be skipped over. See the FilterList alias
            description for the forms that a blacklist can take.
        :return: Whether the row should be skipped.
        """
        if whitelist is not None:
            if isinstance(whitelist, (list, range)):
                return i not in whitelist
            return whitelist(i, row)
        if blacklist is not None:
            if isinstance(blacklist, (list, range)):
                return i in blacklist
            return blacklist(i, row)
        return False
