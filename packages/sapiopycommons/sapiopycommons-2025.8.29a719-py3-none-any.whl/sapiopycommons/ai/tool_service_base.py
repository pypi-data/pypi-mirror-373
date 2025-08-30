from __future__ import annotations

import base64
import io
import json
import logging
import re
import traceback
from abc import abstractmethod, ABC
from logging import Logger
from typing import Any, Iterable, Sequence, Mapping

from grpc import ServicerContext
from sapiopylib.rest.User import SapioUser, ensure_logger_initialized
from sapiopylib.rest.pojo.datatype.FieldDefinition import AbstractVeloxFieldDefinition

from sapiopycommons.ai.protoapi.fielddefinitions.fields_pb2 import FieldValueMapPbo, FieldValuePbo
from sapiopycommons.ai.protoapi.fielddefinitions.velox_field_def_pb2 import VeloxFieldDefPbo, FieldTypePbo, \
    SelectionPropertiesPbo, IntegerPropertiesPbo, DoublePropertiesPbo, BooleanPropertiesPbo, StringPropertiesPbo
from sapiopycommons.ai.protoapi.plan.item.item_container_pb2 import ContentTypePbo
from sapiopycommons.ai.protoapi.plan.tool.entry_pb2 import StepOutputBatchPbo, StepItemContainerPbo, \
    StepBinaryContainerPbo, StepCsvContainerPbo, StepCsvHeaderRowPbo, StepCsvRowPbo, StepJsonContainerPbo, \
    StepTextContainerPbo, StepInputBatchPbo
from sapiopycommons.ai.protoapi.plan.tool.tool_pb2 import ToolDetailsRequestPbo, ToolDetailsResponsePbo, \
    ToolDetailsPbo, ProcessStepRequestPbo, ProcessStepResponsePbo, ToolOutputDetailsPbo, ToolIoConfigBasePbo, \
    ToolInputDetailsPbo, ExampleContainerPbo, ProcessStepResponseStatusPbo
from sapiopycommons.ai.protoapi.plan.tool.tool_pb2_grpc import ToolServiceServicer
from sapiopycommons.ai.protoapi.session.sapio_conn_info_pb2 import SapioUserSecretTypePbo, SapioConnectionInfoPbo
from sapiopycommons.ai.protobuf_utils import ProtobufUtils
from sapiopycommons.ai.test_client import ContainerType
from sapiopycommons.files.file_util import FileUtil
from sapiopycommons.general.aliases import FieldMap, FieldValue


# FR-47422: Created classes.
class SapioToolResult(ABC):
    """
    A class representing a result from a Sapio tool. Instantiate one of the subclasses to create a result object.
    """

    @abstractmethod
    def to_proto(self) -> StepOutputBatchPbo | list[FieldValueMapPbo]:
        """
        Convert this SapioToolResult object to a StepOutputBatchPbo or list of FieldValueMapPbo proto objects.
        """
        pass


class BinaryResult(SapioToolResult):
    """
    A class representing binary results from a Sapio tool.
    """
    binary_data: list[bytes]
    content_type: str
    file_extensions: list[str]
    name: str

    def __init__(self, binary_data: list[bytes], content_type: str = "binary", file_extensions: list[str] = None,
                 name: str | None = None):
        """
        :param binary_data: The binary data as a list of bytes.
        :param content_type: The content type of the data.
        :param file_extensions: A list of file extensions that this binary data can be saved as.
        :param name: An optional identifying name for this result that will be accessible to the next tool.
        """
        self.binary_data = binary_data
        self.content_type = content_type
        self.file_extensions = file_extensions if file_extensions else []
        self.name = name

    def to_proto(self) -> StepOutputBatchPbo | list[FieldValueMapPbo]:
        return StepOutputBatchPbo(
            item_container=StepItemContainerPbo(
                content_type=ContentTypePbo(name=self.content_type, extensions=self.file_extensions),
                container_name=self.name,
                binary_container=StepBinaryContainerPbo(items=self.binary_data)
            )
        )


