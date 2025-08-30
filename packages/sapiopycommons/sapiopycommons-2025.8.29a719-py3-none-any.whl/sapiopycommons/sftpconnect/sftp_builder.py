import io
from enum import Enum

import paramiko
from paramiko import pkey
from paramiko.sftp_client import SFTPClient

from sapiopycommons.general.exceptions import SapioException


class SFTPAuthMethod(Enum):
    """
    An enum being used to specify connection type to the target server.
    """
    PASSWORD = 0
    """Connection is being done via Password."""
    FILEPATH = 1
    """Connection is being done using a private key file in the codebase."""
    KEY_STRING = 2
    """Connection is being done using a private key in string form."""


class SFTPBuilder:
    """
    A class for making SFTP connections.
    """

    @staticmethod
    def open_sftp(username: str, host: str, port: int, authentication: str,
                  connection_type: SFTPAuthMethod = SFTPAuthMethod.PASSWORD) -> SFTPClient:
        """
        Builds a SFTP client from user input.

        :param username: The username of the individual trying to connect to the target server.
        :param host: The hostname/IP address of the target server.
        :param port: The port number used to connect to the target server.
        :param authentication: The string used to connect to the target server. This could hold a filepath, a password
            or a private key in string form depending on the connection_type parameter.

            If authentication is a private key string, they are generally formated like this:
            -----BEGIN OPENSSH PRIVATE KEY-----\n
            asdfh;hjadfh;jghajdg54646+5fasdfadlajklgajd'gj'ajg654564\n
            asdkjfhj;kghj;ahj;wh41234hjadjkhhdsgadshjkdghjshdlsds468\n
            ....

        :param connection_type: This enum is used to specify how the connection to the target server is being made.
            The options are:
            (0) PASSWORD: This means that the authentication parameter contains a password that will be used to connect to the server
            (1) FILEPATH: This means that the authentication parameter contains a filepath leading to a private key file stored in the codebase
            (2) KEY_STRING: This means that the authentication parameter contains the private key in string form

        """

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy)

        if connection_type == SFTPAuthMethod.FILEPATH:
            client.connect(host, username=username, port=port, key_filename=authentication)
            return client.open_sftp()

        if connection_type == SFTPAuthMethod.KEY_STRING:
            private_key: pkey = paramiko.RSAKey.from_private_key(io.StringIO(authentication))
            client.connect(host, username=username, port=port, pkey=private_key)
            return client.open_sftp()

        if connection_type == SFTPAuthMethod.PASSWORD:
            client.connect(host, username=username, password=authentication, port=port)
            return client.open_sftp()

        raise SapioException("The SFTPAuthMethod enumerator was not properly specified.")
