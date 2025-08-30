from __future__ import annotations

from abc import abstractmethod, ABC
from typing import cast
from weakref import WeakValueDictionary

from sapiopylib.rest.User import SapioUser

from sapiopycommons.files.file_bridge import FileBridge, FileBridgeMetadata
from sapiopycommons.general.aliases import AliasUtil, UserIdentifier


class FileBridgeHandler:
    """
    The FileBridgeHandler provides caching of the results of file bridge endpoint calls while also containing quality
    of life functions for common file bridge actions.
    """
    user: SapioUser
    __bridge: str
    __file_data_cache: dict[str, bytes]
    """A cache of file paths to file bytes."""
    __file_objects: dict[str, File]
    """A cache of file paths to File objects."""
    __dir_file_name_cache: dict[str, list[str]]
    """A cache of directory file paths to the names of the files or nested directories within them."""
    __dir_objects: dict[str, Directory]
    """A cache of directory file paths to Directory objects."""
    __file_metadata_cache: dict[str, FileBridgeMetadata]
    """A cache of file or directory paths to file metadata."""
    __dir_metadata_cache: dict[str, list[FileBridgeMetadata]]
    """A cache of directory file paths to the metadata of the files or nested directories within them."""

    __instances: WeakValueDictionary[str, FileBridgeHandler] = WeakValueDictionary()
    __initialized: bool

    def __new__(cls, context: UserIdentifier, bridge_name: str):
        """
        :param context: The current webhook context or a user object to send requests from.
        """
        user = AliasUtil.to_sapio_user(context)
        key = f"{user.__hash__()}:{bridge_name}"
        obj = cls.__instances.get(key)
        if not obj:
            obj = object.__new__(cls)
            obj.__initialized = False
            cls.__instances[key] = obj
        return obj

    def __init__(self, context: UserIdentifier, bridge_name: str):
        """
        :param context: The current webhook context or a user object to send requests from.
        :param bridge_name: The name of the bridge to communicate with. This is the "connection name" in the
            file bridge configurations.
        """
        if self.__initialized:
            return
        self.__initialized = True

        self.user = AliasUtil.to_sapio_user(context)
        self.__bridge = bridge_name
        self.__file_data_cache = {}
        self.__file_objects = {}
        self.__dir_file_name_cache = {}
        self.__dir_objects = {}
        self.__file_metadata_cache = {}
        self.__dir_metadata_cache = {}

    @property
    def connection_name(self) -> str:
        return self.__bridge

    def clear_caches(self) -> None:
        """
        Clear the file and directory caches of this handler.
        """
        self.__file_data_cache.clear()
        self.__file_objects.clear()
        self.__dir_file_name_cache.clear()
        self.__dir_objects.clear()
        self.__file_metadata_cache.clear()
        self.__dir_metadata_cache.clear()

    # CR-47388: Allow the FileBridgeHandler's File and Directory objects to be provided as file path parameters.
    def file_exists(self, file_path: str | File | Directory) -> bool:
        """
        Determine if a file or directory exists in FileBridge at the provided path. This is achieved by calling for the
        metadata of the provided file path. If the file does not exist, then an exception is raised, which is caught and
        handled by this function as a return value of False.

        :param file_path: A file path, File object, or Directory object.
        :return: True if the file exists. False if it does not.
        """
        if isinstance(file_path, FileBridgeObject):
            file_path = file_path.path
        try:
            self.file_metadata(file_path)
            return True
        except Exception:
            return False

    def read_file(self, file_path: str | File, base64_decode: bool = True) -> bytes:
        """
        Read a file from FileBridge. The bytes of the given file will be cached so that any subsequent reads of this
        file will not make an additional webservice call.

        :param file_path: The file path or File object to read from.
        :param base64_decode: If true, base64 decode the file. Files are base64 encoded by default when retrieved from
            FileBridge.
        :return: The bytes of the file.
        """
        if isinstance(file_path, File):
            file_path = file_path.path
        if file_path in self.__file_data_cache:
            return self.__file_data_cache[file_path]
        file_bytes: bytes = FileBridge.read_file(self.user, self.__bridge, file_path, base64_decode)
        self.__file_data_cache[file_path] = file_bytes
        return file_bytes

    def write_file(self, file_path: str | File, file_data: bytes | str) -> None:
        """
        Write a file to FileBridge. The bytes of the given file will be cached so that any subsequent reads of this
        file will not make an additional webservice call.

        :param file_path: The file path or File object to write to. If a file already exists at the given path then the
            file is overwritten.
        :param file_data: A string or bytes of the file to be written.
        """
        if isinstance(file_path, File):
            file_path = file_path.path
        FileBridge.write_file(self.user, self.__bridge, file_path, file_data)
        self.__file_data_cache[file_path] = file_data if isinstance(file_data, bytes) else file_data.encode()

        # Find the directory path to this file and the name of the file. Add the file name to the cached list of
        # files for the directory, assuming we have this directory cached and the file isn't already in it.
        file_name, path_to = split_path(file_path)
        if path_to in self.__dir_file_name_cache and file_name not in self.__dir_file_name_cache[path_to]:
            self.__dir_file_name_cache[path_to].append(file_name)

    def delete_file(self, file_path: str | File) -> None:
        """
        Delete an existing file in FileBridge. If this file is in the cache, it will also be deleted from the cache.

        :param file_path: The file path or File object to delete.
        """
        if isinstance(file_path, File):
            file_path = file_path.path
        FileBridge.delete_file(self.user, self.__bridge, file_path)
        if file_path in self.__file_data_cache:
            self.__file_data_cache.pop(file_path)
        if file_path in self.__file_objects:
            self.__file_objects.pop(file_path)
        if file_path in self.__file_metadata_cache:
            self.__file_metadata_cache.pop(file_path)

    def list_directory(self, file_path: str | Directory) -> list[str]:
        """
        List the contents of a FileBridge directory. The contents of this directory will be cached so that any
        subsequent lists of this directory will not make an additional webservice call.

        :param file_path: The directory path or Directory object to list from.
        :return: A list of names of files and folders in the directory.
        """
        if isinstance(file_path, Directory):
            file_path = file_path.path
        if file_path in self.__dir_file_name_cache:
            return self.__dir_file_name_cache[file_path]
        files: list[str] = FileBridge.list_directory(self.user, self.__bridge, file_path)
        self.__dir_file_name_cache[file_path] = files
        return files

    def create_directory(self, file_path: str | Directory) -> None:
        """
        Create a new directory in FileBridge. This new directory will be added to the cache as empty so that listing
        the same directory does not make an additional webservice call.

        :param file_path: The directory path or Directory object to create the directory at. If a directory already
            exists at the given path then an exception is raised.
        """
        if isinstance(file_path, Directory):
            file_path = file_path.path
        FileBridge.create_directory(self.user, self.__bridge, file_path)
        # This directory was just created, so we know it's empty.
        self.__dir_file_name_cache[file_path] = []
        self.__dir_metadata_cache[file_path] = []

        # Find the directory path to this directory and the name of the directory. Add the directory name to the cached
        # list of files for the directory, assuming we have this directory cached and the directory isn't already in it.
        dir_name, path_to = split_path(file_path)
        if path_to in self.__dir_file_name_cache and dir_name not in self.__dir_file_name_cache[path_to]:
            self.__dir_file_name_cache[path_to].append(dir_name)

    def delete_directory(self, file_path: str | Directory) -> None:
        """
        Delete an existing directory in FileBridge. If this directory is in the cache, it will also be deleted
        from the cache.

        :param file_path: The directory path or Directory object to delete.
        """
        if isinstance(file_path, Directory):
            file_path = file_path.path
        FileBridge.delete_directory(self.user, self.__bridge, file_path)
        # The deletion of a directory also deletes all the files within it, so we need to check every cache for file
        # paths that start with this directory path and remove them.
        for key in list(self.__file_data_cache.keys()):
            if key.startswith(file_path):
                self.__file_data_cache.pop(key)
        for key in list(self.__file_objects.keys()):
            if key.startswith(file_path):
                self.__file_objects.pop(key)
        for key in list(self.__file_metadata_cache.keys()):
            if key.startswith(file_path):
                self.__file_metadata_cache.pop(key)
        for key in list(self.__dir_file_name_cache.keys()):
            if key.startswith(file_path):
                self.__dir_file_name_cache.pop(key)
        for key in list(self.__dir_objects.keys()):
            if key.startswith(file_path):
                self.__dir_objects.pop(key)
        for key in list(self.__dir_metadata_cache.keys()):
            if key.startswith(file_path):
                self.__dir_metadata_cache.pop(key)

    # FR-47387: Add support for the metadata endpoints in FileBridge.
    def file_metadata(self, file_path: str | File | Directory) -> FileBridgeMetadata:
        """
        Get metadata for a file in FileBridge. If this metadata is already cached, then it will be returned from the
        cache.

        The file path may be to a directory, in which case only the metadata for that directory will be returned. If you
        want the metadata for the contents of a directory, then use the directory_metadata function.

        :param file_path: The file path, File object, or Directory object to retrieve the metadata from.
        :return: The metadata for the file.
        """
        if isinstance(file_path, FileBridgeObject):
            file_path = file_path.path
        if file_path in self.__file_metadata_cache:
            return self.__file_metadata_cache[file_path]
        metadata: FileBridgeMetadata = FileBridge.file_metadata(self.user, self.__bridge, file_path)
        self.__file_metadata_cache[file_path] = metadata

        # It's possible that this file is newly created, but the directory it's in was already cached. If that's the
        # case, then we need to add this file's metadata to the directory's cache. (The write_file/create_directory
        # methods will have already handled the directory's file name cache.)
        file_name, path_to = split_path(file_path)
        if (path_to in self.__dir_metadata_cache
                and not any([file_name == x.file_name for x in self.__dir_metadata_cache[path_to]])):
            self.__dir_metadata_cache[path_to].append(metadata)
        return metadata

    def directory_metadata(self, file_path: str | Directory) -> list[FileBridgeMetadata]:
        """
        Get metadata for every file in a directory in FileBridge. If this metadata is already cached, then it will be
        returned from the cache.

        :param file_path: The path to the directory to retrieve the metadata of the contents, or the Directory object.
        :return: A list of the metadata for each file in the directory.
        """
        if isinstance(file_path, Directory):
            file_path = file_path.path
        # If the directory metadata is already cached, then use the cached value instead of making an additional
        # webservice call. The only exception to this is if the size of the directory's file name cache differs from
        # the size of the directory's metadata cache. This can happen if a new file or directory was added to the
        # directory using write_file/create_directory after the metadata of the directory's contents was cached.
        # In this case, we need to make an additional webservice call to get the metadata of the new file or directory.
        # Since there could be multiple new files or directories, just re-query the metadata for the entire directory.
        if (file_path in self.__dir_metadata_cache
                and len(self.__dir_metadata_cache[file_path]) == len(self.__dir_file_name_cache[file_path])):
            return self.__dir_metadata_cache[file_path]
        metadata: list[FileBridgeMetadata] = FileBridge.directory_metadata(self.user, self.__bridge, file_path)
        # Save the metadata to the directory cache.
        self.__dir_metadata_cache[file_path] = metadata
        # We can also save the metadata to the file cache so that we don't have to make additional webservice calls if
        # an individual file's metadata is requested.
        for file_metadata in metadata:
            self.__file_metadata_cache[file_path + "/" + file_metadata.file_name] = file_metadata
        # This also doubles as a list directory call since it contains the file names of the contents of the directory.
        self.__dir_file_name_cache[file_path] = [x.file_name for x in metadata]
        return metadata

    def is_file(self, file_path: str | File | Directory) -> bool:
        """
        Determine if the given file path points to a file. This is achieved by checking the metadata of the provided
        file path. If the metadata is not cached, then this will make a webservice call to get the metadata.

        :param file_path: A file path, File object, or Directory object.
        :return: True if the file path points to a file. False if it points to a directory.
        """
        return self.file_metadata(file_path).is_file

    def is_directory(self, file_path: str | Directory) -> bool:
        """
        Determine if the given file path points to a directory. This is achieved by checking the metadata of the
        provided file path. If the metadata is not cached, then this will make a webservice call to get the metadata.

        :param file_path: A file path or Directory object.
        :return: True if the file path points to a directory. False if it points to a file.
        """
        return self.file_metadata(file_path).is_directory

    def move_file(self, move_from: str | Directory, move_to: str | Directory, old_name: str | File,
                  new_name: str | File | None = None) -> None:
        """
        Move a file from one location to another within File Bridge. This is done be reading the file into memory,
        writing a copy of the file in the new location, then deleting the original file.

        :param move_from: The path or Directory object to the current location of the file.
        :param move_to: The path or Directory object to move the file to.
        :param old_name: The current name of the file, or a File object.
        :param new_name: The name that the file should have after it is moved, or a File object. If this is not
            provided, then the new name will be the same as the old name.
        """
        if isinstance(move_from, Directory):
            move_from = move_from.path
        if isinstance(move_to, Directory):
            move_to = move_to.path
        if isinstance(old_name, File):
            old_name = old_name.name
        if isinstance(new_name, File):
            new_name = new_name.name
        if not new_name:
            new_name = old_name

        # Read the file into memory.
        file_bytes: bytes = self.read_file(move_from + "/" + old_name)
        # Write the file into the new location.
        self.write_file(move_to + "/" + new_name, file_bytes)
        # Delete the file from the old location. We do this last in case the write call fails.
        self.delete_file(move_from + "/" + old_name)

    def get_file_object(self, file_path: str) -> File:
        """
        Get a File object from a file path. This object can be used to get the contents of the file at this path
        and traverse up the file hierarchy to the directory that the file is contained within.

        There is no guarantee that this file actually exists within the current file bridge connection when it is
        constructed. If the file doesn't exist, then retrieving its contents will fail.

        :param file_path: A file path.
        :return: A File object constructed form the given file path.
        """
        if file_path in self.__file_objects:
            return self.__file_objects[file_path]
        file = File(self, file_path)
        self.__file_objects[file_path] = file
        return file

    def get_directory_object(self, file_path: str) -> Directory:
        """
        Get a Directory object from a file path. This object can be used to traverse up and down the file hierarchy
        by going up to the parent directory that this directory is contained within or going down to the contents of
        this directory. A file path of "" (a blank string) equates to the root directory of this file bridge connection.

        There is no guarantee that this directory actually exists within the current file bridge connection when it is
        constructed. If the directory doesn't exist, then retrieving its contents will fail.

        :param file_path: A file path.
        :return: A Directory object constructed from the given file path.
        """
        if file_path in self.__dir_objects:
            return self.__dir_objects[file_path]
        directory = Directory(self, file_path)
        self.__dir_objects[file_path] = directory
        return directory


