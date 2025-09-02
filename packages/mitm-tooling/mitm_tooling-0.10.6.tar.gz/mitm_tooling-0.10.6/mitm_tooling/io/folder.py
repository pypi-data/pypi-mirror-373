import glob
import logging
import os.path
from typing import Self

from mitm_tooling.definition import get_mitm_def
from mitm_tooling.representation.file import read_data_file, read_header_file, write_data_file, write_header_file
from mitm_tooling.representation.intermediate import Header, MITMData
from mitm_tooling.utilities.io_utils import (
    DataSink,
    DataSource,
    ensure_directory_exists,
    ensure_ext,
)

from ..extraction.relational.mapping import BoundExportable, Exportable
from ..utilities.sql_utils import AnyDBBind
from .common import MITMExport, MITMImport, MITMIOError, ensure_filepath

logger = logging.getLogger(__name__)


class FolderImport(MITMImport):
    """
    Import a folder with the structure of the zipped file format designed for MITMs.

    See `ZippedImport` for more details.
    """

    def read_header(self, source: DataSource, **kwargs) -> Header:
        ensure_filepath(source)
        source = ensure_ext(source, '/', override_ext=True)

        try:
            return self.read(source, header_only=True).header
        except Exception as e:
            raise MITMIOError(f'Error reading MITM Header from folder: {source}') from e

    def read(self, source: DataSource, header_only: bool = False, **kwargs) -> MITMData:
        ensure_filepath(source)
        source = ensure_ext(source, '/', override_ext=True)

        try:
            file_names = {os.path.basename(p): p for p in glob.glob(os.path.join(source, '*.csv'))}
            mitm_def = get_mitm_def(self.mitm)

            parts = {'header': read_header_file(file_names.pop('header.csv'), normalize=True)}

            if not header_only:
                for concept in mitm_def.main_concepts:
                    fn = ensure_ext(mitm_def.get_properties(concept).plural, '.csv')
                    if (p := file_names.pop(fn, None)) is not None:
                        parts[concept] = read_data_file(
                            p, target_mitm=self.mitm, target_concept=concept, normalize=True
                        )

            return MITMData(header=Header.from_df(parts.pop('header'), self.mitm), concept_dfs=parts)
        except Exception as e:
            raise MITMIOError(f'Error reading MITMData from folder: {source}') from e


class FolderExport(MITMExport):
    """
    Export `MITMData` to a folder with the structure of the zipped file format designed for MITMs.

    See `ZippedExport` for more details.
    """

    mitm_data: MITMData

    @classmethod
    def from_exportable(cls, exportable: Exportable, bind: AnyDBBind) -> Self:
        mitm_data = exportable.bind(bind).generate_mitm_data()
        return cls(
            mitm=exportable.mitm,
            mitm_data=mitm_data,
            filename=exportable.filename or f'{exportable.mitm}/',
        )

    @classmethod
    def from_bound_exportable(cls, bound_exportable: BoundExportable) -> Self:
        return cls.from_exportable(bound_exportable.exportable, bound_exportable.bind)

    def write(self, sink: DataSink, **kwargs) -> None:
        ensure_filepath(sink, test_existence=False)
        sink = ensure_ext(sink, '/', override_ext=True)
        ensure_directory_exists(sink)

        try:
            folder = os.path.dirname(sink)
            mitm_def = get_mitm_def(self.mitm)

            write_header_file(self.mitm_data.header.generate_header_df(), str(os.path.join(folder, 'header.csv')))
            for c, df in self.mitm_data:
                fn = ensure_ext(mitm_def.get_properties(c).plural, '.csv')
                write_data_file(df, str(os.path.join(folder, fn)))
                logger.debug(f'Wrote {len(df)} rows to {fn} (folder export).')
        except Exception as e:
            raise MITMIOError(f'Error exporting MITM Data to folder: {sink}') from e
        return None
