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

import ftplib
import aioftp

from galaxy.net.net import Client,                  \
                           AsyncClient,             \
                           Server,                  \
                           AsyncServer


class FTPClient(Client):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(FTPClient, self).__init__()

    def _connect(self) -> None:
        pass

    def _close(self) -> None:
        pass

    def __repr__(self) -> str:
        return "<FTPClient(id='{}')>".format(self.id)


class FTPAsyncClient(AsyncClient):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(FTPAsyncClient, self).__init__()

    async def _connect(self) -> None:
        pass

    async def _close(self) -> None:
        pass

    def __repr__(self) -> str:
        return "<FTPAsyncClient(id='{}')>".format(self.id)


class FTPServer(Server):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(FTPServer, self).__init__()

    def _start(self) -> None:
        pass

    def _stop(self) -> None:
        pass

    def __repr__(self) -> str:
        return "<FTPServer(id='{}')>".format(self.id)


class FTPAsyncServer(AsyncServer):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(FTPAsyncServer, self).__init__()

    async def _start(self) -> None:
        pass

    async def _stop(self) -> None:
        pass

    def __repr__(self) -> str:
        return "<FTPAsyncServer(id='{}')>".format(self.id)
