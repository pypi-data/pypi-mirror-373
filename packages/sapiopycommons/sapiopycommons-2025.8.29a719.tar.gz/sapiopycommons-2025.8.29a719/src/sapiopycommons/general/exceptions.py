from enum import Enum


class MessageDisplayType(Enum):
    """
    An enum representing the different ways in which a message can be displayed to the user.
    """
    TOASTER_SUCCESS = 0
    TOASTER_INFO = 1
    TOASTER_WARNING = 2
    TOASTER_ERROR = 3
    OK_DIALOG = 4
    DISPLAY_INFO = 5
    DISPLAY_WARNING = 6
    DISPLAY_ERROR = 7


# FR-46064 - Initial port of PyWebhookUtils to sapiopycommons.
class SapioException(Exception):
    """
    A generic exception thrown by sapiopycommons methods. Typically caused by programmer error, but may also be from
    extremely edge case user errors. For expected user errors, use SapioUserErrorException.

    CommonsWebhookHandler's default behavior for this and any other exception that doesn't extend SapioException is
    to return a generic toaster message saying that an unexpected error has occurred.
    """
    pass


class SapioUserCancelledException(SapioException):
    """
    An exception thrown when the user cancels a client callback.

    CommonsWebhookHandler's default behavior is to simply end the webhook session with a true result without logging
    the exception.
    """
    pass


class SapioDialogTimeoutException(SapioException):
    """
    An exception thrown when the user leaves a client callback open for too long.

    CommonsWebhookHandler's default behavior is to display an OK popup notifying the user that the dialog has timed out.
    """
    pass


class DisplayableException(SapioException):
    """
    A generic exception that promises to return a user-friendly message explaining the error that should be displayed to
    the user. Note that it is up to whichever class that catches this exception to actually display the message.
    """
    msg: str
    display_type: MessageDisplayType | None
    title: str | None

    def __init__(self, msg: str, display_type: MessageDisplayType | None = None, title: str | None = None):
        """
        :param msg: The message that should be displayed to the user.
        :param display_type: The manner in which the message should be displayed. If None, then the display type should
            be controlled by the class that catches this exception.
        :param title: If the display type is able to have a title, this is the title that will be displayed. If None,
            then the title should be controlled by the class that catches this exception.
        """
        self.msg = msg
        self.display_type = display_type
        self.title = title


class SapioUserErrorException(DisplayableException):
    """
    An exception caused by user error (e.g. user provided a CSV when an XLSX was expected), which promises to return a
    user-friendly message explaining the error that should be displayed to the user.

    CommonsWebhookHandler's default behavior is to return the error message in a toaster popup.
    """
    pass


class SapioCriticalErrorException(DisplayableException):
    """
    A critical exception caused by user error, which promises to return a user-friendly message explaining the error
    that should be displayed to the user.

    CommonsWebhookHandler's default behavior is to return the error message in a display_error callback.
    """
    pass
