#  Copyright (c) 2024 bastien.saltel
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

import socket

from galaxy.utils.base import Component
from galaxy.service.service import LogService,          \
                                   LogAsyncService


class SocketFactory(Component):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(SocketFactory, self).__init__()
        self.log: LogService | LogAsyncService | None = None

    def create(self, host: str, port: int) -> socket.socket:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        sock.bind((host, port))
        return sock
