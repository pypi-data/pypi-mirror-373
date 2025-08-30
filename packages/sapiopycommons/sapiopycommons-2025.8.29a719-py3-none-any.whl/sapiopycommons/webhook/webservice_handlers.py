import sys
import traceback
from abc import abstractmethod, ABC
from base64 import b64decode
from logging import Logger
from typing import Any, Mapping

from flask import request, Response, Request
from sapiopylib.rest.DataRecordManagerService import DataRecordManager
from sapiopylib.rest.User import SapioUser
from sapiopylib.rest.WebhookService import AbstractWebhookHandler
from sapiopylib.rest.utils.DataTypeCacheManager import DataTypeCacheManager
from sapiopylib.rest.utils.recordmodel.RecordModelManager import RecordModelManager, RecordModelInstanceManager, \
    RecordModelRelationshipManager
from sapiopylib.rest.utils.recordmodel.ancestry import RecordModelAncestorManager
from werkzeug.datastructures import Headers
from werkzeug.datastructures.structures import MultiDict
from werkzeug.exceptions import UnsupportedMediaType, BadRequest

from sapiopycommons.general.exceptions import SapioException
from sapiopycommons.recordmodel.record_handler import RecordHandler


class SapioWebserviceException(Exception):
    """
    An exception to be thrown by webservice classes when responding to a request with an error.
    """
    msg: str
    code: int

    def __init__(self, msg: str, code: int = 500):
        """
        :param msg: The message to return in the webservice response.
        :param code: The status code to return in the webservice response.
        """
        self.msg = msg
        self.code = code


class SapioWebserviceResult:
    """
    A result to be returned by AbstractWebserviceHandler endpoints, for sending information back to the caller.
    """
    message: str
    is_error: bool
    status_code: int
    payload: dict[str, Any]

    def __init__(self, message: str = "Success", status_code: int = 200, is_error: bool = False,
                 payload: dict[str, Any] | None = None):
        """
        :param message: A message to return to the sender describing what happened.
        :param status_code: An HTTP status code to return to the sender.
        :param is_error: Whether the webservice had an error during processing.
        :param payload: A payload of additional information to return to the sender.
        """
        self.message = message
        self.status_code = status_code
        self.is_error = is_error
        self.payload = payload
        if payload is None:
            self.payload = {}

    def to_json(self) -> dict[str, Any]:
        return {"message": self.message,
                "statusCode": self.status_code,
                "isError": self.is_error,
                "payload": self.payload}

    def to_result(self) -> tuple[dict[str, Any], int]:
        return self.to_json(), self.status_code


WebserviceResponse = SapioWebserviceResult | Response | tuple[dict[str, Any] | int]


