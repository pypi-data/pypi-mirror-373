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

from galaxy.utils.pattern import Builder


class Endpoint(object):
    """
    classdocs
    """

    def __init__(self, transport: str, host: str, port: int | None = None) -> None:
        """
        Constructor
        """
        self.transport: str = transport
        self.host: str = host
        self.port: int | None = port
        self.address: str = self._get_address()

    def _get_address(self) -> str:
        if self.port is None:
            return self.host
        return "{}:{}".format(self.host, self.port)

    def _get_endpoint(self) -> str:
        return "{}://{}".format(self.transport, self.address)

    def __str__(self) -> str:
        return self._get_endpoint()

    def __repr__(self) -> str:
        return "<Endpoint(endpoint='{}')>".format(self._get_endpoint())

    def __eq__(self, other: "Endpoint") -> bool:
        return self._get_endpoint() == other._get_endpoint()

    def __ne__(self, other: "Endpoint") -> bool:
        return self._get_endpoint() != other._get_endpoint()


class EndpointBuilder(Builder):
    """
    classdocs
    """

    def __init__(self):
        """
        Constructor
        """
        super(EndpointBuilder, self).__init__()
        self._transport: str | None = None
        self._host: str | None = None
        self._port: int | None = None

    def transport(self, transport: str) -> "EndpointBuilder":
        if transport in ["tcp", "ipc", "inproc", "pgm", "epgm", "vmci"]:
            self._transport = transport
        return self

    def host(self, host: str) -> "EndpointBuilder":
        self._host = host
        return self

    def port(self, port: int) -> "EndpointBuilder":
        self._port = port
        return self

    def from_conf(self, conf: dict) -> "EndpointBuilder":
        if "transport" in conf and conf["transport"] in ["tcp", "ipc", "inproc", "pgm", "epgm", "vmci"]:
            self._transport = conf["transport"]
        if "host" in conf:
            self._host = conf["host"]
        if "port" in conf:
            self._port = conf["port"]
        return self

    def build(self) -> Endpoint:
        return Endpoint(self._transport, self._host, self._port)
