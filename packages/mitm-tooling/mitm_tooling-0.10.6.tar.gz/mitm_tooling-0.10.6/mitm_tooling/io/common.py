import io
import logging
import os.path
from abc import ABC, abstractmethod
from typing import Literal

import pydantic
from pydantic import ConfigDict

from mitm_tooling.definition import MITM
from mitm_tooling.representation.common import MITMRepresentationError
from mitm_tooling.representation.intermediate import Header, MITMData, StreamingMITMData
from mitm_tooling.utilities.io_utils import ByteSink, DataSink, DataSource, FilePath

logger = logging.getLogger(__name__)


class MITMIOError(MITMRepresentationError):
    pass


class MITMImport(pydantic.BaseModel, ABC):
    """
    Abstract base class for file imports of MITM data.
    """

    mitm: MITM

    @abstractmethod
    def read_header(self, source: DataSource, **kwargs) -> Header:
        pass

    @abstractmethod
    def read(self, source: DataSource, **kwargs) -> MITMData:
        pass


class MITMExport(pydantic.BaseModel, ABC):
    """
    Abstract base class for file exports of MITM data.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    mitm: MITM
    filename: str

    @abstractmethod
    def write(self, sink: DataSink, **kwargs) -> None:
        pass

    def to_buffer(self) -> io.BytesIO:
        buffer = io.BytesIO()
        self.write(buffer)
        buffer.seek(0)
        return buffer

    def into_file(self, path: os.PathLike):
        self.write(path)


class StreamingMITMImport(MITMImport, ABC):
    @abstractmethod
    def read_streaming(self, source: DataSource, **kwargs) -> StreamingMITMData:
        pass

    def read(self, source: DataSource, **kwargs) -> MITMData:
        return self.read_streaming(source).collect()


def ensure_filepath(arg: DataSource | DataSink, test_existence: bool = True, throw: bool = True) -> bool:
    if not isinstance(arg, FilePath):
        if throw:
            raise MITMIOError(f'Attempted to import from/export to unsupported data source/sink: {arg}.')
        else:
            return False
    if test_existence and not os.path.exists(arg):
        if throw:
            raise MITMIOError(f'Attempted to import from/export to nonexistent file: {arg}.')
        else:
            return False
    return True


def ensure_bytes(arg: DataSink | DataSource, throw: bool = True) -> bool:
    if not isinstance(arg, ByteSink):
        if throw:
            raise MITMIOError(f'Attempted to import from/export to unsupported data source/sink: {arg}.')
        else:
            return False
    return True


FileRepresentationVariant = Literal['zip', 'sqlite', 'folder']
