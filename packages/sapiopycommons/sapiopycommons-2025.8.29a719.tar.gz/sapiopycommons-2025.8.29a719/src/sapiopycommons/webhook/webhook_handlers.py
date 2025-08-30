from __future__ import annotations

import json
import sys
import time
import traceback
from abc import abstractmethod
from logging import Logger

from sapiopylib.rest.AccessionService import AccessionManager
from sapiopylib.rest.CustomReportService import CustomReportManager
from sapiopylib.rest.DashboardManager import DashboardManager
from sapiopylib.rest.DataMgmtService import DataMgmtServer
from sapiopylib.rest.DataRecordManagerService import DataRecordManager
from sapiopylib.rest.DataService import DataManager
from sapiopylib.rest.DataTypeService import DataTypeManager
from sapiopylib.rest.ELNService import ElnManager
from sapiopylib.rest.GroupManagerService import VeloxGroupManager
from sapiopylib.rest.MessengerService import SapioMessenger
from sapiopylib.rest.PicklistService import PickListManager
from sapiopylib.rest.ReportManager import ReportManager
from sapiopylib.rest.SesssionManagerService import SessionManager
from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.UserManagerService import VeloxUserManager
from sapiopylib.rest.WebhookService import AbstractWebhookHandler
from sapiopylib.rest.pojo.Message import VeloxLogMessage, VeloxLogLevel
from sapiopylib.rest.pojo.webhook.ClientCallbackRequest import PopupType
from sapiopylib.rest.pojo.webhook.WebhookContext import SapioWebhookContext
from sapiopylib.rest.pojo.webhook.WebhookEnums import WebhookEndpointType
from sapiopylib.rest.pojo.webhook.WebhookResult import SapioWebhookResult
from sapiopylib.rest.utils.DataTypeCacheManager import DataTypeCacheManager
from sapiopylib.rest.utils.FoundationAccessioning import FoundationAccessionManager
from sapiopylib.rest.utils.recordmodel.RecordModelManager import RecordModelManager, RecordModelInstanceManager, \
    RecordModelRelationshipManager
from sapiopylib.rest.utils.recordmodel.ancestry import RecordModelAncestorManager
from sapiopylib.rest.utils.recordmodel.last_saved import LastSavedValueManager

from sapiopycommons.callbacks.callback_util import CallbackUtil
from sapiopycommons.eln.experiment_handler import ExperimentHandler
from sapiopycommons.general.directive_util import DirectiveUtil
from sapiopycommons.general.exceptions import SapioUserErrorException, SapioCriticalErrorException, \
    SapioUserCancelledException, SapioException, SapioDialogTimeoutException, MessageDisplayType
from sapiopycommons.general.sapio_links import SapioNavigationLinker
from sapiopycommons.general.time_util import TimeUtil
from sapiopycommons.recordmodel.record_handler import RecordHandler
from sapiopycommons.rules.eln_rule_handler import ElnRuleHandler
from sapiopycommons.rules.on_save_rule_handler import OnSaveRuleHandler
from sapiopycommons.webhook.webhook_context import ProcessQueueContext


