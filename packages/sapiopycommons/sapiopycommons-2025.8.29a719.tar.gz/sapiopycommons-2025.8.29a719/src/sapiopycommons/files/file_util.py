import io
import warnings
import zipfile

import pandas
from numpy import dtype
from pandas import DataFrame
from sapiopylib.rest.pojo.webhook.ClientCallbackRequest import FilePromptRequest, MultiFilePromptRequest, \
    WriteFileRequest, MultiFileRequest
from sapiopylib.rest.pojo.webhook.ClientCallbackResult import FilePromptResult, MultiFilePromptResult
from sapiopylib.rest.pojo.webhook.WebhookContext import SapioWebhookContext
from sapiopylib.rest.pojo.webhook.WebhookResult import SapioWebhookResult

from sapiopycommons.general.exceptions import SapioUserErrorException


# FR-46064 - Initial port of PyWebhookUtils to sapiopycommons.
# FR-46716 - Add comments noting that some functions are deprecated in favor of CallbackUtil.
class FileUtil:
    """
    Utilities for the handling of files, including the requesting of files from the user and the parsing of files into
    tokenized lists. Makes use of Pandas DataFrames for any file parsing purposes.
    """
    # PR-47433: Add a keep_default_na argument to FileUtil.tokenize_csv and FileUtil.tokenize_xlsx so that N/A values
    # don't get returned as NoneType, and add **kwargs in case any other Pandas input parameters need changed by the
    # caller.
    @staticmethod
    def tokenize_csv(file_bytes: bytes, required_headers: list[str] | None = None, header_row_index: int | None = 0,
                     seperator: str = ",", *, encoding: str | None = None, encoding_error: str | None = "strict",
                     exception_on_empty: bool = True, keep_default_na: bool = False, **kwargs) \
            -> tuple[list[dict[str, str]], list[list[str]]]:
        """
        Tokenize a CSV file. The provided file must be uniform. That is, if row 1 has 10 cells, all the rows in the file
        must have 10 cells. Otherwise, the Pandas parser throws a tokenizer exception.

        :param file_bytes: The bytes of the CSV to be parsed.
        :param required_headers: The headers that must be present in the file. If a provided header is missing, raises
            a user error exception.
        :param header_row_index: The row index in the file that the headers are located at. Everything above the header
            row is returned in the metadata list. If input is None, then no row is considered to be the header row,
            meaning that required headers are also ignored if any are provided. By default, the first row (0th index)
            is assumed to be the header row.
        :param seperator: The character that separates cells in the table.
        :param encoding: The encoding used to read the given file bytes. If not provided, uses utf-8. If your file
            contains a non-utf-8 character, then a UnicodeDecodeError will be thrown. If this happens, consider using
            ISO-8859-1 as the encoding, or investigate what encoding would handle the characters in your file.
        :param encoding_error: The error handling behavior if an encoding error is encountered. By default, the behavior
            is "strict", meaning that encoding errors raise an exception. Change this to "ignore" to skip over invalid
            characters or "replace" to replace invalid characters with a ? character. For a full list of options, see
            https://docs.python.org/3/library/codecs.html#error-handlers
        :param exception_on_empty: Throw a user error exception if the provided file bytes result in an empty list in
            the first element of the returned tuple.
        :param keep_default_na: If False, values that are recognized as NaN (e.g. N/A, NA, NaN) will remain as strings.
            If True, these values will be converted to a NoneType value.
        :param kwargs: Additional arguments to be passed to the pandas read_csv function.
        :return: The CSV parsed into a list of dicts where each dict is a row, mapping the headers to the cells for
            that row. Also returns a list of each row above the headers (the metadata), parsed into a list of each cell.
            If the header row index is 0 or None, this list will be empty.
        """
        # Parse the file bytes into two DataFrames. The first is metadata of the file located above the header row,
        # while the second is the body of the file below the header row.
        file_body, file_metadata = FileUtil.csv_to_data_frames(file_bytes, header_row_index, seperator,
                                                               encoding=encoding, encoding_error=encoding_error,
                                                               keep_default_na=keep_default_na, **kwargs)
        # Parse the metadata from above the header row index into a list of lists.
        metadata: list[list[str]] = FileUtil.data_frame_to_lists(file_metadata)
        # Parse the data from the file body into a list of dicts.
        rows: list[dict[str, str]] = FileUtil.data_frame_to_dicts(file_body, required_headers, header_row_index)
        if exception_on_empty and not rows:
            raise SapioUserErrorException("The provided file contains no rows of information below the headers.")
        return rows, metadata

    @staticmethod
    def tokenize_xlsx(file_bytes: bytes, required_headers: list[str] | None = None, header_row_index: int | None = 0,
                      *, exception_on_empty: bool = True, keep_default_na: bool = False, **kwargs) \
            -> tuple[list[dict[str, str]], list[list[str]]]:
        """
        Tokenize an XLSX file row by row.

        :param file_bytes: The bytes of the XLSX to be parsed.
        :param required_headers: The headers that must be present in the file. If a provided header is missing, raises
            a user error exception.
        :param header_row_index: The row index in the file that the headers are located at. Everything above the header
            row is returned in the metadata list. If input is None, then no row is considered to be the header row,
            meaning that required headers are also ignored if any are provided. By default, the first row (0th index)
            is assumed to be the header row.
        :param exception_on_empty: Throw a user error exception if the provided file bytes result in an empty list in
            the first element of the returned tuple.
        :param keep_default_na: If False, values that are recognized as NaN (e.g. N/A, NA, NaN) will remain as strings.
            If True, these values will be converted to a NoneType value.
        :param kwargs: Additional arguments to be passed to the pandas read_excel function.
        :return: The XLSX parsed into a list of dicts where each dict is a row, mapping the headers to the cells for
            that row. Also returns a list of each row above the headers (the metadata), parsed into a list of each cell.
            If the header row index is 0 or None, this list will be empty.
        """
        # Parse the file bytes into two DataFrames. The first is metadata of the file located above the header row,
        # while the second is the body of the file below the header row.
        file_body, file_metadata = FileUtil.xlsx_to_data_frames(file_bytes, header_row_index,
                                                                keep_default_na=keep_default_na, **kwargs)
        # Parse the metadata from above the header row index into a list of lists.
        metadata: list[list[str]] = FileUtil.data_frame_to_lists(file_metadata)
        # Parse the data from the file body into a list of dicts.
        rows: list[dict[str, str]] = FileUtil.data_frame_to_dicts(file_body, required_headers, header_row_index)
        if exception_on_empty and not rows:
            raise SapioUserErrorException("The provided file contains no rows of information below the headers.")
        return rows, metadata

    @staticmethod
    def csv_to_data_frames(file_bytes: bytes, header_row_index: int | None = 0, seperator: str = ",",
                           *, encoding: str | None = None, encoding_error: str | None = "strict",
                           keep_default_na: bool = False, **kwargs) \
            -> tuple[DataFrame, DataFrame | None]:
        """
        Parse the file bytes for a CSV into DataFrames. The provided file must be uniform. That is, if row 1 has 10
        cells, all the rows in the file must have 10 cells. Otherwise, the Pandas parser throws a tokenizer exception.

        :param file_bytes: The bytes of the CSV to be parsed.
        :param header_row_index: The row index in the file that the headers are located at. Everything above the header
            row is returned in the metadata list. If input is None, then no row is considered to be the header row,
            meaning that required headers are also ignored if any are provided. By default, the first row (0th index)
            is assumed to be the header row.
        :param seperator: The character that separates cells in the table.
        :param encoding: The encoding used to read the given file bytes. If not provided, uses utf-8. If your file
            contains a non-utf-8 character, then a UnicodeDecodeError will be thrown. If this happens, consider using
            ISO-8859-1 as the encoding, or investigate what encoding would handle the characters in your file.
        :param encoding_error: The error handling behavior if an encoding error is encountered. By default, the behavior
            is "strict", meaning that encoding errors raise an exception. Change this to "ignore" to skip over invalid
            characters or "replace" to replace invalid characters with a ? character. For a full list of options, see
            https://docs.python.org/3/library/codecs.html#error-handlers
        :param keep_default_na: If False, values that are recognized as NaN (e.g. N/A, NA, NaN) will remain as strings.
            If True, these values will be converted to a NoneType value.
        :param kwargs: Additional arguments to be passed to the pandas read_csv function.
        :return: A tuple of two DataFrames. The first is the frame for the CSV table body, while the second is for the
            metadata from above the header row, or None if there is no metadata.
        """
        file_metadata: DataFrame | None = None
        if header_row_index is not None and header_row_index > 0:
            with io.BytesIO(file_bytes) as file_io:
                # The metadata DataFrame has no headers and only consists of the rows above the header row index.
                # Therefore, we skip every row including and past the header. Don't skip blank rows, as skipping them
                # can throw off the header row index.
                file_metadata = pandas.read_csv(file_io, header=None, dtype=dtype(str),
                                                skiprows=lambda x: x >= header_row_index,
                                                skip_blank_lines=False, sep=seperator, encoding=encoding,
                                                encoding_errors=encoding_error, keep_default_na=keep_default_na,
                                                **kwargs)
        with io.BytesIO(file_bytes) as file_io:
            # The use of the dtype argument is to ensure that everything from the file gets read as a string. Added
            # because some numerical values would get ".0" appended to them, even when casting the DataFrame cell to a
            # string.
            file_body: DataFrame = pandas.read_csv(file_io, header=header_row_index, dtype=dtype(str),
                                                   skip_blank_lines=False, sep=seperator, encoding=encoding,
                                                   keep_default_na=keep_default_na, **kwargs)

        return file_body, file_metadata

    @staticmethod
    def xlsx_to_data_frames(file_bytes: bytes, header_row_index: int | None = 0, *, keep_default_na: bool = False,
                            **kwargs) -> tuple[DataFrame, DataFrame | None]:
        """
        Parse the file bytes for an XLSX into DataFrames.

        :param file_bytes: The bytes of the XLSX to be parsed.
        :param header_row_index: The row index in the file that the headers are located at. Everything above the header
            row is returned in the metadata list. If input is None, then no row is considered to be the header row,
            meaning that required headers are also ignored if any are provided. By default, the first row (0th index)
            is assumed to be the header row.
        :param keep_default_na: If False, values that are recognized as NaN (e.g. N/A, NA, NaN) will remain as strings.
            If True, these values will be converted to a NoneType value.
        :param kwargs: Additional arguments to be passed to the pandas read_excel function.
        :return: A tuple of two DataFrames. The first is the frame for the XLSX table body, while the second is for the
            metadata from above the header row, or None if there is no metadata.
        """
        file_metadata: DataFrame | None = None
        if header_row_index is not None and header_row_index > 0:
            with io.BytesIO(file_bytes) as file_io:
                # The metadata DataFrame has no headers and only consists of the rows above the header row index.
                # Therefore, we skip every row including and past the header.
                file_metadata = pandas.read_excel(file_io, header=None, dtype=dtype(str),
                                                  skiprows=lambda x: x >= header_row_index,
                                                  keep_default_na=keep_default_na, **kwargs)
        with io.BytesIO(file_bytes) as file_io:
            # The use of the dtype argument is to ensure that everything from the file gets read as a string. Added
            # because some numerical values would get ".0" appended to them, even when casting the DataFrame cell to a
            # string.
            file_body: DataFrame = pandas.read_excel(file_io, header=header_row_index, dtype=dtype(str),
                                                     keep_default_na=keep_default_na, **kwargs)

        return file_body, file_metadata

    @staticmethod
    def data_frame_to_lists(data_frame: DataFrame) -> list[list[str]]:
        """
        Parse a Pandas DataFrame to a list of lists. Each outer list is a row, while each inner list is the cells
        for that row.

        :param data_frame: The DataFrame to be parsed.
        :return: The input DataFrame parsed into a row-wise list of lists.
        """
        if data_frame is None:
            return []
        # DataFrames are oriented column-wise instead of row-wise. Read down each column before moving to the next.
        rows: list[list[str]] = []
        for column_key in data_frame.columns:
            column_rows = list(data_frame.get(column_key))
            # If this is the first column (meaning the rows list is empty), initialize the lists for each row.
            if not rows:
                rows.extend([[] for _ in range(len(column_rows))])
            for value, row in zip(column_rows, rows):
                # Strip each value just in case there is leading or trailing whitespace.
                value = str(value).strip()
                # Empty cells get added to the list as None.
                if value == "nan":
                    value = None
                row.append(value)
        return rows

    @staticmethod
    def data_frame_to_dicts(data_frame: DataFrame,
                            required_headers: list[str] = None,
                            header_row_index: int | None = 0) -> list[dict[str, str]]:
        """
        Parse a Pandas DataFrame to a list of dicts. Each list is a row, while each dict is the cells from that row
        keyed by the column header that the cell is under. Capable of requiring that certain headers are present.

        The names of the data_frame.columns values are expected to be the header names.

        :param data_frame: The DataFrame to be parsed.
        :param required_headers: The headers that must be present in the DataFrame. If a header is missing, raises an
            exception. If no headers are provided, doesn't do any enforcement.
        :param header_row_index: The row index in the file that the headers are located at. Only used ot tell the
            user where the headers are expected to be if a required header is not found, given that the input DataFrame
            was created from a parsed file.
        :return: The input DataFrame parsed into a row-wise list of dicts.
        """
        if data_frame is None:
            return []
        # DataFrames are oriented column-wise instead of row-wise. Read down each column before moving to the next.
        rows: list[dict[str, str]] = []
        witnessed_headers: list[str] = []
        for header in data_frame.columns:
            column_rows = list(data_frame.get(header))
            witnessed_headers.append(header)
            # If this is the first column (meaning the rows list is empty), initialize the lists for each row.
            if not rows:
                rows.extend([{} for _ in range(len(column_rows))])
            for value, row in zip(column_rows, rows):
                # Strip each value just in case there is leading or trailing whitespace.
                value = str(value).strip()
                # Empty cells get added to the list as None.
                if value == "nan":
                    value = None
                row.update({header: value})

        # Warn about improper headers. Confirm that the header contains each of the header column names that we want.
        if required_headers is not None:
            # FR-46702: Report all missing headers instead of only the first missing header.
            missing_headers: list[str] = []
            for required in required_headers:
                if required not in witnessed_headers:
                    missing_headers.append("\"" + required + "\"")
            if missing_headers:
                at_row = " at row " + str(header_row_index + 1) if header_row_index is not None else ""
                raise SapioUserErrorException(f"Incorrect file headers or incorrectly formatted table. Header(s) "
                                              f"{', '.join(missing_headers)} not found{at_row}.")

        return rows

    @staticmethod
    def csv_to_xlsx(file_data: bytes | str) -> bytes:
        """
        Convert a CSV file into an XLSX file.

        :param file_data: The CSV file to be converted.
        :return: The bytes of the CSV file converted to an XLSX file.
        """
        with (io.BytesIO(file_data.encode() if isinstance(file_data, str) else file_data)) as csv:
            # Setting header to false makes pandas read the CSV as-is.
            data_frame = pandas.read_csv(csv, sep=",", header=None)

        with io.BytesIO() as output:
            # noinspection PyTypeChecker
            with pandas.ExcelWriter(output, engine='xlsxwriter') as writer:
                # Setting header and index to false makes the CSV convert to an XLSX as-is.
                data_frame.to_excel(writer, sheet_name='Sheet1', header=False, index=False)
            xlsx_data = output.getvalue()
        return xlsx_data

    @staticmethod
    def csv_to_xls(file_data: bytes | str, delimiter: str = ",", newline: str = "\r\n") -> bytes:
        """
        Convert the bytes or string of a .csv file to .xls bytes.

        :param file_data: The .csv bytes or string to convert.
        :param delimiter: The delimiter character separating columns, with "," being the default.
        :param newline: The newline character(s) separating rows, with "\r\n" being the default.
        :return: The bytes of the new .xls file.
        """
        # Import the libraries we'll need locally since we won't be using them anywhere else in the class.
        from xlwt import Workbook, Worksheet

        # Create an Excel workbook along with a worksheet, which is where the data will be written.
        workbook: Workbook = Workbook()
        sheet: Worksheet = workbook.add_sheet("Sheet1")

        # Make sure the file data is in a string format so that we can work with it.
        formatted_data: str = bytes.decode(file_data, "utf-8") if isinstance(file_data, bytes) else file_data

        # Write each row of the file to the .xls sheet.
        rows: list[str] = formatted_data.split(newline)
        for i, row in enumerate(rows):
            values: list[str] = row.split(delimiter)
            for j, value in enumerate(values):
                sheet.write(i, j, value)

        # Save the worksheet data to the byte buffer and return the bytes.
        with io.BytesIO() as buffer:
            workbook.save(buffer)
            file_bytes: bytes = buffer.getvalue()
        return file_bytes

    @staticmethod
    def zip_files(files: dict[str, str | bytes]) -> bytes:
        """
        Create a zip file for a collection of files.

        :param files: A dictionary of file name to file data as a string or bytes.
        :return: The bytes for a zip file containing the input files.
        """
        with io.BytesIO() as zip_buffer:
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for file_name, file_data in files.items():
                    zip_file.writestr(file_name, file_data)
            # PR-47697: Indent the getvalue call into the outer with block. Making the call outside of the with block
            # throws an I/O exception.
            return zip_buffer.getvalue()

    # Deprecated functions:

    # FR-46097 - Add write file request shorthand functions to FileUtil.
    @staticmethod
    def write_file(file_name: str, file_bytes: bytes, *, request_context: str | None = None) -> SapioWebhookResult:
        """
        DEPRECATED: Make use of CallbackUtil as of 24.5.

        Send a file to the client.

        The calling webhook must catch the WriteFileResult that the client will send back.

        :param file_name: The name of the file.
        :param file_bytes: The bytes of the file.
        :param request_context: Context that will be returned to the webhook server in the client callback result.
        :return: A SapioWebhookResult with the write request as its client callback request.
        """
        warnings.warn("FileUtil.write_file is deprecated as of 24.5+. Use CallbackUtil.write_file instead.",
                      DeprecationWarning)
        return SapioWebhookResult(True, client_callback_request=WriteFileRequest(file_bytes, file_name,
                                                                                 request_context))

    @staticmethod
    def write_files(files: dict[str, bytes], *, request_context: str | None = None) -> SapioWebhookResult:
        """
        DEPRECATED: Make use of CallbackUtil as of 24.5.

        Send a collection of files to the client.

        The calling webhook must catch the MultiFileResult that the client will send back.

        :param files: A dictionary of files names to file bytes.
        :param request_context: Context that will be returned to the webhook server in the client callback result.
        :return: A SapioWebhookResult with the write request as its client callback request.
        """
        warnings.warn("FileUtil.write_files is deprecated as of 24.5+. Use CallbackUtil.write_file instead.",
                      DeprecationWarning)
        return SapioWebhookResult(True, client_callback_request=MultiFileRequest(files, request_context))

    @staticmethod
    def request_file(context: SapioWebhookContext, title: str, exts: list[str] = None,
                     *, request_context: str | None = None) \
            -> tuple[SapioWebhookResult | None, str | None, bytes | None]:
        """
        DEPRECATED: Make use of CallbackUtil as of 24.5.

        Request a single file from the user. This function handles the entire client callback interaction for the
        requesting of the file, including if the user cancels the file upload prompt.

        The first time this method is called in the course of an interaction with the client, it will return a webhook
        result containing the client callback to request the file. The second time it is called, it will return the
        file name and bytes from the callback result.

        :param context: The current webhook context.
        :param title: The title of the file prompt dialog.
        :param exts: The allowable file extensions of the uploaded file. If blank, any file can be uploaded. Throws an
            exception if an incorrect file extension is provided.
        :param request_context: Context that will be returned to the webhook server in the client callback result.
        :return: A tuple with the following elements.
            0 - A webhook result that contains a file prompt if this is the first interaction with this request.
            May also contain a result that will terminate the client interaction if the user canceled the prompt.
            1 - The file name of the requested file if the user provided one.
            2 - The file bytes of the requested file if the user provided one.
        """
        warnings.warn("FileUtil.request_file is deprecated as of 24.5+. Use CallbackUtil.request_file instead.",
                      DeprecationWarning)
        client_callback = context.client_callback_result
        result_context: str | None = client_callback.callback_context_data if client_callback else None
        # If the user cancels, terminate the interaction.
        if client_callback is not None and client_callback.user_cancelled:
            return SapioWebhookResult(True), None, None
        # If no extensions were provided, use an empty list for the extensions instead.
        if exts is None:
            exts = []

        # If the client callback isn't a FilePromptResult, then it's either None or some other callback result, meaning
        # we need to send a new request. We may also send a new request if the client callback result is a
        # FilePromptResult, but its callback context doesn't match the provided callback context, meaning it's a
        # result from a different call to request_file.
        is_file_result = isinstance(client_callback, FilePromptResult)
        if not is_file_result or (is_file_result and result_context != request_context):
            prompt = FilePromptRequest(dialog_title=title, file_extension=",".join(exts),
                                       callback_context_data=request_context)
            return SapioWebhookResult(True, client_callback_request=prompt), None, None

        # Get the file from the result. Enforce that the provided data isn't empty, and that the file path ends in
        # one of the allowed extensions.
        # noinspection PyTypeChecker
        result: FilePromptResult = client_callback
        file_path: str | None = result.file_path
        file_bytes: bytes | None = result.file_bytes
        FileUtil.__verify_file(file_path, file_bytes, exts)
        return None, file_path, file_bytes

    @staticmethod
    def request_files(context: SapioWebhookContext, title: str, exts: list[str] = None,
                      *, request_context: str | None = None) \
            -> tuple[SapioWebhookResult | None, dict[str, bytes] | None]:
        """
        DEPRECATED: Make use of CallbackUtil as of 24.5.

        Request multiple files from the user. This function handles the entire client callback interaction for the
        requesting of the files, including if the user cancels the file upload prompt.

        The first time this method is called in the course of an interaction with the client, it will return a webhook
        result containing the client callback to request the files. The second time it is called, it will return each
        file name and bytes from the callback result.

        :param context: The current webhook context.
        :param title: The title of the file prompt dialog.
        :param exts: The allowable file extensions of the uploaded file. If blank, any file can be uploaded. Throws an
            exception if an incorrect file extension is provided.
        :param request_context: Context that will be returned to the webhook server in the client callback result.
        :return: A tuple with the following elements.
            0 - A webhook result that contains a file prompt if this is the first interaction with this request.
            May also contain a result that will terminate the client interaction if the user canceled the prompt.
            1 - A dictionary that maps the file names to the file bytes for each provided file.
        """
        warnings.warn("FileUtil.request_files is deprecated as of 24.5+. Use CallbackUtil.request_files instead.",
                      DeprecationWarning)
        client_callback = context.client_callback_result
        result_context: str | None = client_callback.callback_context_data if client_callback else None
        # If the user cancels, terminate the interaction.
        if client_callback is not None and client_callback.user_cancelled:
            return SapioWebhookResult(True), None
        # If no extensions were provided, use an empty list for the extensions instead.
        if exts is None:
            exts = []

        # If the client callback isn't a MultiFilePromptResult, then it's either None or some other callback result,
        # meaning we need to send a new request. We may also send a new request if the client callback result is a
        # MultiFilePromptResult, but its callback context doesn't match the provided callback context, meaning it's a
        # result from a different call to request_file.
        is_file_result = isinstance(client_callback, MultiFilePromptResult)
        if not is_file_result or (is_file_result and result_context != request_context):
            prompt = MultiFilePromptRequest(dialog_title=title, file_extension=",".join(exts),
                                            callback_context_data=request_context)
            return SapioWebhookResult(True, client_callback_request=prompt), None

        # Get the files from the result. Enforce that the provided data isn't empty, and that the file paths end in
        # one of the allowed extensions.
        # noinspection PyTypeChecker
        result: MultiFilePromptResult = client_callback
        for file_path, file_bytes in result.files.items():
            FileUtil.__verify_file(file_path, file_bytes, exts)
        return None, result.files

    @staticmethod
    def __verify_file(file_path: str, file_bytes: bytes, allowed_extensions: list[str]):
        """
        Verify that the provided file was read (i.e. the file path and file bytes aren't None or empty) and that it
        has the correct file extension. Raises a user error exception if something about the file is incorrect.

        :param file_path: The name of the file to verify.
        :param file_bytes: The bytes of the file to verify.
        :param allowed_extensions: The file extensions that the file path is allowed to have.
        """
        if file_path is None or len(file_path) == 0 or file_bytes is None or len(file_bytes) == 0:
            raise SapioUserErrorException("Empty file provided or file unable to be read.")
        if len(allowed_extensions) != 0:
            matches: bool = False
            for ext in allowed_extensions:
                if file_path.endswith("." + ext.lstrip(".")):
                    matches = True
                    break
            if matches is False:
                raise SapioUserErrorException("Unsupported file type. Expecting the following extension(s): "
                                              + (",".join(allowed_extensions)))
