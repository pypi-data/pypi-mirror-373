from sapiopycommons.ai.protoapi.session import sapio_conn_info_pb2 as _sapio_conn_info_pb2
from sapiopycommons.ai.protoapi.plan.item import item_container_pb2 as _item_container_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union
from sapiopycommons.ai.protoapi.session.sapio_conn_info_pb2 import SapioConnectionInfoPbo as SapioConnectionInfoPbo
from sapiopycommons.ai.protoapi.session.sapio_conn_info_pb2 import SapioUserSecretTypePbo as SapioUserSecretTypePbo
from sapiopycommons.ai.protoapi.plan.item.item_container_pb2 import ContentTypePbo as ContentTypePbo
from sapiopycommons.ai.protoapi.plan.item.item_container_pb2 import StepCsvHeaderRowPbo as StepCsvHeaderRowPbo
from sapiopycommons.ai.protoapi.plan.item.item_container_pb2 import StepCsvRowPbo as StepCsvRowPbo
from sapiopycommons.ai.protoapi.plan.item.item_container_pb2 import StepCsvContainerPbo as StepCsvContainerPbo
from sapiopycommons.ai.protoapi.plan.item.item_container_pb2 import StepJsonContainerPbo as StepJsonContainerPbo
from sapiopycommons.ai.protoapi.plan.item.item_container_pb2 import StepTextContainerPbo as StepTextContainerPbo
from sapiopycommons.ai.protoapi.plan.item.item_container_pb2 import StepBinaryContainerPbo as StepBinaryContainerPbo
from sapiopycommons.ai.protoapi.plan.item.item_container_pb2 import StepImageContainerPbo as StepImageContainerPbo
from sapiopycommons.ai.protoapi.plan.item.item_container_pb2 import StepItemContainerPbo as StepItemContainerPbo
from sapiopycommons.ai.protoapi.plan.item.item_container_pb2 import DataTypePbo as DataTypePbo

DESCRIPTOR: _descriptor.FileDescriptor
SESSION_TOKEN: _sapio_conn_info_pb2.SapioUserSecretTypePbo
PASSWORD: _sapio_conn_info_pb2.SapioUserSecretTypePbo
BINARY: _item_container_pb2.DataTypePbo
JSON: _item_container_pb2.DataTypePbo
CSV: _item_container_pb2.DataTypePbo
TEXT: _item_container_pb2.DataTypePbo
IMAGE: _item_container_pb2.DataTypePbo

class ConverterDetailsRequestPbo(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ContentTypePairPbo(_message.Message):
    __slots__ = ("input_content_type", "output_content_type", "converter_name")
    INPUT_CONTENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_CONTENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    CONVERTER_NAME_FIELD_NUMBER: _ClassVar[int]
    input_content_type: _item_container_pb2.ContentTypePbo
    output_content_type: _item_container_pb2.ContentTypePbo
    converter_name: str
    def __init__(self, input_content_type: _Optional[_Union[_item_container_pb2.ContentTypePbo, _Mapping]] = ..., output_content_type: _Optional[_Union[_item_container_pb2.ContentTypePbo, _Mapping]] = ..., converter_name: _Optional[str] = ...) -> None: ...

class ConverterDetailsResponsePbo(_message.Message):
    __slots__ = ("supported_types", "service_name")
    SUPPORTED_TYPES_FIELD_NUMBER: _ClassVar[int]
    SERVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    supported_types: _containers.RepeatedCompositeFieldContainer[ContentTypePairPbo]
    service_name: str
    def __init__(self, supported_types: _Optional[_Iterable[_Union[ContentTypePairPbo, _Mapping]]] = ..., service_name: _Optional[str] = ...) -> None: ...

class ConvertRequestPbo(_message.Message):
    __slots__ = ("item_container", "target_content_type")
    ITEM_CONTAINER_FIELD_NUMBER: _ClassVar[int]
    TARGET_CONTENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    item_container: _item_container_pb2.StepItemContainerPbo
    target_content_type: _item_container_pb2.ContentTypePbo
    def __init__(self, item_container: _Optional[_Union[_item_container_pb2.StepItemContainerPbo, _Mapping]] = ..., target_content_type: _Optional[_Union[_item_container_pb2.ContentTypePbo, _Mapping]] = ...) -> None: ...

class ConvertResponsePbo(_message.Message):
    __slots__ = ("item_container",)
    ITEM_CONTAINER_FIELD_NUMBER: _ClassVar[int]
    item_container: _item_container_pb2.StepItemContainerPbo
    def __init__(self, item_container: _Optional[_Union[_item_container_pb2.StepItemContainerPbo, _Mapping]] = ...) -> None: ...
