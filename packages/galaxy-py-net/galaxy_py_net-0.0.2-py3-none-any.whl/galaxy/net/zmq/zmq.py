#  Copyright (c) 2022-2023 Sucden Financial Limited.
#
#  Written by bastien.saltel.
#
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

from uuid import UUID
import zmq
from zmq import ZMQError,                                   \
                Context,                                    \
                Socket,                                     \
                Poller
from zmq.eventloop.zmqstream import ZMQStream
from asyncio import Future,                                 \
                    Queue
from aiozmq.core import create_zmq_connection
from aiozmq.interface import ZmqTransport,                  \
                             ZmqProtocol
from collections.abc import Iterable
import errno
from logging import getLogger,                              \
                    Formatter,                              \
                    StreamHandler,                          \
                    BASIC_FORMAT
from abc import ABC,                                        \
                abstractmethod
from threading import Thread, Event
import time
from ipykernel.iostream import IOPubThread
from jupyter_client.blocking import BlockingKernelClient
from jupyter_client.session import Session
from IPython.core.profiledir import ProfileDir
from tornado import ioloop
from typing import Any,                                     \
                   Tuple

from galaxy.net.net import Server,                          \
                           AsyncServer,                     \
                           Client,                          \
                           AsyncClient
from galaxy.net import constant
from galaxy.net.endpoint import EndpointBuilder,            \
                                Endpoint
from galaxy.net.zmq.protocol import ZmqProtocolFactory
from galaxy.data.serial import Serializer,                  \
                               NoSerializer
from galaxy.net.compression import Compressor,              \
                                   NoCompressor
from galaxy.kernel.loop import AsyncioLoop
from galaxy.utils.base import Component,                    \
                              Configurable
from galaxy.service.log import LogService,                  \
                               LogAsyncService
from galaxy.perfo.decorator import timed,                   \
                                   async_timed


