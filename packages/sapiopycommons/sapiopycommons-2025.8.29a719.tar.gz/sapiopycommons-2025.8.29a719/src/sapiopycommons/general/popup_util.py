import warnings

from sapiopylib.rest.DataMgmtService import DataMgmtServer
from sapiopylib.rest.pojo.datatype.DataType import DataTypeDefinition
from sapiopylib.rest.pojo.datatype.FieldDefinition import VeloxStringFieldDefinition, AbstractVeloxFieldDefinition, \
    VeloxIntegerFieldDefinition, VeloxDoubleFieldDefinition
from sapiopylib.rest.pojo.webhook.ClientCallbackRequest import FormEntryDialogRequest, OptionDialogRequest, \
    TableEntryDialogRequest, ListDialogRequest, DataRecordSelectionRequest
from sapiopylib.rest.pojo.webhook.WebhookContext import SapioWebhookContext
from sapiopylib.rest.pojo.webhook.WebhookResult import SapioWebhookResult
from sapiopylib.rest.utils.FormBuilder import FormBuilder

from sapiopycommons.general.aliases import SapioRecord, AliasUtil, FieldMap
from sapiopycommons.general.exceptions import SapioException


# FR-46064 - Initial port of PyWebhookUtils to sapiopycommons.
# FR-46097 - Greatly expand the options that PopupUtil provides. (Originally just had two OptionDialogRequest
# and one FormEntryDialogRequest methods.)
# CR-46332 - For any functions that use temporary data types, set the data type name, display name, and plural display
# name in the form builder.
# FR-46716 - Add comments noting that this class is deprecated in favor of CallbackUtil.
class PopupUtil:
    """
    DEPRECATED: Make use of CallbackUtil as of 24.5.

    Methods for creating boilerplate SapioWebhookResults with client callback requests to create popup dialogs.
    """
    @staticmethod
    def form_popup(title: str, msg: str, fields: list[AbstractVeloxFieldDefinition], values: FieldMap = None,
                   column_positions: dict[str, tuple[int, int]] = None, data_type: str = "Default",
                   *, display_name: str | None = None, plural_display_name: str | None = None,
                   request_context: str | None = None) -> SapioWebhookResult:
        """
        DEPRECATED: Make use of CallbackUtil as of 24.5.

        Create a basic form entry dialog.

        The calling webhook must catch the FormEntryDialogResult that the client will send back.

        :param title: The title of the dialog.
        :param msg: The message to display at the top of the form.
        :param fields: The definitions of the fields to display in the form. Fields will be displayed in the order they
            are provided in this list.
        :param values: Sets the default values of the fields.
        :param column_positions: If a tuple is provided for a field name, alters that field's column position and column
            span. (Field order is still determined by the fields list.)
        :param data_type: The data type name for the temporary data type that will be created for this form.
        :param display_name: The display name for the temporary data type. If not provided, defaults to the data type
            name.
        :param plural_display_name: The plural display name for the temporary data type. If not provided, defaults to
            the display name + "s".
        :param request_context: Context that will be returned to the webhook server in the client callback result.
        :return: A SapioWebhookResult with the popup as its client callback request.
        """
        warnings.warn("PopupUtil is deprecated as of 24.5+. Use CallbackUtil instead.", DeprecationWarning)
        if display_name is None:
            display_name = data_type
        if plural_display_name is None:
            plural_display_name = display_name + "s"
        builder = FormBuilder(data_type, display_name, plural_display_name)
        for field_def in fields:
            field_name = field_def.data_field_name
            if values and hasattr(field_def, "default_value"):
                field_def.default_value = values.get(field_name)
            column: int = 0
            span: int = 4
            if column_positions and field_name in column_positions:
                position = column_positions.get(field_name)
                column = position[0]
                span = position[1]
            builder.add_field(field_def, column, span)
        callback = FormEntryDialogRequest(title, msg, builder.get_temporary_data_type(),
                                          callback_context_data=request_context)
        return SapioWebhookResult(True, client_callback_request=callback)

    @staticmethod
    def record_form_popup(context: SapioWebhookContext,
                          title: str, msg: str, fields: list[str], record: SapioRecord,
                          column_positions: dict[str, tuple[int, int]] = None, editable: bool | None = True,
                          *, request_context: str | None = None) -> SapioWebhookResult:
        """
        DEPRECATED: Make use of CallbackUtil as of 24.5.

        Create a basic form dialog for a record with displayed fields from the record data type.

        Makes webservice calls to get the data field and type definitions of the given data type.
        The calling webhook must catch the FormEntryDialogResult that the client will send back.

        :param context: The current webhook context.
        :param title: The title of the dialog.
        :param msg: The message to display in the dialog.
        :param fields: The data field names of the fields from the record to display in the form. Fields will be
            displayed in the order they are provided in this list.
        :param record: The record to display the values of.
        :param column_positions: If a tuple is provided for a field name, alters that field's column position and column
            span. (Field order is still determined by the fields list.)
        :param editable: If true, all fields are displayed as editable. If false, all fields are displayed as
            uneditable. If none, only those fields that are defined as editable by the data designer will be editable.
        :param request_context: Context that will be returned to the webhook server in the client callback result.
        :return: A SapioWebhookResult with the popup as its client callback request.
        """
        warnings.warn("PopupUtil is deprecated as of 24.5+. Use CallbackUtil instead.", DeprecationWarning)
        # Get the field definitions of the data type.
        data_type: str = record.data_type_name
        type_man = DataMgmtServer.get_data_type_manager(context.user)
        type_def: DataTypeDefinition = type_man.get_data_type_definition(data_type)
        field_defs: dict[str, AbstractVeloxFieldDefinition] = {x.data_field_name: x for x in
                                                               type_man.get_field_definition_list(data_type)}

        # Build the form using only those fields that are desired.
        builder = FormBuilder(data_type, type_def.display_name, type_def.plural_display_name)
        for field_name in fields:
            field_def = field_defs.get(field_name)
            if field_def is None:
                raise SapioException(f"No field of name \"{field_name}\" in field definitions of type \"{data_type}\"")
            if editable is not None:
                field_def.editable = editable
            field_def.visible = True
            if hasattr(field_def, "default_value"):
                field_def.default_value = record.get_field_value(field_name)
            column: int = 0
            span: int = 4
            if column_positions and field_name in column_positions:
                position = column_positions.get(field_name)
                column = position[0]
                span = position[1]
            builder.add_field(field_def, column, span)
        temp_type_def = builder.get_temporary_data_type()
        callback = FormEntryDialogRequest(title, msg, temp_type_def,
                                          callback_context_data=request_context)
        return SapioWebhookResult(True, client_callback_request=callback)

    @staticmethod
    def string_field_popup(title: str, msg: str, field_name: str, default_value: str | None = None,
                           max_length: int | None = None, editable: bool = True, data_type: str = "Default",
                           *, display_name: str | None = None, plural_display_name: str | None = None,
                           request_context: str | None = None, **kwargs) -> SapioWebhookResult:
        """
        DEPRECATED: Make use of CallbackUtil as of 24.5.

        Create a form dialog with a single string field. May take additional parameters to be passed to the string field
        definition.

        The calling webhook must catch the FormEntryDialogResult that the client will send back.

        :param title: The title of the dialog.
        :param msg: The message to display in the dialog.
        :param field_name: The name and display name of the string field.
        :param default_value: The default value to place into the string field, if any.
        :param max_length: The max length of the string value. If not provided, uses the length of the default value.
            If neither this or a default value are not provided, defaults to 100 characters.
        :param editable: Whether the user may edit the contents of the string field.
        :param data_type: The data type name for the temporary data type that will be created for this form.
        :param display_name: The display name for the temporary data type. If not provided, defaults to the data type
            name.
        :param plural_display_name: The plural display name for the temporary data type. If not provided, defaults to
            the display name + "s".
        :param request_context: Context that will be returned to the webhook server in the client callback result.
        :return: A SapioWebhookResult with the popup as its client callback request.
        """
        warnings.warn("PopupUtil is deprecated as of 24.5+. Use CallbackUtil instead.", DeprecationWarning)
        if max_length is None:
            max_length = len(default_value) if default_value else 100
        string_field = VeloxStringFieldDefinition(data_type, field_name, field_name, default_value=default_value,
                                                  max_length=max_length, editable=editable, **kwargs)
        return PopupUtil.form_popup(title, msg, [string_field], data_type=data_type, display_name=display_name,
                                    plural_display_name=plural_display_name, request_context=request_context)

    @staticmethod
    def integer_field_popup(title: str, msg: str, field_name: str, default_value: int = None, min_value: int = -10000,
                            max_value: int = 10000, data_type: str = "Default", editable: bool = True,
                            *, display_name: str | None = None, plural_display_name: str | None = None,
                            request_context: str | None = None, **kwargs) -> SapioWebhookResult:
        """
        DEPRECATED: Make use of CallbackUtil as of 24.5.

        Create a form dialog with a single integer field. May take additional parameters to be passed to the integer
        field definition.

        The calling webhook must catch the FormEntryDialogResult that the client will send back.

        :param title: The title of the dialog.
        :param msg: The message to display in the dialog.
        :param field_name: The name and display name of the integer field.
        :param default_value: The default value to place into the integer field. If not provided, defaults to the 0 or
            the minimum value, whichever is higher.
        :param min_value: The minimum allowed value of the input.
        :param max_value: The maximum allowed value of the input.
        :param data_type: The data type name for the temporary data type that will be created for this form.
        :param editable: Whether the user may edit the contents of the integer field.
        :param display_name: The display name for the temporary data type. If not provided, defaults to the data type
            name.
        :param plural_display_name: The plural display name for the temporary data type. If not provided, defaults to
            the display name + "s".
        :param request_context: Context that will be returned to the webhook server in the client callback result.
        :return: A SapioWebhookResult with the popup as its client callback request.
        """
        warnings.warn("PopupUtil is deprecated as of 24.5+. Use CallbackUtil instead.", DeprecationWarning)
        if default_value is None:
            default_value = max(0, min_value)
        integer_field = VeloxIntegerFieldDefinition(data_type, field_name, field_name, default_value=default_value,
                                                    min_value=min_value, max_value=max_value, editable=editable,
                                                    **kwargs)
        return PopupUtil.form_popup(title, msg, [integer_field], data_type=data_type, display_name=display_name,
                                    plural_display_name=plural_display_name, request_context=request_context)

    @staticmethod
    def double_field_popup(title: str, msg: str, field_name: str, default_value: float = None,
                           min_value: float = -10000000, max_value: float = 100000000,
                           data_type: str = "Default", editable: bool = True, *, display_name: str | None = None,
                           plural_display_name: str | None = None, request_context: str | None = None, **kwargs) \
            -> SapioWebhookResult:
        """
        DEPRECATED: Make use of CallbackUtil as of 24.5.

        Create a form dialog with a single double field. May take additional parameters to be passed to the double
        field definition.

        The calling webhook must catch the FormEntryDialogResult that the client will send back.

        :param title: The title of the dialog.
        :param msg: The message to display in the dialog.
        :param field_name: The name and display name of the double field.
        :param default_value: The default value to place into the double field. If not provided, defaults to the 0 or
            the minimum value, whichever is higher.
        :param min_value: The minimum allowed value of the input.
        :param max_value: The maximum allowed value of the input.
        :param data_type: The data type name for the temporary data type that will be created for this form.
        :param editable: Whether the user may edit the contents of the double field.
        :param display_name: The display name for the temporary data type. If not provided, defaults to the data type
            name.
        :param plural_display_name: The plural display name for the temporary data type. If not provided, defaults to
            the display name + "s".
        :param request_context: Context that will be returned to the webhook server in the client callback result.
        :return: A SapioWebhookResult with the popup as its client callback request.
        """
        warnings.warn("PopupUtil is deprecated as of 24.5+. Use CallbackUtil instead.", DeprecationWarning)
        if default_value is None:
            default_value = min_value
        double_field = VeloxDoubleFieldDefinition(data_type, field_name, field_name, default_value=default_value,
                                                  min_value=min_value, max_value=max_value, editable=editable, **kwargs)
        return PopupUtil.form_popup(title, msg, [double_field], data_type=data_type, display_name=display_name,
                                    plural_display_name=plural_display_name, request_context=request_context)

    @staticmethod
    def table_popup(title: str, msg: str, fields: list[AbstractVeloxFieldDefinition], values: list[FieldMap],
                    *, data_type: str = "Default", display_name: str | None = None,
                    plural_display_name: str | None = None, request_context: str | None = None) -> SapioWebhookResult:
        """
        DEPRECATED: Make use of CallbackUtil as of 24.5.

        Create a basic table entry dialog.

        The calling webhook must catch the TableEntryDialogResult that the client will send back.

        :param title: The title of the dialog.
        :param msg: The message to display at the top of the form.
        :param fields: The definitions of the fields to display as table columns. Fields will be displayed in the order
            they are provided in this list.
        :param values: The values to set for each row of the table.
        :param data_type: The data type name for the temporary data type that will be created for this table.
        :param display_name: The display name for the temporary data type. If not provided, defaults to the data type
            name.
        :param plural_display_name: The plural display name for the temporary data type. If not provided, defaults to
            the display name + "s".
        :param request_context: Context that will be returned to the webhook server in the client callback result.
        :return: A SapioWebhookResult with the popup as its client callback request.
        """
        warnings.warn("PopupUtil is deprecated as of 24.5+. Use CallbackUtil instead.", DeprecationWarning)
        if display_name is None:
            display_name = data_type
        if plural_display_name is None:
            plural_display_name = display_name + "s"
        builder = FormBuilder(data_type, display_name, plural_display_name)
        for column in fields:
            builder.add_field(column)
        temp_type_def = builder.get_temporary_data_type()
        callback = TableEntryDialogRequest(title, msg, temp_type_def, values,
                                           callback_context_data=request_context)
        return SapioWebhookResult(True, client_callback_request=callback)

    @staticmethod
    def record_table_popup(context: SapioWebhookContext,
                           title: str, msg: str, fields: list[str], records: list[SapioRecord],
                           editable: bool | None = True, *, request_context: str | None = None) -> SapioWebhookResult:
        """
        DEPRECATED: Make use of CallbackUtil as of 24.5.

        Create a table dialog for a list of record where the columns are specific fields from the record data type.

        Makes webservice calls to get the data field and type definitions of the given data type.
        The calling webhook must catch the TableEntryDialogResult that the client will send back.

        :param context: The current webhook context
        :param title: The title of the dialog.
        :param msg: The message to display in the dialog.
        :param records: The records to display as rows in the table.
        :param fields: The names of the fields to display as columns in the table. Fields will be displayed in the order
            they are provided in this list.
        :param editable: If true, all fields are displayed as editable. If false, all fields are displayed as
            uneditable. If none, only those fields that are defined as editable by the data designer will be editable.
        :param request_context: Context that will be returned to the webhook server in the client callback result.
        :return: A SapioWebhookResult with the popup as its client callback request.
        """
        warnings.warn("PopupUtil is deprecated as of 24.5+. Use CallbackUtil instead.", DeprecationWarning)
        if not records:
            raise SapioException("No records provided.")
        data_types: set[str] = {x.data_type_name for x in records}
        if len(data_types) > 1:
            raise SapioException("Multiple data type names encountered in records list for record table popup.")
        data_type: str = data_types.pop()
        # Get the field maps from the records.
        field_map_list: list[FieldMap] = AliasUtil.to_field_map_list(records)
        # Get the field definitions of the data type.
        type_man = DataMgmtServer.get_data_type_manager(context.user)
        type_def: DataTypeDefinition = type_man.get_data_type_definition(data_type)
        field_defs: dict[str, AbstractVeloxFieldDefinition] = {x.data_field_name: x for x in
                                                               type_man.get_field_definition_list(data_type)}

        # Build the form using only those fields that are desired.
        builder = FormBuilder(data_type, type_def.display_name, type_def.plural_display_name)
        for field_name in fields:
            field_def = field_defs.get(field_name)
            if field_def is None:
                raise SapioException(f"No field of name \"{field_name}\" in field definitions of type \"{data_type}\"")
            if editable is not None:
                field_def.editable = editable
            field_def.visible = True
            # Key fields display their columns in order before all non-key fields.
            # Unmark key fields so that the column order is respected exactly as the caller provides it.
            field_def.key_field = False
            builder.add_field(field_def)
        temp_type_def = builder.get_temporary_data_type()
        callback = TableEntryDialogRequest(title, msg, temp_type_def, field_map_list,
                                           callback_context_data=request_context)
        return SapioWebhookResult(True, client_callback_request=callback)

    @staticmethod
    def record_selection_popup(context: SapioWebhookContext,
                               msg: str, fields: list[str], records: list[SapioRecord], multi_select: bool = True,
                               *, request_context: str | None = None) -> SapioWebhookResult:
        """
        DEPRECATED: Make use of CallbackUtil as of 24.5.

        Create a record selection dialog for a list of record where the columns are specific fields from the record data
        type.

        Makes webservice calls to get the data field and type definitions of the given data type.
        The calling webhook must catch the DataRecordSelectionResult that the client will send back.

        :param context: The current webhook context
        :param msg: The message to display in the dialog.
        :param records: The records to display as rows in the table.
        :param fields: The names of the fields to display as columns in the table. Fields will be displayed in the order
            they are provided in this list.
        :param multi_select: Whether the user is able to select multiple records from the list.
        :param request_context: Context that will be returned to the webhook server in the client callback result.
        :return: A SapioWebhookResult with the popup as its client callback request.
        """
        warnings.warn("PopupUtil is deprecated as of 24.5+. Use CallbackUtil instead.", DeprecationWarning)
        if not records:
            raise SapioException("No records provided.")
        data_types: set[str] = {x.data_type_name for x in records}
        if len(data_types) > 1:
            raise SapioException("Multiple data type names encountered in records list for record table popup.")
        data_type: str = data_types.pop()
        # Get the field maps from the records.
        field_map_list: list[FieldMap] = AliasUtil.to_field_map_list(records)
        # Get the field definitions of the data type.
        type_man = DataMgmtServer.get_data_type_manager(context.user)
        type_def: DataTypeDefinition = type_man.get_data_type_definition(data_type)
        field_defs: dict[str, AbstractVeloxFieldDefinition] = {x.data_field_name: x for x in
                                                               type_man.get_field_definition_list(data_type)}

        # Build the form using only those fields that are desired.
        field_def_list: list = []
        for field_name in fields:
            field_def = field_defs.get(field_name)
            if field_def is None:
                raise SapioException(f"No field of name \"{field_name}\" in field definitions of type \"{data_type}\"")
            field_def.visible = True
            # Key fields display their columns in order before all non-key fields.
            # Unmark key fields so that the column order is respected exactly as the caller provides it.
            field_def.key_field = False
            field_def_list.append(field_def)
        callback = DataRecordSelectionRequest(type_def.display_name, type_def.plural_display_name,
                                              field_def_list, field_map_list, msg, multi_select,
                                              callback_context_data=request_context)
        return SapioWebhookResult(True, client_callback_request=callback)

    @staticmethod
    def list_popup(title: str, options: list[str], multi_select: bool = False,
                   *, request_context: str | None = None) -> SapioWebhookResult:
        """
        DEPRECATED: Make use of CallbackUtil as of 24.5.

        Create a list dialog with the given options for the user to choose from.

        The calling webhook must catch the ListDialogResult that the client will send back.

        :param title: The title of the dialog.
        :param options: The list options that the user has to choose from.
        :param multi_select: Whether the user is able to select multiple options from the list.
        :param request_context: Context that will be returned to the webhook server in the client callback result.
        :return: A SapioWebhookResult with the popup as its client callback request.
        """
        warnings.warn("PopupUtil is deprecated as of 24.5+. Use CallbackUtil instead.", DeprecationWarning)
        callback = ListDialogRequest(title, multi_select, options,
                                     callback_context_data=request_context)
        return SapioWebhookResult(True, client_callback_request=callback)

    @staticmethod
    def option_popup(title: str, msg: str, options: list[str], default_option: int = 0, user_can_cancel: bool = False,
                     *, request_context: str | None = None) -> SapioWebhookResult:
        """
        DEPRECATED: Make use of CallbackUtil as of 24.5.

        Create an option dialog with the given options for the user to choose from.

        The calling webhook must catch the OptionDialogResult that the client will send back.

        :param title: The title of the dialog.
        :param msg: The message to display in the dialog.
        :param options: The button options that the user has to choose from.
        :param default_option: The index of the option in the options list that defaults as the first choice.
        :param user_can_cancel: True if the user is able to click the X to close the dialog, returning
            user_cancelled = True in the client callback result. False if the user cannot close the dialog without
            selecting an option.
        :param request_context: Context that will be returned to the webhook server in the client callback result.
        :return: A SapioWebhookResult with the popup as its client callback request.
        """
        warnings.warn("PopupUtil is deprecated as of 24.5+. Use CallbackUtil instead.", DeprecationWarning)
        callback = OptionDialogRequest(title, msg, options, default_option, user_can_cancel,
                                       callback_context_data=request_context)
        return SapioWebhookResult(True, client_callback_request=callback)

    @staticmethod
    def ok_popup(title: str, msg: str, user_can_cancel: bool = False, *, request_context: str | None = None) \
            -> SapioWebhookResult:
        """
        DEPRECATED: Make use of CallbackUtil as of 24.5.

        Create an option dialog where the only option is "OK".

        The calling webhook must catch the OptionDialogResult that the client will send back.

        :param title: The title of the dialog.
        :param msg: The message to display in the dialog.
        :param user_can_cancel: True if the user is able to click the X to close the dialog, returning
            user_cancelled = True in the client callback result. False if the user cannot close the dialog without
            selecting an option.
        :param request_context: Context that will be returned to the webhook server in the client callback result.
        :return: A SapioWebhookResult with the popup as its client callback request.
        """
        warnings.warn("PopupUtil is deprecated as of 24.5+. Use CallbackUtil instead.", DeprecationWarning)
        return PopupUtil.option_popup(title, msg, ["OK"], 0, user_can_cancel, request_context=request_context)

    @staticmethod
    def yes_no_popup(title: str, msg: str, default_yes: bool = True, user_can_cancel: bool = False,
                     *, request_context: str | None = None) -> SapioWebhookResult:
        """
        DEPRECATED: Make use of CallbackUtil as of 24.5.

        Create an option dialog where the only options are "Yes" and "No".

        The calling webhook must catch the OptionDialogResult that the client will send back.

        :param title: The title of the dialog.
        :param msg: The message to display in the dialog.
        :param default_yes: If true, "Yes" is the default choice. Otherwise, the default choice is "No".
        :param user_can_cancel: True if the user is able to click the X to close the dialog, returning
            user_cancelled = True in the client callback result. False if the user cannot close the dialog without
            selecting an option.
        :param request_context: Context that will be returned to the webhook server in the client callback result.
        :return: A SapioWebhookResult with the popup as its client callback request.
        """
        warnings.warn("PopupUtil is deprecated as of 24.5+. Use CallbackUtil instead.", DeprecationWarning)
        return PopupUtil.option_popup(title, msg, ["Yes", "No"], 0 if default_yes else 1, user_can_cancel,
                                      request_context=request_context)

    # FR-46097 - Deprecating the three original functions for ones with briefer names. Functionality is unchanged.
    @staticmethod
    def display_form_popup(title: str, field_name: str, msg: str, data_type: str = "Popup",
                           request_context: str | None = None) -> SapioWebhookResult:
        """
        DEPRECATED: Make use of CallbackUtil as of 24.5.

        Deprecated for PopupUtil.text_field_popup.
        """
        warnings.warn("PopupUtil is deprecated as of 24.5+. Use CallbackUtil instead.", DeprecationWarning)
        return PopupUtil.string_field_popup(title, "", field_name, msg, len(msg), False, data_type,
                                            request_context=request_context, auto_size=True)

    @staticmethod
    def display_option_popup(title: str, msg: str, options: list[str], user_can_cancel: bool = False,
                             request_context: str | None = None) -> SapioWebhookResult:
        """
        DEPRECATED: Make use of CallbackUtil as of 24.5.

        Deprecated for PopupUtil.option_popup.
        """
        warnings.warn("PopupUtil is deprecated as of 24.5+. Use CallbackUtil instead.", DeprecationWarning)
        return PopupUtil.option_popup(title, msg, options, 0, user_can_cancel, request_context=request_context)

    @staticmethod
    def display_ok_popup(title: str, msg: str, request_context: str | None = None) -> SapioWebhookResult:
        """
        DEPRECATED: Make use of CallbackUtil as of 24.5.

        Deprecated for PopupUtil.ok_popup.
        """
        warnings.warn("PopupUtil is deprecated as of 24.5+. Use CallbackUtil instead.", DeprecationWarning)
        return PopupUtil.ok_popup(title, msg, False, request_context=request_context)
