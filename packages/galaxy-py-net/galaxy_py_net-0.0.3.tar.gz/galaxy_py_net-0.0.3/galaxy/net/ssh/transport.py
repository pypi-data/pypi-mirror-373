#  Copyright (c) 2022 bastien.saltel
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from abc import ABC,                                    \
                abstractmethod
from typing import Any
from socket import socket
from paramiko.transport import Transport

from galaxy.utils.base import Component,                \
                              Configurable
from galaxy.service.service import LogService,          \
                                   LogAsyncService
from galaxy.net.socket import SocketFactory


class SSHTransportFactory(Component, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(SSHTransportFactory, self).__init__()
        self.log: LogService | LogAsyncService | None = None

    @abstractmethod
    def create(self) -> Any:
        raise NotImplementedError("Should implement create()")


class ParamikoSSHTransportFactory(SSHTransportFactory):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(ParamikoSSHTransportFactory, self).__init__()
        self.sock: socket | None = None

    def create(self) -> Transport:
        sock = SocketFactory().create(self.conf["host"], self.conf["port"])
        return Transport(sock, gss_kex=False)
