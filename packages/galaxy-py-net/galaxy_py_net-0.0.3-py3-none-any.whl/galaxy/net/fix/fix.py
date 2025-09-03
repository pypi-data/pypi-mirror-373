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
import quickfix

from galaxy.net.net import Client,          \
                           AsyncClient


class FIXClient(Client, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(FIXClient, self).__init__()

    @abstractmethod
    def _connect(self) -> None:
        raise NotImplementedError("Should implement _connect()")

    @abstractmethod
    def _close(self) -> None:
        raise NotImplementedError("Should implement _close()")

    def __repr__(self) -> str:
        return "<FIXClient(id='{0}')>".format(self.id)


class QuickFIXClient(FIXClient):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(QuickFIXClient, self).__init__()

    def _connect(self) -> None:
        pass

    def _close(self) -> None:
        pass

    def __repr__(self) -> str:
        return "<QuickFIXClient(id='{}')>".format(self.id)


class FIXAsyncClient(AsyncClient, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(FIXAsyncClient, self).__init__()

    @abstractmethod
    async def _connect(self) -> None:
        raise NotImplementedError("Should implement _connect()")

    @abstractmethod
    async def _close(self) -> None:
        pass

    def __repr__(self) -> str:
        return "<FIXAsyncClient(id='{0}')>".format(self.id)
