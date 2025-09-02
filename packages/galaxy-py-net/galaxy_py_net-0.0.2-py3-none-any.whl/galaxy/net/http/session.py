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

from typing import Any

from requests.auth import HTTPBasicAuth
from urllib3.poolmanager import PoolManager
from urllib3.util.retry import Retry
from requests.sessions import Session
from requests.adapters import HTTPAdapter
from aiohttp.client import ClientSession,                           \
                           ClientTimeout
from aiohttp.connector import TCPConnector
from aiohttp.helpers import BasicAuth

from galaxy.net.session import SessionFactory,                      \
                               AsyncSessionFactory
from galaxy.net.http.http import HTTPClient,                        \
                                 HTTPAsyncClient
from galaxy.service.service import LogService,                      \
                                   LogAsyncService
from galaxy.net.http.request import HTTPHeaderBuilder


class HTTPSessionFactory(SessionFactory):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(HTTPSessionFactory, self).__init__()
        self.log: LogService | None = None

    def create(self, client: HTTPClient) -> Any:
        pass


class UrllibHTTPSession(object):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        self.pool_manager: PoolManager = PoolManager()
        self.cookies: dict[str, str] = {}


class UrllibHTTPSessionFactory(HTTPSessionFactory):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(UrllibHTTPSessionFactory, self).__init__()

    def create(self, client: HTTPClient) -> PoolManager:
        session = UrllibHTTPSession()
        client.session = session
        return session

class RequestsTimeoutSession(Session):
    """
    classdocs
    """
    def __init__(self, connect: float | None = 0, sock_read: float | None = 0) -> None:
        """
        Constructor
        """
        super(RequestsTimeoutSession, self).__init__()
        self.connect = connect
        self.sock_read = sock_read

    def request(self, method, url, **kwargs):
        kwargs.setdefault("timeout", (self.connect, self.sock_read))
        return super(RequestsTimeoutSession, self).request(method, url, **kwargs)


class RequestsHTTPSessionFactory(HTTPSessionFactory):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(RequestsHTTPSessionFactory, self).__init__()

    def create(self, client: HTTPClient) -> Session:
        if "timeout" in self.conf:
            kwargs_timeout = {}
            if "connect" in self.conf["timeout"]:
                kwargs_timeout["connect"] = self.conf["timeout"]["connect"]
            if "sock_read" in self.conf["timeout"]:
                kwargs_timeout["sock_read"] = self.conf["timeout"]["sock_read"]
            session = RequestsTimeoutSession(**kwargs_timeout)
        else:
            session = Session()
        headers = HTTPHeaderBuilder().from_conf(self.conf["header"]).build()
        session.headers.update(headers)
        if "retries" in self.conf:
            kwargs_retries = {}
            if "total" in self.conf["retries"]:
                kwargs_retries["total"] = self.conf["retries"]["total"]
            if "backoff_factor" in self.conf["retries"]:
                kwargs_retries["backoff_factor"] = self.conf["retries"]["backoff_factor"]
            if "status_forcelist" in self.conf["retries"]:
                kwargs_retries["status_forcelist"] = self.conf["retries"]["status_forcelist"]
            if "allowed_methods" in self.conf["retries"]:
                kwargs_retries["allowed_methods"] = frozenset(self.conf["retries"]["allowed_methods"])
            retries = Retry(**kwargs_retries)
            session.mount("https://", HTTPAdapter(max_retries=retries))
            session.mount("http://", HTTPAdapter(max_retries=retries))
        client.session = session
        return session


class HTTPAsyncSessionFactory(AsyncSessionFactory):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(HTTPAsyncSessionFactory, self).__init__()
        self.log: LogAsyncService | None = None

    async def create(self, client: HTTPAsyncClient) -> Any:
        pass


class AioHTTPAsyncSessionFactory(HTTPAsyncSessionFactory):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(AioHTTPAsyncSessionFactory, self).__init__()

    async def create(self, client: HTTPAsyncClient) -> ClientSession:
        headers = HTTPHeaderBuilder().from_conf(self.conf["header"]).build()
        kwargs = {}
        if "timeout" in self.conf:
            kwargs_timeout = {}
            if "total" in self.conf["timeout"]:
                kwargs_timeout["total"] = self.conf["timeout"]["total"]
            if "connect" in self.conf["timeout"]:
                kwargs_timeout["connect"] = self.conf["timeout"]["connect"]
            if "sock_read" in self.conf["timeout"]:
                kwargs_timeout["sock_read"] = self.conf["timeout"]["sock_read"]
            if "sock_connect" in self.conf["timeout"]:
                kwargs_timeout["sock_connect"] = self.conf["timeout"]["sock_connect"]
            timeout = ClientTimeout(**kwargs_timeout)
            kwargs["timeout"] = timeout
        kwargs["headers"] = headers
        kwargs["connector"] = TCPConnector(verify_ssl=self.conf["verify_ssl"])
        if "cred" in self.conf:
            kwargs["auth"] = BasicAuth(login=self.conf["cred"]["username"],
                                       password=self.conf["cred"]["password"],
                                       encoding="utf-8")
        session = ClientSession(**kwargs)
        client.session = session
        return session

    def init_log(self):
        [self.log.add_logger(logger) for logger in ["aiohttp.client",
                                                    "aiohttp.internal"]]