class CsvResult(SapioToolResult):
    """
    A class representing CSV results from a Sapio tool.
    """
    csv_data: list[dict[str, Any]]
    content_type: str
    file_extensions: list[str]
    name: str

    def __init__(self, csv_data: list[dict[str, Any]], content_type: str = "csv", file_extensions: list[str] = None,
                 name: str | None = None):
        """
        :param csv_data: The list of CSV data results, provided as a list of dictionaries of column name to value.
        :param content_type: The content type of the data.
        :param file_extensions: A list of file extensions that this binary data can be saved as.
        :param name: An optional identifying name for this result that will be accessible to the next tool.
        """
        self.csv_data = csv_data
        self.content_type = content_type
        self.file_extensions = file_extensions if file_extensions else ["csv"]
        self.name = name

    def to_proto(self) -> StepOutputBatchPbo | list[FieldValueMapPbo]:
        return StepOutputBatchPbo(
            item_container=StepItemContainerPbo(
                content_type=ContentTypePbo(name=self.content_type, extensions=self.file_extensions),
                container_name=self.name,
                csv_container=StepCsvContainerPbo(
                    header=StepCsvHeaderRowPbo(cells=self.csv_data[0].keys()),
                    items=[StepCsvRowPbo(cells=[str(x) for x in row.values()]) for row in self.csv_data]
                )
            ) if self.csv_data else None
        )


class FieldMapResult(SapioToolResult):
    """
    A class representing field map results from a Sapio tool.
    """
    field_maps: list[FieldMap]

    def __init__(self, field_maps: list[FieldMap]):
        """
        :param field_maps: A list of field maps, where each map is a dictionary of field names to values. Each entry
            will create a new data record in the system, so long as the tool definition specifies an output data type
            name.
        """
        self.field_maps = field_maps

    def to_proto(self) -> StepOutputBatchPbo | list[FieldValueMapPbo]:
        new_records: list[FieldValueMapPbo] = []
        for field_map in self.field_maps:
            fields: dict[str, FieldValuePbo] = {}
            for field, value in field_map.items():
                field_value = FieldValuePbo()
                if isinstance(value, str):
                    field_value.string_value = value
                elif isinstance(value, int):
                    field_value.int_value = value
                elif isinstance(value, float):
                    field_value.double_value = value
                elif isinstance(value, bool):
                    field_value.bool_value = value
                fields[field] = field_value
            new_records.append(FieldValueMapPbo(fields=fields))
        return new_records


class JsonResult(SapioToolResult):
    """
    A class representing JSON results from a Sapio tool.
    """
    json_data: list[Any]
    content_type: str
    file_extensions: list[str]
    name: str

    def __init__(self, json_data: list[Any], content_type: str = "json", file_extensions: list[str] = None,
                 name: str | None = None):
        """
        :param json_data: The list of JSON data results. Each entry in the list represents a separate JSON object.
            These entries must be able to be serialized to JSON using json.dumps().
        :param content_type: The content type of the data.
        :param file_extensions: A list of file extensions that this binary data can be saved as.
        :param name: An optional identifying name for this result that will be accessible to the next tool.
        """
        self.json_data = json_data
        self.content_type = content_type
        self.file_extensions = file_extensions if file_extensions else ["json"]
        self.name = name

    def to_proto(self) -> StepOutputBatchPbo | list[FieldValueMapPbo]:
        return StepOutputBatchPbo(
            item_container=StepItemContainerPbo(
                content_type=ContentTypePbo(name=self.content_type, extensions=self.file_extensions),
                container_name=self.name,
                json_container=StepJsonContainerPbo(items=[json.dumps(x) for x in self.json_data])
            )
        )


class TextResult(SapioToolResult):
    """
    A class representing text results from a Sapio tool.
    """
    text_data: list[str]
    content_type: str
    file_extensions: list[str]
    name: str

    def __init__(self, text_data: list[str], content_type: str = "text", file_extensions: list[str] = None,
                 name: str | None = None):
        """
        :param text_data: The text data as a list of strings.
        :param content_type: The content type of the data.
        :param file_extensions: A list of file extensions that this binary data can be saved as.
        :param name: An optional identifying name for this result that will be accessible to the next tool.
        """
        self.text_data = text_data
        self.content_type = content_type
        self.file_extensions = file_extensions if file_extensions else ["txt"]
        self.name = name

    def to_proto(self) -> StepOutputBatchPbo | list[FieldValueMapPbo]:
        return StepOutputBatchPbo(
            item_container=StepItemContainerPbo(
                content_type=ContentTypePbo(name=self.content_type, extensions=self.file_extensions),
                container_name=self.name,
                text_container=StepTextContainerPbo(items=self.text_data)
            )
        )


