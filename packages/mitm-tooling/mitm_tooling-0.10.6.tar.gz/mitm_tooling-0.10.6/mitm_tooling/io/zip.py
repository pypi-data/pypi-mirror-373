import datetime
import logging
import os
import zipfile
from collections.abc import Iterable
from typing import Self

from mitm_tooling.definition import MITM, get_mitm_def
from mitm_tooling.representation.common import MITMSyntacticError
from mitm_tooling.representation.file import read_data_file, read_header_file, write_data_file, write_header_file
from mitm_tooling.representation.intermediate import Header, MITMData, StreamingMITMData
from mitm_tooling.utilities.io_utils import ByteSink, DataSource, FilePath, ensure_ext, use_bytes_io
from mitm_tooling.utilities.sql_utils import AnyDBBind

from ..extraction.relational.mapping import BoundExportable, Exportable
from .common import MITMExport, MITMImport, MITMIOError, ensure_bytes

logger = logging.getLogger(__name__)


def infer_mitm_from_zip_path(p: FilePath) -> MITM | None:
    _, ext = os.path.splitext(p)
    try:
        return MITM(ext[1:].upper())
    except ValueError:
        return None


class ZippedImport(MITMImport):
    """
    Import of the specific zip file format designed for MITMs.
    The data source is expected to be a zipped archive of CSV files.
    At least a `header.csv` file is expected.
    The other CSVs are expected to be named according to the pluralized concept names of defined in by the specified `MITM`.
    The CSVs themselves are expected to be in the format of `MITMData`.
    """

    def read_header(self, source: DataSource, **kwargs) -> Header:
        try:
            return self.read(source, header_only=True).header
        except Exception as e:
            raise MITMIOError(f'Error reading MITM Header from zip: {source}') from e

    def read(self, source: DataSource, header_only: bool = False, **kwargs) -> MITMData:
        try:
            mitm_def = get_mitm_def(self.mitm)
            with use_bytes_io(source, expected_file_ext='.zip', mode='rb') as f:
                parts = {}
                with zipfile.ZipFile(f, 'r', compression=zipfile.ZIP_DEFLATED) as zf:
                    files_in_zip = set(zf.namelist())
                    if 'header.csv' not in files_in_zip:
                        raise MITMSyntacticError('MITM data zip file is missing a header.csv file.')
                    with zf.open('header.csv') as h:
                        parts['header'] = read_header_file(h, normalize=True)
                    if not header_only:
                        for concept in mitm_def.main_concepts:
                            fn = ensure_ext(mitm_def.get_properties(concept).plural, '.csv')
                            if fn in files_in_zip:
                                with zf.open(fn) as cf:
                                    parts[concept] = read_data_file(
                                        cf, target_mitm=self.mitm, target_concept=concept, normalize=True
                                    )
                return MITMData(header=Header.from_df(parts.pop('header'), self.mitm), concept_dfs=parts)
        except Exception as e:
            raise MITMIOError(f'Error reading MITMData from zip: {source}') from e


