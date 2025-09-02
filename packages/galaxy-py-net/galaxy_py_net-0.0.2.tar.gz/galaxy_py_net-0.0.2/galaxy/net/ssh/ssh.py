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

from abc import ABC,                                                \
                abstractmethod
from paramiko import client
from typing import Any,                                             \
                   Tuple
from asyncio import Future,                                         \
                    Queue
from asyncssh.connection import SSHClientConnection,                \
                                create_connection
from asyncssh.session import SSHClientSession
from asyncssh.channel import SSHClientChannel
import asyncssh

from galaxy.utils.base import Component,                            \
                              Configurable
from galaxy.kernel.loop import AsyncioLoop
from galaxy.net.net import Client,                                  \
                           AsyncClient,                             \
                           Server,                                  \
                           AsyncServer
from galaxy.net.auth import CredentialBuilder,                      \
                            Credential
from galaxy.net.ssh.transport import SSHTransportFactory
from galaxy.net.ssh.protocol import SSHProtocolFactory
from galaxy.net.ssh.session import SSHSessionFactory
from galaxy.service.log import LogService,                          \
                               LogAsyncService
from galaxy.perfo.decorator import timed,                           \
                                   async_timed


class SSHConnectionFactory(Component, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(SSHConnectionFactory, self).__init__()
        self.log: LogService | None = None

        # Factory
        self.protocol_fact: SSHProtocolFactory | None = None

    @abstractmethod
    def create(self, client: Any) -> Any:
        raise NotImplementedError("Should implement create()")


class SSHAsyncConnectionFactory(Component, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(SSHAsyncConnectionFactory, self).__init__()
        self._cred: Credential | None = None
        self.log: LogAsyncService | None = None
        self.loop: AsyncioLoop | None = None
        self.conf: dict[str, Any] | None = None

        # Factory
        self.protocol_fact: SSHProtocolFactory | None = None

    def from_conf(self, conf: dict[str, Any]) -> "SSHAsyncConnectionFactory":
        self.conf = conf

        # Credential
        self._cred = CredentialBuilder().from_conf(self.conf["cred"]).build()

        return self

    @abstractmethod
    async def create(self, client: Any) -> Any:
        raise NotImplementedError("Should implement create()")


class AsyncSSHAsyncConnectionFactory(SSHAsyncConnectionFactory):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(AsyncSSHAsyncConnectionFactory, self).__init__()

    async def create(self, client: Any) -> Tuple[SSHClientConnection, asyncssh.SSHClient]:
        # options parameter do not work, parameters are overridden in method "connect", file asyncssh/connection.py, line 8743
        # new_options = await SSHServerConnectionOptions.construct(options, config=config, **kwargs)
        # With respect of the comment, options are used when starting the reverse-direction of an SSH server

        # opts = SSHClientConnectionOptions()
        # opts.prepare(self.loop.loop,
        #              host=self.conf["host"],
        #              port=self.conf["port"],
        #              username=self._cred.username,
        #              password=self._cred.password,
        #              passphrase=self._cred.passphrase,
        #              client_keys=[self._cred.private_key] if self._cred.private_key is not None else None,
        #              known_hosts=None)
        closed = Future()
        queue = Queue()
        return await create_connection(lambda: self.protocol_fact.create(client, closed, queue),
                                       host=self.conf["host"],
                                       port=self.conf["port"],
                                       username=self._cred.username,
                                       password=self._cred.password,
                                       passphrase=self._cred.passphrase,
                                       client_keys=[self._cred.private_key] if self._cred.private_key is not None else None,
                                       known_hosts=None)


class SSHAsyncSessionFactory(Component, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(SSHAsyncSessionFactory, self).__init__()

        # Factory
        self.session_fact: SSHSessionFactory | None = None

    @abstractmethod
    async def create(self, transport: Any, cmd: str) -> Any:
        raise NotImplementedError("Should implement create()")


class AsyncSSHAsyncSessionFactory(SSHAsyncSessionFactory):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(AsyncSSHAsyncSessionFactory, self).__init__()

    async def create(self, transport: asyncssh.SSHClient, cmd: str) -> Tuple[SSHClientChannel, SSHClientSession]:
        closed = Future()
        queue = Queue()
        return await transport.create_session(lambda: self.session_fact.create_session(closed, queue), cmd)


class SSHClient(Client):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(SSHClient, self).__init__()

    @abstractmethod
    def _connect(self) -> None:
        raise NotImplementedError("Should implement _connect()")

    @abstractmethod
    def exec(self, cmd: str) -> None:
        raise NotImplementedError("Should implement exec()")

    @abstractmethod
    def _close(self) -> None:
        raise NotImplementedError("Should implement _close()")

    def __repr__(self) -> str:
        return "<SSHClient(id='{}')>".format(self.id)


class ParamikoSSHClient(SSHClient):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(ParamikoSSHClient, self).__init__()
        self.transport_fact: SSHTransportFactory | None = None
        self.client: client.SSHClient | None = None

    @timed
    def _load(self) -> None:
        super(ParamikoSSHClient, self)._load()

    def _connect(self) -> None:
        if self.client is None:
            self.client = client.SSHClient()
        cred = CredentialBuilder().from_conf(self.conf["cred"]).build()
        self.client.connect(hostname=self.conf["host"],
                            port=self.conf["port"],
                            username=cred.username,
                            password=cred.password)

    def exec(self, cmd: str) -> None:
        pass

    def _close(self) -> None:
        return self.client.close()

    def __repr__(self) -> str:
        return "<ParamikoSSHClient(id='{}')>".format(self.id)


class SSHAsyncClient(AsyncClient, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(SSHAsyncClient, self).__init__()
        self.loop: AsyncioLoop | None = None

        # Factory
        self.conn_fact: SSHAsyncConnectionFactory | None = None
        self.session_fact: SSHAsyncSessionFactory | None = None

    @async_timed
    async def _load(self) -> None:
        await super(SSHAsyncClient, self)._load()

    @abstractmethod
    async def _connect(self) -> None:
        raise NotImplementedError("Should implement _connect()")

    @abstractmethod
    async def exec(self, cmd: str) -> None:
        raise NotImplementedError("Should implement exec()")

    @abstractmethod
    async def _close(self) -> None:
        pass

    def __repr__(self) -> str:
        return "<SSHAsyncClient(id='{}')>".format(self.id)


class AsyncSSHAsyncClient(SSHAsyncClient):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(AsyncSSHAsyncClient, self).__init__()
        self.protocol: SSHClientConnection | None = None
        self.transport: asyncssh.SSHClient | None = None
        self.session: SSHClientSession | None = None

    @async_timed
    async def _load(self) -> None:
        await super(AsyncSSHAsyncClient, self)._load()

    @async_timed
    async def _connect(self) -> None:
        self.transport, self.protocol = await self.conn_fact.from_conf(self.conf).create()

    @async_timed
    async def exec(self, cmd: str) -> None:
        async with self.transport:
            chan, self.session = await self.session_fact.create(self.transport, cmd)
            await chan.wait_closed()

    @async_timed
    async def _close(self) -> None:
        pass

    def __repr__(self) -> str:
        return "<AsyncSSHAsyncClient(id='{}')>".format(self.id)


class SSHServer(Server, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(SSHServer, self).__init__()

    @abstractmethod
    def _start(self) -> None:
        raise NotImplementedError("Should implement _start()")

    @abstractmethod
    def _stop(self) -> None:
        raise NotImplementedError("Should implement _stop()")

    def __repr__(self) -> str:
        return "<SSHServer(id='{}')>".format(self.id)


class SSHAsyncServer(AsyncServer, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(SSHAsyncServer, self).__init__()

    @abstractmethod
    async def _start(self) -> None:
        raise NotImplementedError("Should implement _start()")

    @abstractmethod
    async def _stop(self) -> None:
        raise NotImplementedError("Should implement _stop()")

    def __repr__(self) -> str:
        return "<SSHAsyncServer(id='{}')>".format(self.id)
