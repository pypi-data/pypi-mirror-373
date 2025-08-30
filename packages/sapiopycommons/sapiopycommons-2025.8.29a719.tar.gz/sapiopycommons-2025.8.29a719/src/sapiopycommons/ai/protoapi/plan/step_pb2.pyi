from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StepIoInfoPbo(_message.Message):
    __slots__ = ("step_io_number", "content_type", "io_name")
    STEP_IO_NUMBER_FIELD_NUMBER: _ClassVar[int]
    CONTENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    IO_NAME_FIELD_NUMBER: _ClassVar[int]
    step_io_number: int
    content_type: str
    io_name: str
    def __init__(self, step_io_number: _Optional[int] = ..., content_type: _Optional[str] = ..., io_name: _Optional[str] = ...) -> None: ...

class StepIoDetailsPbo(_message.Message):
    __slots__ = ("step_io_info", "description", "example", "validation")
    STEP_IO_INFO_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    EXAMPLE_FIELD_NUMBER: _ClassVar[int]
    VALIDATION_FIELD_NUMBER: _ClassVar[int]
    step_io_info: StepIoInfoPbo
    description: str
    example: str
    validation: str
    def __init__(self, step_io_info: _Optional[_Union[StepIoInfoPbo, _Mapping]] = ..., description: _Optional[str] = ..., example: _Optional[str] = ..., validation: _Optional[str] = ...) -> None: ...

class StepInputDetailsPbo(_message.Message):
    __slots__ = ("step_io_details", "paging_supported", "max_entries")
    STEP_IO_DETAILS_FIELD_NUMBER: _ClassVar[int]
    PAGING_SUPPORTED_FIELD_NUMBER: _ClassVar[int]
    MAX_ENTRIES_FIELD_NUMBER: _ClassVar[int]
    step_io_details: StepIoDetailsPbo
    paging_supported: bool
    max_entries: int
    def __init__(self, step_io_details: _Optional[_Union[StepIoDetailsPbo, _Mapping]] = ..., paging_supported: bool = ..., max_entries: _Optional[int] = ...) -> None: ...

class StepOutputDetailsPbo(_message.Message):
    __slots__ = ("step_io_details",)
    STEP_IO_DETAILS_FIELD_NUMBER: _ClassVar[int]
    step_io_details: StepIoDetailsPbo
    def __init__(self, step_io_details: _Optional[_Union[StepIoDetailsPbo, _Mapping]] = ...) -> None: ...
