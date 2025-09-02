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

from galaxy.utils.base import Component
from galaxy.service.service import LogService,                          \
                                   LogAsyncService


class ResponseFactory(Component, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(ResponseFactory, self).__init__()
        self.log: LogService | LogAsyncService | None = None

    @abstractmethod
    def create(self, data: str) -> Any:
        raise NotImplementedError("Should implement create()")
