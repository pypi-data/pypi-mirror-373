import asyncio
from typing import Any

import grpc

from sapiopycommons.ai.protoapi.plan.converter.converter_pb2_grpc import add_ConverterServiceServicer_to_server, \
    ConverterServiceServicer
from sapiopycommons.ai.protoapi.plan.script.script_pb2_grpc import add_ScriptServiceServicer_to_server, \
    ScriptServiceServicer
from sapiopycommons.ai.protoapi.plan.tool.tool_pb2_grpc import add_ToolServiceServicer_to_server, ToolServiceServicer


class SapioGrpcServer:
    """
    A gRPC server for handling the various Sapio gRPC services.
    """
    port: str
    options: list[tuple[str, Any]]
    _converter_services: list[ConverterServiceServicer]
    _script_services: list[ScriptServiceServicer]
    _tool_services: list[ToolServiceServicer]

    def __init__(self, port: str = "50051", message_mb_size: int = 100, options: list[tuple[str, Any]] | None = None) \
            -> None:
        """
        Initialize the gRPC server with the specified port and message size.

        :param port: The port to listen on for incoming gRPC requests.
        :param message_mb_size: The maximum size of a message in megabytes.
        :param options: Additional gRPC server options to set. This should be a list of tuples where the first item is
            the option name and the second item is the option value.
        """
        self.port = port
        self.options = [
            ('grpc.max_send_message_length', message_mb_size * 1024 * 1024),
            ('grpc.max_receive_message_length', message_mb_size * 1024 * 1024)
        ]
        if options:
            self.options.extend(options)
        self._converter_services = []
        self._script_services = []
        self._tool_services = []

    def add_converter_service(self, service: ConverterServiceServicer) -> None:
        """
        Add a converter service to the gRPC server.

        :param service: The converter service to register with the server.
        """
        self._converter_services.append(service)

    def add_script_service(self, service: ScriptServiceServicer) -> None:
        """
        Add a script service to the gRPC server.

        :param service: The script service to register with the server.
        """
        self._script_services.append(service)

    def add_tool_service(self, service: ToolServiceServicer) -> None:
        """
        Add a tool service to the gRPC server.

        :param service: The tool service to register with the server.
        """
        self._tool_services.append(service)

    def start(self) -> None:
        """
        Start the gRPC server for the provided servicers.
        """
        if not (self._converter_services or self._script_services or self._tool_services):
            raise ValueError("No services have been added to the server. Use add_converter_service, add_script_service,"
                             "or add_tool_service to register a service before starting the server.")

        async def serve():
            server = grpc.aio.server(options=self.options)

            for service in self._converter_services:
                print(f"Registering Converter service: {service.__class__.__name__}")
                add_ConverterServiceServicer_to_server(service, server)
            for service in self._script_services:
                print(f"Registering Script service: {service.__class__.__name__}")
                add_ScriptServiceServicer_to_server(service, server)
            for service in self._tool_services:
                print(f"Registering Tool service: {service.__class__.__name__}")
                add_ToolServiceServicer_to_server(service, server)

            server.add_insecure_port("[::]:" + self.port)
            await server.start()
            print("Server started, listening on " + self.port)
            try:
                await server.wait_for_termination()
            finally:
                print("Stopping server...")
                await server.stop(0)
                print("Server stopped.")

        try:
            asyncio.run(serve())
        except KeyboardInterrupt:
            print("Server stopped by user.")
        except Exception as e:
            print(f"An error occurred: {e}")
