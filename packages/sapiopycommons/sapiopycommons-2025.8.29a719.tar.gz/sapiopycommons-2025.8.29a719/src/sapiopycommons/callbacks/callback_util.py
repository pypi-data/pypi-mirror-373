from __future__ import annotations

import io
import re
import warnings
from copy import copy
from enum import Enum
from typing import Iterable, TypeAlias, Any, Callable, Container, Collection
from weakref import WeakValueDictionary

from requests import ReadTimeout
from sapiopylib.rest.ClientCallbackService import ClientCallback
from sapiopylib.rest.DataMgmtService import DataMgmtServer
from sapiopylib.rest.DataTypeService import DataTypeManager
from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.pojo.CustomReport import CustomReport, CustomReportCriteria
from sapiopylib.rest.pojo.DataRecord import DataRecord
from sapiopylib.rest.pojo.datatype.DataType import DataTypeDefinition
from sapiopylib.rest.pojo.datatype.DataTypeLayout import DataTypeLayout
from sapiopylib.rest.pojo.datatype.FieldDefinition import AbstractVeloxFieldDefinition, VeloxStringFieldDefinition, \
    VeloxIntegerFieldDefinition, VeloxDoubleFieldDefinition, FieldType
from sapiopylib.rest.pojo.datatype.TemporaryDataType import TemporaryDataType
from sapiopylib.rest.pojo.webhook.ClientCallbackRequest import OptionDialogRequest, ListDialogRequest, \
    FormEntryDialogRequest, InputDialogCriteria, TableEntryDialogRequest, ESigningRequestPojo, \
    DataRecordDialogRequest, InputSelectionRequest, FilePromptRequest, MultiFilePromptRequest, \
    TempTableSelectionRequest, DisplayPopupRequest, PopupType
from sapiopylib.rest.pojo.webhook.ClientCallbackResult import ESigningResponsePojo
from sapiopylib.rest.pojo.webhook.WebhookEnums import FormAccessLevel, ScanToSelectCriteria, SearchType
from sapiopylib.rest.utils.DataTypeCacheManager import DataTypeCacheManager
from sapiopylib.rest.utils.FormBuilder import FormBuilder
from sapiopylib.rest.utils.recorddatasinks import InMemoryRecordDataSink
from sapiopylib.rest.utils.recordmodel.PyRecordModel import PyRecordModel
from sapiopylib.rest.utils.recordmodel.RecordModelWrapper import WrappedType

from sapiopycommons.callbacks.field_builder import FieldBuilder, AnyFieldInfo
from sapiopycommons.files.file_util import FileUtil
from sapiopycommons.general.aliases import FieldMap, SapioRecord, AliasUtil, RecordIdentifier, FieldValue, \
    UserIdentifier, FieldIdentifier, DataTypeIdentifier
from sapiopycommons.general.custom_report_util import CustomReportUtil
from sapiopycommons.general.exceptions import SapioUserCancelledException, SapioException, SapioUserErrorException, \
    SapioDialogTimeoutException
from sapiopycommons.general.time_util import TimeUtil
from sapiopycommons.recordmodel.record_handler import RecordHandler

DataTypeLayoutIdentifier: TypeAlias = DataTypeLayout | str | None


# FR-47690: Added enum to customize blank handling result behavior, instead of using the require_selection/input
# boolean parameter.
class BlankResultHandling(Enum):
    """
    An enum that controls how blank results are handled in dialogs.
    """
    DEFAULT = 0
    """Used only by dialog functions. If a dialog function parameter is set to this value, then the blank result
    handling of the CallbackUtil is used."""
    REPEAT = 1
    """If the user provides a blank result, repeat the dialog."""
    CANCEL = 2
    """If the user provides a blank result, throw a cancel exception."""
    RETURN = 3
    """If the user provides a blank result, return it to the caller."""


