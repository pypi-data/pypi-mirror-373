from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DataTypePbo(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    BINARY: _ClassVar[DataTypePbo]
    JSON: _ClassVar[DataTypePbo]
    CSV: _ClassVar[DataTypePbo]
    TEXT: _ClassVar[DataTypePbo]
    IMAGE: _ClassVar[DataTypePbo]
BINARY: DataTypePbo
JSON: DataTypePbo
CSV: DataTypePbo
TEXT: DataTypePbo
IMAGE: DataTypePbo

class ContentTypePbo(_message.Message):
    __slots__ = ("name", "extensions")
    NAME_FIELD_NUMBER: _ClassVar[int]
    EXTENSIONS_FIELD_NUMBER: _ClassVar[int]
    name: str
    extensions: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, name: _Optional[str] = ..., extensions: _Optional[_Iterable[str]] = ...) -> None: ...

class StepCsvHeaderRowPbo(_message.Message):
    __slots__ = ("cells",)
    CELLS_FIELD_NUMBER: _ClassVar[int]
    cells: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, cells: _Optional[_Iterable[str]] = ...) -> None: ...

class StepCsvRowPbo(_message.Message):
    __slots__ = ("cells",)
    CELLS_FIELD_NUMBER: _ClassVar[int]
    cells: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, cells: _Optional[_Iterable[str]] = ...) -> None: ...

class StepCsvContainerPbo(_message.Message):
    __slots__ = ("header", "items")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    header: StepCsvHeaderRowPbo
    items: _containers.RepeatedCompositeFieldContainer[StepCsvRowPbo]
    def __init__(self, header: _Optional[_Union[StepCsvHeaderRowPbo, _Mapping]] = ..., items: _Optional[_Iterable[_Union[StepCsvRowPbo, _Mapping]]] = ...) -> None: ...

class StepJsonContainerPbo(_message.Message):
    __slots__ = ("items",)
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, items: _Optional[_Iterable[str]] = ...) -> None: ...

class StepTextContainerPbo(_message.Message):
    __slots__ = ("items",)
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, items: _Optional[_Iterable[str]] = ...) -> None: ...

class StepBinaryContainerPbo(_message.Message):
    __slots__ = ("items",)
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    items: _containers.RepeatedScalarFieldContainer[bytes]
    def __init__(self, items: _Optional[_Iterable[bytes]] = ...) -> None: ...

class StepImageContainerPbo(_message.Message):
    __slots__ = ("image_format", "items")
    IMAGE_FORMAT_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    image_format: str
    items: _containers.RepeatedScalarFieldContainer[bytes]
    def __init__(self, image_format: _Optional[str] = ..., items: _Optional[_Iterable[bytes]] = ...) -> None: ...

class StepItemContainerPbo(_message.Message):
    __slots__ = ("content_type", "container_name", "binary_container", "csv_container", "json_container", "text_container")
    CONTENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    CONTAINER_NAME_FIELD_NUMBER: _ClassVar[int]
    BINARY_CONTAINER_FIELD_NUMBER: _ClassVar[int]
    CSV_CONTAINER_FIELD_NUMBER: _ClassVar[int]
    JSON_CONTAINER_FIELD_NUMBER: _ClassVar[int]
    TEXT_CONTAINER_FIELD_NUMBER: _ClassVar[int]
    content_type: ContentTypePbo
    container_name: str
    binary_container: StepBinaryContainerPbo
    csv_container: StepCsvContainerPbo
    json_container: StepJsonContainerPbo
    text_container: StepTextContainerPbo
    def __init__(self, content_type: _Optional[_Union[ContentTypePbo, _Mapping]] = ..., container_name: _Optional[str] = ..., binary_container: _Optional[_Union[StepBinaryContainerPbo, _Mapping]] = ..., csv_container: _Optional[_Union[StepCsvContainerPbo, _Mapping]] = ..., json_container: _Optional[_Union[StepJsonContainerPbo, _Mapping]] = ..., text_container: _Optional[_Union[StepTextContainerPbo, _Mapping]] = ...) -> None: ...
