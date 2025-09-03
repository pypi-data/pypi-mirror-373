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

from galaxy.utils.base import Component
from galaxy.service.service import LogService,                          \
                                   LogAsyncService
from galaxy.net import constant
from galaxy.utils.pattern import Builder


class Uri(object):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        self.host: str | None = None
        self.port: int = constant.HTTP_PORT
        self.scheme: str = constant.HTTP_SCHEME
        self.path: str | None = None
        self.query: str | None = None
        self.username: str | None = None
        self.password: str | None = None
        self.userinfo: str | None = None
        self.fragment: str | None = None

    def _get_uri(self) -> str:
        uri = ""
        if self.scheme is not None and len(self.scheme) > 0:
            uri += self.scheme + ":"
        if self.host is not None and len(self.host) > 0:
            uri += "//"
            if self.userinfo is not None and len(self.userinfo) > 0:
                uri += "{}@".format(self.username)
            uri += self.host
            if self.port is not None:
                uri += ":{}".format(self.port)
        if self.path is not None and len(self.path) > 0:
            uri += self.path
            if self.query is not None and len(self.query) > 0:
                uri += "?{}".format(self.query)
            if self.fragment is not None and len(self.fragment) > 0:
                uri += "#{}".format(self.fragment)
        return uri

    def __str__(self) -> str:
        return self._get_uri()

    def __repr__(self) -> str:
        return "<Uri(uri='{}')>".format(self._get_uri())

    def __eq__(self, other: "Uri") -> bool:
        return self._get_uri() == other._get_uri()

    def __ne__(self, other: "Uri") -> bool:
        return self._get_uri() != other._get_uri()


class UriPathFactory(Component, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(UriPathFactory, self).__init__()
        self.log: LogService | LogAsyncService | None = None

    @abstractmethod
    def create(self, **kwargs) -> str:
        raise NotImplementedError("Should implement create()")


class UriQueryFactory(Component, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(UriQueryFactory, self).__init__()
        self.log: LogService | LogAsyncService | None = None

    @abstractmethod
    def create(self, **kwargs) -> str:
        raise NotImplementedError("Should implement create()")


class UriBuilder(Builder):
    """
    classdocs
    """

    def __init__(self):
        """
        Constructor
        """
        super(UriBuilder, self).__init__()
        self._host: str | None = None
        self._port: int | None = None
        self._scheme: str | None = None
        self._path: str | None = None
        self._query: str | None = None
        self._username: str | None = None
        self._password: str | None = None
        self._fragment: str | None = None

    def host(self, host: str) -> "UriBuilder":
        self._host = host
        return self

    def port(self, port: int) -> "UriBuilder":
        self._port = port
        return self

    def scheme(self, scheme: str) -> "UriBuilder":
        self._scheme = scheme
        return self

    def path(self, path: str) -> "UriBuilder":
        self._path = path
        return self

    def query(self, query: str) -> "UriBuilder":
        self._query = query
        return self

    def username(self, username: str) -> "UriBuilder":
        self._username = username
        return self

    def password(self, password: str) -> "UriBuilder":
        self._password = password
        return self

    def fragment(self, fragment: str) -> "UriBuilder":
        self._fragment = fragment
        return self

    def from_conf(self, conf: dict) -> "UriBuilder":
        if "host" in conf:
            self._host = conf["host"]
        if "port" in conf:
            self._port = conf["port"]
        if "scheme" in conf:
            self._scheme = conf["scheme"]
        if "path" in conf:
            self._path = conf["path"]
        if "query" in conf:
            self._query = conf["query"]
        if "username" in conf:
            self._username = conf["username"]
        if "password" in conf:
            self._password = conf["password"]
        if "fragment" in conf:
            self._fragment = conf["fragment"]
        return self

    def build(self) -> Uri:
        uri = Uri()
        uri.host = self._host
        uri.port = self._port
        uri.scheme = self._scheme
        uri.path = self._path
        uri.query = self._query
        uri.username = self._username
        uri.password = self._password
        if uri.username is not None and len(uri.username) > 0:
            if uri.password is not None and len(uri.password) > 0:
                uri.userinfo = "{}:{}".format(self._username, self._password)
            else:
                uri.userinfo = self._username
        else:
            uri.userinfo = None
        uri.fragment = self._fragment
        return uri