# CR-47521: Updated various parameter type hints from list or Iterable to more specific type hints.
# If we need to iterate over the parameter, then it is Iterable.
# If we need to see if the parameter contains a value, then it is Container.
# If the length/size of the parameter is needed, then it is Collection.
# If we need to access the parameter by an index, then it is Sequence. (This excludes sets and dictionaries, so it's
# probably better to accept a Collection then cast the parameter to a list if you need to get an element from it.)
class CallbackUtil:
    user: SapioUser
    callback: ClientCallback
    rec_handler: RecordHandler
    dt_man: DataTypeManager
    dt_cache: DataTypeCacheManager
    _original_timeout: int
    timeout_seconds: int
    width_pixels: int | None
    width_percent: float | None
    _default_blank_result_handling: BlankResultHandling

    __instances: WeakValueDictionary[SapioUser, CallbackUtil] = WeakValueDictionary()
    __initialized: bool

    # TODO: Remove this if ever the DataTypeCacheManager starts handling it.
    __layouts: dict[str, dict[str, DataTypeLayout]]
    """A cache for data type layouts that have been requested by this CallbackUtil."""

    def __new__(cls, context: UserIdentifier):
        """
        :param context: The current webhook context or a user object to send requests from.
        """
        user = AliasUtil.to_sapio_user(context)
        obj = cls.__instances.get(user)
        if not obj:
            obj = object.__new__(cls)
            obj.__initialized = False
            cls.__instances[user] = obj
        return obj

    def __init__(self, context: UserIdentifier):
        """
        :param context: The current webhook context or a user object to send requests from.
        """
        if self.__initialized:
            return
        self.__initialized = True

        self.user = AliasUtil.to_sapio_user(context)
        self.callback = DataMgmtServer.get_client_callback(self.user)
        self.rec_handler = RecordHandler(self.user)
        self.dt_man = DataMgmtServer.get_data_type_manager(self.user)
        self.dt_cache = DataTypeCacheManager(self.user)
        self._original_timeout = self.user.timeout_seconds
        self.timeout_seconds = self.user.timeout_seconds
        self.width_pixels = None
        self.width_percent = None
        self._default_blank_result_handling = BlankResultHandling.CANCEL
        self.__layouts = {}

    def set_dialog_width(self, width_pixels: int | None = None, width_percent: float | None = None):
        """
        Set the width that dialogs will appear as for those dialogs that support specifying their width.

        :param width_pixels: The number of pixels wide that dialogs will appear as.
        :param width_percent: The percentage (as a value between 0 and 1) of the client's screen width that dialogs
            will appear as.
        """
        if width_pixels is not None and width_percent is not None:
            raise SapioException("Cannot set both width_pixels and width_percent at once.")
        self.width_pixels = width_pixels
        self.width_percent = width_percent

    def set_dialog_timeout(self, timeout: int):
        """
        Alter the timeout time used for callback requests that create dialogs for the user to interact with. By default,
        a CallbackUtil will use the timeout time of the SapioUser provided to it. By altering this, a different timeout
        time is used.

        :param timeout: The number of seconds that must elapse before a SapioDialogTimeoutException is thrown by
            any callback that creates a dialog for the user to interact with.
        """
        self.timeout_seconds = timeout

    def set_default_blank_result_handling(self, handling: BlankResultHandling):
        """
        Set the default handling of blank results provided by the user in certain dialogs. This will only be used
        if the dialog functions have their own blank_result_handling parameter set to DEFAULT.

        :param handling: The handling to use for blank results in dialogs.
        """
        if not isinstance(handling, BlankResultHandling):
            raise SapioException("Invalid blank result handling provided.")
        if handling == BlankResultHandling.DEFAULT:
            raise SapioException("Blank result handling cannot be set to DEFAULT.")
        self._default_blank_result_handling = handling

    def toaster_popup(self, message: str, title: str = "", popup_type: PopupType = PopupType.Info) -> None:
        """
        Display a toaster popup in the bottom right corner of the user's screen.

        :param message: The message to display in the toaster. This can be formatted using HTML elements.
        :param title: The title to display at the top of the toaster.
        :param popup_type: The popup type to use for the toaster. This controls the color that the toaster appears with.
            Info is blue, Success is green, Warning is yellow, and Error is red
        """
        self.callback.display_popup(DisplayPopupRequest(title, message, popup_type))

    def display_info(self, message: str) -> None:
        """
        Display an info message to the user in a dialog. Repeated calls to this function will append the new messages
        to the same dialog if it is still opened by the user.

        :param message: The message to display to the user. This can be formatted using HTML elements.
        """
        self.callback.display_info(message)

    def display_warning(self, message: str) -> None:
        """
        Display a warning message to the user in a dialog. Repeated calls to this function will append the new messages
        to the same dialog if it is still opened by the user.

        :param message: The message to display to the user. This can be formatted using HTML elements.
        """
        self.callback.display_warning(message)

    def display_error(self, message: str) -> None:
        """
        Display an error message to the user in a dialog. Repeated calls to this function will append the new messages
        to the same dialog if it is still opened by the user.

        :param message: The message to display to the user. This can be formatted using HTML elements.
        """
        self.callback.display_error(message)

    def option_dialog(self, title: str, msg: str, options: Iterable[str], default_option: int = 0,
                      user_can_cancel: bool = False) -> str:
        """
        Create an option dialog with the given options for the user to choose from.

        :param title: The title of the dialog.
        :param msg: The message to display in the dialog. This can be formatted using HTML elements.
        :param options: The button options that the user has to choose from.
        :param default_option: The index of the option in the options list that defaults as the first choice.
        :param user_can_cancel: True if the user is able to click the X to close the dialog. False if the user cannot
            close the dialog without selecting an option. If the user is able to cancel and does so, a
            SapioUserCancelledException is thrown.
        :return: The name of the button that the user selected.
        """
        if not options:
            raise SapioException("No options provided.")

        # Convert the iterable of options to a list of options.
        options: list[str] = list(options)

        # Send the request to the user.
        request = OptionDialogRequest(title, msg, options, default_option, user_can_cancel,
                                      width_in_pixels=self.width_pixels, width_percentage=self.width_percent)
        response: int = self.__send_dialog(request, self.callback.show_option_dialog)
        return options[response]

    def ok_dialog(self, title: str, msg: str) -> None:
        """
        Create an option dialog where the only option is "OK". Doesn't allow the user to cancel the
        dialog using the X in the top right corner. Returns nothing.

        :param title: The title of the dialog.
        :param msg: The message to display in the dialog. This can be formatted using HTML elements.
        """
        self.option_dialog(title, msg, ["OK"], 0, False)

    def ok_cancel_dialog(self, title: str, msg: str, default_ok: bool = True) -> bool:
        """
        Create an option dialog where the only options are "OK" and "Cancel". Doesn't allow the user to cancel the
        dialog using the X in the top right corner.

        :param title: The title of the dialog.
        :param msg: The message to display in the dialog. This can be formatted using HTML elements.
        :param default_ok: If true, "OK" is the default choice. Otherwise, the default choice is "Cancel".
        :return: True if the user selected OK. False if the user selected Cancel.
        """
        return self.option_dialog(title, msg, ["OK", "Cancel"], 0 if default_ok else 1, False) == "OK"

    def yes_no_dialog(self, title: str, msg: str, default_yes: bool = True) -> bool:
        """
        Create an option dialog where the only options are "Yes" and "No". Doesn't allow the user to cancel the
        dialog using the X in the top right corner.

        :param title: The title of the dialog.
        :param msg: The message to display in the dialog. This can be formatted using HTML elements.
        :param default_yes: If true, "Yes" is the default choice. Otherwise, the default choice is "No".
        :return: True if the user selected Yes. False if the user selected No.
        """
        return self.option_dialog(title, msg, ["Yes", "No"], 0 if default_yes else 1, False) == "Yes"

    # FR-47690: Added function.
    def accept_decline_dialog(self, title: str, msg: str, default_accept: bool = True) -> bool:
        """
        Create an option dialog where the only options are "Accept" and "Decline". Doesn't allow the user to cancel the
        dialog using the X in the top right corner.

        :param title: The title of the dialog.
        :param msg: The message to display in the dialog. This can be formatted using HTML elements.
        :param default_accept: If true, "Accept" is the default choice. Otherwise, the default choice is "Decline".
        :return: True if the user selected Accept. False if the user selected Decline.
        """
        return self.option_dialog(title, msg, ["Accept", "Decline"], 0 if default_accept else 1, False) == "Accept"

    # FR-47690: Added function.
    def confirm_deny_dialog(self, title: str, msg: str, default_confirm: bool = True) -> bool:
        """
        Create an option dialog where the only options are "Confirm" and "Deny". Doesn't allow the user to cancel the
        dialog using the X in the top right corner.

        :param title: The title of the dialog.
        :param msg: The message to display in the dialog. This can be formatted using HTML elements.
        :param default_confirm: If true, "Confirm" is the default choice. Otherwise, the default choice is "Deny".
        :return: True if the user selected Confirm. False if the user selected Deny.
        """
        return self.option_dialog(title, msg, ["Confirm", "Deny"], 0 if default_confirm else 1, False) == "Confirm"

    # CR-47310: Add a parameter to the list, input, selection, and e-sign dialog functions to control reprompting the
    # user if no input/selection/valid credentials are provided.
    # FR-47690: Added shortcut_single_option parameter. Updated with blank result handling behavior.
    def list_dialog(self,
                    title: str,
                    options: Iterable[str],
                    multi_select: bool = False,
                    preselected_values: Iterable[str] | None = None,
                    *,
                    shortcut_single_option: bool = True,
                    require_selection = None,
                    blank_result_handling: BlankResultHandling = BlankResultHandling.DEFAULT,
                    repeat_message: str | None = "Please provide a selection to continue.",
                    cancel_message: str | None = "No selection was provided. Cancelling dialog.") -> list[str]:
        """
        Create a list dialog with the given options for the user to choose from.

        :param title: The title of the dialog.
        :param options: The list options that the user has to choose from.
        :param multi_select: Whether the user is able to select multiple options from the list.
        :param preselected_values: A list of values that will already be selected when the list dialog is created. The
            user can unselect these values if they want to.
        :param shortcut_single_option: If true, then if the list contains only one option, the dialog will not be shown
            and the single option will be returned immediately.
        :param require_selection: DEPRECATED. Use blank_result_handling with a value of BlankResultHandling.REPEAT
            instead.
        :param blank_result_handling: Determine how to handle the result of a callback when the user provides a blank
            result.
        :param repeat_message: If blank_result_handling is REPEAT and a repeat_message is provided, then that message
            appears as toaster text when the user provides a blank result.
        :param cancel_message: If blank_result_handling is CANCEL and a cancel_message is provided, then that message
            appears as toaster text when the user provides a blank result.
        :return: The list of options that the user selected.
        """
        if not options:
            raise SapioException("No options provided.")
        options = list(options)
        if len(options) == 1 and shortcut_single_option:
            return [options[0]]

        # Send the request to the user.
        request = ListDialogRequest(title, multi_select, options,
                                    list(preselected_values) if preselected_values else None,
                                    width_in_pixels=self.width_pixels, width_percentage=self.width_percent)

        # Reverse compatibility: If require_selection is true and blank_result_handling is not set, then
        # set blank_result_handling to REPEAT.
        if require_selection is True and blank_result_handling == BlankResultHandling.DEFAULT:
            blank_result_handling = BlankResultHandling.REPEAT
        def not_blank_func(r: list[str]) -> bool:
            return bool(r)
        return self.__send_dialog_blank_results(request, self.callback.show_list_dialog, not_blank_func,
                                                blank_result_handling, repeat_message, cancel_message)

    # FR-47690: Updated with blank result handling behavior.
    def input_dialog(self,
                     title: str,
                     msg: str,
                     field: AbstractVeloxFieldDefinition,
                     *,
                     require_input = None,
                     blank_result_handling: BlankResultHandling = BlankResultHandling.DEFAULT,
                     repeat_message: str | None = "Please provide a value to continue.",
                     cancel_message: str | None = "No input was provided. Cancelling dialog.") -> FieldValue:
        """
        Create an input dialog where the user must input data for a singular field.

        :param title: The title of the dialog.
        :param msg: The message to display in the dialog. This can be formatted using HTML elements.
        :param field: The definition for a field that the user must provide input to.
        :param require_input: DEPRECATED. Use blank_result_handling with a value of BlankResultHandling.REPEAT
            instead.
        :param blank_result_handling: Determine how to handle the result of a callback when the user provides a blank
            result.
        :param repeat_message: If blank_result_handling is REPEAT and a repeat_message is provided, then that message
            appears as toaster text when the user provides a blank result.
        :param cancel_message: If blank_result_handling is CANCEL and a cancel_message is provided, then that message
            appears as toaster text when the user provides a blank result.
        :return: The response value from the user for the given field.
        """
        # Send the request to the user.
        request = InputDialogCriteria(title, msg, field,
                                      width_in_pixels=self.width_pixels, width_percentage=self.width_percent)

        # Reverse compatibility: If require_selection is true and blank_result_handling is not set, then
        # set blank_result_handling to REPEAT.
        handling = blank_result_handling
        if require_input is True and handling == BlankResultHandling.DEFAULT:
            handling = BlankResultHandling.REPEAT
        if handling == BlankResultHandling.DEFAULT or handling is None:
            handling = self._default_blank_result_handling

        while True:
            try:
                self.user.timeout_seconds = self.timeout_seconds
                # It's not possible to distinguish between the user cancelling this dialog and submitting the dialog
                # with no input if the ClientCallback show_input_dialog function is used, as both cases just return
                # None. Therefore, in order to be able to make that distinction, we need to call the endpoint without
                # ClientCallback and get the raw response object.
                raw_response = self.user.post('/clientcallback/showInputDialog', payload=request.to_json())
                # A response status code of 204 is what represents a cancelled dialog.
                if raw_response.status_code == 204:
                    raise SapioUserCancelledException()
                self.user.raise_for_status(raw_response)
                json_dct: dict | None = self.user.get_json_data_or_none(raw_response)
                response: FieldValue = json_dct['result'] if json_dct else None
            except ReadTimeout:
                raise SapioDialogTimeoutException()
            finally:
                self.user.timeout_seconds = self._original_timeout

            # String fields that the user didn't provide will return as an empty string instead of a None response.
            is_str: bool = isinstance(response, str)
            if (is_str and response) or (not is_str and response is not None):
                return response

            match handling:
                case BlankResultHandling.CANCEL:
                    # If the user provided no selection, throw an exception.
                    if cancel_message:
                        self.toaster_popup(cancel_message, popup_type=PopupType.Warning)
                    raise SapioUserCancelledException()
                case BlankResultHandling.REPEAT:
                    # If the user provided no selection, repeat the dialog.
                    # If a repeatMessage is provided, display it as a toaster popup.
                    if repeat_message:
                        self.toaster_popup(repeat_message, popup_type=PopupType.Warning)
                case BlankResultHandling.RETURN:
                    # If the user provided no selection, return the blank result.
                    return response

    def string_input_dialog(self,
                            title: str,
                            msg: str,
                            field_name: str,
                            default_value: str | None = None,
                            max_length: int | None = None,
                            editable: bool = True,
                            *,
                            require_input: bool = False,
                            repeat_message: str | None = "Please provide a value to continue.",
                            **kwargs) -> str:
        """
        Create an input dialog where the user must input data for a singular text field.

        :param title: The title of the dialog.
        :param msg: The message to display in the dialog. This can be formatted using HTML elements.
        :param field_name: The name and display name of the string field.
        :param default_value: The default value to place into the string field, if any.
        :param max_length: The max length of the string value. If not provided, uses the length of the default value.
            If neither this nor a default value are provided, defaults to 100 characters.
        :param editable: Whether the field is editable by the user.
        :param require_input: If true, the request will be re-sent if the user submits the dialog without making
            a selection.
        :param repeat_message: If require_input is true and a repeat_message is provided, then that message appears
            as toaster text if the dialog is repeated.
        :param kwargs: Any additional keyword arguments to pass to the field definition.
        :return: The string that the user input into the dialog.
        """
        # FR-47690: Deprecated in favor of suggesting the use of the FieldBuilder to customize an input_dialog's field.
        warnings.warn("Deprecated. Use the base input_dialog function and the FieldBuilder class to construct the "
                      "input field.", DeprecationWarning)
        if max_length is None:
            max_length = len(default_value) if default_value else 100
        field = VeloxStringFieldDefinition("Input", field_name, field_name, default_value=default_value,
                                           max_length=max_length, editable=editable, **kwargs)
        return self.input_dialog(title, msg, field,
                                 require_input=require_input, repeat_message=repeat_message)

    def integer_input_dialog(self,
                             title: str,
                             msg: str,
                             field_name: str,
                             default_value: int = None,
                             min_value: int = -10000,
                             max_value: int = 10000,
                             editable: bool = True,
                             *,
                             require_input: bool = False,
                             repeat_message: str | None = "Please provide a value to continue.",
                             **kwargs) -> int:
        """
        Create an input dialog where the user must input data for a singular integer field.

        :param title: The title of the dialog.
        :param msg: The message to display in the dialog. This can be formatted using HTML elements.
        :param field_name: The name and display name of the integer field.
        :param default_value: The default value to place into the integer field. If not provided, defaults to the 0 or
            the minimum value, whichever is higher.
        :param min_value: The minimum allowed value of the input.
        :param max_value: The maximum allowed value of the input.
        :param editable: Whether the field is editable by the user.
        :param require_input: If true, the request will be re-sent if the user submits the dialog without making
            a selection.
        :param repeat_message: If require_input is true and a repeat_message is provided, then that message appears
            as toaster text if the dialog is repeated.
        :param kwargs: Any additional keyword arguments to pass to the field definition.
        :return: The integer that the user input into the dialog.
        """
        # FR-47690: Deprecated in favor of suggesting the use of the FieldBuilder to customize an input_dialog's field.
        warnings.warn("Deprecated. Use the base input_dialog function and the FieldBuilder class to construct the "
                      "input field.", DeprecationWarning)
        if default_value is None:
            default_value = max(0, min_value)
        field = VeloxIntegerFieldDefinition("Input", field_name, field_name, default_value=default_value,
                                            min_value=min_value, max_value=max_value, editable=editable, **kwargs)
        return self.input_dialog(title, msg, field,
                                 require_input=require_input, repeat_message=repeat_message)

    def double_input_dialog(self,
                            title: str,
                            msg: str,
                            field_name: str,
                            default_value: float = None,
                            min_value: float = -10000000,
                            max_value: float = 100000000,
                            editable: bool = True,
                            *,
                            require_input: bool = False,
                            repeat_message: str | None = "Please provide a value to continue.",
                            **kwargs) -> float:
        """
        Create an input dialog where the user must input data for a singular double field.

        :param title: The title of the dialog.
        :param msg: The message to display in the dialog. This can be formatted using HTML elements.
        :param field_name: The name and display name of the double field.
        :param default_value: The default value to place into the double field. If not provided, defaults to the 0 or
            the minimum value, whichever is higher.
        :param min_value: The minimum allowed value of the input.
        :param max_value: The maximum allowed value of the input.
        :param editable: Whether the field is editable by the user.
        :param require_input: If true, the request will be re-sent if the user submits the dialog without making
            a selection.
        :param repeat_message: If require_input is true and a repeat_message is provided, then that message appears
            as toaster text if the dialog is repeated.
        :param kwargs: Any additional keyword arguments to pass to the field definition.
        :return: The float that the user input into the dialog.
        """
        # FR-47690: Deprecated in favor of suggesting the use of the FieldBuilder to customize an input_dialog's field.
        warnings.warn("Deprecated. Use the base input_dialog function and the FieldBuilder class to construct the "
                      "input field.", DeprecationWarning)
        if default_value is None:
            default_value = max(0., min_value)
        field = VeloxDoubleFieldDefinition("Input", field_name, field_name, default_value=default_value,
                                           min_value=min_value, max_value=max_value, editable=editable, **kwargs)
        return self.input_dialog(title, msg, field,
                                 require_input=require_input, repeat_message=repeat_message)

    def form_dialog(self,
                    title: str,
                    msg: str,
                    fields: Iterable[AbstractVeloxFieldDefinition],
                    values: FieldMap = None,
                    column_positions: dict[str, tuple[int, int]] = None,
                    *,
                    data_type: DataTypeIdentifier = "Default",
                    display_name: str | None = None,
                    plural_display_name: str | None = None) -> FieldMap:
        """
        Create a form dialog where the user may input data into the fields of the form. Requires that the caller
        provide the definitions of every field in the form.

        :param title: The title of the dialog.
        :param msg: The message to display at the top of the form. This can be formatted using HTML elements.
        :param fields: The definitions of the fields to display in the form. Fields will be displayed in the order they
            are provided in this list.
        :param values: Sets the default values of the fields. If a field name from the fields parameter is not
            provided in this dictionary, it will be initialized with its default value.
        :param column_positions: If a tuple is provided for a field name, alters that field's column position and column
            span. (Field order is still determined by the fields list.)
        :param data_type: The data type name for the temporary data type that will be created for this form.
        :param display_name: The display name for the temporary data type. If not provided, defaults to the data type
            name.
        :param plural_display_name: The plural display name for the temporary data type. If not provided, defaults to
            the display name + "s".
        :return: A dictionary mapping the data field names of the given field definitions to the response value from
            the user for that field.
        """
        # Build a temporary data type for the request.
        temp_dt = self.__temp_dt_from_field_defs(data_type, display_name, plural_display_name, fields, column_positions)

        # FR-47690: Set default values for fields that aren't present.
        if values is None:
            values = {}
        for field in fields:
            if field.data_field_name not in values:
                values[field.data_field_name] = field.default_value

        # Send the request to the user.
        request = FormEntryDialogRequest(title, msg, temp_dt, values,
                                         width_in_pixels=self.width_pixels, width_percentage=self.width_percent)
        response: FieldMap = self.__send_dialog(request, self.callback.show_form_entry_dialog)
        return response

    def record_form_dialog(self,
                           title: str,
                           msg: str,
                           fields: Iterable[FieldIdentifier | FieldFilterCriteria] | DataTypeLayoutIdentifier,
                           record: SapioRecord,
                           column_positions: dict[str, tuple[int, int]] | None = None,
                           editable=None,
                           *,
                           default_modifier: FieldModifier | None = None,
                           field_modifiers: dict[FieldIdentifier, FieldModifier] | None = None) -> FieldMap:
        """
        Create a form dialog where the user may input data into the fields of the form. The form is constructed from
        a given record.

        Makes webservice calls to get the data type definition and fields of the given record if they weren't
        previously cached.

        :param title: The title of the dialog.
        :param msg: The message to display in the dialog. This can be formatted using HTML elements.
        :param fields: The names of the fields to display as columns in the table. These names must match field names on
            the data type of the provided record. Provided field names may also be extension fields of the form
            [Extension Data Type Name].[Data Field Name]. This parameter may also be an identifier for a data type
            layout from the data type of the provided records. If None, then the layout assigned to the current user's
            group for this data type will be used.
        :param record: The record to display the values of.
        :param column_positions: If a tuple is provided for a field name, alters that field's column position and column
            span. (Field order is still determined by the fields list.) Has no effect if the fields parameter provides
            a data type layout.
        :param editable: DEPRECATED. Has no effect.
        :param default_modifier: A default field modifier that will be applied to the given fields. This can be used to
            make field definitions from the system behave differently than their system values. If this value is None,
            then a default field modifier is created that causes all specified fields to be both visible and not key
            fields. (Key fields get displayed first before any non-key fields in tables, so the key field setting is
            disabled by default in order to have the columns in the table respect the order of the fields as they are
            provided to this function.)
        :param field_modifiers: A mapping of data field name to field modifier for changes that should be applied to
            the matching field. If a data field name is not present in the provided dict, or the provided dictionary is
            None, then the default modifier will be used.
        :return: A dictionary mapping the data field names of the given field definitions to the response value from
            the user for that field.
        """
        # CR-47313: Replace the editable boolean with the default_modifier and field_modifiers parameters.
        if editable is not None:
            warnings.warn("The editable parameter is deprecated. Use the default_modifier and field_modifiers "
                          "parameters instead.", DeprecationWarning)

        # Get the data type name and field values from the provided record.
        data_type: str = AliasUtil.to_data_type_name(record)
        values: dict[str, FieldValue] = AliasUtil.to_field_map(record)

        # Set the default modifier to make all fields visible and not key if no default was provided.
        if default_modifier is None:
            default_modifier = FieldModifier(visible=True, key_field=False)
        # To make things simpler, treat null field modifiers as an empty dict.
        if field_modifiers is None:
            field_modifiers = {}
        else:
            field_modifiers: dict[str, FieldModifier] = AliasUtil.to_data_field_names_dict(field_modifiers)

        # Build a temporary data type for the request.
        if isinstance(fields, DataTypeLayoutIdentifier):
            temp_dt = self.__temp_dt_from_layout(data_type, fields, default_modifier, field_modifiers)
        else:
            temp_dt = self.__temp_dt_from_field_names(data_type, fields, column_positions,
                                                      default_modifier, field_modifiers)

        # Send the request to the user.
        request = FormEntryDialogRequest(title, msg, temp_dt, values,
                                         width_in_pixels=self.width_pixels, width_percentage=self.width_percent)
        response: FieldMap = self.__send_dialog(request, self.callback.show_form_entry_dialog)
        return response

    # FR-47314: Create record form and table dialogs for updating or creating records.
    def set_record_form_dialog(self,
                               title: str,
                               msg: str,
                               fields: Iterable[FieldIdentifier | FieldFilterCriteria] | DataTypeLayoutIdentifier,
                               record: SapioRecord,
                               column_positions: dict[str, tuple[int, int]] | None = None,
                               *,
                               default_modifier: FieldModifier | None = None,
                               field_modifiers: dict[FieldIdentifier, FieldModifier] | None = None) -> None:
        """
        Create a form dialog where the user may input data into the fields of the form. The form is constructed from
        a given record. After the user submits this dialog, the values that the user provided are used to update the
        provided record.

        Makes webservice calls to get the data type definition and fields of the given record if they weren't
        previously cached.

        :param title: The title of the dialog.
        :param msg: The message to display in the dialog. This can be formatted using HTML elements.
        :param fields: The names of the fields to display as columns in the table. These names must match field names on
            the data type of the provided record. Provided field names may also be extension fields of the form
            [Extension Data Type Name].[Data Field Name]. This parameter may also be an identifier for a data type
            layout from the data type of the provided records. If None, then the layout assigned to the current user's
            group for this data type will be used.
        :param record: The record to display and update the values of.
        :param column_positions: If a tuple is provided for a field name, alters that field's column position and column
            span. (Field order is still determined by the fields list.) Has no effect if the fields parameter provides
            a data type layout.
        :param default_modifier: A default field modifier that will be applied to the given fields. This can be used to
            make field definitions from the system behave differently than their system values. If this value is None,
            then a default field modifier is created that causes all specified fields to be both visible and not key
            fields. (Key fields get displayed first before any non-key fields in tables, so the key field setting is
            disabled by default in order to have the columns in the table respect the order of the fields as they are
            provided to this function.)
        :param field_modifiers: A mapping of data field name to field modifier for changes that should be applied to
            the matching field. If a data field name is not present in the provided dict, or the provided dictionary is
            None, then the default modifier will be used.
        """
        results: FieldMap = self.record_form_dialog(title, msg, fields, record, column_positions,
                                                    default_modifier=default_modifier, field_modifiers=field_modifiers)
        record.set_field_values(results)

    # CR-47491: Support providing a data type name string to receive PyRecordModels instead of requiring a WrapperType.
    def create_record_form_dialog(self,
                                  title: str,
                                  msg: str,
                                  fields: Iterable[FieldIdentifier | FieldFilterCriteria] | DataTypeLayoutIdentifier,
                                  wrapper_type: type[WrappedType] | str,
                                  column_positions: dict[str, tuple[int, int]] | None = None,
                                  *,
                                  default_modifier: FieldModifier | None = None,
                                  field_modifiers: dict[FieldIdentifier, FieldModifier] | None = None) \
            -> WrappedType | PyRecordModel:
        """
        Create a form dialog where the user may input data into the fields of the form. The form is constructed from
        a record that is created using the given record model wrapper. After the user submits this dialog, the values
        that the user provided are used to update the created record.

        Makes webservice calls to get the data type definition and fields of the given record if they weren't
        previously cached.

        :param title: The title of the dialog.
        :param msg: The message to display in the dialog. This can be formatted using HTML elements.
        :param fields: The names of the fields to display as columns in the table. These names must match field names on
            the data type of the provided wrapper. Provided field names may also be extension fields of the form
            [Extension Data Type Name].[Data Field Name]. This parameter may also be an identifier for a data type
            layout from the data type of the provided records. If None, then the layout assigned to the current user's
            group for this data type will be used. FieldFilterCriteria may also be provided in lieu of field names.
        :param wrapper_type: The record model wrapper or data type name of the record to be created and updated.
            If a data type name is provided, the returned record will be a PyRecordModel instead of a
            WrappedRecordModel.
        :param column_positions: If a tuple is provided for a field name, alters that field's column position and column
            span. (Field order is still determined by the fields list.) Has no effect if the fields parameter provides
            a data type layout.
        :param default_modifier: A default field modifier that will be applied to the given fields. This can be used to
            make field definitions from the system behave differently than their system values. If this value is None,
            then a default field modifier is created that causes all specified fields to be both visible and not key
            fields. (Key fields get displayed first before any non-key fields in tables, so the key field setting is
            disabled by default in order to have the columns in the table respect the order of the fields as they are
            provided to this function.)
        :param field_modifiers: A mapping of data field name to field modifier for changes that should be applied to
            the matching field. If a data field name is not present in the provided dict, or the provided dictionary is
            None, then the default modifier will be used.
        :return: The record model that was created and updated by the user.
        """
        record: WrappedType | PyRecordModel = self.rec_handler.add_model(wrapper_type)
        self.set_record_form_dialog(title, msg, fields, record, column_positions,
                                    default_modifier=default_modifier, field_modifiers=field_modifiers)
        return record

    def table_dialog(self,
                     title: str,
                     msg: str,
                     fields: Iterable[AbstractVeloxFieldDefinition],
                     values: Iterable[FieldMap] | int,
                     *,
                     data_type: DataTypeIdentifier = "Default",
                     display_name: str | None = None,
                     plural_display_name: str | None = None,
                     group_by: FieldIdentifier | None = None,
                     image_data: Iterable[bytes] | None = None) -> list[FieldMap]:
        """
        Create a table dialog where the user may input data into the fields of the table. Requires that the caller
        provide the definitions of every field in the table.

        :param title: The title of the dialog.
        :param msg: The message to display at the top of the form. This can be formatted using HTML elements.
        :param fields: The definitions of the fields to display as table columns. Fields will be displayed in the order
            they are provided in this list.
        :param values: The values to set for each row of the table. If an integer is provided, it is treated as the
            number of rows to create in the table, with each row using the default values of the field definitions.
        :param group_by: If provided, the created table dialog will be grouped by the field with this name by default.
            The user may remove this grouping if they want to.
        :param image_data: The bytes to the images that should be displayed in the rows of the table. Each element in
            the image data list corresponds to the element at the same index in the values list.
        :param data_type: The data type name for the temporary data type that will be created for this table.
        :param display_name: The display name for the temporary data type. If not provided, defaults to the data type
            name.
        :param plural_display_name: The plural display name for the temporary data type. If not provided, defaults to
            the display name + "s".
        :return: A list of dictionaries mapping the data field names of the given field definitions to the response
            value from the user for that field for each row.
        """
        # FR-47690: Accept an integer as the values parameter to create a table with that many rows.
        if isinstance(values, int):
            values: list[dict[str, Any]] = [{} for _ in range(values)]
        if not values:
            raise SapioException("No values provided.")

        # FR-47690: Set default values for fields that aren't present.
        for row in values:
            for field in fields:
                if field.data_field_name not in row:
                    row[field.data_field_name] = field.default_value

        # Convert the group_by parameter to a field name.
        if group_by is not None:
            group_by: str = AliasUtil.to_data_field_name(group_by)

        # Build a temporary data type for the request.
        temp_dt = self.__temp_dt_from_field_defs(data_type, display_name, plural_display_name, fields, None)
        # PR-47376: Mark record_image_assignable as true if image data is provided.
        temp_dt.record_image_assignable = bool(image_data)

        # Send the request to the user.
        request = TableEntryDialogRequest(title, msg, temp_dt, list(values),
                                          record_image_data_list=image_data, group_by_field=group_by,
                                          width_in_pixels=self.width_pixels, width_percentage=self.width_percent)
        response: list[FieldMap] = self.__send_dialog(request, self.callback.show_table_entry_dialog)
        return response

    def record_table_dialog(self,
                            title: str,
                            msg: str,
                            fields: Iterable[FieldIdentifier | FieldFilterCriteria] | DataTypeLayoutIdentifier,
                            records: Iterable[SapioRecord],
                            editable=None,
                            *,
                            default_modifier: FieldModifier | None = None,
                            field_modifiers: dict[FieldIdentifier, FieldModifier] | None = None,
                            group_by: FieldIdentifier | None = None,
                            image_data: Iterable[bytes] | None = None,
                            index_field: str | None = None) -> list[FieldMap]:
        """
        Create a table dialog where the user may input data into the fields of the table. The table is constructed from
        a given list of records of a singular type.

        Makes webservice calls to get the data type definition and fields of the given records if they weren't
        previously cached.

        :param title: The title of the dialog.
        :param msg: The message to display in the dialog. This can be formatted using HTML elements.
        :param fields: The names of the fields to display as columns in the table. These names must match field names on
            the data type of the provided record. Provided field names may also be extension fields of the form
            [Extension Data Type Name].[Data Field Name]. This parameter may also be an identifier for a data type
            layout from the data type of the provided records. If None, then the layout assigned to the current user's
            group for this data type will be used.
        :param records: The records to display as rows in the table.
        :param editable: DEPRECATED. Has no effect.
        :param default_modifier: A default field modifier that will be applied to the given fields. This can be used to
            make field definitions from the system behave differently than their system values. If this value is None,
            then a default field modifier is created that causes all specified fields to be both visible and not key
            fields. (Key fields get displayed first before any non-key fields in tables, so the key field setting is
            disabled by default in order to have the columns in the table respect the order of the fields as they are
            provided to this function.)
        :param field_modifiers: A mapping of data field name to field modifier for changes that should be applied to
            the matching field. If a data field name is not present in the provided dict, or the provided dictionary is
            None, then the default modifier will be used.
        :param group_by: If provided, the created table dialog will be grouped by the field with this name by default.
            The user may remove this grouping if they want to.
        :param image_data: The bytes to the images that should be displayed in the rows of the table. Each element in
            the image data list corresponds to the element at the same index in the records list.
        :param index_field: If provided, the returned field maps will contain a field with this name that is equal to
            the record ID of the record at the same index in the records list. This can be used to map the results
            back to the original records. This is used instead of using a RecordId field, as the RecordId field has
            special behavior in the system that can cause issues if the given records are uncommitted record models
            with negative record IDs, meaning we don't want to have a RecordId field in the field maps provided to the
            system.
        :return: A list of dictionaries mapping the data field names of the given field definitions to the response
            value from the user for that field for each row.
        """
        # CR-47313: Replace the editable boolean with the default_modifier and field_modifiers parameters.
        if editable is not None:
            warnings.warn("The editable parameter is deprecated. Use the default_modifier and field_modifiers "
                          "parameters instead.", DeprecationWarning)
        # Get the data type name and field values from the provided records.
        if not records:
            raise SapioException("No records provided.")
        data_type: str = AliasUtil.to_singular_data_type_name(records)
        if index_field is not None:
            field_map_list: list[FieldMap] = self.__get_indexed_field_maps(records, index_field)
        else:
            field_map_list: list[FieldMap] = AliasUtil.to_field_map_list(records)

        # Convert the group_by parameter to a field name.
        if group_by is not None:
            group_by: str = AliasUtil.to_data_field_name(group_by)

        # Set the default modifier to make all fields visible and not key if no default was provided.
        if default_modifier is None:
            default_modifier = FieldModifier(visible=True, key_field=False)
        # To make things simpler, treat null field modifiers as an empty dict.
        if field_modifiers is None:
            field_modifiers = {}
        else:
            field_modifiers: dict[str, FieldModifier] = AliasUtil.to_data_field_names_dict(field_modifiers)

        # Build a temporary data type for the request.
        if isinstance(fields, DataTypeLayoutIdentifier):
            temp_dt = self.__temp_dt_from_layout(data_type, fields, default_modifier, field_modifiers)
        else:
            temp_dt = self.__temp_dt_from_field_names(data_type, fields, None, default_modifier, field_modifiers)
        temp_dt.record_image_assignable = bool(image_data)

        # Send the request to the user.
        request = TableEntryDialogRequest(title, msg, temp_dt, field_map_list,
                                          record_image_data_list=image_data, group_by_field=group_by,
                                          width_in_pixels=self.width_pixels, width_percentage=self.width_percent)
        response: list[FieldMap] = self.__send_dialog(request, self.callback.show_table_entry_dialog)
        return response

    # FR-47314: Create record form and table dialogs for updating or creating records.
    def set_record_table_dialog(self,
                                title: str,
                                msg: str,
                                fields: Iterable[FieldValue] | DataTypeLayoutIdentifier,
                                records: Iterable[SapioRecord],
                                *,
                                default_modifier: FieldModifier | None = None,
                                field_modifiers: dict[FieldIdentifier, FieldModifier] | None = None,
                                group_by: FieldIdentifier | None = None,
                                image_data: Iterable[bytes] | None = None):
        """
        Create a table dialog where the user may input data into the fields of the table. The table is constructed from
        a given list of records of a singular type. After the user submits this dialog, the values that the user
        provided are used to update the provided records.

        Makes webservice calls to get the data type definition and fields of the given records if they weren't
        previously cached.

        :param title: The title of the dialog.
        :param msg: The message to display in the dialog. This can be formatted using HTML elements.
        :param fields: The names of the fields to display as columns in the table. These names must match field names on
            the data type of the provided record. Provided field names may also be extension fields of the form
            [Extension Data Type Name].[Data Field Name]. This parameter may also be an identifier for a data type
            layout from the data type of the provided records. If None, then the layout assigned to the current user's
            group for this data type will be used.
        :param records: The records to display as rows in the table and update the values of.
        :param default_modifier: A default field modifier that will be applied to the given fields. This can be used to
            make field definitions from the system behave differently than their system values. If this value is None,
            then a default field modifier is created that causes all specified fields to be both visible and not key
            fields. (Key fields get displayed first before any non-key fields in tables, so the key field setting is
            disabled by default in order to have the columns in the table respect the order of the fields as they are
            provided to this function.)
        :param field_modifiers: A mapping of data field name to field modifier for changes that should be applied to
            the matching field. If a data field name is not present in the provided dict, or the provided dictionary is
            None, then the default modifier will be used.
        :param group_by: If provided, the created table dialog will be grouped by the field with this name by default.
            The user may remove this grouping if they want to.
        :param image_data: The bytes to the images that should be displayed in the rows of the table. Each element in
            the image data list corresponds to the element at the same index in the records list.
        """
        # Index the records with a field name that is the current time in milliseconds. This is done to avoid
        # collisions with any existing field names.
        index_field: str = f"_{TimeUtil.now_in_millis()}"
        results: list[FieldMap] = self.record_table_dialog(title, msg, fields, records,
                                                           default_modifier=default_modifier,
                                                           field_modifiers=field_modifiers,
                                                           group_by=group_by, image_data=image_data,
                                                           index_field=index_field)
        records_by_id: dict[int, SapioRecord] = self.rec_handler.map_by_id(records)
        for result in results:
            index: int = result.pop(index_field)
            records_by_id[index].set_field_values(result)

    # FR-47690: Updated with blank result handling behavior.
    def create_record_table_dialog(self,
                                   title: str,
                                   msg: str,
                                   fields: Iterable[FieldValue] | DataTypeLayoutIdentifier,
                                   wrapper_type: type[WrappedType] | str,
                                   count: int | tuple[int, int],
                                   *,
                                   default_modifier: FieldModifier | None = None,
                                   field_modifiers: dict[FieldIdentifier, FieldModifier] | None = None,
                                   group_by: FieldIdentifier | None = None,
                                   image_data: Iterable[bytes] | None = None,
                                   require_input = None,
                                   blank_result_handling: BlankResultHandling = BlankResultHandling.DEFAULT,
                                   repeat_message: str | None = "Please provide a value to continue.",
                                   cancel_message: str | None = "No value was provided. Cancelling dialog.") \
            -> list[WrappedType] | list[PyRecordModel]:
        """
        Create a table dialog where the user may input data into the fields of the table. The table is constructed from
        a list of records that are created using the given record model wrapper. After the user submits this dialog,
        the values that the user provided are used to update the created records.

        Makes webservice calls to get the data type definition and fields of the given records if they weren't
        previously cached.

        :param title: The title of the dialog.
        :param msg: The message to display in the dialog. This can be formatted using HTML elements.
        :param fields: The names of the fields to display as columns in the table. These names must match field names on
            the data type of the provided wrapper. Provided field names may also be extension fields of the form
            [Extension Data Type Name].[Data Field Name]. This parameter may also be an identifier for a data type
            layout from the data type of the provided records. If None, then the layout assigned to the current user's
            group for this data type will be used.
        :param wrapper_type: The record model wrapper or data type name of the records to be created and updated. If
            a data type name is provided, the returned records will be PyRecordModels instead of WrappedRecordModels.
        :param count: The number of records to create. If provided as a tuple of two integers, the user will first be
            prompted to select an integer between the two values in the tuple.
        :param default_modifier: A default field modifier that will be applied to the given fields. This can be used to
            make field definitions from the system behave differently than their system values. If this value is None,
            then a default field modifier is created that causes all specified fields to be both visible and not key
            fields. (Key fields get displayed first before any non-key fields in tables, so the key field setting is
            disabled by default in order to have the columns in the table respect the order of the fields as they are
            provided to this function.)
        :param field_modifiers: A mapping of data field name to field modifier for changes that should be applied to
            the matching field. If a data field name is not present in the provided dict, or the provided dictionary is
            None, then the default modifier will be used.
        :param group_by: If provided, the created table dialog will be grouped by the field with this name by default.
            The user may remove this grouping if they want to.
        :param image_data: The bytes to the images that should be displayed in the rows of the table. Each element in
            the image data list corresponds to the element at the same index in the records list.
        :param require_input: DEPRECATED. Use blank_result_handling with a value of BlankResultHandling.REPEAT
            instead.
        :param blank_result_handling: Determine how to handle the result of a callback when the user provides a blank
            result.
        :param repeat_message: If blank_result_handling is REPEAT and a repeat_message is provided, then that message
            appears as toaster text when the user provides a blank result.
        :param cancel_message: If blank_result_handling is CANCEL and a cancel_message is provided, then that message
            appears as toaster text when the user provides a blank result.
        :return: A list of the newly created records.
        """
        count: int = self.__prompt_for_count(count, wrapper_type, require_input, blank_result_handling, repeat_message,
                                             cancel_message)
        if count <= 0:
            return []
        records: list[WrappedType] | list[PyRecordModel] = self.rec_handler.add_models(wrapper_type, count)
        self.set_record_table_dialog(title, msg, fields, records,
                                     default_modifier=default_modifier, field_modifiers=field_modifiers,
                                     group_by=group_by, image_data=image_data)
        return records

    # FR-47314: Create record dialogs that adapt to become a form or table based on the size of the input.
    def record_adaptive_dialog(self,
                               title: str,
                               msg: str,
                               fields: Iterable[FieldIdentifier | FieldFilterCriteria] | DataTypeLayoutIdentifier,
                               records: Collection[SapioRecord],
                               *,
                               default_modifier: FieldModifier | None = None,
                               field_modifiers: dict[FieldIdentifier, FieldModifier] | None = None,
                               column_positions: dict[str, tuple[int, int]] | None = None,
                               group_by: FieldIdentifier | None = None,
                               image_data: Iterable[bytes] | None = None,
                               index_field: str | None = None) -> list[FieldMap]:
        """
        Create a dialog where the user may input data into the specified fields. The dialog is constructed from
        a given list of records of a singular type.

        The dialog created will adapt to the number of records. If there is only one record then a form dialog will be
        created. Otherwise, a table dialog is created.

        Makes webservice calls to get the data type definition and fields of the given records if they weren't
        previously cached.

        :param title: The title of the dialog.
        :param msg: The message to display in the dialog. This can be formatted using HTML elements.
        :param fields: The names of the fields to display in the dialog. These names must match field names on
            the data type of the provided record. Provided field names may also be extension fields of the form
            [Extension Data Type Name].[Data Field Name]. This parameter may also be an identifier for a data type
            layout from the data type of the provided records. If None, then the layout assigned to the current user's
            group for this data type will be used.
        :param records: The records to display in the dialog.
        :param default_modifier: A default field modifier that will be applied to the given fields. This can be used to
            make field definitions from the system behave differently than their system values. If this value is None,
            then a default field modifier is created that causes all specified fields to be both visible and not key
            fields. (Key fields get displayed first before any non-key fields in tables, so the key field setting is
            disabled by default in order to have the columns in the table respect the order of the fields as they are
            provided to this function.)
        :param field_modifiers: A mapping of data field name to field modifier for changes that should be applied to
            the matching field. If a data field name is not present in the provided dict, or the provided dictionary is
            None, then the default modifier will be used.
        :param column_positions: If a tuple is provided for a field name, alters that field's column position and column
            span. (Field order is still determined by the fields list.) Has no effect if the fields parameter provides
            a data type layout. Only used if the adaptive dialog becomes a form.
        :param group_by: If provided, the created table dialog will be grouped by the field with this name by default.
            The user may remove this grouping if they want to. Only used if the adaptive dialog becomes a table.
        :param image_data: The bytes to the images that should be displayed in the rows of the table. Each element in
            the image data list corresponds to the element at the same index in the records list. Only used if the
            adaptive dialog becomes a table.
        :param index_field: If provided, the returned field maps will contain a field with this name that is equal to
            the record ID of the record at the same index in the records list. This can be used to map the results
            back to the original records. This is used instead of using a RecordId field, as the RecordId field has
            special behavior in the system that can cause issues if the given records are uncommitted record models
            with negative record IDs, meaning we don't want to have a RecordId field in the field maps provided to the
            system. Only used if the adaptive dialog becomes a table.
        :return: A list of dictionaries mapping the data field names of the given field definitions to the response
            value from the user for that field for each row. Even if a form was displayed, the field values will still
            be returned in a list.
        """
        count: int = len(records)
        if not count:
            raise SapioException("No records provided.")
        if count == 1:
            return [self.record_form_dialog(title, msg, fields, list(records)[0], column_positions,
                                            default_modifier=default_modifier, field_modifiers=field_modifiers)]
        return self.record_table_dialog(title, msg, fields, records,
                                        default_modifier=default_modifier, field_modifiers=field_modifiers,
                                        group_by=group_by, image_data=image_data, index_field=index_field)

    def set_record_adaptive_dialog(self,
                                   title: str,
                                   msg: str,
                                   fields: Iterable[FieldIdentifier | FieldFilterCriteria] | DataTypeLayoutIdentifier,
                                   records: Collection[SapioRecord],
                                   *,
                                   default_modifier: FieldModifier | None = None,
                                   field_modifiers: dict[FieldIdentifier, FieldModifier] | None = None,
                                   column_positions: dict[str, tuple[int, int]] | None = None,
                                   group_by: FieldIdentifier | None = None,
                                   image_data: Iterable[bytes] | None = None) -> None:
        """
        Create a dialog where the user may input data into the fields of the dialog. The dialog is constructed from
        a given list of records of a singular type. After the user submits this dialog, the values that the user
        provided are used to update the provided records.

        The dialog created will adapt to the number of records. If there is only one record then a form dialog will be
        created. Otherwise, a table dialog is created.

        Makes webservice calls to get the data type definition and fields of the given records if they weren't
        previously cached.

        :param title: The title of the dialog.
        :param msg: The message to display in the dialog. This can be formatted using HTML elements.
        :param fields: The names of the fields to display in the dialog. These names must match field names on
            the data type of the provided record. Provided field names may also be extension fields of the form
            [Extension Data Type Name].[Data Field Name]. This parameter may also be an identifier for a data type
            layout from the data type of the provided records. If None, then the layout assigned to the current user's
            group for this data type will be used.
        :param records: The records to display in the dialog and update the values of.
        :param default_modifier: A default field modifier that will be applied to the given fields. This can be used to
            make field definitions from the system behave differently than their system values. If this value is None,
            then a default field modifier is created that causes all specified fields to be both visible and not key
            fields. (Key fields get displayed first before any non-key fields in tables, so the key field setting is
            disabled by default in order to have the columns in the table respect the order of the fields as they are
            provided to this function.)
        :param field_modifiers: A mapping of data field name to field modifier for changes that should be applied to
            the matching field. If a data field name is not present in the provided dict, or the provided dictionary is
            None, then the default modifier will be used.
        :param column_positions: If a tuple is provided for a field name, alters that field's column position and column
            span. (Field order is still determined by the fields list.) Has no effect if the fields parameter provides
            a data type layout. Only used if the adaptive dialog becomes a form.
        :param group_by: If provided, the created table dialog will be grouped by the field with this name by default.
            The user may remove this grouping if they want to. Only used if the adaptive dialog becomes a table.
        :param image_data: The bytes to the images that should be displayed in the rows of the table. Each element in
            the image data list corresponds to the element at the same index in the records list. Only used if the
            adaptive dialog becomes a table.
        """
        count: int = len(records)
        if not count:
            raise SapioException("No records provided.")
        if count == 1:
            self.set_record_form_dialog(title, msg, fields, list(records)[0], column_positions,
                                        default_modifier=default_modifier, field_modifiers=field_modifiers)
        else:
            self.set_record_table_dialog(title, msg, fields, records,
                                         default_modifier=default_modifier, field_modifiers=field_modifiers,
                                         group_by=group_by, image_data=image_data)

    # FR-47690: Updated with blank result handling behavior.
    def create_record_adaptive_dialog(self,
                                      title: str,
                                      msg: str,
                                      fields: Iterable[FieldValue] | DataTypeLayoutIdentifier,
                                      wrapper_type: type[WrappedType] | str,
                                      count: int | tuple[int, int],
                                      *,
                                      default_modifier: FieldModifier | None = None,
                                      field_modifiers: dict[FieldIdentifier, FieldModifier] | None = None,
                                      column_positions: dict[str, tuple[int, int]] | None = None,
                                      group_by: FieldIdentifier | None = None,
                                      image_data: Iterable[bytes] | None = None,
                                      require_input = None,
                                      blank_result_handling: BlankResultHandling = BlankResultHandling.DEFAULT,
                                      repeat_message: str | None = "Please provide a value to continue.",
                                      cancel_message: str | None = "No value was provided. Cancelling dialog.") \
            -> list[WrappedType]:
        """
        Create a dialog where the user may input data into the specified fields. The dialog is constructed from
        a list of records that are created using the given record model wrapper. After the user submits this dialog,
        the values that the user provided are used to update the created records.

        The dialog created will adapt to the number of records. If there is only one record then a form dialog will be
        created. Otherwise, a table dialog is created.

        Makes webservice calls to get the data type definition and fields of the given records if they weren't
        previously cached.

        :param title: The title of the dialog.
        :param msg: The message to display in the dialog. This can be formatted using HTML elements.
        :param fields: The names of the fields to display in the dialog. These names must match field names on
            the data type of the provided wrapper. Provided field names may also be extension fields of the form
            [Extension Data Type Name].[Data Field Name]. This parameter may also be an identifier for a data type
            layout from the data type of the provided records. If None, then the layout assigned to the current user's
            group for this data type will be used.
        :param wrapper_type: The record model wrapper or data type name of the records to be created and updated. If
            a data type name is provided, the returned records will be PyRecordModels instead of WrappedRecordModels.
        :param count: The number of records to create. If provided as a tuple of two integers, the user will first be
            prompted to select an integer between the two values in the tuple.
        :param default_modifier: A default field modifier that will be applied to the given fields. This can be used to
            make field definitions from the system behave differently than their system values. If this value is None,
            then a default field modifier is created that causes all specified fields to be both visible and not key
            fields. (Key fields get displayed first before any non-key fields in tables, so the key field setting is
            disabled by default in order to have the columns in the table respect the order of the fields as they are
            provided to this function.)
        :param field_modifiers: A mapping of data field name to field modifier for changes that should be applied to
            the matching field. If a data field name is not present in the provided dict, or the provided dictionary is
            None, then the default modifier will be used.
        :param column_positions: If a tuple is provided for a field name, alters that field's column position and column
            span. (Field order is still determined by the fields list.) Has no effect if the fields parameter provides
            a data type layout. Only used if the adaptive dialog becomes a form.
        :param group_by: If provided, the created table dialog will be grouped by the field with this name by default.
            The user may remove this grouping if they want to. Only used if the adaptive dialog becomes a table.
        :param image_data: The bytes to the images that should be displayed in the rows of the table. Each element in
            the image data list corresponds to the element at the same index in the records list. Only used if the
            adaptive dialog becomes a table.
        :param require_input: DEPRECATED. Use blank_result_handling with a value of BlankResultHandling.REPEAT
            instead.
        :param blank_result_handling: Determine how to handle the result of a callback when the user provides a blank
            result.
        :param repeat_message: If blank_result_handling is REPEAT and a repeat_message is provided, then that message
            appears as toaster text when the user provides a blank result.
        :param cancel_message: If blank_result_handling is CANCEL and a cancel_message is provided, then that message
            appears as toaster text when the user provides a blank result.
        :return: A list of the newly created records. Even if a form was displayed, the created record will still be
            returned in a list.
        """
        count: int = self.__prompt_for_count(count, wrapper_type, require_input, blank_result_handling, repeat_message,
                                             cancel_message)
        if count <= 0:
            return []
        if count == 1:
            return [self.create_record_form_dialog(title, msg, fields, wrapper_type, column_positions,
                                                   default_modifier=default_modifier, field_modifiers=field_modifiers)]
        return self.create_record_table_dialog(title, msg, fields, wrapper_type, count,
                                               default_modifier=default_modifier, field_modifiers=field_modifiers,
                                               group_by=group_by, image_data=image_data)

    # FR-47690: Add group_by and image_data parameters.
    def multi_type_table_dialog(self,
                                title: str,
                                msg: str,
                                fields: Iterable[tuple[DataTypeIdentifier, FieldIdentifier] | AbstractVeloxFieldDefinition],
                                row_contents: Iterable[Iterable[SapioRecord | FieldMap]],
                                *,
                                default_modifier: FieldModifier | None = None,
                                field_modifiers: dict[FieldIdentifier, FieldModifier] | None = None,
                                data_type: DataTypeIdentifier = "Default",
                                display_name: str | None = None,
                                plural_display_name: str | None = None,
                                group_by: FieldIdentifier | None = None,
                                image_data: list[bytes] | None = None) -> list[FieldMap]:
        """
        Create a table dialog where the user may input data into the fields of the table. The table is constructed from
        a given list of records of multiple data types or field maps. Provided field names must match with field names
        from the data type definition of the given records. The fields that are displayed will have their default value
        be that of the fields on the given records or field maps.

        Makes webservice calls to get the data type field definitions of the given records if they weren't
        previously cached.

        :param title: The title of the dialog.
        :param msg: The message to display in the dialog. This can be formatted using HTML elements.
        :param fields: A list of objects representing the fields in the table. This could either be a two-element tuple
            where the first element is a data type name and the second is a field name, or it could be a field
            definition. If it is the former, a query will be made to find the field definition matching tht data type.
            The data type names of the fields must match the data type names of the records in the row contents.
            See the description of row_contents for what to do if you want to construct a field that pulls from a field
            map.
            If two fields share the same field name, an exception will be thrown. This is even true in the case where
            the data type name of the fields is different. If you wish to display two fields from two data types with
            the same name, then you must provide a FieldModifier for at least one of the fields where prepend_data_type
            is True in order to make that field's name unique again. Note that if you do this for a field, the mapping
            of record to field name will use the unedited field name, but the return results of this function will
            use the edited field name in the results dictionary for a row.
        :param row_contents: A list where each element is another list representing the records or a field map that will
            be used to populate the columns of the table. If the data type of a given record doesn't match any of the
            data type names of the given fields, then it will not be used.
            This list can contain up to one field map, which are fields not tied to a record. This is so that you can
            create abstract field definition not tied to a specific record in the system. If you want to define an
            abstract field that pulls from the field map in the row contents, then you must set the data type name to
            Default.
            If a record of a given data type appears more than once in one of the inner-lists of the row contents, or
            there is more than one field map, then an exception will be thrown, as there is no way of distinguishing
            which record should be used for a field, and not all fields could have their values combined across multiple
            records.
            The row contents may have an inner-list which is missing a record of a data type that matches one of the
            fields. In this case, the field value for that row under that column will be null.
            The inner-list does not need to be sorted in any way, as this function will map the inner-list contents to
            fields as necessary.
            The inner-list may contain null elements; these will simply be discarded by this function.
        :param default_modifier: A default field modifier that will be applied to the given fields. This can be used to
            make field definitions from the system behave differently than their system values. If this value is None,
            then a default field modifier is created that causes all specified fields to be both visible and not key
            fields. (Key fields get displayed first before any non-key fields in tables, so the key field setting is
            disabled by default in order to have the columns in the table respect the order of the fields as they are
            provided to this function.)
        :param field_modifiers: A mapping of data field name to field modifier for changes that should be applied to
            the matching field. If a data field name is not present in the provided dict, or the provided dictionary is
            None, then the default modifier will be used.
        :param data_type: The data type name for the temporary data type that will be created for this table.
        :param display_name: The display name for the temporary data type. If not provided, defaults to the data type
            name.
        :param plural_display_name: The plural display name for the temporary data type. If not provided, defaults to
            the display name + "s".
        :param group_by: If provided, the created table dialog will be grouped by the field with this name by default.
            The user may remove this grouping if they want to.
        :param image_data: The bytes to the images that should be displayed in the rows of the table. Each element in
            the image data list corresponds to the element at the same index in the values list.
        :return: A list of dictionaries mapping the data field names of the given field definitions to the response
            value from the user for that field for each row.
        """
        if not row_contents:
            raise SapioException("No values provided.")

        # Set the default modifier to make all fields visible and not key if no default was provided.
        if default_modifier is None:
            default_modifier = FieldModifier(visible=True, key_field=False)
        # To make things simpler, treat null field modifiers as an empty dict.
        if field_modifiers is None:
            field_modifiers = {}
        else:
            field_modifiers: dict[str, FieldModifier] = AliasUtil.to_data_field_names_dict(field_modifiers)

        # Construct the final fields list from the possible field objects.
        final_fields: list[AbstractVeloxFieldDefinition] = []
        # Keep track of whether any given field name appears more than once, as two fields could have the same
        # field name but different data types. In this case, the user should provide a field modifier or field
        # definition that changes one of the field names.
        raw_field_names: set[str] = set()
        field_names: set[str] = set()
        for field in fields:
            # Find the field definition for this field object.
            if isinstance(field, tuple):
                dt: str = AliasUtil.to_data_type_name(field[0])
                fld: str = AliasUtil.to_data_field_name(field[1])
                field_def: AbstractVeloxFieldDefinition = self.__get_field_def(dt, fld)
            elif isinstance(field, AbstractVeloxFieldDefinition):
                field_def: AbstractVeloxFieldDefinition = field
            else:
                raise SapioException("Unrecognized field object.")

            # Locate the modifier for this field and store the modified field.
            name: str = field_def.data_field_name
            # PR-47378: Account for the scenario where two fields share the same field name and we need to determine
            # which field modifier to apply to each field name.
            duplicate: bool = name in raw_field_names
            if duplicate and name in field_modifiers:
                raise SapioException(f"The field name \"{name}\" appears more than once in the given fields while also "
                                     f"having a field_modifiers dictionary key of the same name. This function is "
                                     f"unable to distinguish which field the field modifier should be applied to. "
                                     f"Update your field_modifiers dictionary to provide keys in the form "
                                     f"[Data Type Name].[Data Field Name] for this field name.")
            raw_field_names.add(name)
            full_name = f"{field_def.data_type_name}.{name}"
            if full_name in field_modifiers:
                modifier: FieldModifier = field_modifiers.get(full_name)
            else:
                modifier: FieldModifier = field_modifiers.get(name, default_modifier)
            field_def: AbstractVeloxFieldDefinition = modifier.modify_field(field_def)
            final_fields.append(field_def)

            # Verify that this field name isn't a duplicate.
            # The field name may have changed due to the modifier.
            name: str = field_def.data_field_name
            if name in field_names:
                raise SapioException(f"The field name \"{name}\" appears more than once in the given fields. "
                                     f"If you have provided two fields with the same name but different data types, "
                                     f"consider providing a FieldModifier where prepend_data_type is true for "
                                     f"this field so that the field names will become different.")
            field_names.add(name)

        # Get the values for each row.
        # FR-47690: Updated this for loop to better match the Java implementation.
        values: list[dict[str, FieldValue]] = []
        for row in row_contents:
            # The final values for this row:
            row_values: dict[str, FieldValue] = {}

            # Map the records for this row by their data type. If a field map is provided, save it separately to
            # the temp_values dict.
            row_records: dict[str, SapioRecord] = {}
            temp_values: FieldMap = {}
            for rec in row:
                # Toss out null elements.
                if rec is None:
                    continue
                # Map records to their data type name. Map field maps to Default.
                dt: str = "Default" if isinstance(rec, dict) else AliasUtil.to_data_type_name(rec)
                if dt == "Default":
                    temp_values.update(rec)
                else:
                    # Warn if the same data type name appears more than once.
                    if dt in row_records:
                        raise SapioException(f"The data type \"{dt}\" appears more than once in the given row contents.")
                    row_records[dt] = rec

            # Get the field values from the above records.
            for field in final_fields:
                value: Any | None = None

                # Find the object that corresponds to this field given its data type name.
                dt: str = field.data_type_name
                fd: str = field.data_field_name
                if dt == "Default":
                    # If the field map is provided, get the value from it.
                    # FR-47690: If a value is not provided, then use the default value of the field definition.
                    if fd in temp_values:
                        value = temp_values.get(fd)
                    else:
                        value = field.default_value
                elif dt in row_records:
                    record: SapioRecord = row_records[dt]
                    # If the record is not null, get the value from the record.
                    if record is not None:
                        value = record.get_field_value(fd)

                # Find out if this field had its data type prepended to it. If this is the case, then we need to find
                # the true data field name before retrieving the value from the field map.
                name: str = field.data_field_name
                if field_modifiers.get(name, default_modifier).prepend_data_type is True:
                    name = name.split(".")[1]

                # Set the value for this particular field.
                row_values[name] = value
            values.append(row_values)

        # Build a temporary data type for the request.
        temp_dt = self.__temp_dt_from_field_defs(data_type, display_name, plural_display_name, final_fields, None)
        temp_dt.record_image_assignable = bool(image_data)

        # Convert the group_by parameter to a field name.
        if group_by is not None:
            group_by: str = AliasUtil.to_data_field_name(group_by)

        # Send the request to the user.
        request = TableEntryDialogRequest(title, msg, temp_dt, values,
                                          record_image_data_list=image_data, group_by_field=group_by,
                                          width_in_pixels=self.width_pixels, width_percentage=self.width_percent)
        response: list[FieldMap] = self.__send_dialog(request, self.callback.show_table_entry_dialog)
        return response

    def record_view_dialog(self,
                           title: str,
                           record: SapioRecord,
                           layout: DataTypeLayoutIdentifier = None,
                           minimized: bool = False,
                           access_level: FormAccessLevel | None = None,
                           plugin_path_list: Iterable[str] | None = None) -> None:
        """
        Create an IDV dialog for the given record. This IDV may use an existing layout already defined in the system,
        and can be created to allow the user to edit the field in the IDV, or to be read-only for the user to review.
        This returns no value, but if the user cancels the dialog instead of clicking the "OK" button, then a
        SapioUserCancelledException will be thrown.

        :param title: The title of the dialog.
        :param record: The record to be displayed in the dialog.
        :param layout: The layout that will be used to display the record in the dialog. If this is not
            provided, then the layout assigned to the current user's group for this data type will be used. If this
            is provided as a string, then a webservice call will be made to retrieve the data type layout matching
            the name of that string for the given record's data type.
        :param minimized: If true, then the dialog will only show key fields and required fields initially
            until the expand button is clicked (similar to when using the built-in add buttons to create new records).
        :param access_level: The level of access that the user will have on this field entry dialog. This attribute
            determines whether the user will be able to edit the fields in the dialog, use core features, or use toolbar
            buttons. If no value is provided, then the form will be editable.
        :param plugin_path_list: A white list of plugins that should be displayed in the dialog. This white list
            includes plugins that would be displayed on sub-tables/components in the layout.
        """
        # Get the data record and data type layout from the provided parameters.
        record: DataRecord = AliasUtil.to_data_record(record)
        layout: DataTypeLayout | None = self.__to_layout(AliasUtil.to_data_type_name(record), layout)

        # Send the request to the user.
        request = DataRecordDialogRequest(title, record, layout, minimized, access_level, plugin_path_list,
                                          width_in_pixels=self.width_pixels, width_percentage=self.width_percent)
        response: bool = self.__send_dialog(request, self.callback.data_record_form_view_dialog)
        # The __handle_dialog_request function only throws a cancelled exception if the response is None, but in
        # this case we also want to throw if the response is False.
        if not response:
            raise SapioUserCancelledException()

    # CR-47326: Allow the selection dialog functions to preselect rows/records in the table.
    # FR-47690: Added shortcut_single_option parameter. Updated with blank result handling behavior.
    def selection_dialog(self,
                         msg: str,
                         fields: Iterable[AbstractVeloxFieldDefinition],
                         values: Iterable[FieldMap],
                         multi_select: bool = True,
                         preselected_rows: Iterable[FieldMap | RecordIdentifier] | None = None,
                         *,
                         data_type: DataTypeIdentifier = "Default",
                         display_name: str | None = None,
                         plural_display_name: str | None = None,
                         image_data: Iterable[bytes] | None = None,
                         shortcut_single_option: bool = True,
                         require_selection = None,
                         blank_result_handling: BlankResultHandling = BlankResultHandling.DEFAULT,
                         repeat_message: str | None = "Please provide a selection to continue.",
                         cancel_message: str | None = "No selection was made. Cancelling dialog.") -> list[FieldMap]:
        """
        Create a selection dialog for a list of field maps for the user to choose from. Requires that the caller
        provide the definitions of every field in the table.
        The title of a selection dialog will always be "Select [plural display name]".

        :param msg: The message to display in the dialog. This can be formatted using HTML elements.
        :param fields: The definitions of the fields to display as table columns. Fields will be displayed in the order
            they are provided in this list.
        :param values: The values to set for each row of the table.
        :param multi_select: Whether the user is able to select multiple rows from the list.
        :param preselected_rows: The rows that should be selected in the dialog when it is initially
            displayed to the user. The user will be allowed to deselect these records if they so wish. If preselected
            rows are provided, the dialog will automatically allow multi-selection of records. Note that in order for
            preselected rows to be identified, they MUST contain a "RecordId" field with a numeric value that is unique
            across all provided values.
        :param data_type: The data type name for the temporary data type that will be created for this table.
        :param display_name: The display name for the temporary data type. If not provided, defaults to the data type
            name.
        :param plural_display_name: The plural display name for the temporary data type. If not provided, defaults to
            the display name + "s".
        :param image_data: The bytes to the images that should be displayed in the rows of the table. Each element in
            the image data list corresponds to the element at the same index in the values list.
        :param shortcut_single_option: If true, then if the list contains only one option, the dialog will not be shown
            and the single option will be returned immediately.
        :param require_selection: DEPRECATED. Use blank_result_handling with a value of BlankResultHandling.REPEAT
            instead.
        :param blank_result_handling: Determine how to handle the result of a callback when the user provides a blank
            result.
        :param repeat_message: If blank_result_handling is REPEAT and a repeat_message is provided, then that message
            appears as toaster text when the user provides a blank result.
        :param cancel_message: If blank_result_handling is CANCEL and a cancel_message is provided, then that message
            appears as toaster text when the user provides a blank result.
        :return: A list of field maps corresponding to the chosen input field maps.
        """
        if not values:
            raise SapioException("No values provided.")
        values = list(values)
        if len(values) == 1 and shortcut_single_option:
            return [values[0]]

        if preselected_rows:
            # Confirm that the provided field maps are validly configured to allow the use of preselected rows.
            encountered_ids: set[int] = set()
            for row in values:
                if "RecordId" not in row or row["RecordId"] is None:
                    raise SapioException("When using preselected_rows, the provided field map values must have a "
                                         "RecordId field.")
                row_id: int = row["RecordId"]
                if row_id in encountered_ids:
                    raise SapioException(f"Not all RecordId values in the provided field maps are unique. "
                                         f"{row_id} was encountered more than once.")
                encountered_ids.add(row_id)

            # Convert the preselected rows to a list of integers.
            new_list: list[int] = []
            for value in preselected_rows:
                if isinstance(value, dict):
                    new_list.append(value["RecordId"])
                else:
                    new_list.append(AliasUtil.to_record_id(value))
            preselected_rows: list[int] = new_list

            # Add a RecordId definition to the fields if one is not already present. This is necessary for the
            # pre-selected records parameter to function.
            fields = list(fields)
            if "RecordId" not in [x.data_field_name for x in fields]:
                builder = FieldBuilder(data_type)
                fields.append(builder.long_field("RecordId", abstract_info=AnyFieldInfo(visible=False)))

        # Build a temporary data type for the request.
        temp_dt = self.__temp_dt_from_field_defs(data_type, display_name, plural_display_name, fields, None)
        temp_dt.record_image_assignable = bool(image_data)

        # Send the request to the user.
        request = TempTableSelectionRequest(temp_dt, msg, list(values), image_data, preselected_rows, multi_select)

        # Reverse compatibility: If require_selection is true and blank_result_handling is not set, then
        # set blank_result_handling to REPEAT.
        if require_selection is True and blank_result_handling == BlankResultHandling.DEFAULT:
            blank_result_handling = BlankResultHandling.REPEAT
        def not_blank_func(r: list[FieldMap]) -> bool:
            return bool(r)
        return self.__send_dialog_blank_results(request, self.callback.show_temp_table_selection_dialog, not_blank_func,
                                                blank_result_handling, repeat_message, cancel_message)

    # FR-47690: Added shortcut_single_option parameter. Updated with blank result handling behavior.
    def record_selection_dialog(self,
                                msg: str,
                                fields: Iterable[FieldIdentifier | FieldFilterCriteria] | DataTypeLayoutIdentifier,
                                records: Iterable[SapioRecord],
                                multi_select: bool = True,
                                preselected_records: Iterable[RecordIdentifier] | None = None,
                                *,
                                image_data: Iterable[bytes] | None = None,
                                shortcut_single_option: bool = True,
                                require_selection = None,
                                blank_result_handling: BlankResultHandling = BlankResultHandling.DEFAULT,
                                repeat_message: str | None = "Please provide a selection to continue.",
                                cancel_message: str | None = "No selection was made. Cancelling dialog.") \
            -> list[SapioRecord]:
        """
        Create a record selection dialog for a list of records for the user to choose from. Provided field names must
        match fields on the definition of the data type of the given records.
        The title of a selection dialog will always be "Select [plural display name]".

        Makes webservice calls to get the data type definition and fields of the given records if they weren't
        previously cached.

        :param msg: The message to display in the dialog. This can be formatted using HTML elements.
        :param fields: The names of the fields to display as columns in the table. Fields will be displayed in the order
            they are provided in this list. This parameter may also be an identifier for a data type layout from the
            data type of the provided records. If None, then the layout assigned to the current user's group for this
            data type will be used.
        :param records: The records to display as rows in the table.
        :param multi_select: Whether the user is able to select multiple records from the list.
        :param preselected_records: The records that should be selected in the dialog when it is initially
            displayed to the user. The user will be allowed to deselect these records if they so wish. If preselected
            record IDs are provided, the dialog will automatically allow multi-selection of records.
        :param image_data: The bytes to the images that should be displayed in the rows of the table. Each element in
            the image data list corresponds to the element at the same index in the records list.
        :param shortcut_single_option: If true, then if the list contains only one option, the dialog will not be shown
            and the single option will be returned immediately.
        :param require_selection: DEPRECATED. Use blank_result_handling with a value of BlankResultHandling.REPEAT
            instead.
        :param blank_result_handling: Determine how to handle the result of a callback when the user provides a blank
            result.
        :param repeat_message: If blank_result_handling is REPEAT and a repeat_message is provided, then that message
            appears as toaster text when the user provides a blank result.
        :param cancel_message: If blank_result_handling is CANCEL and a cancel_message is provided, then that message
            appears as toaster text when the user provides a blank result.
        :return: A list of the selected records.
        """
        # Get the data type name and field values from the provided records.
        if not records:
            raise SapioException("No records provided.")
        records = list(records)
        if len(records) == 1 and shortcut_single_option:
            return [records[0]]
        data_type: str = AliasUtil.to_singular_data_type_name(records)
        field_map_list: list[FieldMap] = AliasUtil.to_field_map_list(records, include_record_id=True)

        # Key fields display their columns in order before all non-key fields.
        # Unmark key fields so that the column order is respected exactly as the caller provides it.
        # Also make everything visible, because presumably the caller give a field name because they want it to be seen.
        modifier = FieldModifier(visible=True, key_field=False)

        # Build a temporary data type for the request.
        if isinstance(fields, DataTypeLayoutIdentifier):
            temp_dt = self.__temp_dt_from_layout(data_type, fields, modifier, {})
        else:
            temp_dt = self.__temp_dt_from_field_names(data_type, fields, None, modifier, {})
        temp_dt.record_image_assignable = bool(image_data)

        if preselected_records:
            # Convert the preselected records to a list of integers.
            preselected_records: list[int] = AliasUtil.to_record_ids(preselected_records)
            # Add a RecordId definition to the fields if one is not already present. This is necessary for the
            # pre-selected records parameter to function.
            if "RecordId" not in [x.data_field_name for x in temp_dt.get_field_def_list()]:
                builder = FieldBuilder(data_type)
                temp_dt.set_field_definition(builder.long_field("RecordId", abstract_info=AnyFieldInfo(visible=False)))

        # Send the request to the user.
        request = TempTableSelectionRequest(temp_dt, msg, field_map_list, image_data, preselected_records, multi_select)

        # Reverse compatibility: If require_selection is true and blank_result_handling is not set, then
        # set blank_result_handling to REPEAT.
        if require_selection is True and blank_result_handling == BlankResultHandling.DEFAULT:
            blank_result_handling = BlankResultHandling.REPEAT
        def not_blank_func(r: list[FieldMap]) -> bool:
            return bool(r)
        response: list[FieldMap] = self.__send_dialog_blank_results(request,
                                                                    self.callback.show_temp_table_selection_dialog,
                                                                    not_blank_func, blank_result_handling,
                                                                    repeat_message, cancel_message)

        # Map the field maps in the response back to the record they come from, returning the chosen record instead of
        # the chosen field map.
        records_by_id: dict[int, SapioRecord] = RecordHandler.map_by_id(records)
        ret_list: list[SapioRecord] = []
        for field_map in response:
            ret_list.append(records_by_id.get(field_map.get("RecordId")))
        return ret_list

    # CR-47377: Add allow_creation and default_creation_number to cover new parameters of this request type from 24.12.
    # FR-47690: Updated with blank result handling behavior.
    def input_selection_dialog(self,
                               wrapper_type: type[WrappedType] | str,
                               msg: str,
                               multi_select: bool = True,
                               only_key_fields: bool = False,
                               search_types: Iterable[SearchType] | None = None,
                               scan_criteria: ScanToSelectCriteria | None = None,
                               custom_search: CustomReport | CustomReportCriteria | str | None = None,
                               preselected_records: Iterable[RecordIdentifier] | None = None,
                               record_blacklist: Iterable[RecordIdentifier] | None = None,
                               record_whitelist: Iterable[RecordIdentifier] | None = None,
                               allow_creation: bool = False,
                               default_creation_number: int = 1,
                               *,
                               require_selection = None,
                               blank_result_handling: BlankResultHandling = BlankResultHandling.DEFAULT,
                               repeat_message: str | None = "Please provide a selection to continue.",
                               cancel_message: str | None = "No selection was made. Cancelling dialog.") \
            -> list[WrappedType] | list[PyRecordModel]:
        """
        Display a table of records that exist in the system matching the given data type and filter criteria and have
        the user select one or more records from the table.
        The title of a selection dialog will always be "Select [plural display name]".

        :param wrapper_type: The record model wrapper or data type name for the records to display in the dialog. If
            a data type name is provided, the returned records will be PyRecordModels instead of WrappedRecordModels.
        :param msg: The message to show near the top of the dialog, below the title. This can be used to
            instruct the user on what is desired from the dialog. This can be formatted using HTML elements.
        :param multi_select: Whether the user may select multiple items at once in this dialog.
        :param only_key_fields: Whether only key fields of the selected data type should be displayed in the table
            of data in the dialog. If false, allows all possible fields to be displayed as columns in the table.
        :param search_types: The type of search that will be made available to the user through the dialog. This
            includes quick searching a list of records, allowing the user to create an advanced search, or allowing
            the user to browse the record tree.
        :param scan_criteria: If present, the dialog will show a scan-to-select editor in the quick search
            section that allows for picking a field to match on and scanning a value to more easily select records.
            If quick search is not an allowable search type from the search_types parameter, then this
            parameter will have no effect.
        :param custom_search: An alternate search to be used in the quick search section to pre-filter the displayed
            records. If not provided or if the search is cross data type or not a report of the type specified, all
            records of the type will be shown (which is the normal quick search results behavior).
            If quick search is not an allowable search type from the search_types parameter, then this
            parameter will have no effect.
            If the search is provided as a string, then a webservice call will be made to retrieve the custom report
            criteria for the system report/predefined search in the system matching that name.
        :param preselected_records: The records that should be selected in the dialog when it is initially
            displayed to the user. The user will be allowed to deselect these records if they so wish. If preselected
            record IDs are provided, the dialog will automatically allow multi-selection of records.
        :param record_blacklist: A list of records that should not be seen as possible options in the dialog.
        :param record_whitelist: A list of records that will be seen as possible options in the dialog. Records not in
            this whitelist will not be displayed if a whitelist is provided.
        :param allow_creation: Whether the "Create New" button will be visible to the user to create new records of the
            given type. The user must also have group access to be able to create the records.
        :param default_creation_number: If the user clicks the "Create New" button, then this is the value that will
            appear by default in the dialog that prompts the user to select how many new records to create. The value
            must be between 1 and 500, with values outside of that range being clamped to it. If this value is greater
            than 1, then multi-selection must be true. The data type definition of the records being created must have
            "Prompt for Number to Add" set to true in order to allow the user to select how many records to create, as
            otherwise user will only ever be able to create one record at a time.
        :param require_selection: DEPRECATED. Use blank_result_handling with a value of BlankResultHandling.REPEAT
            instead.
        :param blank_result_handling: Determine how to handle the result of a callback when the user provides a blank
            result.
        :param repeat_message: If blank_result_handling is REPEAT and a repeat_message is provided, then that message
            appears as toaster text when the user provides a blank result.
        :param cancel_message: If blank_result_handling is CANCEL and a cancel_message is provided, then that message
            appears as toaster text when the user provides a blank result.
        :return: A list of the records selected by the user in the dialog, wrapped as record models using the provided
            wrapper.
        """
        data_type: str = AliasUtil.to_data_type_name(wrapper_type)

        # Reduce the provided lists of records down to lists of record IDs.
        if preselected_records:
            preselected_records: list[int] = AliasUtil.to_record_ids(preselected_records)
        if record_blacklist:
            record_blacklist: list[int] = AliasUtil.to_record_ids(record_blacklist)
        if record_whitelist:
            record_whitelist: list[int] = AliasUtil.to_record_ids(record_whitelist)

        # If CustomReportCriteria was provided, it must be wrapped as a CustomReport.
        if isinstance(custom_search, CustomReportCriteria):
            custom_search: CustomReport = CustomReport(False, [], custom_search)
        # If a string was provided, locate the report criteria for the predefined search in the system matching this
        # name.
        if isinstance(custom_search, str):
            custom_search: CustomReport = CustomReportUtil.get_system_report_criteria(self.user, custom_search)

        # Send the request to the user.
        request = InputSelectionRequest(data_type, msg, search_types, only_key_fields, record_blacklist,
                                        record_whitelist, preselected_records, custom_search, scan_criteria,
                                        multi_select, allow_creation, default_creation_number)

        # Reverse compatibility: If require_selection is true and blank_result_handling is not set, then
        # set blank_result_handling to REPEAT.
        if require_selection is True and blank_result_handling == BlankResultHandling.DEFAULT:
            blank_result_handling = BlankResultHandling.REPEAT
        def not_blank_func(r: list[DataRecord]) -> bool:
            return bool(r)
        return self.__send_dialog_blank_results(request, self.callback.show_input_selection_dialog, not_blank_func,
                                                blank_result_handling, repeat_message, cancel_message)

    # FR-47690: Deprecated the require_authentication parameter.
    # noinspection PyUnusedLocal
    def esign_dialog(self,
                     title: str,
                     msg: str,
                     show_comment: bool = True,
                     additional_fields: Iterable[AbstractVeloxFieldDefinition] | None = None,
                     *,
                     require_authentication = None) -> ESigningResponsePojo:
        """
        Create an e-sign dialog for the user to interact with.

        :param title: The title of the dialog.
        :param msg: The message to display in the dialog. This can be formatted using HTML elements.
        :param show_comment: Whether the "Meaning of Action" field should appear in the e-sign dialog. If true, the
            user is required to provide an action.
        :param additional_fields: Field definitions for additional fields to display in the dialog, for if there is
            other information you wish to gather from the user alongside the e-sign.
        :param require_authentication: DEPRECATED. Authentication is always required when using this function.
        :return: An e-sign response object containing information about the e-sign attempt.
        """
        # Construct a temporary data type if any additional fields are provided.
        temp_dt = None
        if additional_fields:
            builder = FormBuilder()
            for field in additional_fields:
                builder.add_field(field)
            temp_dt = builder.get_temporary_data_type()

        # Send the request to the user.
        request = ESigningRequestPojo(title, msg, show_comment, temp_dt,
                                      width_in_pixels=self.width_pixels, width_percentage=self.width_percent)
        while True:
            response: ESigningResponsePojo = self.__send_dialog(request, self.callback.show_esign_dialog)
            if response.authenticated:
                break
            # This matches the OOB behavior.
            self.toaster_popup("Incorrect username/password", popup_type=PopupType.Error)
            if not response.same_user:
                self.toaster_popup(f"This action requires the credentials of {self.user.username}",
                                   popup_type=PopupType.Error)
        return response

    def request_file(self, title: str, exts: Iterable[str] | None = None,
                     show_image_editor: bool = False, show_camera_button: bool = False) -> tuple[str, bytes]:
        """
        Request a single file from the user.

        :param title: The title of the dialog.
        :param exts: The allowable file extensions of the uploaded file. If blank, any file can be uploaded. Throws an
            exception if an incorrect file extension is provided.
        :param show_image_editor: Whether the user will see an image editor when image is uploaded in this file prompt.
        :param show_camera_button: Whether the user will be able to use camera to take a picture as an upload request,
            rather than selecting an existing file.
        :return: The file name and bytes of the uploaded file.
        """
        # If no extensions were provided, use an empty list for the extensions instead.
        if exts is None:
            exts: list[str] = []

        # Use a data sink to consume the data. In order to get both the file name and the file data,
        # I've recreated a part of sink.upload_single_file_to_webhook_server() in this function, as
        # calling that sink function throws out the file name of the uploaded file.
        sink = InMemoryRecordDataSink(self.user)
        with sink as io_obj:
            def do_consume(chunk: bytes) -> None:
                return sink.consume_data(chunk, io_obj)

            # Send the request to the user.
            request = FilePromptRequest(title, show_image_editor, ",".join(exts), show_camera_button)
            file_path: str = self.__send_dialog(request, self.callback.show_file_dialog, data_sink=do_consume)

        # Verify that each of the file given matches the expected extension(s).
        self.__verify_file(file_path, sink.data, exts)
        return file_path, sink.data

    def request_files(self, title: str, exts: Iterable[str] | None = None,
                      show_image_editor: bool = False, show_camera_button: bool = False) -> dict[str, bytes]:
        """
        Request multiple files from the user.

        :param title: The title of the dialog.
        :param exts: The allowable file extensions of the uploaded files. If blank, any file can be uploaded. Throws an
            exception if an incorrect file extension is provided.
        :param show_image_editor: Whether the user will see an image editor when image is uploaded in this file prompt.
        :param show_camera_button: Whether the user will be able to use camera to take a picture as an upload request,
            rather than selecting an existing file.
        :return: A dictionary of file name to file bytes for each file the user uploaded.
        """
        # If no extensions were provided, use an empty list for the extensions instead.
        if exts is None:
            exts: list[str] = []

        # Send the request to the user.
        request = MultiFilePromptRequest(title, show_image_editor, ",".join(exts), show_camera_button)
        file_paths: list[str] = self.__send_dialog(request, self.callback.show_multi_file_dialog)

        # Verify that each of the files given match the expected extension(s).
        ret_dict: dict[str, bytes] = {}
        for file_path in file_paths:
            sink = InMemoryRecordDataSink(self.user)
            sink.consume_client_callback_file_path_data(file_path)
            self.__verify_file(file_path, sink.data, exts)
            ret_dict.update({file_path: sink.data})

        return ret_dict

    @staticmethod
    def __verify_file(file_path: str, file_bytes: bytes, allowed_extensions: Iterable[str]) -> None:
        """
        Verify that the provided file was read (i.e. the file path and file bytes aren't None or empty) and that it
        has the correct file extension. Raises a user error exception if something about the file is incorrect.

        :param file_path: The name of the file to verify.
        :param file_bytes: The bytes of the file to verify.
        :param allowed_extensions: The file extensions that the file path is allowed to have.
        """
        if file_path is None or len(file_path) == 0 or file_bytes is None or len(file_bytes) == 0:
            raise SapioUserErrorException("Empty file provided or file unable to be read.")
        if allowed_extensions:
            matches: bool = False
            for ext in allowed_extensions:
                # FR-47690: Changed to a case-insensitive match.
                if file_path.casefold().endswith("." + ext.lstrip(".").casefold()):
                    matches = True
                    break
            if matches is False:
                raise SapioUserErrorException("Unsupported file type. Expecting the following extension(s): "
                                              + (",".join(allowed_extensions)))

    def write_file(self, file_name: str, file_data: str | bytes) -> None:
        """
        Send a file to the user for them to download.

        :param file_name: The name of the file.
        :param file_data: The data of the file, provided as either a string or as a bytes array.
        """
        with io.BytesIO(file_data.encode() if isinstance(file_data, str) else file_data) as data:
            self.callback.send_file(file_name, False, data)

    def write_zip_file(self, zip_name: str, files: dict[str, str | bytes]) -> None:
        """
        Send a collection of files to the user in a zip file.

        :param zip_name: The name of the zip file.
        :param files: A dictionary of the files to add to the zip file.
        """
        self.write_file(zip_name, FileUtil.zip_files(files))

    @staticmethod
    def __get_indexed_field_maps(records: Iterable[SapioRecord], index_field: str) -> list[FieldMap]:
        """
        For dialogs that accept multiple records, we may want to be able to match the returned results back to the
        records that they're for. In this case, we need to add an index to each record so that we can match them back
        to the original records. We can't use the RecordId field, as new record models have negative record IDs that
        cause the callback dialogs to bug out if the RecordId field is present and negative.

        :param records: The records to return indexed field maps of.
        :param index_field: The name of the field to use as the index. Make sure that this field doesn't exist on the
            records, as then it will overwrite the existing value.
        :return: A list of field maps for the records, with an index field added to each. The value of the index on
            each field map is the record's record ID (even if it's a record model with a negative ID).
        """
        ret_val: list[FieldMap] = []
        for record in records:
            field_map: FieldMap = AliasUtil.to_field_map(record)
            field_map[index_field] = AliasUtil.to_record_id(record)
            ret_val.append(field_map)
        return ret_val

    @staticmethod
    def __temp_dt_from_field_defs(data_type: DataTypeIdentifier, display_name: str | None,
                                  plural_display_name: str | None, fields: Iterable[AbstractVeloxFieldDefinition],
                                  column_positions: dict[str, tuple[int, int]] | None) -> TemporaryDataType:
        """
        Construct a Temporary Data Type definition from a provided list of field definitions for use in a callback.
        """
        if not fields:
            raise SapioException("No fields provided to create a temporary data type.")
        # Get the data type name as a string from the parameters, and set the display name and plural display name if
        # they haven't been set.
        data_type: str = AliasUtil.to_data_type_name(data_type)
        if display_name is None:
            display_name = data_type
        if plural_display_name is None:
            plural_display_name = display_name + "s"

        # Key fields display their columns in order before all non-key fields.
        # Unmark key fields so that the column order is respected exactly as the caller provides it.
        modifier = FieldModifier(key_field=False)

        builder = FormBuilder(data_type, display_name, plural_display_name)
        for field_def in fields:
            # Determine the column and span for each field in the form.
            # If this isn't a form dialog, then adding the column and span to the FormBuilder has no effect.
            field_name = field_def.data_field_name
            column: int = 0
            span: int = 4
            if column_positions and field_name in column_positions:
                position = column_positions.get(field_name)
                column = position[0]
                span = position[1]
            # Apply the field modifier to each key field in the form.
            if field_def.key_field:
                field_def = modifier.modify_field(field_def)
            builder.add_field(field_def, column, span)
        return builder.get_temporary_data_type()

    def __temp_dt_from_field_names(self, data_type: str, fields: Iterable[FieldIdentifier | FieldFilterCriteria],
                                   column_positions: dict[str, tuple[int, int]] | None,
                                   default_modifier: FieldModifier, field_modifiers: dict[str, FieldModifier]) \
            -> TemporaryDataType:
        """
        Construct a Temporary Data Type definition from a given data type name and list of field identifiers for that
        data type. Queries for the data type's definition to get the display name and plural display name, as well as
        the data field definitions of the data type to map the given field identifiers to field definitions. If an
        extension field is provided, then the extension data type's fields will be queried. Finally, applies the
        provided field modifiers to the field definitions to alter them from their system-set values
        """
        # Get the definition of the data type to construct the form builder with the proper values.
        type_def: DataTypeDefinition = self.dt_cache.get_data_type(data_type)
        builder = FormBuilder(data_type, type_def.display_name, type_def.plural_display_name)

        # Determine if any FieldFilterCriteria were provided. If so, remove them from the fields list so that it
        # contains only field identifiers.
        fields = list(fields)
        filter_criteria: list[FieldFilterCriteria] = [x for x in fields if isinstance(x, FieldFilterCriteria)]
        for criteria in filter_criteria:
            fields.remove(criteria)

        # Build the form using only those fields that are desired.
        field_names: list[str] = AliasUtil.to_data_field_names(fields)
        for field_name in field_names:
            field_def: AbstractVeloxFieldDefinition = self.__get_field_def(data_type, field_name)

            # Determine the column and span for each field in the form.
            # If this isn't a form dialog, then adding the column and span to the FormBuilder has no effect.
            column: int = 0
            span: int = 4
            if column_positions and field_name in column_positions:
                position = column_positions.get(field_name)
                column = position[0]
                span = position[1]

            # Apply the field modifiers to each field in the form.
            modifier: FieldModifier = field_modifiers.get(field_name, default_modifier)
            builder.add_field(modifier.modify_field(field_def), column, span)

        # Now determine if any fields match the provided filter criteria.
        all_fields: dict[str, AbstractVeloxFieldDefinition] = self.dt_cache.get_fields_for_type(data_type)
        current_column: int = 0
        for criteria in filter_criteria:
            for field_name, field_def in all_fields.items():
                # Don't add fields that have already been added.
                if field_name in field_names or not criteria.field_matches(field_def):
                    continue
                field_names.append(field_name)

                # The caller can't know what fields are present, so the column positions dictionary can't be used.
                # Still come up with spans for each field to minimize wasted space.
                # Give boolean fields a span of 1 and HTML or multi-line string fields a span of 4.
                # Give all other fields a span of 2.
                if field_def.data_field_type == FieldType.BOOLEAN:
                    span = 1
                elif (isinstance(field_def, VeloxStringFieldDefinition)
                      and (field_def.html_editor or field_def.num_lines > 1)):
                    span = 4
                else:
                    span = 2
                # Wrap the column position if necessary.
                if current_column + span > 4:
                    current_column = 0

                # Apply the field modifiers to each field in the form.
                modifier: FieldModifier = field_modifiers.get(field_name, default_modifier)
                builder.add_field(modifier.modify_field(field_def), current_column, span)
                current_column += span

        return builder.get_temporary_data_type()

    # CR-47309: Allow layouts to be provided in place of field names for record dialogs.
    def __temp_dt_from_layout(self, data_type: str, layout: DataTypeLayoutIdentifier,
                              default_modifier: FieldModifier, field_modifiers: dict[str, FieldModifier]) \
            -> TemporaryDataType:
        """
        Construct a Temporary Data Type definition from a given data type name and layout identifier.
        Applies the provided field modifiers to the field definitions from the layout's temp data type to alter them
        from their system-set values
        """
        # Get the temp data type for the provided layout.
        temp_dt = self.dt_man.get_temporary_data_type(data_type, self.__to_layout_name(layout))
        # Apply the field modifiers to each field in the layout.
        for field_def in temp_dt.get_field_def_list():
            field_name: str = field_def.data_field_name
            modifier: FieldModifier = field_modifiers.get(field_name, default_modifier)
            temp_dt.set_field_definition(modifier.modify_field(field_def))
        return temp_dt

    # FR-47690: Updated with blank result handling behavior.
    def __prompt_for_count(self, count: tuple[int, int] | int, wrapper_type: type[WrappedType] | str,
                           require_input: bool, blank_result_handling: BlankResultHandling, repeat_message: str,
                           cancel_message: str) -> int:
        """
        Given a count value, if it is a tuple representing an allowable range of values for a number of records to
        create, prompt the user to input the exact count to use. If the count is already a single integer, simply
        return that.
        """
        if isinstance(count, tuple):
            if hasattr(wrapper_type, "PLURAL_DISPLAY_NAME"):
                plural: str = wrapper_type.PLURAL_DISPLAY_NAME
            else:
                plural: str = self.dt_cache.get_plural_display_name(AliasUtil.to_data_type_name(wrapper_type))
            min_val, max_val = count
            msg: str = f"How many {plural} should be created? ({min_val} to {max_val})"
            count_field: VeloxIntegerFieldDefinition = FieldBuilder().int_field("Count", min_value=min_val,
                                                                                max_value=max_val,
                                                                                default_value=min_val)
            count: int = self.input_dialog(f"Create {plural}", msg, count_field,
                                           require_input=require_input, blank_result_handling=blank_result_handling,
                                           repeat_message=repeat_message, cancel_message=cancel_message)
            if count is None:
                count = 0
        return count

    def __to_layout(self, data_type: str, layout: DataTypeLayoutIdentifier) -> DataTypeLayout | None:
        """
        Convert a data type layout identifier to a data type layout.
        """
        if layout is None:
            return None
        if isinstance(layout, DataTypeLayout):
            return layout
        layout_name: str = layout
        layout: DataTypeLayout | None = self.__get_data_type_layout(data_type, layout_name)
        # If a name was provided then the caller expects that name to exist. Throw an exception if it doesn't.
        if not layout:
            raise SapioException(f"The data type \"{data_type}\" does not have a layout by the name "
                                 f"\"{layout_name}\" in the system.")
        return layout

    @staticmethod
    def __to_layout_name(layout: DataTypeLayoutIdentifier) -> str | None:
        """
        Convert a data type layout identifier to a layout name.
        """
        if layout is None:
            return None
        if isinstance(layout, DataTypeLayout):
            return layout.layout_name
        return layout

    def __get_data_type_layout(self, data_type: str, layout: str) -> DataTypeLayout:
        """
        Get a data type layout from the cache given its name.
        """
        if data_type in self.__layouts:
            return self.__layouts[data_type].get(layout)
        self.__layouts[data_type] = {x.layout_name: x for x in self.dt_man.get_data_type_layout_list(data_type)}
        return self.__layouts[data_type].get(layout)

    def __get_field_def(self, data_type: str, field_name: str) -> AbstractVeloxFieldDefinition:
        """
        Given a data type name and a data field name, return the field definition for that field on that data type.
        If the field name is an extension field, properly gets the field definition from the extension data type instead
        of the given data type and updates the extension field def to have its data field name match the given field
        name.
        """
        # CR-47311: Support displaying extension fields with single-data-type record dialogs.
        if "." in field_name:
            # If there is a period in the given field name, then this is an extension field.
            ext_dt, ext_fld = field_name.split(".")
            # Locate the extension data type's field definitions.
            field_def = self.dt_cache.get_fields_for_type(ext_dt).get(ext_fld)
            if field_def is None:
                raise SapioException(f"No field of name \"{ext_fld}\" in field definitions of extension type \"{ext_dt}\"")
            # Copy the field definition and set its field name to match the extension field name so that the record
            # field maps properly map the field value to the field definition.
            field_def = copy(field_def)
            field_def._data_field_name = field_name
        else:
            # If there is no period in the given field name, then this is a field on the base data type.
            field_def = self.dt_cache.get_fields_for_type(data_type).get(field_name)
            if field_def is None:
                raise SapioException(f"No field of name \"{field_name}\" in field definitions of type \"{data_type}\"")
        return field_def

    def __handle_timeout(self, func: Callable, request: Any, **kwargs) -> Any:
        """
        Send a client callback request to the user that creates a dialog.

        This function handles updating the user object's request timeout to match the request timeout of this
        CallbackUtil for the duration of the dialog.
        If the dialog times out then a SapioDialogTimeoutException is thrown.

        :param request: The client callback request to send to the user.
        :param func: The ClientCallback function to call with the given request as input.
        :param kwargs: Additional keywords for the provided function call.
        :return: The response from the client callback.
        """
        try:
            self.user.timeout_seconds = self.timeout_seconds
            response: Any | None = func(request, **kwargs)
        except ReadTimeout:
            raise SapioDialogTimeoutException()
        finally:
            self.user.timeout_seconds = self._original_timeout
        return response

    def __send_dialog(self, request: Any, func: Callable, **kwargs) -> Any:
        """
        Send a client callback request to the user that creates a dialog.

        This function handles updating the user object's request timeout to match the request timeout of this
        CallbackUtil for the duration of the dialog.
        If the dialog times out then a SapioDialogTimeoutException is thrown.
        If the user cancels the dialog then a SapioUserCancelledException is thrown.

        :param request: The client callback request to send to the user.
        :param func: The ClientCallback function to call with the given request as input.
        :param kwargs: Additional keywords for the provided function call.
        :return: The response from the client callback, if one was received.
        """
        response: Any | None = self.__handle_timeout(func, request, **kwargs)
        if response is None:
            raise SapioUserCancelledException()
        return response

    def __send_dialog_blank_results(self, request: Any, func: Callable, not_blank_func: Callable,
                                    handling: BlankResultHandling,
                                    repeat_message: str | None, cancel_message: str | None, **kwargs):
        """
        Send a client callback request to the user that creates a dialog.

        This function handles updating the user object's request timeout to match the request timeout of this
        CallbackUtil for the duration of the dialog.
        If the dialog times out then a SapioDialogTimeoutException is thrown.
        If the user cancels the dialog then a SapioUserCancelledException is thrown.
        If the user provides a blank result, then the handling is used to determine what to do with that result.

        :param request: The client callback request to send to the user.
        :param func: The ClientCallback function to call with the given request as input.
        :param not_blank_func: The function to determine whether the provided result is blank or not.
        :param handling: The handling to use for blank results.
        :param repeat_message: If handling is REPEAT and a repeat_message is provided, then that message appears as
            toaster text when the user provides a blank result.
        :param cancel_message: If handling is CANCEL and a cancel_message is provided, then that message appears as
            toaster text when the user provides a blank result.
        :param kwargs: Additional keywords for the provided function call.
        :return: The response from the client callback, if one was received.
        """
        if handling == BlankResultHandling.DEFAULT or handling is None:
            handling = self._default_blank_result_handling
        while True:
            response: Any | None = self.__handle_timeout(func, request, **kwargs)
            if response is None:
                raise SapioUserCancelledException()
            if not_blank_func(response):
                return response
            match handling:
                case BlankResultHandling.CANCEL:
                    # If the user provided no selection, throw an exception.
                    if cancel_message:
                        self.toaster_popup(cancel_message, popup_type=PopupType.Warning)
                    raise SapioUserCancelledException()
                case BlankResultHandling.REPEAT:
                    # If the user provided no selection, repeat the dialog.
                    # If a repeatMessage is provided, display it as a toaster popup.
                    if repeat_message:
                        self.toaster_popup(repeat_message, popup_type=PopupType.Warning)
                case BlankResultHandling.RETURN:
                    # If the user provided no selection, return the blank result.
                    return response


