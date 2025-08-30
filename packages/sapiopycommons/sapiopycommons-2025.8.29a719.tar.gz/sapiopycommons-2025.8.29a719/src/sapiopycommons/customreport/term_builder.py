from typing import Iterable

from sapiopylib.rest.pojo.CustomReport import RawTermOperation, CompositeTermOperation, RawReportTerm, \
    CompositeReportTerm, AbstractReportTerm, FieldCompareReportTerm

from sapiopycommons.general.aliases import DataTypeIdentifier, AliasUtil, FieldIdentifier

# Raw term operations, for comparing field values.
EQ = RawTermOperation.EQUAL_TO_OPERATOR
NEQ = RawTermOperation.NOT_EQUAL_TO_OPERATOR
LT = RawTermOperation.LESS_THAN_OPERATOR
LTE = RawTermOperation.LESS_THAN_OR_EQUAL_OPERATOR
GT = RawTermOperation.GREATER_THAN_OPERATOR
GTE = RawTermOperation.GREATER_THAN_OR_EQUAL_OPERATOR

# Composite term operations, for comparing two terms.
AND = CompositeTermOperation.AND_OPERATOR
OR = CompositeTermOperation.OR_OPERATOR

# Forms that field term values can take.
TermValue = str | int | float | bool | Iterable | None


