from abc import ABC
from copy import copy
from queue import Queue

from sapiopylib.rest.CustomReportService import CustomReportManager
from sapiopylib.rest.DataMgmtService import DataMgmtServer
from sapiopylib.rest.pojo.CustomReport import CustomReportCriteria, CustomReport, RawReportTerm, ReportColumn
from sapiopylib.rest.pojo.datatype.FieldDefinition import FieldType
# noinspection PyProtectedMember
from sapiopylib.rest.utils.autopaging import SapioPyAutoPager, PagerResultCriteriaType, _default_report_page_size, \
    _default_record_page_size
from sapiopylib.rest.utils.recordmodel.PyRecordModel import PyRecordModel
from sapiopylib.rest.utils.recordmodel.RecordModelWrapper import WrappedType

from sapiopycommons.general.aliases import FieldValue, UserIdentifier, AliasUtil, RecordModel
from sapiopycommons.general.custom_report_util import CustomReportUtil
from sapiopycommons.general.exceptions import SapioException
from sapiopycommons.recordmodel.record_handler import RecordHandler


# FR-47389: Create auto pagers for running custom/system/quick reports that return dictionaries or records for each row.
class _DictReportPagerBase(SapioPyAutoPager[CustomReportCriteria, dict[str, FieldValue]], ABC):
    """
    A base class for automatically paging through a report and returning the results as a list of dictionaries.
    """
    _columns: list[ReportColumn]
    _report_man: CustomReportManager

    def __init__(self, user: UserIdentifier, first_page_criteria: CustomReportCriteria):
        self._columns = first_page_criteria.column_list
        super().__init__(AliasUtil.to_sapio_user(user), first_page_criteria)
        self._report_man = DataMgmtServer.get_custom_report_manager(self.user)

    def get_all_at_once(self) -> list[dict[str, FieldValue]]:
        """
        Get the results of all pages. Be cautious of client memory usage.
        """
        if self.has_iterated:
            raise BrokenPipeError("Cannot use this method if the iterator has already been used.")
        return [x for x in self]

    def default_first_page_criteria(self) -> PagerResultCriteriaType:
        raise ValueError("Cannot generate a default first page criteria for custom reports.")

    def get_next_page_result(self) -> tuple[CustomReportCriteria | None, Queue[dict[str, FieldValue]]]:
        report: CustomReport = self._report_man.run_custom_report(self.next_page_criteria)
        queue: Queue[dict[str, FieldValue]] = Queue()
        for row in _process_results(report.result_table, self._columns):
            queue.put(row)
        if report.has_next_page:
            next_page_criteria = copy(self.next_page_criteria)
            next_page_criteria.page_number += 1
            return next_page_criteria, queue
        else:
            return None, queue


class CustomReportDictAutoPager(_DictReportPagerBase):
    """
    A class that automatically pages through a custom report and returns the results as a list of dictionaries.
    """
    def __init__(self, user: UserIdentifier, report_criteria: CustomReportCriteria,
                 page_number: int = 0, page_size: int = _default_report_page_size):
        """
        IMPORTANT NOTICE: Custom reports that are not single data type (i.e. they have terms or columns from multiple
        data types) may not be 100% time accurate. Such reports use the system's ancestor table to retrieve the
        relationships, and this table takes some time to update after relationships are updated, especially for more
        populous data types. If you need 100% time accurate results to the current state of the records and
        relationships in the database, you should query for the records directly instead of using a custom report.

        :param user: The current webhook context or a user object to send requests from.
        :param report_criteria: The custom report criteria to run.
        :param page_number: The page number to start on. The first page is page 0.
        :param page_size: The number of results to return per page.
        """
        first_page_criteria: CustomReportCriteria = copy(report_criteria)
        first_page_criteria.page_number = page_number
        first_page_criteria.page_size = page_size
        super().__init__(user, first_page_criteria)


class SystemReportDictAutoPager(_DictReportPagerBase):
    """
    A class that automatically pages through a system report and returns the results as a list of dictionaries.

    System reports are also known as predefined searches in the system and must be defined in the data designer for
    a specific data type. That is, saved searches created by users cannot be run using this function.
    """
    def __init__(self, user: UserIdentifier, report_name: str,
                 page_number: int = 0, page_size: int = _default_report_page_size):
        """
        IMPORTANT NOTICE: Custom reports that are not single data type (i.e. they have terms or columns from multiple
        data types) may not be 100% time accurate. Such reports use the system's ancestor table to retrieve the
        relationships, and this table takes some time to update after relationships are updated, especially for more
        populous data types. If you need 100% time accurate results to the current state of the records and
        relationships in the database, you should query for the records directly instead of using a custom report.

        :param user: The current webhook context or a user object to send requests from.
        :param report_name: The name of the system report to run.
        :param page_number: The page number to start on. The first page is page 0.
        :param page_size: The number of results to return per page.
        """
        first_page_criteria: CustomReportCriteria = CustomReportUtil.get_system_report_criteria(user, report_name)
        first_page_criteria.page_number = page_number
        first_page_criteria.page_size = page_size
        super().__init__(user, first_page_criteria)


