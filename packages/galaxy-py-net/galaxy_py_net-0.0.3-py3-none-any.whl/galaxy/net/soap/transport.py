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
from requests.sessions import Session
import httpx
from zeep.transports import Transport,                  \
                            AsyncTransport

from galaxy.utils.base import Component,                \
                              Configurable
from galaxy.service.service import LogService,          \
                                   LogAsyncService
from galaxy.net.auth import HTTPAuthenticationFactory,  \
                            CredentialBuilder


class SOAPTransportFactory(Component, Configurable, ABC):
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

    @abstractmethod
    def create(self) -> Any:
        raise NotImplementedError("Should implement create()")


class ZeepSOAPTransportFactory(SOAPTransportFactory):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(ZeepSOAPTransportFactory, self).__init__()
        self.auth_fact: HTTPAuthenticationFactory | None = None

    def create(self) -> Transport:
        cred = CredentialBuilder().from_conf(self.conf["cred"]).build()
        auth = self.auth_fact.create(cred)
        session = Session()
        session.auth = auth
        return Transport(session=session)


class ZeepSOAPAsyncTransportFactory(SOAPTransportFactory):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(ZeepSOAPAsyncTransportFactory, self).__init__()
        self.auth_fact: HTTPAuthenticationFactory | None = None

    def create(self) -> AsyncTransport:
        cred = CredentialBuilder().from_conf(self.conf["cred"]).build()
        auth = self.auth_fact.create(cred)
        if "timeout" in self.conf:
            timeout = httpx.Timeout(self.conf["timeout"]["default"], connect=self.conf["timeout"]["connect"])
            http_client = httpx.Client(auth=auth, timeout=timeout)
            http_asyncclient = httpx.AsyncClient(auth=auth, timeout=timeout)
        else:
            http_client = httpx.Client(auth=auth)
            http_asyncclient = httpx.AsyncClient(auth=auth)
        return AsyncTransport(client=http_asyncclient, wsdl_client=http_client)
