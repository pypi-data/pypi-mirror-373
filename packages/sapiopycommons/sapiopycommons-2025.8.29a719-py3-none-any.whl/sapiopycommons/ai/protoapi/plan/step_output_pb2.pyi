from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StepJsonSingletonItemPbo(_message.Message):
    __slots__ = ("item",)
    ITEM_FIELD_NUMBER: _ClassVar[int]
    item: str
    def __init__(self, item: _Optional[str] = ...) -> None: ...

class StepTextSingletonItemPbo(_message.Message):
    __slots__ = ("item",)
    ITEM_FIELD_NUMBER: _ClassVar[int]
    item: str
    def __init__(self, item: _Optional[str] = ...) -> None: ...

class StepCsvSingletonItemPbo(_message.Message):
    __slots__ = ("cells",)
    CELLS_FIELD_NUMBER: _ClassVar[int]
    cells: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, cells: _Optional[_Iterable[str]] = ...) -> None: ...

class StepBinarySingletonItemPbo(_message.Message):
    __slots__ = ("item",)
    ITEM_FIELD_NUMBER: _ClassVar[int]
    item: bytes
    def __init__(self, item: _Optional[bytes] = ...) -> None: ...

class StepSingletonItemPbo(_message.Message):
    __slots__ = ("json_singleton", "text_singleton", "csv_singleton", "binary_singleton")
    JSON_SINGLETON_FIELD_NUMBER: _ClassVar[int]
    TEXT_SINGLETON_FIELD_NUMBER: _ClassVar[int]
    CSV_SINGLETON_FIELD_NUMBER: _ClassVar[int]
    BINARY_SINGLETON_FIELD_NUMBER: _ClassVar[int]
    json_singleton: StepJsonSingletonItemPbo
    text_singleton: StepTextSingletonItemPbo
    csv_singleton: StepCsvSingletonItemPbo
    binary_singleton: StepBinarySingletonItemPbo
    def __init__(self, json_singleton: _Optional[_Union[StepJsonSingletonItemPbo, _Mapping]] = ..., text_singleton: _Optional[_Union[StepTextSingletonItemPbo, _Mapping]] = ..., csv_singleton: _Optional[_Union[StepCsvSingletonItemPbo, _Mapping]] = ..., binary_singleton: _Optional[_Union[StepBinarySingletonItemPbo, _Mapping]] = ...) -> None: ...
