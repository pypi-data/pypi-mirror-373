from sapiopycommons.ai.protoapi.plan.item import item_container_pb2 as _item_container_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union
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
BINARY: _item_container_pb2.DataTypePbo
JSON: _item_container_pb2.DataTypePbo
CSV: _item_container_pb2.DataTypePbo
TEXT: _item_container_pb2.DataTypePbo
IMAGE: _item_container_pb2.DataTypePbo

class StepInputBatchPbo(_message.Message):
    __slots__ = ("is_partial", "item_container")
    IS_PARTIAL_FIELD_NUMBER: _ClassVar[int]
    ITEM_CONTAINER_FIELD_NUMBER: _ClassVar[int]
    is_partial: bool
    item_container: _item_container_pb2.StepItemContainerPbo
    def __init__(self, is_partial: bool = ..., item_container: _Optional[_Union[_item_container_pb2.StepItemContainerPbo, _Mapping]] = ...) -> None: ...

class StepOutputBatchPbo(_message.Message):
    __slots__ = ("item_container",)
    ITEM_CONTAINER_FIELD_NUMBER: _ClassVar[int]
    item_container: _item_container_pb2.StepItemContainerPbo
    def __init__(self, item_container: _Optional[_Union[_item_container_pb2.StepItemContainerPbo, _Mapping]] = ...) -> None: ...
