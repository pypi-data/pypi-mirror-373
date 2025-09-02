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

import stat
from abc import ABC,                                \
                abstractmethod

from galaxy.net.net import Client,                  \
                           AsyncClient,             \
                           Server,                  \
                           AsyncServer
from galaxy.net.ssh.transport import SSHTransportFactory
from galaxy.perfo.decorator import timed,                               \
                                   async_timed


class SCPClient(Client, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(SCPClient, self).__init__()

    @abstractmethod
    def _connect(self) -> None:
        raise NotImplementedError("Should implement _connect()")

    @abstractmethod
    def scp(self, path: str) -> None:
        raise NotImplementedError("Should implement scp()")

    @abstractmethod
    def _close(self) -> None:
        raise NotImplementedError("Should implement _close()")

    def __repr__(self) -> str:
        return "<SFTPClient(id='{}')>".format(self.id)


class ParamikoSCPClient(SCPClient):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(ParamikoSCPClient, self).__init__()
        self.transport_fact: SSHTransportFactory | None = None
        self.client = None

    @timed
    def _load(self) -> None:
        super(ParamikoSCPClient, self)._load()
        if self.transport_fact is not None:
            self.transport_fact._load()

    def _connect(self) -> None:
        if self.client is None:
            raise

    def scp(self, path: str) -> None:
        return self.client.chdir(path)

    def _close(self) -> None:
        return self.client.close()

    def __repr__(self) -> str:
        return "<SCPClient(id='{}')>".format(self.id)


class SCPAsyncClient(AsyncClient, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(SCPAsyncClient, self).__init__()

    @abstractmethod
    async def _connect(self) -> None:
        raise NotImplementedError("Should implement _connect()")

    @abstractmethod
    async def scp(self, path: str) -> None:
        raise NotImplementedError("Should implement scp()")

    @abstractmethod
    async def _close(self) -> None:
        pass

    def __repr__(self) -> str:
        return "<SFTPAsyncClient(id='{}')>".format(self.id)


class SCPServer(Server, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(SCPServer, self).__init__()

    @abstractmethod
    def _start(self) -> None:
        raise NotImplementedError("Should implement _start()")

    @abstractmethod
    def _stop(self) -> None:
        raise NotImplementedError("Should implement _stop()")

    def __repr__(self) -> str:
        return "<SFTPServer(id='{}')>".format(self.id)


class SCPAsyncServer(AsyncServer, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(SCPAsyncServer, self).__init__()

    @abstractmethod
    async def _start(self) -> None:
        raise NotImplementedError("Should implement _start()")

    @abstractmethod
    async def _stop(self) -> None:
        raise NotImplementedError("Should implement _stop()")

    def __repr__(self) -> str:
        return "<SCPAsyncServer(id='{}')>".format(self.id)
