from sapiopylib.rest.pojo.Sort import SortDirection
from sapiopylib.rest.pojo.datatype.FieldDefinition import AbstractVeloxFieldDefinition, FieldType, \
    VeloxBooleanFieldDefinition, VeloxDateFieldDefinition, VeloxAccessionFieldDefinition, VeloxActionFieldDefinition, \
    VeloxChildLinkFieldDefinition, VeloxDateRangeFieldDefinition, VeloxDoubleFieldDefinition, \
    VeloxEnumFieldDefinition, VeloxIdentifierFieldDefinition, VeloxIntegerFieldDefinition, \
    VeloxLongFieldDefinition, VeloxMultiParentFieldDefinition, VeloxParentFieldDefinition, \
    VeloxPickListFieldDefinition, VeloxSelectionFieldDefinition, VeloxShortFieldDefinition, \
    VeloxStringFieldDefinition, VeloxSideLinkFieldDefinition, VeloxActionStringFieldDefinition, FieldValidator, \
    ListMode, SapioDoubleFormat, SapioStringFormat

from sapiopycommons.ai.protoapi.fielddefinitions.fields_pb2 import FieldValuePbo
from sapiopycommons.ai.protoapi.fielddefinitions.velox_field_def_pb2 import FieldTypePbo, SortDirectionPbo, \
    DoubleFormatPbo, StringFormatPbo, FieldValidatorPbo, VeloxFieldDefPbo, BooleanPropertiesPbo, DatePropertiesPbo, \
    DoublePropertiesPbo, IntegerPropertiesPbo, LongPropertiesPbo, SelectionPropertiesPbo, StringPropertiesPbo, \
    SideLinkPropertiesPbo, ShortPropertiesPbo, PickListPropertiesPbo, ParentLinkPropertiesPbo, MultiParentPropertiesPbo, \
    IdentifierPropertiesPbo, FileBlobPropertiesPbo, EnumPropertiesPbo, DateRangePropertiesPbo, ChildLinkPropertiesPbo, \
    ActionStringPropertiesPbo, ActionPropertiesPbo, AccessionPropertiesPbo, SelectionDependentFieldEntryPbo, \
    EnumDependentFieldEntryPbo, BooleanDependentFieldEntryPbo
from sapiopycommons.general.aliases import FieldValue


