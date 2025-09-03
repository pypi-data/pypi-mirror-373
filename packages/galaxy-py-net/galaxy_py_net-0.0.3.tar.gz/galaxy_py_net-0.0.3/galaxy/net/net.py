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

from abc import ABC,                                        \
                abstractmethod
import asyncio
from transitions.core import Machine,                       \
                             EventData
from transitions.extensions.asyncio import AsyncMachine

from galaxy.utils.base import Component,                    \
                              TimestampedState,             \
                              TimestampedAsyncState,        \
                              Configurable
from galaxy.service.service import Manager,                 \
                                   AsyncManager,            \
                                   Service,                 \
                                   AsyncService,            \
                                   LogService,              \
                                   LogAsyncService
from galaxy.service import constant
from galaxy.utils.type import CompId
from galaxy.error.net import NetworkError


class Client(Component, Configurable, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        Component.__init__(self)
        Configurable.__init__(self)
        self._machine: ClientStateMachine = ClientStateMachine(self)
        self.log: LogService | None = None
        self.is_connected: bool = False

    @abstractmethod
    def _connect(self) -> None:
        raise NotImplementedError("Should implement connect()")

    @abstractmethod
    def _close(self) -> None:
        raise NotImplementedError("Should implement close()")

    def accept(self, visitor):
        visitor.visit(self)

    def __repr__(self) -> str:
        return "<Client(id='{}')>".format(self.id)


class ClientState(TimestampedState):
    """
    classdocs
    """

    def __init__(self, name: str, client: Client) -> None:
        """
        Constructor
        """
        super(ClientState, self).__init__(name=name)
        self.client: Client = client


class ClientNewState(ClientState):
    """
    classdocs
    """

    def __init__(self, client: Client) -> None:
        """
        Constructor
        """
        super(ClientNewState, self).__init__(constant.STATE_NEW, client)


class ClientInitiatedState(ClientState):
    """
    classdocs
    """

    def __init__(self, client: Client) -> None:
        """
        Constructor
        """
        super(ClientInitiatedState, self).__init__(constant.STATE_INIT, client)

    def enter(self, event_data: EventData) -> None:
        self.client.log.logger.debug("The client {} is loading".format(self.client))
        self.client._load()
        self.client.log.logger.debug("The client {} is loaded".format(self.client))
        super(ClientInitiatedState, self).enter(event_data)


class ClientConnectedState(ClientState):
    """
    classdocs
    """

    def __init__(self, client: Client) -> None:
        """
        Constructor
        """
        super(ClientConnectedState, self).__init__(constant.STATE_CONNECTED, client)

    def enter(self, event_data: EventData) -> None:
        self.client.is_connected = False
        self.client.log.logger.debug("The client {} is connecting".format(self.client))
        self.client._connect()
        self.client.log.logger.debug("The client {} is connected".format(self.client))
        self.client.is_connected = True
        super(ClientConnectedState, self).enter(event_data)


class ClientClosedState(ClientState):
    """
    classdocs
    """

    def __init__(self, client: Client) -> None:
        """
        Constructor
        """
        super(ClientClosedState, self).__init__(constant.STATE_CLOSED, client)

    def enter(self, event_data: EventData) -> None:
        self.client.log.logger.debug("The client {} is disconnecting".format(self.client))
        self.client._close()
        self.client.log.logger.debug("The client {} is disconnected".format(self.client))
        super(ClientClosedState, self).enter(event_data)


class ClientTimeoutState(ClientState):
    """
    classdocs
    """

    def __init__(self, client: Client) -> None:
        """
        Constructor
        """
        super(ClientTimeoutState, self).__init__(constant.STATE_TIMEOUT, client)


class ClientStateMachine(object):
    """
    classdocs
    """

    def __init__(self, client: Client) -> None:
        """
        Constructor
        """
        self._client: Client = client
        self._init_states()
        self._init_machine()

    def _init_states(self):
        self.states: dict[str, ClientState] = {
                                               constant.STATE_NEW: ClientNewState(self._client),
                                               constant.STATE_INIT: ClientInitiatedState(self._client),
                                               constant.STATE_CONNECTED: ClientConnectedState(self._client),
                                               constant.STATE_CLOSED: ClientClosedState(self._client),
                                               constant.STATE_TIMEOUT: ClientTimeoutState(self._client)
                                              }
        self._transitions: list[dict[str, str]] = [{
                                                    "trigger": "load",
                                                    "source": constant.STATE_NEW,
                                                    "dest": constant.STATE_INIT
                                                   },
                                                   {
                                                    "trigger": "connect",
                                                    "source": constant.STATE_INIT,
                                                    "dest": constant.STATE_CONNECTED
                                                   },
                                                   {
                                                    "trigger": "close",
                                                    "source": constant.STATE_CONNECTED,
                                                    "dest": constant.STATE_CLOSED
                                                   },
                                                   {
                                                    "trigger": "connect",
                                                    "source": constant.STATE_CLOSED,
                                                    "dest": constant.STATE_CONNECTED
                                                   }]

    def _init_machine(self) -> None:
        self.machine: Machine = Machine(model=self._client,
                                        states=[state for state in self.states.values()],
                                        transitions=self._transitions,
                                        initial=self.states[constant.STATE_NEW])


class AsyncClient(Component, Configurable, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        Component.__init__(self)
        Configurable.__init__(self)
        self._machine: ClientAsyncStateMachine = ClientAsyncStateMachine(self)
        self.log: LogAsyncService | None = None

        # Boolean in case of connect() method fails in the transition of the State Machine ClientAsyncStateMachine
        # from STATE_INIT or STATE_CLOSED to STATE_CONNECTED (State class ClientConnectedAsyncState).
        # Could be solved if the State Machine can roll the State STATE_CONNECTED back to the initial State STATE_INIT or STATE_CLOSED.
        # This boolean is used in _send_with_retries() of AioHTTPAsyncClient
        self.is_connected: bool = False

    async def _load(self):
        super(AsyncClient, self)._load()

    @abstractmethod
    async def _connect(self) -> None:
        raise NotImplementedError("Should implement connect()")

    @abstractmethod
    async def _close(self) -> None:
        raise NotImplementedError("Should implement close()")

    def accept(self, visitor):
        visitor.visit(self)

    def __repr__(self) -> str:
        return "<AsyncClient(id='{}')>".format(self.id)


class ClientAsyncState(TimestampedAsyncState):
    """
    classdocs
    """

    def __init__(self, name: str, client: AsyncClient) -> None:
        """
        Constructor
        """
        super(ClientAsyncState, self).__init__(name=name)
        self.client: AsyncClient = client


class ClientNewAsyncState(ClientAsyncState):
    """
    classdocs
    """

    def __init__(self, client: AsyncClient) -> None:
        """
        Constructor
        """
        super(ClientNewAsyncState, self).__init__(constant.STATE_NEW, client)


class ClientInitiatedAsyncState(ClientAsyncState):
    """
    classdocs
    """

    def __init__(self, client: AsyncClient) -> None:
        """
        Constructor
        """
        super(ClientInitiatedAsyncState, self).__init__(constant.STATE_INIT, client)

    async def enter(self, event_data: EventData) -> None:
        self.client.log.logger.debug("The client {} is loading".format(self.client))
        await self.client._load()
        self.client.log.logger.debug("The client {} is loaded".format(self.client))
        await super(ClientInitiatedAsyncState, self).enter(event_data)


class ClientConnectedAsyncState(ClientAsyncState):
    """
    classdocs
    """

    def __init__(self, client: AsyncClient) -> None:
        """
        Constructor
        """
        super(ClientConnectedAsyncState, self).__init__(constant.STATE_CONNECTED, client)

    async def enter(self, event_data: EventData) -> None:
        self.client.is_connected = False
        self.client.log.logger.debug("The client {} is connecting".format(self.client))
        try:
            await self.client._connect()
            self.client.log.logger.debug("The client {} is connected".format(self.client))
            self.client.is_connected = True
            await super(ClientConnectedAsyncState, self).enter(event_data)
        except NetworkError as e:
            self.client.log.logger.error("An error occurred : {}".format(str(e)))
            await self.client.close()


class ClientClosedAsyncState(ClientAsyncState):
    """
    classdocs
    """

    def __init__(self, client: AsyncClient) -> None:
        """
        Constructor
        """
        super(ClientClosedAsyncState, self).__init__(constant.STATE_CLOSED, client)

    async def enter(self, event_data: EventData) -> None:
        self.client.log.logger.debug("The client {} is disconnecting".format(self.client))
        await self.client._close()
        self.client.log.logger.debug("The client {} is disconnected".format(self.client))
        await super(ClientClosedAsyncState, self).enter(event_data)


class ClientTimeoutAsyncState(ClientAsyncState):
    """
    classdocs
    """

    def __init__(self, client: AsyncClient) -> None:
        """
        Constructor
        """
        super(ClientTimeoutAsyncState, self).__init__(constant.STATE_TIMEOUT, client)


class ClientAsyncStateMachine(object):
    """
    classdocs
    """

    def __init__(self, client: AsyncClient) -> None:
        """
        Constructor
        """
        self._client: AsyncClient = client
        self._init_states()
        self._init_machine()

    def _init_states(self):
        self.states: dict[str, ClientAsyncState] = {
                                                    constant.STATE_NEW: ClientNewAsyncState(self._client),
                                                    constant.STATE_INIT: ClientInitiatedAsyncState(self._client),
                                                    constant.STATE_CONNECTED: ClientConnectedAsyncState(self._client),
                                                    constant.STATE_CLOSED: ClientClosedAsyncState(self._client),
                                                    constant.STATE_TIMEOUT: ClientTimeoutAsyncState(self._client)
                                                   }
        self._transitions: list[dict[str, str]] = [{
                                                    "trigger": "load",
                                                    "source": constant.STATE_NEW,
                                                    "dest": constant.STATE_INIT
                                                   },
                                                   {
                                                    "trigger": "connect",
                                                    "source": constant.STATE_INIT,
                                                    "dest": constant.STATE_CONNECTED
                                                   },
                                                   {
                                                    "trigger": "close",
                                                    "source": constant.STATE_CONNECTED,
                                                    "dest": constant.STATE_CLOSED
                                                   },
                                                   {
                                                    "trigger": "connect",
                                                    "source": constant.STATE_CLOSED,
                                                    "dest": constant.STATE_CONNECTED
                                                   }]

    def _init_machine(self):
        self.machine: AsyncMachine = AsyncMachine(model=self._client,
                                                  states=[state for state in self.states.values()],
                                                  transitions=self._transitions,
                                                  initial=self.states[constant.STATE_NEW])


class Server(Component, Configurable, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        Component.__init__(self)
        Configurable.__init__(self)
        self._machine: ServerStateMachine = ServerStateMachine(self)
        self.log: LogService | None = None

    @abstractmethod
    def _start(self) -> None:
        raise NotImplementedError("Should implement _start()")

    @abstractmethod
    def _stop(self) -> None:
        raise NotImplementedError("Should implement _stop()")

    def restart(self) -> None:
        self.stop()
        self.start()

    def accept(self, visitor):
        visitor.visit(self)

    def __repr__(self) -> str:
        return "<Server(id='{}')>".format(self.id)


class ServerState(TimestampedState):
    """
    classdocs
    """

    def __init__(self, name: str, server: Server) -> None:
        """
        Constructor
        """
        super(ServerState, self).__init__(name=name)
        self.server: Server = server


class ServerNewState(ServerState):
    """
    classdocs
    """

    def __init__(self, server: Server) -> None:
        """
        Constructor
        """
        super(ServerNewState, self).__init__(constant.STATE_NEW, server)


class ServerInitiatedState(ServerState):
    """
    classdocs
    """

    def __init__(self, server: Server) -> None:
        """
        Constructor
        """
        super(ServerInitiatedState, self).__init__(constant.STATE_INIT, server)

    def enter(self, event_data: EventData) -> None:
        self.server.log.logger.debug("The server {} is loading".format(self.server))
        self.server._load()
        self.server.log.logger.debug("The server {} is loaded".format(self.server))
        super(ServerInitiatedState, self).enter(event_data)


class ServerRunningState(ServerState):
    """
    classdocs
    """

    def __init__(self, server: Server) -> None:
        """
        Constructor
        """
        super(ServerRunningState, self).__init__(constant.STATE_RUNNING, server)

    def enter(self, event_data: EventData) -> None:
        self.server.log.logger.debug("The server {} is starting".format(self.server))
        self.server._start()
        self.server.log.logger.debug("The server {} is running".format(self.server))
        super(ServerRunningState, self).enter(event_data)


class ServerStoppedState(ServerState):
    """
    classdocs
    """

    def __init__(self, server: Server) -> None:
        """
        Constructor
        """
        super(ServerStoppedState, self).__init__(constant.STATE_STOPPED, server)

    def enter(self, event_data: EventData) -> None:
        self.server.log.logger.debug("The server {} is stopping".format(self.server))
        self.server._stop()
        self.server.log.logger.debug("The server {} is stopped".format(self.server))
        super(ServerStoppedState, self).enter(event_data)


class ServerShutdownState(ServerState):
    """
    classdocs
    """

    def __init__(self, server: Server) -> None:
        """
        Constructor
        """
        super(ServerShutdownState, self).__init__(constant.STATE_SHUTDOWN, server)


class ServerTimeoutState(ServerState):
    """
    classdocs
    """

    def __init__(self, server: Server) -> None:
        """
        Constructor
        """
        super(ServerTimeoutState, self).__init__(constant.STATE_TIMEOUT, server)


class ServerStateMachine(object):
    """
    classdocs
    """

    def __init__(self, server: Server) -> None:
        """
        Constructor
        """
        self._server: Server = server
        self._init_states()
        self._init_machine()

    def _init_states(self) -> None:
        self.states: dict[str, ServerState] = {
                                               constant.STATE_NEW: ServerNewState(self._server),
                                               constant.STATE_INIT: ServerInitiatedState(self._server),
                                               constant.STATE_RUNNING: ServerRunningState(self._server),
                                               constant.STATE_STOPPED: ServerStoppedState(self._server),
                                               constant.STATE_SHUTDOWN: ServerShutdownState(self._server),
                                               constant.STATE_TIMEOUT: ServerTimeoutState(self._server)
                                              }
        self._transitions: list[dict[str, str]] = [{
                                                    "trigger": "load",
                                                    "source": constant.STATE_NEW,
                                                    "dest": constant.STATE_INIT
                                                   },
                                                   {
                                                    "trigger": "start",
                                                    "source": constant.STATE_INIT,
                                                    "dest": constant.STATE_RUNNING
                                                   },
                                                   {
                                                    "trigger": "stop",
                                                    "source": constant.STATE_RUNNING,
                                                    "dest": constant.STATE_STOPPED
                                                   },
                                                   {
                                                    "trigger": "start",
                                                    "source": constant.STATE_STOPPED,
                                                    "dest": constant.STATE_RUNNING
                                                   },
                                                   {
                                                    "trigger": "shutdown",
                                                    "source": constant.STATE_STOPPED,
                                                    "dest": constant.STATE_SHUTDOWN
                                                   }]

    def _init_machine(self) -> None:
        self.machine: Machine = Machine(model=self._server,
                                        states=[state for state in self.states.values()],
                                        transitions=self._transitions,
                                        initial=self.states[constant.STATE_NEW])


class AsyncServer(Component, Configurable, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        Component.__init__(self)
        Configurable.__init__(self)
        self._machine: ServerAsyncStateMachine = ServerAsyncStateMachine(self)
        self.log: LogAsyncService | None = None

    async def _load(self):
        super(AsyncServer, self)._load()

    @abstractmethod
    async def _start(self) -> None:
        raise NotImplementedError("Should implement _start()")

    @abstractmethod
    async def _stop(self) -> None:
        raise NotImplementedError("Should implement _stop()")

    async def restart(self) -> None:
        await self.stop()
        await self.start()

    def accept(self, visitor):
        visitor.visit(self)

    def __repr__(self) -> str:
        return "<AsyncServer(id='{}')>".format(self.id)


class ServerAsyncState(TimestampedAsyncState):
    """
    classdocs
    """

    def __init__(self, name: str, server: AsyncServer) -> None:
        """
        Constructor
        """
        super(ServerAsyncState, self).__init__(name=name)
        self.server: AsyncServer = server


class ServerNewAsyncState(ServerAsyncState):
    """
    classdocs
    """

    def __init__(self, server: AsyncServer) -> None:
        """
        Constructor
        """
        super(ServerNewAsyncState, self).__init__(constant.STATE_NEW, server)


class ServerInitiatedAsyncState(ServerAsyncState):
    """
    classdocs
    """

    def __init__(self, server: AsyncServer) -> None:
        """
        Constructor
        """
        super(ServerInitiatedAsyncState, self).__init__(constant.STATE_INIT, server)

    async def enter(self, event_data: EventData) -> None:
        # Specific case for Notification Server : Log Service is dependent on this server
        if self.server.log is not None:
            self.server.log.logger.debug("The server {} is loading".format(self.server))
        await self.server._load()
        if self.server.log is not None:
            self.server.log.logger.debug("The server {} is loaded".format(self.server))
        await super(ServerInitiatedAsyncState, self).enter(event_data)


class ServerRunningAsyncState(ServerAsyncState):
    """
    classdocs
    """

    def __init__(self, server: AsyncServer) -> None:
        """
        Constructor
        """
        super(ServerRunningAsyncState, self).__init__(constant.STATE_RUNNING, server)

    async def enter(self, event_data: EventData) -> None:
        if self.server.log is not None:
            self.server.log.logger.debug("The server {} is starting".format(self.server))
        await self.server._start()
        if self.server.log is not None:
            self.server.log.logger.debug("The server {} is running".format(self.server))
        await super(ServerRunningAsyncState, self).enter(event_data)


class ServerStoppedAsyncState(ServerAsyncState):
    """
    classdocs
    """

    def __init__(self, server: AsyncServer) -> None:
        """
        Constructor
        """
        super(ServerStoppedAsyncState, self).__init__(constant.STATE_STOPPED, server)

    async def enter(self, event_data: EventData) -> None:
        if self.server.log is not None:
            self.server.log.logger.debug("The server {} is stopping".format(self.server))
        await self.server._stop()
        if self.server.log is not None:
            self.server.log.logger.debug("The server {} is stopped".format(self.server))
        await super(ServerStoppedAsyncState, self).enter(event_data)


class ServerShutdownAsyncState(ServerAsyncState):
    """
    classdocs
    """

    def __init__(self, server: AsyncServer) -> None:
        """
        Constructor
        """
        super(ServerShutdownAsyncState, self).__init__(constant.STATE_SHUTDOWN, server)


class ServerTimeoutAsyncState(ServerAsyncState):
    """
    classdocs
    """

    def __init__(self, server: AsyncServer) -> None:
        """
        Constructor
        """
        super(ServerTimeoutAsyncState, self).__init__(constant.STATE_TIMEOUT, server)


class ServerAsyncStateMachine(object):
    """
    classdocs
    """

    def __init__(self, server: AsyncServer) -> None:
        """
        Constructor
        """
        self._server: AsyncServer = server
        self._init_states()
        self._init_machine()

    def _init_states(self) -> None:
        self.states: dict[str, ServerAsyncState] = {
                                                    constant.STATE_NEW: ServerNewAsyncState(self._server),
                                                    constant.STATE_INIT: ServerInitiatedAsyncState(self._server),
                                                    constant.STATE_RUNNING: ServerRunningAsyncState(self._server),
                                                    constant.STATE_STOPPED: ServerStoppedAsyncState(self._server),
                                                    constant.STATE_SHUTDOWN: ServerShutdownAsyncState(self._server),
                                                    constant.STATE_TIMEOUT: ServerTimeoutAsyncState(self._server)
                                                   }
        self._transitions: list[dict[str, str]] = [{
                                                    "trigger": "load",
                                                    "source": constant.STATE_NEW,
                                                    "dest": constant.STATE_INIT
                                                   },
                                                   {
                                                    "trigger": "start",
                                                    "source": constant.STATE_INIT,
                                                    "dest": constant.STATE_RUNNING
                                                   },
                                                   {
                                                    "trigger": "stop",
                                                    "source": constant.STATE_RUNNING,
                                                    "dest": constant.STATE_STOPPED
                                                   },
                                                   {
                                                    "trigger": "start",
                                                    "source": constant.STATE_STOPPED,
                                                    "dest": constant.STATE_RUNNING
                                                   },
                                                   {
                                                    "trigger": "shutdown",
                                                    "source": constant.STATE_STOPPED,
                                                    "dest": constant.STATE_SHUTDOWN
                                                   }]

    def _init_machine(self):
        self.machine: AsyncMachine = AsyncMachine(model=self._server,
                                                  states=[state for state in self.states.values()],
                                                  transitions=self._transitions,
                                                  initial=self.states[constant.STATE_NEW])


class NetworkService(Service):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(NetworkService, self).__init__()
        self.clients: dict[str, Client] = {}
        self.servers: dict[str, Server] = {}

    def _load(self) -> None:
        super(NetworkService, self)._load()
        [client.load() for client in self.clients.values()]
        [server.load() for server in self.servers.values()]

    def _start(self) -> None:
        [client.connect() for client in self.clients.values()]
        [server.start() for server in self.servers.values()]

    def _stop(self) -> None:
        [client.close() for client in self.clients.values()]
        [server.stop() for server in self.servers.values()]

    def accept(self, visitor):
        visitor.visit(self)

    def __repr__(self) -> str:
        return "<NetworkService(id='{}')>".format(self.id)


class NetworkAsyncService(AsyncService):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(NetworkAsyncService, self).__init__()
        self.clients: dict[str, AsyncClient] = {}
        self.servers: dict[str, AsyncServer] = {}
        self.loop = None

    async def _load(self) -> None:
        await super(NetworkAsyncService, self)._load()
        client_loads = [client.load() for client in self.clients.values()]
        server_loads = [server.load() for server in self.servers.values()]
        results = await asyncio.gather(*[*client_loads, *server_loads])

        # Hack for initialization of logging service for notif zmq publisher
        for server in [server for server in self.servers.values() if server.log is None]:
            server.log = self.log

    async def _start(self) -> None:
        client_connects = [client.connect() for client in self.clients.values()]
        server_starts = [server.start() for server in self.servers.values()]
        results = await asyncio.gather(*[*client_connects, *server_starts])

    async def _stop(self) -> None:
        client_closes = [client.close() for client in self.clients.values()]
        server_stops = [server.stop() for server in self.servers.values()]
        results = await asyncio.gather(*[*client_closes, *server_stops])

    def accept(self, visitor):
        visitor.visit(self)

    def __repr__(self) -> str:
        return "<NetworkAsyncService(id='{}')>".format(self.id)


class NetworkManager(Manager):
    """
    classdocs
    """
    def __init__(self) -> None:
        """
        Constructor
        """
        super(NetworkManager, self).__init__()

    def __repr__(self) -> str:
        return "<NetworkManager(id='{}')>".format(self.id)


class NetworkAsyncManager(AsyncManager):
    """
    classdocs
    """
    def __init__(self) -> None:
        """
        Constructor
        """
        super(NetworkAsyncManager, self).__init__()

    def __repr__(self) -> str:
        return "<NetworkAsyncManager(id='{}')>".format(self.id)
