from sapiopylib.rest.pojo.CustomReport import ReportColumn
from sapiopylib.rest.pojo.datatype.FieldDefinition import FieldType

from sapiopycommons.general.aliases import DataTypeIdentifier, FieldIdentifier, AliasUtil
from sapiopycommons.general.exceptions import SapioException

# The system fields that every record has and their field types. System fields aren't generated as record model fields
# for all platform version, hence the need to create a dict for them in the off chance that they're not present on
# the model wrapper.
SYSTEM_FIELDS: dict[str, FieldType] = {
    "DataRecordName": FieldType.IDENTIFIER,
    "RecordId": FieldType.LONG,
    "DateCreated": FieldType.DATE,
    "CreatedBy": FieldType.STRING,
    "VeloxLastModifiedDate": FieldType.DATE,
    "VeloxLastModifiedBy": FieldType.STRING
}


class ColumnBuilder:
    """
    A class for building report columns for custom reports.
    """
    @staticmethod
    def build_column(data_type: DataTypeIdentifier, field: FieldIdentifier, field_type: FieldType | None = None) \
            -> ReportColumn:
        """
        Build a ReportColumn from a variety of possible inputs.

        :param data_type: An object that can be used to identify a data type.
        :param field: An object that can be used to identify a data field.
        :param field_type: The field type of the provided field. This is only required if the field type cannot be
            determined from the given data type and field, which occurs when the given field is a string and the
            given data type is not a wrapped record model or record model wrapper.
        :return: A ReportColumn for the inputs.
        """
        # Get the data type and field names from the inputs.
        data_type_name = AliasUtil.to_data_type_name(data_type)
        field_name = AliasUtil.to_data_field_name(field)
        if field_type is None:
            field_type = ColumnBuilder.__field_type(data_type, field)
        if field_type is None:
            raise SapioException("The field_type parameter is required for the provided data_type and field inputs.")
        return ReportColumn(data_type_name, field_name, field_type)

    @staticmethod
    def __field_type(data_type: DataTypeIdentifier, field: FieldIdentifier) -> FieldType | None:
        """
        Given a record model wrapper and a field name, return the field type for that field. Accounts for system fields.

        :param data_type: The record model wrapper that the field is on.
        :param field: The field name to return the type of.
        :return: The field type of the given field name.
        """
        # Check if the field name is a system field. If it is, use the field type defined in this file.
        field_name: str = AliasUtil.to_data_field_name(field)
        if field_name in SYSTEM_FIELDS:
            return SYSTEM_FIELDS.get(field_name)
        # Otherwise, check if the field type can be found from the wrapper.
        return AliasUtil.to_field_type(field, data_type)
