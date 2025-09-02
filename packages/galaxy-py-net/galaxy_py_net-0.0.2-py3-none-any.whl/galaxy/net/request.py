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


class HeaderFactory(Component, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(HeaderFactory, self).__init__()
        self.log: LogService | LogAsyncService | None = None

    @abstractmethod
    def create(self, **kwargs) -> dict[str, str]:
        raise NotImplementedError("Should implement create()")


class HeaderBuilder(ABC):
    """
    classdocs
    """

    @abstractmethod
    def build_headers(self, **kwargs) -> "HeaderBuilder":
        raise NotImplementedError("Should implement build_headers()")

    @abstractmethod
    def build(self) -> dict[str, str]:
        raise NotImplementedError("Should implement build()")


class BodyFactory(Component, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(BodyFactory, self).__init__()
        self.log: LogService | LogAsyncService | None = None

    @abstractmethod
    def create(self, **kwargs) -> str | dict[str, str]:
        raise NotImplementedError("Should implement create()")