class ZippedExport(MITMExport):
    """
    Export `MITMData` to the specific zip file format designed for MITMs.
    """

    mitm_data: MITMData

    @classmethod
    def from_exportable(cls, exportable: Exportable, bind: AnyDBBind) -> Self:
        mitm_data = exportable.bind(bind).generate_mitm_data()
        return cls(
            mitm=exportable.mitm,
            mitm_data=mitm_data,
            filename=exportable.filename or f'{exportable.mitm}.zip',
        )

    @classmethod
    def from_bound_exportable(cls, bound_exportable: BoundExportable) -> Self:
        return cls.from_exportable(bound_exportable.exportable, bound_exportable.bind)

    def write(self, sink: ByteSink, **kwargs):
        ensure_bytes(sink)
        try:
            mitm_def = get_mitm_def(self.mitm)
            with use_bytes_io(sink, expected_file_ext='.zip', mode='wb', create_file_if_necessary=True) as f:
                with zipfile.ZipFile(f, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
                    with zf.open('header.csv', 'w') as hf:
                        write_header_file(self.mitm_data.header.generate_header_df(), hf)
                    for c, df in self.mitm_data:
                        fn = ensure_ext(mitm_def.get_properties(c).plural, '.csv')
                        with zf.open(fn, 'w') as cf:
                            write_data_file(df, cf)
                            logger.debug(f'Wrote {len(df)} rows to {fn} (in-memory export).')
        except Exception as e:
            raise MITMIOError(f'Error exporting MITMData to zip: {sink}') from e
        return None


class StreamingZippedExport(MITMExport):
    """
    Export `StreamingMITMData` to a streamed zip file in the format designed for MITMs.

    See also `ZippedExport`.
    """

    streaming_mitm_data: StreamingMITMData

    @classmethod
    def from_exportable(cls, exportable: Exportable, bind: AnyDBBind, **kwargs) -> Self:
        streaming_mitm_data = exportable.bind(bind).generate_streaming_mitm_data(**kwargs)
        return cls(
            mitm=exportable.mitm,
            streaming_mitm_data=streaming_mitm_data,
            filename=exportable.filename or f'{exportable.mitm}.zip',
        )

    @classmethod
    def from_bound_exportable(cls, bound_exportable: BoundExportable, **kwargs) -> Self:
        return cls.from_exportable(bound_exportable.exportable, bound_exportable.bind, **kwargs)

    def write(self, sink: ByteSink, **kwargs) -> None:
        ensure_bytes(sink)

        try:
            mitm_def = get_mitm_def(self.mitm)
            collected_header_entries = []
            with use_bytes_io(sink, expected_file_ext='.zip', mode='wb', create_file_if_necessary=True) as f:
                with zipfile.ZipFile(f, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
                    for c, concept_data in self.streaming_mitm_data:
                        fn = ensure_ext(mitm_def.get_properties(c).plural, '.csv')
                        with zf.open(fn, 'w') as cf:
                            write_data_file(concept_data.structure_df, cf, append=False)
                            for df_chunks in concept_data.chunk_iterators:
                                for df_chunk, header_entries in df_chunks:
                                    collected_header_entries.extend(header_entries)
                                    write_data_file(df_chunk, cf, append=True)
                                    logger.debug(f'Wrote {len(df_chunk)} rows to {fn} (streaming export).')

                    with zf.open('header.csv', 'w') as hf:
                        header_df = Header(
                            mitm=self.mitm, header_entries=frozenset(collected_header_entries)
                        ).generate_header_df()
                        write_header_file(header_df, hf)
        except Exception as e:
            raise MITMIOError(f'Error exporting StreamingMITMData to zip: {sink}') from e
        return None

    def iter_bytes(self, chunk_size: int = 65536) -> Iterable[bytes]:
        try:
            from stat import S_IFREG

            from stream_zip import ZIP_64, stream_zip

            mitm_def = get_mitm_def(self.mitm)
            collected_header_entries = []

            def files():
                modified_at = datetime.datetime.now()
                mode = S_IFREG | 0o600

                for c, concept_data in self.streaming_mitm_data:
                    fn = ensure_ext(mitm_def.get_properties(c).plural, '.csv')

                    def concept_file_data(concept_data=concept_data):
                        yield write_data_file(concept_data.structure_df, sink=None, append=False).encode('utf-8')
                        for df_chunks in concept_data.chunk_iterators:
                            for df_chunk, header_entries in df_chunks:
                                collected_header_entries.extend(header_entries)
                                yield write_data_file(df_chunk, sink=None, append=True).encode('utf-8')

                    yield fn, modified_at, mode, ZIP_64, concept_file_data()

                header_df = Header(
                    mitm=self.mitm, header_entries=frozenset(collected_header_entries)
                ).generate_header_df()
                yield (
                    'header.csv',
                    modified_at,
                    mode,
                    ZIP_64,
                    (write_header_file(header_df, sink=None).encode('utf-8'),),
                )

            return stream_zip(files(), chunk_size=chunk_size)
        except Exception as e:
            raise MITMIOError('Error exporting StreamingMITMData to zipfile stream') from e
