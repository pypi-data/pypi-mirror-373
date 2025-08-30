import warnings
from collections.abc import Iterable

from sapiopylib.rest.DataMgmtService import DataMgmtServer
from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.CustomReport import ReportColumn, CustomReport, CustomReportCriteria, RawReportTerm

from sapiopycommons.general.aliases import UserIdentifier, FieldValue, AliasUtil, FieldIdentifierKey


# FR-46064 - Initial port of PyWebhookUtils to sapiopycommons.
class CustomReportUtil:
    @staticmethod
    def run_system_report(context: UserIdentifier,
                          report_name: str,
                          filters: dict[FieldIdentifierKey, Iterable[FieldValue]] | None = None,
                          page_limit: int | None = None,
                          page_size: int | None = None,
                          page_number: int | None = None) -> list[dict[str, FieldValue]]:
        """
        Run a system report and return the results of that report as a list of dictionaries for the values of each
        column in each row.

        System reports are also known as predefined searches in the system and must be defined in the data designer for
        a specific data type. That is, saved searches created by users cannot be run using this function.

        IMPORTANT NOTICE: Custom reports that are not single data type (i.e. they have terms or columns from multiple
        data types) may not be 100% time accurate. Such reports use the system's ancestor table to retrieve the
        relationships, and this table takes some time to update after relationships are updated, especially for more
        populous data types. If you need 100% time accurate results to the current state of the records and
        relationships in the database, you should query for the records directly instead of using a custom report.

        :param context: The current webhook context or a user object to send requests from.
        :param report_name: The name of the system report to run.
        :param filters: If provided, filter the results of the report using the given mapping of headers to values to
            filter on. Only those headers that both the filters and the custom report share will take effect. That is,
            any filters that have a header name that isn't in the custom report will be ignored.
        :param page_limit: The maximum number of pages to query. If None, exhausts all possible pages.
        :param page_size: The size of each page of results in the search. If None, the page size is set by the server,
            which may be unlimited.
        :param page_number: The page number to start the search from, If None, starts on the first page. Note that the
            number of the first page is 0.
        :return: The results of the report listed row by row, mapping each cell to the header it is under. The header
            values in the dicts are the data field names of the columns.
            If two columns in the search have the same data field name but differing data type names, then the
            dictionary key to the value in the column will be "DataTypeName.DataFieldName". For example, if you
            had a Sample column with a data field name of Identifier and a Request column with the same data field name,
            then the dictionary keys for these columns would be Sample.Identifier and Request.Identifier respectively.
        """
        warnings.warn("Deprecated in favor of the SystemReportDictAutoPager class.", DeprecationWarning)
        results: tuple = CustomReportUtil._exhaust_system_report(context, report_name, page_limit,
                                                                 page_size, page_number)
        columns: list[ReportColumn] = results[0]
        rows: list[list[FieldValue]] = results[1]
        return CustomReportUtil._process_results(rows, columns, filters)

    @staticmethod
    def run_custom_report(context: UserIdentifier,
                          report_criteria: CustomReportCriteria,
                          filters: dict[FieldIdentifierKey, Iterable[FieldValue]] | None = None,
                          page_limit: int | None = None,
                          page_size: int | None = None,
                          page_number: int | None = None) -> list[dict[str, FieldValue]]:
        """
        Run a custom report and return the results of that report as a list of dictionaries for the values of each
        column in each row.

        Custom reports are constructed by the caller, specifying the report terms and the columns that will be in the
        results. They are like advanced or predefined searches from the system, except they are constructed from
        within the webhook instead of from within the system.

        IMPORTANT NOTICE: Custom reports that are not single data type (i.e. they have terms or columns from multiple
        data types) may not be 100% time accurate. Such reports use the system's ancestor table to retrieve the
        relationships, and this table takes some time to update after relationships are updated, especially for more
        populous data types. If you need 100% time accurate results to the current state of the records and
        relationships in the database, you should query for the records directly instead of using a custom report.

        :param context: The current webhook context or a user object to send requests from.
        :param report_criteria: The custom report criteria to run.
        :param filters: If provided, filter the results of the report using the given mapping of headers to values to
            filter on. Only those headers that both the filters and the custom report share will take effect. That is,
            any filters that have a header name that isn't in the custom report will be ignored.
            Note that this parameter is only provided for parity with the other run report functions. If you need to
            filter the results of a search, it would likely be more beneficial to have just added a new term to the
            input report criteria that corresponds to the filter.
        :param page_limit: The maximum number of pages to query. If None, exhausts all possible pages.
        :param page_size: The size of each page of results in the search. If None, uses the value from the given report
            criteria. If not None, overwrites the value from the given report criteria.
        :param page_number: The page number to start the search from, If None, uses the value from the given report
            criteria. If not None, overwrites the value from the given report criteria. Note that the number of the
            first page is 0.
        :return: The results of the report listed row by row, mapping each cell to the header it is under. The header
            values in the dicts are the data field names of the columns.
            If two columns in the search have the same data field name but differing data type names, then the
            dictionary key to the value in the column will be "DataTypeName.DataFieldName". For example, if you
            had a Sample column with a data field name of Identifier and a Request column with the same data field name,
            then the dictionary keys for these columns would be Sample.Identifier and Request.Identifier respectively.
        """
        warnings.warn("Deprecated in favor of the CustomReportDictAutoPager class.", DeprecationWarning)
        results: tuple = CustomReportUtil._exhaust_custom_report(context, report_criteria, page_limit,
                                                                 page_size, page_number)
        columns: list[ReportColumn] = results[0]
        rows: list[list[FieldValue]] = results[1]
        return CustomReportUtil._process_results(rows, columns, filters)

    @staticmethod
    def run_quick_report(context: UserIdentifier,
                         report_term: RawReportTerm,
                         filters: dict[FieldIdentifierKey, Iterable[FieldValue]] | None = None,
                         page_limit: int | None = None,
                         page_size: int | None = None,
                         page_number: int | None = None) -> list[dict[str, FieldValue]]:
        """
        Run a quick report and return the results of that report as a list of dictionaries for the values of each
        column in each row.

        Quick reports are helpful for cases where you need to query record field values in a more complex manner than
        the data record manager allows, but still simpler than a full-blown custom report. The columns that are returned
        in a quick search are every visible field from the data type that corresponds to the given report term. (Fields
        which are not marked as visible in the data designer will be excluded.)

        :param context: The current webhook context or a user object to send requests from.
        :param report_term: The raw report term to use for the quick report.
        :param filters: If provided, filter the results of the report using the given mapping of headers to values to
            filter on. Only those headers that both the filters and the custom report share will take effect. That is,
            any filters that have a header name that isn't in the custom report will be ignored.
        :param page_limit: The maximum number of pages to query. If None, exhausts all possible pages.
        :param page_size: The size of each page of results in the search. If None, the page size is set by the server,
            which may be unlimited.
        :param page_number: The page number to start the search from, If None, starts on the first page. Note that the
            number of the first page is 0.
        :return: The results of the report listed row by row, mapping each cell to the header it is under. The header
            values in the dicts are the data field names of the columns.
        """
        warnings.warn("Deprecated in favor of the QuickReportDictAutoPager class.", DeprecationWarning)
        results: tuple = CustomReportUtil._exhaust_quick_report(context, report_term, page_limit,
                                                                page_size, page_number)
        columns: list[ReportColumn] = results[0]
        rows: list[list[FieldValue]] = results[1]
        return CustomReportUtil._process_results(rows, columns, filters)

    @staticmethod
    def get_system_report_criteria(context: UserIdentifier, report_name: str) -> CustomReport:
        """
        Retrieve a custom report from the system given the name of the report. This works by querying the system report
        with a page number of 0 and page size of 1 to minimize the amount of data transfer needed to retrieve the
        report's config.

        System reports are also known as predefined searches in the system and must be defined in the data designer for
        a specific data type. That is, saved searches created by users cannot be run using this function.

        Using this, you can add to the root term of the search to then run a new search, or provide it to client
        callbacks or directives that take CustomReports.

        :param context: The current webhook context or a user object to send requests from.
        :param report_name: The name of the system report to run.
        :return: The CustomReport object for the given system report name.
        """
        user: SapioUser = AliasUtil.to_sapio_user(context)
        report_man = DataMgmtServer.get_custom_report_manager(user)
        return report_man.run_system_report_by_name(report_name, 1, 0)

    @staticmethod
    def get_quick_report_criteria(context: UserIdentifier, report_term: RawReportTerm) -> CustomReport:
        """
        Retrieve a quick report from the system given a report term. This works by making a quick report query
        with a page number of 0 and page size of 1 to minimize the amount of data transfer needed to retrieve the
        report's config.

        Using this, you can add to the root term of the search to then run a new search, or provide it to client
        callbacks or directives that take CustomReports.

        :param context: The current webhook context or a user object to send requests from.
        :param report_term: The raw report term to use for the quick report.
        :return: The CustomReport object for the given report term.
        """
        user: SapioUser = AliasUtil.to_sapio_user(context)
        report_man = DataMgmtServer.get_custom_report_manager(user)
        return report_man.run_quick_report(report_term, 1, 0)

    @staticmethod
    def _exhaust_system_report(context: UserIdentifier,
                               report_name: str,
                               page_limit: int | None,
                               page_size: int | None,
                               page_number: int | None) \
            -> tuple[list[ReportColumn], list[list[FieldValue]]]:
        """
        Given a system report, iterate over every page of the report and collect the results
        until there are no remaining pages.
        """
        user: SapioUser = AliasUtil.to_sapio_user(context)
        report_man = DataMgmtServer.get_custom_report_manager(user)

        # If a page size was provided but no page number was provided, then set the page number to 0,
        # as both parameters are necessary in order to get paged results.
        if page_size is not None and page_number is None:
            page_number = 0

        result = None
        has_next_page: bool = True
        rows: list[list[FieldValue]] = []
        cur_page: int = 1
        while has_next_page and (not page_limit or cur_page <= page_limit):
            result = report_man.run_system_report_by_name(report_name, page_size, page_number)
            page_size = result.page_size
            page_number = result.page_number + 1
            has_next_page = result.has_next_page
            rows.extend(result.result_table)
            cur_page += 1
        return result.column_list, rows

    @staticmethod
    def _exhaust_custom_report(context: UserIdentifier,
                               report: CustomReportCriteria,
                               page_limit: int | None,
                               page_size: int | None,
                               page_number: int | None) \
            -> tuple[list[ReportColumn], list[list[FieldValue]]]:
        """
        Given a custom report, iterate over every page of the report and collect the results
        until there are no remaining pages.
        """
        user: SapioUser = AliasUtil.to_sapio_user(context)
        report_man = DataMgmtServer.get_custom_report_manager(user)

        # If a page size was provided but no page number was provided, then set the page number to 0,
        # as both parameters are necessary in order to get paged results.
        if page_size is not None and page_number is None:
            page_number = 0

        result = None
        if page_size is not None:
            report.page_size = page_size
        if page_number is not None:
            report.page_number = page_number
        has_next_page: bool = True
        rows: list[list[FieldValue]] = []
        cur_page: int = 1
        while has_next_page and (not page_limit or cur_page <= page_limit):
            result = report_man.run_custom_report(report)
            report.page_size = result.page_size
            report.page_number = result.page_number + 1
            has_next_page = result.has_next_page
            rows.extend(result.result_table)
            cur_page += 1
        return result.column_list, rows

    @staticmethod
    def _exhaust_quick_report(context: UserIdentifier,
                              report_term: RawReportTerm,
                              page_limit: int | None,
                              page_size: int | None,
                              page_number: int | None) \
            -> tuple[list[ReportColumn], list[list[FieldValue]]]:
        """
        Given a quick report, iterate over every page of the report and collect the results
        until there are no remaining pages.
        """
        user: SapioUser = AliasUtil.to_sapio_user(context)
        report_man = DataMgmtServer.get_custom_report_manager(user)

        # If a page size was provided but no page number was provided, then set the page number to 0,
        # as both parameters are necessary in order to get paged results.
        if page_size is not None and page_number is None:
            page_number = 0

        result = None
        has_next_page: bool = True
        rows: list[list[FieldValue]] = []
        cur_page: int = 1
        while has_next_page and (not page_limit or cur_page <= page_limit):
            result = report_man.run_quick_report(report_term, page_size, page_number)
            page_size = result.page_size
            page_number = result.page_number + 1
            has_next_page = result.has_next_page
            rows.extend(result.result_table)
            cur_page += 1
        return result.column_list, rows

    @staticmethod
    def _process_results(rows: list[list[FieldValue]], columns: list[ReportColumn],
                         filters: dict[FieldIdentifierKey, Iterable[FieldValue]] | None) -> list[dict[str, FieldValue]]:
        """
        Given the results of a report as a list of row values and the report's columns, combine these lists to
        result in a singular list of dictionaries for each row in the results.

        If any filter criteria has been provided, also use that to filter the row.
        """
        # It may be the case that two columns have the same data field name but differing data type names.
        # If this occurs, then we need to be able to differentiate these columns in the resulting dictionary.
        prepend_dt: set[str] = set()
        encountered_names: list[str] = []
        for column in columns:
            field_name: str = column.data_field_name
            if field_name in encountered_names:
                prepend_dt.add(field_name)
            else:
                encountered_names.append(field_name)

        if filters:
            filters: dict[str, Iterable[FieldValue]] = AliasUtil.to_data_field_names_dict(filters)

        ret: list[dict[str, FieldValue]] = []
        for row in rows:
            row_data: dict[str, FieldValue] = {}
            filter_row: bool = False
            for value, column in zip(row, columns):
                header: str = column.data_field_name
                # If two columns share the same data field name, prepend the data type name of the column to the
                # data field name.
                if header in prepend_dt:
                    header = column.data_type_name + "." + header
                if filters is not None and header in filters and value not in filters.get(header):
                    filter_row = True
                    break
                row_data.update({header: value})
            if filter_row is False:
                ret.append(row_data)
        return ret
