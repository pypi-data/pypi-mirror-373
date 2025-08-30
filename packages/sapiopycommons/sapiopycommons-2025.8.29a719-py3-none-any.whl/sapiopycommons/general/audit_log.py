from enum import Enum

from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.CustomReport import ReportColumn, CustomReportCriteria

from sapiopycommons.customreport.auto_pagers import CustomReportDictAutoPager
from sapiopycommons.customreport.column_builder import ColumnBuilder
from sapiopycommons.customreport.term_builder import TermBuilder
from sapiopycommons.datatype.pseudo_data_types import AuditLogPseudoDef
from sapiopycommons.general.aliases import RecordIdentifier, AliasUtil, UserIdentifier, FieldIdentifier, FieldValue
from sapiopycommons.general.exceptions import SapioException


class EventType(Enum):
    """An enum to represent the possible event type values with the event type column in the audit log table."""
    ADD = 0
    DELETE = 1
    MODIFY = 2
    INFO = 3
    ERROR = 4
    WARNING = 5
    IMPORT = 6
    GENERATE = 7
    EXPORT = 8
    ADDREF = 9
    REMOVEREF = 10
    ESIGNATURE = 11
    ROLEASSIGNMENT = 12


class AuditLogEntry:
    __event_type: EventType
    __date: int
    __data_type_name: str
    __record_id: int
    __description: str
    __users_login_name: str
    __comment: str
    __data_record_name: str
    __data_field_name: str
    __original_value: str
    __new_value: str

    @property
    def event_type(self) -> EventType:
        return self.__event_type

    @property
    def date(self) -> int:
        return self.__date

    @property
    def data_type_name(self) -> str:
        return self.__data_type_name

    @property
    def record_id(self) -> int:
        return self.__record_id

    @property
    def description(self) -> str:
        return self.__description

    @property
    def users_login_name(self) -> str:
        return self.__users_login_name

    @property
    def comment(self) -> str:
        return self.__comment

    @property
    def data_record_name(self) -> str:
        return self.__data_record_name

    @property
    def data_field_name(self) -> str:
        return self.__data_field_name

    @property
    def original_value(self) -> str:
        return self.__original_value

    @property
    def new_value(self) -> str:
        return self.__new_value

    def __init__(self, report_row: dict[str, FieldValue]):
        self.__event_type = EventType((report_row[AuditLogPseudoDef.EVENT_TYPE__FIELD_NAME.field_name]))
        self.__date = report_row[AuditLogPseudoDef.TIME_STAMP__FIELD_NAME.field_name]
        self.__data_type_name = report_row[AuditLogPseudoDef.DATA_TYPE_NAME__FIELD_NAME.field_name]
        self.__record_id = report_row[AuditLogPseudoDef.RECORD_ID__FIELD_NAME.field_name]
        self.__description = report_row[AuditLogPseudoDef.DESCRIPTION__FIELD_NAME.field_name]
        self.__users_login_name = report_row[AuditLogPseudoDef.USER_NAME__FIELD_NAME.field_name]
        self.__comment = report_row[AuditLogPseudoDef.USER_COMMENT__FIELD_NAME.field_name]
        self.__data_record_name = report_row[AuditLogPseudoDef.RECORD_NAME__FIELD_NAME.field_name]
        self.__data_field_name = report_row[AuditLogPseudoDef.DATA_FIELD_NAME__FIELD_NAME.field_name]
        self.__original_value = report_row[AuditLogPseudoDef.ORIGINAL_VALUE__FIELD_NAME.field_name]
        self.__new_value = report_row[AuditLogPseudoDef.NEW_VALUE__FIELD_NAME.field_name]


