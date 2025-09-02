import logging
import os.path

from mitm_tooling.definition import MITM
from mitm_tooling.representation.intermediate import MITMData
from mitm_tooling.utilities.io_utils import DataSource, FilePath

from .common import FileRepresentationVariant, MITMIOError
from .folder import FolderExport, FolderImport
from .sqlite import SQLiteExport, SQLiteImport, infer_mitm_from_sqlite
from .zip import ZippedExport, ZippedImport, infer_mitm_from_zip_path

logger = logging.getLogger(__name__)


def read_file(
    source: FilePath,
    variant: FileRepresentationVariant = 'zip',
    mitm: MITM | None = None,
    header_only: bool = False,
    **kwargs,
) -> MITMData | None:
    """
    Read a file into a `MITMData` object.

    :param source: a readable byte or text buffer, or a file path
    :param variant: the file representation variant, defaults to 'zip'
    :param mitm: the target MITM, is attempted to be inferred from the file path if not specified
    :param header_only: whether to read only the header, skipping the (potentially large) data files
    :param kwargs: any additional keyword arguments to pass to the underlying `ZippedImport.read()` call
    :return: the `MITMData` object, or None if the import failed
    """

    if not mitm:
        match variant:
            case 'zip':
                mitm = infer_mitm_from_zip_path(source)
            case 'sqlite':
                mitm = infer_mitm_from_sqlite(source)
            case _:
                raise MITMIOError(f'Unsupported file representation variant: {variant}')

    if not mitm:
        logger.error('Attempted to import data with unspecified MitM.')
        return None

    match variant:
        case 'zip':
            io_cls = ZippedImport
        case 'sqlite':
            io_cls = SQLiteImport
        case 'folder':
            io_cls = FolderImport
        case _:
            raise MITMIOError(f'Unsupported file representation variant: {variant}')

    try:
        io = io_cls(mitm=mitm)
        if header_only:
            return MITMData(header=io.read_header(source, **kwargs), concept_dfs={})
        else:
            return io.read(source, **kwargs)
    except MITMIOError as e:
        logger.error(f'Error reading {variant} file "{source}":\n{str(e)}')
    return None


def write_file(
    target: FilePath,
    mitm_data: MITMData,
    variant: FileRepresentationVariant = 'zip',
    **kwargs,
):
    """
    Write `mitm_data` to a file.

    :param target: the output file path
    :param mitm_data: the `MITMData` to write
    :param variant: the file representation variant, defaults to 'zip'
    """

    match variant:
        case 'zip':
            io_cls = ZippedExport
        case 'sqlite':
            io_cls = SQLiteExport
        case 'folder':
            io_cls = FolderExport
        case _:
            raise MITMIOError(f'Unsupported file representation variant: {variant}')

    try:
        io = io_cls(mitm=mitm_data.header.mitm, filename=os.path.basename(target), mitm_data=mitm_data)
        io.write(target, **kwargs)
    except MITMIOError as e:
        logger.error(f'Error reading {variant} file "{target}":\n{str(e)}')
    return None


def read_zip(source: DataSource, mitm: MITM | None = None, header_only: bool = False, **kwargs) -> MITMData | None:
    """
    Read a zip file into a `MITMData` object. See `read_file()` for more details.

    :param source: a readable byte or text buffer, or a file path
    :param mitm: the target MITM, is attempted to be inferred from the file path if not specified
    :param header_only: whether to read only the header, skipping the (potentially large) data files
    :param kwargs: any additional keyword arguments to pass to the underlying `ZippedImport.read()` call
    :return: the `MITMData` object, or None if the import failed
    """
    return read_file(source, mitm=mitm, header_only=header_only, variant='zip', **kwargs)


def write_zip(target: FilePath, mitm_data: MITMData) -> None:
    """
    Write `mitm_data` to a zip file. See `read_file()` for more details.

    :param target: the output file path
    :param mitm_data: the `MITMData` to write
    """
    return write_file(target, mitm_data, variant='zip')


def read_sqlite(source: DataSource, mitm: MITM | None = None, header_only: bool = False, **kwargs) -> MITMData | None:
    """
    Read a SQLite file into a `MITMData` object. See `read_file()` for more details.

    :param source: a readable byte or text buffer, or a file path
    :param mitm: the target MITM, is attempted to be inferred from the file path if not specified
    :param header_only: whether to read only the header, skipping the (potentially large) data files
    :param kwargs: any additional keyword arguments to pass to the underlying `ZippedImport.read()` call
    :return: the `MITMData` object, or None if the import failed
    """
    return read_file(source, mitm=mitm, header_only=header_only, variant='sqlite', **kwargs)


def write_sqlite(target: FilePath, mitm_data: MITMData) -> None:
    """
    Write `mitm_data` to a SQLite file. See `read_file()` for more details.

    :param target: the output file path
    :param mitm_data: the `MITMData` to write
    """

    return write_file(target, mitm_data, variant='sqlite')


def read_folder(source: DataSource, mitm: MITM | None = None, header_only: bool = False, **kwargs) -> MITMData | None:
    """
    Read a folder into a `MITMData` object. See `read_file()` for more details.

    :param source: a readable byte or text buffer, or a file path
    :param mitm: the target MITM, is attempted to be inferred from the file path if not specified
    :param header_only: whether to read only the header, skipping the (potentially large) data files
    :param kwargs: any additional keyword arguments to pass to the underlying `ZippedImport.read()` call
    :return: the `MITMData` object, or None if the import failed
    """
    return read_file(source, mitm=mitm, header_only=header_only, variant='folder', **kwargs)


def write_folder(target: FilePath, mitm_data: MITMData) -> None:
    """
    Write `mitm_data` to a folder. See `read_file()` for more details.

    :param target: the output file path
    :param mitm_data: the `MITMData` to write
    """
    return write_file(target, mitm_data, variant='folder')