class FieldModifier:
    """
    A FieldModifier can be used to update the settings of a field definition from the system.
    """
    prepend_data_type: bool
    display_name: str | None
    required: bool | None
    editable: bool | None
    visible: bool | None
    key_field: bool | None
    column_width: int | None

    def __init__(self, *, prepend_data_type: bool = False,
                 display_name: str | None = None, required: bool | None = None, editable: bool | None = None,
                 visible: bool | None = None, key_field: bool | None = None, column_width: int | None = None):
        """
        If any values are given as None then that value will not be changed on the given field.

        :param prepend_data_type: If true, prepends the data type name of the field to the data field name. For example,
            if a field has a data type name X and a data field name Y, then the field name would become "X.Y". This is
            useful for cases where you have the same field name on two different data types and want to distinguish one
            or both of them.
        :param display_name: Change the display name.
        :param required: Change the required status.
        :param editable: Change the editable status.
        :param visible: Change the visible status.
        :param key_field: Change the key field status.
        :param column_width: Change the column width.
        """
        self.prepend_data_type = prepend_data_type
        self.display_name = display_name
        self.required = required
        self.editable = editable
        self.visible = visible
        self.key_field = key_field
        self.column_width = column_width

    def modify_field(self, field: AbstractVeloxFieldDefinition) -> AbstractVeloxFieldDefinition:
        """
        Apply modifications to a given field.

        :param field: The field to modify.
        :return: A copy of the input field with the modifications applied. The input field is unchanged.
        """
        ret_val: AbstractVeloxFieldDefinition = copy(field)
        if self.prepend_data_type is True:
            ret_val._data_field_name = ret_val.data_type_name + "." + ret_val.data_field_name
        if self.display_name is not None:
            ret_val.display_name = self.display_name
        if self.required is not None:
            ret_val.required = self.required
        if self.editable is not None:
            ret_val.editable = self.editable
        if self.visible is not None:
            ret_val.visible = self.visible
        if self.key_field is not None:
            ret_val.key_field = self.key_field
        if self.column_width is not None:
            ret_val.default_table_column_width = self.column_width
        return ret_val


