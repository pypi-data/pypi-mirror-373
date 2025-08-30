from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FieldTypePbo(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FIELD_TYPE_UNSPECIFIED: _ClassVar[FieldTypePbo]
    BOOLEAN: _ClassVar[FieldTypePbo]
    DOUBLE: _ClassVar[FieldTypePbo]
    ENUM: _ClassVar[FieldTypePbo]
    LONG: _ClassVar[FieldTypePbo]
    INTEGER: _ClassVar[FieldTypePbo]
    SHORT: _ClassVar[FieldTypePbo]
    STRING: _ClassVar[FieldTypePbo]
    DATE: _ClassVar[FieldTypePbo]
    ACTION: _ClassVar[FieldTypePbo]
    SELECTION: _ClassVar[FieldTypePbo]
    PARENTLINK: _ClassVar[FieldTypePbo]
    IDENTIFIER: _ClassVar[FieldTypePbo]
    PICKLIST: _ClassVar[FieldTypePbo]
    LINK: _ClassVar[FieldTypePbo]
    MULTIPARENTLINK: _ClassVar[FieldTypePbo]
    CHILDLINK: _ClassVar[FieldTypePbo]
    AUTO_ACCESSION: _ClassVar[FieldTypePbo]
    DATE_RANGE: _ClassVar[FieldTypePbo]
    SIDE_LINK: _ClassVar[FieldTypePbo]
    ACTION_STRING: _ClassVar[FieldTypePbo]
    FILE_BLOB: _ClassVar[FieldTypePbo]

class SortDirectionPbo(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SORT_DIRECTION_UNSPECIFIED: _ClassVar[SortDirectionPbo]
    SORT_DIRECTION_ASCENDING: _ClassVar[SortDirectionPbo]
    SORT_DIRECTION_DESCENDING: _ClassVar[SortDirectionPbo]
    SORT_DIRECTION_NONE: _ClassVar[SortDirectionPbo]

class FontSizePbo(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FONT_SIZE_UNSPECIFIED: _ClassVar[FontSizePbo]
    FONT_SIZE_SMALL: _ClassVar[FontSizePbo]
    FONT_SIZE_MEDIUM: _ClassVar[FontSizePbo]
    FONT_SIZE_LARGE: _ClassVar[FontSizePbo]

class TextDecorationPbo(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TEXT_DECORATION_UNSPECIFIED: _ClassVar[TextDecorationPbo]
    TEXT_DECORATION_NONE: _ClassVar[TextDecorationPbo]
    TEXT_DECORATION_UNDERLINE: _ClassVar[TextDecorationPbo]
    TEXT_DECORATION_STRIKETHROUGH: _ClassVar[TextDecorationPbo]

class StringFormatPbo(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STRING_FORMAT_UNSPECIFIED: _ClassVar[StringFormatPbo]
    STRING_FORMAT_PHONE: _ClassVar[StringFormatPbo]
    STRING_FORMAT_EMAIL: _ClassVar[StringFormatPbo]

class DoubleFormatPbo(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DOUBLE_FORMAT_UNSPECIFIED: _ClassVar[DoubleFormatPbo]
    DOUBLE_FORMAT_CURRENCY: _ClassVar[DoubleFormatPbo]
    DOUBLE_FORMAT_PERCENTAGE: _ClassVar[DoubleFormatPbo]
FIELD_TYPE_UNSPECIFIED: FieldTypePbo
BOOLEAN: FieldTypePbo
DOUBLE: FieldTypePbo
ENUM: FieldTypePbo
LONG: FieldTypePbo
INTEGER: FieldTypePbo
SHORT: FieldTypePbo
STRING: FieldTypePbo
DATE: FieldTypePbo
ACTION: FieldTypePbo
SELECTION: FieldTypePbo
PARENTLINK: FieldTypePbo
IDENTIFIER: FieldTypePbo
PICKLIST: FieldTypePbo
LINK: FieldTypePbo
MULTIPARENTLINK: FieldTypePbo
CHILDLINK: FieldTypePbo
AUTO_ACCESSION: FieldTypePbo
DATE_RANGE: FieldTypePbo
SIDE_LINK: FieldTypePbo
ACTION_STRING: FieldTypePbo
FILE_BLOB: FieldTypePbo
SORT_DIRECTION_UNSPECIFIED: SortDirectionPbo
SORT_DIRECTION_ASCENDING: SortDirectionPbo
SORT_DIRECTION_DESCENDING: SortDirectionPbo
SORT_DIRECTION_NONE: SortDirectionPbo
FONT_SIZE_UNSPECIFIED: FontSizePbo
FONT_SIZE_SMALL: FontSizePbo
FONT_SIZE_MEDIUM: FontSizePbo
FONT_SIZE_LARGE: FontSizePbo
TEXT_DECORATION_UNSPECIFIED: TextDecorationPbo
TEXT_DECORATION_NONE: TextDecorationPbo
TEXT_DECORATION_UNDERLINE: TextDecorationPbo
TEXT_DECORATION_STRIKETHROUGH: TextDecorationPbo
STRING_FORMAT_UNSPECIFIED: StringFormatPbo
STRING_FORMAT_PHONE: StringFormatPbo
STRING_FORMAT_EMAIL: StringFormatPbo
DOUBLE_FORMAT_UNSPECIFIED: DoubleFormatPbo
DOUBLE_FORMAT_CURRENCY: DoubleFormatPbo
DOUBLE_FORMAT_PERCENTAGE: DoubleFormatPbo

class FieldValidatorPbo(_message.Message):
    __slots__ = ("validation_regex", "error_message")
    VALIDATION_REGEX_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    validation_regex: str
    error_message: str
    def __init__(self, validation_regex: _Optional[str] = ..., error_message: _Optional[str] = ...) -> None: ...

class ColorRangePbo(_message.Message):
    __slots__ = ("from_value", "to_value", "color")
    FROM_VALUE_FIELD_NUMBER: _ClassVar[int]
    TO_VALUE_FIELD_NUMBER: _ClassVar[int]
    COLOR_FIELD_NUMBER: _ClassVar[int]
    from_value: float
    to_value: float
    color: str
    def __init__(self, from_value: _Optional[float] = ..., to_value: _Optional[float] = ..., color: _Optional[str] = ...) -> None: ...

class BooleanDependentFieldEntryPbo(_message.Message):
    __slots__ = ("key", "dependent_field_names")
    KEY_FIELD_NUMBER: _ClassVar[int]
    DEPENDENT_FIELD_NAMES_FIELD_NUMBER: _ClassVar[int]
    key: bool
    dependent_field_names: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, key: bool = ..., dependent_field_names: _Optional[_Iterable[str]] = ...) -> None: ...

class SelectionDependentFieldEntryPbo(_message.Message):
    __slots__ = ("key", "dependent_field_names")
    KEY_FIELD_NUMBER: _ClassVar[int]
    DEPENDENT_FIELD_NAMES_FIELD_NUMBER: _ClassVar[int]
    key: str
    dependent_field_names: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, key: _Optional[str] = ..., dependent_field_names: _Optional[_Iterable[str]] = ...) -> None: ...

class EnumDependentFieldEntryPbo(_message.Message):
    __slots__ = ("key", "dependent_field_names")
    KEY_FIELD_NUMBER: _ClassVar[int]
    DEPENDENT_FIELD_NAMES_FIELD_NUMBER: _ClassVar[int]
    key: int
    dependent_field_names: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, key: _Optional[int] = ..., dependent_field_names: _Optional[_Iterable[str]] = ...) -> None: ...

class ProcessDetailEntryPbo(_message.Message):
    __slots__ = ("todo_fields",)
    TODO_FIELDS_FIELD_NUMBER: _ClassVar[int]
    todo_fields: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, todo_fields: _Optional[_Iterable[str]] = ...) -> None: ...

class BooleanPropertiesPbo(_message.Message):
    __slots__ = ("default_value", "is_process_todo_item", "dependent_fields", "is_hide_disabled_fields")
    DEFAULT_VALUE_FIELD_NUMBER: _ClassVar[int]
    IS_PROCESS_TODO_ITEM_FIELD_NUMBER: _ClassVar[int]
    DEPENDENT_FIELDS_FIELD_NUMBER: _ClassVar[int]
    IS_HIDE_DISABLED_FIELDS_FIELD_NUMBER: _ClassVar[int]
    default_value: bool
    is_process_todo_item: bool
    dependent_fields: _containers.RepeatedCompositeFieldContainer[BooleanDependentFieldEntryPbo]
    is_hide_disabled_fields: bool
    def __init__(self, default_value: bool = ..., is_process_todo_item: bool = ..., dependent_fields: _Optional[_Iterable[_Union[BooleanDependentFieldEntryPbo, _Mapping]]] = ..., is_hide_disabled_fields: bool = ...) -> None: ...

class DatePropertiesPbo(_message.Message):
    __slots__ = ("default_value", "static_date", "date_time_format")
    DEFAULT_VALUE_FIELD_NUMBER: _ClassVar[int]
    STATIC_DATE_FIELD_NUMBER: _ClassVar[int]
    DATE_TIME_FORMAT_FIELD_NUMBER: _ClassVar[int]
    default_value: str
    static_date: bool
    date_time_format: str
    def __init__(self, default_value: _Optional[str] = ..., static_date: bool = ..., date_time_format: _Optional[str] = ...) -> None: ...

class DoublePropertiesPbo(_message.Message):
    __slots__ = ("min_value", "max_value", "default_value", "precision", "double_format", "color_ranges", "scientific_notation_min_digits_from_decimal_point")
    MIN_VALUE_FIELD_NUMBER: _ClassVar[int]
    MAX_VALUE_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_VALUE_FIELD_NUMBER: _ClassVar[int]
    PRECISION_FIELD_NUMBER: _ClassVar[int]
    DOUBLE_FORMAT_FIELD_NUMBER: _ClassVar[int]
    COLOR_RANGES_FIELD_NUMBER: _ClassVar[int]
    SCIENTIFIC_NOTATION_MIN_DIGITS_FROM_DECIMAL_POINT_FIELD_NUMBER: _ClassVar[int]
    min_value: float
    max_value: float
    default_value: float
    precision: int
    double_format: DoubleFormatPbo
    color_ranges: _containers.RepeatedCompositeFieldContainer[ColorRangePbo]
    scientific_notation_min_digits_from_decimal_point: int
    def __init__(self, min_value: _Optional[float] = ..., max_value: _Optional[float] = ..., default_value: _Optional[float] = ..., precision: _Optional[int] = ..., double_format: _Optional[_Union[DoubleFormatPbo, str]] = ..., color_ranges: _Optional[_Iterable[_Union[ColorRangePbo, _Mapping]]] = ..., scientific_notation_min_digits_from_decimal_point: _Optional[int] = ...) -> None: ...

class IntegerPropertiesPbo(_message.Message):
    __slots__ = ("min_value", "max_value", "default_value", "unique_value", "color_ranges", "scientific_notation_min_digits_from_decimal_point", "scientific_notation_precision")
    MIN_VALUE_FIELD_NUMBER: _ClassVar[int]
    MAX_VALUE_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_VALUE_FIELD_NUMBER: _ClassVar[int]
    UNIQUE_VALUE_FIELD_NUMBER: _ClassVar[int]
    COLOR_RANGES_FIELD_NUMBER: _ClassVar[int]
    SCIENTIFIC_NOTATION_MIN_DIGITS_FROM_DECIMAL_POINT_FIELD_NUMBER: _ClassVar[int]
    SCIENTIFIC_NOTATION_PRECISION_FIELD_NUMBER: _ClassVar[int]
    min_value: int
    max_value: int
    default_value: int
    unique_value: bool
    color_ranges: _containers.RepeatedCompositeFieldContainer[ColorRangePbo]
    scientific_notation_min_digits_from_decimal_point: int
    scientific_notation_precision: int
    def __init__(self, min_value: _Optional[int] = ..., max_value: _Optional[int] = ..., default_value: _Optional[int] = ..., unique_value: bool = ..., color_ranges: _Optional[_Iterable[_Union[ColorRangePbo, _Mapping]]] = ..., scientific_notation_min_digits_from_decimal_point: _Optional[int] = ..., scientific_notation_precision: _Optional[int] = ...) -> None: ...

class LongPropertiesPbo(_message.Message):
    __slots__ = ("min_value", "max_value", "default_value", "unique_value", "color_ranges", "scientific_notation_min_digits_from_decimal_point", "scientific_notation_precision")
    MIN_VALUE_FIELD_NUMBER: _ClassVar[int]
    MAX_VALUE_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_VALUE_FIELD_NUMBER: _ClassVar[int]
    UNIQUE_VALUE_FIELD_NUMBER: _ClassVar[int]
    COLOR_RANGES_FIELD_NUMBER: _ClassVar[int]
    SCIENTIFIC_NOTATION_MIN_DIGITS_FROM_DECIMAL_POINT_FIELD_NUMBER: _ClassVar[int]
    SCIENTIFIC_NOTATION_PRECISION_FIELD_NUMBER: _ClassVar[int]
    min_value: int
    max_value: int
    default_value: int
    unique_value: bool
    color_ranges: _containers.RepeatedCompositeFieldContainer[ColorRangePbo]
    scientific_notation_min_digits_from_decimal_point: int
    scientific_notation_precision: int
    def __init__(self, min_value: _Optional[int] = ..., max_value: _Optional[int] = ..., default_value: _Optional[int] = ..., unique_value: bool = ..., color_ranges: _Optional[_Iterable[_Union[ColorRangePbo, _Mapping]]] = ..., scientific_notation_min_digits_from_decimal_point: _Optional[int] = ..., scientific_notation_precision: _Optional[int] = ...) -> None: ...

class ShortPropertiesPbo(_message.Message):
    __slots__ = ("min_value", "max_value", "default_value", "unique_value", "color_ranges", "scientific_notation_min_digits_from_decimal_point", "scientific_notation_precision")
    MIN_VALUE_FIELD_NUMBER: _ClassVar[int]
    MAX_VALUE_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_VALUE_FIELD_NUMBER: _ClassVar[int]
    UNIQUE_VALUE_FIELD_NUMBER: _ClassVar[int]
    COLOR_RANGES_FIELD_NUMBER: _ClassVar[int]
    SCIENTIFIC_NOTATION_MIN_DIGITS_FROM_DECIMAL_POINT_FIELD_NUMBER: _ClassVar[int]
    SCIENTIFIC_NOTATION_PRECISION_FIELD_NUMBER: _ClassVar[int]
    min_value: int
    max_value: int
    default_value: int
    unique_value: bool
    color_ranges: _containers.RepeatedCompositeFieldContainer[ColorRangePbo]
    scientific_notation_min_digits_from_decimal_point: int
    scientific_notation_precision: int
    def __init__(self, min_value: _Optional[int] = ..., max_value: _Optional[int] = ..., default_value: _Optional[int] = ..., unique_value: bool = ..., color_ranges: _Optional[_Iterable[_Union[ColorRangePbo, _Mapping]]] = ..., scientific_notation_min_digits_from_decimal_point: _Optional[int] = ..., scientific_notation_precision: _Optional[int] = ...) -> None: ...

class SelectionPropertiesPbo(_message.Message):
    __slots__ = ("default_value", "list_mode", "auto_sort", "direct_edit", "unique_value", "link_out", "link_out_url", "multi_select", "index_for_search", "is_auto_size", "field_validator", "static_list_values", "color_mapping", "auto_clear_field_list", "process_detail_map", "dependent_fields", "is_hide_disabled_fields")
    class ColorMappingEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class ProcessDetailMapEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: ProcessDetailEntryPbo
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[ProcessDetailEntryPbo, _Mapping]] = ...) -> None: ...
    DEFAULT_VALUE_FIELD_NUMBER: _ClassVar[int]
    LIST_MODE_FIELD_NUMBER: _ClassVar[int]
    AUTO_SORT_FIELD_NUMBER: _ClassVar[int]
    DIRECT_EDIT_FIELD_NUMBER: _ClassVar[int]
    UNIQUE_VALUE_FIELD_NUMBER: _ClassVar[int]
    LINK_OUT_FIELD_NUMBER: _ClassVar[int]
    LINK_OUT_URL_FIELD_NUMBER: _ClassVar[int]
    MULTI_SELECT_FIELD_NUMBER: _ClassVar[int]
    INDEX_FOR_SEARCH_FIELD_NUMBER: _ClassVar[int]
    IS_AUTO_SIZE_FIELD_NUMBER: _ClassVar[int]
    FIELD_VALIDATOR_FIELD_NUMBER: _ClassVar[int]
    STATIC_LIST_VALUES_FIELD_NUMBER: _ClassVar[int]
    COLOR_MAPPING_FIELD_NUMBER: _ClassVar[int]
    AUTO_CLEAR_FIELD_LIST_FIELD_NUMBER: _ClassVar[int]
    PROCESS_DETAIL_MAP_FIELD_NUMBER: _ClassVar[int]
    DEPENDENT_FIELDS_FIELD_NUMBER: _ClassVar[int]
    IS_HIDE_DISABLED_FIELDS_FIELD_NUMBER: _ClassVar[int]
    default_value: str
    list_mode: str
    auto_sort: bool
    direct_edit: bool
    unique_value: bool
    link_out: bool
    link_out_url: str
    multi_select: bool
    index_for_search: bool
    is_auto_size: bool
    field_validator: FieldValidatorPbo
    static_list_values: _containers.RepeatedScalarFieldContainer[str]
    color_mapping: _containers.ScalarMap[str, str]
    auto_clear_field_list: _containers.RepeatedScalarFieldContainer[str]
    process_detail_map: _containers.MessageMap[str, ProcessDetailEntryPbo]
    dependent_fields: _containers.RepeatedCompositeFieldContainer[SelectionDependentFieldEntryPbo]
    is_hide_disabled_fields: bool
    def __init__(self, default_value: _Optional[str] = ..., list_mode: _Optional[str] = ..., auto_sort: bool = ..., direct_edit: bool = ..., unique_value: bool = ..., link_out: bool = ..., link_out_url: _Optional[str] = ..., multi_select: bool = ..., index_for_search: bool = ..., is_auto_size: bool = ..., field_validator: _Optional[_Union[FieldValidatorPbo, _Mapping]] = ..., static_list_values: _Optional[_Iterable[str]] = ..., color_mapping: _Optional[_Mapping[str, str]] = ..., auto_clear_field_list: _Optional[_Iterable[str]] = ..., process_detail_map: _Optional[_Mapping[str, ProcessDetailEntryPbo]] = ..., dependent_fields: _Optional[_Iterable[_Union[SelectionDependentFieldEntryPbo, _Mapping]]] = ..., is_hide_disabled_fields: bool = ...) -> None: ...

