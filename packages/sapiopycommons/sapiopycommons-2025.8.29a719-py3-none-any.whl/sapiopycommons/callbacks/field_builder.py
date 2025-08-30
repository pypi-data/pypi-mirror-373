from sapiopylib.rest.pojo.DateRange import DateRange
from sapiopylib.rest.pojo.Sort import SortDirection
from sapiopylib.rest.pojo.datatype.FieldDefinition import VeloxStringFieldDefinition, SapioStringFormat, \
    FieldValidator, VeloxAccessionFieldDefinition, VeloxBooleanFieldDefinition, VeloxDateFieldDefinition, \
    VeloxDateRangeFieldDefinition, VeloxDoubleFieldDefinition, VeloxEnumFieldDefinition, VeloxIntegerFieldDefinition, \
    VeloxLongFieldDefinition, VeloxPickListFieldDefinition, VeloxSelectionFieldDefinition, VeloxShortFieldDefinition, \
    SapioDoubleFormat, ListMode

from sapiopycommons.general.aliases import FieldIdentifier, DataTypeIdentifier, AliasUtil
from sapiopycommons.general.exceptions import SapioException


class AnyFieldInfo:
    """
    Field definition information that can apply to any created field def. This excludes various members of
    AbstractVeloxFieldDefinition such as system_field that wouldn't make sense to edit for a created field def
    used in a temp data type.
    """
    editable: bool
    required: bool
    visible: bool
    description: str | None
    sort_direction: SortDirection | None
    sort_order: int | None
    default_table_column_width: int | None

    def __init__(self, editable: bool = True, required: bool = False, visible: bool = True,
                 description: str | None = None, sort_direction: SortDirection | None = None,
                 sort_order: int | None = None, default_table_column_width: int | None = None):
        """
        :param editable: Whether this field can be edited by the user.
        :param required: Whether input is required for this field before the user can submit the dialog that it is a
            part of.
        :param visible: Whether this field is visible to the user.
        :param description: The description of this field that will appear when the user hovers the cursor over it.
        :param sort_direction: The default sort direction of this field in tables. The user may still change the column
            sorting.
        :param sort_order: The default sort order of this field in tables. The user may still change the column sorting.
        :param default_table_column_width: The width in pixels that this field's column will appear with in tables by
            default. The user may still change the column width.
        """
        self.editable = editable
        self.required = required
        self.visible = visible
        self.description = description
        self.sort_direction = sort_direction
        self.sort_order = sort_order
        self.default_table_column_width = default_table_column_width


