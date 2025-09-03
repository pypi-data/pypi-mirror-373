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

from abc import ABC,                                    \
                abstractmethod
import sys
from typing import Any
from asyncio import Future,                             \
                    Queue
from asyncssh.session import DataType
from asyncssh.session import SSHClientSession
import asyncssh
from asyncssh.connection import SSHClientConnection

from galaxy.utils.base import Component
from galaxy.service.service import LogService,          \
                                   LogAsyncService


class SSHSessionFactory(Component, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(SSHSessionFactory, self).__init__()
        self.log: LogService | LogAsyncService | None = None

    @abstractmethod
    def create(self, on_close: Future, queue: Queue = None) -> Any:
        raise NotImplementedError("Should implement create()")


class AsyncSSHSession(SSHClientSession):
    """
    classdocs
    """

    def __init__(self, on_close: Future, log: LogService | LogAsyncService, queue: Queue | None = None) -> None:
        """
        Constructor
        """
        super(AsyncSSHSession, self).__init__()
        self.transport: SSHClientConnection | None = None
        self.on_close: Future = on_close
        self.queue: Queue | None = queue
        self.log = log

    def data_received(self, data: str, datatype: DataType) -> None:
        if datatype == asyncssh.constants.EXTENDED_DATA_STDERR:
            print(data, end="", file=sys.stderr)
        elif self.queue is not None:
            self.queue.put_nowait(data)

    def connection_lost(self, ex: Exception | None) -> None:
        if ex:
            print("SSH session error: " + str(ex), file=sys.stderr)
        self.on_close.set_result(ex)


class AsyncSSHSessionFactory(SSHSessionFactory):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(AsyncSSHSessionFactory, self).__init__()

    def create(self, on_close: Future, queue: Queue | None = None) -> AsyncSSHSession:
        return AsyncSSHSession(on_close, self.log, queue)