class ToolServiceBase(ToolServiceServicer, ABC):
    """
    A base class for implementing a tool service. Subclasses should implement the register_tools method to register
    their tools with the service.
    """
    def GetToolDetails(self, request: ToolDetailsRequestPbo, context: ServicerContext) -> ToolDetailsResponsePbo:
        try:
            # Get the tool details from the registered tools.
            details: list[ToolDetailsPbo] = []
            for tool in self.register_tools():
                details.append(tool().to_pbo())
            if not details:
                raise Exception("No tools registered with this service.")
            return ToolDetailsResponsePbo(tool_framework_version=self.tool_version(), tool_details=details)
        except Exception as e:
            # Woe to you if you somehow cause an exception to be raised when just initializing your tools.
            # There's no way to log this.
            print(f"CRITICAL ERROR: {e}")
            print(traceback.format_exc())
            return ToolDetailsResponsePbo()

    def ProcessData(self, request: ProcessStepRequestPbo, context: ServicerContext) -> ProcessStepResponsePbo:
        try:
            # Convert the SapioConnectionInfo proto object to a SapioUser object.
            user = self._create_user(request.sapio_user)
            # Get the tool results from the registered tool matching the request.
            success, msg, results, logs = self.run(user, request, context)
            # Convert the results to protobuf objects.
            output_data: list[StepOutputBatchPbo] = []
            new_records: list[FieldValueMapPbo] = []
            for result in results:
                data: StepOutputBatchPbo | list[FieldValueMapPbo] = result.to_proto()
                if isinstance(data, StepOutputBatchPbo):
                    output_data.append(data)
                else:
                    new_records.extend(data)
            # Return a ProcessStepResponse proto object containing the results to the caller.
            status = ProcessStepResponseStatusPbo.SUCCESS if success else ProcessStepResponseStatusPbo.FAILURE
            return ProcessStepResponsePbo(status=status, status_message=msg, output=output_data, log=logs,
                                          new_records=new_records)
        except Exception as e:
            # This try/except should never be needed, as the tool should handle its own exceptions, but better safe
            # than sorry.
            print(f"CRITICAL ERROR: {e}")
            print(traceback.format_exc())
            return ProcessStepResponsePbo(status=ProcessStepResponseStatusPbo.FAILURE,
                                          status_message=f"CRITICAL ERROR: {e}",
                                          log=[traceback.format_exc()])

    @staticmethod
    def _create_user(info: SapioConnectionInfoPbo, timeout_seconds: int = 60) -> SapioUser:
        """
        Create a SapioUser object from the given SapioConnectionInfo proto object.

        :param info: The SapioConnectionInfo proto object.
        :param timeout_seconds: The request timeout for calls made from this user object.
        """
        user = SapioUser(info.webservice_url, True, timeout_seconds, guid=info.app_guid)
        match info.secret_type:
            case SapioUserSecretTypePbo.SESSION_TOKEN:
                user.api_token = info.secret
            case SapioUserSecretTypePbo.PASSWORD:
                secret: str = info.secret
                if secret.startswith("Basic "):
                    secret = secret[6:]
                credentials: list[str] = base64.b64decode(secret).decode().split(":", 1)
                user.username = credentials[0]
                user.password = credentials[1]
            case _:
                raise Exception(f"Unexpected secret type: {info.secret_type}")
        return user

    @staticmethod
    def tool_version() -> int:
        """
        :return: The version of this set of tools.
        """
        return 1

    @abstractmethod
    def register_tools(self) -> list[type[ToolBase]]:
        """
        Register tool types with this service. Provided tools should implement the ToolBase class.

        :return: A list of tools to register to this service.
        """
        pass

    def run(self, user: SapioUser, request: ProcessStepRequestPbo, context: ServicerContext) \
            -> tuple[bool, str, list[SapioToolResult], list[str]]:
        """
        Execute a tool from this service.

        :param user: A user object that can be used to initialize manager classes using DataMgmtServer to query the
            system.
        :param request: The request object containing the input data.
        :param context: The gRPC context.
        :return: Whether or not the tool succeeded, the status message, the results of the tool, and any logs
            generated by the tool.
        """
        # Locate the tool named in the request.
        find_tool: str = request.tool_name
        registered_tools: dict[str, type[ToolBase]] = {t.name(): t for t in self.register_tools()}
        if find_tool not in registered_tools:
            # If the tool is not found, list all of the registered tools for this service so that the LLM can correct
            # the tool it is requesting.
            all_tool_names: str = "\n".join(registered_tools.keys())
            msg: str = (f"Tool \"{find_tool}\" not found in the registered tools for this service. The registered tools "
                        f"for this service are: \n{all_tool_names}")
            return False, msg, [], []

        # Instantiate the tool class.
        tool: ToolBase = registered_tools[find_tool]()
        try:
            # Setup the tool with details from the request.
            tool.setup(user, request, context)
            # Validate that the provided inputs match the tool's expected inputs.
            if len(request.input) != len(tool.input_configs):
                msg: str = f"Expected {len(tool.input_configs)} inputs for this tool, but got {len(request.input)} instead."
            else:
                msg: str = tool.validate_input()
            # If there is no error message, then the inputs are valid.
            success: bool = not bool(msg)
            # If this is a dry run, then provide the fixed dry run output.
            # Otherwise, if the inputs were successfully validated, then the tool is executed normally.
            results: list[SapioToolResult] = []
            if request.dry_run:
                results = tool.dry_run_output()
            elif success:
                results = tool.run(user)
                # Update the status message to reflect the successful execution of the tool.
                msg = f"{tool.name()} successfully completed."
            return success, msg, results, tool.logs
        except Exception as e:
            tool.log_exception("Exception occurred during tool execution.", e)
            return False, str(e), [], tool.logs


