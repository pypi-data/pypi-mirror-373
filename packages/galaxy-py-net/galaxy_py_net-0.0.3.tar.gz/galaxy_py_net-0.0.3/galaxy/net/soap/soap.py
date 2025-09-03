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

from abc import ABC,                                                    \
                abstractmethod
import zeep

from galaxy.net.net import Client,                                      \
                           AsyncClient
from galaxy.net.soap.response import SOAPResponseFactory
from galaxy.net.soap.transport import SOAPTransportFactory
from galaxy.utils.base import Component,                                \
                              Configurable
from galaxy.service.service import LogService,                          \
                                   LogAsyncService
from galaxy.net.uri import UriBuilder
from galaxy.perfo.decorator import timed,                               \
                                   async_timed


class SOAPClient(Client, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """

        super(SOAPClient, self).__init__()
        self.reqreps: dict[str, SOAPRequestReply] | None = None

    def _load(self) -> None:
        super(SOAPClient, self)._load()
        [reqrep._load() for reqrep in self.reqreps.values()]

    @abstractmethod
    def _connect(self) -> None:
        raise NotImplementedError("Should implement connect()")

    @abstractmethod
    def _close(self) -> None:
        raise NotImplementedError("Should implement close()")

    def __repr__(self) -> str:
        return "<SOAPClient(id='{}')>".format(self.id)


class SOAPAsyncClient(AsyncClient):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(SOAPAsyncClient, self).__init__()
        self.reqreps: dict[str, SOAPRequestReply] | None = None

    async def _load(self) -> None:
        await super(SOAPAsyncClient, self)._load()
        [reqrep._load() for reqrep in self.reqreps.values()]

    @abstractmethod
    async def _connect(self) -> None:
        raise NotImplementedError("Should implement connect()")

    @abstractmethod
    async def _close(self) -> None:
        raise NotImplementedError("Should implement close()")

    def __repr__(self) -> str:
        return "<SOAPAsyncClient(id='{}')>".format(self.id)


class ZeepSOAPClient(SOAPClient):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(SOAPClient, self).__init__()
        self.transport_fact: SOAPTransportFactory | None = None
        self.client: zeep.Client | None = None

    @timed
    def _load(self) -> None:
        super(ZeepSOAPClient, self)._load()
        if self.transport_fact is not None:
            self.transport_fact._load()

    @timed
    def _connect(self) -> None:
        transport = self.transport_fact.create()
        uri = UriBuilder().from_conf(self.conf["uri"]).build()
        self.client = zeep.Client(str(uri), transport=transport)
        if self.client is None:
            raise

    @timed
    def _close(self) -> None:
        self.client.transport.close()

    def __repr__(self) -> str:
        return "<ZeepSOAPClient(id='{}')>".format(self.id)


class ZeepSOAPAsyncClient(SOAPAsyncClient):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(ZeepSOAPAsyncClient, self).__init__()
        self.transport_fact: SOAPTransportFactory | None = None
        self.client: zeep.AsyncClient | None

    @async_timed
    async def _load(self) -> None:
        await super(ZeepSOAPAsyncClient, self)._load()
        if self.transport_fact is not None:
            self.transport_fact._load()

    @async_timed
    async def _connect(self) -> None:
        transport = self.transport_fact.create()
        uri = UriBuilder().from_conf(self.conf["uri"]).build()
        self.client = zeep.AsyncClient(str(uri), transport=transport)
        if self.client is None:
            raise

    @async_timed
    async def _close(self) -> None:
        self.client.transport.close()

    def __repr__(self) -> str:
        return "<ZeepSOAPAsyncClient(id='{}')>".format(self.id)


class SOAPRequestReply(Component, Configurable):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        Component.__init__(self)
        Configurable.__init__(self)
        self.log: LogService | LogAsyncService | None = None
        self.resp_fact: SOAPResponseFactory | None = None

    def __repr__(self) -> str:
        return "<SOAPRequestReply(id='{}')>".format(self.id)
