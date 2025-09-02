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

from abc import ABC,                      \
                abstractmethod
import zlib
import gzip

from galaxy.utils.base import Component


class Compressor(Component, ABC):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(Compressor, self).__init__()

    @abstractmethod
    def compress(self, msg: bytes) -> bytes:
        raise NotImplementedError("Should implement compress()")

    @abstractmethod
    def decompress(self, msg: bytes) -> bytes:
        raise NotImplementedError("Should implement decompress()")


class NoCompressor(Compressor):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(NoCompressor, self).__init__()

    def compress(self, data: bytes) -> bytes:
        return data

    def decompress(self, data: bytes) -> bytes:
        return data


class GzipCompressor(Compressor):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(GzipCompressor, self).__init__()

    def compress(self, data: bytes) -> bytes:
        return gzip.compress(data)

    def decompress(self, data: bytes) -> bytes:
        return gzip.decompress(data)


class ZlibCompressor(Compressor):
    """
    classdocs
    """

    def __init__(self) -> None:
        """
        Constructor
        """
        super(ZlibCompressor, self).__init__()

    def compress(self, data: bytes) -> bytes:
        return zlib.compress(data)

    def decompress(self, data: bytes) -> bytes:
        return zlib.decompress(data)