# CR-46866: Create a class that can be used by record-backed dialogs to filter for the fields displayed in the dialog
# based on the attributes of the field definitions of the data type instead of requiring that the caller know the
# names of the fields to be displayed.
class FieldFilterCriteria:
    """
    A FieldFilterCriteria can be used to filter the fields that are displayed in certain record-backed client callbacks.
    """
    required: bool | None
    editable: bool | None
    key_field: bool | None
    identifier: bool | None
    system_field: bool | None
    field_types: Container[FieldType] | None
    not_field_types: Container[FieldType] | None
    matches_tag: str | None
    contains_tag: str | None
    regex_tag: str | re.Pattern[str] | None

    def __init__(self, *, required: bool | None = None, editable: bool | None = None, key_field: bool | None = None,
                 identifier: bool | None = None, system_field: bool | None = None,
                 field_types: Container[FieldType] | None = None, not_field_types: Container[FieldType] | None = None,
                 matches_tag: str | None = None, contains_tag: str | None = None,
                 regex_tag: str | re.Pattern[str] | None = None):
        """
        Values that are left as None have no effect on the filtering. A field must match all non-None values in order
        to count as matching this filter.

        :param required: Whether the field is required.
        :param editable: Whether the field is editable.
        :param key_field: Whether the field is a key field.
        :param identifier: Whether the field is an identifier field.
        :param system_field: Whether the field is a system field.
        :param field_types: Include fields matching these types.
        :param not_field_types: Exclude fields matching these types.
        :param matches_tag: If provided, the field's tag must exactly match this value.
        :param contains_tag: If provided, the field's tag must contain this value.
        :param regex_tag: If provided, the field's tag must match this regex.
        """
        self.required = required
        self.editable = editable
        self.key_field = key_field
        self.identifier = identifier
        self.system_field = system_field
        self.field_types = field_types
        self.not_field_types = not_field_types
        self.matches_tag = matches_tag
        self.contains_tag = contains_tag
        self.regex_tag = regex_tag

    def field_matches(self, field: AbstractVeloxFieldDefinition) -> bool:
        """
        :param field: A field definition from a data type.
        :return: Whether the field definition matches the filter criteria.
        """
        ret_val: bool = True
        if self.required is not None:
            ret_val = ret_val and self.required == field.required
        if self.editable is not None:
            ret_val = ret_val and self.editable == field.editable
        if self.key_field is not None:
            ret_val = ret_val and self.key_field == field.key_field
        if self.identifier is not None:
            ret_val = ret_val and self.identifier == field.identifier
        if self.system_field is not None:
            ret_val = ret_val and self.system_field == field.system_field
        if self.field_types is not None:
            ret_val = ret_val and field.data_field_type in self.field_types
        if self.not_field_types is not None:
            ret_val = ret_val and field.data_field_type not in self.not_field_types
        if self.matches_tag is not None:
            ret_val = ret_val and field.tag is not None and self.matches_tag == field.tag
        if self.contains_tag is not None:
            ret_val = ret_val and field.tag is not None and self.contains_tag in field.tag
        if self.regex_tag is not None:
            ret_val = ret_val and field.tag is not None and bool(re.match(self.regex_tag, field.tag))
        return ret_val