class QuickReportDictAutoPager(_DictReportPagerBase):
    """
    A class that automatically pages through a quick report and returns the results as a list of dictionaries.
    """
    def __init__(self, user: UserIdentifier, report_term: RawReportTerm,
                 page_number: int = 0, page_size: int = _default_report_page_size):
        """
        :param user: The current webhook context or a user object to send requests from.
        :param report_term: The raw report term to use for the quick report.
        :param page_number: The page number to start on. The first page is page 0.
        :param page_size: The number of results to return per page.
        """
        first_page_criteria: CustomReportCriteria = CustomReportUtil.get_quick_report_criteria(user, report_term)
        first_page_criteria.page_number = page_number
        first_page_criteria.page_size = page_size
        super().__init__(user, first_page_criteria)


# CR-47491: Support providing a data type name string to receive PyRecordModels instead of requiring a WrapperType.
class _RecordReportPagerBase(SapioPyAutoPager[CustomReportCriteria, WrappedType | PyRecordModel], ABC):
    """
    A base class for automatically paging through a report and returning the results as a list of records.
    """
    _columns: list[ReportColumn]
    _query_type: type[WrappedType] | str
    _data_type: str
    _rec_handler: RecordHandler
    _report_man: CustomReportManager

    def __init__(self, user: UserIdentifier, first_page_criteria: CustomReportCriteria,
                 wrapper_type: type[WrappedType] | str):
        self._columns = first_page_criteria.column_list
        self._query_type = wrapper_type
        self._data_type = AliasUtil.to_data_type_name(wrapper_type)
        self._rec_handler = RecordHandler(user)
        super().__init__(AliasUtil.to_sapio_user(user), first_page_criteria)
        self._report_man = DataMgmtServer.get_custom_report_manager(self.user)

    def get_all_at_once(self) -> list[RecordModel]:
        """
        Get the results of all pages. Be cautious of client memory usage.
        """
        if self.has_iterated:
            raise BrokenPipeError("Cannot use this method if the iterator has already been used.")
        return [x for x in self]

    def default_first_page_criteria(self) -> PagerResultCriteriaType:
        raise ValueError("Cannot generate a default first page criteria for custom reports.")

    def get_next_page_result(self) -> tuple[CustomReportCriteria | None, Queue[WrappedType] | Queue[PyRecordModel]]:
        report: CustomReport = self._report_man.run_custom_report(self.next_page_criteria)
        queue = Queue()
        id_index: int = -1
        for i, column in enumerate(self._columns):
            if column.data_type_name == self._data_type and column.data_field_name == "RecordId":
                id_index = i
                break
        if id_index == -1:
            raise SapioException(f"This report does not contain a Record ID column for the given record model type "
                                 f"{self._data_type}.")
        ids: set[int] = {row[id_index] for row in report.result_table}
        for row in self._rec_handler.query_models_by_id(self._query_type, ids, page_size=report.page_size):
            queue.put(row)
        if report.has_next_page:
            next_page_criteria = copy(self.next_page_criteria)
            next_page_criteria.page_number += 1
            return next_page_criteria, queue
        else:
            return None, queue


class CustomReportRecordAutoPager(_RecordReportPagerBase):
    """
    A class that automatically pages through a custom report and returns the results as a list of records.
    """
    def __init__(self, user: UserIdentifier, report_criteria: CustomReportCriteria,
                 wrapper_type: type[WrappedType] | str, page_number: int = 0,
                 page_size: int = _default_record_page_size):
        """
        IMPORTANT NOTICE: Custom reports that are not single data type (i.e. they have terms or columns from multiple
        data types) may not be 100% time accurate. Such reports use the system's ancestor table to retrieve the
        relationships, and this table takes some time to update after relationships are updated, especially for more
        populous data types. If you need 100% time accurate results to the current state of the records and
        relationships in the database, you should query for the records directly instead of using a custom report.

        :param user: The current webhook context or a user object to send requests from.
        :param report_criteria: The custom report criteria to run.
        :param wrapper_type: The record model wrapper type or data type name of the records being searched for.
            If a data type name was used instead of a model wrapper, then the returned records will be PyRecordModels
            instead of WrappedRecordModels.
        :param page_number: The page number to start on. The first page is page 0.
        :param page_size: The number of results to return per page.
        """
        first_page_criteria: CustomReportCriteria = copy(report_criteria)
        _add_record_id_column(first_page_criteria, wrapper_type)
        first_page_criteria.page_number = page_number
        first_page_criteria.page_size = page_size
        super().__init__(user, first_page_criteria, wrapper_type)