class StringPropertiesPbo(_message.Message):
    __slots__ = ("default_value", "max_length", "num_lines", "unique_value", "index_for_search", "html_editor", "link_out", "link_out_url", "string_format", "is_auto_size", "field_validator", "preserve_padding")
    DEFAULT_VALUE_FIELD_NUMBER: _ClassVar[int]
    MAX_LENGTH_FIELD_NUMBER: _ClassVar[int]
    NUM_LINES_FIELD_NUMBER: _ClassVar[int]
    UNIQUE_VALUE_FIELD_NUMBER: _ClassVar[int]
    INDEX_FOR_SEARCH_FIELD_NUMBER: _ClassVar[int]
    HTML_EDITOR_FIELD_NUMBER: _ClassVar[int]
    LINK_OUT_FIELD_NUMBER: _ClassVar[int]
    LINK_OUT_URL_FIELD_NUMBER: _ClassVar[int]
    STRING_FORMAT_FIELD_NUMBER: _ClassVar[int]
    IS_AUTO_SIZE_FIELD_NUMBER: _ClassVar[int]
    FIELD_VALIDATOR_FIELD_NUMBER: _ClassVar[int]
    PRESERVE_PADDING_FIELD_NUMBER: _ClassVar[int]
    default_value: str
    max_length: int
    num_lines: int
    unique_value: bool
    index_for_search: bool
    html_editor: bool
    link_out: bool
    link_out_url: str
    string_format: StringFormatPbo
    is_auto_size: bool
    field_validator: FieldValidatorPbo
    preserve_padding: bool
    def __init__(self, default_value: _Optional[str] = ..., max_length: _Optional[int] = ..., num_lines: _Optional[int] = ..., unique_value: bool = ..., index_for_search: bool = ..., html_editor: bool = ..., link_out: bool = ..., link_out_url: _Optional[str] = ..., string_format: _Optional[_Union[StringFormatPbo, str]] = ..., is_auto_size: bool = ..., field_validator: _Optional[_Union[FieldValidatorPbo, _Mapping]] = ..., preserve_padding: bool = ...) -> None: ...

