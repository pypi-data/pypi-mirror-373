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
from asyncio import Future,                             \
                    Queue
from aiozmq import ZmqProtocol
from aiozmq.interface import ZmqTransport
from typing import Any

from galaxy.utils.base import Component
from galaxy.service.service import LogService,          \
                                   LogAsyncService


class ZmqProtocolFactory(Component, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(ZmqProtocolFactory, self).__init__()
        self.log: LogService | LogAsyncService | None = None

    @abstractmethod
    def create(self, on_close: Future, queue: Queue | None = None) -> Any:
        raise NotImplementedError("Should implement create()")


class AioZmqProtocol(ZmqProtocol):
    """
    classdocs
    """

    def __init__(self, on_close: Future, log: LogService | LogAsyncService, queue: Queue | None = None) -> None:
        """
        Constructor
        """
        super(AioZmqProtocol, self).__init__()
        self.transport: ZmqTransport | None = None
        self.on_close: Future = on_close
        self.queue: Queue | None = queue
        self.log = log

    def connection_made(self, transport: ZmqTransport) -> None:
        self.transport = transport

    def msg_received(self, msg: bytes) -> None:
        if self.queue is not None:
            self.queue.put_nowait(msg)

    def connection_lost(self, ex: Exception | None) -> None:
        self.log.logger.info("The connection has been lost : {}".format(ex))
        self.on_close.set_result(ex)


class AioZmqProtocolFactory(ZmqProtocolFactory):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(AioZmqProtocolFactory, self).__init__()

    def create(self, on_close: Future, queue: Queue | None = None) -> AioZmqProtocol:
        return AioZmqProtocol(on_close, self.log, queue)


# class HelloWorldProtocol(AioZmqProtocol):
#
#     def __init__(self, loop):
#         """
#         Constructor
#         """
#         self.transport = None
#         self.wait_ready = Future(loop=loop)
#         self.wait_done = Future(loop=loop)
#         self.wait_closed = Future(loop=loop)
#         self.events_received = Queue(loop=loop)
#
#     def connection_made(self, transport):
#         self.transport = transport
#         self.wait_ready.set_result(True)
#
#     def connection_lost(self, exc):
#         self.wait_closed.set_result(exc)
#
#     def msg_received(self, data):
#         # This protocol is used by both the Router and Dealer sockets.
#         # Messages received by the router come prefixed with an 'identity'
#         # and hence contain two frames in this simple test protocol.
#         if len(data) == 2:
#             identity, msg = data
#             if msg == b'Hello':
#                 self.transport.write([identity, b'World'])
#         else:
#             msg = data[0]
#             if msg == b'World':
#                 self.wait_done.set_result(True)
#
#     def event_received(self, event):
#         self.events_received.put_nowait(event)