class SystemReportRecordAutoPager(_RecordReportPagerBase):
    """
    A class that automatically pages through a system report and returns the results as a list of records.

    System reports are also known as predefined searches in the system and must be defined in the data designer for
    a specific data type. That is, saved searches created by users cannot be run using this function.
    """
    def __init__(self, user: UserIdentifier, report_name: str, wrapper_type: type[WrappedType] | str,
                 page_number: int = 0, page_size: int = _default_record_page_size):
        """
        IMPORTANT NOTICE: Custom reports that are not single data type (i.e. they have terms or columns from multiple
        data types) may not be 100% time accurate. Such reports use the system's ancestor table to retrieve the
        relationships, and this table takes some time to update after relationships are updated, especially for more
        populous data types. If you need 100% time accurate results to the current state of the records and
        relationships in the database, you should query for the records directly instead of using a custom report.

        :param user: The current webhook context or a user object to send requests from.
        :param report_name: The name of the system report to run.
        :param wrapper_type: The record model wrapper type or data type name of the records being searched for.
            If a data type name was used instead of a model wrapper, then the returned records will be PyRecordModels
            instead of WrappedRecordModels.
        :param page_number: The page number to start on. The first page is page 0.
        :param page_size: The number of results to return per page.
        """
        first_page_criteria: CustomReportCriteria = CustomReportUtil.get_system_report_criteria(user, report_name)
        _add_record_id_column(first_page_criteria, wrapper_type)
        first_page_criteria.page_number = page_number
        first_page_criteria.page_size = page_size
        super().__init__(user, first_page_criteria, wrapper_type)


class QuickReportRecordAutoPager(_RecordReportPagerBase):
    """
    A class that automatically pages through a quick report and returns the results as a list of records.
    """
    def __init__(self, user: UserIdentifier, report_term: RawReportTerm, wrapper_type: type[WrappedType] | str,
                 page_number: int = 0, page_size: int = _default_record_page_size):
        """
        :param user: The current webhook context or a user object to send requests from.
        :param report_term: The raw report term to use for the quick report.
        :param wrapper_type: The record model wrapper type or data type name of the records being searched for.
            If a data type name was used instead of a model wrapper, then the returned records will be PyRecordModels
            instead of WrappedRecordModels.
        :param page_number: The page number to start on. The first page is page 0.
        :param page_size: The number of results to return per page.
        """
        if report_term.data_type_name != AliasUtil.to_data_type_name(wrapper_type):
            raise SapioException("The data type name of the report term must match the data type name of the wrapper type.")
        first_page_criteria: CustomReportCriteria = CustomReportUtil.get_quick_report_criteria(user, report_term)
        first_page_criteria.page_number = page_number
        first_page_criteria.page_size = page_size
        super().__init__(user, first_page_criteria, wrapper_type)


def _add_record_id_column(report: CustomReportCriteria, wrapper_type: type[WrappedType] | str) -> None:
    """
    Given a custom report criteria, ensure that the report contains a Record ID column for the given record model's
    data type. Add one if it is missing.
    """
    dt: str = AliasUtil.to_data_type_name(wrapper_type)
    # Ensure that the root data type is the one we're looking for.
    report.root_data_type = dt
    # Enforce that the given custom report has a record ID column.
    if not any([x.data_type_name == dt and x.data_field_name == "RecordId" for x in report.column_list]):
        report.column_list.append(ReportColumn(dt, "RecordId", FieldType.LONG))


def _process_results(rows: list[list[FieldValue]], columns: list[ReportColumn]) -> list[dict[str, FieldValue]]:
    """
    Given the results of a report as a list of row values and the report's columns, combine these lists to
    result in a singular list of dictionaries for each row in the results.
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
            row_data.update({header: value})
        if filter_row is False:
            ret.append(row_data)
    return ret
