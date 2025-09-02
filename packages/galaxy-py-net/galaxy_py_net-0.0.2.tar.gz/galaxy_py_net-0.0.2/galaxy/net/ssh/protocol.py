#  Copyright (c) 2022-2025 Sucden Financial Limited.
#
#  Written by bastien.saltel.
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

from abc import ABC,                                            \
                abstractmethod
from typing import Any
import asyncio
from asyncio import Future,                                     \
                    Queue
from asyncssh.client import SSHClient
from asyncssh.connection import SSHClientConnection

from galaxy.kernel.loop import AsyncioLoop
from galaxy.utils.base import Component
from galaxy.service.service import LogService,                  \
                                   LogAsyncService
from galaxy.net.ssh.session import AsyncSSHSessionFactory,      \
                                   AsyncSSHSession


class SSHProtocolFactory(Component, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(SSHProtocolFactory, self).__init__()
        self.log: LogService | LogAsyncService | None = None

    @abstractmethod
    def create(self, client: Any) -> Any:
        raise NotImplementedError("Should implement create()")


class AsyncSSHProtocol(SSHClient):
    """
    classdocs
    """

    def __init__(self, client: Any, on_close: Future, log: LogService | LogAsyncService, queue: Queue | None = None) -> None:
        """
        Constructor
        """
        super(AsyncSSHProtocol, self).__init__()
        self.client: Any = client
        self.transport: SSHClientConnection | None = None
        self.session: AsyncSSHSession | None = None
        self.on_close: Future = on_close
        self.queue: Queue | None = queue
        self.log = log

    def connection_made(self, transport: SSHClientConnection) -> None:
        self.transport = transport
        self.log.logger.debug("The client {} is connected".format(self.client))

    def connection_lost(self, ex: Exception | None):
        if ex is not None:
            self.log.logger.debug("The connection of the client {} has been lost : {}".format(self.client, ex))
            self.on_close.set_result(ex)
        else:
            self.log.logger.debug("The client {} has been disconnected".format(self.client))

    def auth_completed(self) -> None:
        pass


class AsyncSSHProtocolFactory(Component):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(AsyncSSHProtocolFactory, self).__init__()
        self.log: LogService | LogAsyncService | None = None

        # Factory
        self.session_fact: AsyncSSHSessionFactory | None = None

    def create(self, client: Any, on_close: Future, queue: Queue | None = None) -> AsyncSSHProtocol:
        protocol = AsyncSSHProtocol(client, on_close, self.log, queue)
        protocol.session = self.session_fact.create(on_close, queue)
        return protocol
