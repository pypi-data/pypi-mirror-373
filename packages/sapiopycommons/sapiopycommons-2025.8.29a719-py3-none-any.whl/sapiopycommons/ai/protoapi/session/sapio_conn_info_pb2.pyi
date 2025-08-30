from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SapioUserSecretTypePbo(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SESSION_TOKEN: _ClassVar[SapioUserSecretTypePbo]
    PASSWORD: _ClassVar[SapioUserSecretTypePbo]
SESSION_TOKEN: SapioUserSecretTypePbo
PASSWORD: SapioUserSecretTypePbo

class SapioConnectionInfoPbo(_message.Message):
    __slots__ = ("webservice_url", "rmi_host", "rmi_port", "app_guid", "username", "secret_type", "secret")
    WEBSERVICE_URL_FIELD_NUMBER: _ClassVar[int]
    RMI_HOST_FIELD_NUMBER: _ClassVar[int]
    RMI_PORT_FIELD_NUMBER: _ClassVar[int]
    APP_GUID_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    SECRET_TYPE_FIELD_NUMBER: _ClassVar[int]
    SECRET_FIELD_NUMBER: _ClassVar[int]
    webservice_url: str
    rmi_host: _containers.RepeatedScalarFieldContainer[str]
    rmi_port: int
    app_guid: str
    username: str
    secret_type: SapioUserSecretTypePbo
    secret: str
    def __init__(self, webservice_url: _Optional[str] = ..., rmi_host: _Optional[_Iterable[str]] = ..., rmi_port: _Optional[int] = ..., app_guid: _Optional[str] = ..., username: _Optional[str] = ..., secret_type: _Optional[_Union[SapioUserSecretTypePbo, str]] = ..., secret: _Optional[str] = ...) -> None: ...