class FileBridgeObject(ABC):
    """
    A FileBridgeObject is either a file or a directory that is contained within file bridge. Every object has a
    name and a parent directory that it is contained within, unless the object is the root directory, in
    which case the parent is None. The root directory has a path and name of "" (a blank string).

    Note that this object may not actually exist within the file bridge connection that it is associated with.
    Retrieving the contents of an object that doesn't exist will fail. You can use the write_file or create_directory
    functions of the FileBridgeHandler to create new files or directories from these objects.
    """
    _handler: FileBridgeHandler
    _name: str
    _path_to: str
    _parent: Directory | None

    def __init__(self, handler: FileBridgeHandler, file_path: str):
        self._handler = handler

        # Remove any leading or trailing slashes from the file path.
        if file_path.startswith("/") or file_path.endswith("/"):
            file_path = file_path.strip("/")

        # If the file path is an empty string, then this is the root directory.
        if file_path == "":
            self._name = ""
            self._path_to = ""
            self._parent = None
            return
        name, path_to = split_path(file_path)
        self._name = name
        self._path_to = path_to
        self._parent = handler.get_directory_object(path_to)

    @property
    def name(self) -> str:
        """
        :return: The name of this object.
        """
        return self._name

    @property
    def path_to(self) -> str:
        """
        :return: The file path that leads to this object. Excludes the name of the object itself.
        """
        return self._path_to

    @property
    def path(self) -> str:
        """
        :return: The full file path that leads to this object. Includes the name of the object itself.
        """
        if self._path_to == "":
            return self._name
        return self._path_to + "/" + self._name

    @property
    def parent(self) -> Directory | None:
        """
        :return: The parent directory of this object. If this object is the root directory, then this will be None.
        """
        return self._parent

    @abstractmethod
    def is_file(self) -> bool:
        """
        :return: True if this object is a file. False if it is a directory.
        """
        pass

    @abstractmethod
    def is_directory(self) -> bool:
        """
        :return: True if this object is a directory. False if it is a file.
        """
        pass

    def exists(self) -> bool:
        """
        :return: True if this object exists in the file bridge connection that it is associated with.
            False if it does not.
        """
        return self._handler.file_exists(self.path)

    def get_metadata(self) -> FileBridgeMetadata:
        """
        :return: The metadata for this object.
        """
        return self._handler.file_metadata(self.path)


