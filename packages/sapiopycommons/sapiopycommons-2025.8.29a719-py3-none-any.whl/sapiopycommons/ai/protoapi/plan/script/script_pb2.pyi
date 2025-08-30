from sapiopycommons.ai.protoapi.plan.tool import entry_pb2 as _entry_pb2
from sapiopycommons.ai.protoapi.plan.item import item_container_pb2 as _item_container_pb2
from sapiopycommons.ai.protoapi.plan import step_pb2 as _step_pb2
from sapiopycommons.ai.protoapi.session import sapio_conn_info_pb2 as _sapio_conn_info_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union
from sapiopycommons.ai.protoapi.plan.tool.entry_pb2 import StepInputBatchPbo as StepInputBatchPbo
from sapiopycommons.ai.protoapi.plan.tool.entry_pb2 import StepOutputBatchPbo as StepOutputBatchPbo
from sapiopycommons.ai.protoapi.plan.step_pb2 import StepIoInfoPbo as StepIoInfoPbo
from sapiopycommons.ai.protoapi.plan.step_pb2 import StepIoDetailsPbo as StepIoDetailsPbo
from sapiopycommons.ai.protoapi.plan.step_pb2 import StepInputDetailsPbo as StepInputDetailsPbo
from sapiopycommons.ai.protoapi.plan.step_pb2 import StepOutputDetailsPbo as StepOutputDetailsPbo
from sapiopycommons.ai.protoapi.session.sapio_conn_info_pb2 import SapioConnectionInfoPbo as SapioConnectionInfoPbo
from sapiopycommons.ai.protoapi.session.sapio_conn_info_pb2 import SapioUserSecretTypePbo as SapioUserSecretTypePbo

DESCRIPTOR: _descriptor.FileDescriptor
SESSION_TOKEN: _sapio_conn_info_pb2.SapioUserSecretTypePbo
PASSWORD: _sapio_conn_info_pb2.SapioUserSecretTypePbo

class JobStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PENDING: _ClassVar[JobStatus]
    RUNNING: _ClassVar[JobStatus]
    COMPLETED: _ClassVar[JobStatus]
    FAILED: _ClassVar[JobStatus]
PENDING: JobStatus
RUNNING: JobStatus
COMPLETED: JobStatus
FAILED: JobStatus

class ScriptFileContentsPbo(_message.Message):
    __slots__ = ("file_name", "file_contents")
    FILE_NAME_FIELD_NUMBER: _ClassVar[int]
    FILE_CONTENTS_FIELD_NUMBER: _ClassVar[int]
    file_name: str
    file_contents: bytes
    def __init__(self, file_name: _Optional[str] = ..., file_contents: _Optional[bytes] = ...) -> None: ...

class CreateScriptJobRequestPbo(_message.Message):
    __slots__ = ("sapio_user", "script_language", "plan_instance_id", "step_instance_id", "invocation_id", "input_configs", "output_configs", "script", "timeout", "max_memory_mb", "working_directory", "input_files", "download_file_names", "input")
    SAPIO_USER_FIELD_NUMBER: _ClassVar[int]
    SCRIPT_LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    PLAN_INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    STEP_INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    INVOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    INPUT_CONFIGS_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_CONFIGS_FIELD_NUMBER: _ClassVar[int]
    SCRIPT_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    MAX_MEMORY_MB_FIELD_NUMBER: _ClassVar[int]
    WORKING_DIRECTORY_FIELD_NUMBER: _ClassVar[int]
    INPUT_FILES_FIELD_NUMBER: _ClassVar[int]
    DOWNLOAD_FILE_NAMES_FIELD_NUMBER: _ClassVar[int]
    INPUT_FIELD_NUMBER: _ClassVar[int]
    sapio_user: _sapio_conn_info_pb2.SapioConnectionInfoPbo
    script_language: str
    plan_instance_id: int
    step_instance_id: int
    invocation_id: int
    input_configs: _containers.RepeatedCompositeFieldContainer[_step_pb2.StepIoInfoPbo]
    output_configs: _containers.RepeatedCompositeFieldContainer[_step_pb2.StepIoInfoPbo]
    script: str
    timeout: int
    max_memory_mb: int
    working_directory: str
    input_files: _containers.RepeatedCompositeFieldContainer[ScriptFileContentsPbo]
    download_file_names: _containers.RepeatedScalarFieldContainer[str]
    input: _containers.RepeatedCompositeFieldContainer[_entry_pb2.StepInputBatchPbo]
    def __init__(self, sapio_user: _Optional[_Union[_sapio_conn_info_pb2.SapioConnectionInfoPbo, _Mapping]] = ..., script_language: _Optional[str] = ..., plan_instance_id: _Optional[int] = ..., step_instance_id: _Optional[int] = ..., invocation_id: _Optional[int] = ..., input_configs: _Optional[_Iterable[_Union[_step_pb2.StepIoInfoPbo, _Mapping]]] = ..., output_configs: _Optional[_Iterable[_Union[_step_pb2.StepIoInfoPbo, _Mapping]]] = ..., script: _Optional[str] = ..., timeout: _Optional[int] = ..., max_memory_mb: _Optional[int] = ..., working_directory: _Optional[str] = ..., input_files: _Optional[_Iterable[_Union[ScriptFileContentsPbo, _Mapping]]] = ..., download_file_names: _Optional[_Iterable[str]] = ..., input: _Optional[_Iterable[_Union[_entry_pb2.StepInputBatchPbo, _Mapping]]] = ...) -> None: ...

class CreateScriptJobResponsePbo(_message.Message):
    __slots__ = ("job_id",)
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    def __init__(self, job_id: _Optional[str] = ...) -> None: ...

class GetJobRequestPbo(_message.Message):
    __slots__ = ("job_id", "log_offset", "download_files")
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    LOG_OFFSET_FIELD_NUMBER: _ClassVar[int]
    DOWNLOAD_FILES_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    log_offset: int
    download_files: bool
    def __init__(self, job_id: _Optional[str] = ..., log_offset: _Optional[int] = ..., download_files: bool = ...) -> None: ...

class GetJobResponsePbo(_message.Message):
    __slots__ = ("status", "log", "exception", "output_files", "output")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LOG_FIELD_NUMBER: _ClassVar[int]
    EXCEPTION_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FILES_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    status: JobStatus
    log: str
    exception: str
    output_files: _containers.RepeatedCompositeFieldContainer[ScriptFileContentsPbo]
    output: _containers.RepeatedCompositeFieldContainer[_entry_pb2.StepOutputBatchPbo]
    def __init__(self, status: _Optional[_Union[JobStatus, str]] = ..., log: _Optional[str] = ..., exception: _Optional[str] = ..., output_files: _Optional[_Iterable[_Union[ScriptFileContentsPbo, _Mapping]]] = ..., output: _Optional[_Iterable[_Union[_entry_pb2.StepOutputBatchPbo, _Mapping]]] = ...) -> None: ...