class TermBuilder:
    """
    A class that allows for the easier constructions of custom report terms.
    """
    data_type: str

    def __init__(self, data_type: DataTypeIdentifier):
        """
        :param data_type: An object that can be used to identify a data type name. Used as the default data type name
            of the terms created from this TermBuilder.
        """
        self.data_type = AliasUtil.to_data_type_name(data_type)

    def all_records_term(self, *, data_type: DataTypeIdentifier | None = None) -> RawReportTerm:
        """
        Create a raw report term that captures all records of the given data type.

        :param data_type: If provided, the data type of this term. If not provided, then the data type that this term
            builder was instantiated with is used.
        :return: A raw report term for "data_type.RecordId >= 0".
        """
        data_type: str = AliasUtil.to_data_type_name(data_type) if data_type else self.data_type
        return RawReportTerm(data_type, "RecordId", GTE, TermBuilder.to_term_val(0))

    def is_term(self, field: FieldIdentifier, value: TermValue,
                *, data_type: DataTypeIdentifier | None = None, trim: bool = False) -> RawReportTerm:
        """
        Create a raw report term for comparing a field value with an equals operation.

        :param field: The data field of this term.
        :param value: The value to compare for this term.
        :param data_type: If provided, the data type of this term. If not provided, then the data type that this term
            builder was instantiated with is used.
        :param trim: Whether the string of the given value should be trimmed of trailing and leading whitespace.
        :return: A raw report term for "data_type.field = value".
        """
        data_type: str = AliasUtil.to_data_type_name(data_type) if data_type else self.data_type
        return RawReportTerm(AliasUtil.to_data_type_name(data_type), AliasUtil.to_data_field_name(field), EQ,
                             TermBuilder.to_term_val(value), trim)

    def not_term(self, field: FieldIdentifier, value: TermValue,
                 *, data_type: DataTypeIdentifier | None = None, trim: bool = False) -> RawReportTerm:
        """
        Create a raw report term for comparing a field value with a not equals operation.

        :param field: The data field of this term.
        :param value: The value to compare for this term.
        :param data_type: If provided, the data type of this term. If not provided, then the data type that this term
            builder was instantiated with is used.
        :param trim: Whether the string of the given value should be trimmed of trailing and leading whitespace.
        :return: A raw report term for "data_type.field != value".
        """
        data_type: str = AliasUtil.to_data_type_name(data_type) if data_type else self.data_type
        return RawReportTerm(AliasUtil.to_data_type_name(data_type), AliasUtil.to_data_field_name(field), NEQ,
                             TermBuilder.to_term_val(value), trim)

    def lt_term(self, field: FieldIdentifier, value: TermValue,
                *, data_type: DataTypeIdentifier | None = None, trim: bool = False) -> RawReportTerm:
        """
        Create a raw report term for comparing a field value with a less than operation.

        :param field: The data field of this term.
        :param value: The value to compare for this term.
        :param data_type: If provided, the data type of this term. If not provided, then the data type that this term
            builder was instantiated with is used.
        :param trim: Whether the string of the given value should be trimmed of trailing and leading whitespace.
        :return: A raw report term for "data_type.field < value".
        """
        data_type: str = AliasUtil.to_data_type_name(data_type) if data_type else self.data_type
        return RawReportTerm(AliasUtil.to_data_type_name(data_type), AliasUtil.to_data_field_name(field), LT,
                             TermBuilder.to_term_val(value), trim)

    def lte_term(self, field: FieldIdentifier, value: TermValue,
                 *, data_type: DataTypeIdentifier | None = None, trim: bool = False) -> RawReportTerm:
        """
        Create a raw report term for comparing a field value with a less than or equal to operation.

        :param field: The data field of this term.
        :param value: The value to compare for this term.
        :param data_type: If provided, the data type of this term. If not provided, then the data type that this term
            builder was instantiated with is used.
        :param trim: Whether the string of the given value should be trimmed of trailing and leading whitespace.
        :return: A raw report term for "data_type.field <= value".
        """
        data_type: str = AliasUtil.to_data_type_name(data_type) if data_type else self.data_type
        return RawReportTerm(AliasUtil.to_data_type_name(data_type), AliasUtil.to_data_field_name(field), LTE,
                             TermBuilder.to_term_val(value), trim)

    def gt_term(self, field: FieldIdentifier, value: TermValue,
                *, data_type: DataTypeIdentifier | None = None, trim: bool = False) -> RawReportTerm:
        """
        Create a raw report term for comparing a field value with a greater than operation.

        :param field: The data field of this term.
        :param value: The value to compare for this term.
        :param data_type: If provided, the data type of this term. If not provided, then the data type that this term
            builder was instantiated with is used.
        :param trim: Whether the string of the given value should be trimmed of trailing and leading whitespace.
        :return: A raw report term for "data_type.field > value".
        """
        data_type: str = AliasUtil.to_data_type_name(data_type) if data_type else self.data_type
        return RawReportTerm(AliasUtil.to_data_type_name(data_type), AliasUtil.to_data_field_name(field), GT,
                             TermBuilder.to_term_val(value), trim)

    def gte_term(self, field: FieldIdentifier, value: TermValue,
                 *, data_type: DataTypeIdentifier | None = None, trim: bool = False) -> RawReportTerm:
        """
        Create a raw report term for comparing a field value with a greater than or equal to operation.

        :param field: The data field of this term.
        :param value: The value to compare for this term.
        :param data_type: If provided, the data type of this term. If not provided, then the data type that this term
            builder was instantiated with is used.
        :param trim: Whether the string of the given value should be trimmed of trailing and leading whitespace.
        :return: A raw report term for "data_type.field >= value".
        """
        data_type: str = AliasUtil.to_data_type_name(data_type) if data_type else self.data_type
        return RawReportTerm(AliasUtil.to_data_type_name(data_type), AliasUtil.to_data_field_name(field), GTE,
                             TermBuilder.to_term_val(value), trim)

    @staticmethod
    def compare_is_term(data_type_A: DataTypeIdentifier, field_A: FieldIdentifier,
                        data_type_B: DataTypeIdentifier, field_B: FieldIdentifier,
                        *, trim: bool = False) -> FieldCompareReportTerm:
        """
        Create a field comparison report term for comparing field values between data types with an equals operation.

        :param data_type_A: The data type for the left side of this term.
        :param field_A: The data field for the left side of this term.
        :param data_type_B: The data type for the right side of this term.
        :param field_B: The data field for the right side of this term.
        :param trim: Whether the field values should be trimmed of trailing and leading whitespace for comparing.
        :return: A field comparison report term for "data_type_A.field_A = data_type_B.field_B".
        """
        return FieldCompareReportTerm(AliasUtil.to_data_type_name(data_type_A), AliasUtil.to_data_field_name(field_A), EQ,
                                      AliasUtil.to_data_type_name(data_type_B), AliasUtil.to_data_field_name(field_B), trim)

    @staticmethod
    def compare_not_term(data_type_A: DataTypeIdentifier, field_A: FieldIdentifier,
                         data_type_B: DataTypeIdentifier, field_B: FieldIdentifier,
                         *, trim: bool = False) -> FieldCompareReportTerm:
        """
        Create a field comparison report term for comparing field values between data types with a not equals operation.

        :param data_type_A: The data type for the left side of this term.
        :param field_A: The data field for the left side of this term.
        :param data_type_B: The data type for the right side of this term.
        :param field_B: The data field for the right side of this term.
        :param trim: Whether the field values should be trimmed of trailing and leading whitespace for comparing.
        :return: A field comparison report term for "data_type_A.field_A != data_type_B.field_B".
        """
        return FieldCompareReportTerm(AliasUtil.to_data_type_name(data_type_A), AliasUtil.to_data_field_name(field_A), NEQ,
                                      AliasUtil.to_data_type_name(data_type_B), AliasUtil.to_data_field_name(field_B), trim)

    @staticmethod
    def compare_lt_term(data_type_A: DataTypeIdentifier, field_A: FieldIdentifier,
                        data_type_B: DataTypeIdentifier, field_B: FieldIdentifier,
                        *, trim: bool = False) -> FieldCompareReportTerm:
        """
        Create a field comparison report term for comparing field values between data types with a less than operation.

        :param data_type_A: The data type for the left side of this term.
        :param field_A: The data field for the left side of this term.
        :param data_type_B: The data type for the right side of this term.
        :param field_B: The data field for the right side of this term.
        :param trim: Whether the field values should be trimmed of trailing and leading whitespace for comparing.
        :return: A field comparison report term for "data_type_A.field_A < data_type_B.field_B".
        """
        return FieldCompareReportTerm(AliasUtil.to_data_type_name(data_type_A), AliasUtil.to_data_field_name(field_A), LT,
                                      AliasUtil.to_data_type_name(data_type_B), AliasUtil.to_data_field_name(field_B), trim)

    @staticmethod
    def compare_lte_term(data_type_A: DataTypeIdentifier, field_A: FieldIdentifier,
                         data_type_B: DataTypeIdentifier, field_B: FieldIdentifier,
                         *, trim: bool = False) -> FieldCompareReportTerm:
        """
        Create a field comparison report term for comparing field values between data types with a less than or equal
        to operation.

        :param data_type_A: The data type for the left side of this term.
        :param field_A: The data field for the left side of this term.
        :param data_type_B: The data type for the right side of this term.
        :param field_B: The data field for the right side of this term.
        :param trim: Whether the field values should be trimmed of trailing and leading whitespace for comparing.
        :return: A field comparison report term for "data_type_A.field_A <= data_type_B.field_B".
        """
        return FieldCompareReportTerm(AliasUtil.to_data_type_name(data_type_A), AliasUtil.to_data_field_name(field_A), LTE,
                                      AliasUtil.to_data_type_name(data_type_B), AliasUtil.to_data_field_name(field_B), trim)

    @staticmethod
    def compare_gt_term(data_type_A: DataTypeIdentifier, field_A: FieldIdentifier,
                        data_type_B: DataTypeIdentifier, field_B: FieldIdentifier,
                        *, trim: bool = False) -> FieldCompareReportTerm:
        """
        Create a field comparison report term for comparing field values between data types with a greater than
        operation.

        :param data_type_A: The data type for the left side of this term.
        :param field_A: The data field for the left side of this term.
        :param data_type_B: The data type for the right side of this term.
        :param field_B: The data field for the right side of this term.
        :param trim: Whether the field values should be trimmed of trailing and leading whitespace for comparing.
        :return: A field comparison report term for "data_type_A.field_A > data_type_B.field_B".
        """
        return FieldCompareReportTerm(AliasUtil.to_data_type_name(data_type_A), AliasUtil.to_data_field_name(field_A), GT,
                                      AliasUtil.to_data_type_name(data_type_B), AliasUtil.to_data_field_name(field_B), trim)

    @staticmethod
    def compare_gte_term(data_type_A: DataTypeIdentifier, field_A: FieldIdentifier,
                         data_type_B: DataTypeIdentifier, field_B: FieldIdentifier,
                         *, trim: bool = False) -> FieldCompareReportTerm:
        """
        Create a field comparison report term for comparing field values between data types with a greater than or
        equal to operation.

        :param data_type_A: The data type for the left side of this term.
        :param field_A: The data field for the left side of this term.
        :param data_type_B: The data type for the right side of this term.
        :param field_B: The data field for the right side of this term.
        :param trim: Whether the field values should be trimmed of trailing and leading whitespace for comparing.
        :return: A field comparison report term for "data_type_A.field_A >= data_type_B.field_B".
        """
        return FieldCompareReportTerm(AliasUtil.to_data_type_name(data_type_A), AliasUtil.to_data_field_name(field_A), GTE,
                                      AliasUtil.to_data_type_name(data_type_B), AliasUtil.to_data_field_name(field_B), trim)

    @staticmethod
    def or_terms(a: AbstractReportTerm, b: AbstractReportTerm, *, is_negated: bool = False) -> CompositeReportTerm:
        """
        Combine two report terms with an OR operation.

        :param a: The first term in the operation.
        :param b: The second term in the operation.
        :param is_negated: Whether the returned term should be negated (i.e. turn this into a nor operation).
        :return: A composite report term for "A or B".
        """
        return CompositeReportTerm(a, OR, b, is_negated)

    @staticmethod
    def and_terms(a: AbstractReportTerm, b: AbstractReportTerm, *, is_negated: bool = False) -> CompositeReportTerm:
        """
        Combine two report terms with an AND operation.

        :param a: The first term in the operation.
        :param b: The second term in the operation.
        :param is_negated: Whether the returned term should be negated (i.e. turn this into a nand operation).
        :return: A composite report term for "A and B".
        """
        return CompositeReportTerm(a, AND, b, is_negated)

    @staticmethod
    def xor_terms(a: AbstractReportTerm, b: AbstractReportTerm, *, is_negated: bool = False) -> CompositeReportTerm:
        """
        Combine two report terms with a XOR operation. Note that a XOR operation doesn't actually exist for custom
        reports. This instead constructs a term that is "(A or B) and !(A and B)", which is equivalent to a XOR
        operation.

        :param a: The first term in the operation.
        :param b: The second term in the operation.
        :param is_negated: Whether the returned term should be negated (i.e. turn this into an XNOR operation).
        :return: A composite report term for "A xor B".
        """
        return TermBuilder.and_terms(TermBuilder.or_terms(a, b),
                                     TermBuilder.and_terms(a, b, is_negated=True),
                                     is_negated=is_negated)

    @staticmethod
    def to_term_val(value: TermValue) -> str:
        """
        Convert the given value to be used in a custom report term to a string. Term values may be strings, integers,
        floats, booleans, or lists of values.

        :param value: A value to be used in a custom report term.
        :return: The provided value formatted as a string that can be used
        """
        # If the given value is already a string, then nothing needs to be done with it.
        if not isinstance(value, str):
            # If the given value is None, then use an empty string for the search instead.
            if value is None:
                value = ""
            # If the given value is an iterable object, then the return value is the contents of that iterable
            # in a comma separated list surrounded by curly braces.
            elif isinstance(value, Iterable):
                # When converting a list of values to a string, values in the list which are already strings should be
                # put in quotation marks so that strings that contain commas do not get split up. All other value
                # types can be simply converted to a string, though.
                def convert_list_value(val: TermValue) -> str:
                    return f"'{val}'" if isinstance(val, str) else str(val)
                value = "{" + ",".join([convert_list_value(x) for x in value]) + "}"
            else:
                # Otherwise, the value is simply cast to a string.
                value = str(value)
        return value