class ZmqConnectionFactory(Component, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(ZmqConnectionFactory, self).__init__()
        self.log: LogService | None = None

        # Factory
        self.protocol_fact: ZmqProtocolFactory | None = None

    @abstractmethod
    def create(self, zmq_type: str) -> Any:
        raise NotImplementedError("Should implement create()")


class ZmqAsyncConnectionFactory(Component, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(ZmqAsyncConnectionFactory, self).__init__()
        self._endpoint: Endpoint | None = None
        self.log: LogAsyncService | None = None
        self.loop: AsyncioLoop | None = None

        # Factory
        self.protocol_fact: ZmqProtocolFactory | None = None

    def from_conf(self, conf: dict[str, Any]) -> "ZmqAsyncConnectionFactory":
        # Endpoint
        self._endpoint = EndpointBuilder().from_conf(conf).build()

        return self

    @abstractmethod
    async def create(self, zmq_type: str) -> Any:
        raise NotImplementedError("Should implement create()")


class AioZmqAsyncServerConnectionFactory(ZmqAsyncConnectionFactory):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(AioZmqAsyncServerConnectionFactory, self).__init__()

    async def create(self, zmq_type: str) -> Tuple[ZmqTransport, ZmqProtocol]:
        closed = Future()
        queue = Queue()
        return await create_zmq_connection(lambda: self.protocol_fact.create(closed, queue),
                                           constant.ZMQ_TYPES[zmq_type],
                                           bind=str(self._endpoint),
                                           loop=self.loop.loop)


class AioZmqAsyncClientConnectionFactory(ZmqAsyncConnectionFactory):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(AioZmqAsyncClientConnectionFactory, self).__init__()

    async def create(self, zmq_type: str) -> Tuple[ZmqTransport, ZmqProtocol]:
        closed = Future()
        queue = Queue()
        return await create_zmq_connection(lambda: self.protocol_fact.create(closed, queue),
                                           constant.ZMQ_TYPES[zmq_type],
                                           connect=str(self._endpoint),
                                           loop=self.loop.loop)


class ZmqServer(Server, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(ZmqServer, self).__init__()
        self.serializer: Serializer = NoSerializer()
        self.compressor: Compressor = NoCompressor()

        # Factory
        self.conn_fact: ZmqConnectionFactory | None = None

    @timed
    def _load(self) -> None:
        super(ZmqServer, self)._load()
        if self.conn_fact is not None:
            self.conn_fact._load()

    @abstractmethod
    def _start(self) -> None:
        raise NotImplementedError("Should implement _start()")

    @abstractmethod
    def _stop(self) -> None:
        raise NotImplementedError("Should implement _stop()")

    @abstractmethod
    def send(self, data: Iterable[bytes] | Iterable[bytearray] | Iterable[memoryview]) -> None:
        raise NotImplementedError("Should implement send()")

    def __repr__(self) -> str:
        return "<ZmqServer(id='{}')>".format(self.id)


class ZmqAsyncServer(AsyncServer, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(ZmqAsyncServer, self).__init__()
        self.protocol: ZmqProtocol | None = None
        self.transport: ZmqTransport | None = None
        self.serializer: Serializer = NoSerializer()
        self.compressor: Compressor = NoCompressor()

        # Factory
        self.conn_fact: ZmqAsyncConnectionFactory | None = None

    @async_timed
    async def _load(self) -> None:
        await super(ZmqAsyncServer, self)._load()

    @abstractmethod
    async def _start(self) -> None:
        raise NotImplementedError("Should implement _start()")

    @abstractmethod
    async def _stop(self) -> None:
        raise NotImplementedError("Should implement _stop()")

    @abstractmethod
    def send(self, data: Iterable[bytes] | Iterable[bytearray] | Iterable[memoryview]) -> None:
        raise NotImplementedError("Should implement send()")

    def __repr__(self):
        return "<ZmqAsyncServer(id='{}')>".format(self.id)


class AioZmqAsyncServer(ZmqAsyncServer):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(AioZmqAsyncServer, self).__init__()
        self.protocol: ZmqProtocol | None = None
        self.transport: ZmqTransport | None = None

    @async_timed
    async def _load(self) -> None:
        await super(AioZmqAsyncServer, self)._load()

    @async_timed
    async def _start(self) -> None:
        self.transport, self.protocol = await self.conn_fact.from_conf(self.conf["endpoint"]).create(self.conf["zmq_type"])

        if "socket_options" in self.conf:
            for option, value in self.conf["socket_options"].items():
                if option == "SUBSCRIBE":
                    self.transport.setsockopt(constant.ZMQ_SOCKET_OPTIONS(option), value.bytes)
                elif option in ["IDENTITY", "ROUTING_ID"]:
                    self.transport.setsockopt(constant.ZMQ_SOCKET_OPTIONS[option], UUID(value).bytes)
                else:
                    self.transport.setsockopt(constant.ZMQ_SOCKET_OPTIONS(option), value)

    @async_timed
    async def _stop(self) -> None:
        self.transport.close()

    @timed
    def send(self, data: Iterable[bytes] | Iterable[bytearray] | Iterable[memoryview]) -> None:
        self.transport.write(data)

    def __repr__(self):
        return "<AioZmqAsyncServer(id='{}')>".format(self.id)


class ZmqClient(Client, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(ZmqClient, self).__init__()
        self.serializer: Serializer = NoSerializer()
        self.compressor: Compressor = NoCompressor()

        # Factory
        self.conn_fact: ZmqConnectionFactory | None = None

    @timed
    def _load(self) -> None:
        super(ZmqClient, self)._load()

    @abstractmethod
    def _connect(self) -> None:
        raise NotImplementedError("Should implement _connect()")

    @abstractmethod
    async def _close(self) -> None:
        raise NotImplementedError("Should implement _close()")

    @abstractmethod
    def send(self, data: Iterable[bytes] | Iterable[bytearray] | Iterable[memoryview]) -> None:
        raise NotImplementedError("Should implement send()")

    def __repr__(self) -> str:
        return "<ZmqClient(id='{}')>".format(self.id)


class ZmqAsyncClient(AsyncClient, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(ZmqAsyncClient, self).__init__()
        self.serializer: Serializer = NoSerializer()
        self.compressor: Compressor = NoCompressor()

        # Factory
        self.conn_fact: ZmqAsyncConnectionFactory | None = None

    @async_timed
    async def _load(self) -> None:
        await super(ZmqAsyncClient, self)._load()

    @abstractmethod
    def _connect(self) -> None:
        raise NotImplementedError("Should implement _connect()")

    @abstractmethod
    async def _close(self) -> None:
        raise NotImplementedError("Should implement _close()")

    @abstractmethod
    def send(self, data: Iterable[bytes] | Iterable[bytearray] | Iterable[memoryview]) -> None:
        raise NotImplementedError("Should implement send()")

    def __repr__(self) -> str:
        return "<ZmqAsyncClient(id='{}')>".format(self.id)


class AioZmqAsyncClient(ZmqAsyncClient):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(AioZmqAsyncClient, self).__init__()
        self.protocol: ZmqProtocol | None = None
        self.transport: ZmqTransport | None = None

    @async_timed
    async def _load(self) -> None:
        await super(AioZmqAsyncClient, self)._load()

    @async_timed
    async def _connect(self) -> None:
        self.transport, self.protocol = await self.conn_fact.from_conf(self.conf["endpoint"]).create(self.conf["zmq_type"])

        if "socket_options" in self.conf:
            for option, value in self.conf["socket_options"].items():
                if option == "SUBSCRIBE":
                    self.transport.setsockopt(constant.ZMQ_SOCKET_OPTIONS[option], bytes(value, "utf-8"))
                elif option in ["IDENTITY", "ROUTING_ID"]:
                    self.transport.setsockopt(constant.ZMQ_SOCKET_OPTIONS[option], UUID(value).bytes)
                else:
                    self.transport.setsockopt(constant.ZMQ_SOCKET_OPTIONS[option], value)

    @async_timed
    async def _close(self) -> None:
        self.transport.close()

    @timed
    def send(self, data: Iterable[bytes] | Iterable[bytearray] | Iterable[memoryview]) -> None:
        self.transport.write(data)

    def __repr__(self) -> str:
        return "<AioZmqAsyncClient(id='{}')>".format(self.id)

# class ZmqRouter(ZmqServer, ABC):
#     """
#     classdocs
#     """
#
#     def __init__(self) -> None:
#         """
#         Constructor
#         """
#         super(ZmqRouter, self).__init__()
#         self.socket_type: int = zmq.ROUTER
#         self.stream: ZMQStream | None = None
#
#     def _start(self) -> None:
#         super(ZmqRouter, self)._start()
#         self.stream = ZMQStream(self.socket)
#         if hasattr(zmq, 'ROUTER_HANDOVER'):
#             # set router-handover to workaround zeromq reconnect problems
#             # in certain rare circumstances
#             # see ipython/ipykernel#270 and zeromq/libzmq#2892
#             self.socket.router_handover = 1
#
#     def _stop(self) -> None:
#         super(ZmqRouter, self)._stop()
#
#     def __repr__(self) -> str:
#         return "<ZmqRouter(id='{}')>".format(self.id)
#
#
# class ZmqAsyncRouter(ZmqAsyncServer, ABC):
#     """
#     classdocs
#     """
#
#     def __init__(self) -> None:
#         """
#         Constructor
#         """
#         super(ZmqAsyncRouter, self).__init__()
#         self.socket_type: int = zmq.ROUTER
#         self.stream: ZMQStream | None = None
#
#     async def _start(self) -> None:
#         await super(ZmqAsyncRouter, self)._start()
#         self.stream = ZMQStream(self.socket)
#         if hasattr(zmq, 'ROUTER_HANDOVER'):
#             # set router-handover to workaround zeromq reconnect problems
#             # in certain rare circumstances
#             # see ipython/ipykernel#270 and zeromq/libzmq#2892
#             self.socket.router_handover = 1
#
#     async def _stop(self) -> None:
#         await super(ZmqAsyncRouter, self)._stop()
#
#     def __repr__(self) -> str:
#         return "<ZmqAsyncRouter(id='{}')>".format(self.id)
#
#
# class HeartbeatZmqRouterThread(Thread):
#     """
#     classdocs
#     """
#
#     def __init__(self, socket) -> None:
#         """
#         Constructor
#         """
#         super(HeartbeatZmqRouterThread, self).__init__()
#         self.socket: Socket = socket
#
#     def run(self) -> None:
#         while True:
#             try:
#                 zmq.device(zmq.QUEUE, self.socket, self.socket)
#             except zmq.ZMQError as e:
#                 if e.errno == errno.EINTR:
#                     # signal interrupt, resume heartbeat
#                     continue
#                 elif e.errno == zmq.ETERM:
#                     # context terminated, close socket and exit
#                     try:
#                         self.socket.close()
#                     except zmq.ZMQError:
#                         # suppress further errors during cleanup
#                         # this shouldn't happen, though
#                         pass
#                     break
#                 elif e.errno == zmq.ENOTSOCK:
#                     # socket closed elsewhere, exit
#                     break
#                 else:
#                     raise
#             else:
#                 break
#
#
# class HeartbeatZmqRouter(ZmqRouter):
#     """
#     classdocs
#     """
#
#     def __init__(self) -> None:
#         """
#         Constructor
#         """
#         super(HeartbeatZmqRouter, self).__init__()
#         self.thread: HeartbeatZmqRouterThread | None = None
#
#     def _start(self) -> None:
#         super(HeartbeatZmqRouter, self)._start()
#         self.thread = HeartbeatZmqRouterThread(self.socket)
#         self.log.logger.debug("The heartbeat ROUTER socket is opened on {}".format(self.conf["port"]))
#         self.thread.start()
#
#     def _stop(self) -> None:
#         super(HeartbeatZmqRouter, self)._stop()
#         self.thread.join()
#
#     def __repr__(self) -> str:
#         return "<HeartbeatZmqRouter(id='{}')>".format(self.id)
#
#
# class HeartbeatZmqAsyncRouter(ZmqAsyncRouter):
#     """
#     classdocs
#     """
#
#     def __init__(self) -> None:
#         """
#         Constructor
#         """
#         super(HeartbeatZmqAsyncRouter, self).__init__()
#
#     async def _start(self) -> None:
#         await super(HeartbeatZmqAsyncRouter, self)._start()
#         self.log.logger.debug("Heartbeat REP Channel on port: {}".format(self.conf["port"]))
#
#     async def _stop(self) -> None:
#         await super(HeartbeatZmqAsyncRouter, self)._stop()
#
#     def __repr__(self) -> str:
#         return "<HeartbeatZmqAsyncRouter(id='{}')>".format(self.id)
#
#
# class HeartbeatZmqService(NetworkService):
#     """
#     classdocs
#     """
#
#     def __init__(self) -> None:
#         """
#         Constructor
#         """
#         super(HeartbeatZmqService, self).__init__()
#         self.pub_server = None
#         self.router_client = None
#
#     def _load(self) -> None:
#         super(HeartbeatZmqService, self)._load()
#         self.router_client.stream.on_recv(self.handle_pong)
#
#     def _start(self) -> None:
#         self.tic = time.time()
#         io_loop = ioloop.IOLoop.current()
#         self.caller = io_loop.PeriodicCallback(self.beat, self.period)
#         self.caller.start()
#
#     def _stop(self) -> None:
#         super(HeartbeatZmqRouter, self)._stop()
#         self.thread.join()
#
#     def __repr__(self) -> str:
#         return "<HeartbeatZmqRouter(id='{}')>".format(self.id)
#
#
# class ShellZmqRouter(ZmqRouter):
#     """
#     classdocs
#     """
#
#     def __init__(self) -> None:
#         """
#         Constructor
#         """
#         super(ShellZmqRouter, self).__init__()
#
#     def _start(self) -> None:
#         super(ShellZmqRouter, self)._start()
#
#     def _stop(self) -> None:
#         super(ShellZmqRouter, self)._stop()
#
#     def __repr__(self) -> str:
#         return "<ShellZmqRouter(id='{}')>".format(self.id)
#
#
# class ShellZmqAsyncRouter(ZmqAsyncRouter):
#     """
#     classdocs
#     """
#
#     def __init__(self) -> None:
#         """
#         Constructor
#         """
#         super(ShellZmqAsyncRouter, self).__init__()
#
#     async def _start(self) -> None:
#         await super(ShellZmqAsyncRouter, self)._start()
#
#     async def _stop(self) -> None:
#         await super(ShellZmqAsyncRouter, self)._stop()
#
#     def __repr__(self) -> str:
#         return "<ShellZmqRouter(id='{}')>".format(self.id)
#
#
# class StdinZmqRouter(ZmqRouter):
#     """
#     classdocs
#     """
#
#     def __init__(self) -> None:
#         """
#         Constructor
#         """
#         super(StdinZmqRouter, self).__init__()
#
#     def _start(self) -> None:
#         super(StdinZmqRouter, self)._start()
#
#     def _stop(self) -> None:
#         pass
#
#     def __repr__(self) -> str:
#         return "<StdinZmqRouter(id='{}')>".format(self.id)
#
#
# class StdinZmqAsyncRouter(ZmqAsyncRouter):
#     """
#     classdocs
#     """
#
#     def __init__(self) -> None:
#         """
#         Constructor
#         """
#         super(StdinZmqAsyncRouter, self).__init__()
#
#     async def _start(self) -> None:
#         super(StdinZmqAsyncRouter, self)._start()
#
#     async def _stop(self) -> None:
#         pass
#
#     def __repr__(self) -> str:
#         return "<StdinZmqAsyncRouter(id='{}')>".format(self.id)
#
#
# class ControlZmqRouter(ZmqRouter):
#     """
#     classdocs
#     """
#
#     def __init__(self) -> None:
#         """
#         Constructor
#         """
#         super(ControlZmqRouter, self).__init__()
#
#     def _start(self) -> None:
#         super(ControlZmqRouter, self)._start()
#
#     def _stop(self) -> None:
#         pass
#
#     def __repr__(self) -> str:
#         return "<ControlZmqRouter(id='{}')>".format(self.id)
#
#
# class ControlZmqAsyncRouter(ZmqAsyncRouter):
#     """
#     classdocs
#     """
#
#     def __init__(self) -> None:
#         """
#         Constructor
#         """
#         super(ControlZmqAsyncRouter, self).__init__()
#
#     async def _start(self) -> None:
#         super(ControlZmqAsyncRouter, self)._start()
#
#     async def _stop(self) -> None:
#         pass
#
#     def __repr__(self) -> str:
#         return "<ControlZmqAsyncRouter(id='{}')>".format(self.id)
#
#
# class CommandZmqRouter(ZmqRouter):
#     """
#     classdocs
#     """
#
#     def __init__(self) -> None:
#         """
#         Constructor
#         """
#         super(CommandZmqRouter, self).__init__()
#
#     def _start(self) -> None:
#         super(CommandZmqRouter, self)._start()
#
#     def _stop(self) -> None:
#         pass
#
#     def __repr__(self) -> str:
#         return "<CommandZmqRouter(id='{}')>".format(self.id)
#
#
# class CommandZmqAsyncRouter(ZmqAsyncRouter):
#     """
#     classdocs
#     """
#
#     def __init__(self) -> None:
#         """
#         Constructor
#         """
#         super(CommandZmqAsyncRouter, self).__init__()
#
#     async def _start(self) -> None:
#         await super(CommandZmqAsyncRouter, self)._start()
#
#     async def _stop(self) -> None:
#         await super(CommandZmqAsyncRouter, self)._stop()
#
#     def __repr__(self) -> str:
#         return "<CommandZmqAsyncRouter(id='{}')>".format(self.id)
#
#
# class ZmqPublisher(ZmqServer, ABC):
#     """
#     classdocs
#     """
#
#     def __init__(self) -> None:
#         """
#         Constructor
#         """
#         super(ZmqPublisher, self).__init__()
#         self.socket_type = zmq.PUB
#
#     def _start(self) -> None:
#         super(ZmqPublisher, self)._start()
#
#     def _stop(self) -> None:
#         super(ZmqPublisher, self)._stop()
#
#     def __repr__(self) -> str:
#         return "<ZmqPublisher(id='{}')>".format(self.id)
#
#
# class ZmqAsyncPublisher(ZmqAsyncServer, ABC):
#     """
#     classdocs
#     """
#
#     def __init__(self):
#         """
#         Constructor
#         """
#         super(ZmqAsyncPublisher, self).__init__()
#         self.socket_type = zmq.PUB
#
#     async def _start(self):
#         await super(ZmqAsyncPublisher, self)._start()
#
#     async def _stop(self):
#         await super(ZmqAsyncPublisher, self)._stop()
#
#     def __repr__(self):
#         return "<ZmqAsyncPublisher(id='{}')>".format(self.id)
#
#
# class IOZmqPublisher(ZmqPublisher):
#     """
#     classdocs
#     """
#
#     def __init__(self) -> None:
#         """
#         Constructor
#         """
#         super(IOZmqPublisher, self).__init__()
#         self.thread = None
#
#     def _start(self) -> None:
#         super(IOZmqPublisher, self)._start()
#         self._configure_tornado_logger()
#         self.thread = IOPubThread(self.socket, pipe=True)
#         self.thread.start()
#         self.socket = self.thread.background_socket
#
#     def _configure_tornado_logger(self) -> None:
#         logger = getLogger('tornado')
#         handler = StreamHandler()
#         formatter = Formatter(BASIC_FORMAT)
#         handler.setFormatter(formatter)
#         logger.addHandler(handler)
#
#     def _stop(self) -> None:
#         super(IOZmqPublisher, self)._stop()
#         self.thread.stop()
#         self.thread.close()
#
#     def __repr__(self) -> str:
#         return "<IOZmqPublisher(id='{}')>".format(self.id)
#
#
# class IOZmqAsyncPublisher(ZmqAsyncPublisher):
#     """
#     classdocs
#     """
#
#     def __init__(self) -> None:
#         """
#         Constructor
#         """
#         super(IOZmqAsyncPublisher, self).__init__()
#         self.thread = None
#
#     async def _start(self) -> None:
#         await super(IOZmqAsyncPublisher, self)._start()
#
#     async def _stop(self) -> None:
#         await super(IOZmqAsyncPublisher, self)._stop()
#
#     def __repr__(self) -> str:
#         return "<IOZmqAsyncPublisher(id='{}')>".format(self.id)
#
#
# class NotifZmqPublisher(ZmqPublisher):
#     """
#     classdocs
#     """
#
#     def __init__(self) -> None:
#         """
#         Constructor
#         """
#         super(NotifZmqPublisher, self).__init__()
#
#     def _start(self) -> None:
#         super(NotifZmqPublisher, self)._start()
#
#     def _stop(self) -> None:
#         super(NotifZmqPublisher, self)._stop()
#
#     def __repr__(self) -> str:
#         return "<NotifZmqPublisher(id='{}')>".format(self.id)
#
#
# class NotifZmqAsyncPublisher(ZmqAsyncPublisher):
#     """
#     classdocs
#     """
#
#     def __init__(self) -> None:
#         """
#         Constructor
#         """
#         super(NotifZmqAsyncPublisher, self).__init__()
#
#     async def _start(self) -> None:
#         await super(NotifZmqAsyncPublisher, self)._start()
#
#     async def _stop(self) -> None:
#         await super(NotifZmqAsyncPublisher, self)._stop()
#
#     def __repr__(self) -> str:
#         return "<NotifZmqAsyncPublisher(id='{}')>".format(self.id)
#
#
# class MonitorZmqPublisher(ZmqPublisher):
#     """
#     classdocs
#     """
#
#     def __init__(self) -> None:
#         """
#         Constructor
#         """
#         super(MonitorZmqPublisher, self).__init__()
#
#     def _start(self) -> None:
#         super(MonitorZmqPublisher, self)._start()
#
#     def _stop(self) -> None:
#         super(MonitorZmqPublisher, self)._stop()
#
#     def __repr__(self) -> str:
#         return "<MonitorZmqPublisher(id='{}')>".format(self.id)
#
#
# class MonitorZmqAsyncPublisher(ZmqAsyncPublisher):
#     """
#     classdocs
#     """
#
#     def __init__(self) -> None:
#         """
#         Constructor
#         """
#         super(MonitorZmqAsyncPublisher, self).__init__()
#
#     async def _start(self) -> None:
#         await super(MonitorZmqAsyncPublisher, self)._start()
#
#     async def _stop(self) -> None:
#         await super(MonitorZmqAsyncPublisher, self)._stop()
#
#     def __repr__(self) -> str:
#         return "<MonitorZmqAsyncPublisher(id='{}')>".format(self.id)
#
#
# class DataZmqPublisher(ZmqPublisher):
#     """
#     classdocs
#     """
#
#     def __init__(self) -> None:
#         """
#         Constructor
#         """
#         super(DataZmqPublisher, self).__init__()
#
#     def _start(self) -> None:
#         super(DataZmqPublisher, self)._start()
#
#     def _stop(self) -> None:
#         super(DataZmqPublisher, self)._stop()
#
#     def __repr__(self) -> str:
#         return "<DataZmqPublisher(id='{}')>".format(self.id)
#
#
# class DataZmqAsyncPublisher(ZmqAsyncPublisher):
#     """
#     classdocs
#     """
#
#     def __init__(self) -> None:
#         """
#         Constructor
#         """
#         super(DataZmqAsyncPublisher, self).__init__()
#
#     async def _start(self) -> None:
#         await super(DataZmqAsyncPublisher, self)._start()
#
#     async def _stop(self) -> None:
#         await super(DataZmqAsyncPublisher, self)._stop()
#
#     def __repr__(self) -> str:
#         return "<DataZmqAsyncPublisher(id='{}')>".format(self.id)
#
#
# class ZmqDealer(ZmqClient, ABC):
#     """
#     classdocs
#     """
#
#     def __init__(self) -> None:
#         """
#         Constructor
#         """
#         super(ZmqDealer, self).__init__()
#         self.socket_type = zmq.DEALER
#
#     def _connect(self) -> None:
#         super(ZmqDealer, self)._connect()
#
#     def _disconnect(self) -> None:
#         super(ZmqDealer, self)._disconnect()
#
#     def _close(self) -> None:
#         super(ZmqDealer, self)._close()
#
#     def __repr__(self) -> str:
#         return "<ZmqDealer(id='{}')>".format(self.id)
#
#
# class ZmqAsyncDealer(ZmqAsyncClient, ABC):
#     """
#     classdocs
#     """
#
#     def __init__(self) -> None:
#         """
#         Constructor
#         """
#         super(ZmqAsyncDealer, self).__init__()
#         self.socket_type = zmq.DEALER
#
#     async def _connect(self) -> None:
#         await super(ZmqAsyncDealer, self)._connect()
#
#     async def _disconnect(self) -> None:
#         await super(ZmqAsyncDealer, self)._disconnect()
#
#     async def _close(self) -> None:
#         await super(ZmqAsyncDealer, self)._close()
#
#     def __repr__(self) -> str:
#         return "<ZmqAsyncDealer(id='{}')>".format(self.id)
#
#
# class ShellZmqDealer(ZmqDealer):
#     """
#     classdocs
#     """
#
#     def __init__(self) -> None:
#         """
#         Constructor
#         """
#         super(ShellZmqDealer, self).__init__()
#
#     def _connect(self) -> None:
#         super(ShellZmqDealer, self)._connect()
#
#     def _disconnect(self) -> None:
#         super(ShellZmqDealer, self)._disconnect()
#
#     def _close(self) -> None:
#         super(ShellZmqDealer, self)._close()
#
#     def __repr__(self) -> str:
#         return "<ShellZmqDealer(id='{}')>".format(self.id)
#
#
# class ShellZmqAsyncDealer(ZmqAsyncDealer):
#     """
#     classdocs
#     """
#
#     def __init__(self) -> None:
#         """
#         Constructor
#         """
#         super(ShellZmqAsyncDealer, self).__init__()
#
#     async def _connect(self) -> None:
#         await super(ShellZmqAsyncDealer, self)._connect()
#
#     async def _disconnect(self) -> None:
#         await super(ShellZmqAsyncDealer, self)._disconnect()
#
#     async def _close(self) -> None:
#         await super(ShellZmqAsyncDealer, self)._close()
#
#     def __repr__(self) -> str:
#         return "<ShellZmqAsyncDealer(id='{}')>".format(self.id)
#
#
# class StdinZmqDealer(ZmqDealer):
#     """
#     classdocs
#     """
#
#     def __init__(self) -> None:
#         """
#         Constructor
#         """
#         super(StdinZmqDealer, self).__init__()
#
#     def _connect(self) -> None:
#         super(StdinZmqDealer, self)._connect()
#
#     def _disconnect(self) -> None:
#         super(StdinZmqDealer, self)._disconnect()
#
#     def _close(self) -> None:
#         super(StdinZmqDealer, self)._close()
#
#     def __repr__(self) -> str:
#         return "<StdinZmqDealer(id='{}')>".format(self.id)
#
#
# class StdinZmqAsyncDealer(ZmqAsyncDealer):
#     """
#     classdocs
#     """
#
#     def __init__(self) -> None:
#         """
#         Constructor
#         """
#         super(StdinZmqAsyncDealer, self).__init__()
#
#     async def _connect(self) -> None:
#         await super(StdinZmqAsyncDealer, self)._connect()
#
#     async def _disconnect(self) -> None:
#         await super(StdinZmqAsyncDealer, self)._disconnect()
#
#     async def _close(self) -> None:
#         await super(StdinZmqAsyncDealer, self)._close()
#
#     def __repr__(self) -> str:
#         return "<StdinZmqAsyncDealer(id='{}')>".format(self.id)
#
#
# class ControlZmqDealer(ZmqDealer):
#     """
#     classdocs
#     """
#
#     def __init__(self) -> None:
#         """
#         Constructor
#         """
#         super(ControlZmqDealer, self).__init__()
#
#     def _connect(self) -> None:
#         super(ControlZmqDealer, self)._connect()
#
#     def _disconnect(self) -> None:
#         super(ControlZmqDealer, self)._disconnect()
#
#     def _close(self) -> None:
#         super(ControlZmqDealer, self)._close()
#
#     def __repr__(self) -> str:
#         return "<ControlZmqDealer(id='{}')>".format(self.id)
#
#
# class ControlZmqAsyncDealer(ZmqAsyncDealer):
#     """
#     classdocs
#     """
#
#     def __init__(self) -> None:
#         """
#         Constructor
#         """
#         super(ControlZmqAsyncDealer, self).__init__()
#
#     async def _connect(self) -> None:
#         await super(ControlZmqAsyncDealer, self)._connect()
#
#     async def _disconnect(self) -> None:
#         await super(ControlZmqAsyncDealer, self)._disconnect()
#
#     async def _close(self) -> None:
#         await super(ControlZmqAsyncDealer, self)._close()
#
#     def __repr__(self) -> str:
#         return "<ControlZmqDealer(id='{}')>".format(self.id)
#
#
# class StdoutZmqDealer(ZmqDealer):
#     """
#     classdocs
#     """
#
#     def __init__(self) -> None:
#         """
#         Constructor
#         """
#         super(StdoutZmqDealer, self).__init__()
#
#     def _connect(self) -> None:
#         super(StdoutZmqDealer, self)._connect()
#
#     def _disconnect(self) -> None:
#         super(StdoutZmqDealer, self)._disconnect()
#
#     def _close(self) -> None:
#         super(StdoutZmqDealer, self)._close()
#
#     def __repr__(self) -> str:
#         return "<StdoutZmqDealer(id='{}')>".format(self.id)
#
#
# class StdoutZmqAsyncDealer(ZmqAsyncDealer):
#     """
#     classdocs
#     """
#
#     def __init__(self) -> None:
#         """
#         Constructor
#         """
#         super(StdoutZmqAsyncDealer, self).__init__()
#
#     async def _connect(self) -> None:
#         await super(StdoutZmqAsyncDealer, self)._connect()
#
#     async def _disconnect(self) -> None:
#         await super(StdoutZmqAsyncDealer, self)._disconnect()
#
#     async def _close(self) -> None:
#         await super(StdoutZmqAsyncDealer, self)._close()
#
#     def __repr__(self) -> str:
#         return "<StdoutZmqAsyncDealer(id='{}')>".format(self.id)
#
#
# class ZmqSubscriber(ZmqClient, ABC):
#     """
#     classdocs
#     """
#
#     def __init__(self) -> None:
#         """
#         Constructor
#         """
#         super(ZmqSubscriber, self).__init__()
#         self.socket_type = zmq.SUB
#
#     def _connect(self) -> None:
#         super(ZmqSubscriber, self)._connect()
#         self.socket.setsockopt(zmq.SUBSCRIBE, b'')
#
#     def _disconnect(self) -> None:
#         super(ZmqSubscriber, self)._disconnect()
#
#     def _close(self) -> None:
#         super(ZmqSubscriber, self)._close()
#
#     def __repr__(self) -> str:
#         return "<ZmqSubscriber(id='{}')>".format(self.id)
#
#
# class ZmqAsyncSubscriber(ZmqAsyncClient, ABC):
#     """
#     classdocs
#     """
#
#     def __init__(self) -> None:
#         """
#         Constructor
#         """
#         super(ZmqAsyncSubscriber, self).__init__()
#         self.socket_type = zmq.SUB
#
#     async def _connect(self) -> None:
#         await super(ZmqAsyncSubscriber, self)._connect()
#         self.socket.setsockopt(zmq.SUBSCRIBE, b'')
#
#     async def _disconnect(self) -> None:
#         await super(ZmqAsyncSubscriber, self)._disconnect()
#
#     async def _close(self) -> None:
#         await super(ZmqAsyncSubscriber, self)._close()
#
#     def __repr__(self) -> str:
#         return "<ZmqAsyncSubscriber(id='{}')>".format(self.id)
#
#
# class IOZmqSubscriber(ZmqSubscriber):
#     """
#     classdocs
#     """
#
#     def __init__(self) -> None:
#         """
#         Constructor
#         """
#         super(IOZmqSubscriber, self).__init__()
#
#     def _connect(self) -> None:
#         super(IOZmqSubscriber, self)._connect()
#
#     def _disconnect(self) -> None:
#         super(IOZmqSubscriber, self)._disconnect()
#
#     def _close(self) -> None:
#         super(IOZmqSubscriber, self)._close()
#
#     def __repr__(self) -> str:
#         return "<IOZmqSubscriber(id='{}')>".format(self.id)
#
#
# class IOZmqAsyncSubscriber(ZmqAsyncSubscriber):
#     """
#     classdocs
#     """
#
#     def __init__(self) -> None:
#         """
#         Constructor
#         """
#         super(IOZmqAsyncSubscriber, self).__init__()
#
#     async def _connect(self) -> None:
#         await super(IOZmqAsyncSubscriber, self)._connect()
#
#     async def _disconnect(self) -> None:
#         await super(IOZmqAsyncSubscriber, self)._disconnect()
#
#     async def _close(self) -> None:
#         await super(IOZmqAsyncSubscriber, self)._close()
#
#     def __repr__(self) -> str:
#         return "<IOZmqAsyncSubscriber(id='{}')>".format(self.id)
#
#
# class ZmqRequest(ZmqClient, ABC):
#     """
#     classdocs
#     """
#
#     def __init__(self) -> None:
#         """
#         Constructor
#         """
#         super(ZmqRequest, self).__init__()
#         self.socket_type = zmq.REQ
#
#     def _connect(self) -> None:
#         super(ZmqRequest, self)._connect()
#
#     def _disconnect(self) -> None:
#         super(ZmqRequest, self)._disconnect()
#
#     def _close(self) -> None:
#         super(ZmqRequest, self)._close()
#
#     def __repr__(self) -> str:
#         return "<ZmqRequest(id='{}')>".format(self.id)
#
#
# class ZmqAsyncRequest(ZmqAsyncClient, ABC):
#     """
#     classdocs
#     """
#
#     def __init__(self) -> None:
#         """
#         Constructor
#         """
#         super(ZmqAsyncRequest, self).__init__()
#         self.socket_type = zmq.REQ
#
#     async def _connect(self) -> None:
#         await super(ZmqAsyncRequest, self)._connect()
#
#     async def _disconnect(self) -> None:
#         await super(ZmqAsyncRequest, self)._disconnect()
#
#     async def _close(self) -> None:
#         await super(ZmqAsyncRequest, self)._close()
#
#     def __repr__(self) -> str:
#         return "<ZmqAsyncRequest(id='{}')>".format(self.id)
#
#
# class HeartbeatZmqRequestThread(Thread):
#     """
#     classdocs
#     """
#
#     def __init__(self, req) -> None:
#         """
#         Constructor
#         """
#         super(HeartbeatZmqRequestThread, self).__init__()
#         self.req = req
#         self._exit: Event = Event()
#
#     def _poll(self, start_time) -> None:
#         """poll for heartbeat replies until we reach self.time_to_dead.
#
#         Ignores interrupts, and returns the result of poll(), which
#         will be an empty list if no messages arrived before the timeout,
#         or the event tuple if there is a message to receive.
#         """
#
#         until_dead = self.req.time_to_dead - (time.time() - start_time)
#         # ensure poll at least once
#         until_dead = max(until_dead, 1e-3)
#         events = []
#         while True:
#             try:
#                 events = self.req.poller.poll(1000 * until_dead)
#             except ZMQError as e:
#                 if e.errno == errno.EINTR:
#                     # ignore interrupts during heartbeat
#                     # this may never actually happen
#                     until_dead = self.req.time_to_dead - (time.time() - start_time)
#                     until_dead = max(until_dead, 1e-3)
#                     pass
#                 else:
#                     raise
#             except Exception:
#                 #if self._exiting:
#                 #    break
#                 #else:
#                 raise
#             else:
#                 break
#         return events
#
#     def run(self) -> None:
#         self.req._beating = True
#
#         #while self._running:
#         while True:
#             #if self._pause:
#                 # just sleep, and skip the rest of the loop
#             #    self._exit.wait(self.time_to_dead)
#             #    continue
#
#             since_last_heartbeat = 0.0
#             # no need to catch EFSM here, because the previous event was
#             # either a recv or connect, which cannot be followed by EFSM
#             self.req.socket.send(b'ping')
#             request_time = time.time()
#             ready = self._poll(request_time)
#             if ready:
#                 self.req._beating = True
#                 # the poll above guarantees we have something to recv
#                 msg = self.req.socket.recv()
#                 print(msg)
#                 # sleep the remainder of the cycle
#                 remainder = self.req.time_to_dead - (time.time() - request_time)
#                 if remainder > 0:
#                     self._exit.wait(remainder)
#                 continue
#             else:
#                 # nothing was received within the time limit, signal heart failure
#                 self.req._beating = False
#                 since_last_heartbeat = time.time() - request_time
#                 self.call_handlers(since_last_heartbeat)
#                 # and close/reopen the socket, because the REQ/REP cycle has been broken
#                 self.req.disconnect()
#                 self.req.connect()
#                 continue
#
#     def call_handlers(self, since_last_heartbeat) -> None:
#         """This method is called in the ioloop thread when a message arrives.
#
#         Subclasses should override this method to handle incoming messages.
#         It is important to remember that this method is called in the thread
#         so that some logic must be done to ensure that the application level
#         handlers are called in the application thread.
#         """
#         pass
#
#
# class HeartbeatZmqRequest(ZmqRequest):
#     """
#     classdocs
#     """
#
#     def __init__(self) -> None:
#         """
#         Constructor
#         """
#         super(HeartbeatZmqRequest, self).__init__()
#         self.poller: Poller = Poller()
#         self._beating: bool = False
#         self.thread: HeartbeatZmqRequestThread | None = None
#         self.time_to_dead: int = 1
#
#     def _connect(self) -> None:
#         super(HeartbeatZmqRequest, self)._connect()
#         self.poller.register(self.socket, zmq.POLLIN)
#         self.thread = HeartbeatZmqRequestThread(self)
#         self.log.logger.debug("Heartbeat REQ Channel on port: {}".format(self.conf["port"]))
#         self.thread.start()
#
#     def is_beating(self) -> bool:
#         return self._beating
#
#     def __repr__(self) -> str:
#         return "<HeartbeatZmqRequest(id='{}')>".format(self.id)
#
#
# class HeartbeatZmqAsyncRequest(ZmqAsyncRequest):
#     """
#     classdocs
#     """
#
#     def __init__(self) -> None:
#         """
#         Constructor
#         """
#         super(HeartbeatZmqAsyncRequest, self).__init__()
#         self.poller: Poller = Poller()
#         self._beating: bool = False
#         self.thread: HeartbeatZmqRequestThread | None = None
#         self.time_to_dead: int = 1
#
#     async def _connect(self) -> None:
#         await super(HeartbeatZmqAsyncRequest, self)._connect()
#         self.poller.register(self.socket, zmq.POLLIN)
#         self.thread = HeartbeatZmqRequestThread(self)
#         self.log.logger.debug("Heartbeat REQ Channel on port: {}".format(self.conf["port"]))
#         self.thread.start()
#
#     def is_beating(self) -> bool:
#         return self._beating
#
#     def __repr__(self) -> str:
#         return "<HeartbeatZmqAsyncRequest(id='{}')>".format(self.id)
#
#
# class JupyterClientMeta(type(NetworkService), type(BlockingKernelClient)):
#     pass
#
#
# class JupyterClientService(NetworkService, BlockingKernelClient, metaclass=JupyterClientMeta):
#     """
#     classdocs
#     """
#
#     def __init__(self) -> None:
#         """
#         Constructor
#         """
#         NetworkService.__init__(self)
#         BlockingKernelClient.__init__(self)
#         self.log = None
#
#         self.profile_dir: ProfileDir = ProfileDir()
#         self.user_ns = None
#
#     def _load(self) -> None:
#         NetworkService._load(self)
#         self._create_session()
#
#     def _create_session(self) -> None:
#         self.session = Session(parent=self)
#         self.session.session = self.conf["session"]
#         self.session.bsession = self.conf["session"].encode("utf-8")
#         self.session.key = self.conf["key"].encode("utf-8")
#         self.session.signature_scheme = self.conf["signature_scheme"]
#         self.session.username = self.conf["username"]
#
#         for client in self.clients.values():
#             client.session = self.session
#         self.clients["shell"].identity = self.session.bsession
#         self.clients["stdin"].identity = self.session.bsession
#         self.clients["ctrl"].identity = self.session.bsession
#
#     def _start(self) -> None:
#         NetworkService._start(self)
#         self._inject_client()
#
#     def _inject_client(self) -> None:
#         self._shell_channel = self.clients["shell"]
#         self._iopub_channel = self.clients["iopub"]
#         self._stdin_channel = self.clients["stdin"]
#         self._hb_channel = self.clients["hb"]
#         self._control_channel = self.clients["ctrl"]
#
#
# class JupyterAsyncClientService(NetworkAsyncService, AsyncClient, metaclass=JupyterClientMeta):
#     """
#     classdocs
#     """
#
#     def __init__(self) -> None:
#         """
#         Constructor
#         """
#         NetworkAsyncService.__init__(self)
#         AsyncClient.__init__(self)
#         self.log = None
#
#         self.profile_dir = ProfileDir()
#         self.user_ns = None
#
#     async def _load(self) -> None:
#         NetworkAsyncService._load(self)
#         self._create_session()
#
#     async def _create_session(self) -> None:
#         self.session = Session(parent=self)
#         self.session.session = self.conf["session"]
#         self.session.bsession = self.conf["session"].encode("utf-8")
#         self.session.key = self.conf["key"].encode("utf-8")
#         self.session.signature_scheme = self.conf["signature_scheme"]
#         self.session.username = self.conf["username"]
#
#         for client in self.clients.values():
#             client.session = self.session
#         self.clients["shell"].identity = self.session.bsession
#         self.clients["stdin"].identity = self.session.bsession
#         self.clients["ctrl"].identity = self.session.bsession
#
#     async def _start(self) -> None:
#         NetworkAsyncService._start(self)
#         self._inject_client()
#
#     async def _inject_client(self) -> None:
#         self._shell_channel = self.clients["shell"]
#         self._iopub_channel = self.clients["iopub"]
#         self._stdin_channel = self.clients["stdin"]
#         self._hb_channel = self.clients["hb"]
#         self._control_channel = self.clients["ctrl"]