class ToolBase(ABC):
    """
    A base class for implementing a tool.
    """
    _name: str
    _description: str
    _data_type_name: str | None
    input_configs: list[ToolInputDetailsPbo]
    _input_container_types: list[ContainerType]
    output_configs: list[ToolOutputDetailsPbo]
    _output_container_types: list[ContainerType]
    config_fields: list[VeloxFieldDefPbo]

    logs: list[str]
    logger: Logger
    verbose_logging: bool

    user: SapioUser
    request: ProcessStepRequestPbo
    context: ServicerContext

    @staticmethod
    @abstractmethod
    def name() -> str:
        """
        :return: The name of the tool. This should be unique across all tools in the service.
        """
        pass

    @staticmethod
    @abstractmethod
    def description() -> str:
        """
        :return: A description of the tool.
        """
        pass

    @staticmethod
    def data_type_name() -> str | None:
        """
        :return: The name of the output data type of this tool, if applicable. When this tool returns
            FieldMapResult objects in its run method, this name will be used to set the data type of the output data.
        """
        return None

    def __init__(self):
        self._name = self.name()
        self._description = self.description()
        self._data_type_name = self.data_type_name()
        self.input_configs = []
        self._input_container_types = []
        self.output_configs = []
        self._output_container_types = []
        self.config_fields = []
        self.logs = []
        self.logger = logging.getLogger(f"ToolBase.{self._name}")
        ensure_logger_initialized(self.logger)

    def setup(self, user: SapioUser, request: ProcessStepRequestPbo, context: ServicerContext) -> None:
        """
        Setup the tool with the user, request, and context. This method can be overridden by subclasses to perform
        additional setup.

        :param user: A user object that can be used to initialize manager classes using DataMgmtServer to query the
            system.
        :param request: The request object containing the input data.
        :param context: The gRPC context.
        """
        self.user = user
        self.request = request
        self.context = context
        self.verbose_logging = request.verbose_logging

    def add_input(self, container_type: ContainerType, content_type: str, display_name: str, description: str,
                  structure_example: str | bytes | None = None, validation: str | None = None,
                  input_count: tuple[int, int] | None = None, is_paged: bool = False,
                  page_size: tuple[int, int] | None = None, max_request_bytes: int | None = None) -> None:
        """
        Add an input configuration to the tool. This determines how many inputs this tool will accept in the plan
        manager, as well as what those inputs are. The IO number of the input will be set to the current number of
        inputs. That is, the first time this is called, the IO number will be 0, the second time it is called, the IO
        number will be 1, and so on.

        :param container_type: The container type of the input.
        :param content_type: The content type of the input.
        :param display_name: The display name of the input.
        :param description: The description of the input.
        :param structure_example: An optional example of the structure of the input, such as how the structure of a
            JSON output may look. This does not need to be an entirely valid example, and should often be truncated for
            brevity.
        :param validation: An optional validation string for the input.
        :param input_count: A tuple of the minimum and maximum number of inputs allowed for this tool.
        :param is_paged: If true, this input will be paged. If false, this input will not be paged.
        :param page_size: A tuple of the minimum and maximum page size for this tool. The input must be paged in order
            for this to have an effect.
        :param max_request_bytes: The maximum request size in bytes for this tool.
        """
        structure: ExampleContainerPbo | None = None
        if isinstance(structure_example, str):
            structure = ExampleContainerPbo(text_example=structure_example)
        elif isinstance(structure_example, bytes):
            structure = ExampleContainerPbo(binary_example=structure_example)
        self.input_configs.append(ToolInputDetailsPbo(
            base_config=ToolIoConfigBasePbo(
                io_number=len(self.input_configs),
                content_type=content_type,
                display_name=display_name,
                description=description,
                structure_example=structure
            ),
            validation=validation,
            min_input_count=input_count[0] if input_count else None,
            max_input_count=input_count[1] if input_count else None,
            paged=is_paged,
            min_page_size=page_size[0] if page_size else None,
            max_page_size=page_size[1] if page_size else None,
            max_request_bytes=max_request_bytes,
        ))
        self._input_container_types.append(container_type)

    def add_output(self, container_type: ContainerType, content_type: str, display_name: str, description: str,
                   testing_example: str | bytes, structure_example: str | bytes | None = None) -> None:
        """
        Add an output configuration to the tool. This determines how many inputs this tool will accept in the plan
        manager, as well as what those inputs are. The IO number of the output will be set to the current number of
        outputs. That is, the first time this is called, the IO number will be 0, the second time it is called, the IO
        number will be 1, and so on.

        :param container_type: The container type of the output.
        :param content_type: The content type of the output.
        :param display_name: The display name of the output.
        :param description: The description of the output.
        :param testing_example: An example of the input to be used when testing this tool in the system. This must be
            an entirely valid example of what an output of this tool could look like so that it can be properly used
            to run tests with. The provided example may be a string, such as for representing JSON or CSV outputs,
            or bytes, such as for representing binary outputs like images or files.
        :param structure_example: An optional example of the structure of the input, such as how the structure of a
            JSON output may look. This does not need to be an entirely valid example, and should often be truncated for
            brevity.
        """
        testing: ExampleContainerPbo | None = None
        if isinstance(testing_example, str):
            testing = ExampleContainerPbo(text_example=testing_example)
        elif isinstance(testing_example, bytes):
            testing = ExampleContainerPbo(binary_example=testing_example)

        structure: ExampleContainerPbo | None = None
        if isinstance(structure_example, str):
            structure = ExampleContainerPbo(text_example=structure_example)
        elif isinstance(structure_example, bytes):
            structure = ExampleContainerPbo(binary_example=structure_example)

        self.output_configs.append(ToolOutputDetailsPbo(
            base_config=ToolIoConfigBasePbo(
                io_number=len(self.output_configs),
                content_type=content_type,
                display_name=display_name,
                description=description,
                structure_example=structure,
                testing_example=testing
            )))
        self._output_container_types.append(container_type)

    def add_config_field(self, field: VeloxFieldDefPbo) -> None:
        """
        Add a configuration field to the tool. This field will be used to configure the tool in the plan manager.

        :param field: The configuration field details.
        """
        self.config_fields.append(field)

    def add_config_field_def(self, field: AbstractVeloxFieldDefinition) -> None:
        """
        Add a configuration field to the tool. This field will be used to configure the tool in the plan manager.

        :param field: The configuration field details.
        """
        self.config_fields.append(ProtobufUtils.field_def_to_pbo(field))

    def add_boolean_config_field(self, field_name: str, display_name: str, description: str, default_value: bool,
                                 optional: bool = False) -> None:
        """
        Add a boolean configuration field to the tool. This field will be used to configure the tool in the plan
        manager.

        :param field_name: The name of the field.
        :param display_name: The display name of the field.
        :param description: The description of the field.
        :param default_value: The default value of the field.
        :param optional: If true, this field is optional. If false, this field is required.
        """
        self.config_fields.append(VeloxFieldDefPbo(
            data_field_type=FieldTypePbo.BOOLEAN,
            data_field_name=field_name,
            display_name=display_name,
            description=description,
            required=not optional,
            editable=True,
            boolean_properties=BooleanPropertiesPbo(
                default_value=default_value
            )
        ))

    def add_double_config_field(self, field_name: str, display_name: str, description: str, default_value: float,
                                min_value: float = -10.**120, max_value: float = 10.**120, precision: int = 2,
                                optional: bool = False) -> None:
        """
        Add a double configuration field to the tool. This field will be used to configure the tool in the plan
        manager.

        :param field_name: The name of the field.
        :param display_name: The display name of the field.
        :param description: The description of the field.
        :param default_value: The default value of the field.
        :param min_value: The minimum value of the field.
        :param max_value: The maximum value of the field.
        :param precision: The precision of the field.
        :param optional: If true, this field is optional. If false, this field is required.
        """
        self.config_fields.append(VeloxFieldDefPbo(
            data_field_type=FieldTypePbo.DOUBLE,
            data_field_name=field_name,
            display_name=display_name,
            description=description,
            required=not optional,
            editable=True,
            double_properties=DoublePropertiesPbo(
                default_value=default_value,
                min_value=min_value,
                max_value=max_value,
                precision=precision
            )
        ))

    def add_integer_config_field(self, field_name: str, display_name: str, description: str,
                                 default_value: int, min_value: int = -2**31, max_value: int = 2**31-1,
                                 optional: bool = False) -> None:
        """
        Add an integer configuration field to the tool. This field will be used to configure the tool in the plan
        manager.

        :param field_name: The name of the field.
        :param display_name: The display name of the field.
        :param description: The description of the field.
        :param default_value: The default value of the field.
        :param min_value: The minimum value of the field.
        :param max_value: The maximum value of the field.
        :param optional: If true, this field is optional. If false, this field is required.
        """
        self.config_fields.append(VeloxFieldDefPbo(
            data_field_type=FieldTypePbo.INTEGER,
            data_field_name=field_name,
            display_name=display_name,
            description=description,
            required=not optional,
            editable=True,
            integer_properties=IntegerPropertiesPbo(
                default_value=default_value,
                min_value=min_value,
                max_value=max_value
            )
        ))

    def add_string_config_field(self, field_name: str, display_name: str, description: str,
                                default_value: str, max_length: int = 1000, optional: bool = False) -> None:
        """
        Add a string configuration field to the tool. This field will be used to configure the tool in the plan
        manager.

        :param field_name: The name of the field.
        :param display_name: The display name of the field.
        :param description: The description of the field.
        :param default_value: The default value of the field.
        :param max_length: The maximum length of the field.
        :param optional: If true, this field is optional. If false, this field is required.
        """
        self.config_fields.append(VeloxFieldDefPbo(
            data_field_type=FieldTypePbo.STRING,
            data_field_name=field_name,
            display_name=display_name,
            description=description,
            required=not optional,
            editable=True,
            string_properties=StringPropertiesPbo(
                default_value=default_value,
                max_length=max_length
            )
        ))

    def add_list_config_field(self, field_name: str, display_name: str, description: str, default_value: str,
                              allowed_values: list[str], direct_edit: bool = False, optional: bool = False) -> None:
        """
        Add a list configuration field to the tool. This field will be used to configure the tool in the plan
        manager.

        :param field_name: The name of the field.
        :param display_name: The display name of the field.
        :param description: The description of the field.
        :param default_value: The default value of the field.
        :param allowed_values: The list of allowed values for the field.
        :param direct_edit: If true, the user can enter a value that is not in the list of allowed values. If false,
            the user can only select from the list of allowed values.
        :param optional: If true, this field is optional. If false, this field is required.
        """
        self.config_fields.append(VeloxFieldDefPbo(
            data_field_type=FieldTypePbo.SELECTION,
            data_field_name=field_name,
            display_name=display_name,
            description=description,
            required=not optional,
            editable=True,
            selection_properties=SelectionPropertiesPbo(
                default_value=default_value,
                static_list_values=allowed_values,
                direct_edit=direct_edit,
            )
        ))

    def add_multi_list_config_field(self, field_name: str, display_name: str, description: str,
                                    default_value: list[str], allowed_values: list[str], direct_edit: bool = False,
                                    optional: bool = False) -> None:
        """
        Add a multi-select list configuration field to the tool. This field will be used to configure the tool in the
        plan manager.

        :param field_name: The name of the field.
        :param display_name: The display name of the field.
        :param description: The description of the field.
        :param default_value: The default value of the field.
        :param allowed_values: The list of allowed values for the field.
        :param direct_edit: If true, the user can enter a value that is not in the list of allowed values. If false,
            the user can only select from the list of allowed values.
        :param optional: If true, this field is optional. If false, this field is required.
        """
        self.config_fields.append(VeloxFieldDefPbo(
            data_field_type=FieldTypePbo.SELECTION,
            data_field_name=field_name,
            display_name=display_name,
            description=description,
            required=not optional,
            editable=True,
            selection_properties=SelectionPropertiesPbo(
                default_value=",".join(default_value),
                static_list_values=allowed_values,
                multi_select=True,
                direct_edit=direct_edit,
            )
        ))

    def to_pbo(self) -> ToolDetailsPbo:
        """
        :return: The ToolDetailsPbo proto object representing this tool.
        """
        return ToolDetailsPbo(
            name=self._name,
            description=self._description,
            input_configs=self.input_configs,
            output_configs=self.output_configs,
            output_data_type_name=self._data_type_name,
            config_fields=self.config_fields
        )

    @abstractmethod
    def validate_input(self) -> str | None:
        """
        Validate the request given to this tool. If the request is validly formatted, this method should return None.
        If the request is not valid, this method should return an error message indicating what is wrong with the
        request.

        This method should not perform any actual processing of the request. It should only validate the inputs and
        configurations provided in the request.

        The request inputs can be accessed using the self.get_input_*() methods.
        The request settings can be accessed using the self.get_config_fields() method.
        The request itself can be accessed using self.request.

        :return: A tuple containing a boolean indicating whether the request is valid and a message describing the
            result of the validation.
        """
        pass

    def dry_run_output(self) -> list[SapioToolResult]:
        """
        Provide fixed results for a dry run of this tool. This method should not perform any actual processing of the
        request. It should only return example outputs that can be used to test the next tool in the plan.

        The default implementation of this method looks at the testing_example field of each output configuration
        and returns a SapioToolResult object based on the content type of the output.

        :return: A list of SapioToolResult objects containing example outputs for this tool. Each result in the list
            corresponds to a separate output from the tool.
        """
        results: list[SapioToolResult] = []
        for output, container_type in zip(self.output_configs, self._output_container_types):
            config: ToolIoConfigBasePbo = output.base_config
            example: ExampleContainerPbo = config.testing_example
            content_type: str = config.content_type
            match container_type:
                case ContainerType.BINARY:
                    example: bytes = example.binary_example
                    results.append(BinaryResult(binary_data=[example], content_type=content_type))
                case ContainerType.CSV:
                    example: str = example.text_example
                    results.append(CsvResult(FileUtil.tokenize_csv(example.encode())[0], content_type=content_type))
                case ContainerType.JSON:
                    # The example may be in the JSONL format instead of plain JSON, so we need to use Pandas to parse
                    # the example into plain JSON.
                    example: str = example.text_example
                    # Format the JSONL in a way that Pandas likes. Collapse everything into a single line, and then
                    # split it back into multiple lines where each line is a single JSON list or dictionary.
                    example: str = re.sub("([]}])\s*([\[{])", r"\1\n\2", example.replace("\n", "")).strip()
                    # Read the JSONL into a Pandas DataFrame and convert it back to plain JSON.
                    import pandas as pd
                    with io.StringIO(example) as stream:
                        example: str = pd.read_json(path_or_buf=stream, lines=True).to_json()
                    results.append(JsonResult(json_data=[json.loads(example)], content_type=content_type))
                case ContainerType.TEXT:
                    example: str = example.text_example
                    results.append(TextResult(text_data=[example], content_type=content_type))
        return results

    @abstractmethod
    def run(self, user: SapioUser) -> list[SapioToolResult]:
        """
        Execute this tool.

        The request inputs can be accessed using the self.get_input_*() methods.
        The request settings can be accessed using the self.get_config_fields() method.
        The request itself can be accessed using self.request.

        :param user: A user object that can be used to initialize manager classes using DataMgmtServer to query the
            system.
        :return: A list of SapioToolResult objects containing the response data. Each result in the list corresponds to
            a separate output from the tool. Field map results do not appear as tool output in the plan manager, instead
            appearing as records related to the plan step during the run.
        """
        pass

    def log_info(self, message: str) -> None:
        """
        Log an info message for this tool. If verbose logging is enabled, this message will be included in the logs
        returned to the caller. Empty/None inputs will not be logged.

        :param message: The message to log.
        """
        if not message:
            return
        if self.verbose_logging:
            self.logs.append(f"INFO: {self._name}: {message}")
        self.logger.info(message)

    def log_warning(self, message: str) -> None:
        """
        Log a warning message for this tool. This message will be included in the logs returned to the caller.
        Empty/None inputs will not be logged.

        :param message: The message to log.
        """
        if not message:
            return
        self.logs.append(f"WARNING: {self._name}: {message}")
        self.logger.warning(message)

    def log_error(self, message: str) -> None:
        """
        Log an error message for this tool. This message will be included in the logs returned to the caller.
        Empty/None inputs will not be logged.

        :param message: The message to log.
        """
        if not message:
            return
        self.logs.append(f"ERROR: {self._name}: {message}")
        self.logger.error(message)

    def log_exception(self, message: str, e: Exception) -> None:
        """
        Log an exception for this tool. This message will be included in the logs returned to the caller.
        Empty/None inputs will not be logged.

        :param message: The message to log.
        :param e: The exception to log.
        """
        if not message and not e:
            return
        self.logs.append(f"EXCEPTION: {self._name}: {message} - {e}")
        self.logger.error(f"{message}\n{traceback.format_exc()}")

    def get_input_name(self, index: int = 0) -> str | None:
        """
        Get the name of the input from the request object.

        :param index: The index of the input to parse. Defaults to 0. Used for tools that accept multiple inputs.
        :return: The name of the input from the request object, or None if no name is set.
        """
        return self.request.input[index].item_container.container_name

    def get_input_binary(self, index: int = 0) -> list[bytes]:
        """
        Get the binary data from the request object.

        :param index: The index of the input to parse. Defaults to 0. Used for tools that accept multiple inputs.
        :return: The binary data from the request object.
        """
        return list(self.request.input[index].item_container.binary_container.items)

    def get_input_csv(self, index: int = 0) -> tuple[list[str], list[dict[str, str]]]:
        """
        Parse the CSV data from the request object.

        :param index: The index of the input to parse. Defaults to 0. Used for tools that accept multiple inputs.
        :return: A tuple containing the header row and the data rows. The header row is a list of strings representing
            the column names, and the data rows are a list of dictionaries where each dictionary represents a row in the
            CSV with the column names as keys and the corresponding values as strings.
        """
        input_data: Sequence[StepInputBatchPbo] = self.request.input
        ret_val: list[dict[str, str]] = []
        headers: Iterable[str] = input_data[index].item_container.csv_container.header.cells
        for row in input_data[index].item_container.csv_container.items:
            row_dict: dict[str, str] = {}
            for header, value in zip(headers, row.cells):
                row_dict[header] = value
            ret_val.append(row_dict)
        return list(headers), ret_val

    def get_input_json(self, index: int = 0) -> list[list[Any]] | list[dict[str, Any]]:
        """
        Parse the JSON data from the request object.

        :param index: The index of the input to parse. Defaults to 0. Used for tools that accept multiple inputs.
        :return: A list of parsed JSON objects. Each entry in the list represents a separate JSON entry from the input.
            Depending on this tool, this may be a list of dictionaries or a list of lists.
        """
        return [json.loads(x) for x in self.request.input[index].item_container.json_container.items]

    def get_input_text(self, index: int = 0) -> list[str]:
        """
        Parse the text data from the request object.

        :param index: The index of the input to parse. Defaults to 0. Used for tools that accept multiple inputs.
        :return: A list of text data as strings.
        """
        return list(self.request.input[index].item_container.text_container.items)

    def get_config_defs(self) -> dict[str, VeloxFieldDefPbo]:
        """
        Get the config field definitions for this tool.

        :return: A dictionary of field definitions, where the keys are the field names and the values are the
            VeloxFieldDefPbo objects representing the field definitions.
        """
        field_defs: dict[str, VeloxFieldDefPbo] = {}
        for field_def in self.to_pbo().config_fields:
            field_defs[field_def.data_field_name] = field_def
        return field_defs

    def get_config_fields(self) -> dict[str, FieldValue | list[str]]:
        """
        Get the configuration field values from the request object. If a field is not present in the request,
        the default value from the config definition will be returned.

        :return: A dictionary of configuration field names and their values. For multi-select selection list fields,
            a list of strings will be returned. For all other field types, the value will match the field type
            (bool for boolean fields, float for double fields, int for short, integer, long, and enum fields, and
            string for everything else).
        """
        config_fields: dict[str, Any] = {}
        raw_configs: Mapping[str, FieldValuePbo] = self.request.config_field_values
        for field_name, field_def in self.get_config_defs().items():
            field_value: FieldValue = None
            # If the field is present in the request, convert the protobuf value to a Python value.
            if field_name in raw_configs:
                field_value = ProtobufUtils.field_pbo_to_value(raw_configs[field_name])
            # If the field isn't present or is None, use the default value from the field definition.
            if field_value is None:
                field_value = ProtobufUtils.field_def_pbo_to_default_value(field_def)
            # If the field is a multi-select selection list, split the value by commas and strip whitespace.
            if field_def.data_field_type == FieldTypePbo.SELECTION and field_def.selection_properties.multi_select:
                field_value: list[str] = [x.strip() for x in field_value.split(',') if x.strip()]
            config_fields[field_name] = field_value
        return config_fields

    @staticmethod
    def read_from_json(json_data: list[dict[str, Any]], key: str) -> list[Any]:
        """
        From a list of dictionaries, return a list of values for the given key from each dictionary. Skips null values.

        :param json_data: The JSON data to read from.
        :param key: The key to read the values from.
        :return: A list of values corresponding to the given key in the JSON data.
        """
        ret_val: list[Any] = []
        for entry in json_data:
            if key in entry:
                value = entry[key]
                if isinstance(value, list):
                    ret_val.extend(value)
                elif value is not None:
                    ret_val.append(value)
        return ret_val