class AbstractWebserviceHandler(AbstractWebhookHandler):
    """
    A base class for constructing POST webservice endpoints on your webhook server. These are endpoints that can be
    communicated with by external sources without needing to format the request in the webhook context format that
    normal webhook handlers expect.

    Since this extends AbstractWebhookHandler, you can still register endpoints from this class in the same way you
    would normal webhook endpoints.
    """
    request: Request

    def post(self) -> Response | tuple[dict[str, Any], int]:
        """
        Internal method to be executed to translate incoming POST requests.
        """
        # noinspection PyBroadException
        try:
            self.request = request
            try:
                raw_json = request.json
                headers = request.headers
                params = request.args
            except UnsupportedMediaType as e:
                return SapioWebserviceResult(str(e), 415, True).to_json(), 415
            except BadRequest as e:
                return SapioWebserviceResult(str(e), 400, True).to_json(), 400
            ret_val: WebserviceResponse = self.run(raw_json, headers, params)
            if isinstance(ret_val, SapioWebserviceResult):
                return ret_val.to_result()
            return ret_val
        except Exception:
            print('Error occurred while running webservice custom logic. See traceback.', file=sys.stderr)
            traceback.print_exc()
            return SapioWebserviceResult("Unexpected error occurred.", 500, True).to_json(), 500

    # noinspection PyMethodOverriding
    @abstractmethod
    def run(self, payload: Any, headers: Headers, params: MultiDict[str, str]) -> WebserviceResponse:
        """
        The execution details for this endpoint.

        :param payload: The JSON payload from the request. Usually a dictionary of strings to Any.
        :param headers: The headers from the request. Can be used like a dictionary.
        :param params: The URL parameters from the request.
        :return: A response object to send back to the requester.
        """
        pass

    def authenticate_user(self, headers: Mapping[str, str]) -> SapioUser:
        """
        Authenticate a user for making requests to a Sapio server using the provided headers. If no user can be
        authenticated, then an exception will be thrown.

        :param headers: The headers of the webservice request.
        :return: A SapioUser object used to make requests to a Sapio server as authorized by the headers.
        """
        # Get the system URL from the headers.
        if "System-URL" not in headers:
            raise SapioWebserviceException("No \"System-URL\" provided in headers.", 400)
        url: str = headers.get("System-URL")
        if not url.endswith("/webservice/api"):
            raise SapioWebserviceException(f"\"System-URL\" must be a webservice API URL for the target system: {url}", 400)

        # Get the login credentials from the headers.
        auth: str = headers.get("Authorization")
        if auth and auth.startswith("Basic "):
            credentials: list[str] = b64decode(auth.split("Basic ")[1]).decode().split(":", 1)
            user = self.basic_auth(url, credentials[0], credentials[1])
        elif auth and auth.startswith("Bearer "):
            user = self.bearer_token_auth(url, auth.split("Bearer ")[1])
        elif "X-API-TOKEN" in headers:
            user = self.api_token_auth(url, headers.get("X-API-TOKEN"))
        else:
            raise SapioWebserviceException(f"Unrecognized Authorization method.", 400)
        # Make a simple webservice call to confirm that the credentials are valid.
        try:
            # noinspection PyStatementEffect
            user.session_additional_data
        except Exception:
            if "Unauthorized (javax.ws.rs.NotAuthorizedException: Incorrect username or password.)" in traceback.format_exc():
                raise SapioWebserviceException("Unauthorized. Incorrect username or password.", 401)
            else:
                raise SapioWebserviceException("System-URL is invalid or user cannot be authenticated.", 401)
        return user

    def basic_auth(self, url: str, username: str, password: str) -> SapioUser:
        """
        :param url: The URL of the Sapio system that requests from this user will be sent to.
            Must end in /webservice/api
        :param username: The username to authenticate requests with.
        :param password: The password to authenticate requests with.
        :return: A SapioUser that will authenticate requests using basic auth.
        """
        return SapioUser(url, self.verify_sapio_cert, self.client_timeout_seconds, username=username, password=password)

    def api_token_auth(self, url: str, api_token: str) -> SapioUser:
        """
        :param url: The URL of the Sapio system that requests from this user will be sent to.
            Must end in /webservice/api
        :param api_token: The API token to authenticate requests with.
        :return: A SapioUser that will authenticate requests using an API token.
        """
        return SapioUser(url, self.verify_sapio_cert, self.client_timeout_seconds, api_token=api_token)

    def bearer_token_auth(self, url: str, bearer_token: str) -> SapioUser:
        """
        :param url: The URL of the Sapio system that requests from this user will be sent to.
            Must end in /webservice/api
        :param bearer_token: The bearer token to authenticate requests with.
        :return: A SapioUser that will authenticate requests using a bearer token.
        """
        return SapioUser(url, self.verify_sapio_cert, self.client_timeout_seconds, bearer_token=bearer_token)