class SideLinkPropertiesPbo(_message.Message):
    __slots__ = ("linked_data_type_name", "default_value", "show_in_knowledge_graph", "knowledge_graph_display_name")
    LINKED_DATA_TYPE_NAME_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_VALUE_FIELD_NUMBER: _ClassVar[int]
    SHOW_IN_KNOWLEDGE_GRAPH_FIELD_NUMBER: _ClassVar[int]
    KNOWLEDGE_GRAPH_DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    linked_data_type_name: str
    default_value: int
    show_in_knowledge_graph: bool
    knowledge_graph_display_name: str
    def __init__(self, linked_data_type_name: _Optional[str] = ..., default_value: _Optional[int] = ..., show_in_knowledge_graph: bool = ..., knowledge_graph_display_name: _Optional[str] = ...) -> None: ...

class PickListPropertiesPbo(_message.Message):
    __slots__ = ("default_value", "pick_list_name", "direct_edit", "link_out", "link_out_url", "index_for_search", "field_validator", "color_mapping", "auto_clear_field_list", "process_detail_map", "dependent_fields", "is_hide_disabled_fields")
    class ColorMappingEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class ProcessDetailMapEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: ProcessDetailEntryPbo
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[ProcessDetailEntryPbo, _Mapping]] = ...) -> None: ...
    DEFAULT_VALUE_FIELD_NUMBER: _ClassVar[int]
    PICK_LIST_NAME_FIELD_NUMBER: _ClassVar[int]
    DIRECT_EDIT_FIELD_NUMBER: _ClassVar[int]
    LINK_OUT_FIELD_NUMBER: _ClassVar[int]
    LINK_OUT_URL_FIELD_NUMBER: _ClassVar[int]
    INDEX_FOR_SEARCH_FIELD_NUMBER: _ClassVar[int]
    FIELD_VALIDATOR_FIELD_NUMBER: _ClassVar[int]
    COLOR_MAPPING_FIELD_NUMBER: _ClassVar[int]
    AUTO_CLEAR_FIELD_LIST_FIELD_NUMBER: _ClassVar[int]
    PROCESS_DETAIL_MAP_FIELD_NUMBER: _ClassVar[int]
    DEPENDENT_FIELDS_FIELD_NUMBER: _ClassVar[int]
    IS_HIDE_DISABLED_FIELDS_FIELD_NUMBER: _ClassVar[int]
    default_value: str
    pick_list_name: str
    direct_edit: bool
    link_out: bool
    link_out_url: str
    index_for_search: bool
    field_validator: FieldValidatorPbo
    color_mapping: _containers.ScalarMap[str, str]
    auto_clear_field_list: _containers.RepeatedScalarFieldContainer[str]
    process_detail_map: _containers.MessageMap[str, ProcessDetailEntryPbo]
    dependent_fields: _containers.RepeatedCompositeFieldContainer[SelectionDependentFieldEntryPbo]
    is_hide_disabled_fields: bool
    def __init__(self, default_value: _Optional[str] = ..., pick_list_name: _Optional[str] = ..., direct_edit: bool = ..., link_out: bool = ..., link_out_url: _Optional[str] = ..., index_for_search: bool = ..., field_validator: _Optional[_Union[FieldValidatorPbo, _Mapping]] = ..., color_mapping: _Optional[_Mapping[str, str]] = ..., auto_clear_field_list: _Optional[_Iterable[str]] = ..., process_detail_map: _Optional[_Mapping[str, ProcessDetailEntryPbo]] = ..., dependent_fields: _Optional[_Iterable[_Union[SelectionDependentFieldEntryPbo, _Mapping]]] = ..., is_hide_disabled_fields: bool = ...) -> None: ...