class File(FileBridgeObject):
    def __init__(self, handler: FileBridgeHandler, file_path: str):
        """
        :param handler: A FileBridgeHandler for the connection that this file came from.
        :param file_path: The path to this file.
        """
        super().__init__(handler, file_path)

    @property
    def contents(self) -> bytes:
        """
        Read the bytes of this file.
        This pulls from the cache of this object's related FileBridgeHandler.

        :return: The bytes of this file.
        """
        return self._handler.read_file(self.path)

    def is_file(self) -> bool:
        return True

    def is_directory(self) -> bool:
        return False


class Directory(FileBridgeObject):
    _contents: dict[str, FileBridgeObject] | None

    def __init__(self, handler: FileBridgeHandler, file_path: str):
        """
        :param handler: A FileBridgeHandler for the connection that this directory came from.
        :param file_path: The path to this directory.
        """
        super().__init__(handler, file_path)
        self._contents = None

    @property
    def contents(self) -> dict[str, FileBridgeObject]:
        """
        Get all the objects in this Directory.
        This pulls from the cache of this object's related FileBridgeHandler.

        :return: A dictionary of object names to the objects (Files or Directories) contained within this Directory.
        """
        if self._contents is not None:
            return self._contents

        # Load the metadata of the directory to get the names of the files and directories within it.
        # We don't need the return value of this function, but we need to call it to populate the cache.
        self._handler.directory_metadata(self._path_to)

        # Construct the objects for the contents of this directory.
        self._contents = {}
        for name in self._handler.list_directory(self._path_to):
            file_path: str = self._path_to + "/" + name
            if self._handler.is_file(file_path):
                self._contents[name] = self._handler.get_file_object(file_path)
            else:
                self._contents[name] = self._handler.get_directory_object(file_path)
        return self._contents

    def is_file(self) -> bool:
        return False

    def is_directory(self) -> bool:
        return True

    def get_files(self) -> dict[str, File]:
        """
        Get all the files in this Directory.
        This pulls from the cache of this object's related FileBridgeHandler.

        :return: A mapping of file name to File for every file in this Directory.
        """
        return {x: cast(File, y) for x, y in self.contents.items() if y.is_file()}

    def get_directories(self) -> dict[str, Directory]:
        """
        Get all the nested directories in this Directory.
        This pulls from the cache of this object's related FileBridgeHandler.

        :return: A mapping of directory name to Directory for every nested directory in this Directory.
        """
        return {x: cast(Directory, y) for x, y in self.contents.items() if not y.is_file()}


def split_path(file_path: str) -> tuple[str, str]:
    """
    :param file_path: A file path where directories are separated the "/" characters. If there is no "/" character, then
        that means that the provided path is in the root directory, or is the root directory itself.
    :return: A tuple of two strings that splits the path on its last slash. The first string is the name of the
        file/directory at the given file path and the second string is the location to that file. If there is no slash
        character, then the second string is an empty string.
    """
    last_slash: int = file_path.rfind("/")
    if last_slash == -1:
        return file_path, ""
    return file_path[last_slash + 1:], file_path[:last_slash]