class CommonsWebserviceHandler(AbstractWebserviceHandler, ABC):
    """
    A subclass of AbstractWebservicePostHandler that provides additional quality of life features, including
    authentication of a SapioUser from the request headers, initialization of various commonly used managers, and more.
    """
    logger: Logger

    user: SapioUser | None

    dr_man: DataRecordManager
    rec_man: RecordModelManager
    inst_man: RecordModelInstanceManager
    rel_man: RecordModelRelationshipManager
    an_man: RecordModelAncestorManager

    dt_cache: DataTypeCacheManager
    rec_handler: RecordHandler

    def run(self, payload: Any, headers: Headers, params: MultiDict[str, str]) -> WebserviceResponse:
        try:
            self.initialize(headers)
            result = self.execute(self.user, payload, headers, params)
            if result is None:
                raise SapioException("Your execute function returned a None result! Don't forget your return statement!")
            return result
        except SapioWebserviceException as e:
            return self.handle_webservice_exception(e)
        except Exception as e:
            return self.handle_unexpected_exception(e)

    def initialize(self, headers: Headers) -> None:
        """
        A function that can be optionally overridden by your classes to initialize additional instance variables,
        or set up whatever else you wish to set up before the execute function is ran. Default behavior initializes a
        SapioUser and various manager classes to make requests from.
        """
        self.user = None
        self.user = self.authenticate_user(headers)

        self.logger = self.user.logger

        self.dr_man = DataRecordManager(self.user)
        self.rec_man = RecordModelManager(self.user)
        self.inst_man = self.rec_man.instance_manager
        self.rel_man = self.rec_man.relationship_manager
        self.an_man = RecordModelAncestorManager(self.rec_man)

        self.dt_cache = DataTypeCacheManager(self.user)
        self.rec_handler = RecordHandler(self.user)

    @abstractmethod
    def execute(self, user: SapioUser, payload: Any, headers: Headers, params: MultiDict[str, str]) \
            -> SapioWebserviceResult:
        """
        The execution details for this endpoint.

        :param user: The SapioUser object authenticated from the request headers.
        :param payload: The JSON payload from the request. Usually a dictionary of strings to Any.
        :param headers: The headers from the request. Can be used like a dictionary.
        :param params: The URL parameters from the request.
        :return: A response object to send back to the requester.
        """
        pass

    def handle_webservice_exception(self, e: SapioWebserviceException) -> WebserviceResponse:
        """
        Handle a generic exception which isn't one of the handled Sapio exceptions.

        Default behavior returns a webservice result with the message and error code of the webservice exception.
        Additionally, the stack trace of the exception that was thrown is logged to the webhook server.

        :param e: The exception that was raised.
        :return: A webservice result to return to the requester.
        """
        result: WebserviceResponse | None = self.handle_any_exception(e)
        if result is not None:
            return result
        msg: str = traceback.format_exc()
        self.log_error(msg)
        return SapioWebserviceResult(e.msg, e.code, True)

    def handle_unexpected_exception(self, e: Exception) -> WebserviceResponse:
        """
        Handle a generic exception which isn't one of the handled Sapio exceptions.

        Default behavior returns a 500 code result with a generic error message informing the user to contact Sapio
        support. Additionally, the stack trace of the exception that was thrown is logged to the webhook server.

        :param e: The exception that was raised.
        :return: A webservice result to return to the requester.
        """
        result: SapioWebserviceResult | None = self.handle_any_exception(e)
        if result is not None:
            return result
        msg: str = traceback.format_exc()
        self.log_error(msg)
        return SapioWebserviceResult("Unexpected error occurred during webservice execution. "
                                     "Please contact Sapio support.", 500, True)

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def handle_any_exception(self, e: Exception) -> WebserviceResponse | None:
        """
        An exception handler which runs regardless of the type of exception that was raised. Can be used to "rollback"
        the client if an error occurs. Default behavior does nothing and returns None.

        :param e: The exception that was raised.
        :return: An optional response to the caller. May return a custom message to the client that wouldn't have been
            sent by one of the normal exception handlers, or may return None if no result needs returned. If a result is
            returned, then the default behavior of other exception handlers is skipped.
        """
        return None

    def log_info(self, msg: str) -> None:
        """
        Write an info message to the webhook server log. Log destination is stdout.
        """
        # If there's no user, then there's no logger.
        if self.user:
            self.logger.info(msg)

    def log_error(self, msg: str) -> None:
        """
        Write an error message to the webhook server log. Log destination is stderr.
        """
        # If there's no user, then there's no logger.
        if self.user:
            self.logger.error(msg)