class ParentLinkPropertiesPbo(_message.Message):
    __slots__ = ("default_value",)
    DEFAULT_VALUE_FIELD_NUMBER: _ClassVar[int]
    default_value: str
    def __init__(self, default_value: _Optional[str] = ...) -> None: ...

class MultiParentPropertiesPbo(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class IdentifierPropertiesPbo(_message.Message):
    __slots__ = ("default_value",)
    DEFAULT_VALUE_FIELD_NUMBER: _ClassVar[int]
    default_value: str
    def __init__(self, default_value: _Optional[str] = ...) -> None: ...

class FileBlobPropertiesPbo(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class EnumPropertiesPbo(_message.Message):
    __slots__ = ("default_value", "values", "color_mapping", "auto_clear_field_list", "dependent_fields", "is_hide_disabled_fields")
    class ColorMappingEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    DEFAULT_VALUE_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    COLOR_MAPPING_FIELD_NUMBER: _ClassVar[int]
    AUTO_CLEAR_FIELD_LIST_FIELD_NUMBER: _ClassVar[int]
    DEPENDENT_FIELDS_FIELD_NUMBER: _ClassVar[int]
    IS_HIDE_DISABLED_FIELDS_FIELD_NUMBER: _ClassVar[int]
    default_value: int
    values: _containers.RepeatedScalarFieldContainer[str]
    color_mapping: _containers.ScalarMap[str, str]
    auto_clear_field_list: _containers.RepeatedScalarFieldContainer[str]
    dependent_fields: _containers.RepeatedCompositeFieldContainer[EnumDependentFieldEntryPbo]
    is_hide_disabled_fields: bool
    def __init__(self, default_value: _Optional[int] = ..., values: _Optional[_Iterable[str]] = ..., color_mapping: _Optional[_Mapping[str, str]] = ..., auto_clear_field_list: _Optional[_Iterable[str]] = ..., dependent_fields: _Optional[_Iterable[_Union[EnumDependentFieldEntryPbo, _Mapping]]] = ..., is_hide_disabled_fields: bool = ...) -> None: ...

class DateRangePropertiesPbo(_message.Message):
    __slots__ = ("default_value", "is_static", "date_time_format")
    DEFAULT_VALUE_FIELD_NUMBER: _ClassVar[int]
    IS_STATIC_FIELD_NUMBER: _ClassVar[int]
    DATE_TIME_FORMAT_FIELD_NUMBER: _ClassVar[int]
    default_value: str
    is_static: bool
    date_time_format: str
    def __init__(self, default_value: _Optional[str] = ..., is_static: bool = ..., date_time_format: _Optional[str] = ...) -> None: ...

class ChildLinkPropertiesPbo(_message.Message):
    __slots__ = ("default_value",)
    DEFAULT_VALUE_FIELD_NUMBER: _ClassVar[int]
    default_value: int
    def __init__(self, default_value: _Optional[int] = ...) -> None: ...

class ActionStringPropertiesPbo(_message.Message):
    __slots__ = ("default_value", "max_length", "unique_value", "icon_name", "action_plugin_path", "field_validator", "direct_edit")
    DEFAULT_VALUE_FIELD_NUMBER: _ClassVar[int]
    MAX_LENGTH_FIELD_NUMBER: _ClassVar[int]
    UNIQUE_VALUE_FIELD_NUMBER: _ClassVar[int]
    ICON_NAME_FIELD_NUMBER: _ClassVar[int]
    ACTION_PLUGIN_PATH_FIELD_NUMBER: _ClassVar[int]
    FIELD_VALIDATOR_FIELD_NUMBER: _ClassVar[int]
    DIRECT_EDIT_FIELD_NUMBER: _ClassVar[int]
    default_value: str
    max_length: int
    unique_value: bool
    icon_name: str
    action_plugin_path: str
    field_validator: FieldValidatorPbo
    direct_edit: bool
    def __init__(self, default_value: _Optional[str] = ..., max_length: _Optional[int] = ..., unique_value: bool = ..., icon_name: _Optional[str] = ..., action_plugin_path: _Optional[str] = ..., field_validator: _Optional[_Union[FieldValidatorPbo, _Mapping]] = ..., direct_edit: bool = ...) -> None: ...

class ActionPropertiesPbo(_message.Message):
    __slots__ = ("icon_name", "icon_color", "background_color", "font_color", "action_plugin_path")
    ICON_NAME_FIELD_NUMBER: _ClassVar[int]
    ICON_COLOR_FIELD_NUMBER: _ClassVar[int]
    BACKGROUND_COLOR_FIELD_NUMBER: _ClassVar[int]
    FONT_COLOR_FIELD_NUMBER: _ClassVar[int]
    ACTION_PLUGIN_PATH_FIELD_NUMBER: _ClassVar[int]
    icon_name: str
    icon_color: str
    background_color: str
    font_color: str
    action_plugin_path: str
    def __init__(self, icon_name: _Optional[str] = ..., icon_color: _Optional[str] = ..., background_color: _Optional[str] = ..., font_color: _Optional[str] = ..., action_plugin_path: _Optional[str] = ...) -> None: ...

class AccessionPropertiesPbo(_message.Message):
    __slots__ = ("unique_value", "index_for_search", "link_out", "link_out_url", "sequence_key", "prefix", "suffix", "number_of_digits", "starting_value")
    UNIQUE_VALUE_FIELD_NUMBER: _ClassVar[int]
    INDEX_FOR_SEARCH_FIELD_NUMBER: _ClassVar[int]
    LINK_OUT_FIELD_NUMBER: _ClassVar[int]
    LINK_OUT_URL_FIELD_NUMBER: _ClassVar[int]
    SEQUENCE_KEY_FIELD_NUMBER: _ClassVar[int]
    PREFIX_FIELD_NUMBER: _ClassVar[int]
    SUFFIX_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_DIGITS_FIELD_NUMBER: _ClassVar[int]
    STARTING_VALUE_FIELD_NUMBER: _ClassVar[int]
    unique_value: bool
    index_for_search: bool
    link_out: bool
    link_out_url: str
    sequence_key: str
    prefix: str
    suffix: str
    number_of_digits: int
    starting_value: int
    def __init__(self, unique_value: bool = ..., index_for_search: bool = ..., link_out: bool = ..., link_out_url: _Optional[str] = ..., sequence_key: _Optional[str] = ..., prefix: _Optional[str] = ..., suffix: _Optional[str] = ..., number_of_digits: _Optional[int] = ..., starting_value: _Optional[int] = ...) -> None: ...

class VeloxFieldDefPbo(_message.Message):
    __slots__ = ("data_field_type", "data_field_name", "display_name", "description", "required", "editable", "visible", "identifier", "identifier_order", "sort_direction", "sort_order", "tag", "approve_edit", "workflow_only_editing", "font_size", "bold_font", "italic_font", "text_decoration", "is_key_field", "key_field_order", "is_removable", "is_system_field", "is_restricted", "is_audit_logged", "is_active", "is_for_plugin_use_only", "default_table_column_width", "boolean_properties", "date_properties", "double_properties", "integer_properties", "long_properties", "selection_properties", "string_properties", "side_link_properties", "short_properties", "picklist_properties", "parent_link_properties", "multi_parent_properties", "identifier_properties", "file_blob_properties", "enum_properties", "date_range_properties", "child_link_properties", "action_string_properties", "action_properties", "accession_properties")
    DATA_FIELD_TYPE_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NAME_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_FIELD_NUMBER: _ClassVar[int]
    EDITABLE_FIELD_NUMBER: _ClassVar[int]
    VISIBLE_FIELD_NUMBER: _ClassVar[int]
    IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    IDENTIFIER_ORDER_FIELD_NUMBER: _ClassVar[int]
    SORT_DIRECTION_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    TAG_FIELD_NUMBER: _ClassVar[int]
    APPROVE_EDIT_FIELD_NUMBER: _ClassVar[int]
    WORKFLOW_ONLY_EDITING_FIELD_NUMBER: _ClassVar[int]
    FONT_SIZE_FIELD_NUMBER: _ClassVar[int]
    BOLD_FONT_FIELD_NUMBER: _ClassVar[int]
    ITALIC_FONT_FIELD_NUMBER: _ClassVar[int]
    TEXT_DECORATION_FIELD_NUMBER: _ClassVar[int]
    IS_KEY_FIELD_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_ORDER_FIELD_NUMBER: _ClassVar[int]
    IS_REMOVABLE_FIELD_NUMBER: _ClassVar[int]
    IS_SYSTEM_FIELD_FIELD_NUMBER: _ClassVar[int]
    IS_RESTRICTED_FIELD_NUMBER: _ClassVar[int]
    IS_AUDIT_LOGGED_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    IS_FOR_PLUGIN_USE_ONLY_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_TABLE_COLUMN_WIDTH_FIELD_NUMBER: _ClassVar[int]
    BOOLEAN_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    DATE_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    DOUBLE_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    INTEGER_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    LONG_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    SELECTION_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    STRING_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    SIDE_LINK_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    SHORT_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    PICKLIST_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    PARENT_LINK_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    MULTI_PARENT_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    IDENTIFIER_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    FILE_BLOB_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    ENUM_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    DATE_RANGE_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    CHILD_LINK_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    ACTION_STRING_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    ACTION_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    ACCESSION_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    data_field_type: FieldTypePbo
    data_field_name: str
    display_name: str
    description: str
    required: bool
    editable: bool
    visible: bool
    identifier: bool
    identifier_order: int
    sort_direction: SortDirectionPbo
    sort_order: int
    tag: str
    approve_edit: bool
    workflow_only_editing: bool
    font_size: FontSizePbo
    bold_font: bool
    italic_font: bool
    text_decoration: TextDecorationPbo
    is_key_field: bool
    key_field_order: int
    is_removable: bool
    is_system_field: bool
    is_restricted: bool
    is_audit_logged: bool
    is_active: bool
    is_for_plugin_use_only: bool
    default_table_column_width: int
    boolean_properties: BooleanPropertiesPbo
    date_properties: DatePropertiesPbo
    double_properties: DoublePropertiesPbo
    integer_properties: IntegerPropertiesPbo
    long_properties: LongPropertiesPbo
    selection_properties: SelectionPropertiesPbo
    string_properties: StringPropertiesPbo
    side_link_properties: SideLinkPropertiesPbo
    short_properties: ShortPropertiesPbo
    picklist_properties: PickListPropertiesPbo
    parent_link_properties: ParentLinkPropertiesPbo
    multi_parent_properties: MultiParentPropertiesPbo
    identifier_properties: IdentifierPropertiesPbo
    file_blob_properties: FileBlobPropertiesPbo
    enum_properties: EnumPropertiesPbo
    date_range_properties: DateRangePropertiesPbo
    child_link_properties: ChildLinkPropertiesPbo
    action_string_properties: ActionStringPropertiesPbo
    action_properties: ActionPropertiesPbo
    accession_properties: AccessionPropertiesPbo
    def __init__(self, data_field_type: _Optional[_Union[FieldTypePbo, str]] = ..., data_field_name: _Optional[str] = ..., display_name: _Optional[str] = ..., description: _Optional[str] = ..., required: bool = ..., editable: bool = ..., visible: bool = ..., identifier: bool = ..., identifier_order: _Optional[int] = ..., sort_direction: _Optional[_Union[SortDirectionPbo, str]] = ..., sort_order: _Optional[int] = ..., tag: _Optional[str] = ..., approve_edit: bool = ..., workflow_only_editing: bool = ..., font_size: _Optional[_Union[FontSizePbo, str]] = ..., bold_font: bool = ..., italic_font: bool = ..., text_decoration: _Optional[_Union[TextDecorationPbo, str]] = ..., is_key_field: bool = ..., key_field_order: _Optional[int] = ..., is_removable: bool = ..., is_system_field: bool = ..., is_restricted: bool = ..., is_audit_logged: bool = ..., is_active: bool = ..., is_for_plugin_use_only: bool = ..., default_table_column_width: _Optional[int] = ..., boolean_properties: _Optional[_Union[BooleanPropertiesPbo, _Mapping]] = ..., date_properties: _Optional[_Union[DatePropertiesPbo, _Mapping]] = ..., double_properties: _Optional[_Union[DoublePropertiesPbo, _Mapping]] = ..., integer_properties: _Optional[_Union[IntegerPropertiesPbo, _Mapping]] = ..., long_properties: _Optional[_Union[LongPropertiesPbo, _Mapping]] = ..., selection_properties: _Optional[_Union[SelectionPropertiesPbo, _Mapping]] = ..., string_properties: _Optional[_Union[StringPropertiesPbo, _Mapping]] = ..., side_link_properties: _Optional[_Union[SideLinkPropertiesPbo, _Mapping]] = ..., short_properties: _Optional[_Union[ShortPropertiesPbo, _Mapping]] = ..., picklist_properties: _Optional[_Union[PickListPropertiesPbo, _Mapping]] = ..., parent_link_properties: _Optional[_Union[ParentLinkPropertiesPbo, _Mapping]] = ..., multi_parent_properties: _Optional[_Union[MultiParentPropertiesPbo, _Mapping]] = ..., identifier_properties: _Optional[_Union[IdentifierPropertiesPbo, _Mapping]] = ..., file_blob_properties: _Optional[_Union[FileBlobPropertiesPbo, _Mapping]] = ..., enum_properties: _Optional[_Union[EnumPropertiesPbo, _Mapping]] = ..., date_range_properties: _Optional[_Union[DateRangePropertiesPbo, _Mapping]] = ..., child_link_properties: _Optional[_Union[ChildLinkPropertiesPbo, _Mapping]] = ..., action_string_properties: _Optional[_Union[ActionStringPropertiesPbo, _Mapping]] = ..., action_properties: _Optional[_Union[ActionPropertiesPbo, _Mapping]] = ..., accession_properties: _Optional[_Union[AccessionPropertiesPbo, _Mapping]] = ...) -> None: ...

class VeloxFieldDefListPbo(_message.Message):
    __slots__ = ("field_definitions",)
    FIELD_DEFINITIONS_FIELD_NUMBER: _ClassVar[int]
    field_definitions: _containers.RepeatedCompositeFieldContainer[VeloxFieldDefPbo]
    def __init__(self, field_definitions: _Optional[_Iterable[_Union[VeloxFieldDefPbo, _Mapping]]] = ...) -> None: ...
