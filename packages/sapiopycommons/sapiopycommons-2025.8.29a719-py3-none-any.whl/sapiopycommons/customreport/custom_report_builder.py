from sapiopylib.rest.pojo.CustomReport import ReportColumn, CustomReportCriteria, AbstractReportTerm, \
    ExplicitJoinDefinition, RelatedRecordCriteria, QueryRestriction, FieldCompareReportTerm
from sapiopylib.rest.pojo.datatype.FieldDefinition import FieldType

from sapiopycommons.customreport.column_builder import ColumnBuilder
from sapiopycommons.customreport.term_builder import TermBuilder
from sapiopycommons.general.aliases import DataTypeIdentifier, FieldIdentifier, AliasUtil, SapioRecord
from sapiopycommons.general.exceptions import SapioException


class CustomReportBuilder:
    """
    A class used for building custom reports. Look into using the TermBuilder and ColumnBuilder classes for building
    parts of a custom report.
    """
    root_data_type: DataTypeIdentifier
    data_type_name: str
    root_term: AbstractReportTerm | None
    record_criteria: RelatedRecordCriteria
    column_list: list[ReportColumn]
    join_list: list[ExplicitJoinDefinition]

    def __init__(self, root_data_type: DataTypeIdentifier):
        """
        :param root_data_type: An object that can be used to identify a data type name. Used as the root data type name
            of this search.
        """
        self.root_data_type = root_data_type
        self.data_type_name = AliasUtil.to_data_type_name(root_data_type)
        self.root_term = None
        self.record_criteria = RelatedRecordCriteria(QueryRestriction.QUERY_ALL)
        self.column_list = []
        self.join_list = []

    def get_term_builder(self) -> TermBuilder:
        """
        :return: A TermBuilder with a data type matching this report builder's root data type.
        """
        return TermBuilder(self.root_data_type)

    def has_root_term(self) -> bool:
        """
        :return: Whether this report builder has had its root term set.
        """
        return self.root_term is not None

    def set_root_term(self, term: AbstractReportTerm) -> None:
        """
        Set the root term of the report. Use the TermBuilder class to construct the report terms.

        :param term: The term to set as the root term.
        """
        self.root_term = term

    def has_columns(self) -> bool:
        """
        :return: Whether this report builder has any report columns.
        """
        return bool(self.column_list)

    def add_column(self, field: FieldIdentifier, field_type: FieldType = None,
                   *, data_type: DataTypeIdentifier | None = None) -> None:
        """
        Add a column to this report builder.

        :param field: An object that can be used to identify a data field.
        :param field_type: The field type of the provided field. This is only required if the field type cannot be
            determined from the given data type and field, which occurs when the given field is a string and the
            given data type is not a wrapped record model or record model wrapper.
        :param data_type: An object that can be used to identify a data type. If not provided, uses the root data type
            provided when this builder was initialized. You'll only want to specify this value when adding a column
            that is from a different data type than the root data type.
        """
        if data_type is None:
            data_type = self.root_data_type
        self.column_list.append(ColumnBuilder.build_column(data_type, field, field_type))

    def add_columns(self, fields: list[FieldIdentifier], *, data_type: DataTypeIdentifier | None = None) -> None:
        """
        Add columns to this report builder.

        :param fields: A list of objects that can be used to identify data fields.
        :param data_type: An object that can be used to identify a data type. If not provided, uses the root data type
            provided when this builder was initialized. You'll only want to specify this value when adding a column
            that is from a different data type than the root data type.
        """
        for field in fields:
            self.add_column(field, data_type=data_type)

    def set_query_restriction(self, base_record: SapioRecord, search_related: QueryRestriction) -> None:
        """
        Set a restriction on the report for this report builder such that the returned results must be related in
        some way to the provided base record. Without this, the report searches all records in the system that match the
        root term.

        :param base_record: The base record to run the search from.
        :param search_related: Determine the relationship of the related records that can appear in the search, be those
            children, parents, descendants, or ancestors.
        """
        if search_related == QueryRestriction.QUERY_ALL:
            raise SapioException("The search_related must be something other than QUERY_ALL when setting a query restriction.")
        self.record_criteria = RelatedRecordCriteria(search_related,
                                                     AliasUtil.to_record_id(base_record),
                                                     AliasUtil.to_data_type_name(base_record))

    def add_join(self, comparison_term: FieldCompareReportTerm, data_type: DataTypeIdentifier | None = None) -> None:
        """
        Add a join statement to this report builder.

        :param comparison_term: The field comparison term to join with.
        :param data_type: The data type name that this join is on. If not provided, then the left side data type name
            of the comparison term will be the data type that is joined against.
        """
        if data_type is None:
            data_type: str = comparison_term.left_data_type_name
        else:
            data_type: str = AliasUtil.to_data_type_name(data_type)
        self.join_list.append(ExplicitJoinDefinition(data_type, comparison_term))

    def build_report_criteria(self, page_size: int = 0, page_number: int = -1, case_sensitive: bool = False,
                              owner_restriction_set: list[str] = None) -> CustomReportCriteria:
        """
        Generate a CustomReportCriteria using the column list, root term, and root data type from this report builder.
        You can use the CustomReportManager or CustomReportUtil to run the constructed report.

        :param page_size: The page size of the custom report.
        :param page_number: The page number of the current report.
        :param case_sensitive: When searching texts, should the search be case-sensitive?
        :param owner_restriction_set: Specifies to only return records if the record is owned by this list of usernames.
        :return: A CustomReportCriteria from this report builder.
        """
        if not self.has_root_term():
            raise SapioException("Cannot build a report with no root term.")
        if not self.has_columns():
            raise SapioException("Cannot build a report with no columns.")
        return CustomReportCriteria(self.column_list, self.root_term, self.record_criteria, self.data_type_name,
                                    case_sensitive, page_size, page_number, owner_restriction_set, self.join_list)