class AuditLogUtil:
    user: SapioUser

    def __init__(self, context: UserIdentifier):
        self.user = AliasUtil.to_sapio_user(context)

    @staticmethod
    def report_columns() -> list[ReportColumn]:
        return [
            ColumnBuilder.build_column(AuditLogPseudoDef.DATA_TYPE_NAME, AuditLogPseudoDef.EVENT_TYPE__FIELD_NAME),
            ColumnBuilder.build_column(AuditLogPseudoDef.DATA_TYPE_NAME, AuditLogPseudoDef.TIME_STAMP__FIELD_NAME),
            ColumnBuilder.build_column(AuditLogPseudoDef.DATA_TYPE_NAME, AuditLogPseudoDef.DATA_TYPE_NAME__FIELD_NAME),
            ColumnBuilder.build_column(AuditLogPseudoDef.DATA_TYPE_NAME, AuditLogPseudoDef.RECORD_ID__FIELD_NAME),
            ColumnBuilder.build_column(AuditLogPseudoDef.DATA_TYPE_NAME, AuditLogPseudoDef.DESCRIPTION__FIELD_NAME),
            ColumnBuilder.build_column(AuditLogPseudoDef.DATA_TYPE_NAME, AuditLogPseudoDef.USER_NAME__FIELD_NAME),
            ColumnBuilder.build_column(AuditLogPseudoDef.DATA_TYPE_NAME, AuditLogPseudoDef.USER_COMMENT__FIELD_NAME),
            ColumnBuilder.build_column(AuditLogPseudoDef.DATA_TYPE_NAME, AuditLogPseudoDef.RECORD_NAME__FIELD_NAME),
            ColumnBuilder.build_column(AuditLogPseudoDef.DATA_TYPE_NAME, AuditLogPseudoDef.DATA_FIELD_NAME__FIELD_NAME),
            ColumnBuilder.build_column(AuditLogPseudoDef.DATA_TYPE_NAME, AuditLogPseudoDef.ORIGINAL_VALUE__FIELD_NAME),
            ColumnBuilder.build_column(AuditLogPseudoDef.DATA_TYPE_NAME, AuditLogPseudoDef.NEW_VALUE__FIELD_NAME)
        ]

    @staticmethod
    def create_data_record_audit_log_report(records: list[RecordIdentifier],
                                            fields: list[FieldIdentifier] | None = None) -> CustomReportCriteria:
        """
        This method creates a CustomReportCriteria object for running an audit log query based on data records.

        Creates a CustomReportCriteria object with a query term based on the record ids/records passed into the method.
        Optionally, the fields parameter can be populated to limit the search to particular fields. If the fields
        parameter is not populated, the search will include results for all field changes.

        :param records: The DataRecords, RecordModels, or record ids to base the search on.
        :param fields: The data field names to include changes for.
        :return: The constructed CustomReportCriteria object, which can be used to run a report on the audit log.
        """
        # PR-47701: Throw an exception if no records are provided.
        if not records:
            raise SapioException("No records provided. Please provide at least one record to build a report for.")
        # Build the raw report term querying for any entry with a matching record ID value to the record ID's
        # passed in.
        record_ids = AliasUtil.to_record_ids(records)
        tb = TermBuilder(AuditLogPseudoDef.DATA_TYPE_NAME)
        root_term = tb.is_term(AuditLogPseudoDef.RECORD_ID__FIELD_NAME, record_ids)

        # If the user passed in any specific fields, then we should limit the query to those fields.
        if fields is not None and fields:
            fields: list[str] = AliasUtil.to_data_field_names(fields)
            field_term = tb.is_term(AuditLogPseudoDef.DATA_FIELD_NAME__FIELD_NAME, fields)
            root_term = TermBuilder.and_terms(root_term, field_term)

        return CustomReportCriteria(AuditLogUtil.report_columns(), root_term)

    def run_data_record_audit_log_report(self, records: list[RecordIdentifier],
                                         fields: list[FieldIdentifier] | None = None) \
            -> dict[RecordIdentifier, list[AuditLogEntry]]:
        """
        This method runs a custom report for changes made to the given data records using the audit log.
        See "create_data_record_audit_log_report" for more details about the data record audit log report.

        :param records: The DataRecords, RecordModels, or record ids to base the search on.
        :param fields: The data field names to include changes for.
        :return: A dictionary where the keys are the record identifiers passed in, and the values are a list of
            AuditLogEntry objects which match the record id value of those records.
        """
        # PR-47701: Return an empty dictionary if no records are provided.
        if not records:
            return {}
        # First, we must build our report criteria for running the Custom Report.
        criteria = AuditLogUtil.create_data_record_audit_log_report(records, fields)

        # Then we must run the custom report using that criteria.
        raw_report_data: list[dict[str, FieldValue]] = CustomReportDictAutoPager(self.user, criteria).get_all_at_once()

        # This section will prepare a map matching the original RecordIdentifier by record id.
        # This is because the audit log entries will have record ids, but we want the keys in our result map
        # to match the record identifiers that the user passed in, for convenience.
        record_identifier_mapping: dict[int, RecordIdentifier] = dict()
        for record in records:
            record_id = AliasUtil.to_record_id(record)
            record_identifier_mapping[record_id] = record

        # Finally, we compile our audit data into a map where the keys are the record identifiers passed in,
        # and the value is a list of applicable audit log entries.
        final_audit_data: dict[RecordIdentifier, list[AuditLogEntry]] = dict()
        for audit_entry_data in raw_report_data:
            audit_entry: AuditLogEntry = AuditLogEntry(audit_entry_data)
            identifier: RecordIdentifier = record_identifier_mapping.get(audit_entry.record_id)
            final_audit_data.setdefault(identifier, []).append(audit_entry)

        return final_audit_data