# FR-47422: Created class.
class ProtobufUtils:
    @staticmethod
    def field_type_to_pbo(field_type: FieldType) -> FieldTypePbo:
        """
        Convert a FieldType enum to its corresponding FieldTypePbo.

        :param field_type: The FieldType enum value.
        :return: The corresponding FieldTypePbo.
        """
        match field_type:
            case FieldType.ACTION:
                return FieldTypePbo.ACTION
            case FieldType.ACTION_STRING:
                return FieldTypePbo.ACTION_STRING
            case FieldType.AUTO_ACCESSION:
                return FieldTypePbo.AUTO_ACCESSION
            case FieldType.BOOLEAN:
                return FieldTypePbo.BOOLEAN
            case FieldType.CHILDLINK:
                return FieldTypePbo.CHILDLINK
            case FieldType.DATE:
                return FieldTypePbo.DATE
            case FieldType.DATE_RANGE:
                return FieldTypePbo.DATE_RANGE
            case FieldType.DOUBLE:
                return FieldTypePbo.DOUBLE
            case FieldType.ENUM:
                return FieldTypePbo.ENUM
            # case FieldType.FILE_BLOB:
            #     return FieldTypePbo.FILE_BLOB
            case FieldType.IDENTIFIER:
                return FieldTypePbo.IDENTIFIER
            case FieldType.INTEGER:
                return FieldTypePbo.INTEGER
            case FieldType.LINK:
                return FieldTypePbo.LINK
            case FieldType.LONG:
                return FieldTypePbo.LONG
            case FieldType.MULTIPARENTLINK:
                return FieldTypePbo.MULTIPARENTLINK
            case FieldType.PARENTLINK:
                return FieldTypePbo.PARENTLINK
            case FieldType.PICKLIST:
                return FieldTypePbo.PICKLIST
            case FieldType.SELECTION:
                return FieldTypePbo.SELECTION
            case FieldType.SHORT:
                return FieldTypePbo.SHORT
            case FieldType.SIDE_LINK:
                return FieldTypePbo.SIDE_LINK
            case FieldType.STRING:
                return FieldTypePbo.STRING
            case _:
                return FieldTypePbo.FIELD_TYPE_UNSPECIFIED

    @staticmethod
    def sort_direction_to_pbo(sort_direction: SortDirection | None) -> SortDirectionPbo:
        """
        Convert a SortDirection enum to its corresponding SortDirectionPbo.

        :param sort_direction: The SortDirection enum value.
        :return: The corresponding SortDirectionPbo.
        """
        if sort_direction is None or sort_direction == SortDirection.NONE:
            return SortDirectionPbo.SORT_DIRECTION_NONE
        elif sort_direction == SortDirection.ASCENDING:
            return SortDirectionPbo.SORT_DIRECTION_ASCENDING
        elif sort_direction == SortDirection.DESCENDING:
            return SortDirectionPbo.SORT_DIRECTION_DESCENDING
        else:
            return SortDirectionPbo.SORT_DIRECTION_UNSPECIFIED

    @staticmethod
    def double_format_to_pbo(double_format: SapioDoubleFormat | None) -> DoubleFormatPbo:
        """
        Convert a SapioDoubleFormat enum to its corresponding DoubleFormatPbo.

        :param double_format: The SapioDoubleFormat enum value.
        :return: The corresponding DoubleFormatPbo.
        """
        if double_format is None:
            return DoubleFormatPbo.DOUBLE_FORMAT_UNSPECIFIED
        elif double_format == SapioDoubleFormat.CURRENCY:
            return DoubleFormatPbo.DOUBLE_FORMAT_CURRENCY
        elif double_format == SapioDoubleFormat.PERCENTAGE:
            return DoubleFormatPbo.DOUBLE_FORMAT_PERCENTAGE
        else:
            return DoubleFormatPbo.DOUBLE_FORMAT_UNSPECIFIED

    @staticmethod
    def string_format_to_pbo(string_format: SapioStringFormat | None) -> StringFormatPbo:
        """
        Convert a SapioStringFormat enum to its corresponding StringFormatPbo.

        :param string_format: The SapioStringFormat enum value.
        :return: The corresponding StringFormatPbo.
        """
        if string_format is None:
            return StringFormatPbo.STRING_FORMAT_UNSPECIFIED
        elif string_format == SapioStringFormat.EMAIL:
            return StringFormatPbo.STRING_FORMAT_EMAIL
        elif string_format == SapioStringFormat.PHONE:
            return StringFormatPbo.STRING_FORMAT_PHONE
        else:
            return StringFormatPbo.STRING_FORMAT_UNSPECIFIED

    @staticmethod
    def field_validator_to_pbo(validator: FieldValidator | None) -> FieldValidatorPbo | None:
        """
        Convert a FieldValidator object to its corresponding FieldValidatorPbo.

        :param validator: The FieldValidator object.
        :return: The corresponding FieldValidatorPbo or None if validator is None.
        """
        if validator is None:
            return None
        return FieldValidatorPbo(
            validation_regex=validator.validation_regex,
            error_message=validator.error_message
        )

    @staticmethod
    def list_mode_to_str(list_mode: ListMode, field: VeloxSelectionFieldDefinition) -> str | None:
        """
        Convert a ListMode enum to its string representation.

        :param list_mode: The ListMode enum value.
        :param field: The VeloxSelectionFieldDefinition object.
        :return: The string representation of the ListMode or None if list_mode is None.
        """
        if list_mode is None:
            return None
        list_mode_str = list_mode.list_mode_name
        if list_mode == ListMode.LIST:
            list_mode_str += field.pick_list_name or ""
        elif list_mode == ListMode.PLUGIN:
            list_mode_str += field.plugin_name or ""
        elif list_mode == ListMode.REPORT:
            list_mode_str += field.custom_report_name or ""
        return list_mode_str

    @staticmethod
    def field_def_to_pbo(field: AbstractVeloxFieldDefinition) -> VeloxFieldDefPbo:
        """
        Convert a AbstractVeloxFieldDefinition object to its corresponding VeloxFieldDefPbo.

        :param field: The AbstractVeloxFieldDefinition object.
        :return: The corresponding VeloxFieldDefPbo.
        """
        accession_properties: AccessionPropertiesPbo | None = None
        action_properties: ActionPropertiesPbo | None = None
        action_string_properties: ActionStringPropertiesPbo | None = None
        boolean_properties: BooleanPropertiesPbo | None = None
        child_link_properties: ChildLinkPropertiesPbo | None = None
        date_properties: DatePropertiesPbo | None = None
        date_range_properties: DateRangePropertiesPbo | None = None
        double_properties: DoublePropertiesPbo | None = None
        enum_properties: EnumPropertiesPbo | None = None
        file_blob_properties: FileBlobPropertiesPbo | None = None
        identifier_properties: IdentifierPropertiesPbo | None = None
        integer_properties: IntegerPropertiesPbo | None = None
        long_properties: LongPropertiesPbo | None = None
        multi_parent_properties: MultiParentPropertiesPbo | None = None
        parent_link_properties: ParentLinkPropertiesPbo | None = None
        picklist_properties: PickListPropertiesPbo | None = None
        selection_properties: SelectionPropertiesPbo | None = None
        short_properties: ShortPropertiesPbo | None = None
        side_link_properties: SideLinkPropertiesPbo | None = None
        string_properties: StringPropertiesPbo | None = None

        if isinstance(field, VeloxAccessionFieldDefinition):
            accession_properties = AccessionPropertiesPbo(
                unique_value=field.unique_value,
                # index_for_search # Missing in FieldDefinition.py
                link_out=field.link_out,
                link_out_url=field.link_out_url,
                sequence_key=field.sequence_key,
                prefix=field.prefix,
                suffix=field.suffix,
                number_of_digits=field.number_of_digits,
                starting_value=field.starting_value
            )
        elif isinstance(field, VeloxActionFieldDefinition):
            action_properties = ActionPropertiesPbo(
                # icon_name # Missing in FieldDefinition.py
                # icon_color # Missing in FieldDefinition.py
                # background_color # Missing in FieldDefinition.py
                # font_color # Missing in FieldDefinition.py
                # action_plugin_path # Missing in FieldDefinition.py
            )
        elif isinstance(field, VeloxActionStringFieldDefinition):
            action_string_properties = ActionStringPropertiesPbo(
                default_value=field.default_value,
                max_length=field.max_length,
                unique_value=field.unique_value,
                icon_name=field.icon_name,
                action_plugin_path=field.action_plugin_path,
                field_validator=ProtobufUtils.field_validator_to_pbo(field.field_validator),
                direct_edit=field.direct_edit
            )
        elif isinstance(field, VeloxBooleanFieldDefinition):
            boolean_properties = BooleanPropertiesPbo(
                default_value=field.default_value,
                is_process_todo_item=field.process_todo_item,
                dependent_fields=[BooleanDependentFieldEntryPbo(k, v) for k, v in field.get_dependent_field_map().items()],
                is_hide_disabled_fields=field.hide_disabled_fields
            )
        elif isinstance(field, VeloxChildLinkFieldDefinition):
            child_link_properties = ChildLinkPropertiesPbo(
                # default_value # Missing in FieldDefinition.py
            )
        elif isinstance(field, VeloxDateFieldDefinition):
            date_properties = DatePropertiesPbo(
                default_value=field.default_value,
                static_date=field.static_date,
                date_time_format=field.date_time_format
            )
        elif isinstance(field, VeloxDateRangeFieldDefinition):
            date_range_properties = DateRangePropertiesPbo(
                default_value=field.default_value,
                is_static=field.static_date,
                date_time_format=field.date_time_format
            )
        elif isinstance(field, VeloxDoubleFieldDefinition):
            double_properties = DoublePropertiesPbo(
                min_value=field.min_value,
                max_value=field.max_value,
                default_value=field.default_value,
                precision=field.precision,
                double_format=ProtobufUtils.double_format_to_pbo(field.double_format),
                # color_ranges # Missing in FieldDefinition.py
            )
        # elif isinstance(field, VeloxFileBlobFieldDefinition):
        #     file_blob_properties = FileBlobPropertiesPbo()
        elif isinstance(field, VeloxEnumFieldDefinition):
            enum_properties = EnumPropertiesPbo(
                default_value=field.default_value,
                values=field.values if field.values is not None else [],
                # color_mapping # Missing in FieldDefinition.py
                # auto_clear_field_list # Missing in FieldDefinition.py
                dependent_fields=[EnumDependentFieldEntryPbo(k, v) for k,v in field.get_dependent_field_map().items()],
                is_hide_disabled_fields=field.hide_disabled_fields
            )
        elif isinstance(field, VeloxIdentifierFieldDefinition):
            identifier_properties = IdentifierPropertiesPbo(
                # default_value # Missing in FieldDefinition.py
            )
        elif isinstance(field, VeloxIntegerFieldDefinition):
            integer_properties = IntegerPropertiesPbo(
                min_value=field.min_value,
                max_value=field.max_value,
                default_value=field.default_value,
                unique_value=field.unique_value,
                # color_ranges # Missing in FieldDefinition.py
            )
        elif isinstance(field, VeloxLongFieldDefinition):
            long_properties = LongPropertiesPbo(
                min_value=field.min_value,
                max_value=field.max_value,
                default_value=field.default_value,
                unique_value=field.unique_value,
                # color_ranges # Missing in FieldDefinition.py
            )
        elif isinstance(field, VeloxMultiParentFieldDefinition):
            multi_parent_properties = MultiParentPropertiesPbo()
        elif isinstance(field, VeloxParentFieldDefinition):
            parent_link_properties = ParentLinkPropertiesPbo(
                # default_value # Missing in FieldDefinition.py
            )
        elif isinstance(field, VeloxPickListFieldDefinition):
            picklist_properties = PickListPropertiesPbo(
                default_value=field.default_value,
                pick_list_name=field.pick_list_name,
                direct_edit=field.direct_edit,
                # link_out # Missing in FieldDefinition.py
                # link_out_url # Missing in FieldDefinition.py
                # index_for_search # Missing in FieldDefinition.py
                # field_validator # Missing in FieldDefinition.py
                # color_mapping # Missing in FieldDefinition.py
                # auto_clear_field_list # Missing in FieldDefinition.py
                # process_detail_map # Missing in FieldDefinition.py
                dependent_fields=[SelectionDependentFieldEntryPbo(k, v) for k,v in field.get_dependent_field_map().items()],
                is_hide_disabled_fields=field.hide_disabled_fields
            )
        elif isinstance(field, VeloxSelectionFieldDefinition):
            list_mode_str = ProtobufUtils.list_mode_to_str(field.list_mode, field)
            selection_properties = SelectionPropertiesPbo(
                default_value=field.default_value,
                list_mode=list_mode_str,
                # auto_sort # Missing in FieldDefinition.py
                direct_edit=field.direct_edit,
                unique_value=field.unique_value,
                # link_out # Missing in FieldDefinition.py
                # link_out_url # Missing in FieldDefinition.py
                multi_select=field.multi_select,
                # index_for_search # Missing in FieldDefinition.py
                # is_auto_size # Missing in FieldDefinition.py
                # field_validator # Missing in FieldDefinition.py
                static_list_values=field.static_list_values if field.static_list_values is not None else [],
                # color_mapping # Missing in FieldDefinition.py
                # auto_clear_field_list # Missing in FieldDefinition.py
                # process_detail_map # Missing in FieldDefinition.py
                dependent_fields=[SelectionDependentFieldEntryPbo(k, v) for k,v in field.get_dependent_field_map().items()],
                is_hide_disabled_fields=field.hide_disabled_fields
            )
        elif isinstance(field, VeloxShortFieldDefinition):
            short_properties = ShortPropertiesPbo(
                min_value=field.min_value,
                max_value=field.max_value,
                default_value=field.default_value,
                unique_value=field.unique_value,
                # color_ranges # Missing in FieldDefinition.py
            )
        elif isinstance(field, VeloxSideLinkFieldDefinition):
            side_link_properties = SideLinkPropertiesPbo(
                linked_data_type_name=field.linked_data_type_name,
                default_value=field.default_value,
                # show_in_knowledge_graph # Missing in FieldDefinition.py
                # knowledge_graph_display_name # Missing in FieldDefinition.py
            )
        elif isinstance(field, VeloxStringFieldDefinition):
            string_properties = StringPropertiesPbo(
                default_value=field.default_value,
                max_length=field.max_length,
                num_lines=field.num_lines,
                unique_value=field.unique_value,
                # index_for_search # Missing in FieldDefinition.py
                html_editor=field.html_editor,
                link_out=field.link_out,
                link_out_url=field.link_out_url,
                string_format=ProtobufUtils.string_format_to_pbo(field.string_format),
                is_auto_size=field.auto_size,
                field_validator=ProtobufUtils.field_validator_to_pbo(field.field_validator),
                # preserve_padding # Missing in FieldDefinition.py
            )
        else:
            print(f"Warning: Unhandled field type for properties mapping: {type(field)}")

        return VeloxFieldDefPbo(
            data_field_type=ProtobufUtils.field_type_to_pbo(field.data_field_type),
            data_field_name=field.data_field_name,
            display_name=field.display_name,
            description=field.description,
            required=field.required,
            editable=field.editable,
            visible=field.visible,
            identifier=field.identifier,
            identifier_order=field.identifier_order,
            sort_direction=ProtobufUtils.sort_direction_to_pbo(field.sort_direction),
            sort_order=field.sort_order,
            tag=field.tag,
            # approve_edit # Missing in FieldDefinition.py
            # workflow_only_editing # Missing in FieldDefinition.py
            # font_size # Missing in FieldDefinition.py
            # bold_font # Missing in FieldDefinition.py
            # italic_font # Missing in FieldDefinition.py
            # text_decoration # Missing in FieldDefinition.py
            is_key_field=field.key_field,
            key_field_order=field.key_field_order,
            # is_removable # Missing in FieldDefinition.py
            is_system_field=field.system_field,
            # is_restricted # Missing in FieldDefinition.py
            is_audit_logged=field.audit_logged,
            # is_active # Missing in FieldDefinition.py
            # is_for_plugin_use_only # Missing in FieldDefinition.py
            default_table_column_width=field.default_table_column_width,

            accession_properties=accession_properties,
            action_properties=action_properties,
            action_string_properties=action_string_properties,
            boolean_properties=boolean_properties,
            child_link_properties=child_link_properties,
            date_properties=date_properties,
            date_range_properties=date_range_properties,
            double_properties=double_properties,
            enum_properties=enum_properties,
            file_blob_properties=file_blob_properties,
            identifier_properties=identifier_properties,
            integer_properties=integer_properties,
            long_properties=long_properties,
            multi_parent_properties=multi_parent_properties,
            parent_link_properties=parent_link_properties,
            picklist_properties=picklist_properties,
            selection_properties=selection_properties,
            short_properties=short_properties,
            side_link_properties=side_link_properties,
            string_properties=string_properties,
        )

    @staticmethod
    def value_to_field_pbo(value: FieldValue) -> FieldValuePbo:
        """
        Convert a Python value to its corresponding FieldValuePbo.

        :param value: The Python value (str, int, float, bool).
        :return: The corresponding FieldValuePbo object.
        """
        field_value = FieldValuePbo()
        if isinstance(value, str):
            field_value.string_value = value
        elif isinstance(value, int):
            field_value.int_value = value
        elif isinstance(value, float):
            field_value.double_value = value
        elif isinstance(value, bool):
            field_value.bool_value = value
        else:
            raise ValueError(f"Unsupported value type: {type(value)}")
        return field_value

    @staticmethod
    def field_pbo_to_value(value: FieldValuePbo) -> FieldValue:
        """
        Convert a StepRecordFieldValue to its corresponding Python value.

        :param value: The StepRecordFieldValue object.
        :return: The corresponding Python value.
        """
        if value.HasField("string_value"):
            return value.string_value
        elif value.HasField("int_value"):
            return value.int_value
        elif value.HasField("double_value"):
            return value.double_value
        elif value.HasField("bool_value"):
            return value.bool_value
        else:
            return None

    @staticmethod
    def field_def_pbo_to_default_value(field_def: VeloxFieldDefPbo) -> FieldValue:
        """
        Get the default value of a VeloxFieldDefPbo.

        :param field_def: The VeloxFieldDefPbo object.
        :return: The default value for the field definition.
        """
        match field_def.data_field_type:
            case FieldTypePbo.ACTION:
                return None
            case FieldTypePbo.ACTION_STRING:
                return field_def.action_string_properties.default_value
            case FieldTypePbo.AUTO_ACCESSION:
                return None
            case FieldTypePbo.BOOLEAN:
                return field_def.boolean_properties.default_value
            case FieldTypePbo.CHILDLINK:
                return None
            case FieldTypePbo.DATE:
                return field_def.date_properties.default_value
            case FieldTypePbo.DATE_RANGE:
                return field_def.date_range_properties.default_value
            case FieldTypePbo.DOUBLE:
                return field_def.double_properties.default_value
            case FieldTypePbo.ENUM:
                return field_def.enum_properties.default_value
            # case FieldTypePbo.FILE_BLOB:
            #     return None
            case FieldTypePbo.IDENTIFIER:
                return None
            case FieldTypePbo.INTEGER:
                return field_def.integer_properties.default_value
            case FieldTypePbo.LINK:
                return None
            case FieldTypePbo.LONG:
                return field_def.long_properties.default_value
            case FieldTypePbo.MULTIPARENTLINK:
                return None
            case FieldTypePbo.PARENTLINK:
                return None
            case FieldTypePbo.PICKLIST:
                return field_def.picklist_properties.default_value
            case FieldTypePbo.SELECTION:
                return field_def.selection_properties.default_value
            case FieldTypePbo.SHORT:
                return field_def.short_properties.default_value
            case FieldTypePbo.SIDE_LINK:
                return field_def.side_link_properties.default_value
            case FieldTypePbo.STRING:
                return field_def.string_properties.default_value
            case _:
                raise Exception(f"Unexpected field type: {field_def.data_field_type}")
