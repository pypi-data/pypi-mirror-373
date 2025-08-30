import base64
import io
import urllib.parse
from typing import Any

from requests import Response
from sapiopylib.rest.User import SapioUser

from sapiopycommons.general.aliases import UserIdentifier, AliasUtil


# FR-47387: Add support for the metadata endpoints in FileBridge.
class FileBridgeMetadata:
    """
    Metadata for a file or directory in FileBridge.
    """
    file_name: str
    """The name of the file or directory."""
    is_file: bool
    """True if the metadata is for a file, False if it is for a directory."""
    is_directory: bool
    """True if the metadata is for a directory, False if it is for a file."""
    size: int
    """The size of the file in bytes. For directories, this value will always be zero."""
    creation_time: int
    """The time the file or directory was created, in milliseconds since the epoch."""
    last_accessed_time: int
    """The time the file or directory was last accessed, in milliseconds since the epoch."""
    last_modified_time: int
    """The time the file or directory was last modified, in milliseconds since the epoch."""

    def __init__(self, json_dict: dict[str, Any]):
        self.file_name = json_dict['fileName']
        self.is_file = json_dict['isFile']
        self.is_directory = json_dict['isDirectory']
        self.size = json_dict['size']
        self.creation_time = json_dict['creationTime']
        self.last_accessed_time = json_dict['lastAccessTime']
        self.last_modified_time = json_dict['lastModifiedTime']