# FR-46064 - Initial port of PyWebhookUtils to sapiopycommons.
class CommonsWebhookHandler(AbstractWebhookHandler):
    """
    A subclass of AbstractWebhookHandler that provides additional quality of life features, including exception
    handling for special sapiopycommons exceptions, logging, easy access invocation type methods, and the context and
    record managers accessible through self.
    """
    logger: Logger

    _start_time: float
    _start_time_epoch: int

    user: SapioUser
    """The user who invoked this webhook. Used for authenticating requests back to the Sapio server."""
    group_name: str
    """The name of the group that the user invoked this webhook with."""
    user_utc_offset_seconds: int
    """The number of seconds that the user is offset from the UTC timezone. Able to be used with TimeUtil to display
    timestamps in the user's timezone."""
    context: SapioWebhookContext
    """The context from the server of this webhook's invocation."""

    # CR-47383: Include every manager from DataMgmtServer for easier access.
    acc_man: AccessionManager
    """A class for making requests to the accession webservice endpoints."""
    fnd_acc_man: FoundationAccessionManager
    """A class for making requests to the Foundations accession webservice endpoints."""
    report_man: CustomReportManager
    """A class for making requests to the custom report webservice endpoints."""
    dash_man: DashboardManager
    """A class for making requests to the dashboard management webservice endpoints."""
    xml_data_man: DataManager
    """A class for making requests to the data record import/export via XML webservice endpoints."""
    dr_man: DataRecordManager
    """A class for making requests to the data record webservice endpoints."""
    dt_man: DataTypeManager
    """A class for making requests to the data type webservice endpoints."""
    eln_man: ElnManager
    """A class for making requests to the ELN management webservice endpoints."""
    group_man: VeloxGroupManager
    """A class for making requests to the group management webservice endpoints."""
    messenger: SapioMessenger
    """A class for making requests to the message webservice endpoints."""
    list_man: PickListManager
    """A class for making requests to the pick list webservice endpoints."""
    pdf_report_man: ReportManager
    """A class for making requests to the report webservice endpoints."""
    session_man: SessionManager
    """A class for making requests to the session management webservice endpoints."""
    user_man: VeloxUserManager
    """A class for making requests to the user management webservice endpoints."""

    rec_man: RecordModelManager
    """The record model manager. Used for committing record model changes to the system."""
    inst_man: RecordModelInstanceManager
    """The record model instance manager. Used for adding record models to the cache."""
    rel_man: RecordModelRelationshipManager
    """The record model relationship manager. Used for loading parent/child and side-link relationships between record
    models."""
    # FR-46329: Add the ancestor manager to CommonsWebhookHandler.
    an_man: RecordModelAncestorManager
    """The record model ancestor manager. Used for loading ancestor relationships between record models."""
    saved_vals_man: LastSavedValueManager
    """The last saved values manager. Used for determining what the record values were prior to this commit."""

    dt_cache: DataTypeCacheManager
    """A class that calls the same endpoints as the DataTypeManager (self.dt_man), except the results are cached so that
    repeated calls to the same function don't result in duplicate webservice calls. """
    rec_handler: RecordHandler
    """A class that behaves like a combination between the DataRecordManager and RecordModelInstanceManager, allowing
    you to query and wrap record as record models in a single function call, among other functions useful for dealing
    with record models."""
    callback: CallbackUtil
    """A class for making requests to the client callback webservice endpoints."""
    directive: DirectiveUtil
    """A class for making directives that redirect the user to a new webpage after this webhook returns a result."""
    exp_handler: ExperimentHandler | None
    """If this webhook was invoked from within an ELN experiment, this variable will be populated with an
    ExperimentHandler initialized from the context. """
    rule_handler: OnSaveRuleHandler | ElnRuleHandler | None
    """If this is an ELN or on save rule endpoint, this variable will be populated with an ElnRuleHandler or
    OnSaveRuleHandler, depending on the endpoint type."""
    custom_context: ProcessQueueContext | None
    """If this is a custom endpoint, this variable will be populated with an object that parses the custom context
    data."""

    # FR-47390: Allow for classes that extend CommonsWebhookHandler to change how exception messages are displayed
    # to the user be changing these variables instead of needing to override the exception handling functions.
    default_user_error_display_type: MessageDisplayType
    """The default message display type for user error exceptions. If a user error exception is thrown and doesn't
    specify a display type, this type will be used."""
    default_critical_error_display_type: MessageDisplayType
    """The default message display type for critical error exceptions. If a critical error exception is thrown and
    doesn't specify a display type, this type will be used."""
    default_dialog_timeout_display_type: MessageDisplayType
    """The default message display type for dialog timeout exceptions."""
    default_unexpected_error_display_type: MessageDisplayType
    """The default message display type for unexpected exceptions."""

    default_user_error_title: str
    """The default title to display to the user when a user error occurs. If a user error exception is thrown and
    doesn't specify a title, this title will be used."""
    default_critical_error_title: str
    """The default title to display to the user when a critical error occurs. If a critical error exception is thrown
    and doesn't specify a title, this title will be used."""
    default_dialog_timeout_title: str
    """The default title to display to the user when a dialog times out."""
    default_unexpected_error_title: str
    """The default title to display to the user when an unexpected exception occurs."""

    default_dialog_timeout_message: str
    """The default message to display to the user when a dialog times out."""
    default_unexpected_error_message: str
    """The default message to display to the user when an unexpected exception occurs."""

    def run(self, context: SapioWebhookContext) -> SapioWebhookResult:
        # Timestamps used for measuring performance.
        self._start_time = time.perf_counter()
        self._start_time_epoch = TimeUtil.now_in_millis()

        # Save the webhook context so that any function of this class can access it.
        self.context = context

        # Save the user and commonly sought after user information.
        self.user = context.user
        self.group_name = self.user.session_additional_data.current_group_name
        self.user_utc_offset_seconds = self.user.session_additional_data.utc_offset_seconds

        # Get the logger from the user.
        self.logger = self.user.logger

        # Initialize basic manager classes from sapiopylib.
        self.acc_man = DataMgmtServer.get_accession_manager(self.user)
        self.report_man = DataMgmtServer.get_custom_report_manager(self.user)
        self.dash_man = DataMgmtServer.get_dashboard_manager(self.user)
        self.xml_data_man = DataMgmtServer.get_data_manager(self.user)
        self.dr_man = context.data_record_manager
        self.dt_man = DataMgmtServer.get_data_type_manager(self.user)
        self.eln_man = context.eln_manager
        self.group_man = DataMgmtServer.get_group_manager(self.user)
        self.messenger = DataMgmtServer.get_messenger(self.user)
        self.list_man = DataMgmtServer.get_picklist_manager(self.user)
        self.pdf_report_man = DataMgmtServer.get_report_manager(self.user)
        self.session_man = DataMgmtServer.get_session_manager(self.user)
        self.user_man = DataMgmtServer.get_user_manager(self.user)

        # Initialize record model managers.
        self.rec_man = RecordModelManager(self.user)
        self.inst_man = self.rec_man.instance_manager
        self.rel_man = self.rec_man.relationship_manager
        self.an_man = self.rec_man.ancestor_manager
        self.saved_vals_man = self.rec_man.last_saved_manager

        # Initialize more complex classes from sapiopylib and sapiopycommons.
        self.fnd_acc_man = FoundationAccessionManager(self.user)
        self.dt_cache = DataTypeCacheManager(self.user)
        self.rec_handler = RecordHandler(context)
        self.callback = CallbackUtil(context)
        self.directive = DirectiveUtil(context)
        if context.eln_experiment is not None:
            self.exp_handler = ExperimentHandler(context)
        else:
            self.exp_handler = None
        if self.is_on_save_rule():
            self.rule_handler = OnSaveRuleHandler(context)
        elif self.is_eln_rule():
            self.rule_handler = ElnRuleHandler(context)
        else:
            self.rule_handler = None
        if self.is_custom():
            self.custom_context = ProcessQueueContext(context)
        else:
            self.custom_context = None

        # CR-47526: Set the dialog timeout to 1 hour by default. This can be overridden by the webhook.
        self.callback.set_dialog_timeout(3600)

        # Set the default display types, titles, and messages for each type of exception that can display a message.
        self.default_user_error_display_type = MessageDisplayType.TOASTER_WARNING
        self.default_critical_error_display_type = MessageDisplayType.DISPLAY_ERROR
        self.default_dialog_timeout_display_type = MessageDisplayType.OK_DIALOG
        self.default_unexpected_error_display_type = MessageDisplayType.TOASTER_WARNING

        self.default_user_error_title = ""
        self.default_critical_error_title = ""
        self.default_dialog_timeout_title = "Dialog Timeout"
        self.default_unexpected_error_title = ""

        self.default_dialog_timeout_message = ("You have remained idle for too long and this dialog has timed out. "
                                               "Close and re-initiate it to continue.")
        self.default_unexpected_error_message = ("Unexpected error occurred during webhook execution. Please contact "
                                                 "Sapio support.")

        # Wrap the execution of each webhook in a try/catch. If an exception occurs, handle any special sapiopycommons
        # exceptions. Otherwise, return a generic message stating that an error occurred.
        try:
            self.initialize(context)
            result = self.execute(context)
            if result is None:
                raise SapioException("Your execute function returned a None result! Don't forget your return statement!")
            return result
        except SapioUserErrorException as e:
            return self.handle_user_error_exception(e)
        except SapioCriticalErrorException as e:
            return self.handle_critical_error_exception(e)
        except SapioUserCancelledException as e:
            return self.handle_user_cancelled_exception(e)
        except SapioDialogTimeoutException as e:
            return self.handle_dialog_timeout_exception(e)
        except Exception as e:
            return self.handle_unexpected_exception(e)

    def initialize(self, context: SapioWebhookContext) -> None:
        """
        A function that can be optionally overridden by your webhooks to initialize additional instance variables,
        or set up whatever else you wish to set up before the execute function is ran. Default behavior does nothing.
        """
        pass

    @abstractmethod
    def execute(self, context: SapioWebhookContext) -> SapioWebhookResult:
        """
        The business logic of the webhook, implemented in all subclasses that are called as endpoints.
        """
        pass

    # CR-46153: Make CommonsWebhookHandler exception handling more easily overridable by splitting them out of
    # the run method and into their own functions.
    def handle_user_error_exception(self, e: SapioUserErrorException) -> SapioWebhookResult:
        """
        Handle a SapioUserErrorException.

        Default behavior returns a false result and the error message as display text in a webhook result.

        :param e: The exception that was raised.
        :return: A SapioWebhookResult to end the webhook session with.
        """
        result: SapioWebhookResult | None = self.handle_any_exception(e)
        if result is not None:
            return result
        self.log_error(traceback.format_exc())
        self.handle_user_error_exception_extra(e)

        display_type: MessageDisplayType = e.display_type if e.display_type else self.default_user_error_display_type
        title: str = e.title if e.title is not None else self.default_user_error_title
        return self._display_exception(e.msg, display_type, title)

    def handle_user_error_exception_extra(self, e: SapioUserErrorException) -> None:
        """
        An additional function that can be overridden to provide extra behavior when a SapioUserErrorException is thrown.
        Default behavior does nothing.
        """
        pass

    def handle_critical_error_exception(self, e: SapioCriticalErrorException) -> SapioWebhookResult:
        """
        Handle a SapioCriticalErrorException.

        Default behavior makes a display_error client callback with the error message and returns a false result.

        :param e: The exception that was raised.
        :return: A SapioWebhookResult to end the webhook session with.
        """
        result: SapioWebhookResult | None = self.handle_any_exception(e)
        if result is not None:
            return result
        self.log_error(traceback.format_exc())
        self.handle_critical_error_exception_extra(e)

        display_type: MessageDisplayType = e.display_type if e.display_type else self.default_critical_error_display_type
        title: str = e.title if e.title is not None else self.default_critical_error_title
        return self._display_exception(e.msg, display_type, title)

    def handle_critical_error_exception_extra(self, e: SapioCriticalErrorException) -> None:
        """
        An additional function that can be overridden to provide extra behavior when a SapioCriticalErrorException is
        thrown. Default behavior does nothing.
        """
        pass

    def handle_user_cancelled_exception(self, e: SapioUserCancelledException) -> SapioWebhookResult:
        """
        Handle a SapioUserCancelledException.

        Default behavior simply ends the webhook session with a true result (since the user cancelling is a valid
        action).

        :param e: The exception that was raised.
        :return: A SapioWebhookResult to end the webhook session with.
        """
        result: SapioWebhookResult | None = self.handle_any_exception(e)
        if result is not None:
            return result
        self.handle_user_cancelled_exception_extra(e)
        # FR-47390: Return a False result for user cancelled exceptions so that transactional webhooks cancel the
        # commit.
        return SapioWebhookResult(False)

    def handle_user_cancelled_exception_extra(self, e: SapioUserCancelledException) -> None:
        """
        An additional function that can be overridden to provide extra behavior when a SapioUserCancelledException is
        thrown. Default behavior does nothing.
        """
        pass

    def handle_dialog_timeout_exception(self, e: SapioDialogTimeoutException) -> SapioWebhookResult:
        """
        Handle a SapioDialogTimeoutException.

        Default behavior displays an OK popup notifying the user that the dialog has timed out and returns a false
        webhook result.

        :param e: The exception that was raised.
        :return: A SapioWebhookResult to end the webhook session with.
        """
        result: SapioWebhookResult | None = self.handle_any_exception(e)
        if result is not None:
            return result
        self.handle_dialog_timeout_exception_extra(e)
        return self._display_exception(self.default_dialog_timeout_message,
                                       self.default_dialog_timeout_display_type,
                                       self.default_dialog_timeout_title)

    def handle_dialog_timeout_exception_extra(self, e: SapioDialogTimeoutException) -> None:
        """
        An additional function that can be overridden to provide extra behavior when a SapioDialogTimeoutException is
        thrown. Default behavior does nothing.
        """
        pass

    def handle_unexpected_exception(self, e: Exception) -> SapioWebhookResult:
        """
        Handle a generic exception which isn't one of the handled Sapio exceptions.

        Default behavior returns a false webhook result with a generic error message as display text informing the user
        to contact Sapio support. Additionally, the stack trace of the exception that was thrown is logged to the
        execution log for the webhook call in the system.

        :param e: The exception that was raised.
        :return: A SapioWebhookResult to end the webhook session with.
        """
        result: SapioWebhookResult | None = self.handle_any_exception(e)
        if result is not None:
            return result
        msg: str = traceback.format_exc()
        self.log_error(msg, True)
        # FR-47079: Also log all unexpected exception messages to the webhook execution log within the platform.
        self.log_error_to_webhook_execution_log(msg, True)
        self.handle_unexpected_exception_extra(e)
        return self._display_exception(self.default_unexpected_error_message,
                                       self.default_unexpected_error_display_type,
                                       self.default_unexpected_error_title)

    def handle_unexpected_exception_extra(self, e: Exception) -> None:
        """
        An additional function that can be overridden to provide extra behavior when a generic exception is thrown.
        Default behavior does nothing.
        """
        pass

    def handle_any_exception(self, e: Exception) -> SapioWebhookResult | None:
        """
        An exception handler which runs regardless of the type of exception that was raised. Can be used to "rollback"
        the client if an error occurs. Default behavior does nothing and returns None.

        :param e: The exception that was raised.
        :return: An optional SapioWebhookResult. May return a custom message to the client that wouldn't have been
            sent by one of the normal exception handlers, or may return None if no result needs returned. If a result is
            returned, then the default behavior of other exception handlers is skipped.
        """
        pass

    def display_message(self, msg: str, display_type: MessageDisplayType, title: str = "") -> bool:
        """
        Display a message to the user. The form that the message takes depends on the display type.

        :param msg: The message to display to the user.
        :param display_type: The manner in which the message should be displayed.
        :param title: If the display type is able to have a title, this is the title that will be displayed.
        :return: True if the message was displayed. False if the message could not be displayed (because this
            webhook can't send client callbacks).
        """
        if not self.can_send_client_callback():
            return False
        if display_type == MessageDisplayType.TOASTER_SUCCESS:
            self.callback.toaster_popup(msg, title, PopupType.Success)
        elif display_type == MessageDisplayType.TOASTER_INFO:
            self.callback.toaster_popup(msg, title, PopupType.Info)
        elif display_type == MessageDisplayType.TOASTER_WARNING:
            self.callback.toaster_popup(msg, title, PopupType.Warning)
        elif display_type == MessageDisplayType.TOASTER_ERROR:
            self.callback.toaster_popup(msg, title, PopupType.Error)
        elif display_type == MessageDisplayType.OK_DIALOG:
            self.callback.ok_dialog(title, msg)
        elif display_type == MessageDisplayType.DISPLAY_INFO:
            self.callback.display_info(msg)
        elif display_type == MessageDisplayType.DISPLAY_WARNING:
            self.callback.display_warning(msg)
        elif display_type == MessageDisplayType.DISPLAY_ERROR:
            self.callback.display_error(msg)
        return True

    def _display_exception(self, msg: str, display_type: MessageDisplayType, title: str) -> SapioWebhookResult:
        """
        Display an exception message to the user and return a webhook result to end the webhook invocation.
        This handles the cases where the webhook invocation type is incapable of sending client callbacks and must
        instead return the message in the webhook result, and the case where the display type is an OK dialog, which
        may potentially cause a dialog timeout exception.
        """
        # If the display type is an OK dialog, then we need to handle the dialog timeout exception that could be thrown.
        try:
            # Set the dialog timeout to something low as to not hog the connection.
            self.callback.set_dialog_timeout(60)
            # If this invocation type can't send client callbacks, fallback to sending the message in the result.
            if self.display_message(msg, display_type, title):
                return SapioWebhookResult(False)
            return SapioWebhookResult(False, display_text=msg)
        except SapioDialogTimeoutException:
            return SapioWebhookResult(False)

    def log_info(self, msg: str) -> None:
        """
        Write an info message to the webhook server log. Log destination is stdout. This message will include
        information about the user's group, their location in the system, the webhook invocation type, and other
        important information that can be gathered from the context that is useful for debugging.
        """
        self.logger.info(self._format_log(msg, "log_info call"))

    def log_error(self, msg: str, is_exception: bool = False) -> None:
        """
        Write an info message to the webhook server log. Log destination is stdout. This message will include
        information about the user's group, their location in the system, the webhook invocation type, and other
        important information that can be gathered from the context that is useful for debugging.
        """
        # PR-46209: Use logger.error instead of logger.info when logging errors.
        self.logger.error(self._format_log(msg, "log_error call", is_exception))

    def log_error_to_webhook_execution_log(self, msg: str, is_exception: bool = False) -> None:
        """
        Write an error message to the platform's webhook execution log. This can be reviewed by navigating to the
        webhook configuration where the webhook that called this function is defined and clicking the "View Log"
        button. From there, select one of the rows for the webhook executions and click "Download Log" from the right
        side table.
        """
        msg = self._format_log(msg, "Error occurred during webhook execution.", is_exception)
        self.messenger.log_message(VeloxLogMessage(msg, VeloxLogLevel.ERROR, self.__class__.__name__))

    def _format_log(self, msg: str, prefix: str | None = None, is_exception: bool = False) -> str:
        """
        Given a message to log, populate it with some metadata about this particular webhook execution, including
        the group of the user and the invocation type of the webhook call.
        """
        # Start the message with the provided prefix.
        message: str = prefix + "\n" if prefix else ""

        # Construct a summary of the current state of this webhook.
        message += f"{WebhookStateSummary(self, is_exception)}\n"

        # End the message with the provided msg parameter.
        message += msg
        return message

    @property
    def start_time(self) -> float:
        """
        :return: The time that this webhook was invoked, represented in seconds. This time comes from a performance
            counter and is not guaranteed to correspond to a date. Only use in comparison to other performance counters.
        """
        return self._start_time

    @property
    def start_time_millis(self) -> int:
        """
        :return: The epoch timestamp in milliseconds for the time that this webhook was invoked.
        """
        return self._start_time_epoch

    def elapsed_time(self) -> float:
        """
        :return: The number of seconds that have elapsed since this webhook was invoked to the time that this function
            is called. Measures using a performance counter to a high degree of accuracy.
        """
        return time.perf_counter() - self._start_time

    def elapsed_time_millis(self) -> int:
        """
        :return: The number of milliseconds that have elapsed since this webhook was invoked to the time that this
            function is called.
        """
        return TimeUtil.now_in_millis() - self._start_time_epoch

    def is_main_toolbar(self) -> bool:
        """
        :return: True if this endpoint was invoked as a main toolbar button.
        """
        return self.context.end_point_type == WebhookEndpointType.ACTIONMENU

    def is_form_toolbar(self) -> bool:
        """
        :return: True if this endpoint was invoked as a data record form toolbar button.
        """
        return self.context.end_point_type == WebhookEndpointType.FORMTOOLBAR

    def is_table_toolbar(self) -> bool:
        """
        :return: True if this endpoint was invoked as a data record table toolbar button.
        """
        return self.context.end_point_type == WebhookEndpointType.TABLETOOLBAR

    def is_temp_form_toolbar(self) -> bool:
        """
        :return: True if this endpoint was invoked as a temporary data record form toolbar button.
        """
        return self.context.end_point_type == WebhookEndpointType.TEMP_DATA_FORM_TOOLBAR

    def is_temp_table_toolbar(self) -> bool:
        """
        :return: True if this endpoint was invoked as a temporary data record table toolbar button.
        """
        return self.context.end_point_type == WebhookEndpointType.TEMP_DATA_TABLE_TOOLBAR

    def is_eln_rule(self) -> bool:
        """
        :return: True if this endpoint was invoked as an ELN rule action.
        """
        return self.context.end_point_type == WebhookEndpointType.VELOXELNRULEACTION

    def is_on_save_rule(self) -> bool:
        """
        :return: True if this endpoint was invoked as an on save rule action.
        """
        return self.context.end_point_type == WebhookEndpointType.VELOX_RULE_ACTION
        # TODO: This VELOXONSAVERULEACTION endpoint type exists, but I don't see it actually getting sent by on save
        #  rule action invocations, instead seeing the above VELOX_RULE_ACTION type. Probably worth investigation.
        # return self.context.end_point_type == WebhookEndpointType.VELOXONSAVERULEACTION

    def is_eln_main_toolbar(self) -> bool:
        """
        :return: True if this endpoint was invoked as an ELN main toolbar button.
        """
        return self.context.end_point_type == WebhookEndpointType.NOTEBOOKEXPERIMENTMAINTOOLBAR

    def is_eln_entry_toolbar(self) -> bool:
        """
        :return: True if this endpoint was invoked as an ELN entry toolbar button.
        """
        return self.context.end_point_type == WebhookEndpointType.EXPERIMENTENTRYTOOLBAR

    def is_selection_list(self) -> bool:
        """
        :return: True if this endpoint was invoked as a selection list populator.
        """
        return self.context.end_point_type == WebhookEndpointType.SELECTIONDATAFIELD

    def is_report_builder(self) -> bool:
        """
        :return: True if this endpoint was invoked as a report builder template data populator.
        """
        return self.context.end_point_type == WebhookEndpointType.REPORT_BUILDER_TEMPLATE_DATA_POPULATOR

    def is_scheduled_action(self) -> bool:
        """
        :return: True if this endpoint was invoked as a scheduled action.
        """
        return self.context.end_point_type == WebhookEndpointType.SCHEDULEDPLUGIN

    def is_action_button_field(self) -> bool:
        """
        :return: True if this endpoint was invoked as an action button field.
        """
        return self.context.end_point_type == WebhookEndpointType.ACTIONDATAFIELD

    def is_action_text_field(self) -> bool:
        """
        :return: True if this endpoint was invoked as an action text field.
        """
        return self.context.end_point_type == WebhookEndpointType.ACTION_TEXT_FIELD

    def is_custom(self) -> bool:
        """
        :return: True if this endpoint was invoked from a custom point, such as a custom queue.
        """
        return self.context.end_point_type == WebhookEndpointType.CUSTOM

    def is_calendar_event_click_handler(self) -> bool:
        """
        :return: True if this endpoint was invoked from a calendar event click handler.
        """
        return self.context.end_point_type == WebhookEndpointType.CALENDAR_EVENT_CLICK_HANDLER

    def is_eln_menu_grabber(self) -> bool:
        """
        :return: True if this endpoint was invoked as a notebook entry grabber.
        """
        return self.context.end_point_type == WebhookEndpointType.NOTEBOOKEXPERIMENTGRABBER

    def is_conversation_bot(self) -> bool:
        """
        :return: True if this endpoint was invoked as from a conversation bot.
        """
        return self.context.end_point_type == WebhookEndpointType.CONVERSATION_BOT

    def is_multi_data_type_table_toolbar(self) -> bool:
        """
        :return: True if this endpoint was invoked as a multi data type table toolbar button.
        """
        return self.context.end_point_type == WebhookEndpointType.REPORTTOOLBAR

    def can_send_client_callback(self) -> bool:
        """
        :return: Whether client callbacks and directives can be sent from this webhook's endpoint type.
        """
        return self.context.is_client_callback_available