class FieldBuilder:
    """
    A class used for building fields for temporary data types. Currently designed to only create fields which can
    be used in client callbacks that use temp data types. Some fields will not be displayed in temp data types,
    including but not limited to: action fields, child/parent/side link fields.
    """
    data_type: str

    def __init__(self, data_type: DataTypeIdentifier = "Default"):
        """
        :param data_type: The data type name that fields created from this builder will use as their data type.
        """
        self.data_type = AliasUtil.to_data_type_name(data_type)

    def accession_field(self, field_name: FieldIdentifier, sequence_key: str, prefix: str | None = None,
                        suffix: str | None = None, number_of_digits: int = 8, starting_value: int = 1,
                        link_out: dict[str, str] | None = None, abstract_info: AnyFieldInfo | None = None, *,
                        data_type_name: DataTypeIdentifier | None = None, display_name: str | None = None) \
            -> VeloxAccessionFieldDefinition:
        """
        Create an accession field definition. Accession fields are text fields which generate a unique value
        that has not been used before, incrementing from the most recently generated value. This can be used when a
        guaranteed unique ID is necessary.
    
        :param field_name: The data field name of this field. Unless a display name is also provided, this doubles as
            the display name.
        :param sequence_key: The key of the accession sequence that this field will use.
        :param prefix: The text that should appear before the numerical value.
        :param suffix: The text that should appear after the numerical value.
        :param number_of_digits: The number of digits in the numerical value.
        :param starting_value: The starting value of the numerical value.
        :param link_out: A dictionary where the keys are the display names of the links and the values are the links to
            navigate the user to if this field is clicked on. If the values contain the string "[[LINK_OUT]]" then that
            macro will be replaced with the value of the string field when it is clicked. The display name is only
            important if there is more than one link in the dictionary, in which case all available link out locations
            will display in a dialog with their display names for the user to select. If a non-empty dictionary is
            provided, this becomes a link-out field.
            If the value is not determined to have the appearance of a URL (e.g. it doesn't start with https://), then
            the system will prepend "https://<app-url>/veloxClient/" to the start of the URL. This allows you to create
            links to other locations in the system without needing to know what the app URL is. For example, if you have
            a link out string field that contains a record ID to a Sample, you could set the link value to
            "#dataType=Sample;recordId=[[LINK_OUT]];view=dataRecord" and the client will, seeing that this is not a
            normal looking URL, route the user to
            https://<app-url>/veloxClient/#dataType=Sample;recordId=[[LINK_OUT]];view=dataRecord, which is the form
            page of the Sample corresponding to the record ID recorded by the field value.
        :param abstract_info: The abstract field info for this field, such as whether it is editable or required.
        :param data_type_name: An optional override for the data type name used for this field. If not provided, then
            the data field name of the FieldBuilder is used.
        :param display_name: An optional override for the display name of this field. If not provided, then the data
            field name doubles as the display name.
        :return: An accession field definition with settings from the input criteria.
        """
        data_type_name: str = AliasUtil.to_data_type_name(data_type_name) if data_type_name else self.data_type
        field_name: str = AliasUtil.to_data_field_name(field_name)
        if abstract_info is None:
            abstract_info = AnyFieldInfo()
        if not display_name:
            display_name = field_name
        # Accession fields lock editable to false.
        abstract_info.editable = False
        link_out, link_out_url = self._convert_link_out(link_out)
        # The unique parameter has no effect, so just always set it to false.
        return VeloxAccessionFieldDefinition(data_type_name, field_name, display_name, sequence_key, prefix, suffix,
                                             number_of_digits, False, starting_value, link_out, link_out_url,
                                             **abstract_info.__dict__)

    def boolean_field(self, field_name: FieldIdentifier, default_value: bool | None = False,
                      abstract_info: AnyFieldInfo | None = None, *, data_type_name: DataTypeIdentifier | None = None,
                      display_name: str | None = None) -> VeloxBooleanFieldDefinition:
        """
        Create a boolean field definition. Boolean fields are fields which may have a value of true or false.
        They appear as a checkbox in the UI. Boolean fields may also have a value of null if the field is not required.

        :param field_name: The data field name of this field. Unless a display name is also provided, this doubles as
            the display name.
        :param default_value: The default value to display in this field before the user edits it.
        :param abstract_info: The abstract field info for this field, such as whether it is editable or required.
        :param data_type_name: An optional override for the data type name used for this field. If not provided, then
            the data field name of the FieldBuilder is used.
        :param display_name: An optional override for the display name of this field. If not provided, then the data
            field name doubles as the display name.
        :return: A boolean field definition with settings from the input criteria.
        """
        data_type_name: str = AliasUtil.to_data_type_name(data_type_name) if data_type_name else self.data_type
        field_name: str = AliasUtil.to_data_field_name(field_name)
        if abstract_info is None:
            abstract_info = AnyFieldInfo()
            # Boolean fields assume that they are required if no abstract info is provided.
            abstract_info.required = True
        if not display_name:
            display_name = field_name
        return VeloxBooleanFieldDefinition(data_type_name, field_name, display_name, default_value,
                                           **abstract_info.__dict__)

    def date_field(self, field_name: FieldIdentifier, default_value: int | None = None, date_time_format: str = "MMM dd, yyyy",
                   static_date: bool = False, abstract_info: AnyFieldInfo | None = None, *,
                   data_type_name: DataTypeIdentifier | None = None, display_name: str | None = None) \
            -> VeloxDateFieldDefinition:
        """
        Create a date field definition. Date fields store date and time information as an integer
        representing the number of milliseconds since the unix epoch. This timestamp is then displayed to users in a
        human-readable format.

        :param field_name: The data field name of this field. Unless a display name is also provided, this doubles as
            the display name.
        :param default_value: The default value to display in this field before the user edits it.
        :param date_time_format: The format that this date field should appear in. The date format is Java-style.
            See https://docs.oracle.com/en/java/javase/18/docs/api/java.base/java/text/SimpleDateFormat.html for more
            details.
        :param static_date: If true, this date displays in UTC regardless of the user's timezone. If false, this date
            displays the time in the user's timezone.
        :param abstract_info: The abstract field info for this field, such as whether it is editable or required.
        :param data_type_name: An optional override for the data type name used for this field. If not provided, then
            the data field name of the FieldBuilder is used.
        :param display_name: An optional override for the display name of this field. If not provided, then the data
            field name doubles as the display name.
        :return: A date field definition with settings from the input criteria.
        """
        data_type_name: str = AliasUtil.to_data_type_name(data_type_name) if data_type_name else self.data_type
        field_name: str = AliasUtil.to_data_field_name(field_name)
        if abstract_info is None:
            abstract_info = AnyFieldInfo()
        if not display_name:
            display_name = field_name
        return VeloxDateFieldDefinition(data_type_name, field_name, display_name, date_time_format, default_value,
                                        static_date, **abstract_info.__dict__)

    def date_range_field(self, field_name: FieldIdentifier, default_value: str | DateRange | None = None,
                         date_time_format: str = "MMM dd, yyyy", static_date: bool = False,
                         abstract_info: AnyFieldInfo | None = None, *, data_type_name: DataTypeIdentifier | None = None,
                         display_name: str | None = None) -> VeloxDateRangeFieldDefinition:
        """
        Create a date range field definition. Date range fields store two unix epoch timestamps as a string of the
        format "[start timestamp]/[end timestamp]". This string is then displayed to users in a human-readable
        format as two dates.

        See the DateRange class from sapiopylib for an easy means of converting to/from millisecond timestamps and a
        date range field's string value.

        :param field_name: The data field name of this field. Unless a display name is also provided, this doubles as
            the display name.
        :param default_value: The default value to display in this field before the user edits it.
        :param date_time_format: The format that this date field should appear in. The date format is Java-style.
            See https://docs.oracle.com/en/java/javase/18/docs/api/java.base/java/text/SimpleDateFormat.html for more
            details.
        :param static_date: If true, these dates display in UTC regardless of the user's timezone. If false, they
            display the time in the user's timezone.
        :param abstract_info: The abstract field info for this field, such as whether it is editable or required.
        :param data_type_name: An optional override for the data type name used for this field. If not provided, then
            the data field name of the FieldBuilder is used.
        :param display_name: An optional override for the display name of this field. If not provided, then the data
            field name doubles as the display name.
        :return: A date range field definition with settings from the input criteria.
        """
        data_type_name: str = AliasUtil.to_data_type_name(data_type_name) if data_type_name else self.data_type
        field_name: str = AliasUtil.to_data_field_name(field_name)
        if abstract_info is None:
            abstract_info = AnyFieldInfo()
        if not display_name:
            display_name = field_name
        if isinstance(default_value, DateRange):
            default_value = str(default_value)
        return VeloxDateRangeFieldDefinition(data_type_name, field_name, display_name, date_time_format, static_date,
                                             default_value, **abstract_info.__dict__)

    def double_field(self, field_name: FieldIdentifier, default_value: float | None = None, min_value: float = -10.**120,
                     max_value: float = 10.**120, precision: int = 1, double_format: SapioDoubleFormat | None = None,
                     abstract_info: AnyFieldInfo | None = None, *, data_type_name: DataTypeIdentifier | None = None,
                     display_name: str | None = None) -> VeloxDoubleFieldDefinition:
        """
        Create a double field definition. Double fields represent decimal numerical values. They can also
        be configured to represent currencies or percentages by changing the format parameter.

        :param field_name: The data field name of this field. Unless a display name is also provided, this doubles as
            the display name.
        :param default_value: The default value to display in this field before the user edits it.
        :param min_value: The minimum allowed value in this field.
        :param max_value: The maximum allowed value in this field.
        :param precision: The number of digits past the decimal point to display for this field.
        :param double_format: The format that this double field is displayed in. If no value is provided, the field
            display as a normal numerical value.
        :param abstract_info: The abstract field info for this field, such as whether it is editable or required.
        :param data_type_name: An optional override for the data type name used for this field. If not provided, then
            the data field name of the FieldBuilder is used.
        :param display_name: An optional override for the display name of this field. If not provided, then the data
            field name doubles as the display name.
        :return: A double field definition with settings from the input criteria.
        """
        data_type_name: str = AliasUtil.to_data_type_name(data_type_name) if data_type_name else self.data_type
        field_name: str = AliasUtil.to_data_field_name(field_name)
        if abstract_info is None:
            abstract_info = AnyFieldInfo()
        if not display_name:
            display_name = field_name
        return VeloxDoubleFieldDefinition(data_type_name, field_name, display_name, min_value, max_value, default_value,
                                          precision, double_format, **abstract_info.__dict__)

    def enum_field(self, field_name: FieldIdentifier, options: list[str], default_value: int | None = None,
                   abstract_info: AnyFieldInfo | None = None, *, data_type_name: DataTypeIdentifier | None = None,
                   display_name: str | None = None) -> VeloxEnumFieldDefinition:
        """
        Create an enum field definition. Enum fields allow for the display of a list of options as a field
        definition without the need of a backing method in the system like pick list or selection lists do. Note that
        when setting the default value or reading the return value of an enum field, the value is an integer
        representing the index of the values list, as opposed to a string for the exact value chosen.

        Note that this field is mainly here for completeness' sake. You can now use the static_values parameter of a
        selection list to achieve the same thing without needing to worry about the field value being the index of the
        options.

        :param field_name: The data field name of this field. Unless a display name is also provided, this doubles as
            the display name.
        :param options: The list of strings that the user may select from for this enum field. Note that when a client
            callback returns the value from an enum field, it will be the index of the option in the options list that
            the user chose.
        :param default_value: The default value to display in this field before the user edits it. This is the index of
            the option from the options list that you wish to appear as the default.
        :param abstract_info: The abstract field info for this field, such as whether it is editable or required.
        :param data_type_name: An optional override for the data type name used for this field. If not provided, then
            the data field name of the FieldBuilder is used.
        :param display_name: An optional override for the display name of this field. If not provided, then the data
            field name doubles as the display name.
        :return: An enum field definition with settings from the input criteria.
        """
        data_type_name: str = AliasUtil.to_data_type_name(data_type_name) if data_type_name else self.data_type
        field_name: str = AliasUtil.to_data_field_name(field_name)
        if abstract_info is None:
            abstract_info = AnyFieldInfo()
        if not display_name:
            display_name = field_name
        return VeloxEnumFieldDefinition(data_type_name, field_name, display_name, default_value, options,
                                        **abstract_info.__dict__)

    def int_field(self, field_name: FieldIdentifier, default_value: int | None = None, min_value: int = -2**31,
                  max_value: int = 2**31 - 1, unique_value: bool = False, abstract_info: AnyFieldInfo | None = None, *,
                  data_type_name: DataTypeIdentifier | None = None, display_name: str | None = None) \
            -> VeloxIntegerFieldDefinition:
        """
        Create an integer field definition. Integer fields are 32-bit whole numbers.

        :param field_name: The data field name of this field. Unless a display name is also provided, this doubles as
            the display name.
        :param default_value: The default value to display in this field before the user edits it.
        :param min_value: The minimum allowed value in this field.
        :param max_value: The maximum allowed value in this field.
        :param unique_value: Whether the value in this field must be unique across all temp records in the dialog.
        :param abstract_info: The abstract field info for this field, such as whether it is editable or required.
        :param data_type_name: An optional override for the data type name used for this field. If not provided, then
            the data field name of the FieldBuilder is used.
        :param display_name: An optional override for the display name of this field. If not provided, then the data
            field name doubles as the display name.
        :return: An integer field definition with settings from the input criteria.
        """
        data_type_name: str = AliasUtil.to_data_type_name(data_type_name) if data_type_name else self.data_type
        field_name: str = AliasUtil.to_data_field_name(field_name)
        if abstract_info is None:
            abstract_info = AnyFieldInfo()
        if not display_name:
            display_name = field_name
        return VeloxIntegerFieldDefinition(data_type_name, field_name, display_name, min_value, max_value,
                                           default_value, unique_value, **abstract_info.__dict__)

    def long_field(self, field_name: FieldIdentifier, default_value: int | None = None, min_value: int = -2**63,
                   max_value: int = 2**63 - 1, unique_value: bool = False, abstract_info: AnyFieldInfo | None = None, *,
                   data_type_name: DataTypeIdentifier | None = None, display_name: str | None = None) \
            -> VeloxLongFieldDefinition:
        """
        Create a long field definition. Long fields are 64-bit whole numbers.

        :param field_name: The data field name of this field. Unless a display name is also provided, this doubles as
            the display name.
        :param default_value: The default value to display in this field before the user edits it.
        :param min_value: The minimum allowed value in this field.
        :param max_value: The maximum allowed value in this field.
        :param unique_value: Whether the value in this field must be unique across all temp records in the dialog.
        :param abstract_info: The abstract field info for this field, such as whether it is editable or required.
        :param data_type_name: An optional override for the data type name used for this field. If not provided, then
            the data field name of the FieldBuilder is used.
        :param display_name: An optional override for the display name of this field. If not provided, then the data
            field name doubles as the display name.
        :return: A long field definition with settings from the input criteria.
        """
        data_type_name: str = AliasUtil.to_data_type_name(data_type_name) if data_type_name else self.data_type
        field_name: str = AliasUtil.to_data_field_name(field_name)
        if abstract_info is None:
            abstract_info = AnyFieldInfo()
        if not display_name:
            display_name = field_name
        return VeloxLongFieldDefinition(data_type_name, field_name, display_name, min_value, max_value, default_value,
                                        unique_value, **abstract_info.__dict__)

    def pick_list_field(self, field_name: FieldIdentifier, pick_list_name: str, default_value: str | None = None,
                        direct_edit: bool = False, abstract_info: AnyFieldInfo | None = None, *,
                        data_type_name: DataTypeIdentifier | None = None, display_name: str | None = None) \
            -> VeloxPickListFieldDefinition:
        """
        Create a pick list field definition. Pick list fields are string fields that display a drop-down list of options
        when being edited by a user. The list of options is backed by a pick list defined in the list manager sections
        of the app setup.

        Selection lists can do everything pick lists can do and more, so often it is better to use a selection list.

        :param field_name: The data field name of this field. Unless a display name is also provided, this doubles as
            the display name.
        :param pick_list_name: The name of the pick list to populate the options of this field.
        :param default_value: The default value to display in this field before the user edits it.
        :param direct_edit: Whether the user may input values not present in the list of options.
        :param abstract_info: The abstract field info for this field, such as whether it is editable or required.
        :param data_type_name: An optional override for the data type name used for this field. If not provided, then
            the data field name of the FieldBuilder is used.
        :param display_name: An optional override for the display name of this field. If not provided, then the data
            field name doubles as the display name.
        :return: A pick list field definition with settings from the input criteria.
        """
        data_type_name: str = AliasUtil.to_data_type_name(data_type_name) if data_type_name else self.data_type
        field_name: str = AliasUtil.to_data_field_name(field_name)
        if abstract_info is None:
            abstract_info = AnyFieldInfo()
        if not display_name:
            display_name = field_name
        return VeloxPickListFieldDefinition(data_type_name, field_name, display_name, pick_list_name, default_value,
                                            direct_edit, **abstract_info.__dict__)

    def selection_list_field(self, field_name: FieldIdentifier, default_value: str | None = None,
                             direct_edit: bool = False, multi_select: bool = False, unique_value: bool = False,
                             abstract_info: AnyFieldInfo | None = None, *, pick_list_name: str | None = None,
                             custom_report_name: str | None = None, plugin_name: str | None = None,
                             static_values: list[str] | None = None, user_list: bool = False,
                             user_group_list: bool = False, non_api_user_list: bool = False,
                             data_type_name: DataTypeIdentifier | None = None, display_name: str | None = None) \
            -> VeloxSelectionFieldDefinition:
        """
        Create a selection list field definition. Selection list fields are string fields that display a drop-down list
        of options when being edited by a user. The list of options can be populated from a number of locations,
        including pick lists, predefined searches (custom reports), all usernames or groups in the system, and more.

        Note that the different list types are mutually exclusive with one another. You must only provide the parameter
        necessary for a singular selection list type.

        :param field_name: The data field name of this field. Unless a display name is also provided, this doubles as
            the display name.
        :param default_value: The default value to display in this field before the user edits it.
        :param direct_edit: Whether the user may input values not present in the list of options.
        :param multi_select: Whether the user may select multiple options from the list of this field.
        :param unique_value: Whether the value in this field must be unique across all temp records in the dialog.
        :param pick_list_name: The name of the pick list to populate the options of this field.
        :param custom_report_name: The name of the custom report (predefined search) to populate the options of this
            field.
        :param plugin_name: The path to the plugin used to populate the options of this field.
        :param static_values: The list of string values used to populate the options of this field.
        :param user_list: Whether this field is populated by a list of all users in the system.
        :param user_group_list: Whether this field is populated by a list of all user groups in the system.
        :param non_api_user_list: Whether this field is populated by a list of all non-API users in the system.
        :param abstract_info: The abstract field info for this field, such as whether it is editable or required.
        :param data_type_name: An optional override for the data type name used for this field. If not provided, then
            the data field name of the FieldBuilder is used.
        :param display_name: An optional override for the display name of this field. If not provided, then the data
            field name doubles as the display name.
        :return: A selection list field definition with settings from the input criteria.
        """
        data_type_name: str = AliasUtil.to_data_type_name(data_type_name) if data_type_name else self.data_type
        field_name: str = AliasUtil.to_data_field_name(field_name)
        if abstract_info is None:
            abstract_info = AnyFieldInfo()
        if not display_name:
            display_name = field_name

        list_mode: ListMode | None = None
        if pick_list_name:
            list_mode = ListMode.LIST
        if custom_report_name:
            if list_mode:
                raise SapioException("Unable to set multiple list modes at once for a selection list.")
            list_mode = ListMode.REPORT
        if plugin_name:
            if list_mode:
                raise SapioException("Unable to set multiple list modes at once for a selection list.")
            list_mode = ListMode.PLUGIN
        if user_list:
            if list_mode:
                raise SapioException("Unable to set multiple list modes at once for a selection list.")
            list_mode = ListMode.USER
        if user_group_list:
            if list_mode:
                raise SapioException("Unable to set multiple list modes at once for a selection list.")
            list_mode = ListMode.USER_GROUP
        if non_api_user_list:
            if list_mode:
                raise SapioException("Unable to set multiple list modes at once for a selection list.")
            list_mode = ListMode.NON_API_USER
        if static_values:
            if list_mode:
                raise SapioException("Unable to set multiple list modes at once for a selection list.")
            # Static values don't have a list mode. Evaluate this last so that the multiple list modes check doesn't
            # need to be more complex.
            # PR-47531: Even though static values don't use an existing list mode, a list mode must still be set.
            list_mode = ListMode.USER

        if not list_mode and static_values is None:
            raise SapioException("A list mode must be chosen for selection list fields.")
        return VeloxSelectionFieldDefinition(data_type_name, field_name, display_name,
                                             list_mode, unique_value, multi_select,
                                             default_value, pick_list_name, custom_report_name,
                                             plugin_name, direct_edit, static_values,
                                             **abstract_info.__dict__)

    def short_field(self, field_name: FieldIdentifier, default_value: int | None = None, min_value: int = -2**15,
                    max_value: int = 2**15 - 1, unique_value: bool = False, abstract_info: AnyFieldInfo | None = None,
                    *, data_type_name: DataTypeIdentifier | None = None, display_name: str | None = None) \
            -> VeloxShortFieldDefinition:
        """
        Create a short field definition. Short fields are 16-bit whole numbers.

        :param field_name: The data field name of this field. Unless a display name is also provided, this doubles as
            the display name.
        :param default_value: The default value to display in this field before the user edits it.
        :param min_value: The minimum allowed value in this field.
        :param max_value: The maximum allowed value in this field.
        :param unique_value: Whether the value in this field must be unique across all temp records in the dialog.
        :param abstract_info: The abstract field info for this field, such as whether it is editable or required.
        :param data_type_name: An optional override for the data type name used for this field. If not provided, then
            the data field name of the FieldBuilder is used.
        :param display_name: An optional override for the display name of this field. If not provided, then the data
            field name doubles as the display name.
        :return: A short field definition with settings from the input criteria.
        """
        data_type_name: str = AliasUtil.to_data_type_name(data_type_name) if data_type_name else self.data_type
        field_name: str = AliasUtil.to_data_field_name(field_name)
        if abstract_info is None:
            abstract_info = AnyFieldInfo()
        if not display_name:
            display_name = field_name
        return VeloxShortFieldDefinition(data_type_name, field_name, display_name, min_value, max_value, default_value,
                                         unique_value, **abstract_info.__dict__)

    def string_field(self, field_name: FieldIdentifier, default_value: str | None = None, max_length: int = 100,
                     unique_value: bool = False, html_editor: bool = False,
                     string_format: SapioStringFormat | None = None, num_lines: int = 1, auto_size: bool = False,
                     link_out: dict[str, str] | None = None, field_validator: FieldValidator | None = None,
                     abstract_info: AnyFieldInfo | None = None, *, data_type_name: DataTypeIdentifier | None = None,
                     display_name: str | None = None) -> VeloxStringFieldDefinition:
        """
        Create a string field definition. String fields represent text, and are highly customizable, allowing the
        field to be plain text or rich HTML, take up one line of space or multiple on a form, format as emails or
        phone numbers, or create links to other websites or other locations in the system.

        :param field_name: The data field name of this field. Unless a display name is also provided, this doubles as
            the display name.
        :param default_value: The default value to display in this field before the user edits it.
        :param max_length: The maximum allowed character length of this field.
        :param unique_value: Whether the value in this field must be unique across all temp records in the dialog.
        :param html_editor: Whether this field allows the user to use an HTML editor.
        :param string_format: The format that this string field is displayed in. If no value is provided, the field
            display as a normal string.
        :param num_lines: The number of lines of space that this field takes up on a form.
        :param auto_size: Whether this field should auto-size itself to fix the text when taking up space on a form.
        :param link_out: A dictionary where the keys are the display names of the links and the values are the links to
            navigate the user to if this field is clicked on. If the values contain the string "[[LINK_OUT]]" then that
            macro will be replaced with the value of the string field when it is clicked. The display name is only
            important if there is more than one link in the dictionary, in which case all available link out locations
            will display in a dialog with their display names for the user to select. If a non-empty dictionary is
            provided, this becomes a link-out field.
            If the value is not determined to have the appearance of a URL (e.g. it doesn't start with https://), then
            the system will prepend "https://<app-url>/veloxClient/" to the start of the URL. This allows you to create
            links to other locations in the system without needing to know what the app URL is. For example, if you have
            a link out string field that contains a record ID to a Sample, you could set the link value to
            "#dataType=Sample;recordId=[[LINK_OUT]];view=dataRecord" and the client will, seeing that this is not a
            normal looking URL, route the user to
            https://<app-url>/veloxClient/#dataType=Sample;recordId=[[LINK_OUT]];view=dataRecord, which is the form
            page of the Sample corresponding to the record ID recorded by the field value.
        :param field_validator: If provided, the user's input for this field must pass the regex of the given validator.
        :param abstract_info: The abstract field info for this field, such as whether it is editable or required.
        :param data_type_name: An optional override for the data type name used for this field. If not provided, then
            the data field name of the FieldBuilder is used.
        :param display_name: An optional override for the display name of this field. If not provided, then the data
            field name doubles as the display name.
        :return: A string field definition with settings from the input criteria.
        """
        data_type_name: str = AliasUtil.to_data_type_name(data_type_name) if data_type_name else self.data_type
        field_name: str = AliasUtil.to_data_field_name(field_name)
        if abstract_info is None:
            abstract_info = AnyFieldInfo()
        if not display_name:
            display_name = field_name
        link_out, link_out_url = self._convert_link_out(link_out)
        return VeloxStringFieldDefinition(data_type_name, field_name, display_name, default_value, max_length,
                                          unique_value, html_editor, string_format, num_lines, auto_size, link_out,
                                          link_out_url, field_validator, **abstract_info.__dict__)

    @staticmethod
    def _convert_link_out(link_out: dict[str, str] | None) -> tuple[bool, str | None]:
        """
        Given a dictionary of link-out URLs, convert them to the string format that the field definition expects.
        """
        if link_out:
            return True, "\t".join([display_name + "\t" + link for display_name, link in link_out.items()])
        return False, None
