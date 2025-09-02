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
from abc import ABC,                                                    \
                abstractmethod
from urllib.request import Request
from aiohttp.formdata import FormData

from galaxy.net import constant
from galaxy.net.request import HeaderFactory,                           \
                               HeaderBuilder,                           \
                               BodyFactory
from galaxy.net.uri import Uri,                                         \
                           UriPathFactory,                              \
                           UriQueryFactory,                             \
                           UriBuilder
from galaxy.utils.pattern import Builder
from galaxy.utils.base import Component
from galaxy.service.service import LogService,                          \
                                   LogAsyncService


class HTTPHeaderFactory(HeaderFactory, ABC):
    """
    classdocs
    """

    def __init__(self):
        """
        Constructor
        """
        super(HeaderFactory, self).__init__()

    @abstractmethod
    def create(self, **kwargs) -> dict[str, str]:
        raise NotImplementedError("Should implement create()")


class HTTPHeaderBuilder(HeaderBuilder):
    """
    classdocs
    """

    def __init__(self, header_fact: HTTPHeaderFactory | None = None):
        """
        Constructor
        """
        super(HTTPHeaderBuilder, self).__init__()
        self._headers: dict[str, str] = {}
        self.factory: HTTPHeaderFactory | None = header_fact

    def from_conf(self, conf: dict) -> "HTTPHeaderBuilder":
        for header in constant.HTTP_HEADERS:
            conf_header = header.lower().replace("-", "_")
            if conf_header in conf:
                self._headers[header] = conf[conf_header]
        return self

    def build_headers(self, **kwargs) -> "HTTPHeaderBuilder":
        if self.factory is not None:
            self._headers |= self.factory.create(kwargs)
        return self

    def build(self) -> dict[str, str]:
        return self._headers


class HTTPBodyFactory(BodyFactory):
    """
    classdocs
    """

    def __init__(self):
        """
        Constructor
        """
        super(HTTPBodyFactory, self).__init__()

    @abstractmethod
    def create(self, **kwargs) -> str | dict[str, str]:
        raise NotImplementedError("Should implement create()")


class HTTPUriPathFactory(UriPathFactory, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(HTTPUriPathFactory, self).__init__()
        self.old_path = None

    @abstractmethod
    def create(self, **kwargs) -> str:
        raise NotImplementedError("Should implement create()")


class HTTPUriQueryFactory(UriQueryFactory, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(HTTPUriQueryFactory, self).__init__()

    @abstractmethod
    def create(self, **kwargs) -> str:
        raise NotImplementedError("Should implement create()")


class HTTPUriBuilder(UriBuilder):
    """
    classdocs
    """

    def __init__(self,
                 path_fact: HTTPUriPathFactory | None = None,
                 query_fact: HTTPUriQueryFactory | None = None) -> None:
        """
        Constructor
        """
        super(HTTPUriBuilder, self).__init__()
        self.log: LogService | None = None
        self.path_fact: HTTPUriPathFactory | None = path_fact
        self.query_fact: HTTPUriQueryFactory | None = query_fact

    def build_path(self, **kwargs) -> "HTTPUriBuilder":
        if self.path_fact is not None:
            self._path = self.path_fact.create(**kwargs)
        return self

    def build_query(self, **kwargs) -> "HTTPUriBuilder":
        if self.query_fact is not None:
            self._query = self.query_fact.create(**kwargs)
        return self


class HTTPRequestBuilder(Component, Builder):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        Component.__init__(self)
        Builder.__init__(self)
        self.log: LogService | LogAsyncService | None = None
        self._uri: Uri | None = None
        self._method: str | None = None
        self._headers: dict[str, str] | None = None
        self._body: str | dict[str, str] | None = None
        self._cookies: Any | None = None

        # Factories
        self.path_fact: HTTPUriPathFactory | None = None
        self.query_fact: HTTPUriQueryFactory | None = None
        self.header_fact: HTTPHeaderFactory | None = None
        self.body_fact: HTTPBodyFactory | None = None

    def uri(self, uri: Uri) -> "HTTPRequestBuilder":
        self._uri = uri
        return self

    def method(self, method: str) -> "HTTPRequestBuilder":
        self._method = method
        return self

    def headers(self, headers: dict[str, str]) -> "HTTPRequestBuilder":
        self._headers = headers
        return self

    def body(self, body: str | dict[str, str] | None) -> "HTTPRequestBuilder":
        self._body = body
        return self

    def cookies(self, cookies: dict[str, str]) -> "HTTPRequestBuilder":
        self._cookies = cookies
        return self

    def from_conf(self, conf: dict, **kwargs) -> "HTTPRequestBuilder":
        # URI
        uri_builder = HTTPUriBuilder(self.path_fact, self.query_fact)
        if "uri" in conf:
            uri_builder.from_conf(conf["uri"])
            if self.path_fact is not None:
                self.path_fact.old_path = conf["uri"]["path"]
        self._uri = uri_builder.build_path(**kwargs).build_query(**kwargs).build()

        # Headers
        header_builder = HTTPHeaderBuilder(self.header_fact)
        if "header" in conf:
            header_builder.from_conf(conf["header"])
        self._headers = header_builder.build_headers(**kwargs).build()

        if "method" in conf:
            self._method = conf["method"]

        # Body
        if self.body_fact is not None:
            self._body = self.body_fact.create(**kwargs)

        return self

    def build(self) -> Request:
        return Request(url=self._uri,
                       data=self._body,
                       headers=self._headers,
                       method=self._method.upper())