# FR-47390: Move the gathering of webhook information out of log_error_to_webhook_execution_log and into its own class.
class WebhookStateSummary:
    """
    A class that summarizes the state of a webhook at the time that it is created. This class is useful for logging
    information about the webhook invocation to the execution log.
    """
    username: str
    """The username of the user who invoked the webhook."""
    user_group: str
    """The group that the user is currently in."""
    start_timestamp: int
    """The epoch timestamp in milliseconds for when the webhook was invoked."""
    start_utc_time: str
    """The time that the webhook was invoked in UTC."""
    start_server_time: str | None
    """The time that the webhook was invoked on the server, if the TimeUtil class has a default timezone set."""
    start_user_time: str
    """The time that the webhook was invoked for the user, adjusted for their timezone."""
    timestamp: int
    """The current epoch timestamp in milliseconds."""
    utc_time: str
    """The current time in UTC."""
    server_time: str | None
    """The current time on the webhook server, if the TimeUtil class has a default timezone set."""
    user_time: str
    """The current time for the user, adjusted for their timezone."""
    invocation_type: str
    """The type of endpoint that this webhook was invoked from."""
    class_name: str
    """The name of the class that this webhook is an instance of."""
    link: str | None
    """A link to the location that the webhook was invoked from, if applicable."""
    exc_summary: str | None
    """A summary of the exception that occurred, if this summary is being created for an exception."""

    def __init__(self, webhook: CommonsWebhookHandler, summarize_exception: bool = False):
        """
        :param webhook: The webhook that this summary is being created for.
        :param summarize_exception: If true, then this summary will include information about the most recent exception
            that occurred during the execution of the webhook.
        """
        # User information.
        self.username = webhook.user.username
        self.user_group = webhook.group_name

        # Time information.
        fmt: str = "%Y-%m-%d %H:%M:%S.%f"
        self.start_timestamp = webhook.start_time_millis
        self.start_utc_time = TimeUtil.millis_to_format(self.start_timestamp, fmt, "UTC")
        self.start_server_time = None
        self.start_user_time = TimeUtil.millis_to_format(self.start_timestamp, fmt, webhook.user_utc_offset_seconds)

        self.timestamp = TimeUtil.now_in_millis()
        self.utc_time = TimeUtil.millis_to_format(self.timestamp, fmt, "UTC")
        self.server_time = None
        self.user_time = TimeUtil.millis_to_format(self.timestamp, fmt, webhook.user_utc_offset_seconds)

        if TimeUtil.get_default_timezone():
            self.start_server_time = TimeUtil.millis_to_format(self.start_timestamp, fmt)
            self.server_time = TimeUtil.millis_to_format(self.timestamp, fmt)

        # Webhook invocation information.
        self.invocation_type = webhook.context.end_point_type.display_name
        self.class_name = webhook.__class__.__name__

        # User location information.
        self.link = None
        context = webhook.context
        navigator = SapioNavigationLinker(context)
        if context.eln_experiment is not None:
            self.link = navigator.experiment(context.eln_experiment)
        elif context.base_data_record:
            self.link = navigator.data_record(context.base_data_record)
        elif context.data_record and not context.data_record_list:
            self.link = navigator.data_record(context.data_record)

        # If this is logging an exception, get the system's info on the most recent exception and produce a summary.
        self.exc_summary = None
        if summarize_exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()

            # If this is a SapioServerException, then it can contain json with the exception message from the server.
            # This provides a more useful summary than args[0] does, so use it instead.
            exception_name: str = exc_type.__name__
            if exception_name == "SapioServerException":
                # Sometimes the SapioServerException is HTML instead of JSON. If that's the case, just try/catch the
                # failure to parse the JSON and continue to use args[0] as the exception message.
                try:
                    exc_str: str = str(exc_value)
                    exception_msg = json.loads(exc_str[exc_str.find("{"):]).get("message")
                except Exception:
                    exception_msg = exc_value.args[0]
            else:
                # For all other exceptions, assume that the first argument is a message.
                exception_msg = exc_value.args[0]

            self.exc_summary = f"{exception_name}: {exception_msg}"
            del (exc_type, exc_value, exc_traceback)

    def __str__(self) -> str:
        message: str = ""

        # Record the time that the webhook was started and this state was created.
        message += "Webhook Invocation Time:\n"
        message += f"\tUTC: {self.start_utc_time}\n"
        if TimeUtil.get_default_timezone() is not None:
            message += f"\tServer: {self.start_server_time}\n"
        message += f"\tUser: {self.start_user_time}\n"

        message += "Current Time:\n"
        message += f"\tUTC: {self.utc_time}\n"
        if TimeUtil.get_default_timezone() is not None:
            message += f"\tServer: {self.server_time}\n"
        message += f"\tUser: {self.user_time}\n"

        # Record information about the user and how the webhook was invoked.
        message += f"Username: {self.username}\n"
        message += f"User group: {self.user_group}\n"
        message += f"Webhook invocation type: {self.invocation_type}\n"
        message += f"Class name: {self.class_name}\n"

        # If we're able to, provide a link to the location that the error occurred at.
        if self.link:
            message += f"User location: {self.link}\n"

        # If this state summary is for an exception, include the exception summary.
        if self.exc_summary:
            message += f"{self.exc_summary}\n"

        return message
