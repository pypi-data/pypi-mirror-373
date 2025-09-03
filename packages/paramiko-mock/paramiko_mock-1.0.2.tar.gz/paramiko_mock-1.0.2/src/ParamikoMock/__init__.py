"""
This module provides a set of classes to mock the paramiko library.

Classes that do not contain a docstring will not be included in the documentation.
Some classes are intended to be used internally for the and are not recommended to be used directly without the public interfaces.

We cannot guarantee that the internal classes will not change in minor release so proceed with caution when using them.
"""
from .ssh_mock import (
    SSHClientMock,
    SSHResponseMock,
    SSHCommandMock,
    SSHCommandFunctionMock
)
from .sftp_mock import (
    SFTPClientMock,
    SFTPFileMock
)
from .local_filesystem_mock import (
    LocalFileMock,
    LocalFilesystemMock
)
from .mocked_env import ParamikoMockEnviron
from .exceptions import BadSetupError