# FR-46064 - Initial port of PyWebhookUtils to sapiopycommons.
class FileBridge:
    @staticmethod
    def read_file(context: UserIdentifier, bridge_name: str, file_path: str,
                  base64_decode: bool = True) -> bytes:
        """
        Read a file from FileBridge.

        :param context: The current webhook context or a user object to send requests from.
        :param bridge_name: The name of the bridge to use. This is the "connection name" in the
            file bridge configurations.
        :param file_path: The path to read the file from.
        :param base64_decode: If true, base64 decode the file. Files are by default base64 encoded when retrieved from
            FileBridge.
        :return: The bytes of the file.
        """
        sub_path = '/ext/filebridge/readFile'
        params = {
            'Filepath': f"bridge://{bridge_name}/{file_path}"
        }
        user: SapioUser = AliasUtil.to_sapio_user(context)
        response = user.get(sub_path, params)
        user.raise_for_status(response)

        ret_val = response.content
        if base64_decode:
            ret_val = base64.b64decode(response.content)
        return ret_val

    @staticmethod
    def write_file(context: UserIdentifier, bridge_name: str, file_path: str,
                   file_data: bytes | str) -> None:
        """
        Write a file to FileBridge.

        :param context: The current webhook context or a user object to send requests from.
        :param bridge_name: The name of the bridge to use. This is the "connection name" in the
            file bridge configurations.
        :param file_path: The path to write the file to. If a file already exists at the given path then the file is
            overwritten.
        :param file_data: A string or bytes of the file to be written.
        """
        sub_path = '/ext/filebridge/writeFile'
        params = {
            'Filepath': f"bridge://{bridge_name}/{file_path}"
        }
        user: SapioUser = AliasUtil.to_sapio_user(context)
        with io.BytesIO(file_data.encode() if isinstance(file_data, str) else file_data) as data_stream:
            response = user.post_data_stream(sub_path, params=params, data_stream=data_stream)
        user.raise_for_status(response)

    @staticmethod
    def list_directory(context: UserIdentifier, bridge_name: str,
                       file_path: str | None = "") -> list[str]:
        """
        List the contents of a FileBridge directory.

        :param context: The current webhook context or a user object to send requests from.
        :param bridge_name: The name of the bridge to use. This is the "connection name" in the
            file bridge configurations.
        :param file_path: The path to read the directory from.
        :return: A list of names of files and folders in the directory.
        """
        sub_path = '/ext/filebridge/listDirectory'
        params = {
            'Filepath': f"bridge://{bridge_name}/{file_path}"
        }
        user: SapioUser = AliasUtil.to_sapio_user(context)
        response: Response = user.get(sub_path, params=params)
        user.raise_for_status(response)

        response_body: list[str] = response.json()
        path_length = len(f"bridge://{bridge_name}/")
        return [urllib.parse.unquote(value)[path_length:] for value in response_body]

    @staticmethod
    def create_directory(context: UserIdentifier, bridge_name: str, file_path: str) -> None:
        """
        Create a new directory in FileBridge.

        :param context: The current webhook context or a user object to send requests from.
        :param bridge_name: The name of the bridge to use. This is the "connection name" in the
            file bridge configurations.
        :param file_path: The path to create the directory at. If a directory already exists at the given path then an
            exception is raised.
        """
        sub_path = '/ext/filebridge/createDirectory'
        params = {
            'Filepath': f"bridge://{bridge_name}/{file_path}"
        }
        user: SapioUser = AliasUtil.to_sapio_user(context)
        response = user.post(sub_path, params=params)
        user.raise_for_status(response)

    @staticmethod
    def delete_file(context: UserIdentifier, bridge_name: str, file_path: str) -> None:
        """
        Delete an existing file in FileBridge.

        :param context: The current webhook context or a user object to send requests from.
        :param bridge_name: The name of the bridge to use. This is the "connection name" in the
            file bridge configurations.
        :param file_path: The path to the file to delete.
        """
        sub_path = '/ext/filebridge/deleteFile'
        params = {
            'Filepath': f"bridge://{bridge_name}/{file_path}"
        }
        user: SapioUser = AliasUtil.to_sapio_user(context)
        response = user.delete(sub_path, params=params)
        user.raise_for_status(response)

    @staticmethod
    def delete_directory(context: UserIdentifier, bridge_name: str, file_path: str) -> None:
        """
        Delete an existing directory in FileBridge.

        :param context: The current webhook context or a user object to send requests from.
        :param bridge_name: The name of the bridge to use. This is the "connection name" in the
            file bridge configurations.
        :param file_path: The path to the directory to delete.
        """
        sub_path = '/ext/filebridge/deleteDirectory'
        params = {
            'Filepath': f"bridge://{bridge_name}/{file_path}"
        }
        user: SapioUser = AliasUtil.to_sapio_user(context)
        response = user.delete(sub_path, params=params)
        user.raise_for_status(response)

    @staticmethod
    def file_metadata(context: UserIdentifier, bridge_name: str, file_path: str) -> FileBridgeMetadata:
        """
        Get metadata for a file or directory in FileBridge.

        The file path may be to a directory, in which case only the metadata for that directory will be returned. If you
        want the metadata for the contents of a directory, then use the directory_metadata function.

        :param context: The current webhook context or a user object to send requests from.
        :param bridge_name: The name of the bridge to use. This is the "connection name" in the
            file bridge configurations.
        :param file_path: The path to the file to retrieve the metadata from.
        :return: The metadata for the file.
        """
        sub_path = '/ext/filebridge/file/metadata'
        params = {
            'Filepath': f"bridge://{bridge_name}/{file_path}"
        }
        user: SapioUser = AliasUtil.to_sapio_user(context)
        response = user.get(sub_path, params=params)
        user.raise_for_status(response)
        response_body: dict[str, Any] = response.json()
        return FileBridgeMetadata(response_body)

    @staticmethod
    def directory_metadata(context: UserIdentifier, bridge_name: str, file_path: str) -> list[FileBridgeMetadata]:
        """
        Get metadata for every file or nested directory in a directory in FileBridge.

        :param context: The current webhook context or a user object to send requests from.
        :param bridge_name: The name of the bridge to use. This is the "connection name" in the
            file bridge configurations.
        :param file_path: The path to the directory to retrieve the metadata of the contents.
        :return: A list of the metadata for the contents of the directory.
        """
        sub_path = '/ext/filebridge/directory/metadata'
        params = {
            'Filepath': f"bridge://{bridge_name}/{file_path}"
        }
        user: SapioUser = AliasUtil.to_sapio_user(context)
        response = user.get(sub_path, params=params)
        user.raise_for_status(response)
        response_body: list[dict[str, Any]] = response.json()
        return [FileBridgeMetadata(x) for x in response_body]
